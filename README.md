# ASTS Control Kernel

A loop that is starting to wobble should be steered, not killed.

ASTS is a local, deterministic **control kernel**. Each step it observes the run, measures how far telemetry has moved from baseline, and applies a gated recovery ladder — warn, recover, crit, reset — without stopping the process. **Drift owns the reset.** Pressure and divergence are witnesses: they can raise a warning; they cannot reset the kernel. Missing data prints **UNKNOWN**. The ledger is append-only.

This is not an agent. It is the thing that keeps an agent from thrashing.

![ASTS Control Kernel](docs/asts-hero.jpg)

## What it is

A fixed observer → assess → decide → execute → record pipeline for adaptive or agent-based workflows.

```
OBSERVE → AGGREGATE → ASSESS → DECIDE → EXECUTE → LEDGER
```

| Mode | Meaning |
| --- | --- |
| `ok` | below warn |
| `warn` | slow drift, pressure, or divergence crossed a warn gate |
| `recover` | tighten / validate, or escalate from a warn streak / plateau |
| `crit` | slow drift crossed the critical gate |
| `reset` | baseline reset — drift only, and only if cooldown and rate-limit allow |

A reset that fails its gates downgrades to `recover`. The reason string says so.

## Signals

| Signal | Source | Authority |
| --- | --- | --- |
| **Drift** | distance from persisted baseline, fast / slow | owns `crit` and `reset` |
| **Divergence** | confidence-weighted disagreement between observer reports | witness — `warn` only |
| **Pressure** | hottest load key (`usage`, `latency`, `complexity`, …) vs budget | witness — `warn` only |

Fewer than two usable reports → divergence is UNKNOWN. No load keys → pressure is UNKNOWN. Neither is ever silently zero.

## What it is not

- Not a live host / process governor (that is PulseFlow)
- Not a learned model and not a second policy
- Not a rollback of an external system
- Not a medical, safety, or production-certification surface

## Quick start

```powershell
cd ASTS-Control-Kernel
python main.py --simulate
```

`--simulate` is a **labeled plant**. Every step prints `SIMULATION MODE`. Latency ramps `0.3 + 0.02 * step` so you can watch `ok → warn → recover → crit`. It is not this machine.

Live (default) measures this process:

```powershell
python main.py
```

| Surface | Path |
| --- | --- |
| Entry | `main.py` |
| Orchestrator | `engine/execution/runner.py` |
| Policy | `engine/recovery/controller.py` |
| Side effects | `engine/recovery/executor.py` |
| Live adapter | `adapters/host_process/` |
| Ledger | `ledger.jsonl` (cwd, hash-chained) |
| Persistent state | `state/` |

Optional PFP benchmark:

```powershell
python benchmarks/run_pfp_benchmark.py
python benchmarks/pfp_report.py
```

## Runtime contract

```
main.py
  → engine.execution.runner.run_session
      → adapters.host_process    RSS + previous-step wall
      → runtime.observers        live usage/latency + synthetic plant
      → telemetry aggregator     drift / divergence / pressure / fingerprint
      → monitoring.alerts        ok / warn / crit  (reset stays drift-gated)
      → engine.recovery.controller   ladder + streaks + gates
      → engine.recovery.executor     reset_baseline only, here
      → ledger.append_entry          hash-chained JSONL STEP
```

`stability/pfp/controller.py` is a shim. It re-exports `engine.recovery.controller`. There is one policy.

### Recovery gates

| Gate | Default |
| --- | --- |
| warn / crit / recover / reset | 0.006 / 0.010 / 0.0115 / 0.0125 |
| cooldown before another reset | 5 steps |
| max resets per 100 steps | 3 |
| warn streak → recover | 6 |
| crit streak → reset | 3 |

Thresholds live in `state/thresholds.json` when present, else the defaults in `engine/recovery/controller.py`.

## Verify

```powershell
.\scripts\test.ps1
```

Or:

```powershell
python -m unittest discover -s tests -v
python main.py
```

Current local lattice:

- fingerprint stability
- alert ok / crit
- recovery ladder (`ok` then gated `reset`; witnesses cannot reset)
- divergence agreement → 0, extremes → 1, missing → UNKNOWN
- pressure at budget → 1, no load keys → UNKNOWN
- host adapter reports a real RSS and UNKNOWN latency on step 1
- 3-step session writes three hash-chained `STEP` rows to `ledger.jsonl`
- tampered ledger fails `replay`
- `--simulate` labels every STEP and climbs warn / recover / crit

## Directory map

```
ASTS-Control-Kernel/
  engine/        step orchestrator + recovery policy
  runtime/       observers + telemetry field
  monitoring/    alerts + operator print
  metrics/       drift (authority) · divergence / pressure (witnesses)
  ledger/        append-only JSONL + SHA-256 chain
  control/       governor / autostabilizer hooks
  stability/pfp  pulse-feedback overlay (delegates policy)
  adapters/      host_process (live) · openclaw (thin)
  configs/       schemas + example thresholds
  docs/          hero graphic
  tests/         unittest
  archive/       dead trees (not imported)
  state/         runtime artifacts (gitignored)
```

Each major folder has a mini-README. Read that file before editing the folder.

## Known limits

- Default is **LIVE**: `usage` and `latency` are this Python process. Not PulseFlow. No host QoS.
- `--simulate` is a deterministic plant. The banner, the ledger, and every observer `source` say so.
- `code`, `reasoning`, and `integration` stay synthetic in both modes.
- Divergence compares observer slices on a shared unit interval. Live vs plant will disagree. That is the point.
- Advisory actions (`tighten_constraints`, `request_validation`) are recorded, not wired into an external governor.
- `archive/` holds memory/partition/experiments stubs and old dumps. Not imported.

## License

[MIT](LICENSE) © 2026 James Paul Jackson.
