# Aegis API Bot Route

**When to use this doc alone:** Use when execution/system-first delivery drives the build; strategy plugs in as a module (default strategy included here for standalone use).

**Repo canonical owner:** this doc is canonical for execution/system content; other topics may be MIRROR copies to keep this doc standalone.

## Standalone Quickstart (minimum runnable components)
- Implement data pipelines and storage per sections below.
- Implement venue adapter and order routing.
- Implement strategy plugin interface + default built-in strategy.
- Implement risk management caps and exits.
- Implement execution/order handling lifecycle (place/amend/cancel/reconcile).
- Implement reliability/replayability (logging, checkpoints, backoff).

## Core Invariants (CI_v1.0)
<!-- To be populated identically across route docs in later step -->

## Data Required + Collection Plan

## Symbol Eligibility Plan

## Strategy (default built-in strategy)

## Risk Management (sizing/stops/drawdown)

## Execution & Order Handling (order lifecycle)

## Reliability & Replayability (truth loop, logging/telemetry)

## Definition of Done (pre-live checklist)
