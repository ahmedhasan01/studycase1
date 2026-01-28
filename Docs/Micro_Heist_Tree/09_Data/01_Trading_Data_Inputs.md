# Trading Data Inputs (Minimum Viable)

## Operating Header
  - Mission: Define what market data inputs are REQUIRED vs OPTIONAL to run this trading universe (all styles; focus micro trade).
  - Use when: You want to connect any data source (API export / Excel / CSV) and need to know what inputs the trading decisions require.
  - Hard constraints (cannot override):
    - This is trading-only: no integration/adapter engineering.
    - Missing REQUIRED inputs → BLOCK/THROTTLE entries; exits allowed.
    - No numeric thresholds unless already present locally; otherwise use `[INBOX-REVIEW]`.
  - Inputs / Dependencies (links):
    - `00_AI_RULES_MICRO_HEIST.md` (precedence + strict defaults)
    - `06_Readiness_and_Health_Gates.md` (concept: block entries / exits allowed)
    - `09_Data/02_Data_Quality_Gates.md` (data readiness)
  - Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
    - Output = a checklist of required inputs and strict fallbacks.
  - Failure modes (top 3):
    - Trading on stale/misaligned timestamps.
    - Missing spread/liquidity proxies ignored.
    - Data gaps treated as real signals.
  - Non-goals:
    - Not a vendor/API guide.
    - Not storage architecture.

## Procedure
  1) Decide the trading style you are running (micro trade default).
  2) Ensure you can supply the REQUIRED inputs (below).
  3) If any REQUIRED input is missing → treat as Data-Quality FAIL (BLOCK/THROTTLE entries).
  4) If OPTIONAL inputs are missing → proceed, but keep behavior stricter (more filtering, fewer trades).
  5) Normalize timestamps and symbol mapping (must be consistent across all inputs).
  6) Run `09_Data/02_Data_Quality_Gates.md` before allowing any entries.

## Required inputs (minimum viable)
  - Time-aligned candles for the active timeframe(s) (OHLCV).
  - Reliable timestamps (consistent timezone; monotonic).
  - Symbol mapping (one symbol = one instrument, no ambiguity).

## Optional inputs (improves safety)
  - Bid/ask or spread proxy (if not available, use conservative proxy and tighten behavior).
  - Volume/turnover proxies (if absent, treat liquidity as uncertain).
  - Session/calendar context (market open/close regimes).
  - Event/news flags (if absent, be stricter during suspected shocks).

## Strict fallback rules (when optional inputs missing)
  - If spread is unknown → tighten confirmation, reduce frequency, and prefer “no entry” under uncertainty.
  - If liquidity is unknown → treat as higher slippage risk; throttle entries.
  - If session context unknown → avoid aggressive behavior near opens/closes; default strict.
