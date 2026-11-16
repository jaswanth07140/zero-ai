---
domain: practice/debugging
title: Debugging
status: seeded
source: this repo's runtime/ tooling
updated: 2026-11-15
---

# Engineering practice — Debugging

## Facts

- 2026-11-15 — Debug order that isolated the real fault: systemctl status, then journalctl tail, then curl with an explicit model id, then a DB query for key status. The failures were provider-side (HTTP 503, 60s timeout), not configuration. [src: this session]

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
