# Aegis Micro Heist — Start Here (Operating Universe)

## Mini-Index
- 1.0 What this is
- 1.1 How to use the universe (file-by-file)
- 1.2 The decision flow (one line)
- 1.3 Non-negotiables snapshot
- 1.4 Where to start (P0 order)
- 1.5 If X happens (default actions)
- 1.6 Data for trading (inputs + quality gates)
- 1.7 How to contribute edits (the standard)
- 1.7A Conversation Protocol (OPEN DISCUSSION → #RUN_PS)
- 1.7B Manual Execute Commands (Operator Input Template)

## 1.0 What this is
- A deterministic trading documentation universe (all styles; focus 1–20m micro trade).
- Every file is an operating module: you open it and you can apply it immediately.

## 1.1 How to use the universe (file-by-file)

### 1.1A GitHub RAW rule (mandatory)
- Any time you use or edit a module, first open and read its GitHub RAW(main) version.
- If RAW cannot be read fully (chat behavior): **STOP → OPEN DISCUSSION → strict default** (BLOCK/THROTTLE entries; exits/reductions allowed).
- When you open any module:
  1) Read the Operating Header (Mission / Use when / Constraints).
  2) Follow the Procedure checklist exactly.
  3) If anything is unclear: default strict (BLOCK/THROTTLE entries); exits allowed. (Document-level tags live inside docs, not required in chat.)

## 1.2 The decision flow (one line)
Ready → Winning Bias → Edge-positive → Regime/Router → Setup → Confirm → Enter/Manage → Flip? Exit.

## 1.3 Non-negotiables snapshot
- Reduce-first doctrine.
- Confirmed flip → mandatory reduce/exit current exposure before any new aligned exposure.
- Readiness/Health/Data-Quality can reduce activity to zero entries; exits always allowed.
- Under uncertainty: Unknown-Mode (block/throttle entries); exits allowed.

## 1.4 Where to start (P0 order)
P0 = required to trade safely:
1) `01_Foundations/03_Definitions_Glossary.md`
2) `01_Foundations/04_Core_Invariants.md`
3) `01_Foundations/05_Decision_Glossary.md`
4) `08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
5) `08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md`
6) `06_Risk_and_Frequency/01_Risk_Objectives.md`
7) `06_Risk_and_Frequency/02_Risk_Bounds.md`
8) `06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`
9) `10_Playbook/01_Micro_Trade_Playbook.md`
10) `10_Playbook/00_Runtime_Runbook_One_Page.md`

After P0:
- Bias system (`03_Bias_System/*`)
- Regimes/routing (`04_Regimes_and_Routing/*`)
- Setups + confirmations (`05_Setups/*`)
- Trade management (`07_Trade_Management/*`)
- Data (trading inputs only): `09_Data/*`
- Appendix (`99_Appendix/*`)

## 1.5 If X happens (default actions)
- Readiness fails: BLOCK entries; manage exits only; restore health first.
- Data-quality fails (stale/missing/misaligned): BLOCK/THROTTLE entries; exits allowed.
- Unknown regime/conflict: Unknown-Mode → BLOCK/THROTTLE entries; exits allowed.
- Confirmed flip: reduce/exit current exposure before new aligned exposure.
- Edge unclear/negative: BLOCK entries; exits allowed.

## 1.6 Data for trading (inputs + quality gates)
- Data is a trading input, not an integration project.
- Use:
  - `09_Data/01_Trading_Data_Inputs.md` (what you need vs optional)
  - `09_Data/02_Data_Quality_Gates.md` (when missing/stale → strict)
  - `09_Data/04_Data_Decision_Wiring.md` (which module needs which inputs)

## 1.7 How to contribute edits (the standard)
- Every module must have:
  - Operating Header
  - Procedure checklist
  - Links to canonical definitions (no duplication)
  - QA pass (no loosened invariants, no new numbers unless already local)
- The working plan is tracked in: `Docs/Micro_Heist_Tree/00_MANIFEST_AEGIS_MICRO_HEIST.md`
- Canon protocol: see 1.7A / 1.7B.

## 1.7A Conversation Protocol (OPEN DISCUSSION → #RUN_PS)
Default mode is Discussion-only.
- The assistant begins with **OPEN DISCUSSION**: summarize requested change, map exact insertion points, and provide final proposed text blocks.
- No repository/file-writing steps are performed unless the user explicitly sends: **#RUN_PS**.

If GitHub RAW(main) is unavailable or cannot be read fully (chat behavior):
- **STOP**
- **OPEN DISCUSSION** (state what is missing and what fallback is needed)
- Apply **strict default** (BLOCK/THROTTLE entries; exits/reductions allowed)

## 1.7B Manual Execute Commands (Operator Input Template)
Use this template in chat:
- FILE: <repo-relative path from Road_map OR the RAW(main) link>
- ACTION: EXECUTE_STANDARD
- EXTRA: (optional) + ... / + ...

EXECUTE_STANDARD (what it means):
1) Open and read the target file from GitHub RAW(main).
2) Ensure the module has an Operating Header (Mission / Use when / Constraints / Inputs / Outputs / Failure modes / Non-goals).
3) Ensure a clear Procedure Checklist exists and is usable as-is.
4) Remove duplication by using canonical links (keep only minimal stubs when needed for usability).
5) Apply QA gates: do not loosen invariants; do not introduce new numbers; unresolved ambiguity defaults strict and is flagged for review inside docs.
