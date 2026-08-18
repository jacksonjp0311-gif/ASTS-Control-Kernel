"""Sample the ASTS host process. No third-party packages."""

from __future__ import annotations

import os
import sys
import time
from typing import Any

MEMORY_BUDGET_BYTES = 512 * 1024 * 1024
LATENCY_BUDGET_SECONDS = 1.0

_last_wall: float | None = None


def rss_bytes() -> int | None:
    if os.name == "nt":
        return _rss_windows()
    if os.path.exists("/proc/self/statm"):
        return _rss_linux()
    return _rss_resource()


def _rss_windows() -> int | None:
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        try:
            get_info = kernel32.K32GetProcessMemoryInfo
        except AttributeError:
            get_info = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
        get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
        get_info.restype = wintypes.BOOL
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        if not get_info(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            return None
        return int(counters.WorkingSetSize)
    except Exception:
        return None


def _rss_linux() -> int | None:
    try:
        with open("/proc/self/statm", "r", encoding="ascii") as f:
            rss_pages = int(f.read().split()[1])
        return rss_pages * int(os.sysconf("SC_PAGE_SIZE"))
    except Exception:
        return None


def _rss_resource() -> int | None:
    try:
        import resource

        rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform == "darwin":
            return rss
        return rss * 1024
    except Exception:
        return None


def sample() -> dict[str, Any]:
    return {
        "rss_bytes": rss_bytes(),
        "cpu_seconds": time.process_time(),
        "wall": time.perf_counter(),
        "pid": os.getpid(),
    }


def attach(env: dict[str, Any]) -> dict[str, Any]:
    """Stamp env with a live sample and the wall time of the previous step."""
    global _last_wall
    now = time.perf_counter()
    env["host"] = sample()
    env["step_dt"] = None if _last_wall is None else max(0.0, now - _last_wall)
    _last_wall = now
    return env


def reset_mark() -> None:
    global _last_wall
    _last_wall = None


def usage_fraction(rss: int | None, budget: int = MEMORY_BUDGET_BYTES) -> float | None:
    if rss is None or budget <= 0:
        return None
    return max(0.0, min(1.0, float(rss) / float(budget)))


def latency_fraction(step_dt: float | None, budget: float = LATENCY_BUDGET_SECONDS) -> float | None:
    if step_dt is None or budget <= 0:
        return None
    return max(0.0, min(1.0, float(step_dt) / float(budget)))
