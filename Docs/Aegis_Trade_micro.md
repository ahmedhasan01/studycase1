# Aegis Trade Micro - Standalone End-to-End Spec

Generated on 2026-01-06. This document is a standalone, end-to-end specification for the Aegis "micro" scalping system: strategy, eligibility, risk, data requirements, execution contracts, and operational requirements.


## Standalone Quickstart
1) Follow **Strategy_Rules (must follow)**, then read **Strategy_Idea**, **Confirmation Rules**, **Regimes**, **Indicators**, and **TFs_information**.
2) Apply **Symbol Eligibility (Micro)** and **REST-Eligibility** to construct a tradable universe.
3) Apply **Risk_management** and **Promotion / State Constraints** to control exposure and entry permissioning.
4) Implement market-data ingestion and gates per **Stream Eligibility** and any required persistence per **Data/Storage**.
5) Implement execution behavior and constraints per **Execution & Order Handling** and **OrderEngine**.
6) Implement operational safety per **Operational Reliability & Replayability**.


## Contents
- [AI_Rules](#airules)
- [Strategy_Rules (must follow)](#strategyrules-must-follow)
- [Strategy_Idea](#strategyidea)
- [Confirmation Rules](#confirmation-rules)
- [Regimes](#regimes)
- [Indicators](#indicators)
- [TFs_information](#tfsinformation)
- [Symbol Eligibility (Micro)](#symbol-eligibility-micro)
- [Risk_management](#riskmanagement)
- [Promotion / State Constraints](#promotion-state-constraints)
- [Execution & Order Handling](#execution-order-handling)
- [Data/Storage](#datastorage)
- [REST-Eligibility](#resteligibility)
- [Operational Reliability & Replayability](#operational-reliability-replayability)
- [Stream Eligibility](#stream-eligibility)
- [OrderEngine](#orderengine)
- [Machine_learning](#machinelearning)


## AI_Rules

- (Assistant conduct, boundaries, truthfulness; align with Docs/rules/AI_Rules.md)

- Strictly follow Docs/rules/AI_Rules.md and its Documentation Protocol (INTEGRATE/REFACTOR, Shared/Common + deltas-only, required logs) for any edits to this doc.

- Must read and follow this document line by line before proposing or coding strategy changes.

- In chat, always surface advantages, disadvantages, and key facts when suggesting logic or code changes to this strategy.

- When discussing regimes or changes, propose clear benefits/risks and guards; do not add regimes without explicit rules and validation.

- If any part of the doc (strategy, regimes, indicators, risk, scoring, data, execution, etc.) is missing or unclear, ask the user for clarification rather than guessing.

- Do not ask where state is stored; follow documented storage notes and only request clarification if the doc lacks required detail.


## Strategy_Rules (must follow)

- All information must be verified in order: (1) trading books/reference material, (2) All AI knowledge base, (3) trusted online sources. Do not deviate from this order.

- Purpose: scalp trading with 1-20 minute horizons; operates 24/7.

- Spot: LONG entries only. SHORT intents are EXIT/REDUCE only (no net short opens).

- Indicators must be chosen by: (a) precision of signal, (b) richness of information per indicator, (c) computational lightness/latency in software.

- Any conflict from a single indicator must be confirmed or denied by another independent indicator before action.

- Core invariants: REST/WS-free strategy layer; order flow goes through RiskManager/OrderEngine; no direct exchange calls in strategy.

- Treat each symbol independently: params, risk limits, adaptives, and bias flips are per-symbol; no cross-symbol coupling except explicit cluster caps.

- Adaptive readiness (global, tighten-only): any parameter marked `adaptive_required` must declare `{default_source in {CONST, REST_EXCHANGEINFO, REST_TICKER24H, BARS_OBSERVED, WS_OBSERVED}, bootstrap_value, min_samples, adapt_state in {BOOTSTRAP, ADAPTING, READY, FROZEN}}`. If any adaptive_required item is not READY, block NEW entries (`entry_mode=BLOCK`, `entry_blocked=true`) while still computing/logging; exits/reductions remain allowed. Reuse last-good values only after READY has been reached at least once; bootstrap values are conservative caps/floors from `default_source`.

- Spot asset handling rules:

  - Any spot wallet asset that is actively monitored (per exchange_info and TF analysis) can be promoted to LIVE_HOT and traded long. SHORT intents are EXIT/REDUCE only on spot; use them only to flatten or cut existing long risk (no net short opens).

  - If a live long is open and fresh analysis flips to short: manage exits/reductions only (never open a net short). If the position is safe (no loss), exit then stand down; if unsafe, exit immediately. No lingering in conflicting bias.


## Strategy_Idea

- Multi-brain scalp:

  - Mean-reversion: fade 1m VWAP z extremes with RSI/micro confirm.

  - Momentum/breakout: M5/M15/H1 trend/breakouts with 1m confirm.

  - Range: tighter fades in RANGE/moderate vol.

- Regime/routing: router selects one strategy based on regime weights; CHAOTIC or strong TREND_DOWN can block longs; range prefers mean-rev, trend prefers momentum.

- Goal: capture short moves (1-20m horizon) with strict edge gating (net of fees + expected slippage).


## Confirmation Rules

- Entry hygiene: 1m persistence + confirming candle before entries; applied per symbol.

- Micro checks: spread caps, micro_score, depth/OFI where available; conflicts require a second indicator to confirm/deny.

- Regime checks: H1 regime filter blocks longs in strong TREND_DOWN; CHAOTIC can disable entries; applied per symbol.


## Regimes

- Computed from stored bars (H1/M15/M5 trend/vol) with clear, non-overlapping buckets. Each symbol is classified independently.

- Classifier (deterministic):
  - Direction metric: EMA slope in ATR units on H1/M15 with config keys `regime.direction.SLOPE_THRESH_UP` / `regime.direction.SLOPE_THRESH_DOWN` (defaults bootstrap from per-symbol rolling percentiles of ATR-normalized slope; adaptive_required=true).
  - Volatility metric: ATR/RTV percentile vs rolling baseline with keys `regime.vol.VOL_PCTL_HIGH` / `regime.vol.VOL_PCTL_LOW` (defaults from per-symbol rolling percentiles; adaptive_required=true).
  - Clarity metric: chop/overlap or trend persistence score with keys `regime.clarity.CLARITY_PCTL_LOW` / `regime.clarity.CLARITY_PCTL_HIGH` (defaults from per-symbol rolling percentiles; adaptive_required=true).
  - Hysteresis: regime label changes only after `regime.HYSTERESIS_K_CONSEC` consecutive closed bars meet the new label (default 2; adaptive_required=true). Until all adaptive_required thresholds are READY, block NEW entries (exits allowed).
  - Defaults/bootstraps: thresholds derive from per-symbol rolling percentiles (default_source=BARS_OBSERVED); bootstrap values are conservative blocks until adapt_state reaches READY.

- Buckets with rules (per symbol):

  - **Uptrend Calm**

    - Detection: Uptrend (H1/M15 EMAs up + HH/HL) AND vol near baseline.

    - Allow: momentum/breakout longs; mean-rev only as pullback with strong micro OK. Shorts = exit/reduce only on spot.

    - Gates: M1 persistence + confirming candle; per-symbol micro/spread caps; edge > fees+slip; strong down/chaotic on higher TF blocks longs.

  - **Uptrend HighVol**

    - Detection: Uptrend + vol/ATR in expansion (above the upper volatility percentile band for several bars).

    - Allow: momentum/breakout longs with tighter sizing/micro/edge caps; mean-rev caution/avoid.

    - Gates: stricter micro/slippage caps; edge must compensate high vol; if TF disagreement appears classify as Chaotic/Avoid.

  - **Downtrend Calm**

    - Detection: Downtrend (H1/M15 EMAs down + LH/LL) AND vol near baseline.

    - Allow: shorts = exit/reduce only on spot; mean-rev fades only with strong confirmation.

    - Gates: block longs in strong down; per-symbol micro/edge caps apply.

  - **Downtrend HighVol**

    - Detection: Downtrend + vol expansion spike.

    - Allow: exits prioritized; entries generally avoided; spot shorts = exit/reduce only.

    - Gates: strict edge/micro caps; if structure unclear classify as Chaotic/Avoid.

  - **Range / compression**

    - Detection: Range direction (flat/overlapping EMAs, mixed swings) + vol compression (low ATR/range).

    - Allow: mean-rev/range fades (VWAP z, RSI) with micro confirm; momentum muted.

    - Gates: micro sanity; avoid if liquidity thin; edge > fees+slip.

  - **Range with Expansion**

    - Detection: Range direction + vol/ATR expansion (high).

    - Allow: only if breakout/volatility playbook is explicitly enabled; otherwise treat as high-risk/avoid; mean-rev caution.

    - Gates: strict micro/edge caps; require multi-TF confirmation to avoid whipsaw; ambiguous outcomes route to Chaotic/Avoid.

  - **Trend with Compression**

    - Detection: Up/Down bias intact but vol below baseline; shrinking ranges/pullback-like.

    - Allow: wait/hold bias unless a defined pullback/continuation setup is enabled; reduce size if trading; spot shorts remain exit-only.

    - Gates: maintain trend filters; micro/edge caps apply; if compression persists with mixed signals treat as Range.

  - **Chaotic / high-vol / no clear direction**

    - Detection: TF conflict + vol spikes without structure; poor micro (spread/depth/OFI erratic) or stale/gappy coverage.

    - Allow: avoid entries; exits/flatten only; hard lock until micro + coverage normalize.

- override (Event/Shock Avoid): spread blowout/depth collapse or other shock -> freeze entries; resume only after micro normalizes with hysteresis:
  - Re-enable gates: `spread_bps <= REENABLE_SPREAD_MULT * median_spread_bps_window` and `depth_ratio >= REENABLE_DEPTH_RATIO` for RESUME_WINDOW seconds.
  - Defaults: `REENABLE_SPREAD_MULT` default_source=CONST, bootstrap_value=1.50; `REENABLE_DEPTH_RATIO` default_source=CONST, bootstrap_value=0.70; adaptive_required=true when learned from rolling baselines.
  - Action is tighten-only: block NEW entries until both conditions hold with hysteresis; exits/reductions remain allowed.

- Regime guides strategy routing and entry gating; ambiguous states fall back to Range or Chaotic (avoid). SHORT on spot remains exit/reduce only unless explicitly allowed elsewhere.

### Event / Liquidity Shock Override (runs before regime classification)

- Priority: if triggered, set core_regime = CHAOTIC_AVOID; this overrides normal regime classification.

- Detection (any triggers => lock):

  - Spread shock: spread_now > spread_median * SPREAD_SHOCK_MULT

  - Depth shock: depth_now < depth_median * DEPTH_SHOCK_MULT

  - rapid spread widening + trade-through risk flags.

- Allow while locked:

  - No new entries.

  - Exits/reductions allowed (risk management only).

  - Prefer passive/maker exits if possible; allow taker only for emergency risk control.

- Gates to resume (must all be true for RESUME_WINDOW seconds):

  - spread_now <= spread_median * SPREAD_RESUME_MULT

  - depth_now  >= depth_median  * DEPTH_RESUME_MULT

  - coverage fresh + micro_ok

  - Then unlock and re-run normal regime classifier.


### Regime Confidence, Transitions, and Unknown-Mode (Hardening)

- Regime outputs MUST include: `core_regime`, `regime_confidence`, and `regime_conflict_flag`.
  - `regime_confidence`: monotone score derived from agreement across TF direction/vol/clarity metrics (no new numeric thresholds here; use existing percentile-based gates/hysteresis).
  - `regime_conflict_flag`: TRUE when higher-TF direction/structure materially disagrees with lower-TF micro context (e.g., trend vs chop) or when data quality/micro sanity is degraded.

- Transition policy (tighten-only):
  - Use hysteresis + persistence windows: a regime label MAY change only after it is stable for long enough and the prior label has been invalidated for long enough (prevents flip-flop in clustered volatility environments).
  - If `regime_conflict_flag` is TRUE, force `core_regime = UNKNOWN` (Unknown-Mode) until conflict clears; entries blocked/throttled, exits/reductions allowed.

- Override precedence:
  - Event/Liquidity Shock Override (CHAOTIC_AVOID) runs first.
  - If shock is not active, normal regime classification runs.
  - If classification is ambiguous or confidence is low -> Unknown-Mode.

### Router (Regime -> Setup Menu) - Deterministic Routing Contract

- Purpose: convert `core_regime` + Winning Bias + instrument capability into a *single allowed setup menu* (or AVOID/UNKNOWN). Router is an entry-permissioning layer; it MUST NOT override invariants.

- Router output:
  - `route_mode in {TREND, RANGE, BREAKOUT, MEAN_REV, AVOID, UNKNOWN}`
  - `allowed_setup_families` (explicit list)
  - `entry_policy in {ALLOW, THROTTLE, BLOCK}` (tighten-only; BLOCK is default under uncertainty)

- Router eligibility (MUST pass before any entry is considered):
  - Readiness/health gates pass (otherwise BLOCK).
  - Data quality is "good" (no gappy/stale bars; no missing critical indicators) (otherwise BLOCK).
  - Micro sanity passes (spread/depth/slippage not in shock/degraded state) (otherwise BLOCK).
  - `core_regime` is not CHAOTIC_AVOID; and not UNKNOWN unless explicitly running a *documented* "Unknown-Mode throttle" plan (otherwise BLOCK).
  - Instrument capability gates: if venue/instrument disallows shorting, Router MUST never output a net-short entry route (spot default).

- Default routing (conservative):
  - Uptrend Calm / Trend with Compression -> `route_mode=TREND`, allow only trend-continuation and pullback-into-trend families aligned with Winning Bias.
  - Range Calm -> `route_mode=RANGE`, allow only mean-reversion/range rotation families *if* edge-positive beats friction; otherwise THROTTLE/BLOCK.
  - Range with Expansion -> `route_mode=BREAKOUT` **only** when breakout playbook explicitly enabled; else AVOID.
  - Chaotic/high-vol/no-structure or any Shock Override -> `route_mode=AVOID` (entries BLOCK; exits/reductions allowed).
  - Any material TF conflict or low confidence -> `route_mode=UNKNOWN` (entries BLOCK or strict THROTTLE; exits allowed).

- Hard rule: Router MUST block "counter-regime" entries by default.
  - Example: do not run mean-reversion in a clear trend regime unless that specific counter-regime family is explicitly defined and independently confirmed by regime confidence + edge-positive.

- Rationale (advisory, non-normative): volatility clustering and regime switching motivate persistence/hysteresis and conservative unknown-mode behavior; liquidity often becomes fragile in stress, supporting shock overrides and entry blocking under degraded microstructure.

## Indicators

- Set:

  - Trend/vol: EMAs (1m/5m/15m/1h), trend dirs, vol regime.

  - Mean-rev: 1m VWAP z-score, RSI, ATR/vol.

  - Micro: spread_bps, micro_score, top_depth_quote, last_trade_dir, order flow imbalance (if present), expected_slippage_bps.

- Selection criteria: precision first, then multi-signal richness, then speed/efficiency.

- Conflict resolution: disagreements require a second indicator; micro sanity must pass.

- Config notes: per-indicator parameters (periods, thresholds, z-bands, smoothing), per-TF usage, and any adaptive adjustments (with bounds). Keep defaults here and note where per-symbol overrides live (e.g., symbol_params).


## TFs_information

- Primary TFs: M1, M5, M15, H1.

- Roles (suggested): M1 for execution/micro entries and exits; M5 for short-term structure and confirmation; M15 for bias and noise filtering; H1 for regime/slow trend gate.

- Interaction: faster TFs must not violate H1 regime; alignment rules should be explicit when filled.

- Ticks: record where raw tick/microstructure data is used (e.g., spread, depth, OFI) and how it feeds into M1 features; add details in Indicators and Data/Storage when specified.


## Symbol Eligibility (Micro)

- Purpose: exchangeInfo holds static rules/capabilities; runtime eligibility is spot-only and computed in 
universe_filter() without margin/borrow state.

    - Scope: REST-only (no WS). Step 1 after exchangeInfo + score_ex; fetch 24h ticker FULL for limited symbols=[...] 
set, derive thresholds, apply gates, rank survivors.

    - Derived per symbol: activity_score = ln(max(quoteVolume, EPS)) + ACTIVITY_ALPHA*ln(max(count,1)); range_pct_24h 
= (high-low)/max(low, EPS); abs_change_pct_24h = abs(priceChangePercent).

    - Thresholds (per refresh): compute activity gates on full set: MIN_QVOL_24H=P60(quoteVolume); 
MIN_TRADES_24H=P60(count). Let S_activity = symbols passing both. If |S_activity| < MIN_N_FOR_PERCENTILES: 
MIN_RANGE_PCT_24H=P25(range_pct_24h over S_activity); MAX_ABS_CHANGE_PCT_24H=P95(abs_change_pct_24h over S_activity). 
Else reuse last-good thresholds or set WARMUP_TICKER_THRESHOLDS (skip gating). These thresholds are 
adaptive_required=true with `default_source=REST_TICKER24H`, bootstrap_value=conservative block (no new entries) until 
READY, and adapt_state gating (READY required before allowing entries; exits allowed).

    - Eligibility (REST-only): gates are computed as above. Symbols that meet all four gates are eligible; those that 
do not are kept but annotated as blocked for data-driven reasons (INACTIVE_24H, RANGE_TOO_LOW, MOVE_TOO_EXTREME, 
TICKER_FAIL_STREAK). If the ticker thresholds adapt_state != READY, block NEW entries (exits allowed) while continuing 
to refresh thresholds.

    - Ranking (all symbols): sort by (1) score_ex ascending, (2) activity_score descending, (3) tie = symbol. Keep two 
ordered lists: eligible_symbols_rest_step1 and blocked_symbols_rest_step1 (blocked carry their reason code); do not 
drop blocked symbols entirely.

    - Snapshot health: on refresh failure keep last-good, state=STALE; if age>MAX_SNAPSHOT_AGE_MS state=DEGRADED and 
block new entries (exits still allowed). WARMUP_TICKER_THRESHOLDS means thresholds not stabilized; skip ticker gating 
that cycle but flag it.

    - Drop/aging: if a symbol disappears from exchangeInfo, remove from universe immediately (no rank/trade; stale row 
may be kept for audit only). If fail_streak >= FAIL_STREAK_DROP, exclude from ticker eligibility/ranking (reason 
TICKER_FAIL_STREAK) until a successful refresh resets streak; keep last data in ticker24h_full_latest with 
ticker_stale=1/fail_streak/last_error for reporting/debug. On successful refresh per symbol: fail_streak=0, 
ticker_stale=0, last_error=NULL; on failed batch/parse: fail_streak++, ticker_stale=1, last_error=<error string>.


## Risk_management

### 0) Shared conventions (Risk_management)

- Scope/ownership: RiskManager owns sizing/caps/drawdown keys; Stream Eligibility only tightens (microstructure feasibility, shock, cost) and returns Q_entry_eff.

- Per symbol: sizing, caps, cooldowns per symbol; global/cluster caps layer on top. Spot only; maker-first, taker only within caps for urgent exits (no order-type playbook here).

- Cost/fee ownership: COST_BUDGET_BPS lives in RiskManager; fee worst-case input is stream_eligibility.ws_depth.FEE_BPS_WORSTCASE (venue/account-tier); Stream Eligibility uses both to pass/fail cost, RiskManager consumes the result. Deprecated alias: stream_eligibility.ws_depth.COST_BUDGET_BPS (do not introduce new references; migrate to risk_manager.COST_BUDGET_BPS).

- Expectancy gate (tighten-only, non-trigger): strategy computes or supplies `expected_edge_bps` (default 0 until implemented, which blocks entries). Require `expected_edge_bps >= worstcase_cost_bps + edge_buffer_bps`; otherwise block NEW entries (exits/reductions allowed). `edge_buffer_bps` defaults to a conservative constant (e.g., 5 bps) until adapted. This is a veto/constraint, not a trigger.

- Determinism: no randomness; decisions deterministic given bars/WS streams/thresholds snapshots/config versions on DECISION_LOOP_MS cadence.

- EPS for divisions and finiteness guards; all clamp/adaptive changes are tighten-only.

- risk_manager.mode = "RISK_FRACTION" (options: RISK_FRACTION | CONSTANT_NOTIONAL | EQUAL_SPLIT)

- risk_manager.equity_cap_usdt = 10000; risk_manager.risk_budget_usdt = 1000; risk_manager.CONST_NOTIONAL_USDT = 50

- Q bounds/liquidity fraction: risk_manager.Q_MIN_ENTRY = 10; risk_manager.Q_MAX_ENTRY = 200; risk_manager.Q_DEPTH_FRAC = 0.20

- Caps: risk_manager.MAX_CONCURRENT_POS = 5; risk_manager.MAX_SYMBOL_NOTIONAL = 0.20 * equity_cap_usdt; risk_manager.MAX_GROSS_NOTIONAL = 1.00 * equity_cap_usdt; risk_manager.MAX_NET_NOTIONAL = 0.50 * equity_cap_usdt

- Drawdown limits: risk_manager.DAILY_LOSS_LIMIT_R = 3.0; risk_manager.SESSION_DRAWDOWN_LIMIT_R = 4.0; risk_manager.LOSS_STREAK_LIMIT = 5

- Cost budget: risk_manager.COST_BUDGET_BPS = 25 (Stream Eligibility cost gate consumes it)

- Equity cap / withdraw: MAX_TRADING_EQUITY_USDT; excess may route to withdraw queue (if enabled)

- Defaults are conservative placeholders; tune per venue/fees before live

### B) Sizing pipeline (deterministic)

- Step 1: Q_base per mode (bounded by Q_MIN_ENTRY..Q_MAX_ENTRY)

  - RISK_FRACTION: R_usdt = risk_fraction * equity_usdt (or risk_budget_usdt); if stop distance known, q_base_units = R_usdt / max(stop_dist_usdt_per_unit, EPS); Q_raw = q_base_units * mid_price; else use deterministic vol-proxy stop (e.g., k_vol * ATR_1m/5m); Q_base = clamp(Q_raw, Q_MIN_ENTRY, Q_MAX_ENTRY)

  - CONSTANT_NOTIONAL: Q_base = clamp(CONST_NOTIONAL_USDT, Q_MIN_ENTRY, Q_MAX_ENTRY)

  - EQUAL_SPLIT: Q_split = MAX_GROSS_NOTIONAL / max(MAX_CONCURRENT_POS,1); Q_base = clamp(min(Q_split, Q_MAX_ENTRY), Q_MIN_ENTRY, Q_MAX_ENTRY)

- Step 2: Microstructure clamps (tighten-only) Q_base -> Q_entry_eff (from Stream Eligibility; RiskManager does not recompute micro)

  - Depth fraction: Q_depth_cap = Q_DEPTH_FRAC * min_depth_quote(N); Q1 = min(Q_base, Q_depth_cap) [DEPTH_FRAC_CLAMP]

  - Slip cap (if ENABLE_SLIP_CAP): find largest Q with slip_bps(Q) <= SLIP_CAP_BPS; Q2 = min(Q1, Q_slip_cap) [SLIP_CAP_CLAMP]

  - Spread/cost budget: cost_bps_entry = spread_bps + slip_bps(Q2) + fee_bps_worstcase; require cost_bps_entry <= risk_manager.COST_BUDGET_BPS else block NEW entry [COST_TOO_HIGH]

  - Shock/cooldown/quarantine: if SHOCK_LOCK / COOLDOWN_ACTIVE / FEED_LAG_QUARANTINE / BOOK_GAMEY / REPEATED_SHOCKS -> block NEW entries; exits allowed; primary_reason = deepest level reached

  - Result: Q_entry_eff after tighten-only clamps/viability

- Step 3: Caps enforcement Q_entry_eff -> Q_final (pre + post)

  - Pre-trade order: MAX_CONCURRENT_POS -> MAX_SYMBOL_NOTIONAL -> MAX_GROSS_NOTIONAL -> MAX_NET_NOTIONAL; Q_final = min(Q_entry_eff, remaining caps); if Q_final < Q_MIN_ENTRY -> block NEW entry [RISK_BLOCK_Q_TOO_SMALL]; exits allowed

  - Post-fill: update exposures immediately; exits allowed even when caps bind (respect exchange minNotional/stepSize)

  - Reason codes: RISK_CAP_CONCURRENT, RISK_CAP_SYMBOL, RISK_CAP_GROSS, RISK_CAP_NET, RISK_BLOCK_Q_TOO_SMALL, RISK_BLOCK_DAILY_LOSS, RISK_BLOCK_SESSION_DD, RISK_BLOCK_LOSS_STREAK

- Step 4: Execution: maker-first; taker only within caps for urgent exits (no order-type playbook here)

### C) Drawdown / loss-streak stops

- Evaluate every decision tick: if daily_R >= DAILY_LOSS_LIMIT_R or session_R >= SESSION_DRAWDOWN_LIMIT_R or loss_streak >= LOSS_STREAK_LIMIT -> block NEW entries (exits allowed)

- Recovery: daily reset at trading-day boundary; session reset at session boundary; optional cooldown after breach

### D) Adaptive sizing (slow, bounded; tighten-only)
- Allowed adaptives: size_mult in [0.50, 1.10]; optional per-symbol size_mult_sym in [0.50, 1.00] (SMALLCAP_THIN = 1.00)
- Cadence: update at most once per ADAPT_REFRESH_SEC (default 60s)

- Freeze: during WARMUP/STALE_FEED/COOLDOWN_ACTIVE/BARS_WARMUP/BARS_STALE/feed stress/repeated shocks/quarantine; reuse last-good

- Tighten inputs only: feed stress, BOOK_GAMEY, repeated shocks, TF_CONFLICT caution, elevated realized slip (if logged)

- Telemetry reason tags: SIZE_TIGHTEN_FEED, SIZE_TIGHTEN_SHOCK, SIZE_TIGHTEN_GAMEY, SIZE_TIGHTEN_TF_CONFLICT, SIZE_TIGHTEN_COST

### E) Venue filters (exchange feasibility)

- Apply exchangeInfo filters last: minNotional, lotSize/stepSize, tickSize (and minQty/maxQty if present)

- If rounding down pushes Q_final below filters -> block NEW entry [ORDER_SIZE_INVALID] (do not round up into higher risk); record rounded qty/price in telemetry

### F) Required inputs (Spot long/flat) - deterministic + replay

- Account state: equity_usdt, free_usdt, per-symbol inventory (qty, avg entry), open_orders/reserved

- Exchange filters (per symbol): minNotional, stepSize/lotSize, tickSize, minQty/maxQty if present

- Fees: fee_bps_worstcase (taker worst-case; maker optional)

- Stream Eligibility outputs consumed: Q_entry_eff, primary_reason (+ secondary optional), state flags (COOLDOWN_ACTIVE/SHOCK_LOCK/FEED_LAG_QUARANTINE/BOOK_GAMEY/etc.), thresholds_version_ts per level

- Bars readiness/context: bars_ready_tf, bars_stale_tf; optional TF alignment class tightens size_mult only

- Exposure/caps state: gross_usdt, net_usdt, per_symbol_usdt, open_positions_count

- Drawdown/loss state: daily_R (or pnl), session_R, loss_streak; reset boundaries

- Replay metadata: decision_ts_ms, DECISION_LOOP_MS, config_version snapshots, stream state snapshot ids

### G) Telemetry + determinism (required for ops + backtest)

- Per decision tick log (minimum): {mode, equity_cap_usdt, risk_budget_usdt, Q_base, Q_entry_eff, Q_final, size_mult, caps_hit[], primary_reason, secondary_reasons(optional), exposure_before/after{gross,net,per_symbol}, drawdown_state{daily_R, session_R, loss_streak}, thresholds_version_ts_streams, bars_ready_state, config_version}

- Events: RISK_STATE_CHANGE (daily loss/session DD/loss streak), CAP_BIND_CHANGE, SIZE_MULT_CHANGE (with tighten reason)

- Determinism: no randomness; decisions deterministic given recorded inputs and cadence

### H) Execution-aware scalping details (deltas)

- Purpose: protects small-edge scalps from costs; RiskManager owns sizing/caps; Stream Eligibility tightens only and returns Q_entry_eff

- Base sizing sketches (detail of B): RISK_FRACTION stop/ATR proxy; CONST_NOTIONAL; EQUAL_SPLIT formula; all clamped to Q_MIN_ENTRY..Q_MAX_ENTRY

- Microstructure clamps (detail of B): depth fraction (DEPTH_FRAC_CLAMP), slip cap (SLIP_CAP_CLAMP), cost_bps_entry with fee_bps_worstcase vs COST_BUDGET_BPS, shock/cooldown honoring

- Caps enforcement (detail of B): pre-trade order and post-fill exposure update; exits allowed

- Drawdown stops (detail of C): daily/session/loss-streak blocks; exits allowed

- Adaptives (detail of D): tighten-only bounds/cadence/freeze and reason tags

### I) Required inputs to collect (Spot long/flat) - summary

- Account state, exchange filters, fee_bps_worstcase, Stream Eligibility outputs (Q_entry_eff, reasons, flags, thresholds_version_ts), bars readiness/TF alignment, exposures/caps state, drawdown/loss state, replay metadata (decision_ts_ms, DECISION_LOOP_MS, config_version, stream snapshot ids)

### Audit appendix (Risk_management)

- Unique Facts Inventory: all config defaults, sizing modes/pipeline, caps/drawdown, adaptives, venue filters, inputs, telemetry, determinism, cost/fee ownership, per-symbol scope, maker-first posture retained from prior text.


## Promotion / State Constraints

- Per-symbol promotion/state: symbols must meet promotion/state rules (e.g., LIVE_COLD/HOT) based on net-of-fee/slippage edge and performance.

- Modes (SCALP/HOLD/SLEEP) and kill-switch/trading_enabled gates apply per symbol.


## Execution & Order Handling




## Data/Storage

- Sources: WS klines feeding ring buffers; REST klines for backfill/coverage repair; micro/tick features from order book/trades where available.

- Storage: DuckDB bars_1m/5m/15m/1h for closed bars (persist after signals); per-symbol params/stats in SQLite; ring buffers hold latest bars for signals.

- Retention: per Storage config; note horizons and purge behavior; ensure per-symbol coverage meets required lookbacks before trading.


## REST-Eligibility

### exchangeInfo (structural filters + scoring)

- exchangeInfo:

  - Params: permissions=["SPOT"], symbolStatus="TRADING", showPermissionSets=true.

  - Scoring (per eligible symbol, lower is better):

    - Standards/verification: tickSize prioritized (execution cost driver); constraints come from official Binance filters; percentile method is deterministic. If anything is unclear, ask for clarification.

    - Fetch params (inspect mode): GET /api/v3/exchangeInfo with permissions=["SPOT"], symbolStatus="TRADING", showPermissionSets=true. Enforce Binance rules: only one of symbol/symbols/permissions; symbolStatus cannot be combined with symbol/symbols.

    - Hard requirements (drop unless ALL true):

      - status == "TRADING"

      - SPOT permission present (permissions has "SPOT" OR permissionSets has "SPOT")

      - orderTypes contains "LIMIT", "LIMIT_MAKER", and "MARKET"

    - Required filters: PRICE_FILTER.tickSize; LOT_SIZE.stepSize and LOT_SIZE.minQty; MIN_NOTIONAL or NOTIONAL (if both, use stricter minNotional).

    - Missing handling: missing tickSize/stepSize/minNotionalStrict -> DROP; missing MAX_NUM_ORDERS/MAX_NUM_ALGO_ORDERS -> KEEP and log EXCHANGEINFO_MISSING_LIMITS (unknown; no penalty).

    - Inputs: tickSize (PRICE_FILTER); stepSize (LOT_SIZE); minNotionalStrict = max(MIN_NOTIONAL.minNotional, NOTIONAL.minNotional) if both exist else whichever exists; cancelReplaceAllowed; maxNumOrders (if present).

    - Percentiles (deterministic): sort ascending per metric; average rank for ties; rank is 0-based; p = rank/(N-1) if N>1 else 0; p in [0,1] (0 best). Compute p_tick, p_step, p_notional.

    - Weights (sum=1): w_tick=0.50; w_step=0.30; w_notional=0.20.

    - Score: score_ex = 0.50*p_tick + 0.30*p_step + 0.20*p_notional (lower better).

    - Tie-break order: smaller tickSize, then smaller stepSize, then smaller minNotionalStrict, then cancelReplaceAllowed=true first, then higher MAX_NUM_ORDERS (if present), then lexical symbol.

  - Refresh policy (fixed weights, no adaptive weights):

    - Refresh on startup; refresh every 1 hour (configurable).

    - Refresh immediately on any rule mismatch/reject: LOT_SIZE/stepSize violation; PRICE_FILTER/tickSize violation; MIN_NOTIONAL/NOTIONAL violation; invalid status/permission errors.

    - On refresh: update cached snapshot (SQLite exchange_info_symbols); recompute score_ex and sorted universe.

    - Rationale: exchangeInfo is reference/rules data; hourly + on-reject captures changes without adaptive weights; avoid tight polling on a weighted endpoint.

  - Refresh-on-reject rule (runtime, not a request param):

    - On order reject indicating rule mismatch (filter/precision/min-notional/status/permission): mark symbol_rules_stale=true (symbol-level or global if repeated); fetch exchangeInfo with fixed params; update cached rules; recompute ranking; validate intended order against updated filters before retry.

  - Additional standard rules:

    - Cache/versioning: store exchangeInfo snapshot in SQLite exchange_info_symbols; keep serverTime as exchange_info_ts (snapshot version). On startup load cached snapshot first, then refresh.

    - Notional strictness: if both MIN_NOTIONAL and NOTIONAL exist, minNotionalStrict = max of their minNotional; if neither, drop symbol.

    - Precision precedence: price must conform to PRICE_FILTER.tickSize; quantity to LOT_SIZE.stepSize; filters win over any alternate precision fields.

    - Maker eligibility: require orderTypes has both LIMIT and LIMIT_MAKER for maker-first posture.

    - Recompute score_ex only when the exchangeInfo snapshot updates (scheduled refresh or reject-trigger), not every loop.

  - Stored per symbol from exchangeInfo (static capabilities/constraints):

    - From permissions/permissionSets: supports_spot; supports_margin should be treated as false (spot-only).

    - From orderTypes: supports_limit, supports_limit_maker.

    - From filters: tickSize, stepSize, minQty, minNotionalStrict (use max of MIN_NOTIONAL/NOTIONAL if both exist, else the one present).

    - From scoring: score_ex, rank_ex.

    - Capability flag: short_entry_capability = false (spot-only; no short entries).

    - Not stored in exchangeInfo snapshot (runtime-only, computed later in universe_filter):

      - borrow_ok, margin_risk_ok, short_entry_allowed_now (margin-only concepts removed in spot-only posture).

      - Runtime: SHORT actions are exit/reduce only on spot.

    - Purpose: exchangeInfo holds static rules/capabilities; runtime eligibility is spot-only and computed in universe_filter() without margin/borrow state.

### Level 1: 24hr ticker context cache (after exchangeInfo ranking)

  - Scope: REST-only (no WS). Step 1 after exchangeInfo + score_ex; fetch 24h ticker FULL for limited symbols=[...] set, derive thresholds, apply gates, rank survivors.

  - Config constants (symbol_eligibility.level1_ticker24h.*, defaults): EPS=1e-12; ACTIVITY_ALPHA=0.35; BATCH_SYMBOLS=20; MAX_RETRIES=3; REFRESH_INTERVAL_SEC=120; MAX_TICKER_STALE_MS=2*REFRESH_INTERVAL_SEC*1000; SKEW_TOL_MS=5000; MAX_SNAPSHOT_AGE_MS=3*REFRESH_INTERVAL_SEC*1000; MIN_N_FOR_PERCENTILES=10; FAIL_STREAK_DROP=3.

  - REST collection (FULL, limited by symbols[]): symbols list = exchangeInfo-ranked candidates (after hard requirements + score_ex). Fetch via GET /api/v3/ticker/24hr with type=FULL and symbols=[...] in batches of BATCH_SYMBOLS. Do not omit symbols to fetch all. Fields returned: symbol, priceChange, priceChangePercent, weightedAvgPrice, prevClosePrice, lastPrice, lastQty, bidPrice, bidQty, askPrice, askQty, openPrice, highPrice, lowPrice, volume, quoteVolume, openTime, closeTime, firstId, lastId, count. Window: rolling 24h, not UTC day; use openTime/closeTime for cache sanity only. Refresh cadence: REFRESH_INTERVAL_SEC (default 120s).

    - Chunking/retries: transient 5xx/net errors retry up to MAX_RETRIES with fixed backoff sequence [0.5s, 1.0s, 2.0s] + jitter Uniform(0,0.25). 429: if Retry-After present, sleep = Retry-After + Uniform(0,0.25); else sleep = 2.5s + Uniform(0,0.5). No extra cap beyond MAX_RETRIES (worst-case delay is bounded). Partial failures: keep last-good rows; set ticker_stale=1; increment fail_streak.

    - Staleness/skew: if closeTime older than MAX_TICKER_STALE_MS -> mark stale and trigger refresh; tolerate small skew up to SKEW_TOL_MS, larger skew -> warn and keep snapshot.

    - Small N/warmup: if N<MIN_N_FOR_PERCENTILES, reuse last-good thresholds; if none, state=WARMUP_TICKER_THRESHOLDS and skip ticker gating this cycle (block NEW entries until READY per adaptive_required rule). Emit WARN with n_total, n_activity, and note that ticker gating was skipped this cycle because thresholds are not stabilized.

  - Store per symbol: symbol, openTime, closeTime, quoteVolume, count, volume, openPrice, highPrice, lowPrice, lastPrice, priceChangePercent. Other fields optional/not used for gating.

  - Derived per symbol: activity_score = ln(max(quoteVolume, EPS)) + ACTIVITY_ALPHA*ln(max(count,1)); range_pct_24h = (high-low)/max(low, EPS); abs_change_pct_24h = abs(priceChangePercent).

  - Thresholds (per refresh): compute activity gates on full set: MIN_QVOL_24H=P60(quoteVolume); MIN_TRADES_24H=P60(count). Let S_activity = symbols passing both. If |S_activity| < MIN_N_FOR_PERCENTILES: MIN_RANGE_PCT_24H=P25(range_pct_24h over S_activity); MAX_ABS_CHANGE_PCT_24H=P95(abs_change_pct_24h over S_activity). Else reuse last-good thresholds or set WARMUP_TICKER_THRESHOLDS (skip gating). These thresholds are adaptive_required=true with `default_source=REST_TICKER24H`, bootstrap_value=conservative block (no new entries) until READY, and adapt_state gating (READY required before allowing entries; exits allowed).

  - Eligibility (REST-only): gates are computed as above. Symbols that meet all four gates are eligible; those that do not are kept but annotated as blocked for data-driven reasons (INACTIVE_24H, RANGE_TOO_LOW, MOVE_TOO_EXTREME, TICKER_FAIL_STREAK). If the ticker thresholds adapt_state != READY, block NEW entries (exits allowed) while continuing to refresh thresholds.

  - Ranking (all symbols): sort by (1) score_ex ascending, (2) activity_score descending, (3) tie = symbol. Keep two ordered lists: eligible_symbols_rest_step1 and blocked_symbols_rest_step1 (blocked carry their reason code); do not drop blocked symbols entirely.

  - SQLite cache schema (latest only):

    - ticker24h_full_latest(symbol PK, snapshot_ts, openTime, closeTime, quoteVolume, count, volume, openPrice, highPrice, lowPrice, lastPrice, priceChangePercent, range_pct_24h, abs_change_pct_24h, activity_score, ticker_stale DEFAULT 0, fail_streak DEFAULT 0, last_error TEXT).

    - Index: CREATE INDEX IF NOT EXISTS idx_ticker24h_latest_snapshot_ts ON ticker24h_full_latest(snapshot_ts).

    - ticker24h_snapshot_state(id=1, last_refresh_ts, state OK/STALE/DEGRADED/WARMUP_TICKER_THRESHOLDS, last_ok_ts, notes).

    - ticker24h_thresholds_latest(id=1, computed_ts, min_qvol_24h, min_trades_24h, min_range_pct_24h, max_abs_change_pct_24h, n_total, n_activity).

    - rank_ex remains in exchangeInfo cache; join at query time. eligible_symbols_rest_step1 is computed each cycle (not persisted).

  - Snapshot health: on refresh failure keep last-good, state=STALE; if age>MAX_SNAPSHOT_AGE_MS state=DEGRADED and block new entries (exits still allowed). WARMUP_TICKER_THRESHOLDS means thresholds not stabilized; skip ticker gating that cycle but flag it.

  - Drop/aging: if a symbol disappears from exchangeInfo, remove from universe immediately (no rank/trade; stale row may be kept for audit only). If fail_streak >= FAIL_STREAK_DROP, exclude from ticker eligibility/ranking (reason TICKER_FAIL_STREAK) until a successful refresh resets streak; keep last data in ticker24h_full_latest with ticker_stale=1/fail_streak/last_error for reporting/debug. On successful refresh per symbol: fail_streak=0, ticker_stale=0, last_error=NULL; on failed batch/parse: fail_streak++, ticker_stale=1, last_error=<error string>.

  - WS: ignored in this step (REST-only). This cache is activity/context only; execution quality is gated later via bookTicker/depth.


## Operational Reliability & Replayability

### Account truth loop

- Ingest User Data Stream events (fills, balance updates, order updates) as primary truth.

- Run REST reconciliation on a fixed cadence (RECONCILE_SEC) to recover from missed events and reconnects.

- Maintain an idempotent position/order state machine (dedupe by clientOrderId / exchange order id); partial fills must update exposures incrementally.

### WebSocket reliability rules

- Reconnect policy: exponential backoff with jitter; bounded retry loop; emit FEED_RECONNECT event.

- Gap handling: if any stream is stale beyond its staleness cap or sequence/gap is detected, enter DECISION_FREEZE (block NEW entries; allow exits/reductions).

- Resync policy: on gap detection, resubscribe and resnapshot required streams before clearing DECISION_FREEZE.

### Rate-limit and request budget plan

- Define per-endpoint REST budgets and enforce a request scheduler (budgeted polling + reconciliation + exchangeInfo refresh).

- Degrade mode: if rate-limit risk is high, stop NEW entries and prioritize exits + reconciliation.

- Cache exchangeInfo symbol filters and refresh on a controlled interval (EXCHANGEINFO_REFRESH_MIN) or on reject spikes.

### Order lifecycle robustness (Spot long/flat)

- Idempotency: every order uses a stable clientOrderId; repeated intents must be deduped.

- Cancel/replace semantics: handle partial fills safely; do not assume cancel succeeds instantly; maintain the CANCEL_REQUESTED / INTENT_PENDING state until confirmed.

- Stuck order policy: timeout (ORDER_TTL_MS), cancel, and re-evaluate; escalate to DECISION_FREEZE on repeated rejects/timeouts.

- Long/flat constraint: never place sell quantity exceeding inventory; treat dust as inventory.

### Backtest hygiene guardrails

- Enforce strict event-time alignment; no forward-looking leakage.

- Use walk-forward splits with an out-of-sample window; document promotion criteria from paper to live.

- Record config_version + thresholds_version_ts + decision cadence to ensure deterministic replay.

### Monitoring, alerts, and kill-switch

- Alerts (minimum): feed staleness, repeated shocks/quarantine, order reject spikes, reconciliation mismatch, drawdown blocks, rate-limit pressure.

- Kill switch: manual and automatic (triggered by persistent feed failure, repeated rejects, or drawdown breach); block NEW entries; allow exits/reductions.

- Runbook: for each alert, define operator action steps and required logs to inspect.


## Stream Eligibility

### Shared Nodes (Stream Eligibility)
Stream Eligibility is a set of **shared, tighten-only nodes** (think: graph nodes) that produce **feasibility + guards**.
- These nodes **never create entry triggers**. They can only: block NEW entries, tighten sizing/caps, enforce maker-only preference, and extend cooldown/quarantine.
- Exits/reductions remain allowed under stress states (per Safety Policy).
- Cross-level reason rule still applies: the deepest failing node supplies `primary_reason` (others may be logged as secondary diagnostics).

**Node map (conceptual)**
- `SE.Shared`: global invariants, `primary_reason` precedence, validity primitives, required logging.
- `SE.CandlesBars`: bars readiness + TF owner rules; context-tightening only (no triggers).
- `SE.WS_L1`: ticker freshness/context.
- `SE.WS_L2`: bookTicker/top-of-book stability/tightness sanity.
- `SE.WS_L3_Depth`: partial depth feasibility (walk-the-book), slip/impact guards, small-cap thinness checks.
- `SE.AggTrade`: aggTrade tighten-only node for toxicity/shock/quality; computes toxicity_score, aggtrade_dq, shock_trade_burst, and constraint suggestions (taker_disallowed, entry_mode downgrade). Never a trigger.

### Risk_management (shared)

- `eligibility_state := {LIVE_HOT, LIVE_COLD, WARMUP_*, STALE_FEED, QUARANTINE, COOLDOWN_ACTIVE, SHOCK_LOCK}` (extend only if other documented states already exist elsewhere in this doc)

- `primary_reason` (+ optional `secondary_reasons[]`)

- `dq_score in [0,1]` (WS data-quality scalar; used to tighten only)

- `depth_profile_active := {HOT, COLD}` with active `(depth_levels_n, depth_speed_ms)`

- `depth_feasible_qty`, `depth_feasible_notional` (from walk-the-book feasibility for the planned side)

- `avail_notional_bid_N`, `avail_notional_ask_N` (see Level 3 metric block below)

- Optional (if already defined elsewhere in this doc): `slip_cap_bps`, `cost_budget_bps`, `impact_bps_est`

- Constraint flags: `entry_blocked` (bool), `maker_only_preferred` (bool), `taker_disallowed` (bool; tighten-only when present).

- Size caps: `max_entry_qty_cap` / `max_entry_notional_cap` (tighten-only caps derived from depth feasibility and available_notional_within_N).

**Tighten-only rule**

- `RiskManager` may only tighten based on these outputs (block entries, shrink size, apply stricter caps, maker-only preference, extend cooldown).

### Feasibility Envelope Outputs (tighten-only, for OrderEngine decisioning)

- Purpose: per-symbol per-decision-tick feasibility envelope for execution; constraints only, never triggers.

- Schema (tighten-only):

  - `eligibility_state := {LIVE_HOT, LIVE_COLD, WARMUP_*, STALE_FEED, QUARANTINE, COOLDOWN_ACTIVE, SHOCK_LOCK, ...}` (only include additional states if already referenced elsewhere in this doc)

  - `primary_reason` (+ optional `secondary_reasons`)

  - `entry_allowed` (bool) derived from state/reasons (true only if not blocked)

  - `entry_mode := {BLOCK, PROBE_ONLY, MAKER_ONLY, TAKER_OK}` (ladder guidance; still capped)

  - Constraint flags: `entry_blocked`, `maker_only_preferred`, `taker_disallowed` (tighten-only)

  - `adapt_state in {BOOTSTRAP, ADAPTING, READY, FROZEN}` per adaptive threshold set; if any `adaptive_required` item is not READY, force `entry_blocked=true` and `entry_mode=BLOCK` while continuing to compute/log; exits/reductions still allowed.

  - Depth profile: `depth_profile_active := {HOT, COLD}` with `(DEPTH_LEVELS_N, DEPTH_SPEED_MS)`; defaults reaffirmed: LIVE_HOT => N=20 @100ms; LIVE_COLD (only if required) => N=5 @1000ms; optional 50ms only via explicit config and only when needed.

  - Depth feasibility: `max_feasible_qty`, `max_feasible_notional` (walk-the-book within N)

  - Visible liquidity: `available_notional_bid_N`, `available_notional_ask_N` (explicit sums), optional `available_qty_bid_N` / `available_qty_ask_N`

  - Caps for OrderEngine: `max_entry_qty_cap`, `max_entry_notional_cap`, `max_single_order_qty`

  - Cost/slippage: `expected_slip_bps_for_Q` (for intended Q if provided), `max_slippage_bps` (tighten-only), `max_worstcase_cost_bps` (cap; align with cost budget), `max_cross_spread_ticks` (0 when maker-only)

  - Partial-fill safety: `partial_fill_timeout_ms`, `min_fill_ratio_to_continue`, `max_partial_duration_ms`, `cancel_on_partial_timeout` (bool)

  - Health scores (tighten-only, [0,1]): `dq_score` (data integrity), `liquidity_score` (book usability), `toxicity_score` (adverse-selection proxy; lightweight)

  - Re-enable hysteresis: `reenable_requires_k_good_updates`, `reenable_min_stable_ms`
  - AggTrade fields (tighten-only): `aggtrade_state in {BOOTSTRAP, ADAPTING, READY, FROZEN}`, `aggtrade_stale` (bool), `toxicity_score in [0,1]` (if aggTrade disabled -> 0 and source=DISABLED), `trade_intensity` (raw), `trade_intensity_pct` (optional), `signed_vol_imbalance in [0,1]`
  - Tape caps: `trade_notional_window` and `max_entry_notional_cap_tape` derived from aggTrade window (tighten-only)
  - Envelope validity: `envelope_version_id`, `envelope_ts_ms`, `envelope_valid_for_ms` (TTL)
  - Latency/consistency fields (tighten-only): stream_lag_ms per feed; spread_ticks; cross-stream mismatch flags (L1/L2/L3/aggTrade)

- Rule: These outputs NEVER trigger trades; they only constrain feasibility/tactics. RiskManager and OrderEngine may ONLY tighten based on them, never loosen.

### Adaptive Threshold Engine (tighten-only; deterministic)
- ThresholdSpec schema: `{name, direction MIN_FLOOR|MAX_CAP, default_source CONST|REST_EXCHANGEINFO|REST_TICKER24H|WS_OBSERVED, bootstrap_value (formula or constant), estimator fixed|cross_pctl|sym_pctl, refresh_sec, min_samples, adaptive_required, freeze_states, reset_boundary, ready_rule (deterministic), monotone_update rules}`.
- Monotone tighten-only updates:
  - MIN_FLOOR: `thr := max(prev_thr, new_thr)`
  - MAX_CAP: `thr := min(prev_thr, new_thr)`
- No intraday loosening: cross-sectional adaptives MUST NOT loosen intraday; loosening only allowed at `reset_boundary` (explicit session boundary / manual operator reset / long-stability reenable with hysteresis).
- Sample adequacy + freeze rules (L1/L2/L3 unified):
  - If `N_valid < MIN_N_FOR_PERCENTILES` -> set state=WARMUP_*; freeze threshold updates; reuse last-good; telemetry continues.
  - During STALE_FEED / WARMUP / GAP / QUARANTINE / COOLDOWN -> freeze adaptives; reuse last-good values.

### Adaptive readiness + bootstrap defaults (tighten-only, Shared/Common)
- Adaptive readiness state: `adapt_state in {BOOTSTRAP, ADAPTING, READY, FROZEN}` for each adaptive threshold set.
- Readiness gating rule: if any `adaptive_required` ThresholdSpec has `adapt_state != READY`, then `entry_blocked=true` and `entry_mode=BLOCK` (exits/reductions still allowed) while the system continues computing/logging and refreshing adaptives.
- ThresholdSpec readiness fields (deterministic):
  - `default_source` defines bootstrap: `CONST` (conservative constant), `REST_EXCHANGEINFO` (tickSize/stepSize/minQty/minNotional-derived), `REST_TICKER24H` (cross-sectional ranks), or `WS_OBSERVED` (live observations).
  - `bootstrap_value` is computed from `default_source` (e.g., `tick_bps_at_mid = 10_000 * tickSize / max(mid, EPS)` for spreads; `min_qty = stepSize`; `min_notional` from exchangeInfo).
  - `ready_rule`: `adapt_state` becomes READY only after `min_samples` AND at least one full `refresh_sec` cycle with stable values; `FROZEN` clears only at `reset_boundary` (session boundary/manual reset or long-stability reenable with hysteresis).
  - `adaptive_required` marks thresholds that must be READY before allowing new entries; non-required adaptives may remain in ADAPTING while still acting as telemetry/tightening-only if conservative defaults permit.
- Bootstrap priorities (tighten-only defaults):
  - `REST_EXCHANGEINFO` seeds staleness caps and min floors using tickSize/stepSize/minQty/minNotional (never looser than exchange filters).
  - `REST_TICKER24H` seeds liquidity tags via deterministic cross-sectional ranks (e.g., NORMAL vs SMALLCAP_THIN) with conservative defaults when ranks are unavailable.
  - `WS_OBSERVED` thresholds (e.g., spread stability, depth floors) bootstrap to conservative block values; promotion to READY requires `min_samples` VALID updates across `refresh_sec` windows.
  - ExchangeInfo-derived formulas: `tick_bps_at_mid = 10_000 * tickSize / max(mid, EPS)`, `step_size_qty = stepSize`, `min_qty = minQty`, `min_notional = minNotional` (use as hard floors/caps; never diluted by adaptives).
  - 24h ticker-derived bootstrap: rank symbols by `quoteVolume`, `count`, and `range_pct_24h` to tag liquidity class deterministically (NORMAL vs SMALLCAP_THIN); when ranks are missing, fall back to conservative constants and set adapt_state=BOOTSTRAP until enough samples arrive.
  - WS-observed bootstrap safety: when no samples exist, set bootstrap_value to a conservative block (e.g., spread caps extremely tight, depth floors high) and keep `adapt_state=BOOTSTRAP`; advance to ADAPTING/READY only after `min_samples` VALID observations across at least one `refresh_sec` window.

### Threshold Registry (Stream Eligibility)
- Purpose: mapping of thresholds/caps to config keys and ThresholdSpec; no new thresholds invented. Missing info resolves to conservative defaults (block entries) until adapted.
- Registry fields: each item lists `config_key`, `direction`, `default_source`, `estimator`, `refresh_sec`, `min_samples`, `adaptive_required` flag, `freeze_states`, `reset_boundary`, and whether it is global cross-sectional or per-symbol override.
- Staleness caps: `stream_eligibility.ws_24h_ticker.TICKER_STALE_MS`, `stream_eligibility.ws_bookticker.BOOK_STALE_MS`, `stream_eligibility.ws_depth.DEPTH_STALE_MS` (direction=MAX_CAP, default_source=CONST or REST_EXCHANGEINFO, estimator=fixed, adaptive_required=true, freeze_states=WARMUP/STALE/QUARANTINE/COOLDOWN, reset_boundary=session/manual, scope=global).
- Spread caps: `stream_eligibility.ws_bookticker.SPREAD_CAP_BPS` (direction=MAX_CAP, default_source=WS_OBSERVED bootstrap, estimator=cross_pctl, refresh_sec=THRESH_REFRESH_SEC, min_samples=MIN_N_FOR_PERCENTILES, adaptive_required=true, scope=global with per-symbol overrides allowed).
- Spread emergency/shock: `stream_eligibility.ws_bookticker.SPREAD_EMERGENCY_PCT` and/or `stream_eligibility.ws_bookticker.SPREAD_EMERGENCY_CAP_BPS` (direction=MAX_CAP, default_source=WS_OBSERVED bootstrap, estimator=cross_pctl, adaptive_required=true with conservative bootstrap blocks, scope=global).
- Stability thresholds: `stream_eligibility.ws_bookticker.stability.SPREAD_MAD_CAP`, `stream_eligibility.ws_bookticker.stability.SPREAD_JUMP_BPS`, `stream_eligibility.ws_bookticker.stability.UPD_RATE_CAP` (direction=MAX_CAP, default_source=WS_OBSERVED bootstrap, estimator=cross_pctl for SPREAD_MAD_CAP and fixed conservative constants for SPREAD_JUMP_BPS and UPD_RATE_CAP; adaptive_required=true; freeze_states per Adaptive Engine; scope=global).
- Top qty floors: `stream_eligibility.ws_bookticker.TOP_QTY_FLOOR`, `stream_eligibility.ws_bookticker.TOP_QTY_SHOCK_FLOOR` (direction=MIN_FLOOR, default_source=WS_OBSERVED bootstrap, estimator=cross_pctl, scope=global with per-symbol override).
- Min depth floor: `stream_eligibility.ws_depth.MIN_DEPTH_QUOTE` (direction=MIN_FLOOR, default_source=WS_OBSERVED bootstrap with conservative block, estimator=cross_pctl, refresh_sec=THRESH_REFRESH_SEC, min_samples=MIN_N_FOR_PERCENTILES, adaptive_required=true, scope=global with per-symbol override).
- Depth ratio shock/recover: `stream_eligibility.ws_depth.DEPTH_RATIO_SHOCK` (direction=MIN_FLOOR), `stream_eligibility.ws_depth.DEPTH_RATIO_RECOVER` (direction=MIN_FLOOR), `stream_eligibility.ws_depth.RECOVERY_CONSEC` (direction=MIN_FLOOR) (default_source=WS_OBSERVED or CONST for safety, estimator=fixed, adaptive_required=true, scope=global).
- Churn/BOOK_GAMEY: `stream_eligibility.ws_depth.CHURN_P95_CAP` (direction=MAX_CAP), `stream_eligibility.ws_depth.SPREAD_JUMP_RATE_CAP` (direction=MAX_CAP), `stream_eligibility.ws_depth.RECOVERY_CONSEC_GAMEY` (direction=MIN_FLOOR), `stream_eligibility.ws_depth.DEPTH_RATIO_RECOVER_GAMEY` (direction=MIN_FLOOR) (estimator=cross_pctl where percentile-based, otherwise fixed; default_source=WS_OBSERVED bootstrap; adaptive_required=true; scope=global with per-symbol override).
- Shock rate / replenish: `stream_eligibility.ws_depth.SHOCK_RATE_CAP`, `stream_eligibility.ws_depth.REPLENISH_MS_CAP`, `stream_eligibility.ws_depth.W_shock_min`, `stream_eligibility.ws_depth.COOLDOWN_SEC` (direction=MAX_CAP for rates/times; estimator=fixed; default_source=CONST; scope=global).
- Slip/cost caps: `stream_eligibility.ws_depth.SLIP_CAP_BPS`, `stream_eligibility.ws_depth.LOG_COST_ON_INSUFF_DEPTH`, `risk_manager.COST_BUDGET_BPS`, `stream_eligibility.ws_depth.FEE_BPS_WORSTCASE`, `max_worstcase_cost_bps` (direction=MAX_CAP where applicable; estimator=fixed; default_source=CONST; freeze_states per Adaptive Engine; scope=global).
- Depth profile defaults: `DEPTH_LEVELS_N`/`DEPTH_SPEED_MS` profiles (HOT/COLD) (direction=fixed profile; default_source=CONST).
 - Segmented percentiles: optional class-segmented percentiles by liquidity tag (OFF by default); if per-class sample size is insufficient, fall back to global percentiles and freeze per-class adaptives until sufficient samples.
 - AggTrade toxicity/quality (tighten-only):
   - `stream_eligibility.aggtrade.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=false).
   - `stream_eligibility.aggtrade.WINDOW_SEC` (direction=fixed, default_source=CONST, bootstrap_value=30).
   - `stream_eligibility.aggtrade.MIN_TRADES_FOR_READY` (direction=MIN_FLOOR, default_source=CONST, bootstrap_value=20).
   - `stream_eligibility.aggtrade.K_STABLE_WINDOWS` (direction=MIN_FLOOR, default_source=CONST, bootstrap_value=3).
   - `stream_eligibility.aggtrade.STALE_MS` (direction=MAX_CAP, default_source=CONST, bootstrap_value=3000).
   - Toxicity weights: `stream_eligibility.toxicity.W_IMBALANCE` (direction=fixed, default_source=CONST, bootstrap_value=0.4), `stream_eligibility.toxicity.W_INTENSITY_PCT` (direction=fixed, default_source=CONST, bootstrap_value=0.4), `stream_eligibility.toxicity.W_DEPLETION_PCT` (direction=fixed, default_source=CONST, bootstrap_value=0.2).
   - Toxicity thresholds (tighten-only): `stream_eligibility.toxicity.TOXICITY_BLOCK` (direction=MIN_FLOOR on riskiness, default_source=CONST, bootstrap_value=0.80), `TOXICITY_PROBE` (MIN_FLOOR, bootstrap_value=0.60), `TOXICITY_MAKER` (MIN_FLOOR, bootstrap_value=0.40). If toxicity_score >= threshold -> downgrade mode per ladder; never loosen.
   - Consistency gates: `stream_eligibility.consistency.TRADE_L1_MISMATCH_X_TICKS` (direction=fixed, default_source=CONST, bootstrap_value=2), `TRADE_L1_MISMATCH_Y_SPREAD_MULT` (direction=fixed, default_source=CONST, bootstrap_value=1.0), `TRADE_L1_MISMATCH_Z_EVENTS` (direction=MIN_FLOOR, default_source=CONST, bootstrap_value=3), `BOOK_FREEZE_STALE_MS` (direction=MAX_CAP, default_source=CONST, bootstrap_value=2000), `TAPE_BURST_INTENSITY_PCT` (direction=MIN_FLOOR on riskiness, default_source=CONST, bootstrap_value=0.90), `BOOK_VACUUM_DEPTH_RATIO_FLOOR` (direction=MIN_FLOOR, default_source=CONST, bootstrap_value=0.30), `stream_eligibility.aggtrade.K_TAPE_NOTIONAL_MULT` (direction=MAX_CAP on notional cap multiplier, default_source=CONST, bootstrap_value=0.25).
   - Envelope TTL: `stream_eligibility.envelope.TTL_MS` (direction=MAX_CAP on age, default_source=CONST, bootstrap_value=1000).
   - Markout feedback: `stream_eligibility.markout.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=false), `stream_eligibility.markout.NEG_THRESHOLD_BPS` (direction=MIN_FLOOR on riskiness, default_source=CONST, bootstrap_value=-5), `stream_eligibility.markout.PERSIST_N_TRADES` (direction=MIN_FLOOR, default_source=CONST, bootstrap_value=3), `stream_eligibility.markout.COOLDOWN_MS` (direction=MAX_CAP on cooldown, default_source=CONST, bootstrap_value=60000).
   - Cliff detector: `stream_eligibility.cliff.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=true), `stream_eligibility.cliff.TOP2_RATIO_MAX` (direction=MAX_CAP on ratio, default_source=CONST, bootstrap_value=0.70), `stream_eligibility.cliff.DEPTH_DROP_PCT_TRIGGER` (direction=MIN_FLOOR on drop risk, default_source=CONST, bootstrap_value=0.30), `stream_eligibility.cliff.WINDOW_SEC` (direction=fixed, default_source=CONST, bootstrap_value=10).
   - Coupling rule: `stream_eligibility.coupling.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=true), `stream_eligibility.coupling.INTENSITY_PCT_TRIGGER` (direction=MIN_FLOOR on riskiness, default_source=CONST, bootstrap_value=0.85), `stream_eligibility.coupling.SPREAD_WIDEN_PCT_TRIGGER` (direction=MIN_FLOOR on riskiness, default_source=CONST, bootstrap_value=1.50), `stream_eligibility.coupling.WINDOW_SEC` (direction=fixed, default_source=CONST, bootstrap_value=10).
  - Granularity/latency: `stream_eligibility.granularity.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=true), `stream_eligibility.granularity.SPREAD_TICKS_MAKER` (direction=MIN_FLOOR on permissiveness cap, default_source=CONST, bootstrap_value=1), `SPREAD_TICKS_PROBE` (MIN_FLOOR, bootstrap_value=2), `SPREAD_TICKS_BLOCK` (MIN_FLOOR, bootstrap_value=4); `stream_eligibility.latency.ENABLED` (direction=fixed, default_source=CONST, bootstrap_value=true), `stream_eligibility.latency.LAG_WARN_MS` (direction=MAX_CAP, default_source=CONST, bootstrap_value=500), `stream_eligibility.latency.LAG_HARD_BLOCK_MS` (direction=MAX_CAP, default_source=CONST, bootstrap_value=1000).
  - Envelope TTL governance: `stream_eligibility.envelope.TTL_MS_DEFAULT` (direction=MAX_CAP on age, default_source=CONST, bootstrap_value=1000), `stream_eligibility.envelope.TTL_MS_MIN` (direction=MAX_CAP on age, default_source=CONST, bootstrap_value=250), `stream_eligibility.envelope.TTL_SHRINK_ON_OPS_DEGRADE` (direction=fixed, default_source=CONST, bootstrap_value=true), `stream_eligibility.envelope.TTL_SHRINK_ON_MISMATCH` (direction=fixed, default_source=CONST, bootstrap_value=true).

### Entry Ladder Policy (deterministic mapping; tighten-only)

- Deterministic mapping for `entry_mode` (constraints only; OrderEngine decides tactics):

  - BLOCK: dq too low OR WARMUP/STALE/GAP/QUARANTINE/SHOCK/COOLDOWN gates OR bars not ready OR NONFINITE_SLIP OR INSUFFICIENT_VISIBLE_DEPTH OR venue infeasible.

  - PROBE_ONLY: data OK but liquidity_score low OR toxicity_score high OR spread instability elevated; allow only tiny maker probe with strict partial-fill constraints.

  - MAKER_ONLY: default caution; maker-only with caps/timeouts; no crossing (`max_cross_spread_ticks=0`).

  - TAKER_OK: only if dq_score high, liquidity_score high, toxicity_score low, spread stable, and `worstcase_cost_bps <= max_worstcase_cost_bps`; still capped.

- Hysteresis: upgrades require `reenable_requires_k_good_updates` AND `reenable_min_stable_ms`; downgrades can occur immediately on new faults.

- Toxicity downgrades (combine with ladder via minimum-permissive-mode): if `toxicity_score >= TOXICITY_BLOCK` -> `entry_mode=BLOCK`; else if `toxicity_score >= TOXICITY_PROBE` -> at most PROBE_ONLY; else if `toxicity_score >= TOXICITY_MAKER` -> at most MAKER_ONLY; otherwise no toxicity-based downgrade. If `aggtrade_state != READY`, default to taker_disallowed=true OR entry_mode <= MAKER_ONLY (no toxicity-based upgrades until READY).

### Mode Reducer (min-permissive wins)
- Start from the most permissive mode allowed by current policy (typically TAKER_OK).
- Apply reducers in fixed order; each can only downgrade:
  1) Hard blocks: WARMUP/STALE/GAP/QUARANTINE/SHOCK/NONFINITE_SLIP/COOLDOWN
  2) dq_score/mismatch gates (including cross-stream consistency)
  3) liquidity_score gates
  4) toxicity_score gates (aggTrade)
  5) cost/slippage budget gates
  6) candle timing / regime gates (if referenced)
- Final mode = minimum permissive after reducers. OrderEngine must not override; it may choose to do less (skip), not more.

- Components:

  - `spread_cost_bps`: (ask - bid)/mid * 10_000 (use best bid/ask).

  - `fee_bps`: config (taker worst-case unless maker guaranteed).

  - `expected_slip_bps`: walk-the-book for intended Q (or conservative proxy).

  - `buffer_bps`: config safety margin.

  - `worstcase_cost_bps = spread_cost_bps + fee_bps + expected_slip_bps + buffer_bps`.

- Tightening rules:

  - If `worstcase_cost_bps > max_worstcase_cost_bps` -> downgrade entry_mode in order: TAKER_OK -> MAKER_ONLY -> PROBE_ONLY -> BLOCK.

  - Enforce `max_cross_spread_ticks`: 0 when maker-only; bounded (config) when taker is allowed.

- Constraint-only: never a trigger; only blocks/shrinks or downgrades modes.

### Partial Fill Safety Semantics (tighten-only state semantics)

- States:

  - PARTIAL_PENDING: starts on first fill.

  - PARTIAL_STALLED: `partial_fill_timeout_ms` exceeded OR fill_ratio < `min_fill_ratio_to_continue`.

- Required constrained actions:

  - Cancel remainder when stalled or when `max_partial_duration_ms` reached; do not escalate into forbidden taker actions.

  - If exposure is unacceptable per risk rules, allow risk-driven reduce/exit only (OrderEngine executes within caps).

- Hard bound: `max_partial_duration_ms` is a strict limit; after it, remainder must be canceled and exposure managed per risk rules.

### Computing the Feasibility Envelope (notes)

- `available_notional_side_N = sum_{i=1..N} (px_i * qty_i)` on the relevant side; optional `avail_qty_side_N = sum_{i=1..N} qty_i`.

- Walk-the-book VWAP for target Q (BUY example): accumulate asks until `cum_qty >= Q`; `px_vwap = (sum px_i * fill_qty_i) / Q`; `slip_bps = ((px_vwap - mid)/mid) * 10_000`; if not fillable within N -> `NONFINITE_SLIP` / `INSUFFICIENT_VISIBLE_DEPTH`; emit `expected_slip_bps_for_Q`, `max_feasible_qty`, `max_feasible_notional`.

- Caps (`max_entry_qty_cap` / `max_entry_notional_cap`): min of depth feasibility (`max_feasible_qty`), available-notional cap (`k * avail_notional_side_N`, k bounded/configured), venue min/max/step/notional, and regime/risk caps from RiskManager.

- `dq_score` (tighten-only): maintain incident counters (gap/stale/invalid/mismatch) over a rolling horizon (e.g., 10-60s). Start dq=1.0; each incident: `dq *= (1 - penalty)` (penalty 0.05-0.20 by severity); recover slowly with `dq += recover_rate * dt`; clamp [0,1]; lower dq tightens only.

- `liquidity_score` (tighten-only): combine normalized/percentile features: spread level pct, spread volatility pct, available_notional pct, short-horizon realized vol pct. Example: `badness = mean([spread_pct, spread_vol_pct, vol_pct, (1 - depth_pct)])`; `liquidity_score = 1 - badness`, clamp [0,1] with hard bounds to prevent drift.

- `toxicity_score` (tighten-only): lightweight proxy combining trade intensity pct (vol/sec), signed volume imbalance (`abs(sum sign*vol)/sum vol`), and best-level depletion-rate pct; `toxicity_score = clamp(w1*imbalance + w2*intensity_pct + w3*depletion_pct, 0..1)`.

### Cross-Stream Consistency Gates (tighten-only)
- TRADE_L1_MISMATCH: if aggTrade price repeatedly falls outside `[best_bid - X*tick, best_ask + X*tick]` OR outside `mid +/- Y*spread` for Z events in a window, set `primary_reason=TRADE_L1_MISMATCH` (unless a deeper reason exists), decrement dq_score, and downgrade `entry_mode`. Defaults: `TRADE_L1_MISMATCH_X_TICKS=2`, `TRADE_L1_MISMATCH_Y_SPREAD_MULT=1.0`, `TRADE_L1_MISMATCH_Z_EVENTS=3`.
- BOOK_FREEZE_MISMATCH: if L1 updates continue but L2/L3 stall beyond `BOOK_FREEZE_STALE_MS` (or vice versa), flag mismatch, tighten dq_score, and downgrade entry_mode.
- TAPE_BURST_BOOK_VACUUM: if `trade_intensity_pct` is high AND `available_notional_side_N` falls below a floor/baseline, downgrade entry_mode (at most PROBE_ONLY / MAKER_ONLY per ladder).
- All checks are tighten-only: never upgrade, respect freeze/sample adequacy (no upgrades until READY), and combine via the mode reducer (minimum permissive wins).

### Spread-to-Tick Granularity Guard (tighten-only)
- `spread_ticks = (best_ask - best_bid) / tickSize` (ceil).
- If `spread_ticks >= SPREAD_TICKS_BLOCK` -> `entry_mode=BLOCK`; else if `spread_ticks >= SPREAD_TICKS_PROBE` -> at most PROBE_ONLY; else if `spread_ticks >= SPREAD_TICKS_MAKER` -> at most MAKER_ONLY. Defaults (CONST): ENABLED=true, `SPREAD_TICKS_MAKER=1`, `SPREAD_TICKS_PROBE=2`, `SPREAD_TICKS_BLOCK=4`.
- Combine via mode reducer (minimum permissive wins); never upgrade.

### Latency Mismatch Gate (tighten-only)
- For each stream (L1/L2/L3/aggTrade), compute `stream_lag_ms = now_ts_ms - event_ts_ms` when timestamps exist.
- If any `stream_lag_ms > LAG_HARD_BLOCK_MS` -> downgrade to BLOCK for entries; exits allowed.
- If any `stream_lag_ms > LAG_WARN_MS` -> tighten dq_score, shorten envelope TTL, require stricter reenable.
- Defaults (CONST): ENABLED=true, `LAG_WARN_MS=500`, `LAG_HARD_BLOCK_MS=1000`. Follows adaptive freeze rules; never loosens.
### aggTrade Toxicity & Shock (tighten-only)
- Window: `stream_eligibility.aggtrade.WINDOW_SEC` (default 30s).
- Signed volume imbalance:
  - `v_buy = Sigma qty` over window for buyer-initiated trades; `v_sell = Sigma qty` for seller-initiated trades.
  - `imbalance = abs(v_buy - v_sell) / (v_buy + v_sell + EPS)`.
  - If side is unavailable, use existing side inference (tick rule); if unavailable, default imbalance=0 (conservative).
- Trade intensity:
  - `intensity = (v_buy + v_sell) / WINDOW_SEC`.
  - `intensity_pct = percentile(intensity)` using rolling per-symbol history (adaptive; winsorize at rolling p99 to avoid single-print distortion).
- Optional depletion proxy: `depletion_pct = percentile(best_level_depletion_rate)` if L2/L3 provides it; else 0.
- Toxicity score:
  - `toxicity_score = clamp(W_IMBALANCE * imbalance + W_INTENSITY_PCT * intensity_pct + W_DEPLETION_PCT * depletion_pct, 0..1)`.
- Shock/quality flags:
  - `shock_trade_burst` if intensity_pct exceeds a burst cap; `aggtrade_dq` tightens dq_score on out-of-order/duplicate bursts.
- Tighten-only actions: downgrade entry_mode per toxicity ladder, set `taker_disallowed=true`, shrink caps/partial-fill patience; never create triggers.
- Readiness rule: if `aggtrade_state != READY`, default to taker_disallowed=true or entry_mode <= MAKER_ONLY and do not upgrade based on aggTrade; still compute and log.

- Data integrity & mismatch (aggTrade):
  - Dedup/order: maintain last_trade_id; ignore duplicates or older ids. If out-of-order bursts exceed threshold, decrement dq_score and set `aggtrade_state=FROZEN` temporarily.
  - Staleness: `aggtrade_stale=true` if no aggTrade update for `STALE_MS` while other WS streams are active.
  - Mismatch: if aggTrade is stale while L1/L2/L3 active OR aggTrade active while L1/L2/L3 stale, treat as mismatch -> tighten dq_score and potentially downgrade entry_mode.
  - Freeze: during STALE_FEED/WARMUP/GAP/QUARANTINE/COOLDOWN, freeze aggTrade adaptives; reuse last-good; never upgrade modes from aggTrade during freeze.

- Tape-to-feasible-size cap (tighten-only):
  - `trade_notional_window = Sigma(price*qty)` over aggTrade window.
  - `max_entry_notional_cap_tape = K_TAPE_NOTIONAL_MULT * trade_notional_window`.
  - Final `max_entry_notional_cap = min(existing caps, max_entry_notional_cap_tape)`.
  - If aggTrade not READY, default conservative: cap to 0 (block entries) or very small until READY (bootstrap K is small constant).

### Envelope Snapshot Validity (tighten-only)
- `envelope_version_id` increments per symbol per refresh; `envelope_ts_ms` records snapshot time; `envelope_valid_for_ms` (TTL) defines validity window.
- OrderEngine may only act if `(now_ms - envelope_ts_ms) <= envelope_valid_for_ms`; otherwise must revalidate/refresh before sending.
- Config default: `stream_eligibility.envelope.TTL_MS` (CONST, conservative default 1000 ms).

### Envelope TTL Governance (tighten-only)
- TTL shrinks when ops health degrades (high ack latency/reject/cancel-fail/rate-limit hits), when cross-stream mismatch/latency flags fire, or during shocks/volatility spikes. Exits remain allowed.
- TTL returns to default only at `reset_boundary` or after a long stability window satisfying `reenable_requires_k_good_updates` and `reenable_min_stable_ms`; never loosen intraday without stability proof.
- Config (CONST defaults): `stream_eligibility.envelope.TTL_MS_DEFAULT=1000`, `stream_eligibility.envelope.TTL_MS_MIN=250`, `stream_eligibility.envelope.TTL_SHRINK_ON_OPS_DEGRADE=true`, `stream_eligibility.envelope.TTL_SHRINK_ON_MISMATCH=true`.

### Markout Feedback Contract (tighten-only)
- Telemetry inputs from OrderEngine (optional): `markout_1s_bps`, `markout_5s_bps`, `markout_30s_bps` (per mode if available).
- Tighten-only rules: persistent negative markout beyond threshold => increase buffer_bps, downgrade entry_mode ceiling, shrink caps for a cooldown window.
- Config defaults: `stream_eligibility.markout.ENABLED` (CONST=false), `stream_eligibility.markout.NEG_THRESHOLD_BPS` (CONST=-5), `stream_eligibility.markout.PERSIST_N_TRADES` (CONST=3), `stream_eligibility.markout.COOLDOWN_MS` (CONST=60000).

### Upstream Telemetry Inputs (tighten-only)
- Inputs from OrderEngine: ops_health (ack_latency_p95/p99, reject_rate, cancel_fail_rate, reconnect_count, rate_limit_hits), execution_quality (realized_slip_bps, fees_bps, fill_latency_ms_p95/p99), markouts (1s/5s/30s bps when enabled).
- Tightening actions: ops degradation -> shorten envelope TTL, lower `entry_mode` ceiling, shrink caps, increase dq penalties; poor execution_quality vs expected -> raise buffer_bps, tighten cost budgets and caps; negative markout persistence -> downgrade mode/caps/buffers. Never loosens intraday; follows Adaptive Threshold Engine monotone rules with loosening only at `reset_boundary`/hysteresis.

### Micro-Liquidity Cliff Detector (tighten-only)
- Metrics: `top2_notional_ratio = (notional_L1 + notional_L2) / notional_topN`; `depth_drop_rate = drop in available_notional_side_N over window`.
- If `top2_notional_ratio` exceeds `TOP2_RATIO_MAX` OR `depth_drop_rate` exceeds `DEPTH_DROP_PCT_TRIGGER`, downgrade entry_mode (at most PROBE_ONLY), tighten `max_single_order_qty`, and shorten partial-fill timeouts.
- Config defaults: `stream_eligibility.cliff.ENABLED` (CONST=true), `stream_eligibility.cliff.TOP2_RATIO_MAX` (CONST=0.70), `stream_eligibility.cliff.DEPTH_DROP_PCT_TRIGGER` (CONST=0.30), `stream_eligibility.cliff.WINDOW_SEC` (CONST=10).

### Tape/Spread Coupling (tighten-only)
- If `trade_intensity_pct >= INTENSITY_PCT_TRIGGER` AND `spread_bps >= SPREAD_WIDEN_PCT_TRIGGER`, set `taker_disallowed=true` and downgrade entry_mode (at most MAKER_ONLY/PROBE_ONLY per ladder).
- Config defaults: `stream_eligibility.coupling.ENABLED` (CONST=true), `stream_eligibility.coupling.INTENSITY_PCT_TRIGGER` (CONST=0.85), `stream_eligibility.coupling.SPREAD_WIDEN_PCT_TRIGGER` (CONST=1.50), `stream_eligibility.coupling.WINDOW_SEC` (CONST=10).

- `entry_mode` ladder (recommendation; OrderEngine decides): BLOCK if dq very low or SHOCK/QUARANTINE/WARMUP/STALE/bars not ready; PROBE_ONLY if data ok but liquidity_score low or toxicity_score high (tiny maker probe only); MAKER_ONLY as default caution; TAKER_OK only when stability is high and caps still hold (rare).

- Partial-fill constraints (tighten-only): `partial_fill_timeout_ms`, `min_fill_ratio_to_continue`, `max_partial_duration_ms`, `cancel_on_partial_timeout`; shorten timeouts / increase cancel likelihood when liquidity_score is low or toxicity_score high; allow slightly longer patience only when liquidity_score is strong and toxicity_score low.
  - Toxicity integration: when `toxicity_score` is elevated, tighten `partial_fill_timeout_ms` (shorter), increase `min_fill_ratio_to_continue`, and reduce `max_single_order_qty` if allowed by config; never loosen on toxicity.

- Re-enable hysteresis (exiting STALE/QUARANTINE/SHOCK): `reenable_requires_k_good_updates`, `reenable_min_stable_ms` tighten when exiting stress; require consecutive good updates and minimum stability time before lifting constraints.

### Ownership boundaries (Stream Eligibility vs RiskManager vs OrderEngine)
- Principle: Stream Eligibility produces constraints; OrderEngine produces outcomes. Stream Eligibility MUST NOT generate entry/exit triggers. OrderEngine MUST NOT compute regimes/indicators/depth feasibility/dq_score; it only consumes constraints and reports telemetry upward.
- Ownership split:
  - Stream Eligibility (tighten-only): data readiness (bars warmup/stale/gap/TF readiness, WS freshness/continuity/mismatch), `dq_score` and data-integrity blocks, microstructure feasibility (spread/tightness stability, depth walk feasibility, available_notional_within_N, slip/impact feasibility labels), outputs/flags (`eligibility_state`, `primary_reason`, constraint flags such as entry_blocked/maker_only_preferred/taker_disallowed, max feasible size/notional caps, min reenable rules).
  - RiskManager: position sizing pipeline (base -> clamps -> caps -> final), drawdown/loss-streak brakes and portfolio/cluster caps (if present), stop/vol-stop policy selection (conceptual; actual placement is OrderEngine).
  - Executor/OrderEngine: all exchange interaction (place/cancel/amend, idempotency, reconciliation, partial fills), rate limits/backoff/reconnects/timeouts, execution mechanics within constraints (maker/taker, post-only, price offsets, slicing/pacing), execution telemetry (realized slippage, fill latency, reject/cancel failures, ops_health).
- Where does X go' (quick map):
  - stale WS / gap / mismatch / dq_score -> Stream Eligibility
  - spread too wide / tightness unstable / depth thin / nonfinite slip -> Stream Eligibility
  - maker-only preference / taker ban / max entry notional -> Stream Eligibility (constraints)
  - order slicing / cancel-replace / retry / post-only implementation -> OrderEngine
  - rate limits / reconnect / idempotency -> OrderEngine
  - drawdown / loss streak / portfolio caps -> RiskManager
  - stops/TP placement & emergency exits -> OrderEngine (triggered by RiskManager/position rules)

### 0) Shared conventions (applies to all WS levels)
- Freshness: use local arrival timestamps (ms) for staleness checks; each level has its own stale threshold.
- EPS: use EPS=1e-12 in all divisions; require finite values (no NaN/Inf).
- Pattern: Config per level; State is runtime (reset on restart unless intentionally persisted); Valid set gates percentile recompute; Warmup/stress reuse last-good thresholds; Demotion is logical (unsubscribe optional); Visibility via per-level logger with state/counts.
- Percentile scope:
  - Pxx(x) = CROSS-SECTIONAL percentile across the current VALID symbol set at refresh time.
  - Pxx_sym(x) = per-symbol TIME-SERIES percentile over a long window W_sym_sec (used only in per-symbol overrides).
- Cross-level primary reason rule:
  - Primary_reason is the reason code from the deepest level reached (L3 if depth active, else L2, else L1). Secondary_reasons are optional diagnostics; emit one primary per symbol per evaluation.
- Warmup/stress trading policy:
  - During any WARMUP_* or STALE_FEED state, block NEW entries (reason WARMUP_* or STALE_FEED); exits/reductions remain allowed.
- Adaptive readiness policy:
  - If any `adaptive_required` threshold is not in `adapt_state=READY`, block NEW entries (`entry_mode=BLOCK`, `entry_blocked=true`) while continuing to compute/log; exits/reductions remain allowed.

### 1) Candles/Bars Stream (TF Coverage + Roles + Redundancy Control)

#### 1.0 Parent Node: Purpose, Scope, Non-Negotiables

##### 1.0.1 Scope
- Candles/Bars are **context + tighten-only**. They must **never** become a second trigger.
- The entry trigger lives outside candles (e.g., Hybrid). Candles decide **permission / direction context / structure validity / execution hygiene** only.

##### 1.0.2 Safety Policy
- Under any of: WARMUP / STALE / GAP / Stress / Cooldown / Quarantine -> **Block NEW entries, allow exits/reductions**.
- Long/Flat: entries are **LONG-only**; bearish context => prefer **FLAT** (never "short as entry").

##### 1.0.3 Anti-Redundancy (Owner Rule)
- One concept -> one owner TF:
  - **H1** owns macro regime + volatility regime + macro zones (permission).
  - **M15** owns market direction/bias for LONG entries (direction context).
  - **M5** owns intraday validity/structure quality (validity).
  - **M1** owns micro-safety/hygiene (spike/trap).
- Non-owners can only contribute **modifiers** (tightening), not independent confirmations.

---

#### 1.1 Parent Node: Shared Bottom-Up Primitives (Define Once, Reuse Upward)

##### 1.1.1 Data & Closed-Bar Rule
- All TF decisions that gate entries must be based on **closed bars** (event-time aligned).
- No intrabar logic in Candles: all candle-based pass/fail states are computed from last **closed** bars only.

##### 1.1.2 Normalization Primitives
- `EPS := 1e-12`
- `bps(x) := 10_000 * x`
- `dist_bps(price, ref) := 10_000 * (price - ref) / max(ref, EPS)`
- `atr_units(x, ATR) := x / max(ATR, EPS)`
- `percentile_rank(x, {x_{t-W+1..t}}) in [0,100]` (time-series rank)
- `Pxx({values}) := percentile(values, xx)` (time-series percentile, per symbol)

##### 1.1.4 Bar Validity Primitives
Maintain per TF:
- `n_closed_bars_TF`
- `last_bar_close_ts_TF` (timestamp of last **closed** bar)
- expected close timestamps derived from TF cadence (exchange clock)
- `missing_bars_count_TF`

Compute:
- `BAR_WARMUP(TF) := (n_closed_bars_TF < LOOKBACK_TF_required)`
- `stale_ms_TF := now_ms - last_bar_close_ts_TF`
- `BAR_STALE(TF) := (stale_ms_TF > BAR_STALE_MS_TF[TF])`
- `BAR_GAP(TF) := (missing_bars_count_TF > BAR_GAP_MAX_MISSING_BARS_TF[TF])`

Entry policy:
- If **ANY** TF in `REQUIRED_TFS_HOT(active profile)` is WARMUP/STALE/GAP -> **block NEW entries** (reason = BAR_WARMUP/BAR_STALE/BAR_GAP).
- Exits/reductions always allowed.

##### 1.1.5 Adaptive readiness (candles/regime thresholds)
- Candles/regime adaptive thresholds follow `adapt_state in {BOOTSTRAP, ADAPTING, READY, FROZEN}` (same ladder as Stream Eligibility).
- If any candle/regime threshold marked `adaptive_required` is not READY -> block NEW entries (`entry_mode=BLOCK`, `entry_blocked=true`); exits/reductions remain allowed while adaptives continue computing/logging.

#### Candles Symbol State (Entries Only; Exits Always Allowed)

- Purpose:
  - Candles-only tradability label for NEW entries (not an execution/WS label). Exits/reductions always allowed.

- States:
  - CANDLES_HOT (entry-eligible):
    - All TFs in the active REQUIRED_TFS_HOT profile are VALID (not BAR_WARMUP/STale/GAP)
    - H1 has no regime veto and macro_zone_risk is not NO_TRADE (tighten-only zones)
    - M5 structure_valid is VALID
    - M1 micro_spike_flag = false and trap_flag = false
    - align != 0 (no TF_CONFLICT)

  - CANDLES_WARM (caution / tightened):
    - Validity OK, but tightening modifiers present:
      - align = 1 (TF_MIXED), or
      - M15 mr_risk_flag true (stretch caution), or
      - H1 regime TRANSITION, or
      - M5 structure_valid = WEAK
    - Policy: allow entries only if RiskManager already tightened sizing and all non-candle gates are green.

  - CANDLES_COLD (block entries):
    - Any REQUIRED_TFS_HOT TF is BAR_WARMUP/BAR_STALE/BAR_GAP, OR
    - H1_REGIME_VETO / macro NO_TRADE zone, OR
    - M5_STRUCTURE_INVALID, OR
    - MICRO_SPIKE / TRAP_FLAG, OR
    - align = 0 (TF_CONFLICT)

- Reason codes mapping (candles-only):
  - HOT: none (or CANDLES_OK)
  - WARM: TF_MIXED, VWAP_STRETCH_CAUTION, H1_TRANSITION, M5_WEAK
  - COLD: BAR_WARMUP, BAR_STALE, BAR_GAP, H1_REGIME_VETO, H1_MACRO_ZONE_RISK, M5_STRUCTURE_INVALID, MICRO_SPIKE, TRAP_FLAG, TF_CONFLICT

##### 1.1.6 Direction Sign Primitive (Long/Flat semantics)
Define `bias_sign in {-1,0,+1}`:
- `+1` supportive for LONG entries
- `0` neutral / unclear
- `-1`  LONG (prefer FLAT; treat as conflict for LONG entries when direction is required)

Tie-break:
- If any hard veto is active (H1 veto, M5 invalid, M1 unsafe, or HOT validity failed) -> block entries regardless of bias_sign.

---

#### 1.2 Parent Node: Coverage & Required TF Sets (Hot/Cold)

##### 1.2.1 Recommended Coverage Targets (defaults only)
- Hot lookbacks (deeper):
  - M1: 600 bars (~10h)
  - M5: 480 bars (~40h / ~1-2d)
  - M15: 384 bars (~96h / ~2-4d)
  - H1: 336 bars (~14d)
- Cold lookbacks (lighter):
  - M1: 300 bars (~5h)
  - M5: 240 bars (~20h / ~1d)
  - M15: 192 bars (~48h / ~2d)
  - H1: 168 bars (~7d)

##### 1.2.2 Required TFs (Profile-dependent)
- `REQUIRED_TFS_COLD` default = `{H1}`

Profile required HOT sets:
- `REQUIRED_TFS_HOT_MICRO` default = `{M1, M5}`
- `REQUIRED_TFS_HOT_MINI`  default = `{M1, M5, M15}`

Per-symbol overrides MUST explicitly specify:
- required sets (HOT_MICRO / HOT_MINI / COLD)
- LOOKBACK per TF (and per profile if different)
- BAR_STALE_MS_TF per TF
- BAR_GAP_MAX_MISSING_BARS_TF per TF

#### Horizon Hybrid Profiles (Candles-only; for 1-20 minute scalps)

- This adds horizon behavior without changing TF roles or indicators (Reference: TF roles + Indicator Suite already defined above).
- Two profiles (same TF roles; different HOT requirements + strictness):

  - MICRO profile (~1-5 min):
    - REQUIRED_TFS_HOT_MICRO default = {M1, M5}
    - M15/H1 remain COLD veto-only context unless explicitly promoted per symbol.
    - Priority: M1 micro-safety + M5 structure validity (avoid noise).

  - MINI_SWING profile (~6-20 min):
    - REQUIRED_TFS_HOT_MINI default = {M15, M5, M1}
    - H1 remains COLD permission + macro-zone tightening; may hard-veto entries.
    - Priority: M15 bias context + M5 structure + M1 hygiene.

- Profile selection (tighten-only):
  - If M1 micro_spike_flag OR trap_flag is true -> force MICRO behavior.
  - If H1 permissive AND M15 aligned AND M5 structure_valid -> allow MINI_SWING behavior.
  - Never loosen: profile selection can only tighten tradability, never create permission.

---

#### 1.3 Parent Node: Horizon Controller (Micro-First, Promote to Mini-Swing)

##### 1.3.1 Profiles
- **MICRO (default; 1-5 min intent)**
  - Goal: take only clean micro opportunities, avoid bad minutes.
  - HOT required: `{M1, M5}`
  - M15/H1: veto-only context unless explicitly promoted per symbol.

- **MINI_SWING (promoted; 6-20 min intent)**
  - Goal: allow longer holds only when direction + structure + regime are clean.
  - HOT required: `{M1, M5, M15}`
  - H1 remains COLD permission + macro zones; may hard-veto.

##### 1.3.2 Promotion Rules (MICRO -> MINI_SWING)
Promote only if ALL (based on CLOSED bars only):
- Bar validity OK for all TFs in `REQUIRED_TFS_HOT_MINI`
- H1 has **no regime veto**, and H1 is not CHAOTIC/AVOID (defined in H1 outputs below)
- M15 `bias_sign_M15 = +1` (Long-aligned) AND stretch is not extreme
- M5 `structure_valid = VALID` (not WEAK/INVALID)
- M1 safety persists for `K_confirm` closed M1 bars:
  - `micro_safe_persist := consecutive_closed(M1_safe == true) >= K_confirm`
  - default `K_confirm = 2` (configurable)

##### 1.3.3 Demotion Rules (MINI_SWING -> MICRO)
Demote immediately if ANY:
- M1 unsafe (spike/trap)
- M5 becomes WEAK/INVALID
- M15 flips to 0 or -1, or stretch becomes extreme
- H1 enters EXPANSION/CHAOTIC/AVOID or macro no-trade zone

Tighten-only: promotion expands permission; demotion is immediate risk response.

##### 1.3.4 Micro-first Ordering (Small -> Large) + Sub-minute Handling (No Intrabar)

###### 1.3.4.1 Principle (Filter Chain, Not Multiple Triggers)
- Build candles decisions **from small TF to large TF** as a **filter chain**:
  - M1: **Is it safe to execute now'** (micro-safety only)
  - M5: **Is the environment structurally valid'** (validity)
  - M15: **Is market direction aligned for LONG'** (direction; required only in MINI_SWING)
  - H1: **Is macro regime/permission OK'** (risk posture / hard veto)

---

#### 1.4 Parent Node: TF Owner Blocks (Role -> Indicators -> Formulas -> Adaptives -> Outputs -> Reasons -> Sanity)

#### 1.4.1 H1 Node - Macro Regime & Risk Posture (Owner)

##### Role
- Defines macro permission/tightening: volatility regime + trend/chop regime + macro danger zones.
- May veto entries; must not trigger entries.

##### Indicators (H1)
- Realized volatility (EWMA sigma of log returns) -> `vol_regime`, `vol_spike_flag`
- CHOP (Choppiness Index) -> trend vs range clarity
- ATR-filtered pivots / macro zones -> `macro_zone_risk_flags` (tighten-only)
- Optional slow direction proxy (derived) to label TREND_UP vs TREND_DOWN when in TREND regime (direction owner remains M15).

##### Computing formulas (H1)
Returns:
- `r_t := ln(C_t / C_{t-1})`

EWMA realized volatility:
- `sigma2_t := lambda * sigma2_{t-1} + (1-lambda) * r_t^2`
- `sigma_t := sqrt(sigma2_t)`

Half-life parameterization:
- `lambda := exp( ln(0.5) / h )`  where `h` = half-life in bars

CHOP over n bars:
- `sumATR := Sigma_{i=t-n+1..t} ATR_i`
- `rangeHL := max(H_{t-n+1..t}) - min(L_{t-n+1..t})`
- `CHOP_n := 100 * log10( sumATR / max(rangeHL, EPS) ) / log10(n)`

ATR-filtered pivot significance (danger zones):
- A swing is "significant" only if `swing_move >= k * ATR` (k bounded, adaptive by vol_regime)
- `macro_zone_risk_flags` are proximity rules to last significant swing levels (tighten-only)

Optional slow direction proxy (only for regime labeling; not entry direction):
- `dir_proxy := sign( EMA(C, m) - EMA(C, m_long) )`
- Use `dir_proxy` only to label TREND_UP/TREND_DOWN when CHOP indicates TREND.

##### Adaptive parameters (H1; bounded)
- EWMA half-life: slow drift only (bounded) based on "vol-of-vol"
  - Example: `h_t := clamp(h_base * f(vov), h_min, h_max)` with modest `f(*)`
- CHOP thresholds: adapt via time-series percentiles of CHOP (do not change CHOP length)
- Pivot k: increase in EXPANSION to avoid marking everything as a zone

##### Outputs (H1; minimal)
- `vol_regime in {CALM, NORMAL, EXPANSION}`
- `market_regime in {TREND_UP, TREND_DOWN, RANGE, TRANSITION, CHAOTIC_AVOID}`
  - `RANGE` when CHOP is high; `TREND_*` when CHOP is low; `TRANSITION` otherwise
  - `CHAOTIC_AVOID` when EXPANSION + weak/invalid structure persists or repeated micro-unsafe bursts occur (tighten-only classification)
- `macro_zone_risk_flags` (NO_TRADE / CAUTION / NONE)

##### Reasons (H1)
- `H1_REGIME_VETO`, `H1_MACRO_ZONE_RISK`, `VOL_EXPANSION`, `CHAOTIC_AVOID`

##### Sanity checks (H1)
- sigma rises in expansions and cools in calm periods (no "tiny bar spikes").
- CHOP high in ranges, low in clean trends.
- Macro zones are rare and meaningful; not "everything is a zone".

---

#### 1.4.2 M15 Node - Market Direction & Bias Context (Owner)

##### Role
- Owner of market direction for LONG entries via `bias_sign_M15`.
- Adds stretch / mean-reversion risk as tightening.
- In MICRO: veto-only (unless promoted per symbol). In MINI_SWING: required direction owner.

##### Indicators (M15)
- Session VWAP (anchored VWAP only if anchor policy exists)
- `bias_sign_M15` from price vs VWAP + VWAP slope
- `mr_risk_flag` from normalized stretch (tighten-only)

##### VWAP Policy (24/7; single-owner mode; optional modifiers)
- VWAP modes:
  - SESSION_VWAP: existing session VWAP formula (start/end per session policy).
  - ROLLING_VWAP (windowed): `VWAP_roll_t := (Sigma_{i=t-N+1..t} TP_i*V_i) / max(Sigma_{i=t-N+1..t} V_i, EPS)`.
  - ANCHORED_VWAP: allowed only if an anchor policy exists; cumulative from anchor_id to t: `VWAP_anchor_t := (Sigma_{i=anchor..t} TP_i*V_i) / max(Sigma_{i=anchor..t} V_i, EPS)`.
- Config (no numbers invented; keep in INBOX if unset):
  - `candles_bars.m15.VWAP_MODE in {SESSION_VWAP, ROLLING_VWAP, ANCHORED_VWAP}`
  - `candles_bars.m15.VWAP_ROLL_N_BARS` (if ROLLING_VWAP)
  - `candles_bars.m15.ANCHOR_POLICY` (if ANCHORED_VWAP)
- Single-owner rule:
  - `bias_sign_M15` MUST use exactly one VWAP reference `VWAP_ref(mode)`.
  - Other VWAP variants are modifier-only:
    - If `sign(C - VWAP_ref)` disagrees with `sign(C - VWAP_other)` => set tighten-only flag `VWAP_DISAGREE_CAUTION=true`.
    - This flag must NOT create a second direction veto; it may only contribute to WARM/weak classification or size tightening via RiskManager.
- Telemetry:
  - Emit `vwap_mode_active`, `vwap_ref_value`, and (if enabled) `vwap_disagree_caution`.

##### Computing formulas (M15)
Typical price:
- `TP_i := (H_i + L_i + C_i) / 3`

Session VWAP:
- `VWAP_t := (Sigma_{i=session_start..t} TP_i * V_i) / max(Sigma_{i=session_start..t} V_i, EPS)`

VWAP slope (sign-only):
- `vwap_slope := VWAP_t - VWAP_{t-k}` (k small fixed; sign matters)

Stretch threshold:
- `stretch_th := Pxx(|dist_bps|) over rolling window W`
- `mr_risk_flag := (|dist_bps_t| > stretch_th)`

Direction sign (Long/Flat):
- `bias_sign_M15 := +1` if `(C_t > VWAP_t) AND (vwap_slope >= 0)`
- `bias_sign_M15 := -1` if `(C_t < VWAP_t) AND (vwap_slope <= 0)`
- else `0`

##### Adaptive parameters (M15; bounded)
- `stretch_th` via rolling percentiles; widen in EXPANSION so it doesn't block everything.

##### Outputs (M15; minimal)
- `bias_sign_M15 in {-1,0,+1}`
- `mr_risk_flag`

##### Reasons (M15)
- `M15_BIAS_VETO` (Long misalignment in MINI_SWING), `VWAP_STRETCH_CAUTION`

##### Sanity checks (M15)
- In up sessions: price spends more time above VWAP.
- Stretch flags are rare and meaningful (not always-on).

---

#### 1.4.3 M5 Node - Intraday Validity & Structure Quality (Owner)

##### Role
- Owner of intraday validity: `structure_valid` decides if environment is tradable vs noisy.
- Does not own direction; it validates structure for the direction owner (M15).

##### Indicators (M5)
- Donchian boundaries (rolling high/low) -> structure context
- Median TR -> tiny-break filter (tighten-only)
- Optional: confirmed swing structure classification (used only to support VALID/WEAK/INVALID state)

##### Computing formulas (M5)
Donchian over N bars:
- `upper_N := max(H_{t-N+1..t})`
- `lower_N := min(L_{t-N+1..t})`

Median TR:
- `medianTR_t := median(TR_{t-w+1..t})`

Tiny-break filter (long side):
- `breakout_move := C_t - upper_N`
- `tiny_break_flag := (breakout_move < q * medianTR_t)` (tighten-only)

Structure validity (deterministic states; no trigger timing):
- `VALID` if structure is coherent and tiny_break_flag is false
- `WEAK` if mixed swings / frequent boundary failures
- `INVALID` if chop/whipsaw dominates or rules fail deterministically

##### Adaptive parameters (M5; bounded; profile-aware)
- Donchian windows (bounded):
  - MICRO uses `N_micro := clamp(N_base_micro + DeltaN(H1.market_regime), N_min_micro, N_max_micro)`
  - MINI  uses `N_mini  := clamp(N_base_mini  + DeltaN(H1.market_regime), N_min_mini,  N_max_mini)`
  - TREND -> smaller N; RANGE/CHOP -> larger N
- Tiny-break q (bounded; regime-aware):
  - `q` stricter in CALM, looser in EXPANSION

##### Outputs (M5; minimal)
- `structure_valid in {VALID, WEAK, INVALID}`
- `tiny_break_flag`

##### Reasons (M5)
- `M5_STRUCTURE_INVALID`, `TINY_BREAK_BLOCK`, `M5_WEAK`

##### Sanity checks (M5)
- In ranges: Donchian contains price most of the time.
- In real breaks: break + hold occurs; false breaks are filtered.

---

#### 1.4.4 M1 Node - Micro-Safety & Timing Hygiene (Owner)

##### Role
- Blocks entries in unsafe minutes (spike/trap) and requires persistence for promotion.
- Must not set macro direction or replace M15/H1.

##### Indicators (M1)
- TR percentile spike -> `micro_spike_flag`
- CLV + wick dominance -> `trap_flag`

##### Computing formulas (M1)
TR:
- `TR_t := max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)`

Percentile spike:
- `pr_t := percentile_rank(TR_t within {TR_{t-W+1..t}})`
- `micro_spike_flag := (pr_t >= P_spike)`
- hysteresis clear: clear only when `pr_t <= P_clear` where `P_clear < P_spike`

CLV:
- if `H_t == L_t` then `CLV_t := 0`
- else `CLV_t := ((C_t - L_t) - (H_t - C_t)) / max(H_t - L_t, EPS)`
  - equivalent: `(2*C_t - H_t - L_t) / max(H_t - L_t, EPS)`

Trap flag (tighten-only):
- `body := |C_t - O_t|`
- `range := max(H_t - L_t, EPS)`
- `wick_total := range - body`
- `trap_flag := (|CLV_t| <= clv_eps) AND (wick_total / range >= wick_th)`

M1 safe:
- `M1_safe := (micro_spike_flag == false) AND (trap_flag == false)`
- `micro_safe_persist := consecutive_closed(M1_safe == true) >= K_confirm`

##### Adaptive parameters (M1; bounded; no intrabar)
- P_spike adapts by H1.vol_regime:
  - CALM -> lower P_spike (catch smaller spikes)
  - EXPANSION -> higher P_spike (avoid always-on blocking)
- Always keep hysteresis (P_clear below P_spike).
- CLV thresholds prefer fixed; optional mild session-liquidity adjustment only if explicitly configured.

##### Microtrade Timing (tighten-only)
- Purpose: add **timing hygiene** to micro entries using the active M15 bar phase; this is a filter only (never a trigger).
- Phase buckets (configurable; default fractions shown):
  - `PHASE_EARLY`: elapsed_frac in [0.00, 0.33)
  - `PHASE_MID`:   elapsed_frac in [0.33, 0.66)
  - `PHASE_LATE`:  elapsed_frac in [0.66, 1.00]
- Alignment classification (tighten-only):
  - `aligned_with_bias` if `bias_sign_M15` supports LONG and higher-TF vetoes are clear.
  - `counter_trend` if `bias_sign_M15` opposes LONG (or M15 stretch/mean-reversion risk is flagged).
- Tighten-only rules (no triggers):
  - If `counter_trend` AND `PHASE_LATE`: block NEW entries unless explicitly configured extra confirmation is satisfied (otherwise `primary_reason=COUNTER_TREND_LATE_PHASE`).
  - If `counter_trend` AND `PHASE_MID`: tighten size/caps and require `micro_safe_persist` (and any existing hygiene flags clear).
  - If `aligned_with_bias`: proceed only if all existing micro-safety and depth/fee/impact gates pass (no special permission granted).
- This phase logic never creates entries; it only blocks or tightens.

##### Outputs (M1; minimal)
- `micro_spike_flag`
- `trap_flag`
- `micro_safe_persist`

##### Reasons (M1)
- `MICRO_SPIKE`, `TRAP_FLAG`

##### Sanity checks (M1)
- Spike flag triggers on violent minutes, not constantly.
- Trap flags line up with "big wicks + weak closes".

---

#### 1.5 Parent Node: Shared Decision Synthesis (Bottom-Up)

##### 1.5.1 Conflict / Weak / Alignment Class (tighten-only)
Define hard blocks:
- `hard_block := (H1 veto) OR (M5.structure_valid == INVALID) OR (M1 unsafe) OR (HOT validity failed)`
Where:
- `M1 unsafe := micro_spike_flag OR trap_flag`
- `H1 veto := H1_REGIME_VETO OR macro_zone_risk == NO_TRADE OR market_regime == CHAOTIC_AVOID`

Define weak (caution) modifiers:
- `weak := (mr_risk_flag) OR (M5.structure_valid == WEAK) OR (H1.market_regime == TRANSITION)`

Alignment class:
- `align_class := 0` if hard_block
- `align_class := 1` if (not hard_block) and weak
- `align_class := 2` if (not hard_block) and (not weak)

##### 1.5.2 Candles Symbol State (entries only)
Active profile:
- default profile is MICRO
- can be promoted to MINI_SWING per 1.3 rules

Active required HOT set:
- MICRO -> `REQUIRED_TFS_HOT_MICRO`
- MINI_SWING -> `REQUIRED_TFS_HOT_MINI`

HOT validity:
- `hot_validity := all TF in active_required_hot_set are NOT BAR_WARMUP/BAR_STALE/BAR_GAP`

State:
- `CANDLES_COLD` if `(hot_validity == false) OR (align_class == 0)`
- `CANDLES_WARM` if `(hot_validity == true) AND (align_class == 1)`
- `CANDLES_HOT`  if `(hot_validity == true) AND (align_class == 2)`

Direction gating (Long/Flat):
- In MINI_SWING: require `bias_sign_M15 == +1` (else conflict).
- In MICRO: M15 bias is veto-only unless explicitly promoted per symbol.

Reason mapping:
- COLD: `BAR_WARMUP`, `BAR_STALE`, `BAR_GAP`, `H1_REGIME_VETO`, `H1_MACRO_ZONE_RISK`, `VOL_EXPANSION`, `CHAOTIC_AVOID`,
        `M15_BIAS_VETO` (MINI_SWING), `M5_STRUCTURE_INVALID`, `MICRO_SPIKE`, `TRAP_FLAG`, `TF_CONFLICT`
- WARM: `TF_MIXED`, `VWAP_STRETCH_CAUTION`, `H1_TRANSITION`, `M5_WEAK`
- HOT: optional `CANDLES_OK`

---

#### 1.6 Parent Node: Avoid Over-Stacking Volatility Filters
- H1 vol_regime is the only owner for broad volatility posture (permission).
- M5 medianTR is only for tiny-break filtering (structure quality).
- M1 TR percentile is only for minute safety (execution hygiene).
Do not use all three as hard vetoes for the same reason.

---

#### 1.7 Parent Node: Telemetry & Replayability (Candles)
Per TF on each bar close:
- `{symbol, TF, bar_close_ts, O,H,L,C,V, n_closed_bars_TF, bar_valid_state, outputs..., thresholds_version_ts, config_version}`

Per decision tick:
- `{symbol, active_profile(MICRO/MINI_SWING), active_required_hot_set, CANDLES_STATE(HOT/WARM/COLD),
   align_class, primary_block_reason(if any), secondary_reasons(optional), version_ts}`

Emit transitions:
- `PROFILE_CHANGE`, `BARS_READY_CHANGE`, `CANDLES_STATE_CHANGE`, `TF_ALIGN_CHANGE`

---

#### 1.8 Candles/Bars parameters pending explicit config (conservative defaults)
Default stance: all parameters below are treated as adaptive_required with `default_source=CONST` and bootstrap values that block new entries until configured/READY; exits remain allowed.
- VWAP policy: choose VWAP_MODE (SESSION_VWAP vs ROLLING_VWAP vs ANCHORED_VWAP); if ROLLING_VWAP, specify VWAP_ROLL_N_BARS; if ANCHORED_VWAP, specify ANCHOR_POLICY (valid anchors, reset conditions, anchor_id derivation); session definition (timezone, session start/end) if SESSION_VWAP (bootstrap = disable VWAP gating until set).
- LOOKBACK_HOT/COLD per TF and per profile (MICRO vs MINI_SWING) if not using defaults (bootstrap = longest conservative lookbacks).
- BAR_STALE_MS_TF per TF; BAR_GAP_MAX_MISSING_BARS_TF per TF (bootstrap = block entries on stale/gap until configured).
- H1 EWMA half-life bounds: `h_min/h_base/h_max`; vol-of-vol definition/window (bootstrap = block until configured).
- CHOP length `n` and percentiles for thresholds (bootstrap = block until configured).
- M5 Donchian bounds for MICRO and MINI: `N_min_micro/N_base_micro/N_max_micro` and `N_min_mini/N_base_mini/N_max_mini`, plus DeltaN mapping from H1.market_regime (bootstrap = block until configured).
- Tiny-break bounds: `q_min/q_base/q_max` and mapping by H1.vol_regime (bootstrap = block until configured).
- M1 TR spike window `W`; percentiles `P_spike/P_clear` per vol_regime (bootstrap = block until configured).
- CLV/trap parameters: `clv_eps`, `wick_th` (fixed vs session-adjusted) (bootstrap = block until configured).

CODEx REVIEW NOTES:
- Confirm no duplicated TF owners or double vetoes were introduced; Hybrid remains trigger owner.
- Promotion persistence: `K_confirm` (default 2 closed M1 bars).

### 3) WS bookTicker Eligibility (Level 2)
- Inputs: bookTicker fields u,b,B,a,A; L1 mapping; last_book_ts local arrival.
- Derived: mid=(bid+ask)/2; spread_bps=(ask-bid)/max(mid,EPS)*10_000; top_qty_min=min(bidQty,askQty); L1_notional_bid/ask; micro (imb, microprice, microedge_bps); stability metrics over W=STAB_WINDOW_SEC (spread_bps_med, spread_bps_mad/std, updates_per_sec).
- Config: THRESH_REFRESH_SEC=5; BOOK_STALE_MS=1500; MIN_N_FOR_PERCENTILES=10; DEMOTE_CONSEC_FAILS=3; STALE_ERROR_GRACE_MS=10000; STAB_WINDOW_SEC=10; ENABLE_STABILITY_BLOCK=false; ENABLE_BOOK_SHOCK=true; SPREAD_EMERGENCY_CAP_BPS=P98 (or P99); VALID_RATIO_FLOOR=0.60 (pct_valid freeze).
- SPREAD_EMERGENCY_CAP_BPS default:
  - Default emergency cap percentile is P98 (configurable P99 for ultra-strict); one value at runtime from config: stream_eligibility.ws_bookticker.SPREAD_EMERGENCY_PCT (default 98).
- Documentation vs runtime:
  - Any "(or P99)" text is documentation only; runtime must use stream_eligibility.ws_bookticker.SPREAD_EMERGENCY_PCT to select a single percentile.
  - Telemetry should surface the chosen SPREAD_EMERGENCY_PCT value with thresholds_version_ts.
- Stability settings source of truth:
  - STAB_WINDOW_SEC, MIN_UPDATES_STAB, ENABLE_STABILITY_BLOCK, and SPREAD_MAD_CAP derivation are defined in "WS bookTicker Stability Metrics"; do not duplicate conflicting defaults elsewhere.
- Valid set: ask>bid>0, bidQty>0, askQty>0, finite, now_ms-last_book_ts <= BOOK_STALE_MS, u>last_book_u; otherwise BOOK_OUT_OF_ORDER.
- Thresholds: SPREAD_CAP_BPS=P80; TOP_QTY_FLOOR=P40; SPREAD_EMERGENCY_CAP_BPS=P98; if BOOK_SHOCK: SPREAD_SHOCK_BPS=P98, TOP_QTY_SHOCK_FLOOR=P5, SPREAD_RECOVER_BPS=P90, TOP_QTY_RECOVER_FLOOR=P20; if STABILITY_BLOCK: SPREAD_MAD_CAP=P90(spread_bps_mad), UPD_RATE_CAP=P95(updates_per_sec). Freeze if N_valid low, book stale, or pct_valid<VALID_RATIO_FLOOR.
- pct_valid definition (for VALID_RATIO_FLOOR):
  - pct_valid is computed over ALL subscribed bookTicker symbols (Level-2 universe), not only promoted set; evaluated each THRESH_REFRESH_SEC using the current VALID snapshot (windowless).
- Stability actions (if ENABLE_STABILITY_BLOCK): block promotion if spread_bps_mad>SPREAD_MAD_CAP (QUOTE_UNSTABLE); if updates_per_sec extreme AND spread_bps_mad high -> BOOK_GAMEY_PREWARN (warn-only; tightens L3 recovery/quarantine).
- Stability metrics when ENABLE_STABILITY_BLOCK=false:
  - spread_bps_mad and updates_per_sec are telemetry only (no thresholds/blocks) unless ENABLE_STABILITY_BLOCK=true or a hybrid gate explicitly references them.
- Promotion: sanity, fresh, spread caps, top_qty_min, stability (if enabled), shock logic.
- Demotion: cadence-based using DEMOTE_CONSEC_FAILS; immediate demotion between ticks only when hard-fail conditions occur (STALE_FEED / GAP / QUARANTINE / SHOCK / explicit BAD_QUOTE/BOOK_OUT_OF_ORDER) and only if the matching config flag is true.
- SMALLCAP_THIN carry-over: tightens downstream (L3) routing/params (N=20, stricter quarantine); no L2 threshold change unless configured.
- Reason codes: BOOK_STALE, BAD_QUOTE, SPREAD_WIDE, SPREAD_EMERGENCY, TOP_THIN, BOOK_SHOCK, BOOK_OUT_OF_ORDER, WARMUP_WS_THRESHOLDS, QUOTE_UNSTABLE, BOOK_GAMEY_PREWARN (warn).
- Visibility: logger eligibility.ws_bookticker; emit {ws_book_state, thresholds_version_ts, N_valid, N_promoted_depth, max_book_age_ms}; severities OK/WARMUP_WS_THRESHOLDS/STALE_FEED with STALE_ERROR_GRACE_MS.
  - Include SPREAD_EMERGENCY_PCT alongside SPREAD_EMERGENCY_CAP_BPS and thresholds_version_ts so ops can confirm the active percentile.
- IMMEDIATE_DEMOTION switches (operational):
  - `stream_eligibility.ws_bookticker.stability.IMMEDIATE_DEMOTION_ON_STALE=false` (default): if true, demote immediately on staleness detection between refresh ticks (hard-fail only).
  - `stream_eligibility.ws_bookticker.stability.IMMEDIATE_DEMOTION_ON_BADQUOTE=false` (default): if true, demote immediately on sanity break (ask = bid or non-positive) between refresh ticks (hard-fail only).
  - Default production mode: cadence-based demotion; enable immediate demotion only for the corresponding hard-fail condition when explicitly configured.

- Per-symbol overrides (optional; bounded + slow):
  - General rule: allow per-symbol overrides for thresholds/caps but keep staleness clocks conservative (never auto-learn looser staleness; prefer stricter for small caps).
  - Eligible per-symbol params:
    - L2: SPREAD_CAP_BPS, SPREAD_EMERGENCY_CAP_BPS, TOP_QTY_FLOOR
    - L3: MIN_DEPTH_QUOTE, CHURN_P95_CAP (BOOK_GAMEY), RECOVERY_CONSEC_eff / DEPTH_RATIO_RECOVER_eff (BOOK_GAMEY tightening)
    - Staleness: TICKER_STALE_MS / BOOK_STALE_MS / DEPTH_STALE_MS only within tight bounds (e.g., +/-50%) with a bias to stricter.
    - Absolute caps (in addition to +/-50% bounds):
      - TICKER_STALE_MS in [2000, 60000]; BOOK_STALE_MS in [200, 5000]; DEPTH_STALE_MS in [200, 5000]; prefer tighter for SMALLCAP_THIN; never auto-learn looser caps.
  - Slow, bounded adaptation:
    - Maintain per-symbol rolling distributions over long window W_sym_sec (e.g., 10-60 min) using VALID samples only.
    - Examples: SPREAD_CAP_BPS_sym = min(global_SPREAD_CAP_BPS, P80_sym(spread_bps)); MIN_DEPTH_QUOTE_sym = max(global_MIN_DEPTH_QUOTE, P40_sym(min_depth_quote(N))); CHURN_P95_CAP_sym = min(global_CHURN_P95_CAP, P95_sym(churn)).
    - Freeze per-symbol adaptive updates during feed stress (WARMUP/STALE_FEED); reuse last-good values.
  - Per-symbol override guardrails (explicit):
    - Update cadence: recompute per-symbol adaptives no faster than W_sym_refresh_sec (default 60s; configurable).
    - Bounds: staleness overrides within +/-50% of globals; spread caps use min(global, sym), depth floors use max(global, sym), churn caps use min(global, sym).
    - Freeze per-symbol updates during any WARMUP_* or STALE_FEED state; reuse last-good values.

### Stream Eligibility Notes: Hybrid Roles, Stability Metrics, and Logging/ML
- Stream role separation (avoid duplication):
  - WS `<symbol>@ticker` (24h rolling stats) is for universe/health/routing (activity, dead markets, extreme-move exclusions).
  - WS `<symbol>@bookTicker` is for L1 tightness/stability gating (best bid/ask + sizes) and early shock warning.
  - WS partial depth is for liquidity/impact/shock gating (min_depth_quote, slip_bps(Q_entry), depth_ratio, churn).
  - Small-cap inclusion note:
    - REST-Eligibility (24h ticker cache) uses cross-sectional activity/range gates and may exclude many small caps if used as the primary universe.
    - WS Stream Eligibility can include small caps, but only those passing cross-sectional percentiles. Options (tighten-only):
      - (a) Class-segmented percentiles by liquidity tag (SMALLCAP_THIN vs NORMAL), optional OFF by default; if per-class sample size is insufficient, fall back to global percentiles and freeze adaptive updates until sufficient samples.
      - (b) A hot-slot quota for SMALLCAP_THIN (routing-only) via `stream_eligibility.routing.SMALLCAP_HOT_QUOTA` (default 0).
  - Small-cap routing (optional, routing-only):
    - stream_eligibility.routing.SMALLCAP_HOT_QUOTA (default 0): reserve at least this many live_Hot slots for SMALLCAP_THIN symbols if they meet minimum safety gates. If quota=0, small caps compete normally via ranking.
    - Note: Segmented percentiles by liquidity tag are optional OFF by default; quota-only routing remains the default simpler mode.
- bookTicker stability metrics (spread_jitter / spread_bps_mad):
  - Window config: STAB_WINDOW_SEC (default 10), MIN_UPDATES_STAB (default 30).
  - For spreads S over the last STAB_WINDOW_SEC:
    - spread_bps_med = median(S)
    - spread_bps_mad = median(|spread_bps_i - spread_bps_med|)
    - spread_jitter = P90(|d_spread_bps_i|) where `d_spread_bps_i = spread_bps_i - spread_bps_{i-1}`
    - updates_per_sec = count(S)/STAB_WINDOW_SEC
  - If ENABLE_STABILITY_BLOCK=true: use spread_bps_mad (and/or spread_jitter) to block promotion (reason QUOTE_UNSTABLE). If false: telemetry-only.
- What to save + log (ops + backtest + ML readiness):
  - Save (replay/ML):
    - bookTicker events (ts_local, u, b,B,a,A)
    - depth top-N ladders for hot symbols OR at minimum a feature vector per depth event (min_depth_quote, depth_ratio, slip_bps(Q_entry_eff), churn, flags, primary reason)
    - ticker snapshots at refresh cadence (qvol_per_min, trades_per_min, range_pct_24h, abs_change_pct_24h, tag + tag_state)
    - thresholds snapshots each refresh (thresholds_version_ts + values per level)
    - state transition events (promote/demote, SHOCK enter/exit, quarantine set/clear) with reason codes
  - Log (live debugging):
    - Per refresh per level: {state, thresholds_version_ts, N_valid, N_promoted/N_tradable, max_age_ms, top-K reason counters}
    - Event logs only on transitions: promotion/demotion, SHOCK transitions, quarantine transitions, integrity violations (L1_MISMATCH, BOOK_OUT_OF_ORDER, NONFINITE_SLIP escalation).

### WS bookTicker Stability Metrics (spread_jitter / spread_bps_mad)

- Purpose: quantify L1 spread stability over a short rolling window to detect unstable quoting (telemetry by default; can be used as a promotion block when enabled).

- Inputs: spread_bps computed per bookTicker update; maintain a rolling window of the last STAB_WINDOW_SEC seconds.

- Config (stream_eligibility.ws_bookticker.stability.*):

  - stream_eligibility.ws_bookticker.stability.STAB_WINDOW_SEC (default 10)

  - stream_eligibility.ws_bookticker.stability.MIN_UPDATES_STAB (default 30)

  - stream_eligibility.ws_bookticker.stability.ENABLE_STABILITY_BLOCK (default false)

  - stream_eligibility.ws_bookticker.stability.SPREAD_MAD_CAP (derived from VALID cross-sectional percentiles or configured constant)

  - stream_eligibility.ws_bookticker.stability.SPREAD_JUMP_BPS (optional jump-rate telemetry; default conservative constant 5 bps if not configured)

  - stream_eligibility.ws_bookticker.stability.UPD_RATE_CAP (if used alongside SPREAD_MAD_CAP; default derived from MIN_UPDATES_STAB/STAB_WINDOW_SEC, fallback conservative constant 3 updates/sec)

- Window population rule:

  - Include only VALID bookTicker samples (ask > bid > 0, finite values, now_ms - last_book_ts <= BOOK_STALE_MS, updateId monotonic).

  - If count(window) < MIN_UPDATES_STAB: set stability_state=STAB_INSUFFICIENT_SAMPLES and treat metrics as telemetry-only (do not block).

- Computations (for S = {spread_bps_i} in the last STAB_WINDOW_SEC):

  - spread_bps_med = median(S)

  - spread_bps_mad = median(|spread_bps_i - spread_bps_med|)

  - Optional scaled MAD: spread_bps_mad_std ~ 1.4826 * spread_bps_mad

  - d_spread_bps_i := spread_bps_i - spread_bps_{i-1}

  - spread_jitter := P90(|d_spread_bps_i|)

  - updates_per_sec = count(S) / STAB_WINDOW_SEC

  - Optional spread_jump_rate = fraction of updates in S where |d_spread_bps_i| > SPREAD_JUMP_BPS

- Actions:

  - If ENABLE_STABILITY_BLOCK=true and stability_state != STAB_INSUFFICIENT_SAMPLES:

    - Block promotion to depth when spread_bps_mad > SPREAD_MAD_CAP (reason QUOTE_UNSTABLE) where SPREAD_MAD_CAP is derived from VALID cross-sectional percentiles or configured constant.

  - If ENABLE_STABILITY_BLOCK=false:

    - Metrics are telemetry-only (no thresholds; no block).

- Visibility:

  - Emit each THRESH_REFRESH_SEC: {stability_state, spread_bps_med, spread_bps_mad, spread_jitter, updates_per_sec, spread_jump_rate (optional)}.

### Optional Enhancements (disabled by default; require additional streams)
- Trades/flow toxicity module (requires `<symbol>@aggTrade` or trade stream):
  - Purpose: detect toxic flow bursts; used only to tighten gating/sizing/quarantine (never to loosen).
  - If enabled, compute optional flow metrics from trade prints (e.g., buy/sell imbalance using maker/taker flags) and:
    - shrink Q_entry_eff, extend cooldown, or block entries under TOXIC_FLOW (reason TOXIC_FLOW), per configured caps.
  - Enable flag: stream_eligibility.toxicity.ENABLED=false (default).

### Audit appendix
- Unique Facts Inventory and Deduplication Map retained; precedence: cadence-based demotion is default, with immediate demotion only when the hard-fail config flags are enabled.


## OrderEngine

### Purpose
- Decision/actuation layer: decides whether/how to place orders within Stream Eligibility feasibility envelopes and RiskManager sizing/caps. Does not compute regimes/indicators/depth feasibility/dq_score.

### Inputs
- Order intent from Strategy/Signals after RiskManager sizing.
- Feasibility Envelope outputs from Stream Eligibility (constraints/tactics).
- RiskManager final size/caps and drawdown/portfolio brakes.

### Inputs / Contracts
- `order_intent` (from strategy/router after RiskManager sizing):
  - Fields: `intent_id`, `symbol`, `side` (BUY only for entry), `qty_target`, `notional_target` (optional), `urgency` in {NORMAL, URGENT_EXIT}, `tif`, `allow_reduce_only` (bool).
- `feasibility_envelope` (from Stream Eligibility):
  - `entry_allowed`, `entry_mode` in {BLOCK, PROBE_ONLY, MAKER_ONLY, TAKER_OK}
  - `entry_blocked`, `maker_only_preferred`, `taker_disallowed`
  - `max_entry_qty_cap`, `max_entry_notional_cap`, `max_single_order_qty`
  - `max_slippage_bps`, `max_worstcase_cost_bps`, `max_cross_spread_ticks`
  - `partial_fill_timeout_ms`, `min_fill_ratio_to_continue`, `max_partial_duration_ms`, `cancel_on_partial_timeout`
  - `reenable_requires_k_good_updates`, `reenable_min_stable_ms`
- `risk_caps` (from RiskManager):
  - `final_qty_cap` (<= SE caps), per-trade risk mode, exposure limits, reduce-only rules.
- Cap composition rule: `final_qty_to_execute = min(intent_qty, risk_qty_cap, se_max_entry_qty_cap, venue_max_qty_if_any)`; enforce minQty/minNotional/stepSize/tickSize at execution time (per exchangeInfo rules).

### Integration Contract: Feasibility Envelope Consumption
- OrderEngine must consume and honor: `envelope_version_id`, `envelope_ts_ms`, `envelope_valid_for_ms`, `entry_mode`, `entry_blocked`, `maker_only_preferred`, `taker_disallowed`, caps (`max_entry_qty_cap`, `max_entry_notional_cap`, `max_single_order_qty`), cost/slip limits (`max_worstcase_cost_bps`, `max_slippage_bps`, `max_cross_spread_ticks`), partial-fill constraints (`partial_fill_timeout_ms`, `min_fill_ratio_to_continue`, `max_partial_duration_ms`, `cancel_on_partial_timeout`).
- Every SUBMIT/AMEND must log `envelope_version_id_used`; if any required field is missing -> fail closed with `OE_ENVELOPE_MISSING_FIELD`; if `(now - envelope_ts_ms) > envelope_valid_for_ms` -> abort submit with `OE_ENVELOPE_EXPIRED_ABORT`.

### Concurrency & Working-Set Limits (robustness)
- `max_concurrent_entry_intents_global` (config): if reached, block NEW entries with `OE_BLOCKED_CONCURRENCY_GLOBAL`; exits/reductions still allowed.
- `max_concurrent_entry_intents_per_symbol` (default 1): serialize per symbol; if reached, block NEW entries for that symbol with `OE_BLOCKED_CONCURRENCY_SYMBOL`; exits allowed.
- Working_set per intent remains bounded by `max_working_orders_per_intent` (default 1); cancel-in-flight gate remains in force.

### OrderEngine Decision Ladder (constraint-driven)
- Hard blocks: if intent is ENTRY and (`entry_blocked` OR `entry_mode=BLOCK` OR `entry_allowed=false`) -> do not place entry. Exits/reductions always allowed.
- Mode selection:
  - `PROBE_ONLY`: tiny maker probe only (bounded by config and `max_single_order_qty`).
  - `MAKER_ONLY`: maker quoting only (post-only); enforce `max_cross_spread_ticks=0`.
  - `TAKER_OK`: taker allowed only if `worstcase_cost_bps <= max_worstcase_cost_bps` AND `taker_disallowed=false`.
- SPOT constraint: Entries = BUY only (long opens). Sells are reduce/exit only (`allow_reduce_only` honored).
- If constraints cannot be satisfied, skip ENTRY; never violate feasibility. Exits/reductions remain allowed.

### Pre-Send Revalidation (race-condition guard)
- Before SUBMIT/AMEND: recheck latest `envelope_version_id` and `envelope_valid_for_ms`; confirm `entry_mode`/caps still permit the action.
- If envelope is stale or tightened since plan build: abort or adjust to tighter; do not send. Reason codes: `OE_ABORT_STALE_ENVELOPE`, `OE_ABORT_TIGHTENED_ENVELOPE`.

### Intent -> Execution Plan Compiler (deterministic; rate-limit aware)
- ExecutionPlan fields: `plan_id/plan_hash`, `intent_id`, `child_orders[]` each with {type, qty, price, tif/ttl, post_only, replace_cadence_ms, fallback_allowed}.
- Compilation rules:
  - Cap composition: `qty_cap = min(intent_qty, risk_qty_cap, se_max_entry_qty_cap, venue_max_qty_if_any)`.
  - Rounding: apply tickSize/stepSize; ensure minQty/minNotional; if rounding fails -> block entry with venue reason.
  - Respect `entry_mode` and `max_cross_spread_ticks`; maker-only plans use post-only and do not cross.
  - Plan hash is deterministic from inputs (intent + caps + envelope + venue filters).
  - Rate-limit-aware: before multi-slice plans, check Rate Limit Governor budget; if insufficient for cancel/replace, degrade to minimal PROBE_ONLY plan (tiny, minimal cancels) or skip entry. Do not start plans requiring more cancel/replace than budget allows. Reason codes: `OE_BLOCKED_RATE_BUDGET`, `OE_PLAN_DEGRADED_RATE_BUDGET`.

### Lifecycle state machine (Spot long/flat)
- Entities: Intent {symbol, side, qty, intent_type in {ENTRY, EXIT, REDUCE}, urgency in {NORMAL, URGENT}, price_policy, stop/TP params(optional), reason_context{primary_reason, secondary_reasons}, decision_ts_ms}; Order {clientOrderId, exchangeOrderId(optional), type, tif, price(optional), qty, status}.
- State machine (idempotent): INTENT_NEW -> (preflight) -> INTENT_BLOCKED | ORDER_SUBMITTING -> ORDER_ACKED | ORDER_REJECTED | ORDER_UNCERTAIN -> ORDER_WORKING | ORDER_PARTIALLY_FILLED | ORDER_FILLED | ORDER_CANCELED; ORDER_PARTIALLY_FILLED can loop; ORDER_UNCERTAIN reconciles. Any terminal -> INTENT_DONE (journal + telemetry).
- Inventory-safe: SELL qty must not exceed available inventory; treat dust as inventory. If EXIT/REDUCE cannot size fully due to filters/minNotional, send largest feasible reduction and re-evaluate next tick.

### Lifecycle State Machine (single order + working set)
- States: IDLE, PLAN_BUILT, SUBMITTING, WORKING, PARTIAL_PENDING (timer starts on first fill), REQUOTE_PENDING (maker modes), CANCEL_REQUESTED, CANCELED, FILLED, FAILED (terminal with reason).
- Transitions: IDLE -> PLAN_BUILT -> SUBMITTING -> WORKING; WORKING -> PARTIAL_PENDING on first fill; WORKING/PARTIAL_PENDING -> REQUOTE_PENDING on reprice conditions; WORKING/PARTIAL_PENDING -> CANCEL_REQUESTED -> CANCELED; WORKING/PARTIAL_PENDING -> FILLED; Any -> FAILED on unrecoverable error (with reconcile behavior).
- Invariants: at most one active working order per intent_id (working_set size default = 1). Never place a new order while CANCEL_REQUESTED is in-flight for the same intent.

### Preflight gates (OrderEngine-level; do not loosen upstream)
- Hard blocks (entries only; exits allowed): trading_enabled/kill-switch off; any upstream block that implies "no new entries" -> block ENTRY with same primary_reason.
- Hard blocks (both entry/exit) only for feasibility: if no valid order after rounding down, record ORDER_SIZE_INVALID and continue safest feasible exit sizing on subsequent ticks.
- Tie-break: deepest layer primary_reason wins; OrderEngine must not reorder upstream precedence.

### Entry policy (maker-first)
- Default: LIMIT / LIMIT_MAKER (post-only when required) with inside-spread policy; MARKET/IOC ENTRY only if explicitly enabled and spread/slippage within Stream Eligibility/RiskManager caps.
- Stuck/unfilled ENTRY: if intent no longer valid (micro/coverage change, kill-switch, cost too high), cancel and return to INTENT_NEW next tick; do not chase into taker unless explicitly allowed and still within caps.

### Exit policy (maker preferred; urgent ladder)
- Normal exit: passive LIMIT when micro is healthy (spread/depth within caps).
- Urgent exit ladder (first feasible wins; never opens new exposure): 1) aggressive LIMIT near-touch (maker if possible); 2) IOC (taker) within caps; 3) MARKET (only if enabled and within caps); otherwise emit CRITICAL telemetry and continue best-effort passive exit.

### Venue Feasibility Enforcement (exchange filters)
- Enforce tickSize/stepSize rounding on price/qty; verify minQty/minNotional before submit/amend.
- If venue rejects on filters/precision: mark `OE_BLOCKED_BY_VENUE_FILTER`, re-quantize once; if still invalid, stop new entries for that intent until refreshed; exits continue with best feasible sizing.

### Symbol Trading-Status Gate (REST metadata)
- If exchange metadata marks symbol halted/disabled/unknown -> block entries, cancel open orders, and stay exit-only until status clears (if exits are impossible while halted, document and alert). Reason code: `OE_SYMBOL_STATUS_BLOCK`.
- Config defaults (CONST): `orderengine.symbol_status.ENABLED=true`, `orderengine.symbol_status.REFRESH_SEC=30`.

### Maker Safety Rails (post-only robustness)
- Guardrails: `min_requote_interval_ms`, `max_requotes_per_intent`, `max_quote_staleness_ms`, `price_drift_requote_ticks`.
- In PROBE_ONLY / MAKER_ONLY, never cross spread (post-only). Enforce `max_cross_spread_ticks=0`.
- If requote budget exhausted: fallback ladder -> if entry_mode allows taker and constraints allow, attempt bounded taker; else cancel and stop. Reason codes: `OE_REQUOTE_RATE_LIMITED`, `OE_REQUOTE_BUDGET_EXCEEDED`.

### Cancel/Replace + partial fills (safe handling)
- Partial fills: update exposures incrementally on each fill; remaining qty stays under same intent unless invalidated. Never flip EXIT/REDUCE into ENTRY within the same tick; flatten-first.
- Two-Phase Cancel/Replace Protocol (non-bypassable): Phase 1 CANCEL_REQUESTED -> wait for cancel confirmation or reconciliation proof order is not working; Phase 2 SUBMIT replacement. Never submit a replacement while cancel is in-flight. Reason codes: `OE_CANCEL_REPLACE_TWO_PHASE`, `OE_REPLACE_BLOCKED_CANCEL_IN_FLIGHT`.

### Stops / OCO handling (spot long/flat)
- Protective stop invariant: if policy requires, ensure protective stop (or exchange OCO with stop-loss) is live for any open long after entry stabilization. If cannot place (filters/minNotional/venue reject), emit P1 alert and enforce "no new entries; manage exit only" for the symbol until resolved.
- OCO usage: may bind TP + stop-loss where supported; otherwise emulate with linked orders and strict self-trade prevention; enforce inventory constraint and deterministic cancellation/linkage.

### Reconciliation + uncertain-order handling
- Primary truth: User Data Stream events primary; REST reconciliation on fixed cadence to recover misses.
- Uncertain orders: if no ACK within ACK timeout, mark ORDER_UNCERTAIN and query; resend only after explicit not found/rejected. On reconnect/resubscribe, reconcile open orders + balances before allowing new entries (exits allowed).

### Stale ACK / Late Fill Sanity Guards
- Metrics: `ack_latency_ms = submit_ts -> ack_ts`; late fills after cancel = fill received after CANCEL_REQUESTED/confirmed.
- If `ack_latency_ms > orderengine.ops.ACK_STALE_MS` -> treat ops as degraded for entries (block new entries for symbol cooldown); exits allowed. Reason code: `OE_STALE_ACK_GUARD`.
- If late fills arrive after cancel -> reconcile immediately, freeze new entries for `orderengine.ops.LATE_FILL_FREEZE_MS`, exits allowed. Reason code: `OE_LATE_FILL_RECONCILE_FREEZE`.
- Defaults (CONST): `orderengine.ops.ACK_STALE_MS=1500`, `orderengine.ops.LATE_FILL_FREEZE_MS=2000`.

### Kill-Switch Tiers (deterministic; ops/risk safety)
- Tiers: Tier1 ENTRY_BLOCK (no new entries), Tier2 REDUCE_ONLY (exits/reductions only), Tier3 FLATTEN (optional emergency if enabled).
- Triggers (tighten-only): repeated rejects, cancel failures, reconcile divergence, rate-limit/ACK storms. Tiering escalates immediately; de-escalation requires operator reset or explicit stability window.
- Defaults (CONST): `orderengine.killswitch.ENABLED=true`, `orderengine.killswitch.TIER2_REJECT_RATE=0.05`, `orderengine.killswitch.TIER2_CANCEL_FAIL_RATE=0.02`, `orderengine.killswitch.TIER3_ENABLED=false`, `orderengine.killswitch.TIER3_DIVERGENCE_THRESHOLD=0.05`.
- Reason codes: `OE_KILLSWITCH_TIER1`, `OE_KILLSWITCH_TIER2`, `OE_KILLSWITCH_TIER3`.

### Position Intent Accounting (intended vs actual)
- Track per symbol: `intended_position_qty` (from executed intents) vs `actual_position_qty` (from exchange); `divergence_qty = |intended - actual|`.
- If `divergence_qty > orderengine.reconcile.DIVERGENCE_HARD_QTY` -> block new entries, force reconcile, possibly Tier2 reduce-only. If `> DIVERGENCE_WARN_QTY` -> warn and tighten. Never creates new entry signals.
- Defaults (CONST): `orderengine.reconcile.DIVERGENCE_WARN_QTY=0.01`, `orderengine.reconcile.DIVERGENCE_HARD_QTY=0.05`.
- Reason codes: `OE_POSITION_DIVERGENCE_WARN`, `OE_POSITION_DIVERGENCE_HARD`.

### Error handling, rate limits, and backoff
- Error classes: reject (filters/precision/minNotional), rate-limit (429), transient (5xx/network), semantic (insufficient balance, would-trade/self-trade).
- Policies: rejects -> refresh rules/re-quantize; 429 -> bounded backoff, degrade to exit-only if persistent; transient -> bounded retries then DECISION_FREEZE for entries while managing exits.

### Rate Limit Governor
- Budgets: global token budget plus per-symbol budget (conceptual).
- On 429/limit errors: apply backoff ladder (config); while budget exhausted, block new entries; exits continue.

### Retry Budgets & Terminal Behavior
- Budgets (CONST defaults): `max_submit_retries_per_intent=3`, `max_cancel_retries_per_intent=3`, `max_amend_retries_per_intent=2`, `max_reconcile_cycles_per_intent=3`.
- When exceeded: mark intent FAILED for entries; block new entries for symbol cooldown; exits still allowed. Reason codes: `OE_RETRY_BUDGET_EXCEEDED`, `OE_RECONCILE_BUDGET_EXCEEDED`.

### Chaos Tests (must-pass robustness checklist)
- Drop depth updates by N%: dq_score downgrades mode; entries blocked; exits OK.
- Reorder/duplicate aggTrade IDs: freeze aggTrade; downgrade mode.
- 429 bursts: entries stop; exits continue; backoff works.
- Partial-fill stall: cancel remainder; no forbidden escalation to taker.
- Crash/restart mid-order: reconcile open orders; no duplicate submissions (idempotent).

### Telemetry (per intent lifecycle)
- Emit: {symbol, intent_id, intent_type, urgency, side, qty_requested, qty_quantized, order_type, tif, price_policy, clientOrderId, exchangeOrderId(optional), state, primary_reason, secondary_reasons(optional), stream_state_snapshot_ids, thresholds_version_ts, config_version, decision_ts_ms}
- Latency timers: submit->ACK, ACK->fill, cancel_request->cancel_confirm, reconcile_duration.
- Partial fill series: fill_qty, fill_price, cum_filled, remaining_qty, fees, maker/taker flag.

### Decision policy (within constraints)
- If `entry_blocked` or `entry_mode=BLOCK` -> no new positions; exits/reductions still allowed.
- If `maker_only_preferred` -> enforce post-only/inside-spread pricing; do not cross.
- If `taker_disallowed` -> never send taker/IOC/MARKET.
- On constraint conflicts, choose the tighter/safest action; exits/reductions always permitted.

### Execution tactics
- Maker pricing/offset policy (conceptual): inside-spread quotes honoring `max_cross_spread_ticks` and cost/slip caps.
- Cancel/replace with bounded timeouts; respect cooldown/quarantine from Stream Eligibility.
- Optional slicing/pacing bounded by `max_single_order_qty`, `max_entry_qty_cap`, and `max_entry_notional_cap`.

### Maker Quoting Tactics (PROBE_ONLY / MAKER_ONLY)
- Post-only always; never cross when maker-only (`max_cross_spread_ticks=0` enforced).
- Price selection: best bid/ask +/- tick offsets, bounded by `max_cross_spread_ticks`.
- Requote triggers (tighten-only): price drift beyond X ticks (config), quote stale beyond Y ms, or spread regime change.
- Requote cadence: minimum time between requotes (config); max requotes per intent before fallback decision (see failure handling).
- Maker safety rails: `min_requote_interval_ms`, `max_requotes_per_intent`, `max_quote_staleness_ms`, `price_drift_requote_ticks`. If requote budget exhausted -> fallback ladder: if entry_mode allows taker and constraints allow, attempt bounded taker; else cancel and stop. Reason codes: `OE_REQUOTE_RATE_LIMITED`, `OE_REQUOTE_BUDGET_EXCEEDED`.

### Post-Only Rejection Playbook
- On post-only reject: increment `post_only_reject_count`; attempt bounded requotes within maker safety rails.
- Never convert to taker unless `entry_mode` allows and cost budget passes.
- On repeated rejects beyond budget: cancel intent or apply cooldown for entries on symbol. Reason codes: `OE_POSTONLY_REJECT`, `OE_POSTONLY_REJECT_COOLDOWN`.

### Taker Tactics (only when allowed)
- Conditions: `entry_mode=TAKER_OK` AND `taker_disallowed=false` AND cost budget passes (`worstcase_cost_bps <= max_worstcase_cost_bps`).
- Behavior: IOC or marketable limit preferred with `max_slippage_bps` guard. If slippage cannot be bounded (book unavailable), do not taker. Quantity capped by `final_qty_to_execute` and `max_single_order_qty`.

### Partial-fill playbook (loss-avoidance)
- Honor `partial_fill_timeout_ms`, `min_fill_ratio_to_continue`, `max_partial_duration_ms`, `cancel_on_partial_timeout`.
- If partial fill stalls under risky conditions (high toxicity/low liquidity): cancel remainder; optionally reduce exposure per RiskManager rules; never escalate into disallowed taker actions.
- On first fill: start partial timer. If `time > partial_fill_timeout_ms` OR `fill_ratio < min_fill_ratio_to_continue`: if `cancel_on_partial_timeout` => set CANCEL_REQUESTED and cancel remainder. Do not escalate into forbidden taker actions. Enforce `max_partial_duration_ms` as hard bound; after it, cancel remainder and manage exposure per risk rules. If exposure unacceptable, allow reduce/exit (never blocked).

### Exchange mechanics & safety
- Idempotent clientOrderId; reconcile open orders; safe retries/backoff; rate-limit handling; reconnect handling.
- Respect exchange filters (tickSize/stepSize/minNotional) and truth loop; never invent feasibility beyond the envelope.

### Failure Handling / Ops Degradation
- Idempotency: use intent_id as clientOrderId key where possible.
- Reconcile loop: on reconnect/restart, fetch open orders/positions; reattach state machine.
- Rate limits/errors: on 429/rate-limit, apply backoff schedule (config), block new entries temporarily, allow exits/reductions.
- Repeated rejects/cancel-fails: set `ops_degraded` flag; stop opening new entries; continue exit-only.

### Dust / MinNotional Residual Handling
- Policy: if remaining qty < minQty OR remaining notional < minNotional, do not loop invalid submits; mark residual DUST; optionally consolidate via reduce-only action if `orderengine.dust.CONSOLIDATE_WHEN_FEASIBLE` (default OFF). Reason code: `OE_DUST_REMAINDER`.

### Telemetry outputs
 - Realized slippage and fees (maker/taker), fill latency (p95/p99), reject rate, cancel failure rate, reconnect frequency/backoff events, ops_health metrics for tightening upstream. OrderEngine does not compute regimes/indicators/depth feasibility/dq_score.
 - Log per intent: plan_hash/plan_id, timestamps for each state transition, realized_slip_bps, fees, fill_latency_ms, reject_reason, cancel_fail_count, requote_count, backoff_count. Publish ops_health upward: ack_latency_p95/p99, reject_rate, cancel_fail_rate, reconnect_count (for tightening elsewhere).
 - Reason codes (OrderEngine surface): OE_BLOCKED_BY_VENUE_FILTER, OE_RATE_LIMIT_BACKOFF, OE_OPS_DEGRADED, OE_MAX_REQUOTE_REACHED, OE_PARTIAL_TIMEOUT, OE_COST_CAP, OE_TAKER_DISABLED, OE_ENTRY_MODE_BLOCK, OE_BLOCKED_CONCURRENCY_GLOBAL, OE_BLOCKED_CONCURRENCY_SYMBOL, OE_REQUOTE_RATE_LIMITED, OE_REQUOTE_BUDGET_EXCEEDED, OE_BLOCKED_RATE_BUDGET, OE_PLAN_DEGRADED_RATE_BUDGET, `OE_CANCEL_REPLACE_TWO_PHASE`, `OE_REPLACE_BLOCKED_CANCEL_IN_FLIGHT`, `OE_STALE_ACK_GUARD`, `OE_LATE_FILL_RECONCILE_FREEZE`, `OE_KILLSWITCH_TIER1`, `OE_KILLSWITCH_TIER2`, `OE_KILLSWITCH_TIER3`, `OE_POSITION_DIVERGENCE_WARN`, `OE_POSITION_DIVERGENCE_HARD`, `OE_SYMBOL_STATUS_BLOCK`, `OE_RETRY_BUDGET_EXCEEDED`, `OE_RECONCILE_BUDGET_EXCEEDED`, `OE_ENVELOPE_MISSING_FIELD`, `OE_ENVELOPE_EXPIRED_ABORT`, `OE_TELEMETRY_MISSING`, `OE_TELEMETRY_OUTLIER_CLAMPED`.
 - Replay hooks: log `envelope_version_id_used`, `envelope_ts_ms`, `envelope_valid_for_ms` at send time to ensure deterministic replay with `plan_hash`.
- OrderEngine may pass realized trade-tape metrics upward for telemetry, but toxicity_score remains owned by Stream Eligibility; OrderEngine must not compute toxicity.

### Telemetry Output Contract (tighten-only upstream consumers)
- Per symbol/window emit: ops_health {ack_latency_p95/p99, reject_rate, cancel_fail_rate, reconnect_count, rate_limit_hits}, execution_quality {realized_slip_bps, fees_bps, fill_latency_ms_p95/p99}, optional markouts {markout_1s_bps, markout_5s_bps, markout_30s_bps}. Used only for tightening upstream; never for loosening intraday.
- Telemetry anomalies: if required metrics missing -> `OE_TELEMETRY_MISSING`; if extreme outliers need clamping -> `OE_TELEMETRY_OUTLIER_CLAMPED` and treat as degraded.

### Deterministic Replay & Audit Requirements
- Log `plan_hash` at every state transition, `envelope_version_id_used`, and `intent_id`<->`clientOrderId` mapping for audit.
- Determinism: same (intent + envelope snapshot) must produce the same `plan_hash` and child plan; any deviation is a bug.

### Invariants & Property-Based Tests (must-pass)
- Never place entry when `entry_mode=BLOCK` or `entry_blocked=true`.
- Never send taker when `taker_disallowed=true`; never cross spread in MAKER_ONLY/PROBE_ONLY.
- Never open net short on spot; replay yields same `plan_hash` for same intent+envelope snapshot.
- Cancel-in-flight prevents replacement submit (two-phase honored); late fill after cancel triggers reconcile + freeze.
- Kill-switch tiering blocks entries/requires reduce-only/flatten per tier; position divergence triggers warnings/blocks per thresholds.

### Chaos / Property Test Harness Spec (minimal)
- stale envelope -> inject expired `envelope_ts_ms` -> expect abort submit; reason `OE_ENVELOPE_EXPIRED_ABORT`; no entry sent.
- taker_disallowed -> force flag true -> assert zero taker orders.
- cancel-in-flight -> set CANCEL_REQUESTED before replace -> replacement blocked; reason `OE_REPLACE_BLOCKED_CANCEL_IN_FLIGHT`.
- post-only reject storm -> inject repeated post-only rejects -> intent canceled + cooldown; reason `OE_POSTONLY_REJECT_COOLDOWN`.
- late fill after cancel -> deliver fill after cancel confirm -> reconcile + freeze entries; reason `OE_LATE_FILL_RECONCILE_FREEZE`.
- rate-limit storm -> inject 429s -> entries blocked, exits allowed; reason `OE_BLOCKED_RATE_BUDGET` or killswitch tier if enabled.
- divergence hard -> inject position divergence beyond hard threshold -> enforce reduce-only tier; reason `OE_POSITION_DIVERGENCE_HARD` (+ killswitch if configured).

### Non-goals / boundaries
- Must not compute regimes/indicators/depth feasibility/dq_score.
- Must not loosen constraints from Stream Eligibility or RiskManager; must operate strictly inside the Feasibility Envelope and sizing/caps.
- Must not create entry signals; only actuate provided intent.

### Appendix: Derivatives/Margin-only (inactive for SPOT)
- This appendix captures legacy symmetric long/short handling for potential margin/derivatives deployments; it is INACTIVE for SPOT.
- Legacy symmetric rule (inactive on spot): if a live long flips to short (or vice versa), exit the existing side then enter the opposite bias only when margin/borrow allows and risk policy permits net shorting/longing accordingly.
- Spot remains LONG-entry-only with SHORT intents used solely for EXIT/REDUCE (no net short opens).


## Machine_learning

- (If/when ML is used; features/targets; constraints; fallback behavior)
