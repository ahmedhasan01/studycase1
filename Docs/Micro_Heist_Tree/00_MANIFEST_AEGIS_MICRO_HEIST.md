# Aegis Micro Heist — Manifest (File-by-File Build Queue)

## 0.0 Purpose
- This is the single source of truth for the build plan and status.
- We build the universe module-by-module: each file becomes directly usable with:
  - Operating Header
  - Procedure checklist
  - Canonical links (no duplication)
  - QA pass

## 0.1 Status Legend
- TODO: not started
- DOING: being edited
- DONE: header + procedure + QA gates satisfied
- BLOCKED: needs `[INBOX-REVIEW]` resolution or `[REVIEW-CONFLICT]`

## 0.2 Global Constraints
- No numeric thresholds unless already present locally; otherwise tag `[INBOX-REVIEW]`.
- Under uncertainty: default strict (BLOCK/THROTTLE entries); exits allowed.
- Never weaken invariants or precedence ladder.
- External/online is rationale-only (when needed), never canon.

## 1.0 The Standard (must be applied to every module)
- Canonical standard is defined in: `Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md`
- Every module MUST start with:
  - Operating Header
  - Procedure checklist
- Every module MUST pass QA gates before being marked DONE.

## 2.0 Build Queue (Canonical)

### STEP-01 (P0 Foundations)
Goal: Make the foundational documents directly usable and consistent.
Files:
- DONE `01_Foundations/03_Definitions_Glossary.md`
- DONE `01_Foundations/04_Core_Invariants.md`
- DONE `01_Foundations/05_Decision_Glossary.md`
Done criteria:
- Operating Header + Procedure present
- Definitions consistent (no drift)
- No new numbers unless already local
Notes:
- If friction components are unclear → `[INBOX-REVIEW]`

### STEP-02 (P0 Readiness / Health / Failure)
Goal: Ensure readiness gates and failure responses are deterministic.
Files:
- DONE `08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
- DONE `08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md`
Done criteria:
- Clear PASS/BLOCK/THROTTLE logic
- “block entries / exits allowed” explicit
- Procedure includes abort + recovery

### STEP-03 (P0 Risk / Frequency / Friction)
Goal: Make risk and activity limits directly applicable.
Files:
- TODO `06_Risk_and_Frequency/01_Risk_Objectives.md`
- TODO `06_Risk_and_Frequency/02_Risk_Bounds.md`
- TODO `06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`
- TODO `06_Risk_and_Frequency/04_Cooldowns_and_NoTrade.md`
Done criteria:
- Frequency caps explicitly subordinate to readiness/health
- Edge>friction gate references canonical definitions (no duplication)

### STEP-04 (P0 Playbook)
Goal: Provide action-only playbooks that reference canon (no invention).
Files:
- TODO `10_Playbook/01_Micro_Trade_Playbook.md`
- TODO `10_Playbook/00_Runtime_Runbook_One_Page.md`
Done criteria:
- One-page principle preserved
- Every playbook step references its authoritative module

### STEP-05 (Routing Stack)
Goal: Bias + regime + router + unknown-mode deterministic.
Files:
- TODO `03_Bias_System/*`
- TODO `04_Regimes_and_Routing/*`
Done criteria:
- Conflict resolution and Unknown-Mode are explicit and tighten-only

### STEP-06 (Setups + Confirmations)
Goal: Setup menu + confirmations become directly usable modules.
Files:
- TODO `05_Setups/*`
Done criteria:
- Each setup file has header + procedure + failure modes; no hidden assumptions

### STEP-07 (Trade Management)
Goal: Management rules and scaling policies usable and consistent with invariants.
Files:
- TODO `07_Trade_Management/*`

### STEP-08 (Appendix / Provenance)
Goal: Provenance and trusted sources remain advisory-only.
Files:
- TODO `99_Appendix/*`
Done criteria:
- Advisory labeling clear; no numeric thresholds added

### STEP-09 (Trading Data Inputs — minimum viable)
Goal: Define what market data inputs are required vs optional for trading decisions (not integrations).
Files:
- TODO `09_Data/01_Trading_Data_Inputs.md`
Done criteria:
- Clear “Required vs Optional” list
- Each required input has a fail-safe rule (missing → strict)

### STEP-10 (Data Quality Gates — trading safety)
Goal: Define when data is too stale/missing/misaligned to permit entries.
Files:
- TODO `09_Data/02_Data_Quality_Gates.md`
Done criteria:
- Clear PASS/BLOCK/THROTTLE outcomes
- Explicit: quality fail → BLOCK/THROTTLE entries; exits allowed

### STEP-11 (Replay / Backfill Validation — trading behavior)
Goal: Validate determinism and fail-safe behavior using historical datasets (Excel/CSV/API dumps).
Files:
- TODO `09_Data/03_Replay_Backfill_Validation.md`
Done criteria:
- Procedures define how to verify “same data → same decisions”
- Missing data scenarios default strict

### STEP-12 (Data → Decision Wiring by module)
Goal: Document which modules require which inputs + strict fallbacks.
Files:
- TODO `09_Data/04_Data_Decision_Wiring.md`
Done criteria:
- Every major module category lists required inputs
- Fallbacks are always stricter

### STEP-13 (Data Provenance / Licensing — trading only)
Goal: Keep data usage legal and traceable without turning the repo into a dataset dump.
Files:
- TODO `09_Data/05_Data_Provenance_Licensing.md`
Done criteria:
- Clear “what is stored vs pointers only”
- No secrets/tokens; no restricted raw datasets committed

## 3.0 Open Items ([INBOX-REVIEW])
- [INBOX-REVIEW] Edge-positive friction components finalization (canonical location + links).
- [INBOX-REVIEW] Any missing definitions discovered during STEP-01..STEP-04.

## 4.0 Breaking Change Rule
A change is BREAKING if it modifies:
- Invariants (reduce-first, confirmed flip exit mandate, block entries/exits allowed doctrine)
- Precedence ladder ordering
If BREAKING:
- Mark `[REVIEW-CONFLICT]`
- Update Start Here
- Update playbook references


