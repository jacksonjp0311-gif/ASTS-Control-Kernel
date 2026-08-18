# Host process adapter

The one live adapter. It samples **this** ASTS process — the kernel you are actually running.

## What it does
- RSS via Windows `GetProcessMemoryInfo`, Linux `/proc/self/statm`, or `resource`
- CPU seconds via `time.process_time`
- Previous-step wall time via `perf_counter`

## How it is used
- `engine.execution.runner` calls `attach(env)` at the start of each step
- `runtime.observers.resources` publishes `usage` from RSS / 512 MiB
- `runtime.observers.runtime_exec` publishes `latency` from last-step wall / 1 s

First step has no previous duration. Latency is UNKNOWN until step 2.

## Notes
- No third-party packages.
- This is not PulseFlow. It does not apply host QoS. It only measures.
