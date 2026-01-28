# Replay and Backfill Validation (Trading Behavior)

## Operating Header
  - Mission: Validate that the trading universe behaves deterministically and fail-safe using historical data (Excel/CSV dumps allowed).
  - Use when: You want to verify “same data → same decisions” and confirm missing-data scenarios default strict.
  - Hard constraints (cannot override):
    - This is trading-validation only (not research/optimization).
    - Missing/stale data must reduce activity (THROTTLE/BLOCK), never increase it.
    - Do not add numeric thresholds unless already present locally.
  - Inputs / Dependencies (links):
    - `09_Data/01_Trading_Data_Inputs.md`
    - `09_Data/02_Data_Quality_Gates.md`
    - Core decision vocabulary: `01_Foundations/05_Decision_Glossary.md`
  - Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
    - Output = a repeatable validation procedure and acceptance criteria (qualitative).
  - Failure modes (top 3):
    - Replay differs due to inconsistent timestamp rules.
    - “Data cleaning” changes signals silently.
    - Missing data leads to accidental loosened behavior.
  - Non-goals:
    - Not a performance backtest framework.

## Procedure
  1) Choose a dataset slice (same instrument, same timeframe window).
  2) Normalize timestamps and bar boundaries consistently.
  3) Run the decision flow manually or with your tools and record decisions (PASS/BLOCK/THROTTLE and why).
  4) Re-run on the exact same dataset: decisions should match.
  5) Introduce controlled missing-data cases (remove a chunk, shift timestamps) and verify behavior becomes stricter.
  6) Document any mismatch as `[INBOX-REVIEW]` and fix definitions/rules (not by adding thresholds).

## Acceptance (qualitative)
  - Determinism: repeated runs on identical input produce identical decisions.
  - Fail-safe: degraded data always reduces entries (THROTTLE/BLOCK), exits remain allowed.
  - Traceability: each decision can point to the module(s) that justify it.
