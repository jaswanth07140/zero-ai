---
name: distill-session
when_to_use: At the end of a session, to turn what happened into durable knowledge.
---

## Steps

1. List what changed in the world, not what you did: new installs, paths, limits,
   failures, decisions.
2. For each item ask: *will this still be true in a month, and would it change a future
   answer?* Drop anything that fails either test.
3. Assign a domain. If none fits, `python3 runtime/brain.py grow --domain <cat>/<dom>`.
4. Write one dated bullet per fact, with a number where a number exists, via
   `python3 runtime/ingest.py --domain <cat>/<dom> --fact "..."`.
5. Supersede contradictions — replace the old bullet instead of appending a new one.
6. `python3 runtime/brain.py stats` — if over budget, prune the least answer-changing
   facts.
7. `python3 runtime/brain.py lint` — must be clean.
8. Commit with a message naming the domains touched.

## Verify

- `brain.py lint` reports clean.
- `brain.py stats` shows size under the budget and the touched categories non-zero.
- Every new fact has a date and a domain file.
- No secrets, tokens, or raw transcripts were added.
