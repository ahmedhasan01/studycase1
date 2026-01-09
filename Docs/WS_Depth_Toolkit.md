# Stream Eligibility → WS Depth : Top-of-Book Depth (L1-first), Eligibility + Optional Microstructure Metrics

## 0) L1 FIRST (Top-of-Book Level-1)
- Definition (L1): best bid/ask price and size at the touch: bid1_price, bid1_qty, ask1_price, ask1_qty.
- Sources: bookTicker provides L1 directly; depth also contains L1 as bids[0]/asks[0].
- Uses before/alongside depth:
  - Tightness now: spread from L1 prices (bookTicker preferred).
  - L1 notional proxy: bid1_price*bid1_qty, ask1_price*ask1_qty (cheap pre-screen/tie-break; not full impact protection).
  - Optional micro hints: L1 imbalance, microprice.
  - Shock pre-signal: spread blowout or L1 size collapse can block promotion even before deeper depth confirms.
- Rationale: execution cost/impact = spread + available depth; L1 is fastest/cheapest; depth is authoritative for impact.

## 1) What Depth Is (Function)
- Depth = order book ladder (multiple price levels per side) to estimate liquidity/impact (walk the book).

## 2) Binance Depth Data Sources (Spot)
- WS Partial Book Depth: `<symbol>@depth<levels>` or `<symbol>@depth<levels>@100ms`, levels ∈ {5,10,20}, speed 1000ms/100ms; includes lastUpdateId, bids[[p,q]], asks[[p,q]]. Use for top-of-book analytics, impact proxies, shock detection.
- WS Diff Depth: `<symbol>@depth` or `<symbol>@depth@100ms`; includes U/u and bid/ask deltas. Use for local book (requires buffer + REST snapshot + sequence checks per Binance docs).
- REST depth snapshot: GET /api/v3/depth (limit up to 5000) for sync or one-off checks.
- WS API “depth” RPC: method "depth" with symbol/limit (max 5000).

## 3) Choosing Partial vs Diff Depth
- Partial: fast scalping eligibility/impact proxies from top 5/10/20; no full reconstruction needed.
- Diff + snapshot sync: higher fidelity/deeper-than-20; requires exact sequence/sync per Binance procedure.

## 4) Depth Levels and Update Speed (Adaptive Guidance)
- Default: levels=20, speed=100ms when symbol is actively tradable.
- Adaptive speed: use @100ms when promoted/active; @1000ms (or pause) when only observing.
- Adaptive levels: choose smallest N ∈ {5,10,20} that covers typical notional; if N=20 insufficient, treat as thin or move to diff depth.

## 5) Inputs and Invariants
- depth payload: bids/asks arrays [[p,q],...], best prices at index 0 in partial depth.
- price/qty are strings; parse to numeric.

## 6) Derived Metrics from Depth (EPS=1e-12, tickSize from filters)
- 6.1 L1 (from depth[0] or bookTicker): mid, spread_bps, L1_notional_bid/ask, imb_L1, microprice, microedge_bps.
- 6.2 Top-N quote-notional: depth_quote_bid(N), depth_quote_ask(N), min_depth_quote(N).
- 6.3 Within K ticks of mid: depth_within_K_ticks using tickSize.
- 6.4 Walk-the-book impact: VWAP_buy/sell(Q), slip_bps_buy/sell(Q) for target quote-notional Q.
- 6.5 Depth shape “tight but hollow”: near_depth vs total_depth, near_ratio = near_depth/total_depth.
- 6.6 Multi-level imbalance (optional, spoofable): imb_depth over N levels.
- 6.7 Resilience/stability (rolling W sec): min_depth_med, depth_ratio = min_depth_quote(N)/max(min_depth_med,EPS); depth_update_rate; depth_churn.

## 7) Level-3 Eligibility Gate (Depth Authoritative)
- Valid sample: now_ms - last_depth_ts ≤ DEPTH_STALE_MS; depth arrays present both sides; L1 sanity (ask1 > bid1 > 0). Only VALID symbols used for percentiles.
- Adaptive threshold: MIN_DEPTH_QUOTE = percentile(min_depth_quote(N), p=0.40) over VALID.
- TRADABLE_NOW (entry gate): VALID, not in SHOCK, min_depth_quote(N) ≥ MIN_DEPTH_QUOTE; optionally slip_bps_buy(Q_entry) ≤ SLIP_CAP_BPS if defined.

## 8) Liquidity Shock Override + Recovery
- liq_state ∈ {HEALTHY, THIN, SHOCK}.
- SHOCK triggers: depth_ratio < 0.25 or L1 spread blowout confirmation or depth/book staleness.
- Recovery: require spread normalized (below recovery percentile) AND depth_ratio ≥ 0.80 for RECOVERY_CONSEC consecutive evaluations.

