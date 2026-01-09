Control / Notifications Rules
============================

Control Surface
- Admin actions must enqueue into control_commands or notifications; no direct trading or state mutations from handlers.
- Enforce admin allowlists; no hard-coded tokens/IDs; reject unauthorized requests.

Bots & Separation
- Keep admin bot (commands) and monitor bot (notifications) distinct; do not blend responsibilities.
- Do not leak tokens/IDs in logs; load credentials from env/secrets files only.
- Reuse canonical env vars for Telegram: admin (`TELEGRAM_ADMIN_BOT_TOKEN`, `TELEGRAM_ADMIN_USER_IDS`/`TELEGRAM_ADMIN_IDS`), monitor (`TELEGRAM_MONITOR_BOT_TOKEN`, `TELEGRAM_MONITOR_CHAT_ID`). Do not invent new names; keep admin vs monitor separate.
- Supervisor owns lifecycle: launch/monitor admin and monitor bots as subprocesses (with backoff/restart) instead of ad-hoc launches inside bots.
- Secrets belong in env/.env/secrets paths (e.g., `AEGIS_CREDENTIALS_PATH` pointing to a non-committed folder like `aegis_confedential/aegis_credentials.env`); never commit real tokens/IDs.

Notifications
- Use notifications table + monitor for outbound messages; apply thresholds/cooldowns to avoid spam.
- Log deliveries/failures clearly; mark delivered only on success; retry responsibly.
- Maintain a clear split: commands are requested via admin bot; outbound notifications (startup/shutdown, monitor_check, processor alerts) are auto-sent by monitor when rows appear in the notifications table.

Safety
- No kill-switch or state-changing actions without existing processing pipelines and checks.  
- Avoid adding new command types without wiring into processors and safeguards.
