# Aegis_heist Telegram Control & Monitor (TCM)

Single source of truth for the Telegram subsystem. Main tree only; `./delete` is reference and not used.

## Telegram Code Map (Files & Responsibilities)
- Admin/Control:
  - `Aegis_heist_TCM/tcm_admin.py` — Admin bot (python-telegram-bot polling). Commands: `start`, `monitor_check`, `pause_all`, `resume_all`. Enforces admin allowlist; enqueues control_commands; monitor_check sends a direct message (emoji + date/time) to monitor chat (no DB insert) and echoes the same message to admin chat.
  - `Aegis_heist_TCM/tcm_common.py` — Shared helpers (credentials load, token getters, admin-id parsing, send wrapper without token leakage, enqueue helpers) using `Storage/tcm_db.py`.
- Monitor:
  - `Aegis_heist_TCM/tcm_monitor.py` — Polls `notifications` (delivered=0), sends via Telegram, marks delivered=1 on success, logs failures.
- Storage helper:
  - `Storage/tcm_db.py` — SQLite helper for `control_commands` and `notifications` (AEGIS_DB_PATH override, default `Aegis_heist_DB.db`), short timeout, ensure_tables, insert/query helpers.
- Pipeline:
  - `control/command_processor.py` — Consumes control_commands (PAUSE/RESUME/KILL/WITHDRAW, etc.), writes notifications; sets status=ERROR on exceptions (unchanged).
- Docs: this file (authoritative).

## Entry Points & Runtime Modes
- Admin bot: `python -m Aegis_heist_TCM.tcm_admin` → polling.
- Monitor bot: `python -m Aegis_heist_TCM.tcm_monitor` → polls notifications and sends.
- Command processing: `control/command_processor.process_pending` (driven by supervisor) consumes control_commands.
- Polling only; no webhooks.

## Env Var Matrix (canonical + legacy)
- Admin token: `TELEGRAM_ADMIN_BOT_TOKEN` (canonical). Fallbacks: `TELEGRAM_BOT_TOKEN`, `AEGIS_TELEGRAM_BOT_TOKEN`.
- Admin allowlist: `TELEGRAM_ADMIN_USER_IDS` (canonical). Fallback: `TELEGRAM_ADMIN_IDS`.
- Monitor: `TELEGRAM_MONITOR_BOT_TOKEN`, `TELEGRAM_MONITOR_CHAT_ID`.
- DB path: `AEGIS_DB_PATH` overrides; default `Aegis_heist_DB.db` via `Storage/tcm_db.py`.
- Credentials file: `AEGIS_CREDENTIALS_PATH` or default `aegis_confedential/aegis_credentials.env` (fallback `secrets/aegis_credentials.env`) loaded by tcm_common before reading envs.

## CONTROL SURFACE (factual)
- `/pause_all` → enqueues PAUSE_ALL (control_commands).
- `/resume_all` → enqueues RESUME_ALL.
- `/monitor_check` → sends a direct monitor_check message (emoji + date/time) to monitor chat (no DB insert) and echoes it to admin chat; admin gets success/failure if monitor send fails.
- Admin gating: TELEGRAM_ADMIN_USER_IDS/TELEGRAM_ADMIN_IDS.
- command_processor (existing) still supports other types (KILL_SWITCH, WITHDRAW, etc.), but this clean build exposes only pause/resume/monitor_check.

## BotFather Command Menu ( /setcommands )
Paste into BotFather for the admin bot:
```
start - Show ready message
monitor_check - Verify monitor delivery
pause_all - Pause all symbols (enqueue PAUSE_ALL)
resume_all - Resume all symbols (enqueue RESUME_ALL)
```
Monitor bot typically needs no BotFather commands.

## MONITORING SURFACE (factual)
- notifications table: tcm_monitor sends messages, marks delivered=1 on success; leaves undelivered on failure (retry next poll).
- Admin read-only is limited in this build; other status/positions/trades handlers are not present in the clean TCM.

## Notifications to Monitor (what gets sent)
- Startup (sent by supervisor): “🚀 Aegis_heist Monitoring started …”
- Shutdown (sent by supervisor): “🛑 Aegis_heist Monitoring stopped … Done with Heisting for Today.”
- /monitor_check from admin: direct message (emoji + date/time) sent to monitor chat; echoed to admin; no DB insert.
- control_processor (existing, unchanged): operational alerts it writes to notifications (e.g., command errors, kill-switch actions) will be sent by the monitor loop.
- Any producer inserting into notifications (level/category/message) will be sent by the monitor bot; delivered flag marks success.

## Commands vs Auto-Send (control vs monitor)
- Admin commands (control surface):
  - `/pause_all` (enqueue PAUSE_ALL)
  - `/resume_all` (enqueue RESUME_ALL)
  - `/monitor_check` (direct message to monitor chat with emoji + date/time; no DB insert; echoed to admin)
- Auto-sent to monitor (no admin input needed):
  - Monitor startup/shutdown messages (from supervisor)
  - Delivery of any notifications rows (from command_processor or other producers)

## End-to-End Flow
Command → enqueue_control_command → control_commands(PENDING) → command_processor.process_pending → state change/notification → tcm_monitor.send_message → delivered flag.  
Monitor_check: send direct message to monitor chat → admin sees same message and gets success/failure if monitor send fails.

## Failure Modes
- Missing tokens/IDs: admin/monitor exit with error log.
- send_message exceptions: logged (no token leakage); returns False; leaves delivered=0.
- Monitor loop errors: logged and retried after short sleep.
- DB path mkdir handled in tcm_db; short timeout on connects.

## Troubleshooting & Error Handling
- Verify env vars or credentials file path; ensure both admin and monitor processes are running.
- If monitor_check fails: check monitor token/chat.
- control_commands errors surface via command_processor (status=ERROR, error_message).

## Testing
- Offline default: `pytest` (tests in `tests/offline/test_tcm_db.py` cover env override, inserts, delivered mark).
- Online opt-in: `pytest -m online` (tests/online/test_tcm_online.py` and `tests/e2e/test_tcm_e2e_monitor_check.py`, plus smoke in `tests/smoke/test_tcm_monitor_check_smoke.py`); requires real TELEGRAM_MONITOR_BOT_TOKEN/CHAT_ID (and admin token/IDs for e2e). You can also run the e2e test alone: `python -m pytest tests/e2e/test_tcm_e2e_monitor_check.py -m online`.

## Improvement Backlog (Telegram-only)
- Add richer admin surface (status/positions/last_trades) with allowlist checks.
- Add chat allowlist for admin bot.
- Add configurable retry/backoff thresholds for monitor and send_message telemetry.
- Add online smoke that drives `/monitor_check` end-to-end with running bots.

## Files
- Admin: `Aegis_heist_TCM/tcm_admin.py`
- Monitor: `Aegis_heist_TCM/tcm_monitor.py`
- Helpers: `Aegis_heist_TCM/tcm_common.py`, `Storage/tcm_db.py`
- Pipeline: `control/command_processor.py` (existing)
- Tests: `tests/offline/test_tcm_db.py`, `tests/online/test_tcm_online.py`, `tests/e2e/test_tcm_e2e_monitor_check.py`, `tests/smoke/test_tcm_monitor_check_smoke.py` (opt-in)
- Docs: `Docs/Aegis_heist_TCM.md` (this file, authoritative)

Report path: `Docs/Aegis_heist_TCM.md` (no duplicates).
