# Entry Hygiene

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Define pre-entry hygiene checks for micro trades.

1.1 Inputs / Dependencies
- Confirmations, edge-positive status, health/readiness, bias/regime alignment.

1.2 Rules (MUST/SHOULD/MAY)
- MUST verify confirmations (persistence + confirming candle) and micro hygiene before any entry.
- MUST ensure edge-positive; if unclear -> no entry.
- MUST respect robustness gates and cooldowns; entries blocked if not ready.
- SHOULD align with Winning Bias and regime eligibility.

1.3 Edge Cases / Conflicts
- Conflicting checks: robustness veto wins; else Unknown-Mode.

1.4 Examples (minimal, conceptual)
- Entry only after spread/quality within bounds and confirmations satisfied.

1.5 Open Questions
- [INBOX-REVIEW] Exact hygiene metrics to enforce.
