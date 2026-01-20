# 05 — Risk, Frequency, Friction

## Overview Block
- Mission: Define risk objectives/bounds, frequency caps, cooldowns, and the edge>friction gate.
- Use when: You need to know if trading is permitted today and how to throttle activity safely.
- Hard constraints (never override): Readiness/health/shock gating precedes frequency; no loosening under uncertainty.
- Inputs/Dependencies:
  - `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/*` (migration source)
  - `Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md` (friction definitions)
- Outputs/Decisions: Whether entries are permitted; how to cap/throttle; what friction means in canon.
- Failure modes: Overtrading; mitigated via caps + gating.
- Non-goals: Introducing numeric thresholds if absent; use `[INBOX-REVIEW]`.

## Content (Migration placeholders)
- TODO (MIGRATE): Risk objectives and bounds
  - Sources: `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/01_Risk_Objectives.md`, `02_Risk_Bounds.md`
- TODO (MIGRATE): Max trades under winning bias; cooldowns/no-trade
  - Sources: `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`, `04_Cooldowns_and_NoTrade.md`
- TODO (MIGRATE): Canonical friction components (if missing -> `[INBOX-REVIEW]`)
  - Source: `Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md`
