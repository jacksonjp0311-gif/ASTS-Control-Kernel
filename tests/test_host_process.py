"""Live host-process adapter: this kernel, not a synthetic constant."""

from __future__ import annotations

import unittest

from adapters.host_process.probe import (
    attach,
    latency_fraction,
    reset_mark,
    rss_bytes,
    sample,
    usage_fraction,
)


class HostProcessTests(unittest.TestCase):
    def test_rss_is_a_real_number(self):
        rss = rss_bytes()
        self.assertIsNotNone(rss)
        self.assertGreater(rss, 0)
        usage = usage_fraction(rss)
        self.assertIsNotNone(usage)
        self.assertGreater(usage, 0.0)
        self.assertLess(usage, 1.0)

    def test_first_step_latency_unknown_then_real(self):
        reset_mark()
        first = {}
        attach(first)
        self.assertIsNone(first["step_dt"])
        self.assertIsNone(latency_fraction(first["step_dt"]))
        second = {}
        attach(second)
        self.assertIsNotNone(second["step_dt"])
        self.assertGreaterEqual(second["step_dt"], 0.0)
        lat = latency_fraction(second["step_dt"])
        self.assertIsNotNone(lat)
        self.assertGreaterEqual(lat, 0.0)

    def test_sample_names_this_pid(self):
        import os

        s = sample()
        self.assertEqual(s["pid"], os.getpid())
        self.assertIn("cpu_seconds", s)
