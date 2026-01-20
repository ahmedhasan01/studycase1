# Decision Glossary

# CANONICAL START (Decision Glossary)
- Ready/Readiness: health + data quality + operational readiness are OK; if not, entries blocked and exits allowed.
- Winning Bias: current favored side (Long/Short). Bias strength tiers follow Bias System (Strong/Moderate/Weak/Neutral); if tiers are undefined -> [INBOX-REVIEW] and default stricter.
- Confirmed flip: bias shift that meets confirmation criteria in Bias module (persistence/stability + conflicts resolved); triggers mandatory reduce/exit before any new aligned exposure; if criteria missing -> [INBOX-REVIEW] and treat as not confirmed.
- Edge-positive: expected edge exceeds expected friction (spread/impact); if undefined -> [INBOX-REVIEW] and treat as not met.
- Friction (trade costs/drag): components include spread/price improvement uncertainty; slippage/impact based on marketability/urgency; fees/commissions (generic); adverse selection risk when conditions degrade. If any component is unclear -> [INBOX-REVIEW] and default stricter on gating.
- Unknown-mode: regime/conflict unresolved; entries blocked or heavily throttled; exits allowed until clarity and readiness return.
- VALID trade: passes readiness/health, edge-positive, regime/router eligibility, confirmations, and risk/frequency/cooldown gates.
- Regime: per-symbol market-context label (trend/range/vol/shock) used to gate entries and select a setup menu; ambiguous/low-confidence regimes route to Unknown-Mode.
- Router: deterministic mapping from (Readiness, Regime, Winning Bias, instrument capability, micro sanity) -> allowed setup families + entry policy (ALLOW/THROTTLE/BLOCK); cannot override invariants.
- Router-eligibility: router may allow entries only when readiness+data quality+micro sanity pass and regime is not Shock/Chaotic/Unknown; otherwise block/throttle entries (exits allowed).
- Regime-confidence: agreement/persistence measure for the current regime; low confidence or TF conflict => Unknown-Mode and tighten-only behavior.
- Throttle: intentional reduction of frequency/size; applies when uncertainty, caps, or cooldowns demand tighter behavior.
# CANONICAL END (Decision Glossary)

