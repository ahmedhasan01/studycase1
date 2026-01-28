# Range Setups (Micro 1-20m) -- CANONICAL

## Scope
  - Applies when Router outputs:
    - `route_mode=RANGE` (primary).

  - Hard blocks (MUST):
    - If Readiness/Health fails -> BLOCK entries; exits allowed.
    - If Shock/Dislocation or `route_mode=AVOID` -> BLOCK entries; exits allowed.
    - If `route_mode=UNKNOWN` -> default BLOCK entries; exits allowed (strict throttle only if explicit plan exists).
    - If `entry_policy=BLOCK` -> BLOCK entries; exits allowed.

  - Tighten-only:
    - If range integrity weakens or conditions become unclear -> default stricter (THROTTLE/BLOCK entries); exits allowed.

## Common Preconditions (MUST)
  - Winning Bias does not conflict with the intended range trade direction:
    - No counter-bias entries by default.
    - If bias_conflict_flag=TRUE -> treat as not tradeable -> default BLOCK entries; exits allowed.
    - If flip_state=CONFIRMED -> reduce/exit current exposure FIRST before any new aligned exposure.
  - Edge-positive is clear and exceeds expected friction; if unclear -> BLOCK entries.
  - Confirmations (VALID trade) pass: CLOSED-BAR ONLY (M1+); persistence where relevant; micro hygiene OK (spread/tightness/quality within caps).
  - If confirmations disagree (one pass, one fail) -> treat as Unknown-Mode for THIS setup: default BLOCK/THROTTLE entries; exits allowed.
  - Management posture is reduce-first.

  - Core range rule (MUST):
    - No mid-range guessing. Entries must be boundary-driven or clearly defined mean/anchor-driven per Setup Menu allowances.

## RG-1: Boundary Rejection (Fade at Extremes)
  - Intent:
    - Fade a range extreme when the boundary holds with persistence and rejection behavior is confirmed.

  - Prerequisites:
    - A clear range boundary is respected (not breaking with persistence).
    - Rejection behavior is present (failed break or repeated failure to hold outside boundary).
    - Micro sanity OK; no shock conditions.

  - Setup Trigger (structure-first):
    - Boundary test + rejection structure forms at/near the extreme (not mid-range).

  -   Confirmations (MUST):
    - CLOSED-BAR ONLY (M1+). No live-candle confirmations.
    - If confirmations disagree (one pass, one fail) -> treat as Unknown-Mode for THIS setup: default BLOCK/THROTTLE entries; exits allowed.
    - Closed-bar rejection at boundary.
    - Persistence: boundary continues to hold after rejection.
    - Edge-positive remains positive after friction.
    - Closed-bar structure confirming rotation.
    - Persistence: rotation does not immediately fail.
    - Edge-positive remains positive; friction acceptable.
    - Closed-bar reclaim inside range.
    - Persistence: price holds inside range (not an immediate re-break).
    - Edge-positive remains positive; friction acceptable.

  - Invalidation (MUST):
    - Boundary breaks and holds with persistence (range integrity failed).
    - Shock/Dislocation cues appear or micro sanity degrades -> reduce/exit first.

  - Management (tighten-only):
    - Reduce-first if boundary retests repeatedly (range may be weakening).
    - Partial reductions as rotation progresses; avoid overstaying into chop.

  - Failure Modes
    - Range weakening to breakout: repeated boundary pressure -> stop fading; tighten or exit.
    - Fake rejection: one-tick wicks without persistence -> no entry.

## RG-2: Rotation to Mid (Extreme -> Mid/Anchor)
  - Intent:
    - Participate in the rotation after an extreme rejection is confirmed, aiming for mid/anchor.

  - Prerequisites:
    - A confirmed extreme rejection (RG-1 conditions satisfied) OR a structurally clear rotation start.
    - Path to mid/anchor is not obstructed by shock/degraded micro sanity.

  - Setup Trigger:
    - After rejection, rotation establishes direction with persistence (no immediate snapback).
    - Entry occurs after structure confirms rotation (avoid chasing the first impulse).

  - Invalidation (MUST):
    - Rotation stalls into chop and loses edge-positive.
    - Boundary breaks in the wrong direction with persistence.

  - Management:
    - Reduce-first if rotation becomes noisy.
    - Prefer partial reductions approaching mid/anchor.

  - Failure Modes
    - Chop zone: rotation fails repeatedly -> tighten/avoid.
    - Trend transition: if rotation turns into continuation beyond mid with persistence, reassess regime (possible TREND/BREAKOUT).

## RG-3: Failed Breakout Back into Range (Re-entry Play)
  - Intent:
    - Trade the re-entry back into the range after a breakout attempt fails and the range is re-established.

  - Prerequisites:
    - A breakout attempt occurred but did not hold with persistence.
    - Price re-enters the prior range and the boundary is reclaimed.

  - Setup Trigger:
    - Re-entry into range + reclaim of boundary with persistence.

  - Invalidation (MUST):
    - Breakout resumes and holds with persistence (failure thesis invalid).
    - Shock/Dislocation cues appear -> reduce/exit first.

  - Management:
    - Reduce-first if re-entry becomes noisy.
    - Partial reductions toward mid/anchor; avoid overstaying.

  - Failure Modes
    - Whipsaw: repeated in/out -> default stricter and reassess routing.
    - Low-quality structure: unclear range edges -> [INBOX-REVIEW] and block entries.

## Operational Notes (tighten-only)
  - Range trading is strict: boundaries and persistence matter more than "feel".
  - `entry_policy=THROTTLE` means fewer attempts and stricter confirmations; never loosen to "force trades".
  - If repeated range failures occur, treat environment as not eligible for range and default stricter (THROTTLE/BLOCK).

## Open Questions / [INBOX-REVIEW]
  - [INBOX-REVIEW] Define a single canonical "Unknown-Mode throttle plan" location if strict throttle is ever allowed.
  - [INBOX-REVIEW] If Router allows MEAN_REV within RANGE, define the exact boundary-only allowance in Setup Menu (no mid-range entries).
