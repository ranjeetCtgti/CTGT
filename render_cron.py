from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys


JOB_ENV_VAR_BY_NAME = {
    "pipeline": "PIPELINE_ARGS",
    "enrichment": "ENRICHMENT_ARGS",
}

SCRIPT_BY_JOB_NAME = {
    "pipeline": "pipeline.py",
    "enrichment": "lead_enrichment_pass.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render cron entrypoint for CTGT jobs")
    parser.add_argument("job", choices=sorted(SCRIPT_BY_JOB_NAME), help="Cron job to run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    job_name = args.job
    script_name = SCRIPT_BY_JOB_NAME[job_name]
    extra_args = shlex.split(os.getenv(JOB_ENV_VAR_BY_NAME[job_name], ""))
    command = [sys.executable, script_name, *extra_args]

    print(f"Running {job_name} job: {' '.join(command)}")
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
