"""Smoke + contract tests for ASTS Control Kernel.

No third-party test runner required: python -m unittest
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class FingerprintTests(unittest.TestCase):
    def test_stable_hash(self):
        from invariants.fingerprint.fingerprint import fingerprint

        a = fingerprint({"latency": 0.3, "usage": 0.4})
        b = fingerprint({"usage": 0.4, "latency": 0.3})
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)

    def test_changes_with_payload(self):
        from invariants.fingerprint.fingerprint import fingerprint

        self.assertNotEqual(fingerprint({"x": 1}), fingerprint({"x": 2}))


class AlertTests(unittest.TestCase):
    def test_ok_below_warn(self):
        from monitoring.alerts import evaluate

        with tempfile.TemporaryDirectory() as tmp:
            theta = {"drift": {"total": 0.001, "fast": 0.001, "slow": 0.001}, "pressure": 0.1, "divergence": 0.1}
            out = evaluate(theta, tmp)
        self.assertEqual(out["level"], "ok")

    def test_crit_on_slow_drift(self):
        from monitoring.alerts import evaluate

        with tempfile.TemporaryDirectory() as tmp:
            theta = {"drift": {"total": 0.02, "fast": 0.015, "slow": 0.012}, "pressure": 0.1, "divergence": 0.1}
            out = evaluate(theta, tmp)
        self.assertEqual(out["level"], "crit")
        self.assertTrue(out["warnings"])


class RecoveryTests(unittest.TestCase):
    def test_ladder_ok_then_reset(self):
        from engine.recovery import controller

        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            state_dir.mkdir()
            recovery_file = state_dir / "recovery_state.json"
            with mock.patch.object(controller, "RECOVERY_STATE_FILE", str(recovery_file)), mock.patch.object(
                controller, "STATE_DIR", str(state_dir)
            ):
                ok = controller.decide({"drift": {"slow": 0.0}}, tmp)
                self.assertEqual(ok["mode"], "ok")
                reset = controller.decide({"drift": {"slow": 0.02}}, tmp)
                self.assertEqual(reset["mode"], "reset")
                self.assertIn("reset_baseline", reset["actions"])


class SessionTests(unittest.TestCase):
    def test_three_steps_ledger_and_modes(self):
        from engine.execution.runner import run_session

        state_dir = ROOT / "state"
        state_dir.mkdir(exist_ok=True)
        for path in state_dir.glob("*.json"):
            path.unlink()

        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                run_session(steps=3)
                ledger_path = Path(tmp) / "ledger.json"
                self.assertTrue(ledger_path.exists())
                data = json.loads(ledger_path.read_text(encoding="utf-8"))
                self.assertEqual(len(data), 3)
                self.assertTrue(all(row.get("type") == "STEP" for row in data))
                self.assertTrue(all("theta" in row and "recovery" in row for row in data))
                self.assertEqual(data[0]["recovery"]["mode"], "ok")
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
