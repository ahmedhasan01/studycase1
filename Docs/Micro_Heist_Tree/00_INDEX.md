# Aegis Micro Heist Index

## Mini-Index
- 1.0 Purpose
- 1.1 Core Rules Snapshot
- 1.2 Master Index Table
- 1.3 Conflict Precedence

1.0 Purpose
- Provide a routes-first, micro-horizon documentation map for live trading (1-20 minutes) without venue assumptions.
- Start here: read `00_START_HERE_AEGIS_MICRO_HEIST.md` then follow the canonical order below.

## 1.0A Runtime Entry Points (daily use)
- One-page runbook: `Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Runbook_One_Page.md`
- Pocket checklists: `Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Checklists.md`
- Note: These are operational shortcuts. Canonical truth remains the module tree under `Docs/Micro_Heist_Tree/`.

1.1 Core Rules Snapshot
- Reduce/Exit invariant: Long reduces/exits Short; Short reduces/exits Long; reduce-first when conditions change.
- Edge-positive gate: if edge is unclear/negative, block entries; exits/reductions stay allowed.
- Robustness gating: degraded readiness/health blocks entries; exits allowed; Unknown-Mode throttles/blocks entries.
- Winning Bias priority: when bias is clear, prioritize that side; frequency still bounded by confirmations, risk, cooldowns.
- Adaptive changes follow Adaptive Parameters Policy; invariants never adapt.

1.2 Master Index Table
| ID | Level | Path | Title | One-line purpose | Depends on |
|---:|---|---|---|---|---|
| 0 | Root | Docs/Micro_Heist_Tree | Root | Container for micro trading strategy docs | Core Invariants |
| 0.0 | File | 00_START_HERE_AEGIS_MICRO_HEIST.md | Start Here - Aegis Micro Heist | Orientation + reading order | AI_Rules.md + overlay |
| 0.0a | File | 00_AI_RULES_MICRO_HEIST.md | AI Rules Overlay - Aegis Micro Heist | Folder-scoped overlay (stricter/safer) | AI_Rules.md + overlay |
| 0.0b | File | 00_MANIFEST_AEGIS_MICRO_HEIST.md | Manifest - Aegis Micro Heist | Status, open items, next steps | AI_Rules.md + overlay |
| 0.1 | Folder | 01_Foundations | Foundations | Definitions and invariants | Core Invariants |
| 0.1.4 | File | 01_Foundations/04_Core_Invariants.md | Core Invariants | Non-adaptive guardrails (edge, exits, robustness) | None |
| 0.1.5 | File | 01_Foundations/05_Decision_Glossary.md | Decision Glossary | Definitions of readiness/bias/edge/unknown/throttle | Core Invariants |
| 0.2 | Folder | 02_Timeframes | Timeframes | Roles for M1-H1 within 1-20m horizon | Core Invariants |
| 0.3 | Folder | 03_Bias_System | Bias System | Winning bias definition and priority side | Foundations |
| 0.3.2 | File | 03_Bias_System/02_Priority_Biased_Side.md | Priority Biased Side | How winning bias drives priority trades | Core Invariants |
| 0.4 | Folder | 04_Regimes_and_Routing | Regimes and Routing | Regime taxonomy, routing, unknown mode, adaptives | Bias System |
| 0.4.1 | File | 04_Regimes_and_Routing/01_Regime_Taxonomy.md | Regime Taxonomy | Minimal regimes with allowed/blocked setups | Core Invariants |
| 0.4.2 | File | 04_Regimes_and_Routing/02_Router_Eligibility_Policy.md | Router Eligibility Policy | Routing eligibility per regime/bias | Core Invariants |
| 0.4.4 | File | 04_Regimes_and_Routing/04_Adaptive_Parameters_Policy.md | Adaptive Parameters Policy | What can adapt and how; governance | Core Invariants |
| 0.5 | Folder | 05_Setups | Setups | Setup families and confirmations | Regimes |
| 0.5.5 | File | 05_Setups/05_Confirmation_Gates.md | Confirmation Gates | Persistence + confirmation rules for entries | Core Invariants |
| 0.6 | Folder | 06_Risk_and_Frequency | Risk and Frequency | Risk objectives, bounds, max trades | Core Invariants |
| 0.6.3 | File | 06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md | Max Trades Under Winning Bias | Frequency caps under bias + readiness gating | Core Invariants |
| 0.7 | Folder | 07_Trade_Management | Trade Management | Entry hygiene, add/hold/reduce/exit doctrine | Core Invariants |
| 0.8 | Folder | 08_Operational_Robustness | Operational Robustness | Readiness, shocks, failure modes | Core Invariants |
| 0.8.3 | File | 08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md | Failure Modes and Emergency Actions | Stand-down and recovery rules | Core Invariants |
| 0.10 | Folder | 10_Playbook | Playbook | One-page micro trading sequence | All above |
| 0.99 | Folder | 99_Appendix | Appendix | Supporting matrices and references | Core Invariants |
| 0.99.0 | File | 99_Appendix/00_CORE_TOPICS_FIXED.md | Core Topics (Fixed) | Canonical list of fixed Core Topics headers | Core Invariants |
| 0.99.1 | File | 99_Appendix/01_Knowledge_Comparison_Matrix.md | Knowledge Comparison Matrix | Provenance of key rules; local vs trusted sources | Core Invariants |
| 0.99.2 | File | 99_Appendix/02_Trusted_Online_Pack.md | Trusted Online Pack | Online/trusted sources scaffold aligned to Core Topics | Core Invariants |
| 10.0A | File | Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Runbook_One_Page.md | Runtime Runbook (One Page) | Daily operating flow; does not override canonical modules | StartHere + Core modules |
| 10.0B | File | Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Checklists.md | Runtime Checklists | Pocket checklists for readiness/bias/router/setup/risk | Runbook + Core modules |
| 0.3.2.a | Section | 03_Bias_System/02_Priority_Biased_Side.md#1-2-rules | Rules: Winning bias priority and edge gate | Core Invariants |
| 0.4.1.a | Section | 04_Regimes_and_Routing/01_Regime_Taxonomy.md#1-2-rules | Rules: regime allowed/blocked setups and throttles | Core Invariants |
| 0.5.5.a | Section | 05_Setups/05_Confirmation_Gates.md#1-2-rules | Rules: persistence + confirm filters | Core Invariants |
| 0.6.3.a | Section | 06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md#1-2-rules | Rules: frequency caps under bias/readiness | Core Invariants |
| 0.8.3.a | Section | 08_Operational_Robustness/03_Failure_Modes_and_Emergency_Actions.md#1-2-rules | Rules: block entries on failure, exits allowed | Core Invariants |
| 09_Data | Trading-only data layer (inputs + quality gates + fail-safe) | Docs/Micro_Heist_Tree/09_Data/01_Trading_Data_Inputs.md |

1.3 Conflict Precedence
- Core Invariants win any conflict.
- Operational Robustness can veto entries at any time; exits/reductions always allowed.
- Adaptive Parameters Policy can only tune Adaptive rules; it never alters invariants.
- Unknown-Mode (conflict/unclear) blocks or heavily throttles entries until clarity and readiness return.


## 09_Data (Trading-only Data Layer)
- Purpose: data as *trading input only* (no integration engineering).
  - 09_Data/01_Trading_Data_Inputs.md
  - 09_Data/02_Data_Quality_Gates.md
  - 09_Data/03_Replay_Backfill_Validation.md
  - 09_Data/04_Data_Decision_Wiring.md
  - 09_Data/05_Data_Provenance_Licensing.md

