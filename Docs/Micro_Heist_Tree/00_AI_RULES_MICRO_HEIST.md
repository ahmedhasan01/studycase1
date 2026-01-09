# AI Rules Overlay — Aegis Micro Heist

## 0.0 Purpose
- Folder-scoped overlay to `AI_Rules.md` for `Docs/Micro_Heist_Tree/`.
- Ensure a robust LIVE micro trading strategy universe (1–20m): deterministic, resilient, permissioning-first, non-overfit.
- If conflict with Global rules, choose the stricter/safer interpretation; if unresolved, tag `[REVIEW-CONFLICT]` and default to entry-blocking/stricter gating; if info is missing, tag `[INBOX-REVIEW]`.
- Navigation starts from `00_START_HERE_AEGIS_MICRO_HEIST.md`; execution should follow Manifest task steps.
- RUN_MODE must be obeyed: EXECUTE (default) or SYNTHESIZE as specified by the user/STEP; research is rationale only; invariants and precedence ladder remain non-negotiable.

## Run Modes — Comparison Pipelines
- MODE 1 (LOCAL+AI_DB COMPARE): MUST consult `Aegis_Trade_micro.md`, `Heist_strategy_doc.md`, and AI Trusted DB. MUST produce a single Final Patch applied to STEP files (best result after comparing all inputs). MUST NOT show per-source patch notes in output.
- MODE 2 (LOCAL+ONLINE+AI_DB COMPARE): MUST consult `Aegis_Trade_micro.md`, `Heist_strategy_doc.md`, Online trusted books, Online trusted sources, and AI Trusted DB. MUST produce a single Final Patch applied to STEP files (best result after comparing all inputs). MUST NOT show per-source patch notes in output.
- Invariants and precedence ladder remain non-negotiable. Research is rationale-only and cannot override invariants. No numeric thresholds unless already present; otherwise use [INBOX-REVIEW].
- Core Topics (Fixed) — Canonical Reference: `99_Appendix/00_CORE_TOPICS_FIXED.md` holds the only authoritative list. Other files MUST NOT duplicate the list; reference it directly. Trusted Online Pack uses the same headers and is general/stable.
## 0.1 Scope
- Applies ONLY to content under `Docs/Micro_Heist_Tree/`.
- Strategy documentation only (no implementation/code, no venue assumptions).

## 1.0 Non-Negotiables (INVARIANTS)
- MUST use Long/Short language only; no venue types/names.
- MUST Reduce/Exit invariant: Long reduces/exits Short; Short reduces/exits Long.
- MUST Reduce-first doctrine: if conditions change, reduce/exit first, then consider new exposure.
- MUST Confirmed Winning Bias flip → MUST reduce/exit current exposure before any new aligned exposure.
- MUST Robustness gating: if readiness/health/quality is degraded, block new entries; exits allowed.
- MUST Unknown-Mode: if regime is unclear or conflict unresolved, entries blocked or heavily throttled; exits allowed.
- MUST Minimal regime taxonomy: Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation.

## 2.0 Adaptive vs Override (Governed Adaptivity)
- Adaptive (allowed via policy ONLY): setup eligibility; confirmation strictness; frequency throttle; edge-positive tolerance (still must be positive); tighten-only behavior under uncertainty.
- Forbidden-to-adapt: all invariants above; risk hard stops/emergency actions; precedence ladder; “entries blocked / exits allowed” principle.
- Tighten-only default: under uncertainty/degradation, become stricter (throttle/block), never looser.
- Hysteresis: adaptive mode changes require confirmation/stability; if oscillating/ambiguous → Unknown-Mode.

## 3.0 Precedence Ladder
1) Operational Robustness (health/readiness/shock) — may veto entries.  
2) Core Invariants (Section 1.0).  
3) Confirmed flip exit mandate.  
4) Winning Bias priority + bias strength tier behavior.  
5) Regime & Router eligibility policy.  
6) Confirmation gates (valid trade rules).  
7) Setup definitions (menu/families).  
8) Frequency fine-tuning (adaptive).

## 4.0 “VALID Trade” Definition (Micro)
- VALID only if ALL: readiness/health gates pass; edge-positive is clear; setup eligible for regime/router; confirmations pass; risk/frequency/cooldown allow it.
- If unclear → default to stricter gating or `[INBOX-REVIEW]`.

## 5.0 Playbook Rule (One Page)
- `10_Playbook/01_Micro_Trade_Playbook.md` must stay one-page and follow: Ready → Winning Bias → Edge-positive → Setup → Confirm → Enter/Manage → Flip? Exit.
- Playbook MUST NOT invent rules; every step MUST reference its authoritative module.

## 6.0 External/Trusted Sources (Rationale only)
- External/books/online are advisory only for rationale/definitions.
- Verification order MUST NOT be swapped: (1) Online trusted books, (2) Online trusted sources, (3) AI Database, (4) Project Docs — then compare to get the top answer related to the main project.
- MUST NOT introduce numeric thresholds unless already present locally.
- If external conflicts with invariants/robustness gates → discard external; invariants and robustness gates remain non-negotiable and always apply.
- Provenance recorded in `99_Appendix/01_Knowledge_Comparison_Matrix.md`.

## 7.0 Documentation Protocol (Local enforcement)
- Use Shared/Common + deltas-only; prevent duplication.
- Sections SHOULD be bullet-first; allow at most 1–2 context sentences per section.
- If placement unclear → `[INBOX-REVIEW]` (default strict).
- If unreconcilable conflict → `[REVIEW-CONFLICT]` and do NOT guess.
