#!/usr/bin/env python3
"""zero-ai brain engine — stdlib only.

Commands:
  init     materialize knowledge/<category>/<domain>.md from brain/taxonomy.json
  stats    size, coverage, and budget report
  build    assemble a system prompt (optionally query-scored) within a char budget
  lint     check dates, secrets, duplicates, undated bullets
  grow     scaffold one new domain

The brain is designed to grow large. That is exactly why `build` scores facts
against the query instead of dumping every file into the prompt.
"""

import argparse
import json
import pathlib
import re
import sys
import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
BRAIN = ROOT / "brain"
TAXONOMY = BRAIN / "taxonomy.json"
BUDGET_DEFAULT = 24000

SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|gsk_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"
    r"|sk-or-v1-[a-f0-9]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|freellmapi-[a-f0-9]{20,})"
)
DATE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) — (.+)$")
STOP = set("the a an and or of to in on for with is are was were be been it this that "
           "from by as at not no but if then than so do does did can could should would "
           "what which who how why when where i you we they he she my your our their".split())


def load_taxonomy():
    return json.loads(TAXONOMY.read_text(encoding="utf-8"))


def terms(text):
    return {w for w in re.findall(r"[a-z0-9_./-]+", text.lower())
            if len(w) > 2 and w not in STOP}


