# Configs
This directory stores config examples and contract artifacts for ASTS.

## What it does
- Provides schema references and static threshold examples for maintainers.

## How it works
- Runtime thresholds are primarily read from `state/thresholds.json`; files here are source-controlled references.

## Mini directory
- `thresholds.yaml`
- `schemas/`

## Notes
- Keep schema updates backward compatible with observer/telemetry payloads.
