# 03 — Indicators and Signals

## Overview Block
- Mission: Define which signals exist in this universe and how they are interpreted deterministically.
- Use when: You need to translate chart/indicator state into PASS/BLOCK decisions.
- Hard constraints (never override): Precedence ladder; Unknown-Mode under conflict; no numeric thresholds unless already present locally.
- Inputs/Dependencies:
  - Primary sources during migration: `Docs/Micro_Heist_Tree/02_Timeframes/*`, `03_Bias_System/*`, `05_Setups/*`
- Outputs/Decisions: Signal interpretation rules that do not conflict with invariants.
- Failure modes: Signal conflict; handled via Unknown-Mode and stricter gating.
- Non-goals: Adding new indicators without provenance; tag `[INBOX-REVIEW]`.

## Content (Migration placeholders)
- TODO (MIGRATE): Timeframe priority + higher context filters
  - Sources: `Docs/Micro_Heist_Tree/02_Timeframes/*`
- TODO (MIGRATE): Winning Bias definitions and conflict resolution
  - Sources: `Docs/Micro_Heist_Tree/03_Bias_System/*`
