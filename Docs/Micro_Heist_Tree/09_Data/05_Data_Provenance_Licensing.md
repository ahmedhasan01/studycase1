# Data Provenance and Licensing (Trading-only)

## Operating Header
  - Mission: Keep data usage legal and traceable without turning this repo into a dataset dump.
  - Use when: You want to use API/Excel/CSV data and need to know what can be stored in-repo vs pointers only.
  - Hard constraints (cannot override):
    - No secrets/tokens in repo (keys live in env vars outside repo).
    - No restricted raw datasets committed; store pointers/metadata only when required.
    - Trading-only: provenance supports safe usage, not distribution.
  - Inputs / Dependencies (links):
    - `09_Data/01_Trading_Data_Inputs.md`
    - `99_Appendix/*` (if you maintain source notes there)
  - Outputs / Decisions (PASS/BLOCK/THROTTLE/EXIT):
    - Output = rules for storing/pointing to datasets and documenting sources.
  - Failure modes (top 3):
    - Accidentally committing licensed data.
    - Untraceable datasets leading to unverifiable results.
    - Keys/tokens leaking in docs or logs.
  - Non-goals:
    - Not a legal opinion; this is governance and hygiene.

## Procedure
  1) For any dataset used in validation/replay, record:
    - source name (provider or file origin),
    - instrument(s),
    - timeframe(s),
    - date range,
    - timezone,
    - any transformations applied.
  2) If licensing forbids redistribution:
    - store only a pointer (how to obtain) + metadata; do NOT commit the raw file.
  3) Never store API keys in markdown; use environment variables.
  4) If unsure about license → treat as restricted and store pointers only.

## Storage rules
  - Allowed in repo:
    - schemas/templates (column names, sample empty templates),
    - metadata manifests (no raw prices if restricted),
    - small synthetic examples (non-real).
  - Not allowed in repo (by default):
    - full raw market datasets from paid/restricted sources,
    - any file containing secrets/tokens.
