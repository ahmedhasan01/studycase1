# Momentum Setups (Micro 1-20m) -- CANONICAL

## Scope
Applies when Router outputs:
- `route_mode=TREND` (trend continuation context), or
- `route_mode=BREAKOUT` (breakout context).

Hard blocks (MUST):
- If Readiness/Health fails -> BLOCK entries; exits allowed.
- If Shock/Dislocation or `route_mode=AVOID` -> BLOCK entries; exits allowed.
- If `route_mode=UNKNOWN` -> default BLOCK entries; exits allowed (strict throttle only if explicit plan exists).
- If `entry_policy=BLOCK` -> BLOCK entries; exits allowed.

Tighten-only:
- If uncertainty rises, do not pay noise tax -> default stricter (THROTTLE/BLOCK entries); exits allowed.

## Common Preconditions (MUST)
- Winning Bias is aligned with the intended direction:
  - No counter-bias entries by default.
  - If bias_conflict_flag=TRUE -> treat as not tradeable -> default BLOCK entries; exits allowed.
  - If flip_state=CONFIRMED -> reduce/exit current exposure FIRST before any new aligned exposure.
- Edge-positive is clear and exceeds expected friction; if unclear -> BLOCK entries.
- Confirmations (VALID trade) pass: closed bars + persistence where relevant; micro sanity OK.
- Management posture is reduce-first.

## MO-1: Compression Breakout (Quiet -> Expansion)
Intent:
- Enter with direction when tight consolidation resolves into expansion aligned with Winning Bias and Router context.

Prerequisites:
- Router context supports breakout/momentum (`route_mode=BREAKOUT` preferred).
- Consolidation is well-defined (not chaotic chop).
- Micro sanity OK; no shock conditions.

Setup Trigger (structure-first):
- Break from compression with follow-through behavior:
  - price leaves the compression area, AND
  - does not immediately snap back inside.

Confirmations (MUST):
- Closed-bar break in the intended direction.
- Persistence: follow-through or hold behavior (no immediate full reversal).
- Edge-positive remains positive after friction.

Invalidation (MUST):
- Fast reclaim back into compression with persistence (failed breakout).
- Shock/Dislocation cues or micro sanity degradation -> reduce/exit first.

Management (tighten-only):
- Reduce-first if momentum stalls or turns into chop.
- Do not add risk to "rescue" a failed breakout.

Failure Modes
- Fakeout regime: repeated failed breaks -> default stricter (THROTTLE/BLOCK) and reassess routing.
- Liquidity degradation: friction dominates -> no entries.

## MO-2: Breakout + Retest + Go
Intent:
- Participate in breakout continuation after a retest validates the new level (hold confirmation).

Prerequisites:
- Router context supports breakout/momentum.
- A clean breakout level exists (structure is readable).
- Retest is not occurring under shock/degraded micro sanity.

Setup Trigger:
- Breakout occurs, then price retests the breakout level and holds with persistence.
- Entry is after the hold is confirmed (avoid guessing mid-retest).

Confirmations (MUST):
- Closed-bar hold on/above (for long) or on/below (for short) the breakout level.
- Persistence: retest does not immediately fail.
- Edge-positive remains positive; friction acceptable.

Invalidation (MUST):
- Retest fails with persistence (reclaim through the level in the wrong direction).
- Micro sanity degrades -> reduce/exit first.

Management:
- Reduce-first if post-retest continuation does not materialize.
- If conditions degrade into chop, tighten or exit.

Failure Modes
- "Level is not real": repeated pierce-and-reject -> treat environment as not eligible.
- Trend conflict: if higher context disagrees and conflict persists -> treat as UNKNOWN (default block entries).

## MO-3: Trend Continuation (Pullback -> Continue)
Intent:
- Enter with the prevailing trend after a pullback resolves and continuation resumes, aligned with Winning Bias.

Prerequisites:
- Router context supports trend continuation (`route_mode=TREND` preferred).
- Pullback is orderly (not chaotic reversal behavior).
- Micro sanity OK; no shock conditions.

Setup Trigger:
- Pullback stabilizes, then continuation structure appears:
  - higher-low (for long) / lower-high (for short) behavior, and
  - continuation attempt holds with persistence.

Confirmations (MUST):
- Closed-bar confirmation of continuation.
- Persistence: continuation does not immediately fail.
- Edge-positive remains positive after friction.

Invalidation (MUST):
- Pullback deepens into reversal behavior with persistence (trend thesis breaks).
- Bias flip confirmed -> reduce/exit first.

Management:
- Reduce-first if continuation stalls or becomes noisy.
- Avoid repeated re-entries in chop; tighten frequency under THROTTLE.

Failure Modes
- Chop masquerading as trend: repeated starts/stops -> default stricter and reassess routing.
- Counter-bias temptation: do not trade against Winning Bias by default.

## Operational Notes (tighten-only)
- Momentum trades are high-quality only when confirmation and persistence are present.
- `entry_policy=THROTTLE` means fewer attempts and stricter confirmations; never loosen to "get a trade".
- If repeated failures occur, treat environment as not eligible for momentum and default stricter (THROTTLE/BLOCK).

## Open Questions / [INBOX-REVIEW]
- [INBOX-REVIEW] Define a single canonical "Unknown-Mode throttle plan" location if strict throttle is ever allowed.
- [INBOX-REVIEW] If Router allows both TREND and BREAKOUT simultaneously, define a tie-break rule (default: choose stricter or the one with clearer confirmations and alignment).

## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md -> "Canonical Unknown-Mode Strict Throttle Plan (if enabled)"
- **TREND vs BREAKOUT tie-break (deterministic):**
  - Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md -> "Tie-break: TREND vs BREAKOUT (when both appear eligible)"

## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md -> "Canonical Unknown-Mode Strict Throttle Plan (if enabled)"
- **TREND vs BREAKOUT tie-break (deterministic):**
  - Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md -> "Tie-break: TREND vs BREAKOUT (when both appear eligible)"

## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md -> "Canonical Unknown-Mode Strict Throttle Plan (if enabled)"
- **TREND vs BREAKOUT tie-break (deterministic):**
  - Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md -> "Tie-break: TREND vs BREAKOUT (when both appear eligible)"

## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md -> 'Canonical Unknown-Mode Strict Throttle Plan (if enabled)'
- **TREND vs BREAKOUT tie-break (deterministic):**
  - Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md -> 'Tie-break: TREND vs BREAKOUT (when both appear eligible)'

## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md -> 'Canonical Unknown-Mode Strict Throttle Plan (if enabled)'
- **TREND vs BREAKOUT tie-break (deterministic):**
  - Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md -> 'Tie-break: TREND vs BREAKOUT (when both appear eligible)'
