# Adaptive Parameters Policy

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Govern which parameters may adapt in live 1–20m trading, how they change, and what is forbidden.

1.1 Inputs / Dependencies
- Regime state and bias strength.
- Health/readiness status and Unknown-Mode state.
- Edge-positive assessment and confirmation outcomes.

1.2 Rules (MUST/SHOULD/MAY)
- MUST classify every rule as Invariant, Adaptive, or Override; invariants never adapt.
- MUST Allowed-to-adapt (examples): confirmation strictness; setup eligibility per regime; trade frequency throttle under Winning Bias; edge-positive tolerance (still must be positive); stand-down sensitivity to quality degradation.
- MUST Forbidden-to-adapt: Reduce/Exit invariant; reduce-first doctrine; confirmed bias flip exit mandate; block-entries/allow-exits principle; conflict precedence; hard risk caps; emergency actions.
- MUST Governance: adaptive changes only on confirmed condition shifts (regime change, health improvement/deterioration); no minute-to-minute oscillation; defaults tighten under uncertainty.
- MUST Unknown-Mode: if clarity/readiness is insufficient, adaptives default to strictest state (entries blocked or heavily throttled) until READY and clear regime.
- SHOULD document trigger ? change mapping (e.g., High-Vol Expansion ? stricter confirmations and lower frequency; Low-Vol Compression ? normal confirmations but throttled frequency).
- MAY include hysteresis to prevent flip-flop; must be deterministic.

1.3 Edge Cases / Conflicts
- Health veto vs adaptive loosening: health veto wins; adaptives cannot loosen under degraded conditions.
- If a parameter lacks definition ? treat as not READY; default to strictest; mark [INBOX-REVIEW].

1.4 Examples (minimal, conceptual)
- Regime shifts from Range to Trend: confirmations tighten; Mean-Reversion setups disabled; Momentum enabled with throttled frequency; invariants unchanged.
- Health improves from degraded to OK: can relax throttling one step if edge-positive and confirmations pass; invariants unchanged.

1.5 Open Questions
- [INBOX-REVIEW] Exact hysteresis values for moving between adaptive levels.
