Testing Rules
=============

Scopes & Markers
- Default runs are offline/unit only; no network by default.  
- Mark online/integration tests explicitly and keep them opt-in.  
- Smoke/e2e tests are opt-in; place e2e under tests/e2e/ and avoid long waits.

Isolation
- Use temporary files/DBs; avoid writing to production paths.  
- Fixtures must clean up; no shared global state across tests.

Regression
- Add/adjust tests for every behavior change or bug fix.  
- Cover critical guards (mode gates, retries, error paths).

Determinism
- Use deterministic seeds/data where feasible; avoid time/source of randomness in core assertions.

Docs
- Document how to run offline vs online suites; list required env vars for online tests (placeholders only).

Location & exceptions
- Tests live under `tests/` (unit/integration/safety/online/e2e/smoke).  
- If a test must exist outside `tests/`, obtain approval and document the pipeline/linkage from that folder.
