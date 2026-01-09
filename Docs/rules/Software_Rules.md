Software Rules (System/Ops)
===========================

Architecture Boundaries
- Supervisor orchestrates scheduling; no hidden daemons.  
- binance_bot_core owns exchange I/O; aegis_core stays REST/WS-free.  
- Storage helpers own DB access (SQLite/DuckDB); no ad hoc connects.

Scheduling & Load
- Keep hot loops O(1) per tick; push heavy work into scheduled/background tasks.  
- Avoid overlapping gate concepts; one clear policy per optional task.  
- Respect cadence/guards/budgets to limit REST/DB load; add backoff on repeated failures.
- Design for low resource footprint (CPU/memory/network) while staying fully functional: prefer cheap guards first, short bursts for heavy work, and clear observability without chatty logs.

Secrets & Config
- Use env/.env/secrets files only; never hard-code secrets; fail fast/clear if required config is missing.  
- Keep config precedence documented; validate formats and ranges.

Alerts/Observability
- Use existing emit/log pipelines; add thresholded alerts only when necessary to avoid spam.  
- Logs must exclude secrets; include context (task, symbol, tf) and outcomes (skip/retry/error).  
- For scalp mode: log skips for stale data/health/micro caps; threshold notifications only for repeated REST failures/lock giveups/health degradation.

DB Usage
- SQLite/DuckDB accessed via helpers; prefer single-writer patterns and bounded retries on locks.  
- Respect retention/paths; tests must never write to production paths.  
- Follow folder roles from docs/logic: DuckDB via Storage helpers (duck_writer/reader/tf_persistor/history_manager); SQLite via control/execution helpers; no ad hoc connects.

Scalp Ops Guardrails
- Enforce health/latency gating before firing hot-path tasks; pause symbols under poor p95 or stale data.  
- Keep hot loops O(1); ensure mid-bar/close persistence remains gated (mode/cadence/guard/stale).  
- Kill switch/trading_enabled defaults to safe on startup; enable only after reconciliation/health checks.

Wiring/Pipeline
- Ensure components are wired/connected per architecture (I/O in binance_bot_core, core logic in aegis_core, storage via Storage helpers, execution via OrderEngine, control via control/ scripts).  
- If wiring gaps or missing connections are found, call them out explicitly in chat and/or docs; do not leave implicit.

Change Control
- No trading/risk/strategy changes unless explicitly in scope.  
- Summarize changes, impacts, and tests run; keep docs/tests in sync.
