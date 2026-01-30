# Risk Objectives

## Operating Header
- Mission: Trading-only risk objectives for 1–20m micro horizon (survival first, then consistency).
- Hard constraints:
  - No new numeric thresholds; otherwise tag [INBOX-REVIEW].
  - Readiness veto always wins (BLOCK entries; exits allowed).

## Procedure
1) Confirm readiness state.
2) If THROTTLE/BLOCK ⇒ tighten-only or stand down.
3) Treat every entry as optional; avoid “must trade”.
4) Prefer small, reversible exposure under uncertainty.

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Risk Objectives)</summary>

# Risk Objectives

## Operating Header
- Mission: Define trading-only risk objectives for 1–20m micro horizon (survival first, then consistency).
- Hard constraints:
  - No numeric thresholds unless already present locally; otherwise tag [INBOX-REVIEW].
  - If readiness/data-quality fails → BLOCK entries; exits/reductions allowed.
  - Invariants override this module (reduce-first, unknown-mode strict).
- Inputs / Dependencies:
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
- Outputs / Decisions: Risk posture guidelines that constrain sizing/frequency/permission.
- Legacy policy: keep legacy under <details> only.

## Procedure
1) Confirm readiness PASS/THROTTLE/BLOCK.
2) If THROTTLE/BLOCK → tighten activity (or stop) and prioritize risk reduction.
3) Treat every entry as optional; avoid “must trade”.
4) Prefer small, reversible exposure when uncertainty rises.
5) If any objective conflicts with invariants → follow invariants and tag [REVIEW-CONFLICT].

## Decision States
- PASS: allowed (subject to all other gates).
- THROTTLE: tighten activity; stricter confirmations; prefer no-trade.
- BLOCK: freeze entries; exits/reductions allowed.

## Triggers
- Readiness/health/data-quality changes.
- Friction/impact surprise (fills worsen).
- Bias flip/unknown-mode conflicts.

## Actions
- Tighten-only under uncertainty.
- Reduce-first on conflict or degradation.

## Recovery Ladder
1) Fix data/platform/operator state.
2) Return via THROTTLE first.
3) Only then PASS.


## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Risk Objectives)</summary>

# Risk Objectives

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- State high-level risk objectives for micro trading.

1.1 Inputs / Dependencies
- Overall risk appetite; edge-positive gate; robustness state; bias/regime.

1.2 Rules (MUST/SHOULD/MAY)
- MUST prioritize capital preservation; entries require edge-positive and readiness.
- SHOULD limit exposure duration to 1û20m targets; reduce when conditions drift.
- MAY adjust position sizing rules via separate risk module (not defined here) provided invariants remain.

1.3 Edge Cases / Conflicts
- If objectives conflict with bias-driven opportunities ? objectives win; reduce/exit first.

1.4 Examples (minimal, conceptual)
- Seeking small, repeatable edges with controlled downside per trade and session.

1.5 Open Questions
- [INBOX-REVIEW] Specific risk metrics (e.g., max draw per session) to adopt.

</details>

</details>

