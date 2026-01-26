# AI Rules Overlay — Aegis Micro Heist (Trading-Only Universe)

## 0.0 Purpose
- Folder-scoped overlay to `Docs/rules/AI_Rules.md` for `Docs/Micro_Heist_Tree/`.
- Goal: every file must be immediately understandable and directly applicable as an operating module for trading (all styles, with focus on 1–20m micro trade).
- Default safety: under uncertainty or missing info → become stricter (BLOCK/THROTTLE entries); exits/reductions always allowed.
- If unresolved conflict → tag `[REVIEW-CONFLICT]` and DO NOT guess.
- If missing definitions/criteria → tag `[INBOX-REVIEW]` and default strict.

## 0.1 Canon Policy (Local rules are king)
- Project-local docs are canonical.
- External/online/books may be consulted ONLY as *rationale* for wording/definitions when needed.
- External rationale MUST NOT:
  - override invariants,
  - introduce numeric thresholds if not already local,
  - weaken gating under uncertainty,
  - change the precedence ladder.
- If external conflicts with local canon → discard external.

## 1.0 Non-Negotiables (INVARIANTS)
- Long/Short only; no venue types/names.
- Reduce/Exit invariant: Long reduces/exits Short; Short reduces/exits Long.
- Reduce-first doctrine: reduce/exit first, then consider new exposure.
- Confirmed Winning Bias flip → MUST reduce/exit current exposure before any new aligned exposure.
- Robustness gating: if readiness/health/quality is degraded, block new entries; exits allowed.
- Unknown-Mode: if regime is unclear or conflicts persist, entries blocked or heavily throttled; exits allowed.
- Minimal regime taxonomy: Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation.

## 2.0 Precedence Ladder (Always)
1) Operational Robustness (health/readiness/shock/data-quality) — may veto entries.
2) Core Invariants (Section 1.0).
3) Confirmed flip exit mandate.
4) Winning Bias priority + bias strength tier behavior.
5) Regime & Router eligibility policy.
6) Confirmation gates.
7) Setup definitions.
8) Frequency fine-tuning (adaptive, tighten-only).

## 3.0 Mandatory File Standard (Every `.md` module)
Every file MUST start with the following header (INTEGRATE-only: add on top without rewriting existing content unless requested):

### 3.1 Operating Header (required)
- Mission:
- Use when:
- Hard constraints (cannot override):
- Inputs / Dependencies (links):
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
- Failure modes (top 3):
- Non-goals:

### 3.2 Procedure (required)
A checklist of exact steps to apply this module (5–12 steps):
1) Preconditions (readiness/health/data-quality/unknown-mode, etc.)
2) Checks (what to inspect)
3) Decision (PASS/BLOCK/THROTTLE)
4) Action (enter/manage/exit)
5) Abort conditions (when to stop / go Unknown-Mode)
6) Post-action note (what to record)

### 3.3 Anti-duplication rule
- If a definition exists canonically elsewhere, link it; do not copy it.
- If linking would make the file unusable, include a short local “definition stub” and link to the canonical definition.

## 4.0 Trading Data Rule (Trading-only; not engineering)
- Data is treated as a trading input, not an integration project.
- We only define:
  - what data is required/optional,
  - how to validate it (quality gates),
  - how decisions fail-safe when data is missing.
- If required data is missing or stale → BLOCK/THROTTLE entries; exits allowed.

## 5.0 QA Gates (Before marking a file DONE)
- Header present and accurate (Mission/Use/Constraints/Procedure).
- Definitions consistent with glossary; no terminology drift.
- No weakening of invariants or precedence ladder.
- No new numeric thresholds unless already present locally.
- Any uncertainty is tagged `[INBOX-REVIEW]` and defaults strict.
- Any irreconcilable conflict is tagged `[REVIEW-CONFLICT]` and blocks entries by default.

## 6.0 Batch Rules (How we work file-by-file)
- Touch 1–4 files per patch.
- Integrate only; avoid refactors unless explicitly requested.
- Each completed file must be directly usable by a reader without needing hidden context.
