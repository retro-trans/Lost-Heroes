"""Remove Japanese script from committed translation files (AGENTS.md rule).

Scans work/translation/**/*.en.json. Any string containing kana/kanji is
replaced: "en" fields become null (and are reported, since that is a real
defect); notes/report text has the Japanese runs replaced with "[JP]".
Japanese is allowed only in work/glossary (names and UI terms).

Usage:
    python tools/strip_jp.py [--check]
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JP = re.compile(r"[぀-ヿ㐀-鿿ｦ-ﾟ]+")


def clean(obj, path, issues):
    if isinstance(obj, dict):
        return {k: (None if k == "en" and isinstance(v, str) and JP.search(v) and not issues.append((path, v))
                    else clean(v, path, issues)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(v, path, issues) for v in obj]
    if isinstance(obj, str):
        return JP.sub("[JP]", obj)
    return obj


def main():
    check = "--check" in sys.argv
    changed = 0
    for p in glob.glob(os.path.join(ROOT, "work/translation/**/*.en.json"), recursive=True):
        raw = open(p, encoding="utf-8").read()
        if not JP.search(raw):
            continue
        issues = []
        data = clean(json.loads(raw), p, issues)
        changed += 1
        for _, v in issues:
            print(f"{os.path.relpath(p, ROOT)}: Japanese in an 'en' field, set to null: {v[:40]!r}")
        if not check:
            json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{changed} file(s) {'contain' if check else 'cleaned of'} Japanese script")
    sys.exit(1 if check and changed else 0)


if __name__ == "__main__":
    main()
