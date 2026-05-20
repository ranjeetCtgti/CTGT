from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote_plus

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import DEFAULT_REQUEST_TIMEOUT_SECONDS


SCRAPEDO_BASE_URL = "https://api.scrape.do/"
HTTP_TIMEOUT_HEADROOM_SECONDS = 10


class ScrapeDoClientError(Exception):
    """Raised when scrape.do requests cannot be completed."""


@dataclass
class ScrapeRequest:
    source: str
    query: str | None
    target_url: str
    render: bool = False
    super_proxy: bool = False
    geo_code: str | None = None
    wait_selector: str | None = None
    block_resources: bool = True
    timeout_ms: int = 30_000
    # When True the client sends render=True regardless of the render field.
    # Use for Cloudflare-protected targets (e.g. Stepstone).
    force_render: bool = False
    # Headers forwarded to target via scrape.do extraHeaders feature.
    # Sent as sd-{key} HTTP headers on the scrape.do request itself.
    # scrape.do strips the "sd-" prefix and forwards to the target.
    # Do NOT use for common browser headers (UA, Accept-Language) —
    # scrape.do sets those automatically with better values than we can.
    extra_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class ScrapeResponse:
    ok: bool
    status_code: int | None
    html: str | None
    final_url: str
    credits_used: int
    error: str | None = None


class ScrapeDoClient:
    def __init__(
        self,
        api_key: str | None = None,
        timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        max_requests: int | None = None,
        max_requests_by_source: dict[str, int] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SCRAPEDO_API_KEY")
        if not self.api_key:
            raise ScrapeDoClientError("SCRAPEDO_API_KEY is missing")

        self.timeout_seconds = timeout_seconds
        self.max_requests = max_requests
        self.max_requests_by_source = max_requests_by_source or {}
        self._http = httpx.Client(timeout=self.timeout_seconds + HTTP_TIMEOUT_HEADROOM_SECONDS)
        self.credits_used_total = 0
        self.request_count = 0
        self.request_count_by_source: dict[str, int] = {}

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "ScrapeDoClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def _build_params(self, req: ScrapeRequest) -> dict[str, str]:
        params: dict[str, str] = {
            "token": self.api_key,
            "url": req.target_url,
            "render": str(req.render).lower(),
            "super": str(req.super_proxy).lower(),
            "blockResources": str(req.block_resources).lower(),
            "timeout": str(req.timeout_ms),
            "device": "desktop",
        }
        if req.geo_code:
            params["geoCode"] = req.geo_code
        if req.wait_selector:
            params["waitSelector"] = req.wait_selector
        # extraHeaders=true activates sd-* header forwarding
        if req.extra_headers:
            params["extraHeaders"] = "true"
        return params

    def _build_request_headers(self, req: ScrapeRequest) -> dict[str, str]:
        """sd-prefixed headers are forwarded by scrape.do to the target site."""
        return {f"sd-{k}": v for k, v in req.extra_headers.items()}

    def _estimate_credits(self, req: ScrapeRequest) -> int:
        if req.render and req.super_proxy:
            return 25
        if req.render:
            return 5
        return 1

    def _build_final_url(self, params: dict[str, str]) -> str:
        encoded_parts = [f"{k}={quote_plus(v)}" for k, v in params.items()]
        return f"{SCRAPEDO_BASE_URL}?{'&'.join(encoded_parts)}"

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _do_request(self, params: dict[str, str], headers: dict[str, str]) -> httpx.Response:
        return self._http.get(SCRAPEDO_BASE_URL, params=params, headers=headers)

    def scrape(self, req: ScrapeRequest) -> ScrapeResponse:
        # ── Per-source cap ────────────────────────────────────────────────────
        source_count = self.request_count_by_source.get(req.source, 0)
        source_limit = self.max_requests_by_source.get(req.source)
        if source_limit is not None and source_count >= source_limit:
            logger.warning(
                "scrape.do request skipped source={} target={} reason=max_requests_reached_for_source limit={}",
                req.source, req.target_url, source_limit,
            )
            return ScrapeResponse(ok=False, status_code=None, html=None,
                final_url=req.target_url, credits_used=0,
                error=f"max_requests_reached_for_source:{req.source}:{source_limit}")

        # ── Global cap ────────────────────────────────────────────────────────
        if self.max_requests is not None and self.request_count >= self.max_requests:
            logger.warning(
                "scrape.do request skipped source={} target={} reason=max_requests_reached limit={}",
                req.source, req.target_url, self.max_requests,
            )
            return ScrapeResponse(ok=False, status_code=None, html=None,
                final_url=req.target_url, credits_used=0,
                error=f"max_requests_reached:{self.max_requests}")

        # ── force_render ──────────────────────────────────────────────────────
        effective_render = True if req.force_render else req.render
        if req.force_render and not req.render:
            logger.debug("scrape.do force_render overriding render=False source={} target={}",
                req.source, req.target_url)

        resolved = ScrapeRequest(
            source=req.source, query=req.query, target_url=req.target_url,
            render=effective_render, super_proxy=req.super_proxy,
            geo_code=req.geo_code, wait_selector=req.wait_selector,
            block_resources=req.block_resources, timeout_ms=req.timeout_ms,
            force_render=req.force_render, extra_headers=req.extra_headers,
        )

        params = self._build_params(resolved)
        headers = self._build_request_headers(resolved)
        final_url = self._build_final_url(params)
        estimated_credits = self._estimate_credits(resolved)
        self.request_count += 1
        self.request_count_by_source[req.source] = source_count + 1

        logger.info(
            "scrape.do request source={} render={} super={} geo={} target={}",
            req.source, resolved.render, resolved.super_proxy,
            resolved.geo_code or "-", resolved.target_url,
        )

        try:
            response = self._do_request(params, headers)
        except Exception as exc:
            logger.error("scrape.do request failed source={} target={} error={}",
                req.source, req.target_url, str(exc))
            return ScrapeResponse(ok=False, status_code=None, html=None,
                final_url=final_url, credits_used=0, error=str(exc))

        status = response.status_code
        body = response.text
        ok = 200 <= status < 300 and bool(body.strip())

        # scrape.do bills on 2xx AND on 400/404/410 — track these separately
        billable_failure = not ok and status in (400, 404, 410)
        credits_used = estimated_credits if (ok or billable_failure) else 0
        self.credits_used_total += credits_used

        if ok:
            logger.info("scrape.do success source={} status={} chars={} credits={}",
                req.source, status, len(body), credits_used)
            return ScrapeResponse(ok=True, status_code=status, html=body,
                final_url=final_url, credits_used=credits_used)

        error_msg = f"status={status} empty_body={not bool(body.strip())}"
        logger.warning(
            "scrape.do non-success source={} target={} {} credits_charged={}",
            req.source, req.target_url, error_msg, credits_used,
        )
        return ScrapeResponse(ok=False, status_code=status,
            html=body if body.strip() else None,
            final_url=final_url, credits_used=credits_used, error=error_msg)

    def stats(self) -> dict[str, int]:
        return {
            "request_count": self.request_count,
            "credits_used_total": self.credits_used_total,
        }