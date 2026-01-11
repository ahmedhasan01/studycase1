# Rules (Canonical)

> Canonical formatting & documentation rules for this repo.
> This file is the source of truth for numbering, markers, and structure.

## 1) Structure
- Use deterministic, spec-like writing.
- Prefer stable headings and consistent ordering.
- Keep changes minimal and avoid broad reformat unless explicitly requested.

## 2) Numbering
- Use hierarchical numbering: 1.0, 1.1, 1.1.1 …
- Do not renumber unrelated sections.
- If inserting a new section, choose the smallest change that preserves ordering.

## 3) Canonical markers
- Use explicit markers when needed:
  - CANONICAL START
  - CANONICAL END
- Do not duplicate canonical blocks.
- If common content appears in multiple places, prefer a single canonical block + references.

## 4) Dedupe & Commonization
- Avoid meaning-duplication even with different wording.
- Prefer “Shared/Common” blocks for repeated rules and constants.
- When consolidating, preserve meaning (0% information loss).

## 5) Change discipline
- No invention of new rules/thresholds/values unless explicitly agreed.
- Keep “why” short; keep “what changed” precise.
- If a change is risky, add a short reason-code note.

## 6) Output expectations (when generating patches)
- Patch must be unified diff (diff --git ...).
- Exact agreed edits only.
