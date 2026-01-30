# Readiness and Health Gates

## Operating Header
- Mission: Veto-capable gate deciding whether NEW entries are allowed right now (micro 1–20m).
- Hard constraints:
  - Readiness/health/data-quality FAIL ⇒ **BLOCK entries**; exits/reductions allowed.
  - Under uncertainty ⇒ strict (THROTTLE/BLOCK entries); exits allowed.
Numeric thresholds are allowed when explicitly labeled **[LOCAL]** (include units + applicability). If uncertain, tag **[INBOX-REVIEW]** and default strict.
- Dependencies:
  - Docs/Micro_Heist_Tree/09_Data/02_Data_Quality_Gates.md
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md

## Procedure
1) Run Data-Quality first.
2) Verify platform/execution stability (charts, routing, fills, connectivity).
3) Verify operator state (calm, focused, not urgent).
4) Sanity-check market state (shock / unexplainable behavior?).
5) Decide: PASS / THROTTLE / BLOCK.
6) If THROTTLE/BLOCK: apply defaults immediately and record reason.
7) Re-evaluate only after real improvement (no “hope trade”).
8) Return via ladder: THROTTLE first → PASS only after stability.

## Decision States
- PASS: entries allowed (still subject to all other gates).
- THROTTLE: entries allowed only with stricter confirmations + reduced activity.
- BLOCK: no new entries; exits/reductions allowed.

## Actions
- THROTTLE ⇒ tighten-only (fewer attempts, stricter confirmation, prefer no-trade).
- BLOCK ⇒ freeze entries; manage exits/reductions only; observe + recover.

## Recovery Ladder
1) Data-quality PASS.
2) Platform/execution verified stable.
3) Operator calm/focused.
4) Market explainable (no shock suspicion).
5) Rule-integrity restored (no unresolved conflicts).
6) THROTTLE → PASS.

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Readiness Gates)</summary>

Numeric thresholds are allowed when explicitly labeled **[LOCAL]** (include units + applicability). If uncertain, tag **[INBOX-REVIEW]** and default strict.

</details>


## Precedence Ladder (Canon, tighten-only for entries)
1) **Readiness/Health/Data-quality FAIL** ⇒ BLOCK entries; exits/reductions allowed.
2) **Unknown-Mode / conflict unresolved** ⇒ BLOCK or heavy THROTTLE entries; exits/reductions allowed.
3) **Edge-positive undefined or NOT met** ⇒ BLOCK entries; exits/reductions allowed.
4) **Confirmed flip = YES** ⇒ EXIT current exposure before any new aligned exposure; no overlap.
5) Only after (1–4) may setup/confirmation logic permit entries.

