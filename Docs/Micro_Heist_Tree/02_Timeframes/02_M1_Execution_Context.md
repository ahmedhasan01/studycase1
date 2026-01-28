# M1 Execution Context

## Mini-Index
    - 1.0 Purpose
    - 1.1 Inputs / Dependencies
    - 1.2 Rules (MUST/SHOULD/MAY)
    - 1.3 Edge Cases / Conflicts
    - 1.4 Examples (minimal, conceptual)
    - 1.5 Open Questions

## 1.0 Purpose
    - Define how M1 closed bars inform execution hygiene within 1-20m horizon.

## 1.1 Inputs / Dependencies
    - M1 closed bars; micro hygiene metrics; confirmations; health state.

## 1.2 Rules (MUST/SHOULD/MAY)
    - MUST base confirmations/persistence on closed M1 bars; no intrabar triggers.
    - SHOULD use M1 to validate micro structure and timing windows.
    - MAY tighten M1 requirements when health is degraded or regime is High-Vol/Chop.

## 1.3 Edge Cases / Conflicts
    - If M1 and higher TFs disagree strongly and Unknown-Mode until alignment or explicit throttle.

## 1.4 Examples (minimal, conceptual)
    - Two-bar M1 persistence before a Mean-Reversion entry with strict micro hygiene.

## 1.5 Open Questions
    - [INBOX-REVIEW] Exact M1 persistence counts and confirm thresholds.
