# Aegis Micro Heist — Book Overview (Cockpit Entry)

## Overview Block
- Mission: Provide a Book-first cockpit for the Aegis Micro Heist universe (1–20m).
- Use when: You want the canonical reading path and how decisions are gated.
- Hard constraints (never override): Invariants + robustness gating; “block entries / exits allowed” under uncertainty.
- Inputs/Dependencies:
  - Source pool during migration: `Docs/Micro_Heist_Tree/*`
  - Global rules: `Docs/rules/AI_Rules.md`
  - Overlay: `Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md`
- Outputs/Decisions: You know where to read next and what is canon vs advisory.
- Failure modes: Reader confusion due to duplication; prevented by single-source-of-truth + references.
- Non-goals: Introducing new rules or numeric thresholds.

## Table of Contents (Book)
- 01 Principles and Scope
- 02 Market Microstructure & Execution
- 03 Indicators & Signals
- 04 Entry/Exit Logic
- 05 Risk, Frequency, Friction
- 06 Readiness & Health Gates
- 07 Playbooks & Examples
- 99 Appendix (Glossary + Matrix + Provenance)

## Canonical Reading Order
- Start: `01_Principles_and_Scope.md`
- Then: `06_Readiness_Health_Gates.md` → `05_Risk_Frequency_Friction.md` → `04_Entry_Exit_Logic.md`
- Then: `03_Indicators_Signals.md` → `02_Market_Microstructure_Execution.md`
- Then: `07_Playbooks_Examples.md`
- Finally: `99_Appendix_Glossary_Matrix.md`

## Migration Note (no invention)
- This Book is being populated by migrating content from `Docs/Micro_Heist_Tree/*` with 0% info loss.
- Until migration is complete, chapters may reference the source modules directly.
