Coding Rules
============

Style & Structure
- Favor clear naming, small functions, and reuse of existing helpers/utilities.  
- Avoid duplication; keep logic DRY and localized.

Error Handling
- Catch only where recovery is possible; log context; avoid silent failures.  
- Use bounded retries/backoff where safe; otherwise fail fast and clearly.

Dependencies
- Keep dependencies minimal and justified; prefer built-in or existing repo utilities.  
- Do not reimplement helpers that already exist (DB paths, credentials, rate limiting, logging).

Performance
- Short-circuit cheap gates before heavy work (I/O, DB, network).  
- Keep hot paths O(1); avoid unnecessary allocations and blocking calls in hot loops.

Docs & Tests
- Update relevant docs and tests when behavior changes; maintain single source-of-truth docs per subsystem.  
- No secrets in code or logs; use placeholders in examples.

Artifacts
- Do not commit or rely on pycache artifacts; clean them as needed. Global disabling should only be done if confirmed safe for the tooling.
