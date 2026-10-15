from __future__ import annotations

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


def main() -> int:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({"status": "skipped", "reason": "active run marker exists"}), flush=True)
        return 3

    payload = {
        "pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "mode": "manual-broader-rerun",
    }
    os.write(fd, json.dumps(payload).encode("utf-8"))
    os.fsync(fd)
    print(json.dumps({"status": "LOCK_ACQUIRED", **payload}), flush=True)

    def stop(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        return 0
    finally:
        os.close(fd)
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass
        print(json.dumps({"status": "LOCK_RELEASED", "pid": os.getpid()}), flush=True)


if __name__ == "__main__":
    sys.exit(main())
