---
domain: models/providers
title: Providers
status: seeded
source: freellmapi DB: api_keys, models tables
updated: 2026-11-15
---

# Models and inference — Providers

## Facts
- 2026-11-15 — OVH is scoped to modelScope Qwen3.8-27B because Qwen3.5-397B-A17B leaks its thinking process into content and burns the output cap. [src: freellmapi api_keys row 4]
- 2026-11-15 — As of 2026-11-15 the router has six configured providers: google, groq, openrouter with real keys, kilo and ovh added keyless, and aihorde added then disabled because only 10 of its 32 catalog rows have a live worker and it has no tool support. [src: freellmapi api_keys table]

- 2026-11-15 — Exactly three providers hold real API keys and return real completions: google, groq, openrouter. The other configured providers are keyless and must not be counted as keyed. [src: freellmapi api_keys table]
- 2026-11-15 — NVIDIA NIM never issued a usable key; Cerebras, HuggingFace, and Ollama Cloud have zero models in the catalog.

## Constraints

- <!-- what this domain forbids or bounds -->

## Open questions

- <!-- unverified; promote to Facts once confirmed -->
