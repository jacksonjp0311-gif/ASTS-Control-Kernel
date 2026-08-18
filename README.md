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
python main.py
```

Ten steps. Synthetic observers. You should see drift climb with latency, then `warn` → `recover` → `crit` as slow drift crosses the published thresholds.

| Surface | Path |
| --- | --- |
| Entry | `main.py` |
| Orchestrator | `engine/execution/runner.py` |
| Policy | `engine/recovery/controller.py` |
| Side effects | `engine/recovery/executor.py` |
| Ledger | `ledger.json` (cwd) |
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
      → runtime.observers        collect domain slices
      → telemetry aggregator     drift / divergence / pressure / fingerprint
      → monitoring.alerts        ok / warn / crit  (reset stays drift-gated)
      → engine.recovery.controller   ladder + streaks + gates
      → engine.recovery.executor     reset_baseline only, here
      → ledger.append_entry          STEP event
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
- 3-step session writes three `STEP` ledger rows

## Directory map

```
ASTS-Control-Kernel/
  engine/        step orchestrator + recovery policy
  runtime/       observers + telemetry field
  monitoring/    alerts + operator print
  metrics/       drift (authority) · divergence / pressure (witnesses)
  ledger/        append-only STEP log
  control/       governor / autostabilizer hooks
  stability/pfp  pulse-feedback overlay (delegates policy)
  adapters/      OpenClaw skill entry
  configs/       schemas + example thresholds
  docs/          hero graphic
  tests/         unittest smoke
  state/         runtime artifacts (gitignored)
```

Each major folder has a mini-README. Read that file before editing the folder.

## Known limits

- Default observers are **synthetic** and deterministic. They demonstrate the ladder; they do not inspect a live agent.
- Divergence compares observer slices on a shared unit interval. Different domains will show some spread even when each slice is internally consistent.
- Advisory actions (`tighten_constraints`, `request_validation`) are recorded, not wired into an external governor.
- `memory/`, `partition/`, and most of `experiments/` are extension points.

## License

[MIT](LICENSE) © 2026 James Paul Jackson.
