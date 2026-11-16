---
domain: models/routing
title: Routing
status: seeded
source: freellmapi DB: api_keys, models tables
updated: 2026-11-16
---

# Models and inference — Routing

## Facts
- 2026-11-16 — As of 2026-11-16 the openrouter key is scoped to dots-3-note-preview, cohere/north-mini-code and nemotron-3.5-super-vl; the nvidia/nemotron-3.5-lightning and google/gemma-4-31b-it model rows were disabled after scratchpad reasoning leaks were observed in completions. [src: freellmapi DB: api_keys, models]

- 2026-11-15 — auto classifies the request and fails over across providers; observed latency about 1.5 seconds.
- 2026-11-15 — intelligence_rank is lower-is-smarter, range 17-203 across the catalog.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
