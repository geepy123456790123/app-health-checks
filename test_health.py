import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import check_health


class HealthTests(unittest.TestCase):
    def test_accepts_production_health(self):
        with patch.object(check_health.subprocess, "run", return_value=SimpleNamespace(stdout='{"status":"ok","release":"production"}')):
            self.assertEqual(check_health.check(), "ok")

    def test_retries_and_rejects_wrong_release(self):
        with patch.object(check_health.subprocess, "run", return_value=SimpleNamespace(stdout='{"status":"ok","release":"staging"}')) as fetch, patch.object(check_health.time, "sleep"):
            self.assertEqual(check_health.check(), "down")
            self.assertEqual(fetch.call_count, 4)

    def test_network_failure_is_not_healthy(self):
        with patch.object(check_health.subprocess, "run", side_effect=OSError("unreachable")), patch.object(check_health.time, "sleep"):
            self.assertEqual(check_health.check(), "down")

    def test_status_changes_are_recorded_and_healthy_checks_do_not_churn(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            check_health.record("ok", path)
            first = path.read_text()
            check_health.record("ok", path)
            self.assertEqual(path.read_text(), first)
            check_health.record("down", path)
            self.assertIn('"status": "down"', path.read_text())


if __name__ == "__main__":
    unittest.main()
