---
domain: ops/logs
title: Logs
status: seeded
source: journalctl --user -u freellmapi
updated: 2026-11-16
---

# Operations — Logs

## Facts
- 2026-11-16 — The freellmapi service logs to the systemd journal via journalctl --user -u freellmapi; the freellmapi/freellmapi.log file is no longer written by the unit; an operations log exists at ~/zero-ops/logs/20261115-operations.log. [src: journalctl --user -u freellmapi, ls ~/zero-ops/logs]

- 2026-11-15 — Service logs go to journald (journalctl --user -u freellmapi) and self-cap; the app no longer writes its own log file.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
