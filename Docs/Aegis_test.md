# Heist Strategy Doc (Scalp Trading)

Use this as the single place for scalp strategy details. Update sections as the strategy evolves.

## AI_Rules
- (Assistant conduct, boundaries, truthfulness; align with Docs/rules/AI_Rules.md)
- Strictly follow Docs/rules/AI_Rules.md and its Documentation Protocol (INTEGRATE/REFACTOR, Shared/Common + deltas-only, required logs) for any edits to this doc.
- Must read and follow this document line by line before proposing or coding strategy changes.
- In chat, always surface advantages, disadvantages, and key facts when suggesting logic or code changes to this strategy.
- When discussing regimes or changes, propose clear benefits/risks and guards; do not add regimes without explicit rules and validation.
- If any part of the doc (strategy, regimes, indicators, risk, scoring, data, execution, etc.) is missing or unclear, ask the user for clarification rather than guessing.
- Do not ask where state is stored; follow documented storage notes and only request clarification if the doc lacks required detail.

## Strategy_Rules (must follow)
- This document is authoritative; follow every line when designing/updating the scalp strategy.
- All information must be verified in order: (1) trading books/reference material, (2) All AI knowledge base, (3) trusted online sources. Do not deviate from this order.
- Purpose: scalp trading with 1â€“20 minute horizons; operates 24/7.
- Strategy supports long/short entries and short/long exits, but SHORT on spot is exit/reduce only (no net short opens).
- Indicators must be chosen by: (a) precision of signal, (b) richness of information per indicator, (c) computational lightness/latency in software.
- Any conflict from a single indicator must be confirmed or denied by another independent indicator before action.
- Core invariants: REST/WS-free strategy layer; order flow goes through RiskManager/OrderEngine; no direct exchange calls in strategy.
- Treat each symbol independently: params, risk limits, adaptives, and bias flips are per-symbol; no cross-symbol coupling except explicit cluster caps.
- Spot asset handling rules:
  - Any spot wallet asset that is actively monitored (per exchange_info and TF analysis) can be promoted to LIVE_HOT and traded long or short (exit/reduce) to mitigate drop risk on either side of the pair.
  - If a live long is open and fresh analysis flips to short: confirm the short; if the position is safe (no loss), exit then flip; if unsafe, exit immediately. No lingering in conflicting bias.
  - Symmetric handling for live shorts: if analysis flips to long, confirm; exit safely if possible, otherwise exit immediately.

## Strategy_Idea
- Multi-brain scalp:
  - Mean-reversion: fade 1m VWAP z extremes with RSI/micro confirm.
  - Momentum/breakout: M5/M15/H1 trend/breakouts with 1m confirm.
  - Range: tighter fades in RANGE/moderate vol.
- Regime/routing: router selects one strategy based on regime weights; CHAOTIC or strong TREND_DOWN can block longs; range prefers mean-rev, trend prefers momentum.
- Goal: capture short moves (1â€“20m horizon) with strict edge gating (net of fees + expected slippage).

## Execution & Order Handling
- Per-symbol flow: Signals â†’ RiskManager â†’ OrderEngine; all gating/sizing is per-symbol (plus cluster/global caps).
- RiskManager: sizing modes (RISK_FRACTION, CONSTANT_NOTIONAL, EQUAL_SPLIT), per-symbol overrides, global/symbol caps (daily loss/drawdown/streak), cluster caps, cooldowns. Expected edge must exceed fees+slippage.
- OrderEngine gates: kill-switch/trading_enabled, one position per symbol, mode=SCALP, cooldowns; short = exit/reduce only on spot (no net-short opens).
- Order types: Entries default LIMIT inside spread (LIMIT_ENTRY_ALPHA); MARKET only if enabled + spread/slippage within caps. Exits default LIMIT; urgent exits (health/withdraw/emergency) may use MARKET if caps allow, else critical log and LIMIT.
- Unfilled/aged LIMITs: polling cancels invalid NEW orders (micro/spread/kill-switch); partial fills exited conservatively.
- Journaling: orders/positions/decision_log/trade_journal are mode-tagged (PAPER/LIVE). Slippage and PnL go to symbol_stats.
- Bias flips (per symbol, confirmed only; block during shock/coverage/micro failures):
  - If pos=LONG and bias â†’ SHORT: EXIT LONG immediately (maker preferred if safe; market allowed for emergency); stay FLAT (no short entry on spot).
  - If pos=SHORT and bias â†’ LONG: only relevant if any short state exists in code; otherwise ignore. If present, EXIT SHORT; re-enter long only after cooldown + confirm + edge/micro; if unsafe, EXIT SHORT immediately; no immediate flip from flat.
  - Always require confirmation (e.g., M1 persistence + confirming candle); never reverse inside event/liquidity shock or stale/gappy coverage; spot SHORT remains exit/reduce only.
  - Define micro_ok: spread/depth within caps, no event/shock lock, coverage fresh.
  - Define safe: unrealized_pnl â‰¥ 0 AND exit can be executed without violating risk/micro guards. In SHOCK, still exit (risk-first) but do not flip until unlocked.

## Confirmation Rules
- Entry hygiene: 1m persistence + confirming candle before entries; applied per symbol.
- Micro checks: spread caps, micro_score, depth/OFI where available; conflicts require a second indicator to confirm/deny.
- Regime checks: H1 regime filter blocks longs in strong TREND_DOWN; CHAOTIC can disable entries; applied per symbol.

## Regimes
- Computed from stored bars (H1/M15/M5 trend/vol) with clear, non-overlapping buckets. Each symbol is classified independently.
- Classifier (deterministic): Direction (H1/M15 structure + EMA slope) Ã— Volatility state (RTV/ATR bands) Ã— Clarity (micro/coverage). Ambiguous â†’ Chaotic/Avoid.
- Buckets with rules (per symbol):
  - **Uptrend â€“ calm/normal vol**
    - Detection: Uptrend (H1/M15 EMAs up + HH/HL) AND vol near baseline.
    - Allow: momentum/breakout longs; mean-rev only as pullback with strong micro OK. Shorts = exit/reduce only on spot.
    - Gates: M1 persistence + confirming candle; per-symbol micro/spread caps; edge > fees+slip; strong down/chaotic on higher TF blocks longs.
  - **Uptrend â€“ expanding/high vol**
    - Detection: Uptrend + vol/ATR in expansion (â‰¥ upper band for several bars).
    - Allow: momentum/breakout longs with tighter sizing/micro/edge caps; mean-rev caution/avoid.
    - Gates: stricter micro/slippage caps; edge must compensate high vol; if TF disagreement appears â†’ Chaotic/Avoid.
  - **Downtrend â€“ calm/normal vol**
    - Detection: Downtrend (H1/M15 EMAs down + LH/LL) AND vol near baseline.
    - Allow: shorts = exit/reduce only on spot; mean-rev fades only with strong confirmation.
    - Gates: block longs in strong down; per-symbol micro/edge caps apply.
  - **Downtrend â€“ expanding/high vol**
    - Detection: Downtrend + vol expansion spike.
    - Allow: exits prioritized; entries generally avoided; spot shorts = exit/reduce only.
    - Gates: strict edge/micro caps; if structure unclear â†’ Chaotic/Avoid.
  - **Range / compression**
    - Detection: Range direction (flat/overlapping EMAs, mixed swings) + vol compression (low ATR/range).
    - Allow: mean-rev/range fades (VWAP z, RSI) with micro confirm; momentum muted.
    - Gates: micro sanity; avoid if liquidity thin; edge > fees+slip.
  - **Range with expansion**
    - Detection: Range direction + vol/ATR expansion (high).
    - Allow: only if breakout/volatility playbook is explicitly enabled; otherwise treat as high-risk/avoid; mean-rev caution.
    - Gates: strict micro/edge caps; require multi-TF confirmation to avoid whipsaw; ambiguous â†’ Chaotic/Avoid.
  - **Trend with compression**
    - Detection: Up/Down bias intact but vol below baseline; shrinking ranges/pullback-like.
    - Allow: â€œwait/holdâ€ bias unless a defined pullback/continuation setup is enabled; reduce size if trading; spot shorts remain exit-only.
    - Gates: maintain trend filters; micro/edge caps apply; if compression persists with mixed signals â†’ Range.
  - **Chaotic / high-vol / no clear direction**
    - Detection: TF conflict + vol spikes without structure; poor micro (spread/depth/OFI erratic) or stale/gappy coverage.
    - Allow: avoid entries; exits/flatten only; hard lock until micro + coverage normalize.
