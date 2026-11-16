# Evals

`cases.jsonl` holds one JSON object per line:

| Field | Meaning |
|---|---|
| `id` | Stable name; used in output |
| `prompt` | The user message sent to the model |
| `must_include` | Every string here must appear in the answer (case-insensitive) |
| `must_not_include` | None of these may appear |

Grading is deterministic substring matching. No LLM judge — judges flatter themselves
and drift. A case either passes or fails, and the exit code reflects it so CI can gate.

## Writing a good case

- Test a **behavior**, not trivia: refusal to fabricate, honesty about a gap, refusal to
  leak a secret, correct handling of a known constraint.
- Keep `must_include` short (1-3 characters to a few words). Long strings are brittle.
- `must_not_include` is where the value is — the wrong answer you want to prevent.
- Add a case every time the assistant gets something wrong in a way that would recur.

## Running

```bash
ZERO_AI_BASE_URL=http://127.0.0.1:3001/v1 \
ZERO_AI_API_KEY=... \
ZERO_AI_MODEL=auto \
python3 runtime/run_eval.py

python3 runtime/run_eval.py --dry-run   # structure only, no network, safe in CI
```

Non-zero exit means at least one case failed.
