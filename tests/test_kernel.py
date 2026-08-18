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


class SignalTests(unittest.TestCase):
    def test_divergence_agreement_is_near_zero(self):
        from metrics.divergence.divergence import compute_divergence

        reports = [
            {"metrics": {"a": 0.5}, "confidence": 1.0},
            {"metrics": {"b": 0.5}, "confidence": 1.0},
            {"metrics": {"c": 0.5}, "confidence": 0.8},
        ]
        v = compute_divergence(reports)
        self.assertIsNotNone(v)
        self.assertLess(v, 1e-9)

    def test_divergence_extremes_is_one(self):
        from metrics.divergence.divergence import compute_divergence

        v = compute_divergence(
            [
                {"metrics": {"a": 0.0}, "confidence": 1.0},
                {"metrics": {"b": 1.0}, "confidence": 1.0},
            ]
        )
        self.assertAlmostEqual(v, 1.0, places=6)

    def test_divergence_unknown_without_two_reports(self):
        from metrics.divergence.divergence import compute_divergence

        self.assertIsNone(compute_divergence([]))
        self.assertIsNone(compute_divergence([{"metrics": {"a": 0.4}, "confidence": 1.0}]))
        self.assertIsNone(compute_divergence([{"metrics": {}, "confidence": 1.0}, {"confidence": 1.0}]))

    def test_pressure_at_budget_is_one(self):
        from metrics.pressure.pressure import compute_pressure

        self.assertAlmostEqual(compute_pressure({"usage": 1.0}), 1.0, places=6)
        self.assertAlmostEqual(compute_pressure({"usage": 100}), 1.0, places=6)

    def test_pressure_unknown_without_load_keys(self):
        from metrics.pressure.pressure import compute_pressure

        self.assertIsNone(compute_pressure({}))
        self.assertIsNone(compute_pressure({"coherence": 0.9, "agreement": 0.8}))

    def test_pressure_is_hottest_load(self):
        from metrics.pressure.pressure import compute_pressure

        self.assertAlmostEqual(
            compute_pressure({"usage": 0.4, "latency": 0.3, "complexity": 0.5, "coherence": 0.9}),
            0.4,
            places=6,
        )

    def test_witness_warns_but_does_not_crit(self):
        from monitoring.alerts import evaluate

        with tempfile.TemporaryDirectory() as tmp:
            out = evaluate(
                {"drift": {"total": 0.0, "fast": 0.0, "slow": 0.0}, "pressure": 0.95, "divergence": 0.8},
                tmp,
            )
        self.assertEqual(out["level"], "warn")
        self.assertTrue(any(w.startswith("PRESSURE_WARN") for w in out["warnings"]))
        self.assertTrue(any(w.startswith("DIVERGENCE_WARN") for w in out["warnings"]))

    def test_unknown_witness_does_not_become_zero(self):
        from monitoring.alerts import evaluate

        with tempfile.TemporaryDirectory() as tmp:
            out = evaluate(
                {"drift": {"total": 0.0, "fast": 0.0, "slow": 0.0}, "pressure": None, "divergence": None},
                tmp,
            )
        self.assertEqual(out["level"], "ok")
        self.assertIsNone(out["signals"]["pressure"])
        self.assertIsNone(out["signals"]["divergence"])
        self.assertEqual(out["warnings"], [])


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
                still_ok = controller.decide({"drift": {"slow": 0.0}, "pressure": 0.99, "divergence": 1.0}, tmp)
                self.assertEqual(still_ok["mode"], "ok")


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
                from ledger.ledger import replay, verify

                ledger_path = Path(tmp) / "ledger.jsonl"
                self.assertTrue(ledger_path.exists())
                self.assertEqual(verify(), [])
                data = replay()
                self.assertEqual(len(data), 3)
                self.assertTrue(all(row.get("type") == "STEP" for row in data))
                self.assertTrue(all("theta" in row and "recovery" in row for row in data))
                self.assertEqual(data[0]["recovery"]["mode"], "ok")
                usage = data[0]["theta"]["metrics"].get("usage")
                self.assertIsNotNone(usage)
                self.assertGreater(usage, 0.0)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
