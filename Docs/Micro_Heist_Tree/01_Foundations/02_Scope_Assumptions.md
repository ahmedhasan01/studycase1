# Scope & Assumptions

## Mini-Index
    - 1.0 Purpose
    - 1.1 Inputs / Dependencies
    - 1.2 Rules (MUST/SHOULD/MAY)
    - 1.3 Edge Cases / Conflicts
    - 1.4 Examples (minimal, conceptual)
    - 1.5 Open Questions

## ## 1.0 Purpose
    - Clarify scope and assumptions for this micro trading universe.

## 1.1 Inputs / Dependencies
    - Time horizon 1-20 minutes.
    - Bias, regime, readiness, edge assessments.

## 1.2 Rules (MUST/SHOULD/MAY)
    - MUST avoid venue-specific assumptions; docs remain venue-agnostic.
    - MUST avoid implementation specifics (no code/API/architecture here).
    - MUST Long/Short semantics per invariants; reduce-first on changes.
    - SHOULD assume closed-bar data for confirmations; intrabar not used for triggers.

## 1.3 Edge Cases / Conflicts
    - If an assumption requires venue details, move to [INBOX-REVIEW] or point to venue-specific doc (not present here).

## 1.4 Examples (minimal, conceptual)
    - Using M1/M5/M15/H1 closed bars to classify regime and confirm entries without referring to any venue.

## 1.5 Open Questions
    - [INBOX-REVIEW] Assumed data latency bounds for readiness gates.
