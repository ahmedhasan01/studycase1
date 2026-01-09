# Failure Modes and Emergency Actions

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Define how the strategy responds to failures and emergencies so live trading remains safe and deterministic.

1.1 Inputs / Dependencies
- Health/readiness monitors (data quality, execution feedback, confirmation availability).
- Edge-positive status and bias state.
- Unknown-Mode indicator for unclear regimes or conflicts.

1.2 Rules (MUST/SHOULD/MAY)
- MUST If readiness/quality/health degrades: block new entries; exits/reductions allowed (robustness override).
- MUST Reduce/Exit invariant still applies; reduce-first on conflicts or failures.
- MUST Edge gate remains in force; failure cannot justify ignoring edge requirements.
- MUST Unknown-Mode on unresolved conflicts or missing clarity; stay blocked/throttled until clarity and readiness return.
- SHOULD Define fail ? action mappings: data gap/stale -> stand-down; confirmation unavailable -> block entries; conflicting bias -> Unknown-Mode and exit-only posture.
- MAY include emergency stand-down timers after repeated failures; timers cannot block exits.

1.3 Edge Cases / Conflicts
- Partial readiness (some checks fail, others pass): robustness veto wins; entries blocked until all required checks pass.
- Bias strong but health failing: health veto overrides bias.

1.4 Examples (minimal, conceptual)
- Data quality falls below threshold ? block entries, manage exits until quality restores for a stable window.
- Confirmation feed missing but prices updating ? block entries; exit if risk mandates.

1.5 Open Questions
- [INBOX-REVIEW] Exact thresholds for declaring health degraded and the length of recovery windows.
