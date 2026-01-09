Control / Notifications Logic
=============================

Control Commands
- Table: control_commands (SQLite). Admin bot enqueues commands (pause/resume); command_processor (supervisor) consumes and applies, updating status/error fields.

Notifications
- Table: notifications (SQLite). Producers insert messages; monitor bot polls undelivered rows, sends, and marks delivered on success. (monitor_check is direct-send and does not use the table.)

Bots
- Admin bot: `Aegis_heist_TCM/tcm_admin.py` (polling). Commands: pause_all/resume_all enqueue control_commands; monitor_check sends a direct message (emoji + date/time) to monitor chat (no DB insert) and echoes the same message to admin chat. Reads credentials from env/secrets; enforces admin allowlist.
- Monitor bot: `Aegis_heist_TCM/tcm_monitor.py` (polling). Sends notifications; uses TELEGRAM_MONITOR_* env vars; polls notifications table.
- Supervisor: `aegis_heist_main/supervisor.py` launches/monitors TCM admin/monitor subprocesses (backoff/restart, clean shutdown); loads credentials once; sends startup/shutdown messages to monitor/admin.

Flows
- Admin command → control_commands (status=PENDING) → command_processor → action + notifications.
- Producer (e.g., supervisor/errors) → notifications → monitor bot → chat (delivered flag).
- monitor_check: direct send to monitor chat; echoed to admin; no DB insert.

Safety
- Admin allowlists enforced in bot; no direct trading side effects from handlers (enqueue-only). Tokens/IDs loaded from env/secrets; no logging of secrets.
- Notifications table drives outbound sends for producers; monitor_check/startup/shutdown are handled outside the table as described.

Docs references
- Docs/Aegis_heist_TCM.md (authoritative Telegram report).
- control/command_processor.py (pipeline consumer).
- Testing layout: offline/online/smoke/e2e under tests/.
