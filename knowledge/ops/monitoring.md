---
domain: ops/monitoring
title: Monitoring
status: seeded
source: journalctl --user -u freellmapi
updated: 2026-11-15
---

# Operations — Monitoring

## Facts

- 2026-11-15 — Health check sequence: systemctl --user is-active freellmapi; curl -o /dev/null -w '%{http_code}' http://127.0.0.1:3001/ expects 200; /v1/models expects 200 with a bearer key and 401 without. [src: systemctl, curl]

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
