# Risk Bounds

## Operating Header
  - Mission: Define qualitative risk bounds (no new numbers) and how they tighten under uncertainty.
  - Hard constraints:
    - Missing bounds criteria ⇒ [INBOX-REVIEW] + default stricter behavior.
    - Under Unknown-mode/shock → tighten-only; never loosen.
  - Inputs / Dependencies:
    - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
    - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
  - Outputs / Decisions: Rules for when to reduce/stop adding/freeze entries.

## Procedure
  1) If any gate says THROTTLE → reduce frequency and avoid adding risk.
  2) If any gate says BLOCK → freeze entries; manage exits only.
  3) If realized friction increases (fills worse) → tighten bounds further.
  4) Return only via readiness ladder (THROTTLE → PASS).

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
<summary>Show legacy content (Max Trades)</summary>

### Mini-Index
  - 1.0 Purpose
  - 1.1 Inputs / Dependencies
  - 1.2 Rules (MUST/SHOULD/MAY)
  - 1.3 Edge Cases / Conflicts
  - 1.4 Examples (minimal, conceptual)
  - 1.5 Open Questions

### 1.0 Purpose
  - Outline risk limits that constrain trading within the micro horizon.

### 1.1 Inputs / Dependencies
  - Risk appetite; session/daily limits; edge-positive; health/readiness.

### 1.2 Rules (MUST/SHOULD/MAY)
  - MUST enforce hard risk caps (per-trade, per-session) before allowing entries; exits always allowed.
  - SHOULD include cool-down/no-trade triggers after breaches; entries blocked until recovery.
  - MAY refine bounds per regime via Adaptive Parameters Policy, but caps themselves remain invariant.

### 1.3 Edge Cases / Conflicts
  - Edge-positive but bound breached ? no entry; reduce/exit only.

### 1.4 Examples (minimal, conceptual)
  - Daily loss limit hit ? stand down for entries; manage exits.

### 1.5 Open Questions
  - [INBOX-REVIEW] Specific numeric caps to set for sessions and trades.

</details>

</details>
