Storage Rules (SQLite + DuckDB)
===============================

Access & Boundaries
- Access SQLite/DuckDB only via storage helpers; no ad hoc connections.  
- Strategies/core remain read-only consumers; no ring_buffer writes from storage layer.

Integrity & Concurrency
- Enforce PK/constraints to prevent duplicates; avoid last-write-wins surprises.  
- Handle locks with bounded retries/backoff; prefer single-writer patterns for hot tables.

Paths & Retention
- Honor configured DB paths; never write to production paths in tests (use temp/overrides).  
- Apply retention policies through scheduled tasks; avoid manual purges without safeguards.

Reads/Writes
- Separate read-only from write paths; use read_only connects where possible.  
- Align timestamps/timeframes; write closed bars only unless explicitly designed otherwise.

Testing
- Tests must use temporary DB files and clean up; no reliance on default production paths.  
- Validate schema assumptions in tests when schema changes.
