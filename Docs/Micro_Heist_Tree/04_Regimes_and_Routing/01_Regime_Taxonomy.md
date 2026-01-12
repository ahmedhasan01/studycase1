# Regime Taxonomy (Micro 1-20m) -- CANONICAL

## Purpose
- Provide a deterministic per-symbol market-context label used to gate entries and select a setup menu.
- Tighten-only: under uncertainty, BLOCK/THROTTLE entries; exits allowed.

## Output Contract (regime classifier)
- MUST output:
  - `core_regime in {TREND, RANGE, BREAKOUT, MEAN_REV, CHAOTIC_AVOID, UNKNOWN}`
  - `regime_confidence` (monotone score; no new numeric thresholds here)
  - `regime_conflict_flag` (TRUE/FALSE)
- Meaning:
  - `regime_conflict_flag=TRUE` when higher-TF context materially disagrees with lower-TF micro context, OR when data quality / micro sanity is degraded.

## Overlay Alignment (Minimal Regime Taxonomy)
- Overlay minimal taxonomy: Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation.
- Mapping (tighten-only; if unclear -> `UNKNOWN`):
  - Trend -> `core_regime=TREND`
  - Range -> `core_regime=RANGE`
  - Chop/Noise -> typically `core_regime=UNKNOWN` (or `MEAN_REV` only when a clear anchor/mean exists)
  - Low-Vol Compression -> typically:
    - `core_regime=RANGE` (compression inside a range), OR
    - pre-condition for `core_regime=BREAKOUT` (compression resolving)
  - High-Vol Expansion -> typically:
    - `core_regime=BREAKOUT` (expansion with follow-through), OR
    - `core_regime=TREND` (trend acceleration) ONLY if structure stays orderly
  - Shock/Dislocation -> `core_regime=CHAOTIC_AVOID` (entries blocked; exits allowed)

## Precedence (MUST)
1) Readiness/Health gates (if NOT OK -> entries blocked; exits allowed)
2) Shock/Dislocation override (`CHAOTIC_AVOID`)
3) Regime classification (only if not in shock)
4) If conflict or low confidence -> `UNKNOWN` (tighten-only)

## The 6 Regimes (definitions; no numeric thresholds)

### 1) TREND
- Directional structure is stable and persistent; pullbacks are orderly; continuation is plausible.
- “Orderly” means: swings are legible, breaks do not instantly revert, and micro sanity is not degraded.
- Typical routing: TREND menu (trend continuation / pullback-into-trend).

### 2) RANGE
- Boundaries are respected; rotations are orderly; break attempts tend to fail or revert.
- Range can include low-vol compression without implying an imminent breakout.
- Typical routing: RANGE menu (range rotation / strict boundary rejection).

### 3) BREAKOUT
- Compression resolves into expansion with follow-through; structure breaks and holds with persistence.
- Distinction vs TREND:
  - BREAKOUT: transition phase (break + hold + follow-through), often after compression.
  - TREND: established directional structure (continuation/pullback framing dominates).
- Typical routing: BREAKOUT menu (breakout + retest + go; structured momentum).

### 4) MEAN_REV
- Short impulses overextend and revert toward an anchor/mean; trend-follow edges are weak.
- Distinction vs RANGE:
  - MEAN_REV: a clear “anchor/mean” exists and price repeatedly reverts toward it.
  - RANGE: boundaries/rotation dominate even if an anchor is less explicit.
- Typical routing: MEAN_REV menu (VWAP/anchor fade, EMA mean fade, range extremes fade).

### 5) CHAOTIC_AVOID (Shock/Dislocation)
- Microstructure is unstable (liquidity fragility / dislocation) OR event shock conditions active.
- Rule: entries BLOCKED; exits/reductions allowed.
- Router MUST return `route_mode=AVOID` and `entry_policy=BLOCK`.

### 6) UNKNOWN
- Triggered when:
  - `regime_conflict_flag=TRUE`, OR
  - regime confidence is low / classification ambiguous, OR
  - repeated regime flip-flops are observed (unstable environment), OR
  - Chop/Noise dominates (low clarity), OR
  - inputs are present but not decision-grade (quality degraded without full shock).
- Rule: entries BLOCKED by default (or strict THROTTLE only with an explicit documented plan); exits allowed.

## Transitions (tighten-only; no numeric thresholds)
- Use hysteresis + persistence windows:
  - A regime label MAY change only after stability persists long enough AND the prior label is invalidated long enough.
- Prevent flip-flop:
  - repeated switching -> force `UNKNOWN` (tighten-only).
- Shock recovery bias:
  - after `CHAOTIC_AVOID`, require stability before resuming normal routing; do not assume normal immediately.
- If any transition logic is unclear/missing -> [INBOX-REVIEW] and default stricter (UNKNOWN/AVOID entry blocking).

## Notes
- This file defines the regime labels and their intent.
- Routing/eligibility is defined in:
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/02_Router_Eligibility_Policy.md`
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md`
