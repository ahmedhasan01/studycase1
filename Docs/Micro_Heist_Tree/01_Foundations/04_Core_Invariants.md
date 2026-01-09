# Core Invariants

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Define non-adaptive guardrails for live 1–20 minute trading that always hold, regardless of regime or bias.

1.1 Inputs / Dependencies
- Strategy signals (Long/Short) and confirmations on closed bars.
- Readiness/quality/health states from robustness gates.
- Edge-positive assessment (must be explicit; if missing → [INBOX-REVIEW]).

1.2 Rules (MUST/SHOULD/MAY)
- MUST Long/Short semantics: Long reduces/exits Short; Short reduces/exits Long.
- MUST Reduce-first doctrine: when conditions degrade or conflict, reduce/exit before any new exposure.
- MUST Confirmed Winning Bias flip → MUST reduce/exit current exposure before any new aligned exposure.
- MUST Edge-positive gate: if edge is unclear/negative → block entries; exits/reductions allowed. Edge-positive MUST exceed expected friction under current conditions (spread/impact); if friction definition is missing → [INBOX-REVIEW] and treat edge as not met.
- MUST Robustness gating: if readiness/quality/health is degraded → block entries; exits allowed.
- MUST Unknown-Mode: unresolved conflicts/unclear regime → block or heavily throttle entries until clarity returns.
- MUST Determinism: given inputs and states, outcomes are deterministic; no randomness.
- MAY Pause/throttle when uncertainty rises even if not fully Unknown-Mode, but never loosen these invariants.

1.3 Edge Cases / Conflicts
- Bias flips while in position: reduce/exit first, then reassess; do not overlap opposing exposures.
- Edge-positive definition absent → treat as not met; block entries ([INBOX-REVIEW]).
- Health and confirmations disagree: health veto wins; confirmations cannot override robustness.

1.4 Examples (minimal, conceptual)
- Ready and clear Long bias with edge-positive → ENTER; manage per risk/frequency.
- Regime unclear but health OK → BLOCK entries (Unknown-Mode), manage exits only.
- Edge borderline and health degraded → BLOCK entries; EXIT or REDUCE existing.
- Confirmed Winning Bias flip while holding → EXIT/REDUCE current before any new aligned exposure.

1.5 Open Questions
- [INBOX-REVIEW] Precise edge-positive metric definition and threshold.




