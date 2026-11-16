#!/usr/bin/env python3
"""Run evals/cases.jsonl against any OpenAI-compatible endpoint.

Deterministic grading only: substring must_include / must_not_include.
Exit code 1 if any case fails, so CI can gate on it.

Env: ZERO_AI_BASE_URL, ZERO_AI_API_KEY, ZERO_AI_MODEL
"""
import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases.jsonl"


def load_cases(path):
    cases = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path.name}:{n}: invalid JSON — {e}")
    return cases


def call(base, key, model, prompt, timeout, system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    routed = (data.get("_routed_via") or {}).get("model") or data.get("model")
    return (data["choices"][0]["message"]["content"] or "").strip(), routed


def call_with_retry(base, key, model, prompt, timeout, system, retries, delay):
    last = None
    for attempt in range(retries + 1):
        try:
            content, routed = call(base, key, model, prompt, timeout, system)
            return content, None, routed
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries:
                break
            wait = delay * (2 ** attempt)
            retry_after = e.headers.get("Retry-After") if e.headers else None
            if retry_after and retry_after.isdigit():
                wait = max(wait, int(retry_after))
            print(f"     {e.code} — backing off {wait:.0f}s (attempt {attempt+1}/{retries})")
            time.sleep(wait)
        except Exception as e:
            last = e
            break
    return None, last, None


LEAK = ("thinking process", "analyze user input", "here's my reasoning",
        "let me think step by step", "<scratchpad>", "reasoning process",
        "key term", "**question:**", "let me break this down",
        "here's a thinking", "thinking:")
# Scratchpad dumps often open with a bulleted restatement of the question.
HEAD = ("*   question:", "* question:", "question:", "step 1:")


def leaked(answer):
    low = answer.lower()
    hits = [m for m in LEAK if m in low]
    head = low[:300]
    if not hits and any(h in head for h in HEAD) and "answer:" in low:
        hits = ["scratchpad restatement"]
    return hits


def grade(case, answer):
    low = answer.lower()
    missing = [s for s in case.get("must_include", []) if s.lower() not in low]
    forbidden = [s for s in case.get("must_not_include", []) if s.lower() in low]
    return missing, forbidden


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="structure only, no network")
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--delay", type=float, default=3.0, help="seconds between cases (free tiers rate-limit)")
    ap.add_argument("--retries", type=int, default=3, help="retries on HTTP 429/5xx with backoff")
    ap.add_argument("--case", help="run a single case id")
    ap.add_argument("--brain", action="store_true", help="load the assembled brain as the system prompt")
    ap.add_argument("--system-file", help="use this file as the system prompt")
    a = ap.parse_args()

    if not CASES.exists():
        print(f"no cases at {CASES}", file=sys.stderr)
        return 2

    cases = load_cases(CASES)
    if a.case:
        cases = [c for c in cases if c.get("id") == a.case]
        if not cases:
            print(f"no case with id {a.case}", file=sys.stderr)
            return 2

    for c in cases:
        if not c.get("id") or not c.get("prompt"):
            print(f"invalid case (needs id and prompt): {c}", file=sys.stderr)
            return 2

    if a.dry_run:
        print(f"dry-run: {len(cases)} case(s) valid")
        for c in cases:
            inc = len(c.get("must_include", []))
            exc = len(c.get("must_not_include", []))
            print(f"  {c['id']:<28} +{inc} required  -{exc} forbidden")
        return 0

    base = os.environ.get("ZERO_AI_BASE_URL")
    key = os.environ.get("ZERO_AI_API_KEY")
    model = os.environ.get("ZERO_AI_MODEL", "auto")
    if not base or not key:
        print("need ZERO_AI_BASE_URL and ZERO_AI_API_KEY", file=sys.stderr)
        return 2

    system = None
    if a.brain:
        import subprocess
        system = subprocess.run([sys.executable, str(ROOT / "runtime" / "brain.py"),
                                 "build"], capture_output=True, text=True).stdout
    elif a.system_file:
        system = pathlib.Path(a.system_file).read_text(encoding="utf-8")
    if system:
        print(f"system prompt: {len(system):,} chars loaded\n")

    passed = failed = 0
    for c in cases:
        answer, err, routed = call_with_retry(base, key, model, c["prompt"], a.timeout, system, a.retries, a.delay)
        if answer is None:
            print(f"FAIL {c['id']:<28} request error: {err}")
            failed += 1
            time.sleep(a.delay)
            continue
        if leaked(answer):
            failed += 1
            print(f"FAIL {c['id']:<28} reasoning leaked ({routed}): {leaked(answer)}")
            continue
        missing, forbidden = grade(c, answer)
        if missing or forbidden:
            failed += 1
            print(f"FAIL {c['id']:<28} [{routed}] missing={missing} forbidden={forbidden}")
            print(f"     answer: {answer[:160]!r}")
        else:
            passed += 1
            print(f"pass {c['id']:<28} [{routed}]")
        time.sleep(a.delay)

    print(f"\n{passed}/{len(cases)} passed via {model}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
