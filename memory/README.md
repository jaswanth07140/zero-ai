# Memory — session digests

Not a log. A digest: what a future session would need to know that the knowledge files
do not already say.

## Why not store transcripts

Transcripts rot. They are long, they duplicate what `knowledge/` already holds, and they
make every future load more expensive. The value in a transcript is about 2% durable
fact and 98% noise.

## Format

One file per session: `memory/YYYY-MM-DD-<slug>.md`

```markdown
# 2026-11-16 — <what the session was about>

## Changed
- What is now true that was not true before (systems, files, versions).

## Learned
- Facts that were promoted into knowledge/<domain>.md (list the paths).

## Failed
- What was tried and did not work, so nobody repeats it.

## Next
- The single most valuable next action, stated as an imperative.
```

## Rules

- Write the digest **after** promoting facts, so `Learned` is a list of links, not a copy.
- If a session produced no durable change, write no digest. Silence is honest.
- Never paste secrets, tokens, or full command output here.
- Digests are append-only history; they are not loaded into the prompt by default.