- override (Event/Shock Avoid): spread blowout/depth collapse or other shock â†’ freeze entries; resume only after micro normalizes (e.g., spread â‰¤ 1.5Ã— median and depth â‰¥ 70% baseline for a cooldown).
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

## Risk_management
CANONICAL START (Risk_management)
- The content between CANONICAL START/END is authoritative.
- If any duplicated/garbled text appears below CANONICAL END, it is legacy/forensics only and must be ignored by implementers.
- Per-symbol: sizing, caps, cooldowns are per symbol; global caps and cluster caps layer on top.
- Sizing modes: RISK_FRACTION (default), CONSTANT_NOTIONAL, EQUAL_SPLIT; per-symbol overrides bounded by global caps.
- Config surface (single source of truth; declare once here):
  - Sizing keys: Q_MIN_ENTRY, Q_MAX_ENTRY (per symbol + global), Q_DEPTH_FRAC (liquidity fraction clamp), CONST_NOTIONAL_USDT, risk_budget_usdt (for RISK_FRACTION), equity_cap_usdt (for EQUAL_SPLIT).
  - Caps: MAX_CONCURRENT_POS, MAX_SYMBOL_NOTIONAL, MAX_GROSS_NOTIONAL, MAX_NET_NOTIONAL, DAILY_LOSS_LIMIT_R, SESSION_DRAWDOWN_LIMIT_R (or equivalents).
  - Cost budget: COST_BUDGET_BPS (bps) is defined here; Stream Eligibility consumes it (no redefinition).
  - Fee worst-case input (for Stream Eligibility cost gate):
    - Defined as stream_eligibility.ws_depth.FEE_BPS_WORSTCASE (venue/account-tier setting); RiskManager consumes the resulting pass/fail via Stream Eligibility, not the fee source.
- Defaults (conservative placeholders; tune per venue/fees before live):
  - risk_manager.mode = "RISK_FRACTION" (options: RISK_FRACTION | CONSTANT_NOTIONAL | EQUAL_SPLIT)
  - risk_manager.equity_cap_usdt = 10000
  - risk_manager.risk_budget_usdt = 1000
  - risk_manager.CONST_NOTIONAL_USDT = 50
  - risk_manager.Q_MIN_ENTRY = 10
  - risk_manager.Q_MAX_ENTRY = 200
  - risk_manager.Q_DEPTH_FRAC = 0.20
  - risk_manager.MAX_CONCURRENT_POS = 5
  - risk_manager.MAX_SYMBOL_NOTIONAL = 0.20 * equity_cap_usdt
  - risk_manager.MAX_GROSS_NOTIONAL = 1.00 * equity_cap_usdt
  - risk_manager.MAX_NET_NOTIONAL = 0.50 * equity_cap_usdt
  - risk_manager.DAILY_LOSS_LIMIT_R = 3.0
  - risk_manager.SESSION_DRAWDOWN_LIMIT_R = 4.0
  - risk_manager.LOSS_STREAK_LIMIT = 5
  - risk_manager.COST_BUDGET_BPS = 25
- Sizing pipeline (deterministic):
  - RiskManager computes Q_base from the selected sizing mode (CONST_NOTIONAL / RISK_FRACTION using risk_budget_usdt + stop distance / EQUAL_SPLIT using equity_cap_usdt and n_live_hot).
  - Stream Eligibility clamps Q_base → Q_entry_eff via micro gates (shock/depth/slip/spread/feasibility) using Q_MIN_ENTRY / Q_MAX_ENTRY / Q_DEPTH_FRAC and configured caps.
  - Final order sizing uses Q_entry_eff; maker-first + taker-within-caps remains a high-level rule (no order-type playbook here).
- Adaptive sizing clamps (slow, bounded adaptives; sizing remains strategy-agnostic):
  - Definition: RiskManager computes a base planned notional Q_base from the chosen sizing mode, then applies bounded clamps using microstructure gates (spread/depth/slippage/shock) to produce Q_entry_eff.
  - Base sizing (existing modes):
    - CONSTANT_NOTIONAL: Q_base = CONST_NOTIONAL_USDT
    - RISK_FRACTION: Q_base derived from risk_budget_usdt and stop distance; then converted to quote-notional at current mid
    - EQUAL_SPLIT: Q_base = equity_cap_usdt / max(n_live_hot, 1)
  - Clamp inputs (from eligibility/micro layers):
    - liq_state (HEALTHY|THIN|SHOCK), spread_bps (L1), min_depth_quote(N) (L3), slip_bps(Q_entry) or slip_bps(Q_base) if enabled, and INSUFFICIENT_VISIBLE_DEPTH flag.
  - Clamp policy (apply in this order):
    - SHOCK clamp: if liq_state == SHOCK â‡’ Q_entry_eff = 0 (block new entries); exits/reductions are handled elsewhere.
    - Depth clamp (liquidity fraction): Q_entry_eff â‰¤ Q_DEPTH_FRAC * min_depth_quote(N)  (prevents oversized entries vs visible liquidity)
    - Slippage clamp (if enabled): iteratively shrink Q_entry_eff until max(slip_bps_buy(Q_entry_eff), slip_bps_sell(Q_entry_eff)) â‰¤ SLIP_CAP_BPS, else block if it cannot be satisfied above Q_MIN_ENTRY.
    - Spread clamp: if spread_bps > SPREAD_CAP_BPS (or emergency cap) â‡’ block or reduce to Q_MIN_ENTRY depending on policy (prefer block for entries).
    - Visibility clamp: if INSUFFICIENT_VISIBLE_DEPTH for the planned size â‡’ reduce size or block (prefer block if frequent).
  - Slow, bounded adaptives:
    - Any adaptive multipliers (e.g., Q_DEPTH_FRAC, per-symbol Q_max) must be updated slowly (e.g., every 5â€“60s) and bounded within [min,max] ranges.
    - Freeze adaptive updates during feed stress (VALID set too small / staleness); reuse last-good parameters.
  - Required params (no hard numbers here; configured elsewhere):
    - Q_MIN_ENTRY, Q_MAX_ENTRY (per symbol and global), Q_DEPTH_FRAC, SLIP_CAP_BPS (optional), SPREAD_CAP_BPS (from L2), and a boolean ENABLE_SLIP_CAP.
- Sizing pipeline (explicit):
  - Step 1 (Q_base): per mode, bounded by Q_MIN_ENTRY..Q_MAX_ENTRY.
  - Step 2 (Q_entry_eff): Stream Eligibility tightening only (feasibility, slip/spread/cost, shock/quarantine).
  - Step 3 (Q_final): apply caps (per-order, per-symbol, portfolio). If Q_final < Q_MIN_ENTRY ⇒ block new entry; exits allowed.
  - Step 4: OrderEngine executes with maker-first; taker only within caps for urgent exits.
- Caps: global/symbol open-risk, daily loss R, drawdown R, loss streak; cluster caps; cooldowns instead of full-day bans when limits trip.
- Equity cap: MAX_TRADING_EQUITY_USDT; excess routes to withdraw queue (if enabled).
- Stops/exits enforced via OrderEngine; urgent exits allowed under configured caps.
- Caps enforcement (pre-trade + post-fill):
  - Pre-trade: enforce MAX_CONCURRENT_POS, MAX_SYMBOL_NOTIONAL, MAX_GROSS_NOTIONAL, MAX_NET_NOTIONAL before placing/adjusting entries. If a cap binds and Q_final < Q_MIN_ENTRY, block entry.
  - Post-fill: update exposures on fill; recompute remaining caps immediately. Exits allowed even when caps bind; respect exchange minNotional/stepSize filters.
  - Reason codes (RiskManager): RISK_CAP_CONCURRENT, RISK_CAP_SYMBOL, RISK_CAP_GROSS, RISK_CAP_NET, RISK_BLOCK_Q_TOO_SMALL, RISK_BLOCK_DAILY_LOSS, RISK_BLOCK_SESSION_DD, RISK_BLOCK_LOSS_STREAK.
