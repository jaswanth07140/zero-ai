---
domain: security/secrets
title: Secrets
status: seeded
source: filesystem permission audit, ls -l
updated: 2026-11-16
---

# Security — Secrets

## Facts
- 2026-11-16 — Secrets live outside the repo: freellmapi key at ~/.config/opencode/freellmapi.key (600), GitHub PAT at ~/.config/opencode/gh.token (600), upstream keys encrypted in the freellmapi DB; repos gitignore *.key, *.token, credentials*, *.dat.php, backups/, config.php.

- 2026-11-15 — API keys never enter repositories or chat output; they live in mode-600 files or encrypted database columns.
- 2026-11-15 — A pasted mcp_token URL parameter matched nothing in its claimed source and was treated as burned without being written to disk.
- 2026-11-15 — A GitHub fine-grained PAT lives at ~/.config/opencode/gh.token (600) and is passed to git via http.extraheader, never stored in .git/config.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
