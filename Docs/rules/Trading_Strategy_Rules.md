Trading Strategy Rules
======================

Scope
- Strategy, signals, and risk/execution invariants only. No REST/WS inside strategies.

Data & Purity
- Strategies/signals consume only provided data (ring buffers, persisted bars, configs); no direct network, DB, or file I/O.
- Use closed bars only; no look-ahead on forming bars. Respect timeframe alignment.
- Honor per-symbol params/stats provided by higher layers; do not bypass caps.

State & Modes
- Obey BOT_MODE (PAPER/LIVE) and symbol state machine (LIVE_HOT/LIVE_COLD/SLEEP/etc.). No trading when state/mode blocks it.
- One position per symbol invariant remains enforced by execution/risk; strategies never open net-new paths.

Risk & Execution Path
- All orders flow through RiskManager + OrderEngine; no direct client calls from strategies.
- Respect risk fractions, slippage/fee caps, microstructure gates, cooldowns, and kill switches as provided by config/risk layers.
- No new order types or sizing paths without explicit scope and risk validation.

Outputs
- Strategies emit decisions only (direction/strength/intent) with no side effects. Execution and sizing are outside strategy code.

Scalp Trading Guardrails
- Target horizons: seconds to ~20 minutes; favor closed-bar signals and microstructure-aware gates.
- Tight caps: respect spread/slippage/fee caps and min_notional/step checks before entries; prefer LIMIT unless microstructure/latency is excellent.
- Cooldowns/stops: honor per-symbol cooldowns after losses/streak/drawdown; no rapid re-entry until risk layers clear it.
- Data freshness: block/skip if data lag, health, or microstructure is stale/unhealthy; no look-ahead on forming bars.
Testing & Changes
- Any strategy change requires tests (unit/backtest/offline) and doc updates for the strategy pipeline; keep PAPER/LIVE parity in behavior.