- Slow, bounded adaptives (RiskManager):
  - Allowed adaptives (tightening only): size_mult ∈ [0.50, 1.10]; optional per-symbol size_mult_sym ∈ [0.50, 1.00] (small caps tighter by default).
  - Update cadence: at most once per ADAPT_REFRESH_SEC (default 60s).
  - Freeze triggers: during WARMUP/STALE_FEED/COOLDOWN, feed stress, repeated shocks/quarantine, BARS_WARMUP/BARS_STALE; reuse last-good.
  - Inputs to tighten: feed stress, BOOK_GAMEY, repeated shocks, TF_CONFLICT caution, elevated realized slip (if available).
  - Reason tags (telemetry): SIZE_TIGHTEN_FEED, SIZE_TIGHTEN_SHOCK, SIZE_TIGHTEN_GAMEY, SIZE_TIGHTEN_TF_CONFLICT, SIZE_TIGHTEN_COST.
- RiskManager telemetry (required):
  - Per decision tick (or THRESH_REFRESH_SEC): {mode, equity_cap_usdt, risk_budget_usdt, Q_base, Q_entry_eff, Q_final, size_mult, caps_hit[], primary_reason, secondary_reasons(optional), exposure_before{gross,net,per_symbol}, exposure_after{gross,net,per_symbol}, drawdown_state{daily_R, session_R, loss_streak}, thresholds_version_ts_streams, bars_ready_state}.
  - Events: RISK_STATE_CHANGE (daily loss/session DD/loss streak), CAP_BIND_CHANGE, SIZE_MULT_CHANGE (with tighten reason).
- Determinism:
  - Given recorded inputs (bars, WS streams, thresholds snapshots, config versions) and deterministic cadence, RiskManager decisions are deterministic; no randomness used.
### Risk_management (Execution-aware scalping) — expanded concepts + computations
- Purpose (scalping-specific):
  - Risk_management is part of the strategy: it controls execution risk (spread/slip/impact/fees), exposure concentration, and drawdown stops so that small-edge scalps are not overwhelmed by costs.
  - RiskManager owns sizing/caps keys; Stream Eligibility tightens only (microstructure feasibility + cost/shock) and returns Q_entry_eff.

#### A) Base sizing (Q_base) — computation sketches (deterministic)
- Mode: RISK_FRACTION
  - Define per-trade risk budget: R_usdt = risk_fraction * equity_usdt (or use risk_budget_usdt).
  - If using stop distance: q_base_units = R_usdt / max(stop_dist_usdt_per_unit, EPS); Q_raw = q_base_units * mid_price.
  - If no hard stop: use volatility proxy for deterministic “effective stop” (example):
    - stop_dist_usdt_per_unit = k_vol * ATR_1m (or k_vol * ATR_5m) converted to USDT per unit.
  - Bound: Q_base = clamp(Q_raw, Q_MIN_ENTRY, Q_MAX_ENTRY).
- Mode: CONSTANT_NOTIONAL
  - Q_base = clamp(CONST_NOTIONAL_USDT, Q_MIN_ENTRY, Q_MAX_ENTRY).
- Mode: EQUAL_SPLIT
  - Q_split = MAX_GROSS_NOTIONAL / max(MAX_CONCURRENT_POS,1)
  - Q_base = clamp(min(Q_split, Q_MAX_ENTRY), Q_MIN_ENTRY, Q_MAX_ENTRY).

#### B) Microstructure sizing clamps (tighten-only) — Q_base → Q_entry_eff
- Depth fraction clamp (liquidity-aware):
  - min_depth_quote(N) = min(bid_quote_N, ask_quote_N) from partial depth within N levels.
  - Q_depth_cap = Q_DEPTH_FRAC * min_depth_quote(N)
  - Q1 = min(Q_base, Q_depth_cap)  (reason DEPTH_FRAC_CLAMP)
- Slippage-cap sizing (execution cost cap; if enabled):
  - slip_bps(Q) estimated from walking the book over N levels (or a proxy if configured).
  - Find the largest Q such that slip_bps(Q) ≤ SLIP_CAP_BPS; set Q2 = min(Q1, Q_slip_cap) (reason SLIP_CAP_CLAMP).
- Spread/cost budget gate (viability check):
  - cost_bps_entry = spread_bps + slip_bps(Q2) + fee_bps_worstcase
  - Require cost_bps_entry ≤ risk_manager.COST_BUDGET_BPS else block NEW entry (reason COST_TOO_HIGH).
- Shock/cooldown/quarantine honoring:
  - If Stream Eligibility returns SHOCK_LOCK / COOLDOWN_ACTIVE / FEED_LAG_QUARANTINE / BOOK_GAMEY / REPEATED_SHOCKS:
    - Block NEW entries; allow exits/reductions (primary reason = deepest level reached).
- Result: Q_entry_eff = Q2 after tighten-only clamps and viability gates.

#### C) Caps enforcement (RiskManager) — Q_entry_eff → Q_final (pre-trade + post-fill)
- Pre-trade enforcement order (tighten-only):
  1) Concurrent cap: if open_positions ≥ MAX_CONCURRENT_POS -> block NEW entry (RISK_CAP_CONCURRENT).
  2) Symbol cap: Q <= remaining_symbol_cap_usdt = MAX_SYMBOL_NOTIONAL - symbol_exposure_usdt.
  3) Gross cap: Q <= remaining_gross_cap_usdt = MAX_GROSS_NOTIONAL - gross_exposure_usdt.
  4) Net cap: Q <= remaining_net_cap_usdt = MAX_NET_NOTIONAL - abs(net_exposure_usdt in intended direction).
  - Q_final = min(Q_entry_eff, remaining_symbol_cap, remaining_gross_cap, remaining_net_cap).
  - If Q_final < Q_MIN_ENTRY -> block NEW entry (RISK_BLOCK_Q_TOO_SMALL).
- Post-fill:
  - Update exposures immediately on fills; recompute remaining caps for subsequent decisions.
  - Exits/reductions remain allowed even when entry caps bind (still must pass exchange filters).

#### D) Venue filters (exchange feasibility) — applied last (reject prevention)
- Apply exchangeInfo filters to the final order request:
  - minNotional, lotSize/stepSize, tickSize.
- If rounding down causes Q_final to fall below minNotional/stepSize -> block NEW entry (ORDER_SIZE_INVALID) rather than rounding up into higher risk.
- Record the exact rounded quantities/prices in telemetry for replay.

#### E) Drawdown / loss-streak stops (risk state machine)
- Evaluate on every decision tick (pre-trade):
  - If daily_R ≥ DAILY_LOSS_LIMIT_R -> block NEW entries (RISK_BLOCK_DAILY_LOSS).
  - If session_R ≥ SESSION_DRAWDOWN_LIMIT_R -> block NEW entries (RISK_BLOCK_SESSION_DD).
  - If loss_streak ≥ LOSS_STREAK_LIMIT -> block NEW entries (RISK_BLOCK_LOSS_STREAK).
- Recovery:
  - Daily reset at trading-day boundary; session reset at configured session boundary; optional cooldown after breach.
- Exits/reductions always allowed.

#### F) Safe adaptives (slow, bounded; tighten-only)
- Allowed adaptives:
  - size_mult (global) ∈ [0.50, 1.10]; size_mult_sym ∈ [0.50, 1.00] (SMALLCAP_THIN must never exceed 1.00).
- Cadence:
  - Update at most once per ADAPT_REFRESH_SEC; freeze updates during WARMUP/STALE_FEED/COOLDOWN_ACTIVE/BARS_WARMUP/BARS_STALE.
- Inputs allowed to tighten only:
  - repeated shocks/quarantine, BOOK_GAMEY, TF_CONFLICT caution mode, elevated realized slippage metrics (if logged).
