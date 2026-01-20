# Aegis Micro Heist — Manifest (Book Build + Ops Archive)

## Mini-Index
- 1.0 Purpose
- 1.1 Current Status
- 1.2 Completed Items
- 1.3 Open Items ([INBOX-REVIEW])
- 1.4 Planning Notes (Non-canonical)
- 1.5 Recent Change Notes
- 1.6 How to Work in Small Batches
- CP Change Policy (How we update without drift)
- Next Steps (Book Backlog Queue)
- Archived Task Queue (History)

## 1.0 Purpose
- Snapshot of state and priorities for the Aegis Micro Heist documentation (1–20m trading).
- Reader surface is now `Docs/Book/*` (Book-first).
- Governance by `Docs/rules/AI_Rules.md` + `Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md`.

## 1.1 Current Status
- BOOK-FIRST pivot adopted:
  - `Docs/Book/*` is the cockpit (reader surface).
  - `Docs/Micro_Heist_Tree/*` remains the module warehouse during migration (no deletions).
- Verification order remains (rationale-only):
  1) Online trusted books
  2) Online trusted sources
  3) AI Database
  4) Project Docs
  -> then compare to produce the best final answer.
- Runtime Layer remains available:
  - `Docs/Micro_Heist_Tree/10_Playbook/00_Runtime_Runbook_One_Page.md` is the daily ops reference.
  - Canonical rules live in modules / invariants; playbook is action-only.

## 1.2 Completed Items
- Overlay renamed and hardened for Aegis Micro Heist.
- Core Invariants clarified (flip rule, edge-positive, determinism).
- Knowledge Comparison Matrix centralized in Appendix.
- Start Here + Index exist for navigation.
- BOOK scaffold created under `Docs/Book/*` with mandatory per-file Overview blocks (migration placeholders only).

## 1.3 Open Items ([INBOX-REVIEW])
- [INBOX-REVIEW] Define friction components for edge-positive gate (ensure glossary is canonical and referenced).
- [INBOX-REVIEW] Populate/verify Trusted Source citations in Knowledge Matrix (advisory only; no numeric thresholds).
- [INBOX-REVIEW] Migration pass: move canonical content from Micro_Heist_Tree into Book chapters (0% info loss; single-source-of-truth).

## 1.4 Planning Notes (Non-canonical)
- Book build strategy:
  - Build a stable Book backbone (chapter files).
  - Migrate content chapter-by-chapter from Micro_Heist_Tree modules into Book (no invention; no loss).
  - Keep Micro_Heist_Tree as source until migration completes; then archive (not delete).
- Universe feel rule:
  - Each Book file must start with a short “Overview block” that states mission, when to use, constraints, failure modes, and non-goals.

## 1.5 Recent Change Notes
- Pivoted to Book-first reader surface while preserving Micro_Heist_Tree as migration source.
- Added Book scaffold files with mandatory Overview blocks.

## 1.6 How to Work in Small Batches
- Prefer single-chapter migration edits; keep changes scoped and reversible.
- Apply Documentation Protocol (INTEGRATE) with logs on each touch.
- If uncertain placement/ownership → mark `[INBOX-REVIEW]`, default strict (block/throttle entries; exits allowed).

## Change Policy (How we update without drift)

### CP.1 Three layers of stability
- **Stable Core (rare changes / breaking changes):**
  - `Docs/rules/AI_Rules.md`
  - `Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md`
  - `Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md`
  - `Docs/Micro_Heist_Tree/10_Playbook/01_Micro_Trade_Playbook.md`
- **Semi-stable (occasional changes):**
  - Bias system docs
  - Regime taxonomy + router eligibility + unknown-mode
  - Confirmation gates
  - Adaptive parameters policy
  - Readiness/health gates + failure modes
- **Flexible (frequent changes):**
  - Setup pages
  - Examples, notes, appendix rationale
  - Book chapter narrative (must never weaken invariants)

### CP.2 What counts as a "Breaking Change"
A change is BREAKING if it modifies any invariant or the precedence ladder:
- Reduce-first doctrine
- Confirmed flip → mandatory exit
- Block entries / allow exits principle
- Invariant vs Adaptive vs Override definitions
- Precedence ladder ordering
- Playbook flow (Ready → Bias → Edge → Setup → Confirm → Manage → Flip? Exit)

If BREAKING:
- MUST document in this Manifest under “Breaking Changes Log”
- MUST review Playbook for consistency
- SHOULD update Start Here if reading order or operational behavior changes

### CP.3 Non-breaking changes (allowed)
- Clarifying wording (determinism, removing ambiguity)
- Adding short examples (conceptual)
- Improving organization (Book chapter structure) without changing meaning

### CP.4 Anti-duplication rule (prevents drift)
- Canonical rules live in ONE place:
  - Invariants in Core Invariants
  - Precedence ladder in the overlay
  - Playbook is action-only (references modules)
  - Book chapters must converge to single source-of-truth as migration completes

