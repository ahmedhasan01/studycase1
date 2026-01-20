# Aegis Micro Heist — Start Here (Book-First)

## Mini-Index
- 1.0 Briefing (what this universe is)
- 1.1 Canonical Reading Order (Book-first)
- 1.2 Non-Negotiables Snapshot (fast safety)
- 1.3 Precedence Ladder (short)
- 1.4 Playbook Flow (one line)
- 1.5 If X Happens (default actions)
- 1.6 Where the “Old Ops/Steps” live now
- 1.7 Change Policy Reminder
- 1.8 Operating Mode (How the AI MUST run this universe)
- 1.9 Run Modes

## 1.0 Briefing (what this universe is)
- This is a deterministic micro-trading documentation universe (1–20m).
- Reader goal: open ANY file and immediately know:
  - Mission (what it does),
  - When to use it,
  - What it can and cannot override,
  - What failure looks like,
  - What the next action is.

## 1.1 Canonical Reading Order (Book-first)
- Primary entry: `Docs/Book/00_Overview.md`
- Then: `Docs/Book/01_Principles_and_Scope.md`
- Then (operational stack):
  - `Docs/Book/06_Readiness_Health_Gates.md`
  - `Docs/Book/05_Risk_Frequency_Friction.md`
  - `Docs/Book/04_Entry_Exit_Logic.md`
  - `Docs/Book/03_Indicators_Signals.md`
  - `Docs/Book/02_Market_Microstructure_Execution.md`
- Then: `Docs/Book/07_Playbooks_Examples.md`
- Finally: `Docs/Book/99_Appendix_Glossary_Matrix.md` (provenance + glossary + matrix)

## 1.2 Non-Negotiables Snapshot (fast safety)
- Long/Short only; Reduce/Exit invariant; Reduce-first doctrine.
- Confirmed Winning Bias flip → MUST exit/reduce current exposure before any new aligned exposure.
- Edge-positive MUST exceed expected friction; if unclear → BLOCK entries; exits allowed.
- Robustness gating and Unknown-Mode can veto entries; exits always allowed.
- Minimal regime taxonomy (Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation).

## 1.3 Precedence Ladder (short)
1) Operational Robustness (health/readiness/shock) — may veto entries.
2) Core Invariants.
3) Confirmed flip exit mandate.
4) Winning Bias priority.
5) Regime & Router eligibility.
6) Confirmation gates.
7) Setup definitions.
8) Frequency fine-tuning (adaptive).

## 1.4 Playbook Flow (one line)
- Ready → Winning Bias → Edge-positive → Setup → Confirm → Enter/Manage → Flip? Exit.

## 1.5 If X Happens (default actions)
- Readiness fails: BLOCK entries; manage exits only; restore health before resuming.
- Unknown-Mode (regime/conflict unclear): BLOCK/THROTTLE entries; exits allowed; wait for clarity + readiness.
- Confirmed flip: EXIT/REDUCE current exposure before any new aligned exposure.
- Edge unclear/negative: BLOCK entries; exits allowed; re-evaluate edge definition if missing (`[INBOX-REVIEW]`).
- Conflicting signals: default to Unknown-Mode; BLOCK/THROTTLE entries; exits allowed.

## 1.6 Where the “Old Ops/Steps” live now
- The prior step-based build queue remains in `Docs/Micro_Heist_Tree/00_MANIFEST_AEGIS_MICRO_HEIST.md` under “Archived Task Queue (History)”.
- Micro_Heist_Tree remains the source pool during migration, but the BOOK is the reader surface.

## 1.7 Change Policy Reminder
- Stable Core changes require extra care: overlay, invariants, playbook.
- Under uncertainty: become stricter (block/throttle); exits allowed.

## 1.8 Operating Mode (How the AI MUST run this universe)
- This universe is BOOK-FIRST.
- The BOOK is the reader’s cockpit; Micro_Heist_Tree is the module warehouse during migration.
- No numeric thresholds unless already present locally; otherwise tag `[INBOX-REVIEW]`.

## 1.9 Run Modes
- MODE 1: LOCAL + AI_DB compare (final patch only).
- MODE 2: LOCAL + ONLINE + AI_DB compare (final patch only; external is rationale-only).
