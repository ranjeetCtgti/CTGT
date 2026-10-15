from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from enrichment.domain_resolution import canonicalize_domain
from models.schema import ExtractedSignal


class IdentityVerificationError(ValueError):
    """Raised when company identity evidence is inconsistent or incomplete."""


@dataclass(frozen=True, slots=True)
class CompanyIdentityEvidence:
    """Evidence collected before a company may be published as a prospect.

    ``linkedin_website_url`` is the website shown on the LinkedIn company page,
    not merely the LinkedIn URL discovered by search. Requiring it prevents a
    similarly named but unrelated LinkedIn company from being attached.
    """

    official_name: str
    official_website_url: str
    corroborating_urls: tuple[str, ...]
    linkedin_url: str | None = None
    linkedin_website_url: str | None = None


@dataclass(frozen=True, slots=True)
class VerifiedCompanyIdentity:
    company_name: str
    company_domain: str
    company_url: str
    linkedin_url: str | None
    verification_urls: tuple[str, ...]


_LEGAL_DESCRIPTORS = {
    "and",
    "co",
    "company",
    "corp",
    "corporation",
    "inc",
    "incorporated",
    "limited",
    "ltd",
    "pvt",
    "the",
}


def verify_company_identity(
    signal: ExtractedSignal,
    evidence: CompanyIdentityEvidence,
) -> VerifiedCompanyIdentity:
    """Validate externally collected identity evidence against a signal.

    This function intentionally performs no web requests. The research layer
    must collect the official and corroborating URLs, then pass them here so
    persistence has a deterministic, testable gate.
    """

    official_domain = canonicalize_domain(evidence.official_website_url)
    signal_domain = canonicalize_domain(signal.company_domain)
    company_url_domain = canonicalize_domain(signal.company_url)
    if not official_domain:
        raise IdentityVerificationError("official website does not contain a valid domain")
    if not _names_match(signal.company_name, evidence.official_name):
        raise IdentityVerificationError("official company name does not match the candidate")
    if signal_domain and signal_domain != official_domain:
        raise IdentityVerificationError(
            f"candidate domain {signal_domain!r} conflicts with official domain {official_domain!r}"
        )
    if company_url_domain and company_url_domain != official_domain:
        raise IdentityVerificationError(
            f"company URL domain {company_url_domain!r} conflicts with official domain {official_domain!r}"
        )

    corroborating_urls = tuple(dict.fromkeys(url for url in evidence.corroborating_urls if url))
    if not corroborating_urls:
        raise IdentityVerificationError("at least one independent corroborating URL is required")
    if not any(canonicalize_domain(url) != official_domain for url in corroborating_urls):
        raise IdentityVerificationError(
            "corroboration must include a source outside the official company domain"
        )

    linkedin_url = evidence.linkedin_url or signal.linkedin_url
    if linkedin_url:
        parsed = urlparse(linkedin_url)
        host = (parsed.hostname or "").lower()
        if host not in {"linkedin.com", "www.linkedin.com", "ca.linkedin.com"}:
            raise IdentityVerificationError("LinkedIn URL is not on an accepted LinkedIn host")
        if not parsed.path.lower().startswith("/company/"):
            raise IdentityVerificationError("LinkedIn URL is not a company page")
        linkedin_domain = canonicalize_domain(evidence.linkedin_website_url)
        if not linkedin_domain:
            raise IdentityVerificationError(
                "LinkedIn company-page website must be captured before storing LinkedIn"
            )
        if linkedin_domain != official_domain:
            raise IdentityVerificationError(
                f"LinkedIn website domain {linkedin_domain!r} conflicts with official domain {official_domain!r}"
            )

    verification_urls = tuple(
        dict.fromkeys(
            (
                evidence.official_website_url,
                *corroborating_urls,
                *(url for url in (linkedin_url,) if url),
            )
        )
    )
    return VerifiedCompanyIdentity(
        company_name=evidence.official_name.strip(),
        company_domain=official_domain,
        company_url=_canonical_homepage(evidence.official_website_url),
        linkedin_url=linkedin_url,
        verification_urls=verification_urls,
    )


def _names_match(left: str, right: str) -> bool:
    left_tokens = _identity_tokens(left)
    right_tokens = _identity_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    return left_tokens == right_tokens or left_tokens.issubset(right_tokens) or right_tokens.issubset(left_tokens)


def _identity_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in _LEGAL_DESCRIPTORS
    }


def _canonical_homepage(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    scheme = parsed.scheme if parsed.scheme in {"http", "https"} else "https"
    return f"{scheme}://{parsed.netloc}/"
