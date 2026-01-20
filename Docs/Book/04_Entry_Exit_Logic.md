# 04 — Entry and Exit Logic

## Overview Block
- Mission: Define what constitutes a VALID entry, and how exits/reductions are always permitted.
- Use when: You are about to enter/manage/exit a trade and need deterministic rules.
- Hard constraints (never override): Reduce-first doctrine; confirmed flip exit mandate; exits allowed under blocks.
- Inputs/Dependencies:
  - `Docs/Micro_Heist_Tree/07_Trade_Management/*` (migration source)
  - `Docs/Micro_Heist_Tree/05_Setups/05_Confirmation_Gates.md` (migration source)
- Outputs/Decisions: PASS/BLOCK entry; reduce/exit rules; management doctrine.
- Failure modes: Entering under uncertainty; prevented by strict gating.
- Non-goals: Strategy optimization and numeric tuning.

## Content (Migration placeholders)
- TODO (MIGRATE): Entry hygiene, add/hold/reduce/exit doctrine
  - Sources: `Docs/Micro_Heist_Tree/07_Trade_Management/*`
- TODO (MIGRATE): Confirmation gates
  - Source: `Docs/Micro_Heist_Tree/05_Setups/05_Confirmation_Gates.md`
