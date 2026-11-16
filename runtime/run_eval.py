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


def call(base, key, model, prompt, timeout):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
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
    return (data["choices"][0]["message"]["content"] or "").strip()


def grade(case, answer):
    low = answer.lower()
    missing = [s for s in case.get("must_include", []) if s.lower() not in low]
    forbidden = [s for s in case.get("must_not_include", []) if s.lower() in low]
    return missing, forbidden


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="structure only, no network")
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--case", help="run a single case id")
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

    passed = failed = 0
    for c in cases:
        try:
            answer = call(base, key, model, c["prompt"], a.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
            print(f"FAIL {c['id']:<28} request error: {e}")
            failed += 1
            continue
        missing, forbidden = grade(c, answer)
        if missing or forbidden:
            failed += 1
            print(f"FAIL {c['id']:<28} missing={missing} forbidden={forbidden}")
            print(f"     answer: {answer[:160]!r}")
        else:
            passed += 1
            print(f"pass {c['id']}")

    print(f"\n{passed}/{len(cases)} passed via {model}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
