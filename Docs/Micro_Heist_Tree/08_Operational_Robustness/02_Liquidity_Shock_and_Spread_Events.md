# Liquidity Shock and Spread Events  ## Mini-Index - 1.0 Purpose - 1.1 Inputs / Dependencies - 1.2 Rules (MUST/SHOULD/MAY) - 1.3 Edge Cases / Conflicts - 1.4 Examples (minimal, conceptual) - 1.5 Open Questions  1.0 Purpose - Describe how to respond to liquidity shocks and spread events in micro trading.  1.1 Inputs / Dependencies - Observed spread/liq metrics; confirmations; edge; health/readiness.  1.2 Rules (MUST/SHOULD/MAY) - MUST treat shock/dislocation events as stand-down triggers: block entries; exits allowed. - SHOULD tighten confirmations and frequency after shock until stability window passes. - SHOULD integrate with Unknown-Mode when shocks create ambiguity. - MAY define thresholds via Adaptive Parameters Policy; defaults should be strict if undefined.  1.3 Edge Cases / Conflicts - Shock detected mid-trade ? reduce/exit based on risk; do not add.  1.4 Examples (minimal, conceptual) - Sudden spread widening beyond tolerance ? block entries, manage exits until spreads normalize for defined window.  1.5 Open Questions - [INBOX-REVIEW] Specific spread/liquidity thresholds and recovery windows.

## Operating Header
- Mission: Define the fail-safe trading response to liquidity shocks and spread/spread-events (micro trade).
- Use when: Spread widens, liquidity disappears, fills degrade, or behavior becomes shock-like.
- Hard constraints (cannot override):
  - Shock/dislocation ⇒ BLOCK entries by default; exits/reductions allowed.
  - Under uncertainty ⇒ stricter (BLOCK/THROTTLE entries); exits allowed.
  - No numeric thresholds unless already present locally; otherwise tag [INBOX-REVIEW].
- Inputs / Dependencies (links):
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
  - Output = shock classification + immediate actions + recovery ladder.
- Failure modes (top 3):
  - Trading through spread blowout.
  - Adding exposure mid-shock.
  - Returning to normal too early.

## Procedure
1) Detect shock symptoms (spread jump, liquidity vanish, whipsaw, abnormal fills).
2) Default action: BLOCK entries; manage exits/reductions only.
3) Tag state as Shock/Dislocation (or Unknown-Mode if ambiguous).
4) Return via readiness gates: THROTTLE first → PASS only after stability returns.

