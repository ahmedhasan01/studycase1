# Bias Degrade vs Flip

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Describe how bias degrades (confidence drops) versus flips (direction change) and the required actions.

1.1 Inputs / Dependencies
- Winning Bias state; confirmations; health; edge-positive status.

1.2 Rules (MUST/SHOULD/MAY)
- MUST Degrade to Neutral/Unknown-Mode when confidence weakens or conflicts arise; entries blocked/throttled.
- MUST On confirmed flip (Long → Short or Short → Long): reduce/exit existing exposure before any new aligned entry.
- MUST Define “confirmed flip” as: (a) persistence/stability of the new bias across required confirmations, AND (b) conflicts resolved (no active disagreement with readiness/health/edge gates). No numeric thresholds; if missing, tag [INBOX-REVIEW].
- SHOULD Use Adaptive Parameters Policy to tighten confirmations/frequency when bias degrades before a flip.
- MAY hold Neutral when signals are mixed until clarity returns; entries throttled or blocked.

1.3 Edge Cases / Conflicts
- Partial evidence of flip but not confirmed → treat as degrade; do not switch sides until confirmation criteria above are met.
- Health degraded during potential flip → robustness veto; exit-only posture.
- If bias strength tier drops (Strong → Moderate → Weak) without confirming a flip → throttle frequency/strict confirmations; prefer Neutral/Unknown-Mode until clarity.

1.4 Examples (minimal, conceptual)
- Bias Long degrades to Neutral due to conflicting confirmations → pause entries, manage existing risk.
- Bias flip confirmed to Short → exit Long, then consider Short only after confirmations and edge-positive gate.

1.5 Open Questions
- [INBOX-REVIEW] Exact confirmation needed to declare a flip.

