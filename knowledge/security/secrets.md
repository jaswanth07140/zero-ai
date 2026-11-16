---
domain: security/secrets
title: Secrets
status: seeded
updated: 2026-11-15
---

# Security — Secrets

## Facts

- 2026-11-15 — API keys never enter repositories or chat output; they live in mode-600 files or encrypted database columns.
- 2026-11-15 — A pasted mcp_token URL parameter matched nothing in its claimed source and was treated as burned without being written to disk.
- 2026-11-15 — A GitHub fine-grained PAT lives at ~/.config/opencode/gh.token (600) and is passed to git via http.extraheader, never stored in .git/config.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
