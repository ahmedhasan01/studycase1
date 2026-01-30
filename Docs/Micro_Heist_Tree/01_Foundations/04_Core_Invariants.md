# Core Invariants

## Operating Header
- **Mission:** Define non-adaptive guardrails for live 1–20 minute trading that always hold.
- **Use when:** Before any entry; when bias/regime conflicts; when a flip is suspected; when readiness/data-quality is degraded.
- **Hard constraints (cannot override):**
  - Reduce-first doctrine.
  - **Confirmed flip** ⇒ mandatory exit current exposure before any new aligned exposure.
  - If edge is unclear/negative ⇒ BLOCK entries; exits/reductions allowed.
  - If readiness/quality/health is degraded ⇒ BLOCK entries; exits allowed.
  - Unknown-Mode / conflict unresolved ⇒ strict (BLOCK/THROTTLE entries); exits allowed.
  - Determinism: given the same inputs/states, outcomes are deterministic (no randomness).
- **Inputs / Dependencies (links):**
  - [05_Decision_Glossary.md](05_Decision_Glossary.md)
  - [01_Readiness_and_Health_Gates.md](../08_Operational_Robustness/01_Readiness_and_Health_Gates.md)
- **Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):**
  - Veto-capable guardrails constraining all modules.
- **Failure modes (top 3):**
  - Allowing confirmations to override robustness.
  - Trading when edge/friction is undefined.
  - Overlapping opposing exposure during a confirmed flip.
- **Non-goals:** Not a setup catalog; not indicator tuning.

## Procedure
1) Check readiness/health/data-quality first (degraded ⇒ **BLOCK** entries; exits allowed).
2) If regime/conflict unclear ⇒ Unknown-Mode ⇒ **BLOCK/THROTTLE** entries; exits allowed.
3) If a **Confirmed flip** exists ⇒ **exit current exposure first** (no overlap).
4) Edge-positive must be explicit (unclear/negative/undefined ⇒ **BLOCK** entries; exits/reductions allowed).
5) Only after (1–4) may any setup/confirmation logic permit entries.
6) If any module suggests weakening these invariants ⇒ tag **[REVIEW-CONFLICT]** and keep strict behavior.

## Decision States
- **PASS:** Invariants satisfied → modules may permit entries (subject to their own gates).
- **THROTTLE:** Uncertainty elevated → fewer/stricter entries; exits allowed.
- **BLOCK:** No new entries; exits/reductions allowed.
- **EXIT/REDUCE:** Mandatory when flip/health/risk dictates.

## Mini-Index
- 1.0 Purpose
- 1.1 Inputs / Dependencies
- 1.2 Rules (MUST/SHOULD/MAY)
- 1.3 Edge Cases / Conflicts
- 1.4 Examples (minimal, conceptual)
- 1.5 Open Questions (Audit)

## 1.0 Purpose
Define non-adaptive guardrails for live 1–20 minute trading that always hold, regardless of regime or bias.

## 1.1 Inputs / Dependencies
- Strategy signals (Long/Short) and confirmations on closed bars.
- Readiness/quality/health states from robustness gates.
- Edge-positive assessment (must be explicit; if missing → [INBOX-REVIEW]).

## 1.2 Rules (MUST/SHOULD/MAY)
- **MUST** Long/Short semantics: Long reduces/exits Short; Short reduces/exits Long.
- **MUST** Reduce-first doctrine: when conditions degrade or conflict, reduce/exit before any new exposure.
- **MUST** **Confirmed flip** → MUST exit current exposure before any new aligned exposure.
- **MUST** Edge-positive gate: if edge is unclear/negative → BLOCK entries; exits/reductions allowed.
- **MUST** Edge-positive MUST exceed expected friction under current conditions. If friction definition is missing → [INBOX-REVIEW] and treat edge as not met.
- **MUST** Robustness gating: if readiness/quality/health is degraded → BLOCK entries; exits allowed.
- **MUST** Unknown-Mode: unresolved conflicts/unclear regime → BLOCK or heavily THROTTLE entries until clarity returns; exits allowed.
- **MUST** Determinism: given inputs and states, outcomes are deterministic; no randomness.
- **MAY** Pause/throttle when uncertainty rises, but never loosen these invariants.

## 1.3 Edge Cases / Conflicts
- Bias flips while in position: reduce/exit first, then reassess; do not overlap opposing exposures.
- Edge-positive definition absent → treat as not met; BLOCK entries ([INBOX-REVIEW]).
- Health and confirmations disagree: health veto wins; confirmations cannot override robustness.

## 1.4 Examples (minimal, conceptual)
- Ready and clear Long bias with edge-positive → ENTER; manage per risk/frequency.
- Regime unclear but health OK → BLOCK entries (Unknown-Mode), manage exits only.
- Edge borderline and health degraded → BLOCK entries; EXIT or REDUCE existing.
- **Confirmed flip** while holding → EXIT current before any new aligned exposure.

## 1.5 Open Questions (Audit)

> Operating rule: until these are resolved, default strict behavior applies (BLOCK/THROTTLE entries; exits/reductions allowed). Tag items as [INBOX-REVIEW]. Do not guess.

### Questions
- [INBOX-REVIEW] **Confirmed flip:** canonical definition + confirmation criteria; where is it defined?
- [INBOX-REVIEW] **Unknown-Mode:** exact triggers for “conflict unresolved / regime unclear”; where is it defined?
- [INBOX-REVIEW] **Edge-positive:** operational definition without introducing new numeric thresholds.
- [INBOX-REVIEW] **Friction:** what components are included (spread/impact only, or also slippage/fees/latency); deterministic handling without adding numbers.
- [INBOX-REVIEW] **EXIT vs REDUCE:** does “exit current exposure” mean full flatten immediately, or staged reduction allowed before full exit?

### Missing
- [INBOX-REVIEW] Canonical links for Confirmed flip / Unknown-Mode / Edge-positive / Friction once finalized.
- [INBOX-REVIEW] Explicit triggers for THROTTLE vs BLOCK under uncertainty.

### Contradictions
- None detected inside this file currently. Watch for future definitions that weaken robustness veto or permit entries when edge/friction is undefined.

### Safe defaults until resolved
- If Edge-positive is not explicitly defined/verified ⇒ treat edge as NOT met ⇒ **BLOCK entries; exits/reductions allowed**.
- If Friction definition is missing ⇒ treat edge as NOT met ⇒ **BLOCK entries; exits/reductions allowed**.
- If Confirmed flip definition is unclear in live context ⇒ treat as uncertainty ⇒ **THROTTLE/BLOCK entries** and prioritize reducing risk; never overlap opposing exposures.
- If Unknown-Mode trigger is uncertain ⇒ prefer **Unknown-Mode strict** (BLOCK/THROTTLE entries); exits allowed.