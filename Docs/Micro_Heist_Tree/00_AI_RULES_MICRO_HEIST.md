# AI Rules Overlay — Aegis Micro Heist (File-by-File Build Universe)

## 0.0 Purpose
- Folder-scoped overlay to `Docs/rules/AI_Rules.md` for `Docs/Micro_Heist_Tree/`.
- Goal: every file must be immediately understandable and directly applicable as an operating module.
- Default safety: under uncertainty or missing info → become stricter (BLOCK/THROTTLE entries); exits/reductions always allowed.
- If unresolved conflict → tag `[REVIEW-CONFLICT]` and DO NOT guess.
- If missing definitions/criteria → tag `[INBOX-REVIEW]` and default strict.

## 0.1 Run Modes (Comparison Pipelines)
- MODE 1 (LOCAL + AI_DB):
  - Consult local project docs + AI Trusted DB.
  - Produce a single final patch (best result), no per-source patch notes in output.
- MODE 2 (LOCAL + ONLINE + AI_DB):
  - Consult local project docs + online trusted books/sources + AI Trusted DB.
  - External is rationale-only; local canonical rules win.
  - Produce a single final patch, no per-source patch notes in output.

## 1.0 Non-Negotiables (INVARIANTS)
- Long/Short only; no venue types/names.
- Reduce/Exit invariant: Long reduces/exits Short; Short reduces/exits Long.
- Reduce-first doctrine: reduce/exit first, then consider new exposure.
- Confirmed Winning Bias flip → MUST reduce/exit current exposure before any new aligned exposure.
- Robustness gating: if readiness/health/quality is degraded, block new entries; exits allowed.
- Unknown-Mode: if regime is unclear or conflicts persist, entries blocked or heavily throttled; exits allowed.
- Minimal regime taxonomy: Trend, Range, Chop/Noise, High-Vol Expansion, Low-Vol Compression, Shock/Dislocation.

## 2.0 Precedence Ladder (Always)
1) Operational Robustness (health/readiness/shock) — may veto entries.
2) Core Invariants (Section 1.0).
3) Confirmed flip exit mandate.
4) Winning Bias priority + bias strength tier behavior.
5) Regime & Router eligibility policy.
6) Confirmation gates.
7) Setup definitions.
8) Frequency fine-tuning (adaptive, tighten-only).

## 3.0 Canonical vs Advisory
- Canonical rules live in ONE place only (single source of truth).
- Advisory content (books/online) is rationale-only and must be labeled as such.
- Do NOT introduce numeric thresholds unless already present locally.
- If external conflicts with invariants/robustness gating → discard external.

## 4.0 Mandatory File Standard (Every `.md` module)
Every file MUST start with the following header (INTEGRATE-only: add on top without rewriting existing content unless requested):

### 4.1 Operating Header (required)
- Mission:
- Use when:
- Hard constraints (cannot override):
- Inputs / Dependencies (links):
- Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
- Failure modes (top 3):
- Non-goals:

### 4.2 Procedure (required)
A checklist of exact steps to apply this module (5–12 steps):
1) Preconditions (readiness/health, unknown-mode, etc.)
2) Checks (what to inspect)
3) Decision (PASS/BLOCK/THROTTLE)
4) Action (enter/manage/exit)
5) Abort conditions (when to stop / go Unknown-Mode)
6) Post-action note (what to record)

### 4.3 Anti-duplication rule
- If a definition exists canonically elsewhere, link it; do not copy it.
- If linking would make the file unusable, include a short local “definition stub” and link to the canonical definition.

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
