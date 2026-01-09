Heavy Tasks Logic
=================

What counts as heavy
- DuckDB maintenance: purge_old, vacuum (Storage/duck_writer.py), scheduled via supervisor task_purge.
- Candle persistence: tf_persistor persist_latest_closed_bars (REST) can be heavy on large symbol sets; mid-bar/close paths are gated.
- Coverage/backfill: ensure_history/backfill_rest (tf_persistor/history_manager) for gaps or promotions.
- WS ingest gap repair: history_manager.process_ws_kline triggers REST fetch on detected gaps.
- heavy_tasks queue (aegis_core/heavy_tasks.py): defines heavy task schema; consumption depends on supervisor/watchdog.

Scheduling
- supervisor task_purge (daily) runs purge/vacuum.  
- heavy_watchdog in supervisor polls heavy_tasks queue periodically (if used).  
- Mid-bar/close persistence run on cadence/guards; WS ingest runs continuously.

Load controls
- Bounded retries/backoff for DuckDB locks in tf_persistor writes.  
- Rate orchestrator used by historical data client for REST pacing.  
- No unified budget/cooldown per heavy task; gating is per-task (cadence/guards/retention).

Docs references
- storage.md, FLOW.md (retention/purge), runtime_and_supervisor.md (scheduling), control/FOLDER_DOC.md (watchdog mention).
