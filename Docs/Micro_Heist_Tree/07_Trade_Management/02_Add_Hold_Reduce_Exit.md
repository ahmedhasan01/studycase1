# Add / Hold / Reduce / Exit

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

1.0 Purpose
- Describe how positions are managed after entry within 1–20m horizon.

1.1 Inputs / Dependencies
- Edge updates, confirmations, bias/regime changes, health/readiness, cooldowns.

1.2 Rules (MUST/SHOULD/MAY)
- MUST reduce/exit first when conditions degrade or bias flips; adds allowed only when edge-positive, healthy, and within frequency/risk bounds.
- SHOULD limit adds to maintain 1–20m intent; avoid over-sizing in tight horizons.
- MUST allow exits/reductions even when entries blocked.
- MAY hold if conditions stable and edge remains positive; reassess frequently.

1.3 Edge Cases / Conflicts
- Add signal during cooldown -> reject; manage existing exposure only.
- Edge drops below zero while holding -> reduce/exit promptly.

1.4 Examples (minimal, conceptual)
- Reduce partial when confirmation weakens; exit fully on confirmed bias flip.

1.5 Open Questions
- [INBOX-REVIEW] Specific add/scale rules consistent with risk bounds.
