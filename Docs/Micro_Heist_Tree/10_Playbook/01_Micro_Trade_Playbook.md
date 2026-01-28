# Micro Trade Playbook

## Mini-Index
  - 1.0 Purpose
  - 1.1 Inputs / Dependencies
  - 1.2 Rules (MUST/SHOULD/MAY)
  - 1.3 Edge Cases / Conflicts
  - 1.4 Examples (minimal, conceptual)
  - 1.5 Open Questions

## 1.0 Purpose
  - One-page checklist to execute micro trades safely: Ready -> Winning Bias -> Edge-positive -> Setup -> Confirm -> Enter/Manage -> Flip' Exit.

## 1.1 Inputs / Dependencies
  - Readiness/health only (Operational Robustness/Readiness and Health Gates).
  - Winning Bias (Bias System) and regime (Regime Taxonomy).
  - Edge-positive status (Core Invariants, Priority Biased Side).
  - Setup/confirmation rules (Setup Menu, Confirmation Gates).
  - Adaptive Parameters Policy settings.

## 1.2 Rules (MUST/SHOULD/MAY)
  - MUST: If Readiness/health is not OK -> BLOCK new entries; manage/reduce/exit allowed.
  - MUST: Determine Winning Bias first; do not trade against the priority side unless an explicit, documented exception exists.
  - MUST: Determine Regime -> run Router-eligibility:
    - If Shock/Chaotic or Unknown-Mode (low confidence / TF conflict / degraded micro) -> BLOCK or strict THROTTLE entries; exits allowed.
    - If eligible -> Router selects the allowed setup family menu for this regime (trend / range / breakout / mean-rev).
  - MUST: Edge-positive gate (expected edge > expected friction). If unclear -> treat as NOT met.
  - MUST: Confirmations pass for the chosen setup family; otherwise no entry.
  - MUST: Risk/frequency/cooldown gates pass; otherwise no entry (exits allowed).
  - SHOULD: Prefer persistence/hysteresis (avoid regime flip-flop); if routing flips repeatedly -> default to Unknown-Mode.
  - MAY: Throttle (size/frequency) under mild uncertainty; never loosen gates due to "desire to trade".

## 1.3 Edge Cases / Conflicts
  - Health degrades mid-sequence -> abort entry; manage exits only.
  - Regime/confirmation conflicts -> Unknown-Mode; block/throttle entries until aligned.
  - Frequency cap hit -> no further entries despite bias strength; exits allowed.

## 1.4 Examples (minimal, conceptual)
  - Ready OK -> Bias Long Trend -> Edge-positive -> Momentum setup chosen -> Confirmation passes -> ENTER within caps; later bias flips Short -> EXIT Long before any Short.

## 1.5 Open Questions
  - [INBOX-REVIEW] Additional per-setup notes to embed without breaking one-page constraint.

## Reference: 
  - Knowledge Comparison Matrix lives in `Docs/Micro_Heist_Tree/99_Appendix/01_Knowledge_Comparison_Matrix.md`.
