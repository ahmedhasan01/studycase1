Heavy Tasks Rules
=================

Scope & Scheduling
- Identify heavy operations (e.g., purge/vacuum, large backfills, reconciliations) and schedule them; never place them in hot loops.
- Use a single clear gating policy for optional heavy work; avoid overlapping freeze/maintenance concepts.

Load Control
- Apply cadence/limits (e.g., max items per run) and bounded retries/backoff on recoverable errors; add cooldowns on repeated failures.
- Respect rate limits for REST-heavy tasks; defer rather than spam when hitting limits.

Safety
- Do not block WS/strategy hot paths; run heavy work asynchronously or at low frequency.
- Log outcomes (counts, skips, retries, errors) with context; avoid log spam via thresholds or aggregation.

Data Integrity
- Use helper functions for DB access; respect single-writer guidance where applicable; handle locks with retry/backoff.
- Ensure retention/cleanup tasks are well-defined and do not remove needed data without safeguards.
