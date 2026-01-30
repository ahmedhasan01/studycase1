# Data Quality Gates (Trading Safety)

## Operating Header
- Mission: Decide whether market data is “safe enough” to allow entries right now.
- Use when: Before any entry; when feeds are delayed; when you suspect gaps/spikes/time drift.
- Hard constraints (cannot override):
  - If data-quality FAIL → BLOCK/THROTTLE entries; exits allowed.
  - Under uncertainty → stricter behavior.
  - Do not invent numeric thresholds unless already present locally.
- Inputs / Dependencies (links):
  - `00_AI_RULES_MICRO_HEIST.md`
  - `09_Data/01_Trading_Data_Inputs.md`
  - `08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
  - PASS: data OK for entries (subject to other gates).
  - THROTTLE: entries allowed only with strict confirmations + reduced frequency.
  - BLOCK: no new entries; exits allowed.
- Failure modes (top 3):
  - Stale feed interpreted as “flat market”.
  - Time drift causing false regime or false signals.
  - Data gaps causing phantom breakouts.
- Non-goals:
  - Not vendor error handling.

## Procedure
1) Check timestamp freshness and monotonicity.
2) Check for missing bars / gaps / duplicates.
3) Check for obvious spikes/outliers that do not match context.
4) Check symbol mapping consistency (no symbol swaps).
5) Decide: PASS / THROTTLE / BLOCK.
6) If THROTTLE/BLOCK, document the reason in `[INBOX-REVIEW]` notes if unclear.

## Gate checks (no numeric thresholds)
- Freshness: data is recent enough for the timeframe being traded.
- Completeness: no unexpected gaps in the active window.
- Alignment: all inputs share the same time base (timezone + bar boundaries).
- Consistency: no sudden symbol mapping changes.
- Plausibility: price/volume changes are plausible given nearby context; if not, treat as suspect.

## Default decisions
- Any REQUIRED input missing → BLOCK.
- Any critical misalignment (timezone/bar-boundary mismatch) → BLOCK.
- Minor anomalies (few suspect points) → THROTTLE.
- Uncertainty about anomaly cause → THROTTLE or BLOCK (prefer stricter).
