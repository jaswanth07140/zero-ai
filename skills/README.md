# Skills index

A skill is a procedure, not a fact. Facts live in `knowledge/`; procedures live here.

| Skill | When to use |
|---|---|
| `distill-session.md` | End of a working session — turn it into durable facts |

Only the name and `when_to_use` are loaded by default; the body loads when the skill is
actually invoked, so a long skill costs nothing until it is needed.

## Format

```
---
name: kebab-case
when_to_use: one sentence
---
## Steps
1. ...
## Verify
- ...
```

A skill without a `Verify` section is a wish, not a skill.
