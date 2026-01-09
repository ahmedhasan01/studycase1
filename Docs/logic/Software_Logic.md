Software Logic (System/Ops Summary)
===================================

Process Ownership
- scripts/supervisor.py: main orchestrator; schedules tasks (WS ingest, persistence, purge, heavy_tasks watchdog, wallet/health snapshots, mid-bar/close persistence).
- binance_bot_core: exchange I/O (REST/WS), credentials loader, rate orchestrator, historical data client, logging utilities, DB path helper.
- aegis_core: state machine, promotion/demotion, signals router, history_manager (bars/ring buffers), validators; remains REST/WS-free.

Data Stores
- SQLite (aegis.db): control plane (commands, notifications, run_status, orders/positions/trade_journal, symbol/state metadata). Accessed via DB helpers, not directly by strategies.
- DuckDB (bars.duckdb): candle history (1m+ TFs) written via Storage/duck_writer; read via duck_reader/history_manager.

Scheduling & Tasks
- WS ingest: history_manager.process_ws_kline writes closed bars, updates ring buffers, repairs gaps via REST as needed.
- Persistence: tf_persistor.maybe_persist_at_close (1s tick) and maybe_persist_midbar (cadence/guard/stale-gated) write CLOSED bars via REST → DuckDB.
- Maintenance: purge_old/vacuum via supervisor task_purge; heavy_tasks watchdog monitors queued heavy work (if used).

Control/Notifications
- control_commands + command_processor: enqueue/consume admin actions.
- notifications + telegram_monitor: outbound alerts; admin bot enqueues commands/queries via DB.

Scalp-mode operational notes
- Health/latency gating should run before executing hot-path tasks; stale data or degraded health should pause symbols and skip scalps.  
- Persistence remains CLOSED-only; mid-bar/close paths gated by mode/cadence/guard/stale (no quiet hours).  
- Kill switch/trading_enabled safe defaults at startup; LIVE enable after reconciliation/health checks; PAPER mirrors logic without live orders.

Config Sources
- aegis_config modules (timeframes, signals, risk, runtime, etc.) — see docs/aegis_config.md and aegis_config/FOLDER_DOC.md.
- Env/secrets for credentials, tokens, DB paths (loaded via binance_bot_core.credentials); see binance_bot_core/README.md, binance_bot_core/FOLDER_DOC.md for client/credential details.

Docs references
- runtime & wiring: docs/runtime_and_supervisor.md, docs/WIRING_SYSTEM.md, docs/WIRING_CHECKLIST.md.
- Exchange I/O layer: binance_bot_core/README.md, binance_bot_core/FOLDER_DOC.md.
- Quotes/tradable: Quotes/FOLDER_DOC.md (tradable_monitor, universe/ranking).
- Registry: Registry/README.md (in-process state cache, summaries).
- Storage: Storage/FOLDER_DOC.md and README.md (DuckDB retention/purge/backfill).
- Execution: execution/FOLDER_DOC.md (OrderEngine, clients, journaling).
