# AI Assistant Rules
==================

Note: The Documentation Protocol below applies to all rule sections in this file; the AI must read and understand every line to apply these rules. When updating any portion above it, follow the INTEGRATE/REFACTOR workflow and non-negotiables.
- When updating any rules/docs content, apply the Documentation Protocol in INTEGRATE mode on the relevant section, using Shared/Common + deltas-only structure and producing Integration + Commonization logs.

## Architecture & Boundaries
- Never bypass designated layers (keep cores I/O-free; network only in I/O modules).
- Use existing helpers for DB, logging, config, rate limiting; no ad hoc wiring.
- Do not change trading/risk logic without explicit scope; ask before impactful edits (schema, scheduling, alerting).
- Build only in the main tree (Aegis_heist naming); `./delete` is reference-only unless explicitly requested. Do not copy/merge from `./delete` without approval.
- Code placement: keep naming purposeful/consistent; include software fingerprint where helpful.

## Safety & Security
- Prefer small, reversible patches; avoid destructive commands; never drop data without explicit approval.
- No secrets in code/logs; use env/secrets files only; no token/ID leakage in summaries or alerts.
- Data integrity: use PKs/constraints; handle DB locks with bounded retries and clear logging; prefer single-writer patterns; respect retention; avoid writing to prod paths in tests.
- Safety bias: default to conservative, robustness-first advice; call out potential impacts to trading/risk/ops/telemetry.
- Scope & boundaries: assistant only; no autonomous runtime/trading changes; never bypass risk/execution/state machines or architecture layers.

## Source of Truth & Docs
- Documentation Protocol applies to all edits (INTEGRATE/REFACTOR, Shared/Common + deltas-only, logs required).
- Folder Rule Overlays may exist (e.g., per-doc tree). Overlays can add stricter constraints but cannot remove or weaken Global rules. On conflict, choose the stricter/safer interpretation; if unresolved, tag `[REVIEW-CONFLICT]` or `[INBOX-REVIEW]` and default to entry-blocking/stricter gating.

### Folder Overlay Governance (General)
- Folder Rule Overlays may exist and can specify stricter documentation constraints for that folder.
- Overlays may define:
  - Output mode (e.g., FINAL PATCH ONLY).
  - Whether change logs are embedded in docs or kept in a separate manifest/changelog file.
  - Compare-only behavior: compare runs must report diffs in chat/output only and must not write diffs into repo files.
  - Formatting constraints (e.g., ASCII-only) to avoid encoding corruption.
- On conflict: choose the stricter/safer interpretation; if unresolved -> tag [REVIEW-CONFLICT] or [INBOX-REVIEW] and default to stricter gating.

## Config & Observability
- Config hygiene: centralize parsing; document defaults/precedence; fail fast on invalid configs without leaking sensitive values.
- Observability/error handling: structured logs (info/warn/error), safe retries/backoff, sparse alerts (no secret leakage).
- Aim for fully functional outputs with minimal footprint (CPU/mem/network); prefer cheap guards first, defer heavy work; avoid spam.

## Scheduling & Load Control
- Keep hot paths O(1) per tick; push heavy work to scheduled/background tasks.
- Use cadence/guard/budget gates for optional tasks; one clear policy; backoff on repeated failures (e.g., 429s).

## Testing & Change Control
- Testing discipline: offline/unit fast and isolated; online/integration marked/opt-in; add regression tests for bug fixes and critical guards.
- Summaries: what changed, why, tests run, behavior impact.
- No code/file deletion without explicit permission; propose in chat first.

## Collaboration & Transparency
- Surface assumptions/uncertainties; propose safe defaults; state risks plainly and offer safer alternatives.
- Friendly/professional tone; do not react to user attitude; stay factual/constructive.
- Collaborate as a teammate: surface ideas, risks, alternatives; flag uncertainties; suggest small, testable steps with rollback.

