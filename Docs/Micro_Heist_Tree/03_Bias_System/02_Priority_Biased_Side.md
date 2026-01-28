# Priority Biased Side

## Mini-Index
  - 1.0 Purpose
  - 1.1 Inputs / Dependencies
  - 1.2 Rules (MUST/SHOULD/MAY)
  - 1.3 Edge Cases / Conflicts
  - 1.4 Examples (minimal, conceptual)
  - 1.5 Open Questions

## 1.0 Purpose
  - Define how the Winning Bias drives side selection and frequency under the 1-20 minute horizon.

## 1.1 Inputs / Dependencies
  - Winning Bias state (Long/Short/Neutral) from bias system.
  - Edge-positive gate status.
  - Readiness/health gates and Unknown-Mode state.
  - Adaptive Parameters Policy for confirmation strictness and frequency adjustments.

## 1.2 Rules (MUST/SHOULD/MAY)
  - MUST: Determine Winning Bias only after Readiness/Health PASS; if not ready -> BLOCK entries; exits allowed.
  - MUST: Winning Bias is an output contract:
    - `winning_bias_side in {LONG, SHORT, NEUTRAL}`
    - `winning_bias_strength in {STRONG, MODERATE, WEAK, NEUTRAL}`
    - `flip_state in {NONE, CANDIDATE, CONFIRMED}`
    - `bias_conflict_flag` (TRUE when bias signals materially conflict across timeframes/structure, or when micro sanity/data quality is degraded)
  - MUST: If `bias_conflict_flag = TRUE` -> treat bias as not tradeable for entries (default `winning_bias_side = NEUTRAL` for permissioning); exits/reductions allowed. Route to Unknown-Mode behavior downstream (tighten-only).
  - MUST: Priority side:
    - If `winning_bias_side` is LONG (or SHORT) and `winning_bias_strength` is not WEAK/NEUTRAL -> prioritize that side only (no counter-bias entries by default).
    - If `winning_bias_strength in {WEAK, NEUTRAL}` -> default to BLOCK/THROTTLE entries (tighten-only) unless an explicit, documented exception exists.
  - MUST: Confirmed flip mandate:
    - If `flip_state = CONFIRMED` -> reduce/exit current exposure FIRST before any new aligned exposure is permitted.
    - A new entry MUST NOT be used to "solve" a flip (no flip-chasing).
  - SHOULD: Multi-timeframe confirmation:
    - Higher timeframe(s) provide direction context; lower timeframe refines timing.
    - Agreement across TFs increases `winning_bias_strength`; disagreement sets `bias_conflict_flag`.

## 1.3 Bias Strength Tiers (no new numeric thresholds)

  - STRONG: Clear directional structure + multi-timeframe agreement + low conflict; bias is stable and repeated tests/continuations favor the side.
  - MODERATE: Direction favored but with mild friction (occasional stalls, weaker structure, or partial TF agreement); still priority-side, but stricter confirmation and/or throttling may apply.
  - WEAK: Directional edge is tentative (frequent reversals, mixed TF signals, or unclear structure); default to THROTTLE/BLOCK entries.
  - NEUTRAL: No reliable priority side (range/chop, structural ambiguity, or conflicts); entries default BLOCK unless explicitly documented as allowed (tighten-only).
  - If any tier interpretation is unclear -> `[INBOX-REVIEW]` and default stricter (WEAK/NEUTRAL behavior).

## 1.4 Confirmed Flip (definition; no new numeric thresholds)

  - Candidate flip (`flip_state=CANDIDATE`): bias appears to shift but is not yet stable; treat as conflict/uncertainty -> tighten (THROTTLE/BLOCK entries).
  - Confirmed flip (`flip_state=CONFIRMED`): requires ALL of:
    - Persistence/stability of the new side on closed bars over the module's configured persistence window (do not invent numbers here).
    - Prior side is invalidated with persistence (not a single-bar spike).
    - Conflicts resolved: `bias_conflict_flag=FALSE`, and no readiness/micro sanity degradation is active.
  - If persistence window configuration is missing -> `[INBOX-REVIEW]` and treat flips as NOT confirmed (tighten-only).

## 1.5 Open Questions
  - [INBOX-REVIEW] Precise bias confidence scale used to throttle frequency.

