from __future__ import annotations

import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import trigger_api


class TriggerApiStreamingTests(unittest.TestCase):
    def test_pipeline_output_is_streamed_and_retained(self) -> None:
        process = SimpleNamespace(
            stdout=io.StringIO("pipeline output\n"),
            stderr=io.StringIO("pipeline warning\n"),
            wait=lambda: 3,
        )
        terminal_stdout = io.StringIO()
        terminal_stderr = io.StringIO()

        with (
            patch("trigger_api.subprocess.Popen", return_value=process) as popen,
            patch("trigger_api.sys.stdout", terminal_stdout),
            patch("trigger_api.sys.stderr", terminal_stderr),
        ):
            code, stdout, stderr = trigger_api._run_pipeline()

        self.assertEqual(code, 3)
        self.assertEqual(stdout, "pipeline output\n")
        self.assertEqual(stderr, "pipeline warning\n")
        self.assertEqual(terminal_stdout.getvalue(), stdout)
        self.assertEqual(terminal_stderr.getvalue(), stderr)

        command = popen.call_args.args[0]
        options = popen.call_args.kwargs
        self.assertEqual(command[1:3], ["-u", "render_cron.py"])
        self.assertEqual(options["env"]["PYTHONUNBUFFERED"], "1")


if __name__ == "__main__":
    unittest.main()
