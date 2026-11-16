#!/usr/bin/env python3
"""Append one durable fact to knowledge/<category>/<domain>.md.

Refuses duplicates and refuses anything that looks like a secret. Rewrites the
file rather than appending blindly, so the structure stays canonical.
"""
import argparse
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|gsk_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"
    r"|sk-or-v1-[a-f0-9]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|freellmapi-[a-f0-9]{20,})"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, help="category/domain, e.g. hardware/disk")
    ap.add_argument("--fact", required=True)
    ap.add_argument("--source", help="where this was verified: a path, URL, or command")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if SECRET_RE.search(a.fact):
        print("refused: fact looks like it contains a secret", file=sys.stderr)
        return 2

    cat, _, dom = a.domain.partition("/")
    if not cat or not dom:
        print("refused: --domain must be category/domain", file=sys.stderr)
        return 2

    path = KNOWLEDGE / cat / f"{dom}.md"
    if not path.exists():
        print(f"refused: {path.relative_to(ROOT)} does not exist; run brain.py grow first",
              file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    key = re.sub(r"\W+", "", a.fact.lower())[:60]
    for line in text.splitlines():
        if re.sub(r"\W+", "", line.lower()).find(key) != -1 and key:
            print(f"skipped: a near-identical fact already exists in {path.relative_to(ROOT)}")
            return 0

    bullet = f"- {a.date} — {a.fact.strip()}"
    if a.source:
        bullet += f" [src: {a.source.strip()}]"
    if "## Facts" not in text:
        print("refused: file has no '## Facts' section", file=sys.stderr)
        return 2

    placeholder = "- <!-- none yet: add a dated fact when one is verified -->"
    if placeholder in text:
        text = text.replace(placeholder, bullet, 1)
    else:
        text = text.replace("## Facts\n", f"## Facts\n{bullet}\n", 1)

    text = re.sub(r"^updated: .*$", f"updated: {a.date}", text, count=1, flags=re.M)
    text = re.sub(r"^status: scaffold$", "status: seeded", text, count=1, flags=re.M)

    if a.dry_run:
        print(f"would add to {path.relative_to(ROOT)}: {bullet}")
        return 0

    path.write_text(text, encoding="utf-8")
    print(f"added to {path.relative_to(ROOT)}: {bullet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
