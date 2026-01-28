# Runtime Runbook (One Page) -- DAILY USE

## What this is
  - A condensed operating flow for day-to-day use (1-20m).
  - It does NOT override canonical modules.
  - If any conflict appears: follow `00_START_HERE_AEGIS_MICRO_HEIST.md` reading order and the canonical modules under `Docs/Micro_Heist_Tree/`.

## Precedence reminder (tighten-only)
  - Not ready / health fail -> BLOCK entries; exits allowed.
  - Shock/Dislocation or route_mode=AVOID -> BLOCK entries; exits allowed.
  - route_mode=UNKNOWN or bias_conflict_flag=TRUE -> BLOCK (default) or strict THROTTLE only if explicitly documented; exits allowed.
  - entry_policy=BLOCK -> BLOCK entries regardless of anything else.

## Runtime Flow (do in order)

  ### 1) Preflight: Readiness/Health
    - Source: `Docs/Micro_Heist_Tree/08_Operational_Robustness/01_Readiness_and_Health_Gates.md`
    - If NOT PASS -> no new entries. Manage/reduce/exit only.

  ### 2) Winning Bias (priority side + flip state)
    - Source: `Docs/Micro_Heist_Tree/03_Bias_System/02_Priority_Biased_Side.md`
    - Record:
      - winning_bias_side in {LONG, SHORT, NEUTRAL}
      - winning_bias_strength in {STRONG, MODERATE, WEAK, NEUTRAL}
      - flip_state in {NONE, CANDIDATE, CONFIRMED}
      - bias_conflict_flag (TRUE/FALSE)
    - If flip_state=CONFIRMED -> reduce/exit current exposure FIRST.

  ### 3) Regime -> Router (route_mode + entry_policy)
    - Sources:
      - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/01_Regime_Taxonomy.md`
      - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/02_Router_Eligibility_Policy.md`
      - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md`
    - Router outputs (contract):
      - route_mode in {TREND, RANGE, BREAKOUT, MEAN_REV, AVOID, UNKNOWN}
      - entry_policy in {ALLOW, THROTTLE, BLOCK}
    - If entry_policy=BLOCK -> no entries.

  ### 4) Pick ONE setup family from Setup Menu
    - Source: `Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md`
    - Allowed families:
      - MEAN_REV -> MR-* only
      - TREND -> TR/MO-* only (as defined)
      - BREAKOUT -> BO/MO-* only
      - RANGE -> RG/MR-* only if explicitly allowed

  ### 5) Confirmations (closed bars + persistence + micro hygiene)
    - Source: `Docs/Micro_Heist_Tree/05_Setups/05_Confirmation_Gates.md`
    - If unclear -> default stricter; no entry.

  ### 6) Risk + Frequency (max trades, cooldowns)
    - Source: `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/03_Max_Trades_Under_Winning_Bias.md`
    - Caps NEVER override readiness/router blocking.

  ### 7) Execute + Manage
    - Source: `Docs/Micro_Heist_Tree/10_Playbook/01_Micro_Trade_Playbook.md`
    - Reduce-first when conditions degrade.
    - Exits always allowed.

## Quick emergency defaults
  - If anything becomes ambiguous/degraded -> tighten: THROTTLE or BLOCK entries; manage/reduce/exit only.
  - If repeated flip-flops -> treat as UNKNOWN and block entries by default.

## Notes
  - This file is an operational shortcut. Canonical truth lives in the modules.
