# Heist Split Plan

Purpose: create 3 independent route docs (same end goal, different paths) while maintaining one authoritative owner per topic.

## Ownership Matrix (authoritative owner in repo)
- Strategy primary spec owner: `Docs/Aegis_Trade_micro.md`
- Execution/system primary spec owner: `Docs/Aegis_API_bot.md`
- Binance/venue primary spec owner: `Docs/Aegis_Heist_Binance.md`
- Heist index/stub: `Docs/Heist_strategy_doc.md` will point to the above (reference/index once split).

## Mapping Table (old Heist H2 → target doc(s) + target headings)
| Old Heist H2                         | Target Doc(s)                         | Target Section(s)                                      |
|--------------------------------------|---------------------------------------|--------------------------------------------------------|
| Strategy_Rules                       | Aegis_Trade_micro                     | Strategy (overview/constraints)                        |
| Strategy_Idea                        | Aegis_Trade_micro                     | Strategy (core idea)                                   |
| Confirmation Rules                   | Aegis_Trade_micro                     | Strategy → Confirmations                               |
| Regimes                              | Aegis_Trade_micro                     | Strategy → Regimes                                     |
| Indicators                           | Aegis_Trade_micro                     | Strategy → Indicators                                  |
| TFs_information                      | Aegis_Trade_micro                     | Strategy → Timeframes/TF roles                         |
| Risk_management                      | Aegis_Trade_micro; Aegis_API_bot      | Risk management                                        |
| Promotion / State Constraints        | Aegis_Trade_micro; Aegis_API_bot      | Symbol eligibility / Promotion                         |
| Machine_learning                     | Aegis_Trade_micro (reference)         | Strategy → ML/optional                                 |
| Data/Storage                         | Aegis_API_bot                         | Data required + collection plan                        |
| REST-Eligibility                     | Aegis_Heist_Binance                   | Symbol eligibility                                     |
| Stream Eligibility                   | Aegis_Heist_Binance                   | Symbol eligibility                                     |
| Execution & Order Handling           | Aegis_API_bot                         | Execution & order handling                             |
| OrderEngine                          | Aegis_API_bot                         | Execution & order handling                             |
| Operational Reliability & Replayability | Aegis_API_bot; Aegis_Heist_Binance  | Reliability & replayability                            |
| Monitoring/Kill-switch/Alerts        | Aegis_API_bot; Aegis_Heist_Binance    | Reliability & replayability                            |
| WS_Depth_Toolkit (external)          | Aegis_Heist_Binance                   | Symbol eligibility → Stream Eligibility                |

## Standalone Duplication Policy (MIRROR copies)
- One authoritative owner per rule/topic (as listed above).
- Other route docs may include **MIRROR COPY (for standalone use)** blocks solely for standalone completeness.
- If a conflict exists, the authoritative owner wins; MIRROR blocks must defer.

## Checklist (next steps)
- [ ] Populate Core Invariants (CI_v1.0) identically in all three route docs.
- [ ] Fill Aegis_Trade_micro with strategy-first content (entries/exits/regimes/indicators/risk).
- [ ] Fill Aegis_API_bot with execution-first content (architecture, order handling, strategy plugin, default strategy).
- [ ] Fill Aegis_Heist_Binance with venue-first content (REST/WS eligibility, depth toolkit integration, loop).
- [ ] Convert Heist_strategy_doc.md into index/stub with preserved headings and route links.
