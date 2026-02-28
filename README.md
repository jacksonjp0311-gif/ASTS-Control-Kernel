
# ASTS Control Kernel (v1.0)
![image](https://github.com/user-attachments/assets/9ca1b64c-8b1f-4641-8bac-c8de4dba2856)


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

## Root folder mini map
Quick directory guide for top-level project folders:

### engine/
- **Engine role**: Core run pipeline and deterministic step orchestration.
- **How it works**: `engine/execution/runner.py` executes step order and attaches monitoring/recovery/ledger events; `engine/recovery/*` governs escalation and gates.
- **Mini directory**: `execution/`, `recovery/`.

### runtime/
- **Engine role**: Observer collection and telemetry-field synthesis.
- **How it works**: Domain observers emit metric slices, then aggregation composes canonical `theta`.
- **Mini directory**: `observers/`, `telemetry_field/`.

### monitoring/
- **Engine role**: Observational operator surface and alert evaluation.
- **How it works**: `alerts.py` computes status/action hints, `monitor.py` prints telemetry + assessment.
- **Mini directory**: `monitor.py`, `alerts.py`, `dashboards/`.

### metrics/
- **Engine role**: Signal generation for control and recovery.
- **How it works**: Drift baseline + multiscale smoothing combine with divergence/pressure/horizon modules.
- **Mini directory**: `drift/`, `divergence/`, `pressure/`, `horizon/`.

### control/
- **Engine role**: Policy primitives for constraint shaping and stabilization support.
- **How it works**: Governor and autostabilizer utilities are consumed by adapters/recovery flows.
- **Mini directory**: `governor_v2.py`, `autostabilizer_v2.py`.

### stability/
- **Engine role**: Optional stabilization overlays (PFP).
- **How it works**: PFP predicts/thresholds slow drift, emits pulse events, persists pulse state.
- **Mini directory**: `pfp/`.

### adapters/
- **Engine role**: Integration wrapper layer.
- **How it works**: Bridges external skill entrypoints into ASTS step execution.
- **Mini directory**: `openclaw/`.

### benchmarks/
- **Engine role**: Experimental measurement + report generation.
- **How it works**: Runs PFP benchmark loops and writes analysis artifacts.
- **Mini directory**: `run_pfp_benchmark.py`, `pfp_report.py`, `pfp_export_csv.py`, `recorder.py`.

### tests/
- **Engine role**: Verification and stress evaluation.
- **How it works**: `pytest` smoke tests validate baseline behavior; `tests/stress/` runs parameter sweeps.
- **Mini directory**: `test_*.py`, `stress/`.

### ledger/
- **Engine role**: Historical run-event append surface.
- **How it works**: Structured `STEP` events are appended to ledger output.
- **Mini directory**: `ledger.py`, `replay.py`, `compaction.py`, `hashchain.py`.

### state/
- **Engine role**: Runtime persistence and diagnostics.
- **How it works**: Stores drift, baseline, recovery, and pulse state files plus diagnostic logs.
- **Mini directory**: `*.json` state files, `core_analysis/`, `core_dumps/`, `patch_logs/`.

### configs/
- **Engine role**: Contract and threshold references.
- **How it works**: Schemas and static config examples support maintainability and validation.
- **Mini directory**: `thresholds.yaml`, `schemas/`.

### invariants/
- **Engine role**: Deterministic consistency primitives.
- **How it works**: Fingerprinting/validation helpers protect telemetry comparability.
- **Mini directory**: `fingerprint/`.

### memory/
- **Engine role**: Future memory subsystem extension point.
- **How it works**: Episodic and summarization placeholders define future interfaces.
- **Mini directory**: `episodic/`, `summaries/`.

### partition/
- **Engine role**: Future partitioning/budget API surface.
- **How it works**: Placeholder modules expose minimal partition/compression/budget hooks.
- **Mini directory**: `phi_partition.py`, `compression.py`, `budgeter.py`.

### experiments/
- **Engine role**: Non-production exploratory workspace.
- **How it works**: Keeps scenarios/notebooks isolated from release runtime.
- **Mini directory**: `notebooks/`, `scenarios/`.

## Folder mini-README system
Every major project folder includes a local `README.md` (mini README) so each scope can be understood in-place without scanning the full repository first.

### How to use mini READMEs (Human workflow)
1. Start in the folder you plan to modify.
2. Read that folder’s `README.md` first for scope, contracts, and key files.
3. Follow the listed mini directory entries to jump directly to relevant modules.

### How to use mini READMEs (AI workflow)
1. Treat each folder `README.md` as the local contract before editing files in that scope.
2. Preserve deterministic execution order and telemetry/recovery contract boundaries.
3. Use inter-folder links/contracts to avoid out-of-scope state edits or bypassing orchestrator behavior.

## Requirements
- Python 3.10+
- No third-party dependencies required for core execution in this repository snapshot

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

This repository is documented as a **v1.0 operational baseline**:
- deterministic step pipeline
- persistent recovery state with safeguards
- benchmark + stress scaffolding
- folder-level documentation for maintenance

## Clutter and archival policy

To keep the kernel maintainable:
- runtime-generated artifacts belong in `state/`, `benchmarks/runs/`, and `tests/stress/runs/`
- historical backup trees are **archive-only** and excluded from active development workflows
- folder mini READMEs define local ownership and usage boundaries

<img width="754" height="740" alt="image" src="https://github.com/user-attachments/assets/c0839db0-997f-429c-97a3-e4c195ec9b98" />

-SEEK STABILITY. SPIRAL. EVOLVE. 
