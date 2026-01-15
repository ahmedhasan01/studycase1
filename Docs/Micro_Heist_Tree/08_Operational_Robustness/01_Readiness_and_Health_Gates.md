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
- Router eligibility policy determines whether entries are allowed at all (entry_policy=ALLOW/THROTTLE/BLOCK).
- See: `06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md` (frequency caps are tighten-only; readiness failure implies no new entries; exits/reductions allowed).

1.2 Rules (MUST/SHOULD/MAY)
- MUST block NEW entries when readiness/health fail (exit-only behavior is allowed).
- MUST treat readiness/health failure as "exit-only": manage risk, reduce exposure, or exit; do not add new exposure.
- MUST set Unknown-Mode when readiness is unclear; default to BLOCK for entries until clarity returns.
- SHOULD require a stability window before lifting blocks after a failure (avoid immediate flip-flop).
- MAY escalate strictness (longer stability window / tighter throttles) when repeated failures occur; invariants unchanged.

### Precedence Ladder (tighten-only)
Order of enforcement for NEW ENTRIES (highest priority first):
1) Readiness/Health FAIL  -> BLOCK entries (exit-only)
2) Router Eligibility says BLOCK -> BLOCK entries (exit-only)
3) Shock/Dislocation/Unknown-Mode -> BLOCK entries (exit-only)
4) Throttles / cooldowns (if any) -> reduce/delay entries
5) Max-trades / frequency caps -> tighten-only limiter (never forces entries)

1.3 Edge Cases / Conflicts
- Partial failures (some checks pass) -> default to BLOCK until all required checks pass.
- If any upstream rule yields entry_policy=BLOCK, then downstream frequency caps are irrelevant for entries (effective behavior becomes max_trades=0 for entries).
- "Pass" must be unambiguous: if measurement is noisy or ambiguous, treat as Unknown-Mode and remain blocked for entries.

1.4 Examples (minimal, conceptual)
- Data stale ? block entries; exit or reduce only until freshness recovers for a stable window.

1.5 Open Questions
- [INBOX-REVIEW] Exact metrics/time windows for declaring readiness OK.
