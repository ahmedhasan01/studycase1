# Core Invariants

## Operating Header
- **Mission:** Define non-adaptive guardrails for live 1–20 minute trading that always hold.
- **Use when:** Before any entry; when bias/regime conflicts; when a flip is suspected; when readiness/data-quality is degraded.
- **Hard constraints (cannot override):**
  - Reduce-first doctrine.
  - Confirmed flip ⇒ mandatory exit current exposure before any new aligned exposure.
  - If edge is unclear/negative ⇒ block entries; exits/reductions allowed.
  - If readiness/quality/health is degraded ⇒ block entries; exits allowed.
  - Unknown-Mode/Conflict unresolved ⇒ strict (BLOCK/THROTTLE entries); exits allowed.
  - Determinism: given the same inputs/states, outcomes are deterministic (no randomness).
- **Inputs / Dependencies (links):**
  - [05_Decision_Glossary.md](05_Decision_Glossary.md)
  - [01_Readiness_and_Health_Gates.md](../08_Operational_Robustness/01_Readiness_and_Health_Gates.md)
- **Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):**
  - Output = veto-capable guardrails that constrain all modules.
- **Failure modes (top 3):**
  - Allowing confirmations to override robustness.
  - Trading when edge/friction is undefined.
  - Overlapping opposing exposure during a confirmed flip.
- **Non-goals:**
  - Not a setup catalog; not indicator tuning.

## Procedure
1) Check readiness/health/data-quality state first (if degraded ⇒ BLOCK entries; exits allowed).
2) Check whether regime/conflict is unclear (if yes ⇒ Unknown-Mode ⇒ BLOCK/THROTTLE entries; exits allowed).
3) Check whether a confirmed flip exists (if yes ⇒ exit current exposure first).
4) Check edge-positive explicitly (if unclear/negative/undefined ⇒ BLOCK entries; exits allowed).
5) Only after (1–4) can any setup/confirmation logic grant entry permission.
6) If any module suggests weakening these rules ⇒ tag [REVIEW-CONFLICT] and keep strict behavior.

## Decision States
- **PASS:** All invariants satisfied → modules may permit entries (subject to their own gates).
- **THROTTLE:** Elevated uncertainty → fewer/stricter entries; exits allowed.
- **BLOCK:** No new entries; exits/reductions allowed.
- **EXIT/REDUCE:** Mandatory when flip/health/risk dictates.

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
- **MUST** Confirmed flip → MUST exit current exposure before any new aligned exposure.
- **MUST** Edge-positive gate: if edge is unclear/negative → block entries; exits/reductions allowed.
- **MUST** Edge-positive MUST exceed expected friction under current conditions (spread/impact). If friction definition is missing → [INBOX-REVIEW] and treat edge as not met.
- **MUST** Robustness gating: if readiness/quality/health is degraded → block entries; exits allowed.
- **MUST** Unknown-Mode: unresolved conflicts/unclear regime → block or heavily throttle entries until clarity returns; exits allowed.
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
- Confirmed flip while holding → EXIT current before any new aligned exposure.

## 1.5 Open Questions
- [INBOX-REVIEW] Precise edge-positive metric definition and threshold.
