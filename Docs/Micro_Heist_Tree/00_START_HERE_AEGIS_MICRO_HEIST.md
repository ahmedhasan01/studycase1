# Aegis Micro Heist — Start Here (Operating Universe)

## Mini-Index
- 1.0 What this is
- 1.1 How to use the universe (file-by-file)
- 1.2 The decision flow (one line)
- 1.3 Non-negotiables snapshot
- 1.4 Where to start (P0 order)
- 1.5 If X happens (default actions)
- 1.6 How to contribute edits (the standard)

## 1.0 What this is
- A deterministic micro trading documentation universe (1–20m).
- Every file is an operating module: you open it and you can apply it immediately.

## 1.1 How to use the universe (file-by-file)
- Read the P0 files in order (Section 1.4).
- When you open any module:
  1) Read the Operating Header (Mission / Use when / Constraints).
  2) Follow the Procedure checklist exactly.
  3) If anything is unclear → treat as `[INBOX-REVIEW]` and default strict (BLOCK/THROTTLE entries); exits allowed.

## 1.2 The decision flow (one line)
Ready → Winning Bias → Edge-positive → Regime/Router → Setup → Confirm → Enter/Manage → Flip? Exit.

## 1.3 Non-negotiables snapshot
- Reduce-first doctrine.
- Confirmed flip → mandatory reduce/exit current exposure before any new aligned exposure.
- Readiness/Health can reduce activity to zero entries; exits always allowed.
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
- Appendix (`99_Appendix/*`)

## 1.5 If X happens (default actions)
- Readiness fails: BLOCK entries; manage exits only; restore health first.
- Unknown regime/conflict: Unknown-Mode → BLOCK/THROTTLE entries; exits allowed.
- Confirmed flip: reduce/exit current exposure before new aligned exposure.
- Edge unclear/negative: BLOCK entries; exits allowed; tag `[INBOX-REVIEW]`.

## 1.6 How to contribute edits (the standard)
- Every module must have:
  - Operating Header
  - Procedure checklist
  - Links to canonical definitions (no duplication)
  - QA pass (no loosened invariants, no new numbers unless already local)
- The working plan is tracked in: `Docs/Micro_Heist_Tree/00_MANIFEST_AEGIS_MICRO_HEIST.md`.