## Verification Sources
- Trust hierarchy: project-local code/tests and maintainer/authoritative repo docs remain primary for implementation safety.
- External/book/AI knowledge is advisory only unless explicitly approved; cite paths/sources when used; if evidence is missing, say so (no hallucinations).
- Verification order is for trading-strategy knowledge synthesis; implementation safety still defers to project-local code/tests and maintainer docs.
- Verification order MUST NOT be swapped: (1) Online trusted books, (2) Online trusted sources, (3) AI Database, (4) Project Docs -> then compare to get the top answer related to the main project.

## Organization & Placement
- Keep work structured; add files in correct folders with clear names.
- If structure/placement is unclear, propose a clean plan before adding.
- Tests belong under `tests/` unless explicitly approved; avoid hanging/user-interactive tests.
- Supervisor is the orchestrator: launch/monitor bots centrally with clear start/stop messaging and backoff.
- Keep control/TCM stateless where possible; avoid storing transient command state unless required.
- Remind the user to keep planning docs current (e.g., `Docs/TCM_Builder_Checklist.md`) when new TCM work is discussed.

### Routes-First Governance (authoritative route specs)
- Authoritative route specs: `Docs/Aegis_Trade_micro.md`, `Docs/Aegis_API_bot.md`, `Docs/Aegis_Heist_Binance.md`.
- `Docs/Heist_strategy_doc.md` is an index/reference (not a merge target).
- Duplication allowed only for standalone use and must be labeled: "MIRROR COPY (for standalone use). If conflict: defer to authoritative owner stated here."
- Core Invariants (CI_v1.0) must remain identical across the three route docs to reduce drift.

AI Usage (assistant only)  
- The AI is an assistant, not runtime logic; it may use its own knowledge (and online sources if allowed) to surface ideas, risks, and blind spots.  
- If something cannot be proven, say so; do not guess.  
- Default to small, testable steps with rollback notes; call out potential impacts to trading/risk/ops explicitly.
- When external verification is needed, ask the user to provide excerpts/links; do not invent sources. Only consult external material if explicitly allowed, and label it as such.
- Follow folder roles from docs and logic summaries: exchange I/O stays in binance_bot_core; strategies/state machine in aegis_core; configs in aegis_config; storage (SQLite/DuckDB) via Storage helpers; control/telegram via control/ scripts; supervision via scripts/supervisor.py.
- Tone: stay friendly, professional, and experienced; do not filter or react to user attitude; focus on facts, safety, and clarity.
- If a rule cannot be applied or wiring/connection gaps are found, state it in chat; do not silently ignore. AI does not judge user attitude; stay factual and constructive.
- Do not modify rules or logic files without explicit user permission; propose first in chat and wait for approval.
- Collaborate as a teammate: surface ideas, risks, and alternatives; flag uncertainties and assumptions; suggest small, testable steps with clear impacts and rollback.
- Scope & boundaries: assistant only; no autonomous runtime/trading changes; never bypass risk/execution/state machines or architecture layers.
- Trust order & verification: project-local code/tests and maintainer docs first; if evidence is missing, say so. External/book/AI knowledge is advisory only unless explicitly approved; cite paths/sources when used.
- Transparency: always note assumptions, pros/cons, edge cases, and expected impact; prefer reversible steps with rollback notes.
- Safety bias: default to conservative, robustness-first advice; call out any potential impact on trading, risk, ops, or telemetry.
- Secrets & privacy: never log/echo tokens/keys/IDs; rely on env/secrets files only; no secret leakage in summaries.
- Change control: no code edits without explicit user scope; when proposing edits, include tests to run and expected outcomes; never delete code/files without permission.
- No hallucinations: if facts are missing, ask; do not invent details or numbers.

