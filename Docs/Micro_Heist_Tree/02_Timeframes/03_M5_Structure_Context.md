# M5 Structure Context

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Describe how M5 closed bars provide structure for micro trades.

1.1 Inputs / Dependencies
- M5 closed bars; regime/bias context; confirmations from M1.

1.2 Rules (MUST/SHOULD/MAY)
- SHOULD use M5 for structure validation (ranges/trend continuity) supporting M1 execution.
- MUST not override robustness or edge gates.
- MAY tighten or loosen allowable setups based on M5 context using Adaptive Parameters Policy.

1.3 Edge Cases / Conflicts
- M5 Range while M1 signals Momentum ? require stricter confirmations or revert to Unknown-Mode.

1.4 Examples (minimal, conceptual)
- M5 range bounds used to validate Mean-Reversion targets on M1.

1.5 Open Questions
- [INBOX-REVIEW] Exact M5 structure metrics for validation.
