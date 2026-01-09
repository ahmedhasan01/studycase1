Documentation Rules
===================

Canonical Sources
- Maintain one authoritative doc per subsystem; avoid duplicates. Cross-link rather than copy content.

Sync with Behavior
- Update docs when behavior or interfaces change; flag and resolve any code vs doc conflicts.

Secrets & Examples
- Never include real secrets; use placeholders.  
- Provide runnable/clear examples where helpful; note prerequisites and env vars needed.

Change Logs
- Summarize changes and impacts in docs when relevant (what changed, why, tests run).  
- Keep runbooks/checklists current for operators.

Folder docs
- Each folder should have a single-source doc (md) listing purpose, key py files, entrypoints, and interfaces.  
- Update that folder doc whenever code in the folder changes.

Fingerprint/identity
- Include software name/fingerprint where appropriate (e.g., Aegis_Heist) in documentation headers or metadata (no secrets).
