# Data → Decision Wiring (By Module)

## Operating Header
  - Mission: List which trading modules require which data inputs, and define strict fallbacks when inputs are missing.
  - Use when: You are wiring your charts/tools/data feed to the rules and want to know what each module depends on.
  - Hard constraints (cannot override):
    - Missing required input for a module → that module must BLOCK/THROTTLE entries.
    - Fallbacks must always be stricter, never looser.
  - Inputs / Dependencies (links):
    - `09_Data/01_Trading_Data_Inputs.md`
    - `09_Data/02_Data_Quality_Gates.md`
    - `00_AI_RULES_MICRO_HEIST.md` (precedence)
  - Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
    - Output = dependency map + strict fallback table.
  - Failure modes (top 3):
    - A module silently assumes an input exists.
    - Two modules use different time bases.
    - Optional inputs treated as required without fallback policy.
  - Non-goals:
    - Not an implementation blueprint.

## Procedure
  1) For each module category below, mark required inputs and optional inputs.
  2) If an input is missing, apply the strict fallback and record why.
  3) Keep this file updated whenever a module starts referencing a new input.

## Module categories (required inputs + strict fallback)
  ### A) Foundations (definitions, invariants)
    - Inputs: none (pure logic)
    - Fallback: N/A

  ### B) Readiness/Health (operational)
    - Required inputs: timestamps/clock integrity; data-quality outcome
    - Fallback: if unknown → BLOCK entries; exits allowed

  ### C) Risk/Frequency
    - Required inputs: none (logic) + data-quality outcome (to allow entries)
    - Fallback: data-quality fail → BLOCK entries

  ### D) Bias/Regime/Router
    - Required inputs: candles for relevant timeframes
    - Optional: volume/spread proxies
    - Fallback: missing timeframe candles → BLOCK entries (or Unknown-Mode → THROTTLE/BLOCK)

  ### E) Setups/Confirmations
    - Required inputs: candles; any indicator prerequisites explicitly stated by the setup
    - Fallback: missing prerequisite → setup not eligible (BLOCK entries for that setup)

  ### F) Trade Management / Playbook
    - Required inputs: current price proxy; candles for management timeframe
    - Fallback: if uncertain → reduce exposure; avoid adds; exits allowed
