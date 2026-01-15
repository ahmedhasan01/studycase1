# Max Trades Under Winning Bias

### Readiness-Gated Frequency Caps (Hardening)
- Purpose: Ensure max-trades / frequency caps NEVER override Readiness/Health and Router entry permissioning (tighten-only).
- See: `08_Operational_Robustness/01_Readiness_and_Health_Gates.md` (readiness failures force exit-only; new entries blocked until readiness is unambiguous).
- Precedence (MUST):
  - If Readiness/Health is NOT OK -> `max_trades = 0` effectively (BLOCK new entries); manage/reduce/exit allowed.
  - If Shock/Dislocation active or `route_mode=AVOID` -> entries BLOCKED regardless of any baseline cap; exits allowed.
  - If `route_mode=UNKNOWN` (TF conflict / low confidence) -> entries BLOCKED by default unless an explicit "Unknown-Mode throttle" plan is documented; exits allowed.
  - If `entry_policy=BLOCK` -> entries BLOCKED regardless of any max-trades cap; exits allowed.
- Tighten-only interaction with caps:
  - If `entry_policy=THROTTLE`, apply the stricter side of your existing cap logic (never loosen due to "desire to trade").
  - If uncertainty increases (micro sanity degrades, conflict rises), frequency rules MAY tighten (reduce trades), but MUST NOT loosen.
- Winning Bias interaction:
  - Frequency caps must respect "Confirmed flip -> mandatory exit" precedence: exit/reduce first; do not "use a new entry" to solve a flip.
  - If bias is unclear -> treat as NOT tradable unless explicitly permitted elsewhere; default stricter.
- If any referenced cap tiering or definitions are missing -> tag `[INBOX-REVIEW]` and default stricter (BLOCK/THROTTLE entries; exits allowed).

1.0 Purpose
- Define how many trades may occur when Winning Bias is active, respecting robustness, edge, and confirmations for 1-20 minute horizon.

1.1 Inputs / Dependencies
- Winning Bias state and strength.
- Edge-positive status and confirmation outcomes.
- Health/readiness gates; Unknown-Mode state.
- Adaptive Parameters Policy for frequency throttles.
- Router output `entry_policy in {ALLOW, THROTTLE, BLOCK}` and route_mode; Shock/Dislocation overrides.
- Cooldown/no-trade states from risk/robustness and per-setup cooldowns.

1.2 Rules (MUST/SHOULD/MAY)
- MUST "maximum valid trades" is always bounded by confirmations, risk caps, cooldowns, and robustness gates; never exceed these.
  If `entry_policy=BLOCK` or Shock/Dislocation override is active -> no new entries; exits/reductions allowed.
- MUST If Winning Bias active and health OK: trades may proceed up to frequency caps defined by adaptives; edge-positive required per trade; router entry_policy must be ALLOW/THROTTLE.
- MUST If bias neutral/uncertain: frequency is throttled sharply; only highest-quality setups may proceed if health OK and router allows; otherwise block.
- MUST Health degraded, Unknown-Mode, or micro sanity degraded: block new entries regardless of bias; exits/reductions allowed.
- SHOULD Use adaptive frequency caps tied to regime and bias strength; tighten by default under uncertainty or repeated conflicts.
- MAY enforce per-session max trades and per-setup cooldowns; if undefined -> [INBOX-REVIEW] and default to stricter (fewer trades).

1.3 Edge Cases / Conflicts
- Edge-positive borderline + bias strong: defer to stricter cap or block; do not override edge gate.
- Rapid alternating signals: apply reduce-first and cooldown before any new entry; frequency cap cannot be bypassed.

1.4 Examples (minimal, conceptual)
- Bias Long, health OK, Trend regime -> normal cap subject to confirmations and edge-positive; stop if cooldown triggered.
- Bias Neutral, Range regime -> at most one high-quality fade after strict confirmation; else stand down.

1.5 Open Questions
- [INBOX-REVIEW] Exact numeric trade caps per regime and per session.
