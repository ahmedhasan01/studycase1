Trading Strategy Logic (Summary)
================================

Purpose
- Strategies produce entry/exit decisions from market data without performing I/O or placing orders directly. RiskManager + OrderEngine handle sizing, gating, and order placement.

Key Components (aegis_core + Adaptive)
- signals.py + strategy_router.py: build SignalContext from ring buffers/persisted bars, route to strategies (mean-reversion/momentum/range, etc.), emit EntryExitDecision only (docs: STRATEGY_PIPELINE.md, STRATEGIES_AND_REGIMES.md).
- strategies/*: pure decision functions; no REST/WS/DB writes; regimes influence which strategy is active (docs: STRATEGIES_AND_REGIMES.md).
- symbol_params.py / symbol_stats.py: provide per-symbol overrides and performance stats consumed by signals (docs: risk_and_execution.md).
- aegis_state.py / aegis_promotion.py: symbol lifecycle (LIVE_HOT/COLD/etc.), states read by signals/risk but maintained elsewhere (docs: AEGIS_OVERVIEW_V1.md, aegis_core/FOLDER_DOC.md).
- Adaptive/README.md: regime/stress concepts referenced in STRATEGIES_AND_REGIMES.md (if used).

Data Flow
- Inputs: ring buffer bars (WS ingestion), DuckDB history via history_manager, per-symbol params/stats, configs under aegis_config (docs: aegis_config.md, runtime_and_supervisor.md).
- Outputs: EntryExitDecision (side/strength/strategy id) → RiskManager → OrderEngine.
- No direct order placement, sizing, or risk checks inside strategies.

Constraints
- Closed bars only; no forming-bar look-ahead.
- REST/WS-free inside strategies; all external I/O lives in binance_bot_core or storage layers.
- One position per symbol enforced downstream; strategies do not bypass execution/risk.
- Scalp emphasis: short horizons (seconds to ~20 minutes) rely on fresh data/microstructure; expect tight spread/slippage caps and cooldowns enforced downstream.
