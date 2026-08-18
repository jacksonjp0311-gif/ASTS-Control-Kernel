# ASTS Control Kernel

Bounded **corrective control** for telemetry-driven stability.

ASTS watches an execution loop, measures drift, and applies a gated recovery ladder — warn, recover, crit, reset — without halting the run. Persistence, cooldown, and reset-rate limits keep the kernel from thrashing. The ledger is append-only.

This is a control kernel. It is not an agent, and it is not a claim that the process it watches is stable.

![ASTS Control Kernel](docs/asts-hero.jpg)

## What it is

A deterministic observer → assess → decide → execute → record pipeline for adaptive or agent-based workflows.

```
OBSERVE → AGGREGATE → ASSESS → DECIDE → EXECUTE → LEDGER
```

| Mode | Meaning |
| --- | --- |
| `ok` | below warn |
| `warn` | slow drift crossed the warn gate |
| `recover` | tighten / validate, or escalate from a warn streak / plateau |
| `crit` | slow drift crossed the critical gate |
| `reset` | baseline reset, only if cooldown and rate-limit allow |

A reset that fails its gates downgrades to `recover`. The reason string says so.

## What it is not

- Not a live host / process governor (that is PulseFlow)
- Not a claim that pressure or divergence are learned signals — those modules currently return fixed placeholders
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
      → telemetry aggregator     drift / fast / slow / fingerprint
      → monitoring.alerts        ok / warn / crit
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
- recovery ladder (`ok` then gated `reset`)
- 3-step session writes three `STEP` ledger rows

## Directory map

```
ASTS-Control-Kernel/
  engine/        step orchestrator + recovery policy
  runtime/       observers + telemetry field
  monitoring/    alerts + operator print
  metrics/       drift (real) · divergence/pressure (placeholder)
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
- `metrics/divergence` returns `0.2`. `metrics/pressure` returns `0.3`.
- Advisory actions (`tighten_constraints`, `request_validation`) are recorded, not wired into an external governor.
- `memory/`, `partition/`, and most of `experiments/` are extension points.

## License

[MIT](LICENSE) © 2026 James Paul Jackson.
