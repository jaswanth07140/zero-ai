---
domain: os/systemd
title: systemd
status: seeded
source: /etc/os-release, systemctl --user
updated: 2026-11-16
---

# Operating system — systemd

## Facts
- 2026-11-16 — The freellmapi user unit is ~/.config/systemd/user/freellmapi.service, enabled, WantedBy=default.target, Restart=on-failure; linger is enabled on this host.

- 2026-11-15 — System units unavailable; user units in ~/.config/systemd/user work and persist with linger enabled.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
