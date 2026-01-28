# M15 Higher Context

## Mini-Index
    - 1.0 Purpose
    - 1.1 Inputs / Dependencies
    - 1.2 Rules (MUST/SHOULD/MAY)
    - 1.3 Edge Cases / Conflicts
    - 1.4 Examples (minimal, conceptual)
    - 1.5 Open Questions

## 1.0 Purpose
    - Provide higher-level context from M15 closed bars to guide micro trades.

## 1.1 Inputs / Dependencies
    - M15 closed bars; regime classification; bias assessment.

## 1.2 Rules (MUST/SHOULD/MAY)
    - SHOULD use M15 for bias filtering and structure sanity; cannot override robustness or edge gates.
    - MAY demand stricter confirmations when M15 conflicts with M1/M5.
    - MUST keep decisions within 1-20m horizon; M15 is context, not a trigger.

## 1.3 Edge Cases / Conflicts
    - M15 Trend opposite M1 signal and Unknown-Mode or higher confirmation strictness until resolved.

## 1.4 Examples (minimal, conceptual)
    - M15 Trend up supports Momentum Long on M1 with normal confirmations.

## 1.5 Open Questions
    - [INBOX-REVIEW] Exact M15 thresholds for bias support/blocking.
