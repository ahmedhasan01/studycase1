# Definitions & Glossary

## Operating Header
  - Mission: Provide canonical definitions used across the micro trading universe (1–20m).
  - Use when: Any term appears in another module (Winning Bias, Edge-positive, Unknown-Mode, etc.).
  - Hard constraints (cannot override):
Numeric thresholds are allowed when explicitly labeled **[LOCAL]** (include units + applicability). If uncertain, tag **[INBOX-REVIEW]** and default strict.
    - Under uncertainty: default strict (BLOCK/THROTTLE entries); exits/reductions allowed.
  - Inputs / Dependencies (links):
    - Docs/Micro_Heist_Tree/01_Foundations/04_Core_Invariants.md
    - Docs/Micro_Heist_Tree/01_Foundations/05_Decision_Glossary.md
  - Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
    - Output = shared vocabulary; enables deterministic gating across modules.
  - Failure modes (top 3):
    - Term drift across files (same word, different meaning).
    - Hidden thresholds introduced without canon.
    - Missing definition treated as “ok to trade”.
  - Non-goals:
    - Not an exhaustive finance dictionary.
    - Not a place to invent thresholds.

## Procedure
  1) When a module uses a term, check this file first.
  2) If the term exists: use it verbatim (link here; do not copy).
  3) When a term is missing or ambiguous: add [INBOX-REVIEW] + default stricter behavior.
  4) If the definition needs numbers/criteria not available locally: tag [INBOX-REVIEW] and default strict.
  5) After edits, scan nearby modules to remove duplicates and replace with links.
  6) Prefer linking canon over copying definitions.
  7) If any conflict is found with Core Invariants: tag [REVIEW-CONFLICT] and keep strict behavior.

## Mini-Index
  - 1.0 Purpose
  - 1.1 Terms
  - 1.2 Open Questions

## 1.0 Purpose
  Provide concise canonical definitions used throughout the micro trading docs.

## 1.1 Terms
  - **Winning Bias**: current favored side (Long or Short) determined by bias system.
  - **Edge-positive**: expected edge exceeds expected friction; if undefined → [INBOX-REVIEW] and treat as not met.
  - **Unknown-Mode**: state when regime/confidence/health unclear; entries blocked or heavily throttled; exits allowed.
  - **Confirmation**: persistence + confirming candle quality + micro hygiene checks on closed bars.
  - **Robustness gating**: readiness/health controls that can block entries; exits/reductions always allowed.
  - **Adaptive Parameters Policy**: governance for allowed adaptive changes; invariants never adapt.
  - **Confirmed flip**: bias change that meets confirmation criteria; triggers reduce/exit first.
  - **Friction**: spread + slippage/impact + fees + adverse selection risk; missing components → [INBOX-REVIEW].
  - **Readiness**: operational + data-quality + operator state; failure blocks entries; exits allowed.

## 1.2 Open Questions
  - [INBOX-REVIEW] Additional terms needing definition (e.g., exact persistence counts, edge metrics).