- Never loosen beyond configured maxima; never “learn” looser staleness/feasibility bounds as a fix.

#### G) Telemetry + determinism (required for ops + backtest)
- Determinism:
  - No randomness; decisions are deterministic given recorded inputs (bars + WS streams + thresholds snapshots + config versions) evaluated on DECISION_LOOP_MS cadence.
- Per decision tick log (minimum):
  - {mode, equity_usdt, Q_base, Q_entry_eff, Q_final,
     clamp_reasons[], caps_hit[], primary_reason, secondary_reasons(optional),
     exposures_before/after{gross_usdt, net_usdt, per_symbol_usdt},
     drawdown_state{daily_R, session_R, loss_streak},
     thresholds_version_ts_streams, bars_ready_state, config_version}
- Event logs (transitions only):
  - CAP_BIND_CHANGE, RISK_STATE_CHANGE, SIZE_MULT_CHANGE.

### Required inputs to collect (Spot long/flat) — for deterministic RiskManager + backtest
- Account state:
  - equity_usdt, free_usdt, per-symbol inventory (qty, avg entry), open_orders/reserved.
- Exchange filters (per symbol, from exchangeInfo):
  - minNotional, stepSize/lotSize, tickSize, minQty/maxQty if present.
- Fees (config/account tier):
  - fee_bps_worstcase (taker worst-case; maker optional if modeled).
- Stream Eligibility outputs (consumed; RiskManager does not recompute microstructure):
  - Q_entry_eff, primary_reason (+ secondary optional), state flags (COOLDOWN_ACTIVE/SHOCK_LOCK/FEED_LAG_QUARANTINE/BOOK_GAMEY/etc.),
    thresholds_version_ts per level.
- Bars readiness / TF context flags:
  - bars_ready_tf, bars_stale_tf; optional TF alignment class used only to tighten (size_mult) not to loosen.
- Exposure and caps state (USDT notional units):
  - gross_usdt, net_usdt (kept for consistency), per_symbol_usdt, open_positions_count.
- Drawdown/loss state:
  - daily_R (or daily_pnl_usdt), session_R (or session_pnl_usdt), loss_streak; reset boundaries.
- Replay metadata:
  - decision_ts_ms, DECISION_LOOP_MS, config_version snapshots, stream state snapshot ids.
CANONICAL END (Risk_management)
- Ignore any repeated/garbled text below this marker (do not implement from it).

## Promotion / State Constraints
- Per-symbol promotion/state: symbols must meet promotion/state rules (e.g., LIVE_COLD/HOT) based on net-of-fee/slippage edge and performance.
- Modes (SCALP/HOLD/SLEEP) and kill-switch/trading_enabled gates apply per symbol.

## Machine_learning
- (If/when ML is used; features/targets; constraints; fallback behavior)

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
    - Missing handling: missing tickSize/stepSize/notional â‡’ drop; missing MAX_NUM_ORDERS/MAX_NUM_ALGO_ORDERS â‡’ keep (unknown; no penalty).
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
    - Precision precedence: price must conform to PRICE_FILTER.tickSize; quantity to LOT_SIZE.stepSize; filters win over â€œprecision fields.â€
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
    - Staleness/skew: if closeTime older than MAX_TICKER_STALE_MS â†’ mark stale and trigger refresh; tolerate small skew up to SKEW_TOL_MS, larger skew â†’ warn, keep snapshot.
    - Small N/warmup: if N<MIN_N_FOR_PERCENTILES, reuse last-good thresholds; if none, state=WARMUP_TICKER_THRESHOLDS and skip ticker gating this cycle. Emit WARN with n_total, n_activity, â€œticker gating skipped this cycle; thresholds not stabilized.â€
  - Store per symbol: symbol, openTime, closeTime, quoteVolume, count, volume, openPrice, highPrice, lowPrice, lastPrice, priceChangePercent. Other fields optional/not used for gating.
  - Derived per symbol: activity_score = ln(max(quoteVolume, EPS)) + ACTIVITY_ALPHA*ln(max(count,1)); range_pct_24h = (high-low)/max(low, EPS); abs_change_pct_24h = abs(priceChangePercent).
  - Thresholds (per refresh): compute activity gates on full set: MIN_QVOL_24H=P60(quoteVolume); MIN_TRADES_24H=P60(count). Let S_activity = symbols passing both. If |S_activity|â‰¥MIN_N_FOR_PERCENTILES: MIN_RANGE_PCT_24H=P25(range_pct_24h over S_activity); MAX_ABS_CHANGE_PCT_24H=P95(abs_change_pct_24h over S_activity). Else reuse last-good thresholds or set WARMUP_TICKER_THRESHOLDS (skip gating).
  - Eligibility (REST-only): gates are computed as above. Symbols that meet all four gates are â€œeligibleâ€; those that do not are kept but annotated as blocked for data-driven reasons (INACTIVE_24H, RANGE_TOO_LOW, MOVE_TOO_EXTREME, TICKER_FAIL_STREAK).
  - Ranking (all symbols): sort by (1) score_ex ascending, (2) activity_score descending, (3) tie = symbol. Keep two ordered lists: eligible_symbols_rest_step1 and blocked_symbols_rest_step1 (blocked carry their reason code); do not drop blocked symbols entirely.
  - SQLite cache schema (latest only):
    - ticker24h_full_latest(symbol PK, snapshot_ts, openTime, closeTime, quoteVolume, count, volume, openPrice, highPrice, lowPrice, lastPrice, priceChangePercent, range_pct_24h, abs_change_pct_24h, activity_score, ticker_stale DEFAULT 0, fail_streak DEFAULT 0, last_error TEXT).
    - Index: CREATE INDEX IF NOT EXISTS idx_ticker24h_latest_snapshot_ts ON ticker24h_full_latest(snapshot_ts).
    - ticker24h_snapshot_state(id=1, last_refresh_ts, state OK/STALE/DEGRADED/WARMUP_TICKER_THRESHOLDS, last_ok_ts, notes).
    - ticker24h_thresholds_latest(id=1, computed_ts, min_qvol_24h, min_trades_24h, min_range_pct_24h, max_abs_change_pct_24h, n_total, n_activity).
    - rank_ex remains in exchangeInfo cache; join at query time. eligible_symbols_rest_step1 is computed each cycle (not persisted).
  - Snapshot health: on refresh failure keep last-good, state=STALE; if age>MAX_SNAPSHOT_AGE_MS state=DEGRADED and block new entries (exits still allowed). WARMUP_TICKER_THRESHOLDS means thresholds not stabilized; skip ticker gating that cycle but flag it.
  - Drop/aging: if a symbol disappears from exchangeInfo, remove from universe immediately (no rank/trade; stale row may be kept for audit only). If fail_streak â‰¥ FAIL_STREAK_DROP, exclude from ticker eligibility/ranking (reason TICKER_FAIL_STREAK) until a successful refresh resets streak; keep last data in ticker24h_full_latest with ticker_stale=1/fail_streak/last_error for reporting/debug. On successful refresh per symbol: fail_streak=0, ticker_stale=0, last_error=NULL; on failed batch/parse: fail_streak++, ticker_stale=1, last_error=<error string>.
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
- Cancel/replace semantics: handle partial fills safely; do not assume cancel succeeds instantly; maintain “intent state” until confirmed.
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

### 1) Candles/Bars Stream (TF Coverage + Roles + Redundancy Control)

#### Recommended bar coverage (Hot vs Cold)
- live_Hot (deeper context):
  - M1: 600 bars (~10 hours)
  - M5: 480 bars (~40 hours / ~1–2 days)
  - M15: 384 bars (~96 hours / ~2–4 days)
  - H1: 336 bars (~14 days)
- live_Cold (lighter context):
  - M1: 300 bars (~5 hours)
  - M5: 240 bars (~20 hours / ~1 day)
  - M15: 192 bars (~48 hours / ~2 days)
  - H1: 168 bars (~7 days)

#### What each timeframe informs (distinct roles; avoid duplication)
- M1 (execution timing; 5–10 hours):
  - Immediate micro-regime (last-hours trend/range/chop), micro volatility/pace, local swing structure used for entry timing and short-horizon risk.
