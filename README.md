# ASTS Control Kernel (v1.0)

ASTS is a deterministic control kernel for **telemetry-driven stability management**.
It executes a fixed observer pipeline, computes drift/pressure/divergence signals, evaluates stability risk, and applies recovery policies with persistent safeguards (cooldowns, streaks, and rate limits).

## What this repository does

At runtime, ASTS follows this loop:

1. **Observe**: collect domain-specific reports (`runtime/observers/*`).
2. **Aggregate**: merge metrics and compute drift, divergence, pressure, and a fingerprint hash (`runtime/telemetry_field/aggregator.py`).
3. **Assess**: evaluate warning/critical thresholds (`monitoring/alerts.py`).
4. **Decide Recovery**: choose mode (`ok`, `warn`, `crit`, `recover`, `reset`) using streak logic, plateau sensing, cooldown gates, and reset rate limits (`engine/recovery/controller.py`).
5. **Execute Recovery**: apply side effects in one place (`engine/recovery/executor.py`).
6. **Record**: append an immutable step event (`ledger/ledger.py`).

## Runtime architecture

```text
main.py
  -> engine.execution.runner.run_session
      -> runtime.observers.base.run_observers
      -> runtime.telemetry_field.aggregator.aggregate
      -> monitoring.monitor.monitor
      -> engine.recovery.controller.decide/apply
      -> engine.recovery.executor.execute
      -> ledger.ledger.append_entry
```

## Component deep-dive

### 1) Engine
- `engine/execution/runner.py` is the orchestrator for each step.
- `engine/recovery/controller.py` contains the policy ladder and autonomous escalation logic.
- `engine/recovery/executor.py` is the single side-effect execution point.
- `engine/recovery/persist.py` and `engine/recovery/plateau.py` track persistence and plateau conditions in `state/`.

### 2) Runtime observers and telemetry
- `runtime/observers/*` currently provide deterministic synthetic metrics.
- `runtime/telemetry_field/aggregator.py` merges observer metrics and computes:
  - scalar drift + per-key deltas
  - fast/slow multiscale drift
  - divergence and pressure
  - telemetry fingerprint

### 3) Metrics and invariants
- `metrics/drift/drift.py` stores baseline metrics and computes normalized absolute deltas.
- `metrics/drift/multiscale.py` persists exponentially-smoothed fast/slow drift state.
- `metrics/divergence` and `metrics/pressure` are currently placeholder implementations.
- `invariants/fingerprint/fingerprint.py` computes SHA-256 hash fingerprints.

### 4) Monitoring and control
- `monitoring/alerts.py` translates telemetry into `ok/warn/crit` with action hints.
- `control/governor_v2.py` exposes execution-constraint policy hooks.
- `control/autostabilizer_v2.py` handles cooldown-aware stabilization triggers.

### 5) Adapter and PFP extension
- `adapters/openclaw/skill_entry.py` bridges external skill entry into the core runner.
- `adapters/openclaw/adaptive_skill_pfp.py` applies pulse-feedback policy on top of base skill output.
- `stability/pfp/*` tracks pulse state and threshold logic.

## Repository layout

```text
ASTS-Control-Kernel/
├─ adapters/               # Integration adapters and skill entrypoints
├─ benchmarks/             # Benchmark runners, recorders, and report exporters
├─ configs/                # Config schemas and static threshold examples
├─ control/                # Constraint governor and auto-stabilizer hooks
├─ engine/                 # Core execution and recovery orchestration
├─ experiments/            # Scenario and notebook placeholders
├─ invariants/             # Fingerprint/validation utilities
├─ ledger/                 # Append-only event log and replay/compaction stubs
├─ memory/                 # Episodic/summarization memory placeholders
├─ metrics/                # Drift/divergence/pressure/horizon metrics
├─ monitoring/             # Alert evaluation and telemetry printing
├─ partition/              # Partition/compression/budget helpers (currently minimal)
├─ runtime/                # Observers and telemetry field aggregation
├─ stability/              # Pulse feedback policy modules
├─ state/                  # Runtime state and diagnostic artifacts
├─ tests/                  # Smoke and stress tests
├─ main.py                 # Entry point
├─ VERSION                 # Release marker
└─ pyproject.toml          # Python project metadata
```

## Quickstart

```bash
python main.py
```

Optional benchmark run:

```bash
python benchmarks/run_pfp_benchmark.py
python benchmarks/pfp_report.py
```

## Release posture (v1.0)

This repository is now documented as **v1.0 operational baseline**:
- deterministic step pipeline
- persistent recovery state with safeguards
- benchmark + stress scaffolding
- folder-level documentation for maintenance

## Clutter and archival policy

To keep the kernel maintainable:
- runtime-generated artifacts belong in `state/`, `benchmarks/runs/`, and `tests/stress/runs/`
- historical backup trees must be considered **archive-only** and excluded from active development workflows
- see folder-level README files for boundaries and ownership
