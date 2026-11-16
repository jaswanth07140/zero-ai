# Knowledge index

Nested one level: `knowledge/<category>/<domain>.md`. The full breadth map lives in
`brain/taxonomy.json` and is materialized by `python3 runtime/brain.py init`.

## Categories

| Category | Covers |
|---|---|
| `hardware/` | CPU, memory, disk, GPU |
| `os/` | Distribution, systemd, packages, shell |
| `runtime/` | Node, Python, git, containers |
| `opencode/` | Config, agents, skills, sessions |
| `models/` | Providers, routing, quotas, catalog |
| `freellmapi/` | Service, keys, dashboard, MCP |
| `zero/` | The Zero site, API layer, deployment, admin |
| `web/` | HTTP, DNS, TLS, performance |
| `data/` | SQLite, files, backups, retention |
| `security/` | Secrets, auth, threats, hardening |
| `practice/` | Testing, docs, git workflow, debugging |
| `ops/` | Monitoring, logs, cost, incidents |

## Rules for facts

- One bullet per fact, prefixed with the date it was verified: `- 2026-11-15 — ...`
- Facts must be **durable and answer-changing**. If it will not matter next month, it
  does not belong here.
- Numbers over adjectives: `4.3 GB free`, not `low on disk`.
- Mark anything unverified `(unverified)` so it can be challenged later.
- When a fact is superseded, replace it. Git keeps history; the file holds only truth.
- `status: seeded` means it has facts; `status: scaffold` means the domain exists but is
  empty. Scaffolds are honest placeholders, not filler.

## Why nested

A flat directory stops scaling around 30 files. Nested directories let the brain reach
hundreds of domains without a single index file becoming the bottleneck, and `build`
scores facts across the whole tree so growth never costs context budget.
