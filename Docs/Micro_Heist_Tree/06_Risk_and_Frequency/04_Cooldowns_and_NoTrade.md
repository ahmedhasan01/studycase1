# Cooldowns and No-Trade

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Define when trading must pause or throttle after events or limits.

1.1 Inputs / Dependencies
- Risk bounds, robustness/health signals, regime shifts, bias flips, confirmation failures.

1.2 Rules (MUST/SHOULD/MAY)
- MUST trigger cooldown/no-trade after risk breaches, repeated failures, or health degradation; entries blocked; exits allowed.
- SHOULD include per-setup and per-session cooldowns governed by Adaptive Parameters Policy (tighten by default).
- MAY allow gradual re-entry after stability window; requires confirmations and readiness.

1.3 Edge Cases / Conflicts
- Conflicting cooldown sources ? use longest/strictest.

1.4 Examples (minimal, conceptual)
- After consecutive failed confirmations, enforce a short cooldown before next attempt.

1.5 Open Questions
- [INBOX-REVIEW] Duration and criteria for lifting cooldowns.
