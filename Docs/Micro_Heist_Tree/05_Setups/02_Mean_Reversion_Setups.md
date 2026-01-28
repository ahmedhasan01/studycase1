# Mean Reversion Setups (Micro 1-20m) -- CANONICAL

## Scope
  - Applies when Router outputs:
    - `route_mode=MEAN_REV` (primary), or
    - `route_mode=RANGE` AND Setup Menu explicitly allows MEAN_REV behavior at range extremes.

  - Hard blocks (MUST):
    - If Readiness/Health fails -> BLOCK entries; exits allowed.
    - If Shock/Dislocation or `route_mode=AVOID` -> BLOCK entries; exits allowed.
    - If `route_mode=UNKNOWN` -> default BLOCK entries; exits allowed (strict throttle only if explicit plan exists).
    - If `entry_policy=BLOCK` -> BLOCK entries; exits allowed.

  - Mean reversion is tighten-only by nature:
    - If clarity is not high, do not pay noise tax -> default stricter.

## Common Preconditions (MUST)
  - Winning Bias does not conflict with the intended trade, OR bias is NEUTRAL but trade is still edge-positive and confirmations are strong.
  - Edge-positive is clear and exceeds expected friction; if unclear -> BLOCK entries.
  - Confirmations (VALID trade) pass: closed bars + persistence where relevant; micro sanity OK.
  - Management posture is reduce-first.

## MR-1: Anchor Fade (VWAP / Session Anchor)
  - Intent:
    - Fade an overextension back toward an anchor/mean when impulse exhausts and reversion becomes likely.

  - Prerequisites:
    - A stable anchor exists (e.g., VWAP or a clearly used session anchor).
    - Price is meaningfully stretched away from the anchor and begins to lose momentum.
    - Micro sanity OK; no shock conditions.

  - Setup Trigger (structure-first):
    - Overextension away from anchor, then loss of continuation:
      - failed continuation attempt OR repeated inability to extend
      - rejection behavior consistent with exhaustion
    - Avoid "catching a falling knife": wait for confirmation behavior.

  - Confirmations (MUST):
    - Closed-bar evidence of rejection/exhaustion (no single-tick decisions).
    - Persistence: reversion attempt is not immediately invalidated.
    - Edge-positive remains positive after considering friction.

  - Invalidation (MUST):
    - Continuation resumes with persistence away from anchor (reversion thesis broken).
    - Micro sanity degrades (spread/impact shock) -> reduce/exit first.

  - Management (tighten-only):
    - Reduce risk if reversion stalls or becomes choppy.
    - Take partial reductions as the trade moves back toward anchor; do not overstay if momentum fades.

  - Failure Modes
    - "Trend day" behavior: repeated fades get run over -> stop fading, treat as not eligible (router should move away from MEAN_REV).
    - Anchor not respected: no stable mean -> do not force the setup.
    - Liquidity degradation: friction dominates -> block entries.

## MR-2: Mean Snapback (EMA Mean / Local Mean)
  - Intent:
    - Capture snapback toward a local mean after a short impulse becomes stretched and stalls.

  - Prerequisites:
    - A local mean is visually/structurally respected (e.g., EMA cluster or local mean band).
    - Impulse shows weakening; reversion path is not obstructed by shock conditions.

  - Setup Trigger:
    - Impulse away from mean stalls, then forms a reversion-friendly structure:
      - compression after impulse
      - failed attempt to re-accelerate in impulse direction

  - Confirmations (MUST):
    - Closed-bar reversion signal (structure shows turn, not just a wick).
    - Persistence of the turn (no immediate reclaim of impulse direction).
    - Edge-positive remains positive; if friction likely dominates -> no entry.

  - Invalidation (MUST):
    - Mean is not respected (price continues to drift away with persistence).
    - Counter-impulse acceleration returns with persistence.

  - Management:
    - Reduce-first if snapback is slow/noisy.
    - Prefer clean path to mean; if path is choppy and friction-heavy, tighten or exit.

  - Failure Modes
    - Sideways chop around mean: fake signals -> treat as UNKNOWN/THROTTLE or avoid.
    - Strong continuation (trend-like) environment -> MR becomes low expectancy.

## MR-3: Range Extreme Fade (only when range integrity is strong)
  - Intent:
    - Fade a range extreme back toward mid/anchor when the boundary holds with persistence.

  - Prerequisites:
    - A well-defined range boundary is respected (not breaking with persistence).
    - Overextension into the boundary shows rejection/exhaustion.
    - Router allows MEAN_REV behavior in RANGE context (Setup Menu).

  - Setup Trigger:
    - Boundary test + rejection behavior:
      - failed breakout attempt OR repeated failure to hold beyond boundary
      - reversal structure forms near the boundary (not mid-range guessing)

  - Confirmations (MUST):
    - Closed-bar rejection at boundary.
    - Persistence: boundary continues to hold.
    - Edge-positive remains positive; friction acceptable.

  - Invalidation (MUST):
    - Boundary breaks and holds with persistence (range integrity failed).
    - Shock/Dislocation cues appear -> reduce/exit first.

  - Management:
    - Reduce-first if boundary retests repeatedly (range may be weakening).
    - Partial reductions toward mid/anchor; avoid overstaying into noise.

  - Failure Modes
    - Range weakening / transition to breakout: repeated boundary pressure -> stop fading.
    - Mid-range entries: unacceptable; only boundary-driven.

## Operational Notes (tighten-only)
  - Mean reversion entries should be fewer and higher quality than momentum entries.
  - Do not loosen confirmations to "get the trade".
  - If repeated failures occur, treat environment as not eligible for MR and default stricter (THROTTLE/BLOCK).

## Open Questions
  - [INBOX-REVIEW] Define a single canonical "Unknown-Mode throttle plan" location if strict throttle is ever allowed.
  - [INBOX-REVIEW] If friction decomposition is incomplete for MR setups, add a short friction checklist in the glossary (keep it general; no numbers).
