# Readiness and Health Gates

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Define readiness and health gates that must pass before entries in live micro trading.

1.1 Inputs / Dependencies
- Data quality, confirmation availability, edge-positive status, bias/regime clarity.

1.2 Rules (MUST/SHOULD/MAY)
- MUST block entries when readiness/health fail; exits allowed.
- MUST Unknown-Mode when readiness unclear; stay blocked/throttled until resolved.
- SHOULD require stability window before lifting blocks after a failure.
- MAY escalate strictness when repeated failures occur; invariants unchanged.

1.3 Edge Cases / Conflicts
- Partial failures (some checks pass) -> default to block until all required checks pass.

1.4 Examples (minimal, conceptual)
- Data stale ? block entries; exit or reduce only until freshness recovers for a stable window.

1.5 Open Questions
- [INBOX-REVIEW] Exact metrics/time windows for declaring readiness OK.
