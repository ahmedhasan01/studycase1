# Reduce / Exit Doctrine

## Mini-Index
    - 1.0 Purpose
    - 1.1 Inputs / Dependencies
    - 1.2 Rules (MUST/SHOULD/MAY)
    - 1.3 Edge Cases / Conflicts
    - 1.4 Examples (minimal, conceptual)
    - 1.5 Open Questions

## 1.0 Purpose
    - Codify mandatory reduce/exit behavior for micro trades.

## 1.1 Inputs / Dependencies
    - Bias flips/degrades; edge status; health/readiness; confirmations; risk bounds.

## 1.2 Rules (MUST/SHOULD/MAY)
    - MUST reduce/exit on confirmed bias flip before any new aligned entry.
    - MUST reduce-first when conditions degrade (health, edge, confirmations, regime conflict).
    - MUST allow exits/reductions even when entries blocked (robustness override).
    - SHOULD stage exits to control risk within 1-20m horizon; avoid lingering conflicting exposure.
    - MAY hold small residual only if consistent with edge-positive and risk bounds; otherwise exit.

## 1.3 Edge Cases / Conflicts
    - Edge unknown but health OK: prefer reduce/exit unless strict rationale to hold; mark [INBOX-REVIEW] if undefined.
    - Conflicting signals without clarity: Unknown-Mode ? reduce/exit posture.

## 1.4 Examples (minimal, conceptual)
    - Bias flips Short ? exit Long immediately; wait for new confirmations before any Short entry.

## 1.5 Open Questions
    - [INBOX-REVIEW] Exact thresholds to trigger staged exits vs full exits.
