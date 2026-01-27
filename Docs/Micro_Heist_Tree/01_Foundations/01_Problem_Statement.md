# Problem Statement

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Describe the live micro trading problem: sustained, safe Long/Short scalps on 1-20 minute horizons with bias priority.

1.1 Inputs / Dependencies
- Market data suitable for 1-20 minute decisions.
- Bias, regime, confirmations, edge-positive checks, robustness status.

1.2 Rules (MUST/SHOULD/MAY)
- MUST target 1-20 minute outcomes (priority from 1 minute).
- MUST obey Reduce/Exit invariant and reduce-first doctrine.
- SHOULD prioritize Winning Bias side when edge-positive and healthy.
- MAY throttle or stand down when clarity is low.

1.3 Edge Cases / Conflicts
- If scope drifts beyond 30 minutes, treat as out-of-scope; reframe or reject.

1.4 Examples (minimal, conceptual)
- Quick Long scalp aiming for 1-20 minutes with strict confirmations and robustness OK.

1.5 Open Questions
- [INBOX-REVIEW] Precise target metrics for success (e.g., expected edge definition).
