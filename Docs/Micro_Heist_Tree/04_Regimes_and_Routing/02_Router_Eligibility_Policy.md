# Router Eligibility Policy -- CANONICAL (Micro 1-20m)

## Purpose
- Deterministically map (Readiness/Health, Regime, Winning Bias, instrument capability, micro sanity) to:
  - allowed setup families
  - an entry permissioning policy
- Router does NOT override invariants. It only tightens.

## Router Output Contract
- MUST output:
  - `route_mode in {TREND, RANGE, BREAKOUT, MEAN_REV, AVOID, UNKNOWN}`
  - `allowed_setup_families` (explicit list)
  - `entry_policy in {ALLOW, THROTTLE, BLOCK}`

## Router Eligibility (MUST pass before any entry)
If ANY condition fails -> `entry_policy=BLOCK` (entries blocked; exits allowed):

1) Readiness/Health PASS
- If NOT PASS -> BLOCK entries.

2) Data Quality OK
- No missing/stale critical inputs; no gappy bars on required TFs.
- If degraded -> BLOCK entries.

3) Micro Sanity PASS
- Spread/impact/quote quality not in shock/degraded state.
- If degraded -> BLOCK entries.

4) Shock/Dislocation Override
- If active -> `route_mode=AVOID`, `entry_policy=BLOCK`.

5) Unknown / Conflict Handling
- If `core_regime=UNKNOWN` OR `regime_conflict_flag=TRUE` -> default `route_mode=UNKNOWN`, `entry_policy=BLOCK`.
- Exception: strict THROTTLE is allowed ONLY if an explicit "Unknown-Mode throttle" plan is documented elsewhere; never loosen gates.

6) Capability Gates (instrument/venue)
- If shorting is disallowed -> router MUST NOT allow net-short entry families.
- If other capability constraints exist -> restrict allowed families accordingly.

## Default Routing (conservative)
- If `core_regime=CHAOTIC_AVOID` -> `route_mode=AVOID`, `entry_policy=BLOCK`, `allowed_setup_families=[]`
- If `core_regime=UNKNOWN` -> `route_mode=UNKNOWN`, `entry_policy=BLOCK` (default), `allowed_setup_families=[]`

Otherwise (eligible):

- core_regime=TREND
  - `route_mode=TREND`
  - allow TREND families only (trend continuation / pullback-into-trend) aligned with Winning Bias.
  - If routing begins to flip-flop or structure stops being orderly -> tighten to UNKNOWN/BLOCK.

- core_regime=RANGE
  - `route_mode=RANGE`
  - allow RANGE families (range rotation / strict boundary rejection).
  - If Chop/Noise dominates (low clarity / frequent false moves) -> tighten to UNKNOWN/BLOCK.

- core_regime=BREAKOUT
  - `route_mode=BREAKOUT`
  - allow breakout/momentum families (breakout + retest + go; compression breakout).
  - If the “break” is not holding (false breaks / instant reverts) -> tighten to UNKNOWN/BLOCK.

- core_regime=MEAN_REV
  - `route_mode=MEAN_REV`
  - allow mean-reversion families (VWAP/anchor fade, EMA mean fade, range extremes fade).
  - If a clear anchor/mean is not present -> tighten to RANGE or UNKNOWN (default stricter).

## Counter-bias / Counter-regime Rules (MUST)
- No counter-bias entries by default.
- No counter-regime entries by default:
  - Example: do not run MEAN_REV inside TREND unless explicitly defined AND independently edge-positive > friction AND does not violate invariants.
- If bias is WEAK/NEUTRAL or `bias_conflict_flag=TRUE` -> tighten: THROTTLE/BLOCK entries (default stricter).

## Re-routing / Flip-flop Protection (SHOULD)
- Prefer persistence/hysteresis: avoid frequent route changes.
- If routing flips repeatedly -> treat as UNKNOWN and BLOCK entries by default.

## References
- Regime labels: `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/01_Regime_Taxonomy.md`
- Unknown-mode: `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md`
- Setup Menu: `Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md`
- Bias: `Docs/Micro_Heist_Tree/03_Bias_System/02_Priority_Biased_Side.md`
