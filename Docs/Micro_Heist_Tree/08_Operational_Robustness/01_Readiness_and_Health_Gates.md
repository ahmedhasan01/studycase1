# Readiness and Health Gates

## Operating Header
- Mission: Veto-capable gate that decides whether NEW entries are allowed right now (1–20m micro).
- Use when: Before every entry; after interruptions; when data/feeds/execution feel off; under stress/confusion.
- Hard constraints (cannot override):
  - If readiness/health/data-quality FAIL ⇒ **BLOCK entries**; exits/reductions allowed.
  - Under uncertainty ⇒ stricter (THROTTLE/BLOCK entries); exits allowed.
  - No numeric thresholds unless already present; otherwise tag [INBOX-REVIEW].
  - This module can veto entries even if setups/confirmations look good.
- Inputs / Dependencies:
  - Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Docs/Micro_Heist_Tree/09_Data/02_Data_Quality_Gates.md
- Outputs / Decisions: PASS / THROTTLE / BLOCK (entries); exits allowed always.

## Procedure
1) Run Data-Quality first.
2) Verify Platform/Execution stability (charts, routing, fills, connectivity).
3) Verify Operator state (calm, focused, not urgent).
4) Sanity-check market state (shock/dislocation suspicion?).
5) Rule-integrity check (no conflicts; Unknown-Mode if unclear).
6) Decide: PASS / THROTTLE / BLOCK.
7) If THROTTLE/BLOCK: apply actions immediately; record reason.
8) Re-evaluate only after conditions improve; never “hope trade” back to PASS.

## Decision States
- **PASS:** entries allowed (still subject to all other gates).
- **THROTTLE:** entries allowed only with stricter confirmations + reduced activity.
- **BLOCK:** no new entries; exits/reductions allowed.

## Triggers
- Data-quality not PASS.
- Execution/connection instability.
- Emotional compromise (anger/urgency/fatigue).
- Market becomes unexplainable / shock-like.
- Rule conflicts / unclear regime.

## Actions
- THROTTLE ⇒ tighten-only: fewer attempts, stricter confirmation, prefer no-trade.
- BLOCK ⇒ freeze entries; manage exits/reductions only; observation + recovery.

## Recovery Ladder
1) Data-quality PASS.
2) Platform/execution verified stable.
3) Operator calm/focused.
4) Market explainable (no shock suspicion).
5) Rule-integrity restored.
6) Return at THROTTLE first → then PASS.

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Readiness Gates)</summary>

<details> <summary>Show legacy content (Readiness Gates)</summary>  # Readiness and Health Gates  ## Mini-Index - 1.0 Purpose - 1.1 Inputs / Dependencies - 1.2 Rules (MUST/SHOULD/MAY) - 1.3 Edge Cases / Conflicts - 1.4 Examples (minimal, conceptual) - 1.5 Open Questions  1.0 Purpose - Define readiness and health gates that must pass before entries in live micro trading.  1.1 Inputs / Dependencies - Data quality, confirmation availability, edge-positive status, bias/regime clarity. - Router eligibility policy determines whether entries are allowed at all (entry_policy=ALLOW/THROTTLE/BLOCK). - See: `06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md` (frequency caps are tighten-only; readiness failure implies no new entries; exits/reductions allowed).  1.2 Rules (MUST/SHOULD/MAY) - MUST block NEW entries when readiness/health fail (exit-only behavior is allowed). - MUST treat readiness/health failure as "exit-only": manage risk, reduce exposure, or exit; do not add new exposure. - MUST set Unknown-Mode when readiness is unclear; default to BLOCK for entries until clarity returns. - SHOULD require a stability window before lifting blocks after a failure (avoid immediate flip-flop). - MAY escalate strictness (longer stability window / tighter throttles) when repeated failures occur; invariants unchanged.  ### Precedence Ladder (tighten-only) Order of enforcement for NEW ENTRIES (highest priority first): 1) Readiness/Health FAIL  -> BLOCK entries (exit-only) 2) Router Eligibility says BLOCK -> BLOCK entries (exit-only) 3) Shock/Dislocation/Unknown-Mode -> BLOCK entries (exit-only) 4) Throttles / cooldowns (if any) -> reduce/delay entries 5) Max-trades / frequency caps -> tighten-only limiter (never forces entries)  1.3 Edge Cases / Conflicts - Partial failures (some checks pass) -> default to BLOCK until all required checks pass. - If any upstream rule yields entry_policy=BLOCK, then downstream frequency caps are irrelevant for entries (effective behavior becomes max_trades=0 for entries). - "Pass" must be unambiguous: if measurement is noisy or ambiguous, treat as Unknown-Mode and remain blocked for entries.  1.4 Examples (minimal, conceptual) - Data stale ? block entries; exit or reduce only until freshness recovers for a stable window.  1.5 Open Questions - [INBOX-REVIEW] Exact metrics/time windows for declaring readiness OK.  </details>

</details>

