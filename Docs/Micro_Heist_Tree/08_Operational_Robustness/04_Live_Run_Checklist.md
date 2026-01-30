# Live Run Checklist

## Mini-Index
- 1.0 Purpose
- 1.1 Checklist
- 1.2 Open Questions

1.0 Purpose
- Provide a minimal pre/during/post run checklist for micro trading.

1.1 Checklist
- Verify health/readiness gates OK; no Unknown-Mode.
- Confirm bias/regime set; edge-positive criteria defined; [INBOX-REVIEW] if missing.
- Confirm confirmations configured and using closed bars only.
- Validate risk bounds and cooldowns active; exits always permitted.
- Ensure Adaptive Parameters Policy settings are at intended levels; default to stricter if uncertain.
- During run: monitor edge, health, and confirmations; block entries on degradation; exits allowed.
- Post run: review failures, Unknown-Mode occurrences, and adherence to reduce-first doctrine.

1.2 Open Questions
- [INBOX-REVIEW] Additional run-time checks specific to deployment environment (venue-agnostic).
