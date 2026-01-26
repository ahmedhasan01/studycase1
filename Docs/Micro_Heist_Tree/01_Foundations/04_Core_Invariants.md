# Core Invariants

## Operating Header
- Mission: Non-adaptive guardrails that ALWAYS override all other modules in live 1–20m trading.
- Hard constraints (cannot override):
  - Reduce-first doctrine.
  - Confirmed flip ⇒ reduce/exit current exposure before new aligned exposure.
  - Edge unclear/negative ⇒ BLOCK entries; exits allowed.
  - Readiness/data-quality fail ⇒ BLOCK entries; exits allowed.
  - Unknown-Mode/Conflict unresolved ⇒ strict (BLOCK/THROTTLE entries); exits allowed.

## Procedure
1) Run readiness gates first (veto-capable).
2) Apply reduce-first on degradation/conflict.
3) Confirmed flip ⇒ exit/reduce first (no overlap).
4) If edge/friction unclear ⇒ BLOCK entries (strict default).

## Invariants (canonical list)
- Reduce-first.
- Flip-first-exit.
- Edge-positive required for entries.
- Readiness veto over “beautiful setups”.
- Determinism: same inputs ⇒ same decisions.

## Legacy (pre-standard) content (do not treat as canon unless re-integrated)
<details>
<summary>Show legacy content (Core Invariants)</summary>

# Core Invariants

## Operating Header
- Mission: Define non-adaptive guardrails for live 1–20 minute trading that always hold, regardless of regime or bias.
- Use when: Before any entry; when bias/regime conflicts; when a flip is suspected; when readiness/data-quality is degraded.
- Hard constraints (cannot override):
  - Reduce-first doctrine.
  - Confirmed Winning Bias flip ⇒ mandatory reduce/exit current exposure before any new aligned exposure.
  - If edge is unclear/negative ⇒ block entries; exits/reductions allowed.
  - If readiness/quality/health is degraded ⇒ block entries; exits allowed.
  - Under unresolved conflict/unclear regime ⇒ Unknown-Mode (block or heavily throttle entries); exits allowed.
  - Determinism: given the same inputs/states, outcomes are deterministic (no randomness).
- Inputs / Dependencies (links):
  - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
  - Output = veto-capable guardrails that constrain all modules.
- Failure modes (top 3):
  - Allowing confirmations to override robustness.
  - Trading when edge/friction is undefined.
  - Overlapping opposing exposure during a confirmed flip.
- Non-goals:
  - Not a setup catalog; not indicator tuning.

## Procedure
1) Check readiness/health/data-quality state first (if degraded ⇒ BLOCK entries; exits allowed).
2) Check whether regime/conflict is unclear (if yes ⇒ Unknown-Mode ⇒ BLOCK/THROTTLE entries; exits allowed).
3) Check whether a confirmed Winning Bias flip exists (if yes ⇒ reduce/exit current exposure first).
4) Check edge-positive explicitly (if unclear/negative/undefined ⇒ BLOCK entries; exits allowed).
5) Only after (1–4) can any setup/confirmation logic grant entry permission.
6) If any module suggests weakening these rules ⇒ tag [REVIEW-CONFLICT] and keep strict behavior.

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions

## 1.0 Purpose
Define non-adaptive guardrails for live 1–20 minute trading that always hold, regardless of regime or bias.

## 1.1 Inputs / Dependencies
- Strategy signals (Long/Short) and confirmations on closed bars.
- Readiness/quality/health states from robustness gates.
- Edge-positive assessment (must be explicit; if missing → [INBOX-REVIEW]).

## 1.2 Rules (MUST/SHOULD/MAY)
- **MUST** Long/Short semantics: Long reduces/exits Short; Short reduces/exits Long.
- **MUST** Reduce-first doctrine: when conditions degrade or conflict, reduce/exit before any new exposure.
- **MUST** Confirmed Winning Bias flip → MUST reduce/exit current exposure before any new aligned exposure.
- **MUST** Edge-positive gate: if edge is unclear/negative → block entries; exits/reductions allowed.
- **MUST** Edge-positive MUST exceed expected friction under current conditions (spread/impact). If friction definition is missing → [INBOX-REVIEW] and treat edge as not met.
- **MUST** Robustness gating: if readiness/quality/health is degraded → block entries; exits allowed.
- **MUST** Unknown-Mode: unresolved conflicts/unclear regime → block or heavily throttle entries until clarity returns.
- **MUST** Determinism: given inputs and states, outcomes are deterministic; no randomness.
- **MAY** Pause/throttle when uncertainty rises even if not fully Unknown-Mode, but never loosen these invariants.

## 1.3 Edge Cases / Conflicts
- Bias flips while in position: reduce/exit first, then reassess; do not overlap opposing exposures.
- Edge-positive definition absent → treat as not met; block entries ([INBOX-REVIEW]).
- Health and confirmations disagree: health veto wins; confirmations cannot override robustness.

## 1.4 Examples (minimal, conceptual)
- Ready and clear Long bias with edge-positive → ENTER; manage per risk/frequency.
- Regime unclear but health OK → BLOCK entries (Unknown-Mode), manage exits only.
- Edge borderline and health degraded → BLOCK entries; EXIT or REDUCE existing.
- Confirmed Winning Bias flip while holding → EXIT/REDUCE current before any new aligned exposure.

## 1.5 Open Questions
- [INBOX-REVIEW] Precise edge-positive metric definition and threshold.

</details>

