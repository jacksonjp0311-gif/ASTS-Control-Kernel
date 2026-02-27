# Adapters
This directory contains integration entrypoints that expose ASTS runtime capabilities to external callers.

## What it does
- Defines adapter boundaries so outside systems can call ASTS without touching core engine internals.

## How it works
- Adapter modules receive `env` payloads, invoke kernel paths, and return structured telemetry bundles.

## Mini directory
- `openclaw/` — OpenClaw adapter family and skill wrappers.

## Notes
- Keep adapter code thin; policy and control logic should stay in `engine/`, `monitoring/`, and `control/`.
