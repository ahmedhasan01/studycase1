Health Logic
============

Components
- health/system_load.py: computes system load/score from OS metrics (docs: HEALTH.md, health/FOLDER_DOC.md).
- health/health_db.py: stores/reads system_health and symbol_health snapshots.
- Monitor/latency_guard.py: tracks decision/REST latency metrics.
- health/canary.py: canary checks (if used; docs: health/README.md).
- interval_guard.py (health/README.md): should_run/mark_ran helpers (optionally persistent).

Usage
- Supervisor reads health to gate tasks; health DB populated by scheduled checks.  
- No direct budget/cooldown integration for mid-bar; health primarily observes load/latency.
- Docs references: docs/HEALTH.md, health/FOLDER_DOC.md, health/README.md.

Observability
- Health snapshots written to SQLite; logs/metrics used to gate or pause operations via HealthManager logic (outside strategies).

Limits
- No built-in per-task budgets/cooldowns for mid-bar; would require explicit integration.