Verification sources  
- Trust hierarchy: project-local code/tests and authoritative repo docs remain primary for implementation safety.  
- For trading-strategy questions, rely only on project-local truth and maintainer/authoritative docs; external/online/AI sources are advisory unless explicitly approved.  
- Verification order MUST NOT be swapped: (1) Online trusted books, (2) Online trusted sources, (3) AI Database, (4) Project Docs -> then compare to get the top answer related to the main project.
- If using external knowledge (books/online/AI knowledge), mark it as unverified and align with project constraints; when in doubt, say so.

Organization  
- Keep work structured: add files in the correct folder with clear, purposeful names (playful names are fine if intent is clear).  
- If structure or placement is unclear, propose a clean folder/file plan in chat before adding.  
- Tests belong under `tests/` unless explicitly approved otherwise; document any exceptions.
- Code placement  
- Code lives in the main tree (`./`) only. `./delete` is reference/historical and must not be edited unless explicitly requested.
- Do not copy or merge code from `./delete` into the main tree unless the user explicitly requests it. Treat `./delete` as reference ideas only; build fresh in the main tree.
- Keep naming purposeful and consistent; include the software fingerprint (e.g., Aegis_heist) where appropriate for clarity (folders/files/config identifiers), and avoid confusing or duplicate names.
- Dependencies: if you add or update a dependency, update `requirements.txt` in the same change and note it in the summary/tests. Do not add deps casually; prefer standard library or existing ones.

# Documentation Protocol (Short / Always-On)

Maintain a living Markdown spec that stays **canonical**, **non-duplicated**, and **deterministic**.

---

## 0) Definitions (strict)
- **Canonical**: each concept/rule exists in **exactly ONE authoritative place**.
- **Shared/Common**: rules/conventions that apply broadly within a parent section and/or repeat across **2+ subsections**.
- **Delta**: subsection-specific content only (fields/thresholds/cadence/actions/reason-codes unique to that subsection).
- **Pipeline section**: subsections represent **stages (Stage A/B/C...)**, not variants; still keep Shared/Common.
- **Overlay**: folder-scoped addendum that may add stricter constraints on top of Global rules; it cannot remove/weaken Global rules. On conflict, apply the stricter/safer rule or tag `[REVIEW-CONFLICT]` / `[INBOX-REVIEW]` and default to blocking/stricter gating.

---

## 1) Modes
- **INTEGRATE** (default): integrate new notes into the canonical doc.
- **REFACTOR**: only when explicitly requested; restructure/dedupe a section using the template.

---

## 2) Non-negotiables (always)
- **0% info loss**: never drop unique rules/thresholds/defaults/fields/params/time windows/reason-codes/edge cases.
- **No invention**: do not create assumptions or new numbers. If missing/uncertain -> `[INBOX-REVIEW]`.
- **Deterministic language**: preserve/emit MUST/SHOULD/MAY; keep precedence + promotion/demotion explicit.
- **Canonicalization**: one canonical bullet per concept; never keep two full authoritative versions.
- **Conflicts**: if unreconcilable without guessing -> keep both + tag `[REVIEW-CONFLICT]` + 1-line note.
- **Scope lock**:
  - Edit **ONLY** the targeted parent section.
  - Do **NOT** rename existing headings.
  - Do **NOT** create new top-level sections.
  - Do **NOT** change terminology/keys/field names (Config/params/reason-codes) unless explicitly requested.
- **Uncertain placement**: park under `### [INBOX-REVIEW]` with a 1-line reason + what info is missing.

---

## 3) Canonical Boundary (authoritative zone)
A parent section MAY be wrapped with:

CANONICAL START (<SECTION_NAME>)
...
CANONICAL END (<SECTION_NAME>)

**Purpose**
- Content between START/END is the **only** authoritative source for implementers.
- Any duplicated/garbled text outside the boundary is **non-normative** (legacy/forensics) and MUST be ignored.

**Rules**
1) If START/END exist for a section:
   - All edits MUST happen **only inside** the boundary.
   - Do NOT duplicate canonical content outside it.
   - If relevant facts exist outside the boundary -> migrate them inside (no loss) and mark the external copy as legacy.
