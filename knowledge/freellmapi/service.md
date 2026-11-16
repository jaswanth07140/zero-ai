---
domain: freellmapi/service
title: Service
status: seeded
source: systemctl --user, curl 127.0.0.1:3001
updated: 2026-11-15
---

# FreeLLMAPI router — Service

## Facts

- 2026-11-15 — Runs as a systemd user unit bound to 127.0.0.1:3001, Restart=on-failure, linger enabled so it survives logout.
- 2026-11-15 — Health checks: GET / returns 200, GET /v1/models returns 200 with a bearer key and 401 without one.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
