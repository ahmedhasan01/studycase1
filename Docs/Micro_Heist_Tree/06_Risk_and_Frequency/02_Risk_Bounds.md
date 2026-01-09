# Risk Bounds

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Outline risk limits that constrain trading within the micro horizon.

1.1 Inputs / Dependencies
- Risk appetite; session/daily limits; edge-positive; health/readiness.

1.2 Rules (MUST/SHOULD/MAY)
- MUST enforce hard risk caps (per-trade, per-session) before allowing entries; exits always allowed.
- SHOULD include cool-down/no-trade triggers after breaches; entries blocked until recovery.
- MAY refine bounds per regime via Adaptive Parameters Policy, but caps themselves remain invariant.

1.3 Edge Cases / Conflicts
- Edge-positive but bound breached ? no entry; reduce/exit only.

1.4 Examples (minimal, conceptual)
- Daily loss limit hit ? stand down for entries; manage exits.

1.5 Open Questions
- [INBOX-REVIEW] Specific numeric caps to set for sessions and trades.
