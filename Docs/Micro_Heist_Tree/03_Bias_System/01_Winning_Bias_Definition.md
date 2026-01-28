# Winning Bias Definition

## Mini-Index
  - 1.0 Purpose
  - 1.1 Inputs / Dependencies
  - 1.2 Rules (MUST/SHOULD/MAY)
  - 1.3 Edge Cases / Conflicts
  - 1.4 Examples (minimal, conceptual)
  - 1.5 Open Questions

## 1.0 Purpose
  - Define how Winning Bias is determined for Long/Short prioritization within 1–20m horizon.

## 1.1 Inputs / Dependencies
  - Regime classification, confirmations, edge assessments, health/readiness.

## 1.2 Rules (MUST/SHOULD/MAY)
  - MUST classify bias as Long, Short, or Neutral/Uncertain.
  - MUST Winning Bias requires supporting evidence from regimes/confirmations and edge-positive gate.
  - SHOULD degrade to Neutral/Unknown-Mode if evidence weakens or conflicts emerge.
  - MAY weight TFs and micro cues per Adaptive Parameters Policy; never bypass invariants.
  - SHOULD use conceptual bias strength tiers (no numbers): Strong / Moderate / Weak / Neutral.
    - Strong: clear alignment across regimes/confirmations/edge; frequency may be higher but still bounded by caps/cooldowns; confirmation strictness normal or stricter per Adaptive Policy.
    - Moderate: alignment present but less persistent; frequency normal; confirmation strictness normal/strict.
    - Weak: limited alignment or recently resolved conflicts; frequency throttled; confirmation strictness strict; may default to probe-only sizing if downstream rules allow.
    - Neutral: unresolved or no alignment; entries blocked or heavily throttled; treat as Unknown-Mode until clarity returns.

## 1.3 Edge Cases / Conflicts
  - Conflicting signals -> Neutral or Unknown-Mode; block or throttle entries.
  - Bias cannot be set if edge is negative/unknown.
  - If bias strength unclear -> default to weaker tier; apply stricter confirmations and lower frequency.

## 1.4 Examples (minimal, conceptual)
  - Trend regime + confirming Momentum setup -> Bias Long if edge-positive and healthy.
  - Mixed signals resolving but still unstable -> Bias Weak Long with strict confirmations and throttled frequency; upgrade only after stability.

## 1.5 Open Questions
  - [INBOX-REVIEW] Exact bias scoring/thresholds.
  - [INBOX-REVIEW] Formal mapping of tier labels to specific confirmation persistence if required.