- M5 (intraday structure; 1–2 days):
  - Today vs yesterday structure, intraday trend quality vs mean reversion, key intraday levels; used as an intraday filter.
- M15 (multi-session regime; 2–4 days):
  - Multi-session trend/range regime, breakout validity relative to the last few days’ range, higher-quality S/R zones; used for trade bias/regime gating.
- H1 (macro regime; 7–14 days):
  - Weekly context, volatility regime shifts, major levels/danger zones; used for risk posture and tightening rules near macro zones.

#### Redundancy control (multi-TF anti-dup rules)
- Assign a single owner TF per concept:
  - Macro regime / volatility posture: H1
  - Trade bias / mean-reversion vs continuation regime: M15
  - Intraday filter / trend quality: M5
  - Entry timing and micro execution: M1
- Do not duplicate vetoes:
  - Never allow more than one TF to veto trades for the same concept (e.g., volatility, trend, range).
  - If H1 blocks due to high-vol regime, do not add a second high-vol block from M15/M5.
- Keep M1 as “timing only”:
  - M1 should not set macro bias; it only refines entries/exits consistent with higher TF context.

#### Safe Redundancy (TF alignment as modifiers, not extra vetoes)
- Principle:
  - Use ONE “owner TF” per concept for hard gating (veto).
  - Use redundancy across other TFs only as soft modifiers (confidence/size/caution), not as additional hard blocks.
- Alignment score (example; configurable):
  - Define per TF a directional/bias sign: bias_H1, bias_M15, bias_M5 ∈ {-1, 0, +1}.
  - Alignment score = count of TFs that match the owner direction (e.g., owner=M15):
    - align = I(bias_H1 == bias_M15) + I(bias_M5 == bias_M15)
  - Classify:
    - STRONG_ALIGN if align=2
    - MIXED if align=1
    - CONFLICT if align=0
- Actions (safe, bounded):
  - STRONG_ALIGN:
    - allow normal operation; optionally increase confidence and size slightly within bounds:
      - size_mult = min(1.10, size_mult_max)
  - MIXED:
    - caution mode:
      - size_mult = 0.70–0.90 (configurable)
      - stricter recovery/filters (e.g., require better depth health before entry)
  - CONFLICT:
    - do NOT add a new “trend veto”; instead apply defensive routing:
      - route symbol to live_Cold OR block NEW entries only if a separate, owner TF hard-gate already exists
      - size_mult = 0.50 (or block entries if already near other risk caps)
- Micro timing (M1) rule:
  - M1 does not change macro bias; it can only:
    - delay entries (wait for a confirming close)
    - tighten risk (smaller size / closer stop logic)
    - trigger a temporary pause if micro-vol spikes (cooldown-like behavior for entries only)
- Bounded adaptives:
  - Any multiplier adjustments must be slow and bounded:
    - clamp size_mult ∈ [0.50, 1.10]
    - update at most once per TF-refresh window (e.g., per 60s) and freeze during WARMUP/STALE_FEED.
- Logging/telemetry:
  - Emit per refresh: {bias_H1, bias_M15, bias_M5, align_class, size_mult, caution_mode}.
  - On transitions (align_class change), emit event: TF_ALIGN_CHANGE with prior/new class.

#### Bars Study Setup (Owner TF map + minimum outputs + bars warmup gate)
- Owner TF map (single owner per concept; prevents duplication):
  - H1 owner: macro_regime + vol_regime + macro_zone_risk (risk posture/tightening only).
  - M15 owner: trade_bias (trend vs mean-reversion regime) and multi-session range context.
  - M5 owner: intraday_filter (trend quality/session structure) and key intraday levels.
  - M1 owner: execution timing only (entry/exit triggers, micro_vol, local_swings); M1 must not set macro bias.
- Minimum outputs (keep small; expand later only if needed):
  - H1 outputs: {macro_regime, vol_regime, macro_zone_risk}
  - M15 outputs: {trade_bias, mr_vs_trend, range_context}
  - M5 outputs: {intraday_filter, trend_quality, session_levels}
  - M1 outputs: {entry_timing, micro_vol, local_swings}
- Bars readiness / warmup gate (data coverage requirement):
  - Maintain per TF: bars_ready_tf = (n_closed_bars_tf ≥ LOOKBACK_BARS_TF) and bars_stale_tf = (now_ms - last_closed_bar_arrival_ms_tf > BARS_STALE_MS_TF).
  - New-entry policy:
    - If any required TF is not ready OR is stale: block NEW entries (reason BARS_WARMUP or BARS_STALE).
    - Exits/reductions remain allowed.
  - Default lookbacks (from the Hot/Cold coverage table in this section):
    - live_Hot uses the “big counts”; live_Cold uses the “small counts”.
  - Closed-bars rule:
  - Use closed bars only for regime/bias calculations (H1/M15/M5); M1 may use forming bar for timing but must confirm with last closed bar when required by entry hygiene.
- Visibility:
  - Emit each TF refresh: {n_closed_bars_tf, bars_ready_tf, bars_stale_tf, last_closed_bar_arrival_ms_tf}.
  - Emit on transitions: BARS_READY_CHANGE (per TF) and BARS_WARMUP_CLEAR when all required TFs become ready.

### Bar validity, warmup, and safety policy (mirrors WS VALID-set philosophy)
- Per-TF bar readiness:
  - BAR_WARMUP(TF): count(bars_TF) < LOOKBACK_{Hot/Cold}_TF
  - BAR_STALE(TF): now_ms - last_bar_close_ts_TF > BAR_STALE_MS_TF
  - BAR_GAP(TF): detected missing bar(s) by timestamp sequence
- Policy:
  - If any required TF is BAR_WARMUP or BAR_STALE or BAR_GAP: block NEW entries (reason BAR_WARMUP/BAR_STALE/BAR_GAP) and allow exits/reductions only.
  - Warmup uses last-good derived TF features if available; never “invent” missing bars.

### TF redundancy control (safe application; avoid duplicate signals)
- Ownership (non-duplicative decision roles):
  - H1/M15: bias + macro/multi-session regime (risk posture + no-trade zones)
  - M5: intraday structure confirmation filter
  - M1: execution timing / trigger and short-horizon risk
- Redundancy is confirm/deny only:
  - Higher TF veto rule: if M15/H1 bias gate blocks, do not trade even if M1 trigger fires.
  - No additive voting/averaging across TFs for entry; redundancy only reduces risk (tighten, delay, or block).
- Optional confidence downgrade:
  - If M1 trigger conflicts with M5 structure, downgrade (size clamp / require extra confirmation) rather than taking “half signals.”

### Config surface (explicit keys)
- bars_stream.lookback.live_hot: {M1=600, M5=480, M15=384, H1=336}
- bars_stream.lookback.live_cold: {M1=300, M5=240, M15=192, H1=168}
- bars_stream.stale_ms: {M1=120000, M5=600000, M15=1800000, H1=7200000}  # defaults; configurable
- bars_stream.require_tfs_for_entry: [M1, M5, M15, H1]  # configurable
- bars_stream.enable_redundancy_veto=true

### Logging (for ML + backtest; minimal but sufficient)
- On each bar close per TF:
  - store {symbol, TF, bar_ts, O,H,L,C,V, ret_1, range, realized_vol, bar_valid_state}
- On each decision tick:
  - store {symbol, bias_state(H1/M15), structure_state(M5), trigger_state(M1), entry_allowed(bool), primary_block_reason, size_clamp_applied, version_ts}
- Keep consistent reason codes: BAR_WARMUP, BAR_STALE, BAR_GAP.

### 2) WS 24h Ticker Eligibility (Level 1)
- Inputs: WS `<symbol>@ticker` fields q,n,P,o,h,l,c,b,B,a,A,O,C; last_ticker_ts is local arrival.
- Derived: range_pct_24h=(h-l)/max(l,EPS); abs_change_pct_24h=abs(P); window_min=max((C-O)/60000,1); trades_per_min=n/window_min; qvol_per_min=q/window_min; mid=(a+b)/2; spread_bps_ticker=(a-b)/max(mid,EPS)*10_000; top_qty_min=min(A,B).
- Ticker window timing guard:
  - If WS ticker lacks reliable O/C timestamps, compute window_min from local arrival deltas (last_ticker_ts_local) to avoid bad per-minute rates.
