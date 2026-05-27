from __future__ import annotations

import argparse
import json
import os
import sys
from http.client import HTTPSConnection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test Serper Google search requests for domain resolution")
    parser.add_argument("query", help="Search query to send to Serper")
    parser.add_argument("--gl", default="de", help="Google country code, e.g. de, us, in")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = (os.getenv("SERPER_API_KEY") or "").strip()
    if not api_key:
        print("SERPER_API_KEY is missing", file=sys.stderr)
        return 1

    conn = HTTPSConnection("google.serper.dev")
    payload = json.dumps(
        {
            "q": args.query,
            "gl": args.gl,
            "type": "search",
            "engine": "google",
        }
    )
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    conn.request("POST", "/search", payload, headers)
    response = conn.getresponse()
    data = response.read()
    print(data.decode("utf-8"))
    return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
