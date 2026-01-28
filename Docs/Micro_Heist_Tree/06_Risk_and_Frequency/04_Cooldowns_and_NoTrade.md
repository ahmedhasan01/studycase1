# Cooldowns and No-Trade

## Operating Header
  - Mission: Define cooldown / no-trade logic in qualitative, deterministic terms (no new numbers).
  - Hard constraints:
    - Emotional/operational failure ⇒ enforce no-trade until readiness PASS again.
    - No numeric timers unless already present locally; otherwise [INBOX-REVIEW].
  - Inputs / Dependencies:
    - Docs/Micro_Heist_Tree/08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md
    - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
  - Outputs / Decisions: When to pause after loss/flip/failure.

## Procedure
  1) After any failure class ⇒ BLOCK entries; manage exits only.
  2) After repeated uncertainty/conflict → THROTTLE then consider BLOCK.
  3) Resume via readiness ladder only (THROTTLE → PASS).

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
<summary>Show legacy content (Cooldowns/No-Trade)</summary>

### Mini-Index
  - 1.0 Purpose
  - 1.1 Inputs / Dependencies
  - 1.2 Rules (MUST/SHOULD/MAY)
  - 1.3 Edge Cases / Conflicts
  - 1.4 Examples (minimal, conceptual)
  - 1.5 Open Questions

### 1.0 Purpose
  - Define when trading must pause or throttle after events or limits.

### 1.1 Inputs / Dependencies
  - Risk bounds, robustness/health signals, regime shifts, bias flips, confirmation failures.

### 1.2 Rules (MUST/SHOULD/MAY)
  - MUST trigger cooldown/no-trade after risk breaches, repeated failures, or health degradation; entries blocked; exits allowed.
  - SHOULD include per-setup and per-session cooldowns governed by Adaptive Parameters Policy (tighten by default).
  - MAY allow gradual re-entry after stability window; requires confirmations and readiness.

### 1.3 Edge Cases / Conflicts
  - Conflicting cooldown sources ? use longest/strictest.

### 1.4 Examples (minimal, conceptual)
  - After consecutive failed confirmations, enforce a short cooldown before next attempt.

### 1.5 Open Questions
  - [INBOX-REVIEW] Duration and criteria for lifting cooldowns.

</details>

</details>

