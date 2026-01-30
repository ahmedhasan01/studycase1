# Setup Menu (Micro 1-20m) -- CANONICAL

## Purpose
- A deterministic "menu" the Router uses to select ONE allowed setup family.
- This file does not loosen any gate. It only organizes eligible choices.
- Tighten-only: if anything is unclear -> default stricter (THROTTLE/BLOCK entries); exits allowed.

## Inputs / Dependencies (authoritative)
- Readiness/Health gates:
  - `Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
- Winning Bias (priority side + conflict/flip):
  - `Docs/Micro_Heist_Tree/03_Bias_System/02_Priority_Biased_Side.md`
- Regime + Router outputs:
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/01_Regime_Taxonomy.md`
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/02_Router_Eligibility_Policy.md`
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md`
- Confirmations (VALID trade gates):
  - `Docs/Micro_Heist_Tree/05_Setups/05_Confirmation_Gates.md`
- Risk/Frequency caps:
  - `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`
- Edge-positive vs friction (definitions live in glossary + invariants):
  - `Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md`
  - `Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md`

## Router Contract (required for setup selection)
Router MUST provide:
- `route_mode in {TREND, RANGE, BREAKOUT, MEAN_REV, AVOID, UNKNOWN}`
- `entry_policy in {ALLOW, THROTTLE, BLOCK}`
- `allowed_setup_families` (explicit list)

## Global Entry Permissioning (MUST)
Entries are permitted ONLY if ALL of the following hold:
- Readiness/Health PASS (otherwise BLOCK entries; exits allowed).
- `entry_policy != BLOCK` (otherwise BLOCK entries; exits allowed).
- Winning Bias is tradeable for entries:
  - If bias_conflict_flag=TRUE -> treat as not tradeable -> default BLOCK entries; exits allowed.
  - If flip_state=CONFIRMED -> reduce/exit current exposure FIRST before any new aligned exposure.
- Edge-positive is clear and expected friction is acceptable:
  - If unclear -> treat as NOT met -> BLOCK entries; exits allowed.
- Confirmations pass (VALID trade definition).
- Risk/Frequency caps allow it.

Tighten-only notes:
- `route_mode in {AVOID, UNKNOWN}` defaults to BLOCK entries; exits allowed.
- `entry_policy=THROTTLE` means "stricter than normal": fewer attempts, stricter confirmations, reduce-first management.

## Setup Families (choose ONE family)
The Router selects ONE family from `allowed_setup_families`. If multiple are listed, pick ONE and stay consistent (avoid flip-flopping).

### Family: MEAN_REV (Mean Reversion)
- Canonical doc: `Docs/Micro_Heist_Tree/05_Setups/02_Mean_Reversion_Setups.md`
- Intent: fade overextension back toward an anchor/mean under controlled conditions.
- Default posture: strict confirmations; avoid chasing impulse.

### Family: MOMENTUM (Trend / Breakout momentum)
- Canonical doc: `Docs/Micro_Heist_Tree/05_Setups/03_Momentum_Setups.md`
- Intent: participate in continuation/breakout with follow-through and structure.
- Default posture: no counter-bias entries; require persistence/hold behavior.

### Family: RANGE (Range rotation / boundary rejection)
- Canonical doc: `Docs/Micro_Heist_Tree/05_Setups/04_Range_Setups.md`
- Intent: operate inside defined boundaries; avoid "mid-range guessing".
- Default posture: boundary-driven; invalidation is strict.

## Confirmations (shared, must pass)
- All setups must satisfy Confirmation Gates:
  - closed-bar confirmation where applicable
  - persistence/stability (no single-tick decisions)
  - micro sanity (no degraded spread/impact conditions)
- If any confirmation requirement is unclear -> [INBOX-REVIEW] and default to BLOCK entries.

## Invalidation & Management (shared)
- Reduce-first doctrine always applies:
  - If conditions degrade, reduce/exit first, then reassess.
- If a setup's defining condition fails, treat as invalid:
  - do not "hope it comes back"
  - do not add risk to rescue an invalidated setup
- Exits/reductions are always allowed under BLOCK states.

## Open Questions / [INBOX-REVIEW]
- [INBOX-REVIEW] If friction components are not explicitly decomposed for a setup, default stricter and avoid edge-positive ambiguity.
- [INBOX-REVIEW] If router allows multiple families simultaneously, define a tie-break policy (default: choose stricter or the one aligned with strongest bias and clearest confirmations).

## Tie-break: TREND vs BREAKOUT (when both appear eligible)

Apply this ladder **in order**:

1) **Route-mode wins.** If Router outputs a single oute_mode (TREND or BREAKOUT), pick that family (do not mix).
2) If Router allows both families (ambiguity remains), choose **the clearer structure**:
   - Choose **BREAKOUT** if a clean level exists and the breakout has a **confirmed retest hold** (MO-2 shape).
   - Choose **TREND** if an orderly pullback exists and continuation structure confirms (MO-3 shape) without level-chop.
3) If neither structure is clearly dominant -> default stricter: entry_policy=THROTTLE or BLOCK (prefer BLOCK if uncertainty remains).
