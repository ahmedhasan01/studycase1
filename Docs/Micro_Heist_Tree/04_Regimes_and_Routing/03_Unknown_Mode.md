# Unknown Mode -- CANONICAL (Tighten-only)

## Purpose
- Define how the system behaves when regime/bias/context is ambiguous or conflicting.
- Unknown-Mode is a safety state: default to protecting capital and reducing exposure to noise/fakeouts.

## When Unknown-Mode is triggered (any of the following)
- `core_regime=UNKNOWN`
- `regime_conflict_flag=TRUE`
- Low regime confidence / ambiguous classification
- Repeated regime or router flip-flops (unstable context)
- Bias conflict (`bias_conflict_flag=TRUE`) that makes entries non-tradeable
- Data quality or micro sanity degradation that invalidates decision inputs
- Chop/Noise dominates (low clarity) and no stable routing is defensible

## Default Behavior (MUST)
- Entries: BLOCK by default.
- Exits/reductions: ALWAYS allowed.
- Router: `route_mode=UNKNOWN` and `entry_policy=BLOCK` by default.

## Escalation Rule (MUST)
- If Unknown-Mode is triggered due to liquidity fragility / dislocation symptoms (even without a formal shock flag),
  escalate to AVOID behavior:
  - `route_mode=AVOID`, `entry_policy=BLOCK`
  - exits/reductions allowed (reduce-first)

## Strict Throttle Exception (MAY, but only if explicitly documented)
Unknown-Mode may allow strict THROTTLE ONLY when:
- A documented "Unknown-Mode throttle" plan exists (where it lives must be explicit),
- It does not violate readiness/health/shock constraints,
- It does not loosen confirmation or edge-positive requirements,
- It uses reduce-first management and conservative frequency.

If the plan is missing -> [INBOX-REVIEW] and keep BLOCK default.

## Re-entry Conditions (tighten-only; no numeric thresholds)
Return to normal routing ONLY when:
- Conflicts clear (`regime_conflict_flag=FALSE` and `bias_conflict_flag=FALSE`),
- Data quality and micro sanity are healthy,
- Regime/routing becomes stable for a persistence window (do not invent numbers here),
- Shock/Dislocation is not active.

## Operational Notes
- Unknown-Mode is not "wait for a better entry"; it is "do not pay noise tax".
- If in doubt -> BLOCK entries and manage existing risk.

## References
- Router policy: `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/02_Router_Eligibility_Policy.md`
- Regimes: `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/01_Regime_Taxonomy.md`
- Confirmations: `Docs/Micro_Heist_Tree/05_Setups/05_Confirmation_Gates.md`

## Canonical Unknown-Mode Strict Throttle Plan (if enabled)

**Default is still BLOCK.** THROTTLE is a **rare exception** and must never be used to 'find trades'.

### Allowed pattern (only)
- **MO-2: Breakout + Retest + Go** (only after a **confirmed hold**; no mid-retest guessing).

### Gates (MUST all hold)
- **Eligibility stays absolute**: Readiness/Health PASS, Data Quality OK, Micro Sanity PASS.
- **No Shock/Dislocation**: any fragility symptoms -> escalate to AVOID/BLOCK.
- **Bias alignment required**: if ias_conflict_flag=TRUE -> BLOCK.
- **Readable structure**:
  - One clean level (no multi-level chop).
  - Retest hold is unambiguous (closed-bar + persistence).
- **Confirmations are stricter than normal** (never looser):
  - Closed-bar hold + persistence required.
  - No 'early' entries inside the retest.
- **Edge-positive remains required**: if edge vs friction is unclear -> BLOCK.

### Frequency + failure handling (tighten-only)
- THROTTLE means **fewer attempts** + **higher selectivity** (do not 'cycle' attempts).
- After **any failed attempt**, enforce cooldown (no immediate re-attempt).
- If repeated failures begin to appear -> revert Unknown-mode to **BLOCK** (no bargaining).
- Exits are always allowed; management remains **reduce-first**.

### Cooldown reference (MUST)
- See: Docs/Micro_Heist_Tree/06_Risk_and_Frequency/04_Cooldowns_and_NoTrade.md
