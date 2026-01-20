# 02 — Market Microstructure and Execution

## Overview Block
- Mission: Explain execution realities that affect micro trading decisions (spread, liquidity, slippage, shocks).
- Use when: You need to judge whether the market is tradable (quality gates) and how execution risk changes outcomes.
- Hard constraints (never override): Readiness/health/shock gating; no loosening under uncertainty.
- Inputs/Dependencies:
  - `Docs/Micro_Heist_Tree/08_Operational_Robustness/02_Liquidity_Shock_and_Spread_Events.md` (migration source)
  - `Docs/Micro_Heist_Tree/02_Timeframes/02_M1_Execution_Context.md` (migration source)
- Outputs/Decisions: Know when to block/throttle entries due to execution quality.
- Failure modes: Overconfidence in fills; mitigated by strict gating and “exits allowed” doctrine.
- Non-goals: Venue-specific mechanics.

## Content (Migration placeholders)
- TODO (MIGRATE): Execution context and microstructure notes
  - Source: `Docs/Micro_Heist_Tree/02_Timeframes/02_M1_Execution_Context.md`
- TODO (MIGRATE): Liquidity shock, spread events, dislocation handling
  - Source: `Docs/Micro_Heist_Tree/08_Operational_Robustness/02_Liquidity_Shock_and_Spread_Events.md`
