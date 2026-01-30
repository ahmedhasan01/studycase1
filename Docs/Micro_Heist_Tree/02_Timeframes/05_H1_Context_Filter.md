# H1 Context Filter

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Set higher-timeframe (H1) filters that constrain micro trades without changing the 1–20m target horizon.

1.1 Inputs / Dependencies
- H1 closed bars; regime classification; bias system.

1.2 Rules (MUST/SHOULD/MAY)
- SHOULD use H1 to filter out trades against dominant context (e.g., block Longs in strong downward H1 bias).
- MUST not convert H1 into triggers; it is gating/context only.
- MAY tighten confirmation/frequency when H1 conflicts with lower TFs; Unknown-Mode if unresolved.

1.3 Edge Cases / Conflicts
- H1 conflict with M15/M5/M1: robustness and Unknown-Mode dominate; entries blocked/throttled until aligned.

1.4 Examples (minimal, conceptual)
- H1 strong downtrend ? Long entries blocked or require exceptional edge; Shorts still reduce/exit Longs per invariant.

1.5 Open Questions
- [INBOX-REVIEW] H1 slope/vol thresholds for gating.
