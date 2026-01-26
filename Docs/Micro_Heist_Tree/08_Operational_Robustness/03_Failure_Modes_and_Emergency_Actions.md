# Failure Modes and Emergency Actions

## Operating Header
- Mission: Deterministic fail-safe responses to failures.
- Hard constraints:
  - Failures ⇒ **BLOCK entries**; exits/reductions allowed.
  - Reduce-first doctrine always applies.
  - No numeric thresholds unless already present; otherwise tag [INBOX-REVIEW].
- Dependencies:
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md

## Procedure
1) Freeze entries (BLOCK entries).
2) Stabilize risk (reduce/exit as needed; reduce-first).
3) Identify failure class (Data / Execution / Shock / Operator / Rule conflict).
4) Recover prerequisites.
5) Return via readiness ladder only (THROTTLE → PASS).

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Failure Modes)</summary>

# Failure Modes and Emergency Actions

## Operating Header
- Mission: Deterministic responses to failures so the system fails safe.
- Use when: Data/platform breaks, execution is unreliable, emotional control slips, rule conflicts, shock conditions.
- Hard constraints (cannot override):
  - Fail-safe: failures ⇒ **BLOCK entries**; exits/reductions allowed.
  - Reduce-first doctrine always applies.
  - No numeric thresholds unless already present; otherwise tag [INBOX-REVIEW].
- Inputs / Dependencies:
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
  - Docs/Micro_Heist_Tree/09_Data/02_Data_Quality_Gates.md
- Outputs / Decisions: Emergency sequence + recovery ladder (default BLOCK entries).

## Procedure
1) Freeze entries immediately (BLOCK entries).
2) Stabilize risk (reduce/exit as needed; reduce-first).
3) Identify failure class and apply the exact action.
4) If uncertainty persists: remain BLOCK and observe.
5) Recover prerequisites (data/platform/operator).
6) Return via readiness ladder only (THROTTLE → PASS).

## Failure Classes → Actions
### A) Data failure (missing/stale/misaligned)
- Action: BLOCK entries; exits only; re-validate data-quality; stand down if unresolved.

### B) Platform / execution failure (connectivity, routing, fills)
- Action: BLOCK entries; reduce/exit if you can’t trust execution; go flat & observe if fills can’t be verified.

### C) Shock / dislocation / abnormal market behavior
- Action: BLOCK entries; reduce risk; re-enter only after stability + readiness PASS.

### D) Operator failure (emotional/mental)
- Action: BLOCK entries; flatten/reduce; cooldown (qualitative); return only after readiness PASS.

### E) Rule conflict / Unknown-mode confusion
- Action: prefer BLOCK; manage exits only; tag [REVIEW-CONFLICT] or [INBOX-REVIEW].

### F) Unexpected slippage / impact surprise
- Action: THROTTLE/BLOCK; treat friction elevated; investigate; return via readiness ladder.

## Recovery Ladder
1) Data-quality PASS.
2) Platform/execution stable and verified.
3) Operator calm and focused.
4) Market explainable (no shock suspicion).
5) Rule-integrity restored.
6) Return at THROTTLE first → then PASS.

## Post-Incident Log (short)
- What failed? (A/B/C/D/E/F)
- What did I do immediately?
- What confirmed recovery?
- What needs [INBOX-REVIEW] update?

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Failure Modes)</summary>

<details> <summary>Show legacy content (Failure Modes)</summary>  # Failure Modes and Emergency Actions  ## Mini-Index - 1.0 Purpose - 1.1 Inputs / Dependencies - 1.2 Rules (MUST/SHOULD/MAY) - 1.3 Edge Cases / Conflicts - 1.4 Examples (minimal, conceptual) - 1.5 Open Questions  1.0 Purpose - Define how the strategy responds to failures and emergencies so live trading remains safe and deterministic.  1.1 Inputs / Dependencies - Health/readiness monitors (data quality, execution feedback, confirmation availability). - Edge-positive status and bias state. - Unknown-Mode indicator for unclear regimes or conflicts.  1.2 Rules (MUST/SHOULD/MAY) - MUST If readiness/quality/health degrades: block new entries; exits/reductions allowed (robustness override). - MUST Reduce/Exit invariant still applies; reduce-first on conflicts or failures. - MUST Edge gate remains in force; failure cannot justify ignoring edge requirements. - MUST Unknown-Mode on unresolved conflicts or missing clarity; stay blocked/throttled until clarity and readiness return. - SHOULD Define fail ? action mappings: data gap/stale -> stand-down; confirmation unavailable -> block entries; conflicting bias -> Unknown-Mode and exit-only posture. - MAY include emergency stand-down timers after repeated failures; timers cannot block exits.  1.3 Edge Cases / Conflicts - Partial readiness (some checks fail, others pass): robustness veto wins; entries blocked until all required checks pass. - Bias strong but health failing: health veto overrides bias.  1.4 Examples (minimal, conceptual) - Data quality falls below threshold ? block entries, manage exits until quality restores for a stable window. - Confirmation feed missing but prices updating ? block entries; exit if risk mandates.  1.5 Open Questions - [INBOX-REVIEW] Exact thresholds for declaring health degraded and the length of recovery windows.  </details>

</details>

</details>

