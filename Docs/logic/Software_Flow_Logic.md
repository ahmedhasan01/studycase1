Software Flow Logic (Doc-Derived Summary)
=========================================
Source docs: docs/AEGIS_OVERVIEW_V1.md, docs/FLOW.md, docs/runtime_and_supervisor.md, docs/storage.md, docs/aegis_core.md, docs/STRATEGY_PIPELINE.md, docs/control_and_telegram.md, docs/TELEGRAM_AND_CONTROL.md, docs/HEALTH.md, docs/risk_and_execution.md, docs/WIRING_SYSTEM.md, docs/WIRING_CHECKLIST.md.

End-to-End Flow (per docs)
1) Discovery & Wallet: exchangeInfo cached; wallet_sync derives quote assets (always include USDT).
2) Ranking/Tradable: Quotes/ranking builds per-quote shards; tradable_monitor applies spread/depth gates + hysteresis → LIVE_COLD/HOT candidates.
3) Promotion/Backfill: Promotion queue backfills TFs (big/small) for new tradables; ready_for_hot emitted when history available.
4) Persistence: Big TFs persisted at candle close (15m/30m/1h). Mid-bar noted in docs as “not used for big TFs” (outdated vs current code).
5) Signals/Regimes: Regime classification per TF; strategies (mean-rev/momentum/range) compute decisions from ring buffers/persisted bars.
6) Risk/Execution: RiskManager checks caps/cooldowns; OrderEngine sizes/orders via TradingClient (paper/live); journals orders/positions/trades in SQLite.
7) Control/Telemetry: Admin bot enqueues control_commands; command_processor applies; notifications table feeds monitor bot for Telegram; health metrics recorded via HealthManager.
8) Maintenance: Purge_old/vacuum at PURGE_UTC; gap repair/backfill on coverage gaps; heavy_tasks watchdog (if used); run_status/metrics snapshots.

Docs vs code notes
- Docs claim no mid-bar for big TFs (FLOW.md step 6); current code has optional mid-bar REST for 15m/30m/1h. Code is authoritative; doc is outdated on this point.
- Quiet hours removed in code; not present in docs.

Open items to confirm when coding
- Heavy_tasks consumer usage.
- Mid-bar budgeting/cooldowns (none documented).
- Telegram alert thresholds (not documented as unified).