- Valid/Thresholds: Valid if now_ms-last_ticker_ts <= TICKER_STALE_MS; N_valid >= MIN_N_FOR_PERCENTILES. Percentiles: P60(qvol_per_min), P60(trades_per_min), P25(range_pct_24h), P95(abs_change_pct_24h), P80(spread_bps_ticker), P40(top_qty_min). THRESH_REFRESH_SEC=30.
- Promotion: sanity (a>b>0, c>0, A,B>0); activity; range; abs-change; spread; top_qty_min gates.
- Demotion: stale > TICKER_STALE_MS OR fail criteria for DEMOTE_CONSEC_FAILS OR sanity break; cadence-based demotion (immediate optional). Warmup: WARMUP_WS_THRESHOLDS uses last-good or skips; WARN with N_valid etc.
- Liquidity class (metadata/routing only): SMALLCAP_THIN if (qvol_per_min<P60 OR trades_per_min<P60 OR spread_bps_ticker>P80); NORMAL otherwise. Recompute each refresh; if stale keep tag with tag_state=STALE_TAG; reset on restart unless persisted. Default consumer: route SMALLCAP_THIN to depth N=20 and stricter downstream recovery/quarantine; otherwise metadata only if routing-only disabled.
- Tag timestamp + staleness behavior:
  - tag_version_ts = thresholds_version_ts (no separate clock).
  - If tag_state=STALE_TAG, keep last-known tag but suppress routing changes driven by the tag until ticker is VALID again (informational only while stale).
- Level 1 policy note:
  - Level 1 is routing-only (universe/health/tagging). It does not block exits or manage positions; it controls promotion to Level 2 and routing metadata only.
- Reason codes (not promoted to bookTicker / routing block):
  - TICKER_STALE (now_ms - last_ticker_ts > TICKER_STALE_MS)
  - BAD_TICKER (non-finite fields, missing required fields)
  - WARMUP_TICKER_THRESHOLDS (N_valid < MIN_N_FOR_PERCENTILES)
  - LOW_ACTIVITY (fails activity floor: qvol_per_min or trades_per_min below adaptive floor)
  - EXTREME_MOVE (fails 24h move/range safety cap if enabled)
  - STALE_TAG (tag_state=STALE_TAG; informational; suppress routing changes)
- Config keys (make floors implementable):
  - LOW_ACTIVITY floors keyed via stream_eligibility.ws_24h_ticker.MIN_QVOL_PCTL / MIN_TRADES_PCTL (default P60; MIN_QVOL_PCTL=60; MIN_TRADES_PCTL=60).
  - EXTREME_MOVE cap keyed via stream_eligibility.ws_24h_ticker.MAX_ABS_CHANGE_PCTL (default P95 or configured; MAX_ABS_CHANGE_PCTL=98 here for explicit default).
  - Emit the active percentile choices in telemetry for audit/debug.
- Visibility: logger eligibility.ws_24h_ticker; emit {state, N_valid, N_promoted, max_ticker_age_ms, thresholds_version_ts}; states OK/WARMUP_WS_THRESHOLDS/STALE_FEED with STALE_ERROR_GRACE_MS=30000.
  - Logger: eligibility.ws_ticker.
  - Emit each refresh: {ws_ticker_state, thresholds_version_ts, N_valid, N_promoted_book, max_ticker_age_ms, top_reason_codes}.
  - STALE_TAG should emit WARN (telemetry-only) so operators know routing is suppressed until ticker validity returns.
  - Logger naming:
    - Use logger name "eligibility.ws_ticker" consistently for Level 1 ticker eligibility logs (aliases may map to this canonical name).

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
- Demotion: stale/sanity/u-order/fail criteria for DEMOTE_CONSEC_FAILS; immediate demotion between ticks optional. [REVIEW-CONFLICT]: cadence-based demotion is default; immediate demotion on detect is optional override.
- Note:
  - Treat the REVIEW-CONFLICT line as an internal comment: cadence-based demotion is the default; immediate demotion on detect is an optional override.
- SMALLCAP_THIN carry-over: tightens downstream (L3) routing/params (N=20, stricter quarantine); no L2 threshold change unless configured.
- Reason codes: BOOK_STALE, BAD_QUOTE, SPREAD_WIDE, SPREAD_EMERGENCY, TOP_THIN, BOOK_SHOCK, BOOK_OUT_OF_ORDER, WARMUP_WS_THRESHOLDS, QUOTE_UNSTABLE, BOOK_GAMEY_PREWARN (warn).
- Visibility: logger eligibility.ws_bookticker; emit {ws_book_state, thresholds_version_ts, N_valid, N_promoted_depth, max_book_age_ms}; severities OK/WARMUP_WS_THRESHOLDS/STALE_FEED with STALE_ERROR_GRACE_MS.
  - Include SPREAD_EMERGENCY_PCT alongside SPREAD_EMERGENCY_CAP_BPS and thresholds_version_ts so ops can confirm the active percentile.
- IMMEDIATE_DEMOTION switches (operational):
  - IMMEDIATE_DEMOTION_ON_STALE=false (default): if true, demote immediately on staleness detection between refresh ticks.
  - IMMEDIATE_DEMOTION_ON_BADQUOTE=false (default): if true, demote immediately on sanity break (ask = bid or non-positive) between refresh ticks.
  - Default production mode: cadence-based demotion; enable immediate demotion only if needed.

### 4) WS depth Eligibility (Level 3)
- Inputs: From L2 (symbol, PROMOTE_TO_DEPTH, last_book_ts, spread_bps/top_qty_min, hot/cold), exchangeInfo (tickSize, stepSize), WS partial depth payload (lastUpdateId, bids/asks), last_depth_ts local.
- Q_entry walk-the-book (once): BUY/SELL accumulate Q_rem with Q_i=p_i*q_i; compute VWAP_buy/sell and slip_bps; INSUFFICIENT_VISIBLE_DEPTH if not filled; NONFINITE_SLIP blocks.
- NONFINITE_SLIP policy:
  - NONFINITE_SLIP blocks entries for the current evaluation only; if it occurs NONFINITE_SLIP_CONSEC times consecutively, treat as feed/compute fault and demote/quarantine (reason NONFINITE_SLIP_QUARANTINE). Default NONFINITE_SLIP_CONSEC=3.
- Stream selection: partial depth only `<symbol>@depth{N}`[@100ms]; hot@100ms, cold@1000ms; start N=20; optimize down via coverage+slip metrics; subscription budget with COOLDOWN_SEC=60; diff depth is excluded/disabled (legacy note; do not implement).
- Partial-depth-only enforcement:
  - Ignore any mention of diff-depth here; diff-depth/local book reconstruction is out of scope for this design (live gating uses WS partial depth only).
- Out of scope note (partial depth only):
  - This design excludes diff-depth/local book reconstruction for live gating; eligibility uses WS partial depth top-N only.
  - Operational enforcement: do NOT subscribe to diff-depth streams in production for this design (partial depth only).
- Cooldown/quarantine runtime rules:
  - On any quarantine trigger (FEED_LAG_QUARANTINE, L1_MISMATCH, BOOK_GAMEY, REPEATED_SHOCKS), set cooldown_until_ts = now_ms + COOLDOWN_SEC.
  - While now_ms < cooldown_until_ts: route to live_Cold (depth@1000ms) and block NEW entries (reason COOLDOWN_ACTIVE); exits/reductions remain allowed.
  - Clear cooldown automatically when now_ms ≥ cooldown_until_ts.
  - If multiple quarantine triggers fire, set cooldown_until_ts = max(cooldown_until_ts, now_ms + COOLDOWN_SEC). Emit one primary reason per priority order; secondary reasons optional for diagnostics.