def parse_domain_file(path):
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---\n"):
        end = raw.find("\n---\n", 4)
        if end != -1:
            for line in raw[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = raw[end + 5:]
    facts, section = [], None
    for line in body.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        m = DATE_RE.match(line.strip())
        if m and section == "facts":
            facts.append((m.group(1), m.group(2).strip()))
    return meta, facts, body


def all_domain_files():
    if not KNOWLEDGE.is_dir():
        return []
    return sorted(p for p in KNOWLEDGE.rglob("*.md")
                  if p.name not in ("README.md", "_template.md"))


def domain_id(path):
    return str(path.relative_to(KNOWLEDGE)).removesuffix(".md").replace("\\", "/")


# ---------------------------------------------------------------- init

def cmd_init(args):
    tax = load_taxonomy()
    today = datetime.date.today().isoformat()
    created = skipped = 0
    for cat in tax["categories"]:
        cdir = KNOWLEDGE / cat["id"]
        for dom in cat["domains"]:
            path = cdir / f"{dom['id']}.md"
            if path.exists() and not args.force:
                skipped += 1
                continue
            seeds = dom.get("seed") or []
            cdir.mkdir(parents=True, exist_ok=True)
            lines = [
                "---",
                f"domain: {cat['id']}/{dom['id']}",
                f"title: {dom['title']}",
                f"status: {'seeded' if seeds else 'scaffold'}",
                f"updated: {today}",
                "---",
                "",
                f"# {cat['title']} — {dom['title']}",
                "",
                "## Facts",
                "",
            ]
            if seeds:
                lines += [f"- {s}" for s in seeds]
            else:
                lines.append("- <!-- none yet: add a dated fact when one is verified -->")
            lines += ["", "## Constraints", "",
                      "- <!-- what this domain forbids or bounds -->", "",
                      "## Open questions", "",
                      "- <!-- unverified; promote to Facts once confirmed -->", ""]
            path.write_text("\n".join(lines), encoding="utf-8")
            created += 1
    print(f"init: {created} created, {skipped} existing (use --force to rewrite)")


# ---------------------------------------------------------------- stats

def cmd_stats(args):
    tax = load_taxonomy()
    files = all_domain_files()
    total_facts = 0
    by_cat = {}
    chars = 0
    seeded = scaffold = 0
    oldest = None
    for p in files:
        meta, facts, body = parse_domain_file(p)
        chars += len(body)
        total_facts += len(facts)
        cat = domain_id(p).split("/")[0]
        by_cat[cat] = by_cat.get(cat, 0) + len(facts)
        if facts:
            seeded += 1
        else:
            scaffold += 1
        for d, _ in facts:
            if oldest is None or d < oldest:
                oldest = d

    declared = sum(len(c["domains"]) for c in tax["categories"])
    print(f"taxonomy : {len(tax['categories'])} categories, {declared} domains declared")
    print(f"materialized: {len(files)} files ({seeded} seeded, {scaffold} scaffold)")
    print(f"facts    : {total_facts}  oldest {oldest or 'n/a'}")
    print(f"body size: {chars:,} chars (~{chars // 4:,} tokens)")
    print(f"budget   : {args.budget:,} chars -> {'OK' if chars <= args.budget else 'OVER by %d' % (chars - args.budget)}")
    print("\nper category:")
    for cat in tax["categories"]:
        n = by_cat.get(cat["id"], 0)
        bar = "#" * min(40, n)
        print(f"  {cat['id']:<12} {n:>4}  {bar}")
    empty = [domain_id(p) for p in files if not parse_domain_file(p)[1]]
    if empty and args.verbose:
        print(f"\nempty domains ({len(empty)}): " + ", ".join(empty[:24]) + (" ..." if len(empty) > 24 else ""))


# ---------------------------------------------------------------- build

def score(fact_text, meta, q_terms):
    t = terms(fact_text + " " + meta.get("title", "") + " " + meta.get("domain", ""))
    return len(t & q_terms)


def cmd_build(args):
    q = terms(args.query or "")
    parts = []
    for name in ("identity/rules.md", "identity/persona.md"):
        f = ROOT / name
        if f.exists():
            label = name.split("/")[-1].split(".")[0].upper()
            parts.append(f"## {label}\n\n{f.read_text(encoding='utf-8').strip()}")

    cands = []
    for p in all_domain_files():
        meta, facts, _ = parse_domain_file(p)
        for d, text in facts:
            cands.append((score(text, meta, q) if q else 0, d, domain_id(p), text))

    if q:
        cands.sort(key=lambda c: (-c[0], c[1]))
        if any(c[0] > 0 for c in cands):
            cands = [c for c in cands if c[0] > 0]
    else:
        cands.sort(key=lambda c: c[2])

    used = sum(len(h) for h in parts)
    included = 0
    current = None
    for s, d, dom, text in cands:
        line = f"- {d} — {text}"
        if used + len(line) + 24 > args.budget:
            continue
        if dom != current:
            block = f"## KNOWLEDGE — {dom}\n\n"
            parts.append(block)
            used += len(block)
            current = dom
        parts.append(line)
        used += len(line) + 1
        included += 1

    if args.skills:
        sdir = ROOT / "skills"
        idx = ["## SKILL INDEX"]
        if sdir.is_dir():
            for f in sorted(sdir.glob("*.md")):
                if f.name in ("README.md", "_template.md"):
                    continue
                txt = f.read_text(encoding="utf-8")
                name = re.search(r"^name:\s*(.+)$", txt, re.M)
                when = re.search(r"^when_to_use:\s*(.+)$", txt, re.M)
                if name and when:
                    idx.append(f"- {name.group(1).strip()} — {when.group(1).strip()}")
        if len(idx) > 1:
            parts.append("\n".join(idx))

    prompt = "\n\n".join(parts) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(prompt, encoding="utf-8")
        print(f"wrote {args.out}: {len(prompt):,} chars (~{len(prompt)//4:,} tokens), "
              f"{included}/{len(cands)} facts, budget {args.budget:,}")
    else:
        sys.stdout.write(prompt)


# ---------------------------------------------------------------- lint

def cmd_lint(args):
    problems = []
    seen = {}
    for p in all_domain_files():
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        if SECRET_RE.search(text):
            problems.append(f"{rel}: possible secret in file")
        meta, facts, body = parse_domain_file(p)
        if "domain:" not in text[:400]:
            problems.append(f"{rel}: missing frontmatter")
        for d, t in facts:
            if d > datetime.date.today().isoformat():
                problems.append(f"{rel}: future-dated fact {d}")
            key = re.sub(r"\W+", "", t.lower())[:80]
            if key in seen:
                problems.append(f"{rel}: duplicate fact also in {seen[key]}")
            seen[key] = rel
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("- ") and not DATE_RE.match(s) and "<!--" not in s:
                problems.append(f"{rel}: undated bullet: {s[:60]}")
    if problems:
        print(f"lint: {len(problems)} problem(s)")
        for x in problems[:40]:
            print("  " + x)
        return 1
    print("lint: clean")
    return 0


# ---------------------------------------------------------------- grow

def cmd_grow(args):
    cat, _, dom = args.domain.partition("/")
    if not cat or not dom:
        print("grow: --domain must be category/domain", file=sys.stderr)
        return 2
    path = KNOWLEDGE / cat / f"{dom}.md"
    if path.exists():
        print(f"grow: {path.relative_to(ROOT)} already exists")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    title = args.title or dom.replace("-", " ").title()
    path.write_text(
        "---\n"
        f"domain: {cat}/{dom}\n"
        f"title: {title}\n"
        "status: scaffold\n"
        f"updated: {today}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Facts\n\n- <!-- none yet -->\n\n"
        "## Constraints\n\n- <!-- what this domain forbids -->\n\n"
        "## Open questions\n\n- <!-- unverified -->\n",
        encoding="utf-8")
    print(f"grow: created {path.relative_to(ROOT)}")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="brain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init"); p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("stats")
    p.add_argument("--budget", type=int, default=BUDGET_DEFAULT)
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("build")
    p.add_argument("--query", default="")
    p.add_argument("--budget", type=int, default=BUDGET_DEFAULT)
    p.add_argument("--out")
    p.add_argument("--skills", action="store_true")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("lint"); p.set_defaults(fn=cmd_lint)

    p = sub.add_parser("grow")
    p.add_argument("--domain", required=True)
    p.add_argument("--title")
    p.set_defaults(fn=cmd_grow)

    args = ap.parse_args()
    return args.fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())
