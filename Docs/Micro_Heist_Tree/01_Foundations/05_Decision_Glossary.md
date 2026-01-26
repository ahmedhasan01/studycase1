# Decision Glossary

## Operating Header
- Mission: Provide canonical decision terms used to gate trading (Ready, Winning Bias, Confirmed flip, Edge-positive, Friction, Unknown-Mode, VALID, Throttle).
- Use when: Any module outputs PASS/BLOCK/THROTTLE or references readiness/edge/friction/unknown-mode.
- Hard constraints (cannot override):
  - No numeric thresholds unless already present locally; otherwise tag [INBOX-REVIEW].
  - If a decision term’s criteria is missing/unclear → default strict (BLOCK/THROTTLE entries); exits allowed.
  - This file is canonical for decision vocabulary; other modules must link here (no redefinition).
- Inputs / Dependencies (links):
  - Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md
  - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
  - Output = deterministic decision language used across the universe.
- Failure modes (top 3):
  - “Ready” treated as subjective instead of gated.
  - “Edge-positive” used without friction consideration.
  - “Unknown” treated as tradeable.
- Non-goals:
  - Not a strategy chapter; no setup catalog.

## Procedure
1) When a module uses a decision term, it MUST reference this file.
2) If a new decision term is needed, add it here first (short + deterministic).
3) If criteria for a term are missing, mark [INBOX-REVIEW] and default strict.
4) If any module contradicts this glossary, tag [REVIEW-CONFLICT] and keep strict behavior.

# CANONICAL START (Decision Glossary)

- **Ready/Readiness**: health + data quality + operational readiness are OK; if not, entries blocked and exits allowed.
- **Winning Bias**: current favored side (Long/Short). Bias strength tiers follow Bias System (Strong/Moderate/Weak/Neutral); if tiers are undefined → [INBOX-REVIEW] and default stricter.
- **Confirmed flip**: bias shift that meets confirmation criteria in Bias module (persistence/stability + conflicts resolved); triggers mandatory reduce/exit before any new aligned exposure; if criteria missing → [INBOX-REVIEW] and treat as not confirmed.
- **Edge-positive**: expected edge exceeds expected friction (spread/impact); if undefined → [INBOX-REVIEW] and treat as not met.
- **Friction (trade costs/drag)**: components include spread/price-improvement uncertainty; slippage/impact based on marketability/urgency; fees/commissions (generic); adverse selection risk when conditions degrade. If any component is unclear → [INBOX-REVIEW] and default stricter on gating.
- **Unknown-mode**: regime/conflict unresolved; entries blocked or heavily throttled; exits allowed until clarity and readiness return.
- **VALID trade**: passes readiness/health, edge-positive, regime/router eligibility, confirmations, and risk/frequency/cooldown gates.
- **Regime**: per-symbol market-context label (trend/range/vol/shock) used to gate entries and select a setup menu; ambiguous/low-confidence regimes route to Unknown-Mode.
- **Router**: deterministic mapping from (Readiness, Regime, Winning Bias, instrument capability, micro sanity) → allowed setup families + entry policy (ALLOW/THROTTLE/BLOCK); cannot override invariants.
- **Router-eligibility**: router may allow entries only when readiness+data quality+micro sanity pass and regime is not Shock/Chaotic/Unknown; otherwise block/throttle entries (exits allowed).
- **Regime-confidence**: agreement/persistence measure for the current regime; low confidence or TF conflict ⇒ Unknown-Mode and tighten-only behavior.
- **Throttle**: intentional reduction of frequency/size; applies when uncertainty, caps, or cooldowns demand tighter behavior.

# CANONICAL END (Decision Glossary)