- Config: THRESH_REFRESH_SEC=10; DEPTH_STALE_MS=1500; MIN_N_FOR_PERCENTILES=10; RING_WINDOW_SEC=10; RECOVERY_CONSEC=5; DEPTH_LEVELS_N=20; DEPTH_SPEED 100/1000ms; ENABLE_NEAR_TOUCH=true; K_TICKS=5; ENABLE_SLIP_CAP=true; ENABLE_HOLLOW_TOUCH_BLOCK=false; SHOCK params DEPTH_RATIO_SHOCK=0.25, DEPTH_RATIO_RECOVER=0.80; ENABLE_SPREAD_CONFIRM=false; COST_BUDGET_BPS=25; LOG_COST_ON_INSUFF_DEPTH=false; RECOVERY_CONSEC_GAMEY=8; DEPTH_RATIO_RECOVER_GAMEY=0.85.
  - ENABLE_SLIP_CAP default policy:
    - For small-cap universe, recommend ENABLE_SLIP_CAP=true with size-reduction loop before blocking; for majors, it may remain false if MIN_DEPTH_QUOTE + feasibility + cost budget suffice.
  - Deployment note:
    - For a small-cap universe, set stream_eligibility.ws_depth.ENABLE_SLIP_CAP=true in runtime config (baseline line may show false as a generic default).
  - RiskManager sizing key references (single source of truth):
    - Q_MIN_ENTRY, Q_MAX_ENTRY, Q_DEPTH_FRAC live in RiskManager config; Stream Eligibility consumes them for Q_entry_eff and slip-cap sizing; do not redefine values here.
- Derived: L1 from depth; mid/spread; min_depth_quote(N); near_depth_quote/near_ratio; slip_bps; depth_ratio (median over ring).
- Valid set: now_ms-last_depth_ts <= DEPTH_STALE_MS; bids/asks present; ask1>bid1>0; finite.
- Thresholds: MIN_DEPTH_QUOTE=P40; optional NEAR_RATIO_FLOOR=P20; optional SLIP_CAP_BPS=P90; warmup reuse last-good if N_valid low.
- Ring baseline: min_depth_med median over W; depth_ratio = min_depth_quote(N)/max(min_depth_med, EPS).
- Liquidity state: SHOCK if invalid sample or depth_ratio<DEPTH_RATIO_SHOCK or spread confirm; recovery depth_ratio>=DEPTH_RATIO_RECOVER for RECOVERY_CONSEC (plus spread if enabled); SHOCK blocks entries, exits allowed.
- Entry gating: PROMOTE_TO_DEPTH, VALID, not SHOCK, min_depth_quote>=MIN_DEPTH_QUOTE, near_ratio/SLIP caps if enabled, require not INSUFFICIENT_VISIBLE_DEPTH (impact check default ON).
- Gate evaluation priority (to avoid duplicate reasons):
  - If INSUFFICIENT_VISIBLE_DEPTH is true for the planned size, block with INSUFFICIENT_VISIBLE_DEPTH and skip cost_bps_entry evaluation for that pass (you may still log cost_bps_entry for telemetry if desired).
  - Otherwise compute slip_bps and cost_bps_entry; if cost_bps_entry > COST_BUDGET_BPS, block with COST_TOO_HIGH (you may still log cost_bps_entry as telemetry even when skipped by priority).
  - Optional cost telemetry on insufficient depth (off by default):
    - If stream_eligibility.ws_depth.LOG_COST_ON_INSUFF_DEPTH=true, still compute/log cost_bps_entry as telemetry when blocking on INSUFFICIENT_VISIBLE_DEPTH; decision priority unchanged.
    - Default: LOG_COST_ON_INSUFF_DEPTH=false (telemetry-only; enable for diagnostics).
- Exit: maker preferred if healthy; in SHOCK flatten/reduce within caps.
- Reason codes: DEPTH_STALE, DEPTH_EMPTY, BAD_L1, WARMUP_DEPTH_THRESHOLDS, MIN_DEPTH_FAIL, SHOCK_LOCK, INSUFFICIENT_VISIBLE_DEPTH, HOLLOW_TOUCH, SLIPPAGE_CAP, NONFINITE_SLIP, COOLDOWN_ACTIVE, COST_TOO_HIGH, BOOK_GAMEY, L1_MISMATCH, FEED_LAG_QUARANTINE, REPEATED_SHOCKS, ORDER_SIZE_INVALID, NONFINITE_SLIP_QUARANTINE.
- Demotion: PROMOTE_TO_DEPTH=false if persistent invalid/stale/SHOCK/fail gating for DEMOTE_CONSEC_FAILS; unsubscribe/downgrade optional.
- Visibility: logger eligibility.ws_depth; emit {ws_depth_state, thresholds_version_ts, N_valid, N_tradable_now, max_depth_age_ms, shock_count}; severities OK/WARMUP_DEPTH_THRESHOLDS/STALE_FEED with STALE_ERROR_GRACE_MS.
- Additional hybrid robustness (small-cap aware, non-duplicative):
  - L1_MISMATCH: mismatch_bps = max(|bid_depth - bid_book|, |ask_depth - ask_book|)/max(mid,EPS)*10_000; trigger if > L1_MISMATCH_BPS for MISMATCH_CONSEC (defaults 2 bps, 3). Block/quarantine; demote to cold.
    - Action timing: only demote/quarantine after MISMATCH_CONSEC consecutive mismatches (no action on the first isolated mismatch).
  - FEED_LAG_QUARANTINE: track stale_count in window W_stale_sec=30s; trigger if stale_count >= STALE_HITS_QUARANTINE=5; demote to cold for COOLDOWN_SEC=60.
  - FEED_LAG_QUARANTINE clearing: clear quarantine automatically when COOLDOWN_SEC elapses (cooldown_until_ts reached).
  - COST_BUDGET: cost_bps_entry = spread_bps + max(slip_bps_buy/sell(Q_entry)) + fee_bps_worstcase (config, taker worst-case unless maker guaranteed); if > COST_BUDGET_BPS block (COST_TOO_HIGH).
  - fee_bps_worstcase config key:
    - stream_eligibility.ws_depth.FEE_BPS_WORSTCASE (bps, worst-case entry+exit; default assumes taker+taker unless maker guaranteed by policy).
    - Fee worst-case default: must be non-zero; fail-safe assumption is taker+taker if maker fills are not guaranteed.
  - COST_BUDGET_BPS config:
    - risk_manager.COST_BUDGET_BPS (bps): max allowed cost proxy (spread + slip + fee worst-case) for entries (blocks with COST_TOO_HIGH).
    - Default: COST_BUDGET_BPS=25 (bps) as a conservative starting point; tune per venue/fees.
  - BOOK_GAMEY: churn_p95 over W_gamey_sec=30s and spread_jump_rate (spread jumps > SPREAD_JUMP_BPS=5 between updates); trigger if churn_p95 > CHURN_P95_CAP (adaptive P95 or config) AND spread_jump_rate > SPREAD_JUMP_RATE_CAP=0.20; block entries and tighten recovery (BOOK_GAMEY).
    - Recovery tightening: when BOOK_GAMEY true, increase recovery strictness: RECOVERY_CONSEC_eff = max(RECOVERY_CONSEC, RECOVERY_CONSEC_GAMEY); DEPTH_RATIO_RECOVER_eff = max(DEPTH_RATIO_RECOVER, DEPTH_RATIO_RECOVER_GAMEY). Defaults RECOVERY_CONSEC_GAMEY=8; DEPTH_RATIO_RECOVER_GAMEY=0.85 (configurable).
    - Config keys: stream_eligibility.ws_depth.RECOVERY_CONSEC_GAMEY and stream_eligibility.ws_depth.DEPTH_RATIO_RECOVER_GAMEY.
  - CHURN_P95_CAP source:
    - Adaptive mode: CHURN_P95_CAP = P95(churn) over VALID symbols at THRESH_REFRESH_SEC (store with thresholds_version_ts).
    - Otherwise CHURN_P95_CAP is a fixed config constant.
  - REPEATED_SHOCKS: shock_rate (shocks/min) over W_shock_min=5; replenish_time_ms_p50; trigger quarantine if shock_rate > SHOCK_RATE_CAP=3 or replenish_time_ms_p50 > REPLENISH_MS_CAP=20_000; cooldown = COOLDOWN_SEC.
  - REPEATED_SHOCKS windowing: W_shock_min applies to BOTH shock_rate and replenish_time_ms aggregations unless overridden.
  - ORDER_SIZE_INVALID: quantize qty to stepSize; enforce minNotional/filters; block if invalid after quantization.
  - Optional depth-derived micros (tightening only): weighted multi-level imbalance; near_ratio/slope/convexity (ENTRY_BLOCKED_HOLLOW_TOUCH); churn/instability (ENTRY_BLOCKED_MAKER_UNRELIABLE); resiliency; VPIN/flow toxicity (ENTRY_BLOCKED_VPIN). Use VALID samples; entry/size tightening only.
    - VPIN dependency note: requires trade/volume flow data; do not implement VPIN with depth-only inputs.
    - VPIN gating rule: disable ENTRY_BLOCKED_VPIN unless trades/aggTrades stream exists; do not emit VPIN-based blocks in partial-depth-only mode.
  - Hybrid robustness event log schema (transitions only):
    - Emit {event_type, symbol, ts_ms, primary_reason, secondary_reasons(optional), key_metrics} where key_metrics match the trigger: mismatch_bps (L1_MISMATCH); stale_count, W_stale_sec (FEED_LAG_QUARANTINE); churn_p95, spread_jump_rate (BOOK_GAMEY); shock_rate, replenish_time_ms (REPEATED_SHOCKS).
  - Optional repeated-cooldown escalation (routing-only):
    - Track cooldown_cycles over window W_escalate_min; if cooldown_cycles ≥ COOLDOWN_CYCLES_CAP, set exclusion_until_ts = now_ms + EXCLUSION_SEC (block new entries; route cold).
    - Defaults: W_escalate_min=10; COOLDOWN_CYCLES_CAP=3; EXCLUSION_SEC=300 (configurable).
  - Hybrid event logger:
    - Logger: eligibility.hybrid_events (transition-only, event_type-based).