## 9) Using Depth for Entries vs Exits
- Entries: depth gate protects against impact; THIN/SHOCK blocks new entries.
- Exits: depth informs urgency/method; HEALTHY → maker-friendly exits; SHOCK → prioritize flattening.

## 10) Historical Depth via Ring Buffer (Accuracy Notes)
- Ring buffer good for short-horizon stability baselines (10–60s), shock detection, micro health.
- Not full-history accurate: partial depth misses deeper levels and intra-interval changes; for higher fidelity use diff depth with correct snapshot/sequence sync.

## 11) Operational Notes (Accuracy/Limitations)
- Visible depth can be spoofed; treat depth signals as risk controls, not standalone alpha.
- Diff depth requires strict sequence correctness; resync from snapshot on breaks.
- Numeric safety: use EPS, handle empty books, guard against non-finite.
- Precision compliance: tickSize/stepSize from exchangeInfo for tick-band depth and sizing/rounding.

## 13) Optional Extensions (Risk Controls Only; Not Standalone Alpha)
- These are OPTIONAL add-ons.
- Must not override core VALID rules.
- Use them to tighten entry permission / shock detection / recovery only.

### 13.1 OFI (Order Flow Imbalance) as toxicity warning (risk control)
- Lightweight L1 OFI proxy using best bid/ask size/price changes across updates.
- Track persistence over ring window W:
  - ofi_sum_W, ofi_zscore_W (optional), ofi_sign_persist_W.
- Policy:
  - If OFI is one-sided persistent AND min_depth_quote(N) is falling (depth_ratio declining) → tighten entry gating:
    - either raise MIN_DEPTH_QUOTE (multiplier) OR
    - force THIN/SHOCK sooner (configurable).
- Optional reason code: ENTRY_BLOCKED_TOXIC_FLOW (use only if consistent with existing reason style).

### 13.2 Impact slope proxy (Kyle-style lambda) as “thinness” indicator (risk control)
- Impact proxy over short window:
  - lambda_hat = abs(Δmid_bps) / max(abs(ΔOFI), EPS)
  - or lambda_hat = abs(Δmid_bps) / max(Δsigned_flow, EPS) if signed_flow exists.
- Policy:
  - If lambda_hat spikes above a rolling percentile (e.g., P90 over W) → treat as THIN or SHOCK amplifier.
- Optional config: LAMBDA_SPIKE_PCTL (e.g., 0.90).

### 13.3 Depth shape / slope / convexity (avoid “deep far, hollow near”)
- Optional features (from existing depth bands/top-N):
  - near_depth_quote (from 6.2)
  - near_ratio = near_depth_quote / max(min_depth_quote(N), EPS) (from 6.4)
  - slope proxy: near_depth_quote / max(K, 1) (quote per tick-band)
  - convexity proxy (optional): compare depth in band K1 vs K2 (K2 > K1).
- Policy:
  - If near_ratio < NEAR_RATIO_FLOOR OR slope collapses → block entries (HOLLOW_TOUCH).
- Optional reason code: ENTRY_BLOCKED_HOLLOW_TOUCH (if not already present).

### 13.4 Maker feasibility / queue-risk proxy (fill reliability)
- We do NOT know queue position; proxy only.
- Optional churn metrics:
  - l1_churn_rate_W: count of L1 size/price changes per second (or per update) over W
  - top_size_drop_rate_W: frequency of top_qty_min dropping sharply.
- Policy:
  - If churn is high → maker fills unreliable:
    - tighten entry: require stronger depth/spread OR
    - prefer smaller Q_entry / reduce size / require longer recovery.
- Optional reason code: ENTRY_BLOCKED_MAKER_UNRELIABLE (optional).

### 13.5 Resiliency (replenishment time after depletion)
- Define:
  - When depth_ratio drops below DEPLETION_RATIO (e.g., 0.50), start timer.
  - replenish_time_ms = time until depth_ratio ≥ 0.80 (or recovery threshold).
- Policy:
  - Symbols with slow replenishment:
    - require higher RECOVERY_CONSEC, or
    - keep THIN longer (cooldown), or
    - reduce allowed Q_entry.
- Optional configs: DEPLETION_RATIO (e.g., 0.50); REPLENISH_MAX_MS (optional cap for “slow” classification).

### 13.6 VPIN / toxicity bucket (ONLY if trades/prints are available)
- Only compute if you have trade stream data; do not infer from candles.
- Policy:
  - Use as risk-off amplifier (tighten gates / trigger SHOCK), never as standalone entry signal.
- Optional reason code: ENTRY_BLOCKED_VPIN (optional).

### 13.7 Size scaling / liquidity class (Q_entry adaptation)
- Define: Q_entry_eff = min(Q_entry_user, Q_ENTRY_FRAC * min_depth_quote(N)).
- Policy:
  - Prevents unrealistic slippage tests on thin symbols.
- Config: Q_ENTRY_FRAC (e.g., 0.02–0.10 depending on aggressiveness).
