"""Labeled plant: SIMULATION MODE climbs the ladder and never pretends to be live."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from runtime.observers.plant import plant_latency, plant_usage


ROOT = Path(__file__).resolve().parents[1]


class PlantTests(unittest.TestCase):
    def test_latency_ramp(self):
        self.assertAlmostEqual(plant_latency(0), 0.3)
        self.assertAlmostEqual(plant_latency(9), 0.48)

    def test_usage_ramp(self):
        self.assertAlmostEqual(plant_usage(0), 0.4)
        self.assertAlmostEqual(plant_usage(9), 0.49)


class SimulateSessionTests(unittest.TestCase):
    def test_ten_steps_are_labeled_and_climb(self):
        from engine.execution.runner import run_session
        from ledger.ledger import replay

        state_dir = ROOT / "state"
        state_dir.mkdir(exist_ok=True)
        for path in state_dir.glob("*.json"):
            path.unlink()

        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                run_session(steps=10, simulate=True)
                rows = replay()
            finally:
                os.chdir(cwd)

        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row.get("simulated") is True for row in rows))
        self.assertTrue(all(row["theta"].get("simulated") is True for row in rows))
        self.assertTrue(all(row["theta"]["metrics"]["latency"] == plant_latency(row["step"]) for row in rows))
        modes = [row["recovery"]["mode"] for row in rows]
        self.assertEqual(modes[0], "ok")
        self.assertIn("warn", modes)
        self.assertTrue(any(m in ("recover", "crit", "reset") for m in modes))

    def test_live_session_is_not_labeled_simulation(self):
        from engine.execution.runner import run_step

        state_dir = ROOT / "state"
        state_dir.mkdir(exist_ok=True)
        for path in state_dir.glob("*.json"):
            path.unlink()
        theta, _, decision = run_step({"step": 0, "simulate": False})
        self.assertFalse(theta.get("simulated"))
        self.assertEqual(decision["mode"], "ok")