- Visibility extras: emit top reason-code counts (e.g., top K=5 over window W_reason_sec=60) per level for operator insight.
  - Defaults: W_reason_sec=60; K=5; emit per-level (L1/L2/L3) counters, not a single global aggregation.
  - Reason counter schema: top_reasons = [{code:<REASON>, count:<INT>}] per level per refresh, alongside {level, state, thresholds_version_ts, N_valid, N_promoted/N_tradable, max_age_ms}.

- Per-symbol overrides (optional; bounded + slow):
  - General rule: allow per-symbol overrides for thresholds/caps but keep staleness clocks conservative (never auto-learn looser staleness; prefer stricter for small caps).
  - Eligible per-symbol params:
    - L2: SPREAD_CAP_BPS, SPREAD_EMERGENCY_CAP_BPS, TOP_QTY_FLOOR
    - L3: MIN_DEPTH_QUOTE, CHURN_P95_CAP (BOOK_GAMEY), RECOVERY_CONSEC_eff / DEPTH_RATIO_RECOVER_eff (BOOK_GAMEY tightening)
    - Staleness: TICKER_STALE_MS / BOOK_STALE_MS / DEPTH_STALE_MS only within tight bounds (e.g., ±50%) with a bias to stricter.
    - Absolute caps (in addition to ±50% bounds):
      - TICKER_STALE_MS ∈ [2000, 60000]; BOOK_STALE_MS ∈ [200, 5000]; DEPTH_STALE_MS ∈ [200, 5000]; prefer tighter for SMALLCAP_THIN; never auto-learn looser caps.
  - Slow, bounded adaptation:
    - Maintain per-symbol rolling distributions over long window W_sym_sec (e.g., 10-60 min) using VALID samples only.
    - Examples: SPREAD_CAP_BPS_sym = min(global_SPREAD_CAP_BPS, P80_sym(spread_bps)); MIN_DEPTH_QUOTE_sym = max(global_MIN_DEPTH_QUOTE, P40_sym(min_depth_quote(N))); CHURN_P95_CAP_sym = min(global_CHURN_P95_CAP, P95_sym(churn)).
    - Freeze per-symbol adaptive updates during feed stress (WARMUP/STALE_FEED); reuse last-good values.
  - Per-symbol override guardrails (explicit):
    - Update cadence: recompute per-symbol adaptives no faster than W_sym_refresh_sec (default 60s; configurable).
    - Bounds: staleness overrides within ±50% of globals; spread caps use min(global, sym), depth floors use max(global, sym), churn caps use min(global, sym).
    - Freeze per-symbol updates during any WARMUP_* or STALE_FEED state; reuse last-good values.

### Stream Eligibility Notes: Hybrid Roles, Stability Metrics, and Logging/ML
- Stream role separation (avoid duplication):
  - WS `<symbol>@ticker` (24h rolling stats) is for universe/health/routing (activity, dead markets, extreme-move exclusions).
  - WS `<symbol>@bookTicker` is for L1 tightness/stability gating (best bid/ask + sizes) and early shock warning.
  - WS partial depth is for liquidity/impact/shock gating (min_depth_quote, slip_bps(Q_entry), depth_ratio, churn).
  - Small-cap inclusion note:
    - REST-Eligibility (24h ticker cache) uses cross-sectional activity/range gates and may exclude many small caps if used as the primary universe.
    - WS Stream Eligibility can include small caps, but only those passing cross-sectional percentiles. To ensure representation, use either (a) class-segmented percentiles by liquidity tag (SMALLCAP_THIN vs NORMAL) or (b) a hot-slot quota for SMALLCAP_THIN (routing-only).
  - Small-cap routing (optional, routing-only):
    - stream_eligibility.routing.SMALLCAP_HOT_QUOTA (default 0): reserve at least this many live_Hot slots for SMALLCAP_THIN symbols if they meet minimum safety gates. If quota=0, small caps compete normally via ranking.
    - Note: Segmented percentiles by liquidity tag remain a future option; current implementation is quota-only to limit complexity.
- bookTicker stability metrics (spread_jitter / spread_bps_mad):
  - Window config: STAB_WINDOW_SEC (default 10), MIN_UPDATES_STAB (default 30).
  - For spreads S over the last STAB_WINDOW_SEC:
    - spread_bps_med = median(S)
    - spread_bps_mad = median(|spread_bps_i - spread_bps_med|)
    - spread_jitter = P90(|?spread_bps_i|) where ?spread_bps_i = spread_bps_i - spread_bps_{i-1}
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
- Config (stream_eligibility.ws_bookticker.stability.*, defaults):
  - STAB_WINDOW_SEC=10
  - MIN_UPDATES_STAB=30
  - ENABLE_STABILITY_BLOCK=false
  - Optional (if using jump-rate telemetry): SPREAD_JUMP_BPS=5
- Window population rule:
  - Include only VALID bookTicker samples (ask > bid > 0, finite values, now_ms - last_book_ts = BOOK_STALE_MS, updateId monotonic).
  - If count(window) < MIN_UPDATES_STAB: set stability_state=STAB_INSUFFICIENT_SAMPLES and treat metrics as telemetry-only (do not block).
- Computations (for S = {spread_bps_i} in the last STAB_WINDOW_SEC):
  - spread_bps_med = median(S)
  - spread_bps_mad = median(|spread_bps_i - spread_bps_med|)
  - Optional scaled MAD: spread_bps_mad_std ˜ 1.4826 * spread_bps_mad
  - spread_jitter = P90(|?spread_bps_i|) where ?spread_bps_i = spread_bps_i - spread_bps_{i-1}
  - updates_per_sec = count(S) / STAB_WINDOW_SEC
  - Optional spread_jump_rate = fraction of updates in S where |?spread_bps_i| > SPREAD_JUMP_BPS
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
  - Enable flag: stream_eligibility.toxicity.ENABLE=false (default).

### Audit appendix
- Unique Facts Inventory, Deduplication Map, [REVIEW-CONFLICT] retained as above (cadence vs optional immediate demotion at L2).
