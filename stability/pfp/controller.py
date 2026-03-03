"""
PFP Controller Shim (Single Source of Truth)

This module intentionally delegates to the canonical recovery controller:
    engine.recovery.controller

Goal: prevent dual-policy divergence while keeping the public API under stability/pfp.
"""

from engine.recovery.controller import decide, apply  # re-export
