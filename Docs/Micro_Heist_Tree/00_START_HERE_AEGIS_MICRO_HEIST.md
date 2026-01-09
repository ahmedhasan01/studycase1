# Aegis Micro Heist - Start Here

## Mini-Index
- 1.0 Purpose
- 1.1 Canonical Reading Order
- 1.2 Non-Negotiables Snapshot
- 1.3 Precedence Ladder (short)
- 1.4 Playbook Flow (one line)
- 1.5 What To Do When X Happens
- 1.6 Links to Core Sections
- 1.7 Change Policy Reminder
- 1.8 Operating Mode (How the AI MUST run this universe)
- 1.9 Run Modes

1.0 Purpose
- Quick orientation for the Aegis Micro Heist doc set (1-20m trading). Bullet-first, deterministic, no venue assumptions.
- Use this before opening detailed modules; follow AI_Rules.md and the overlay (`00_AI_RULES_MICRO_HEIST.md`).

1.1 Canonical Reading Order
- AI_Rules.md -> 00_AI_RULES_MICRO_HEIST.md (overlay) -> 01_Foundations/04_Core_Invariants.md.
- Then: 08_Operational_Robustness/01_Readiness_and_Health_Gates.md -> 05_Setups/05_Confirmation_Gates.md -> 03_Bias_System/02_Priority_Biased_Side.md.
- Next: 04_Regimes_and_Routing/01_Regime_Taxonomy.md + 04_Regimes_and_Routing/02_Router_Eligibility_Policy.md -> 06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md.
- Last: 10_Playbook/01_Micro_Trade_Playbook.md -> 99_Appendix/01_Knowledge_Comparison_Matrix.md (for provenance).

1.2 Non-Negotiables Snapshot
- Long/Short only; Reduce/Exit invariant; Reduce-first doctrine.
- Confirmed Winning Bias flip -> MUST exit/reduce before any new aligned exposure.
- Edge-positive MUST exceed expected friction; if unclear -> BLOCK entries, exits allowed.
- Robustness gating and Unknown-Mode can veto entries; exits always allowed.
- Minimal regime taxonomy (Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation).

1.3 Precedence Ladder (short)
1) Operational Robustness (health/readiness/shock) - may veto entries.  
2) Core Invariants.  
3) Confirmed flip exit mandate.  
4) Winning Bias priority.  
5) Regime & Router eligibility.  
6) Confirmation gates.  
7) Setup definitions.  
8) Frequency fine-tuning (adaptive).  

1.4 Playbook Flow (one line)
- Ready -> Winning Bias -> Edge-positive -> Setup -> Confirm -> Enter/Manage -> Flip- Exit.

1.5 What To Do When X Happens
- Readiness fails: BLOCK entries; manage exits only; fix health before resuming.
- Unknown-Mode (regime/conflict unclear): BLOCK/THROTTLE entries; exits allowed; wait for clarity + readiness.
- Confirmed flip: EXIT/REDUCE current exposure before any new aligned exposure.
- Edge unclear/negative: BLOCK entries; exits allowed; re-evaluate edge definition if missing ([INBOX-REVIEW]).
- Conflicting signals (bias/confirmation disagree): default to Unknown-Mode; BLOCK/THROTTLE entries; exits allowed; resolve conflict via bias/regime modules.

1.6 Links to Core Sections
- Core Invariants: `01_Foundations/04_Core_Invariants.md`
- Readiness/Health: `08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
- Confirmation Gates: `05_Setups/05_Confirmation_Gates.md`
- Bias Priority: `03_Bias_System/02_Priority_Biased_Side.md`
- Regimes/Router: `04_Regimes_and_Routing/01_Regime_Taxonomy.md`, `04_Regimes_and_Routing/02_Router_Eligibility_Policy.md`
- Max Trades: `06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`
- Playbook: `10_Playbook/01_Micro_Trade_Playbook.md`
- Knowledge Matrix: `99_Appendix/01_Knowledge_Comparison_Matrix.md`
- Runtime Runbook (daily use shortcut; non-overriding): `Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Runbook_One_Page.md`
- Runtime Checklists (pocket): `Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Checklists.md`

1.7 Change Policy Reminder
- Stable Core changes are BREAKING; MUST be logged in Manifest and Playbook reviewed for consistency.
- Under uncertainty: default stricter gating + `[INBOX-REVIEW]`.
- Playbook is rechecked after any breaking change; Start Here updates if reading order/behavior shifts.

1.8 Operating Mode (How the AI MUST run this universe)
- MUST start from this file and follow its reading order before editing any module.
- MUST treat `00_MANIFEST_AEGIS_MICRO_HEIST.md` as the task-queue authority.
- When user says "Execute next step" -> MUST execute the highest-priority incomplete STEP in the Manifest Task Queue.
- When user says "Execute STEP-XX" or provides a STEP name -> MUST execute that specific STEP.
- MUST apply the precedence ladder (Overlay 3.0) on conflicts.
- If unclear or missing definitions -> MUST tag `[INBOX-REVIEW]` and default to stricter gating (block/throttle entries; exits allowed).
- SHOULD work in small batches (2-4 files per task) and output patched sections only (full content only for new files).

1.9 Run Modes
- EXECUTE: use Project Docs + AI Database only (light); no web research unless the STEP explicitly requires it; apply patches directly.
- SYNTHESIZE: before patching, MUST gather required knowledge and compare in order: (1) Online trusted books, (2) Online trusted sources, (3) AI Database, (4) Project Docs; then compare and select the best outcome aligned to project goals; provide a short "Comparison Summary" and "Decision" (bullets) before patching.
- Commands:
  - "Execute next step (MODE 1: LOCAL+AI_DB COMPARE -> FINAL PATCH ONLY)"
  - "Execute next step (MODE 2: LOCAL+ONLINE+AI_DB COMPARE -> FINAL PATCH ONLY)"
- If MODE not specified -> default MODE 1.
- Core Topics: use `99_Appendix/00_CORE_TOPICS_FIXED.md` (do not duplicate); Online Pack structure lives in `99_Appendix/02_Trusted_Online_Pack.md`.