### CP.5 Batch size rule (prevents memory + drift)
- Each task SHOULD touch 2–4 files max (except Book scaffold / meta refresh tasks).
- If a definition is missing → tag `[INBOX-REVIEW]`.
- Default to stricter gating under uncertainty.

## Next Steps (Book Backlog Queue) — Canonical
- B1 (NOW): Populate `Docs/Book/00_Overview.md` with the universe entry + navigation (no new rules; references only).
- B2: Migrate Foundations into Book:
  - Definitions/Glossary, Core Invariants, Decision Glossary (0% loss; remove duplicates by reference).
- B3: Migrate Operational stack into Book:
  - Readiness/Health, Risk/Frequency/Friction, Entry/Exit logic.
- B4: Migrate Signals/Indicators + Microstructure into Book.
- B5: Playbooks + Examples into Book, keep one-page playbook principle.
- B6: Appendix: Knowledge Matrix + Trusted Pack alignment (advisory; provenance only).

## Archived Task Queue (History)
- Prior STEP-based queue retained for forensics/traceability.
- Do not delete; treat as historical record only.
- (Original content preserved below.)

## Next Steps (Task Queue)
This Task Queue is canonical.
Execute next step or STEP-XX.

- STEP-01A (DONE)
- Goal: Bias tiers + confirmed flip semantics aligned.
- Files touched: 03_Bias_System/*.
- Output expected: Bias tiers and confirmed flip definitions aligned with overlay/core invariants/playbook.
- Done criteria: Persistence/stability + conflicts resolved definition applied; tiers in use.
- Notes: Status: DONE.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB].
Output policy: FINAL PATCH ONLY. Core Topics list lives in `99_Appendix/00_CORE_TOPICS_FIXED.md`; do not duplicate.

- STEP-01B
- Goal: Regimes & Routing hardening.
- Files touched: 04_Regimes_and_Routing/01_Regime_Taxonomy.md; 04_Regimes_and_Routing/02_Router_Eligibility_Policy.md; 04_Regimes_and_Routing/03_Unknown_Mode.md.
- Output expected: Regime taxonomy and router eligibility consistent with overlay precedence/core invariants/playbook.
- Done criteria: Rules deterministic; conflicts resolved or [INBOX-REVIEW].
- Notes: DONE. RUN_MODE: MODE 1 (LOCAL+AI_DB COMPARE) applied; docs hardened with deterministic routing/unknown-mode/shock blocking; no unresolved conflicts.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-02 (parent)
- Goal: Populate setup families without placeholders.
- Files touched: 05_Setups/* (via sub-steps).
- Output expected: Setups completed through sub-steps.
- Done criteria: Sub-steps 02A/02B/02C complete.
- Notes: DONE. RUN_MODE: MODE 1 applied; 02A/02B/02C completed with tighten-only gating and [INBOX-REVIEW] placeholders where definitions are missing.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-02A
- Goal: Fill Setup Menu + Mean Reversion.
- Files touched: 05_Setups/01_Setup_Menu.md; 05_Setups/02_Mean_Reversion_Setups.md.
- Output expected: Menu + Mean Reversion fully written, no placeholders.
- Done criteria: Completed text; gaps tagged [INBOX-REVIEW].
- Notes: Prerequisite: Decision Glossary canonical section defines "Friction" (edge > friction) before writing setups.
- Notes: DONE.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-02B
- Goal: Fill Momentum Setups.
- Files touched: 05_Setups/03_Momentum_Setups.md.
- Output expected: Momentum setups complete.
- Done criteria: Completed text; gaps tagged [INBOX-REVIEW].
- Notes: DONE.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-02C
- Goal: Fill Range Setups.
- Files touched: 05_Setups/04_Range_Setups.md.
- Output expected: Range setups complete.
- Done criteria: Completed text; gaps tagged [INBOX-REVIEW].
- Notes: DONE.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-03
- Goal: Verify Max Trades/frequency caps align with readiness gates.
- Files touched: 06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md; readiness references.
- Output expected: Consistency note tying frequency caps to readiness/health gating.
- Done criteria: Explicit linkage written; conflicts resolved or tagged [INBOX-REVIEW].
- Notes: DONE. Friction defined in canonical glossary; readiness/health/router/shock gating now explicitly precede caps.
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.

- STEP-04
- Goal: Backfill Trusted Sources references (advisory only).
- Files touched: 99_Appendix/01_Knowledge_Comparison_Matrix.md.
- Output expected: Populated trusted source citations marked advisory; no numeric thresholds added.
- Done criteria: Citations added or [INBOX-REVIEW] placeholders; matrix consistent with verification order.
- Notes: DONE. Friction defined in canonical glossary; citations added (trusted sources advisory only).
- RUN_MODE: MODE 2 (LOCAL+ONLINE+AI_DB COMPARE). Compare Set: [Aegis_Trade_micro, Heist_strategy_doc, Online Books, Online Sources, AI DB]. Output policy: FINAL PATCH ONLY.
