# Core Topics (Fixed)

## Mini-Index
    - 1.0 Purpose
    - 1.1 Rules
    - 1.2 Fixed Core Topics (verbatim headers)
    - 1.3 How modules use Core Topics
    - 1.4 Change protocol

## 1.0 Purpose
    - Provide a single canonical list of fixed Core Topics for Aegis Micro Heist (1–20m). No venue assumptions; no numeric thresholds.

## 1.1 Rules
    - These headers are FIXED and MUST be used verbatim anywhere they appear.
    - If a topic is added later, it MUST be added here first, then referenced everywhere else.
    - Other files MUST reference this list; do NOT duplicate the list content elsewhere.

## 1.2 Fixed Core Topics (verbatim headers)
    1) Microstructure & friction
    2) Liquidity fragility in stress
    3) Regime switching / persistence & transitions
    4) Volatility clustering / expansion vs compression
    5) Shock/dislocation overrides

## 1.3 How modules use Core Topics
    - Core Invariants + Playbook reference these topics for robustness gates; no new invariants are created here.
    - Regime/Router modules align behavior to “Regime switching / persistence & transitions” and “Volatility clustering / expansion vs compression.”
    - Confirmation/Edge gates consider “Microstructure & friction” and “Liquidity fragility in stress” when tightening.
    - Shock handling references “Shock/dislocation overrides” for stand-down behavior.
    - Trusted Online Pack structures any external rationale by these same headers (general/stable; rationale-only).

## 1.4 Change protocol
    - When updating Core Topics: update ONLY this file, the Trusted Online Pack structure headers, and optionally the Index row.
    - Any other file MUST reference this file; do NOT copy the list.
