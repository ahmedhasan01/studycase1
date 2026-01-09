Storage Logic (SQLite + DuckDB)
===============================

DuckDB (candles)
- Files: Storage/duck_writer.py (ensure_tables, append_bars INSERT OR REPLACE PK(symbol, open_ms), purge_old, vacuum), Storage/duck_reader.py (last_bars), Storage/tf_persistor.py (persist_latest_closed_bars, get_coverage, backfill_rest, mid-bar/close persistence), history_manager (WS ingest and gap repair).
- Purpose: store closed candles for TFs (1m+). Writes via REST fetch (tf_persistor) or WS ingestion (history_manager). Ring buffer is in memory, not DuckDB.
- Docs: storage.md, FLOW.md (retention defaults and purge schedule), runtime_and_supervisor.md (scheduler), Storage/FOLDER_DOC.md, Storage/README.md (writer policy, retention).

SQLite (aegis.db)
- Control plane: control_commands, notifications, run_status, orders/positions/trade_journal, symbol metadata (aegis_state, symbol_params/stats), health snapshots, etc. Accessed via dedicated helpers/modules (not strategies).

Access Patterns
- DuckDB writes: tf_persistor persist_latest_closed_bars (REST) and history_manager (WS) → duck_writer.append_bars with PK replace and lock retry.
- DuckDB reads: duck_reader/history_manager for indicators/coverage; tf_persistor get_coverage for staleness gate.
- SQLite reads/writes: control/command_processor, telegram bots/monitor, execution/order_engine, risk manager, health modules.

Retention
- DuckDB retention via purge_old (called by supervisor task_purge); configs in Storage/config.py; docs note defaults per TF and PURGE_UTC (storage.md, FLOW.md). SQLite retention not automated (operational policy).

Paths
- DuckDB path from Storage/config.py (env override); SQLite path via DB helper/AEGIS_DB_PATH/env. Tests should override paths to temp files.
