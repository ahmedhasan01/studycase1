# Confirmation Gates

## Mini-Index
    - 1.0 Purpose
    - 1.1 Inputs / Dependencies
    - 1.2 Rules (MUST/SHOULD/MAY)
    - 1.3 Edge Cases / Conflicts
    - 1.4 Examples (minimal, conceptual)
    - 1.5 Open Questions

## 1.0 Purpose
    - Define confirmation requirements for 1�20 minute setups so entries are gated by persistence, quality, and robustness.

## 1.1 Inputs / Dependencies
    - Setup signals (Mean-Reversion, Momentum, Range) aligned to Winning Bias and regime.
    - Closed-bar data only (M1+ higher) for confirmations.
    - Health/readiness states and Unknown-Mode.
    - Edge-positive status.

## 1.2 Rules (MUST/SHOULD/MAY)
    - MUST use closed bars only; no intrabar triggers for confirmations.
    - MUST Persistence: setup condition true for required consecutive closed bars; if value is undefined -> [INBOX-REVIEW] and block entries.
    - MUST Confirming candle quality: body/wick/close-quality checks appropriate to setup family; if undefined -> [INBOX-REVIEW] and block.
    - MUST Micro hygiene: spread/tightness/quality gates must be passable; if micro degraded -> block or tighten to Unknown-Mode behavior.
    - MUST Edge-positive gate before final confirmation; confirmations cannot override edge check.
    - SHOULD Adjust confirmation strictness per regime/bias strength via Adaptive Parameters Policy (tighten under uncertainty/high-vol).
    - MAY add independent secondary confirmations; they cannot override robustness or edge gates.

## 1.3 Edge Cases / Conflicts
    - Conflicting confirmations (one pass, one fail) -> Unknown-Mode for that setup: block or throttle entries until aligned.
    - Health degraded even if confirmations pass -> block entries (robustness veto).
    - Bias flip during confirmation window -> reduce/exit first; restart confirmation if re-entering aligned side.

## 1.4 Examples (minimal, conceptual)
    - Mean-Reversion: persistence on M1 + confirming candle with controlled wicks and body in favor of reversion; spread within hygiene cap; edge-positive -> entry MAY proceed.
    - Momentum: breakout close beyond structure + confirming follow-through; high-vol regime -> stricter thresholds and lower frequency.

## 1.5 Open Questions
    - [INBOX-REVIEW] Exact persistence count and confirm candle numeric thresholds per setup family.
