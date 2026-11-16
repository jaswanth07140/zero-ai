---
domain: freellmapi/keys
title: Keys
status: seeded
source: systemctl --user, curl 127.0.0.1:3001
updated: 2026-11-15
---

# FreeLLMAPI router — Keys

## Facts

- 2026-11-15 — The unified key is stored at ~/.config/opencode/freellmapi.key (mode 600, no trailing newline) and referenced via {file:...}.
- 2026-11-15 — Upstream provider keys are entered in the dashboard and stored encrypted in the api_keys table (encrypted_key/iv/auth_tag).

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
