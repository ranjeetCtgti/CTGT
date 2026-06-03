from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import time


_job_lock = threading.Lock()
_status_lock = threading.Lock()
_pipeline_status: dict[str, object] = {
    "state": "idle",
    "started_at": None,
    "finished_at": None,
    "exit_code": None,
    "stdout": "",
    "stderr": "",
}


def _expected_token() -> str | None:
    token = (os.getenv("TRIGGER_TOKEN") or "").strip()
    return token or None


def _allowed_origin() -> str:
    return (os.getenv("TRIGGER_ALLOWED_ORIGIN") or "*").strip() or "*"


def _is_authorized(handler: BaseHTTPRequestHandler) -> bool:
    expected = _expected_token()
    if expected is None:
        return True
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    provided = auth_header[len("Bearer ") :].strip()
    return provided == expected


def _run_pipeline() -> tuple[int, str, str]:
    command = [sys.executable, "render_cron.py", "pipeline"]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _read_status() -> dict[str, object]:
    with _status_lock:
        return dict(_pipeline_status)


def _write_status(**updates: object) -> None:
    with _status_lock:
        _pipeline_status.update(updates)


def _run_pipeline_in_background() -> None:
    try:
        code, stdout, stderr = _run_pipeline()
        _write_status(
            state="succeeded" if code == 0 else "failed",
            finished_at=time(),
            exit_code=code,
            stdout=stdout,
            stderr=stderr,
        )
    except Exception as exc:
        _write_status(
            state="failed",
            finished_at=time(),
            exit_code=-1,
            stdout="",
            stderr=str(exc),
        )
    finally:
        _job_lock.release()


class TriggerHandler(BaseHTTPRequestHandler):
    server_version = "CTGTTrigger/1.0"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._write_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._write_json(HTTPStatus.OK, {"ok": True, "service": "trigger-api"})
            return
        if self.path == "/pipeline-status":
            self._write_json(HTTPStatus.OK, {"ok": True, **_read_status()})
            return
        self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/run-pipeline":
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        if not _is_authorized(self):
            self._write_json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return

        acquired = _job_lock.acquire(blocking=False)
        if not acquired:
            self._write_json(
                HTTPStatus.CONFLICT,
                {
                    "ok": False,
                    "error": "pipeline_already_running",
                    **_read_status(),
                },
            )
            return

        _write_status(
            state="running",
            started_at=time(),
            finished_at=None,
            exit_code=None,
            stdout="",
            stderr="",
        )
        thread = threading.Thread(target=_run_pipeline_in_background, daemon=True)
        thread.start()

        self._write_json(
            HTTPStatus.ACCEPTED,
            {
                "ok": True,
                "message": "pipeline_started",
                **_read_status(),
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._write_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", _allowed_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")


def main() -> int:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer((host, port), TriggerHandler)
    print(f"Trigger API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
