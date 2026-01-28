# Runtime Checklists (Pocket)

## A) Preflight Checklist (must pass)
    - [ ] Readiness/Health PASS (else BLOCK entries; exits allowed)
    - [ ] Data quality OK (no missing/stale critical inputs)
    - [ ] Micro sanity OK (spread/impact not degraded)
    - [ ] No Shock/Dislocation active

## B) Bias Checklist
    - [ ] winning_bias_side chosen (LONG/SHORT/NEUTRAL)
    - [ ] winning_bias_strength chosen (STRONG/MODERATE/WEAK/NEUTRAL)
    - [ ] flip_state recorded (NONE/CANDIDATE/CONFIRMED)
    - [ ] bias_conflict_flag = FALSE (if TRUE -> treat as not tradeable for entries)
    - [ ] If flip_state=CONFIRMED -> reduce/exit FIRST

## C) Router Checklist
    - [ ] route_mode set (TREND/RANGE/BREAKOUT/MEAN_REV/AVOID/UNKNOWN)
    - [ ] entry_policy set (ALLOW/THROTTLE/BLOCK)
    - [ ] entry_policy != BLOCK (else no entries)
    - [ ] route_mode not AVOID/UNKNOWN (default: block entries; exits allowed)

## D) Setup Checklist (choose ONE family)
    - [ ] Setup family allowed by route_mode (Setup Menu)
    - [ ] No counter-bias entry unless explicit documented exception exists
    - [ ] No counter-regime entry by default

## E) Confirmations Checklist
    - [ ] Closed-bar confirmation (unless explicitly allowed)
    - [ ] Persistence/stability present (no one-tick signals)
    - [ ] Micro hygiene stable
    - [ ] If unclear -> [INBOX-REVIEW] and default stricter (no entry)

## F) Risk/Frequency Checklist
    - [ ] Caps/cooldowns pass
    - [ ] entry_policy=THROTTLE -> tighten frequency/size (never loosen)
    - [ ] If conditions worsen -> reduce/exit first

## References
    - StartHere: `00_START_HERE_AEGIS_MICRO_HEIST.md`
    - Playbook: `Docs/Micro_Heist_Tree/10_Playbook/01_Micro_Trade_Playbook.md`
