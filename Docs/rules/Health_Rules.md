Health Rules
============

Ownership & Scope
- HealthManager/health_db own health state; other modules read but do not override health arbitrarily.
- Use existing load/latency metrics; avoid duplicating health checks.

Budgets & Throttles
- Integrate new budgets/cooldowns with existing health/rate-orchestrator patterns where feasible; avoid ad hoc throttles sprinkled across code.
- Apply bounded retries/backoff for recoverable health-related errors; fail fast otherwise.

Monitoring
- Emit clear health-related logs/metrics; avoid flooding.  
- Treat repeated health degradations as high-signal; consider thresholded alerts via existing notification mechanisms.

Separation
- Health gating should not silently alter trading logic beyond defined policies; keep actions explicit and logged.