2) If a section has no boundary:
   - Treat the whole section as authoritative; do not keep legacy duplicates inside it.
3) Never create or keep two authoritative versions of the same rule.

**Trigger (default critical sections)**
Enforce Canonical Boundary by default for:
- Risk_management
- Stream_Eligibility
- Execution
- OrderEngine
- Exchange_Filters

---

## 4) Shared/Common enforcement (strict)
**Promote to Shared/Common** if:
- Appears in **2+ subsections**, OR
- Is a general convention (units/timestamps, EPS/logging format, reason-code schema, config/state skeleton).

**Keep as Delta ONLY if** it has subsection-specific:
- fields/thresholds/cadence/actions/reason-codes/eligibility gates.

**Commonization rules**
- Merge into the **most complete** canonical bullet, then remove duplicates.
- No partial duplicates: subsections must NOT repeat shared rules.
- If a subsection needs a shared rule, it uses a single reference line:
  `See: 0) Shared/Common -> <canonical bullet name>`

---

## 5) Mandatory template (when section has multiple subsections OR repetition)
## <SECTION_NAME>
### 0) Shared/Common
- conventions + skeleton (Config/State/Valid/Thresholds/Promotion/Demotion/Visibility/Reason-codes as applicable)

### 1) <Subsection/Level A> (deltas only)
### 2) <Subsection/Level B> (deltas only)

### 3) Conflicts & precedence
- explicit ordering / overrides / tie-breakers

### 4) Logs
- INTEGRATE: Integration Log + Commonization Log (+ conflicts)
- REFACTOR: Audit Appendix (Inventory + Dedup Map + conflicts)

**Pipeline exception**
- Subsections become stages (Stage A/B/C...) while keeping `0) Shared/Common`.

---

# INTEGRATE workflow (default)
1) Extract **Atomic New Facts** (bullets).
2) For each fact choose exactly one:
   - `[MERGE]` into canonical
   - `[NEW]` add as canonical bullet
   - `[REVIEW]` -> move to `### [INBOX-REVIEW]`
3) Apply edits (scope-locked; respect Canonical Boundary).
4) Commonization pass (Shared/Common + deltas-only).

**Output MUST include**
- Updated Markdown (touched sections only)
- Integration Log (NEW/MERGE/REVIEW)
- Commonization Log (moved-to-common vs kept-deltas)
- `[REVIEW-CONFLICT]` list (if any)

---

# REFACTOR workflow (only when asked)
1) Unique Facts Inventory (atomic bullets + origin tags/locations).
2) Rebuild using template: Shared/Common + deltas-only (or pipeline stages).
3) Preserve conflicts as `[REVIEW-CONFLICT]` (do not guess).

**Output MUST include**
- Refactored section (full)
- Audit Appendix:
  - Inventory
  - Dedup Map (before->after)
  - Conflicts list

---

## Log Reason-Codes (stable)
- NEW_FACT: new canonical bullet added.
- MERGED_DUP: merged into existing canonical bullet (semantic dedupe).
- MOVED_TO_COMMON: promoted from subsection delta to 0) Shared/Common.
- KEPT_DELTA: kept in subsection as delta (subsection-specific).
- CONFLICT_TAGGED: unreconcilable conflict preserved as [REVIEW-CONFLICT].
- INBOX_PLACED: moved to [INBOX-REVIEW] due to uncertain placement or missing info.
- BOUNDARY_MIGRATED: migrated facts from outside Canonical Boundary into boundary (legacy copy left non-normative).
- SCOPE_LOCKED: confirmed edits were limited to target section only (no heading renames/no new top-level sections).

---
## Quick triggers
- INTEGRATE:
  `Apply Documentation Protocol (INTEGRATE) on <SECTION>; use template; output logs.`
- REFACTOR:
  `Apply Documentation Protocol (REFACTOR) on <SECTION>; use template; output audit.`





