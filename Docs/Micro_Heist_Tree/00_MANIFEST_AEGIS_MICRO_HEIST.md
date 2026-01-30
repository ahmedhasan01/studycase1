# Aegis Micro Heist — Manifest (Build Plan Pointer)

## 0.0 Purpose
- This file is a **pointer + constraints** for the build plan.
- The detailed Build Queue / step order is maintained manually and must not be overwritten by automated patches.

## 0.1 Status Legend (optional)
- TODO / DOING / DONE / BLOCKED (project-specific usage)

## 0.2 Global Constraints
- Under uncertainty: default strict (BLOCK/THROTTLE entries); exits/reductions allowed.
- Never weaken invariants or precedence ladder.
- No numeric thresholds unless already present locally; otherwise tag `[INBOX-REVIEW]` inside docs.
- External/online/books are rationale-only (if used), never canon.

## 1.0 The Standard (must be applied to every module)
- Canonical module standard is defined in: `Docs/Micro_Heist_Tree/00_AI_RULES_MICRO_HEIST.md`
- Editing protocol is canonical in:
- EXECUTE_STANDARD ends with a Line-by-line Deep Read Audit (Questions / Missing / Contradictions).
  - `Docs/Micro_Heist_Tree/00_START_HERE_AEGIS_MICRO_HEIST.md` → 1.7A / 1.7B
- Every module MUST have:
  - Operating Header
  - Procedure checklist
  - Canonical links (no duplication)
  - QA pass

## 2.0 Build Queue (Canonical)
**Intentionally not stored here.**
- Keep the authoritative queue in your manual system.
- This file should only point to standards + protocols to avoid accidental overwrites.

## 3.0 Open Items (in-doc tags)
- Use `[INBOX-REVIEW]` for missing definitions/criteria discovered while editing modules.
- Use `[REVIEW-CONFLICT]` for irreconcilable conflicts (default strict).


