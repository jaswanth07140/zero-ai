# zero-ai

A **portable brain** for an AI: identity, knowledge, skills, and evals as plain files in git.

This is not a model. It is the layer that makes any model behave like *your* AI, on any
machine, at any time. Clone the repo, load the prompt, and the assistant is instantly
itself again — same voice, same facts, same procedures.

## How this differs from `OpenCode`

| | `OpenCode` repo | `zero-ai` (this repo) |
|---|---|---|
| Job | This machine's agent state: installs, ports, keys, gotchas | The AI's identity and accumulated knowledge |
| Lifetime | Tied to one box and one setup | Portable — clone anywhere |
| Audience | The operator running OpenCode | Any runtime: OpenCode, Zero, a script, a web app |
| Changes | When the machine changes | When the AI learns something |

They are complementary. `OpenCode` remembers *the environment*; `zero-ai` remembers
*the assistant*.

## Layout

```
brain/taxonomy.json   48 domains across 12 categories — the breadth map
identity/             who it is — persona and hard rules (loaded first)
knowledge/            facts, nested one level: <category>/<domain>.md
skills/               procedures it can follow (index loaded, body on demand)
evals/                test prompts + what a good answer must contain
memory/               session digests, distilled (never raw logs)
runtime/              stdlib-only Python: init, build, ingest, stats, lint, eval
.github/              CI: lint + budget check on push, weekly digest reminder
```

## Quick start

```bash
python3 runtime/brain.py init            # materialize all 48 domains
python3 runtime/brain.py stats --verbose # coverage and budget
python3 runtime/brain.py build --out prompt.txt --skills
python3 runtime/brain.py lint

python3 runtime/ingest.py --domain hardware/disk --fact "4.3 GB free on /dev/vdb."
```

Grading against a live endpoint:

```bash
ZERO_AI_BASE_URL=http://127.0.0.1:3001/v1 \
ZERO_AI_API_KEY=$(cat ~/.config/opencode/freellmapi.key) \
ZERO_AI_MODEL=auto \
python3 runtime/run_eval.py
```

No dependencies. Python 3.8+ standard library only.

## Why it is built to be huge

A brain that grows to hundreds of domains cannot be pasted into a prompt. So `build`
**scores every fact against the query** and fills a character budget with the most
relevant ones, identity always included. Breadth therefore costs nothing at read time:

- Add domains freely — retrieval decides what loads.
- `stats` shows which categories are thin, so breadth work is measurable.
- `lint` refuses secrets, undated bullets, duplicate facts, and future dates.

## How memory grows

1. Load `identity/` + relevant `knowledge/` + skill index.
2. Answer.
3. Distill **only** durable facts into `knowledge/` via `ingest.py`.
4. Commit. That is the whole persistence story.

A fact earns a place only if it will still be true next month *and* would change a future
answer. Everything else belongs in the transcript, not here.

## What this is not

- **Not compute.** It cannot think by itself; inference comes from a provider.
- **Not a server.** GitHub Actions runs cron jobs, not chat requests.
- **Not a secret store.** No keys, ever. Use environment variables or Actions secrets.
