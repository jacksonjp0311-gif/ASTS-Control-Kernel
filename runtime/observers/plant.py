"""Labeled deterministic plant. Not a live process."""

from __future__ import annotations

from typing import Any


def plant_latency(step: int) -> float:
    return max(0.0, min(1.0, 0.3 + 0.02 * int(step)))


def plant_usage(step: int) -> float:
    return max(0.0, min(1.0, 0.4 + 0.01 * int(step)))


def is_simulated(env: Any) -> bool:
    return bool(isinstance(env, dict) and env.get("simulate"))


def observe_runtime_plant(env: dict) -> dict:
    step = int(env.get("step", 0))
    return {
        "domain": "runtime",
        "metrics": {"latency": plant_latency(step)},
        "confidence": 0.8,
        "source": "simulation",
    }


def observe_resources_plant(env: dict) -> dict:
    step = int(env.get("step", 0))
    return {
        "domain": "resources",
        "metrics": {"usage": plant_usage(step)},
        "confidence": 0.9,
        "source": "simulation",
    }
