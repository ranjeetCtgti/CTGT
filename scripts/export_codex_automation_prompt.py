"""Print a Codex automation prompt, optionally replacing device-specific paths.

This helper is intentionally read-only. Run it on the source device and pipe the
output to Set-Clipboard, or redirect it to a secure temporary text file.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path


DEFAULT_AUTOMATION_ID = "daily-keyword-company-research"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--automation-id",
        default=DEFAULT_AUTOMATION_ID,
        help="Automation directory/id under %%USERPROFILE%%/.codex/automations.",
    )
    parser.add_argument(
        "--project-root",
        help="Replace the project root named by the existing prompt.",
    )
    parser.add_argument(
        "--staging-workbook",
        help="Replace the local staging workbook path named by the existing prompt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    automation_path = (
        Path.home()
        / ".codex"
        / "automations"
        / args.automation_id
        / "automation.toml"
    )
    if not automation_path.is_file():
        print(f"Automation file not found: {automation_path}", file=sys.stderr)
        return 2

    with automation_path.open("rb") as handle:
        config = tomllib.load(handle)

    prompt = config.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        print(f"No prompt found in: {automation_path}", file=sys.stderr)
        return 3

    cwds = config.get("cwds") or []
    old_project_root = cwds[0] if cwds and isinstance(cwds[0], str) else None
    if args.project_root:
        if not old_project_root:
            print("The source automation has no project root to replace.", file=sys.stderr)
            return 4
        prompt = prompt.replace(old_project_root, str(Path(args.project_root).resolve()))

    if args.staging_workbook:
        marker = "EDITABLE WORKBOOK SYNC: After every scheduled discovery/qualification pass, update this exact workbook in place:\n"
        start = prompt.find(marker)
        if start == -1:
            print("The staging-workbook marker was not found in the prompt.", file=sys.stderr)
            return 5
        path_start = start + len(marker)
        path_end = prompt.find("\n", path_start)
        if path_end == -1:
            print("The existing staging-workbook path could not be parsed.", file=sys.stderr)
            return 6
        prompt = (
            prompt[:path_start]
            + str(Path(args.staging_workbook).resolve())
            + prompt[path_end:]
        )

    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
