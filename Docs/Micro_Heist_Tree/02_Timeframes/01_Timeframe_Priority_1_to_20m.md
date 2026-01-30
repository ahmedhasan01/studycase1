# Timeframe Priority 1–20m

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Clarify the priority of 1–20 minute horizons, with 1 minute as the most reactive layer.

1.1 Inputs / Dependencies
- Closed bars for M1/M5/M15/H1.
- Bias/regime classification; confirmations.

1.2 Rules (MUST/SHOULD/MAY)
- MUST anchor decisions to 1–20 minute outcomes; longer context used only as filters.
- SHOULD let M1 drive execution hygiene; M5/M15 provide structure; H1 provides context filter.
- MAY throttle responsiveness if health is degraded (Unknown-Mode blocks entries).

1.3 Edge Cases / Conflicts
- If higher TF conflicts with M1 bias: Unknown-Mode or stricter confirmations until resolved.

1.4 Examples (minimal, conceptual)
- M1 shows setup, M5 supports, M15 neutral ? proceed if edge-positive and healthy.

1.5 Open Questions
- [INBOX-REVIEW] Exact weighting between TFs for bias decisions.
