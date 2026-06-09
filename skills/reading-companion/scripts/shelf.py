#!/usr/bin/env python3
"""Scan the Obsidian reading shelf and print a compact, sortable view.

Reads the frontmatter of every book-note in `02 Areas/Reading/Books/` and emits
the few fields the picker actually weighs: status, pages, language, form,
priority, list, dates, position, rating. This keeps the 22+ book files out of
the model's context — call this instead of grepping each note.

Usage:
  shelf.py                      # everything, grouped by status
  shelf.py --status to-read     # one status only
  shelf.py --status reading
  shelf.py --json               # machine-readable, all books
  shelf.py --vault /path/to/vault

Vault resolution: --vault, else walk up from CWD looking for the Books folder,
else fall back to the known vault path.
"""
import argparse
import json
import os
import sys

BOOKS_REL = os.path.join("02 Areas", "Reading", "Books")
DEFAULT_VAULT = "/Users/sudakshsoti/dev/vault"
# Fields we surface, in display order.
SCALARS = ["status", "pages", "priority", "language", "rating",
           "started", "finished", "position", "list"]
LISTS = ["author", "categories"]


def find_vault(explicit):
    if explicit:
        return explicit
    cur = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(cur, BOOKS_REL)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return DEFAULT_VAULT


def parse_frontmatter(text):
    """Minimal YAML frontmatter parser. Handles scalars, inline [a, b] lists,
    and block lists (`- item` on following lines). No external deps."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end].strip("\n")
    data = {}
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            # Possible block list on following indented `- ` lines.
            items = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("- "):
                items.append(lines[j].lstrip()[2:].strip().strip('"\''))
                j += 1
            if items:
                data[key] = items
                i = j
                continue
            data[key] = ""
            i += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [v.strip().strip('"\'') for v in inner.split(",") if v.strip()] if inner else []
        else:
            data[key] = val.strip('"\'')
        i += 1
    return data


def load_books(vault):
    books_dir = os.path.join(vault, BOOKS_REL)
    if not os.path.isdir(books_dir):
        sys.exit(f"Books folder not found: {books_dir}")
    out = []
    for fn in sorted(os.listdir(books_dir)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(books_dir, fn)
        with open(path, encoding="utf-8") as fh:
            fm = parse_frontmatter(fh.read())
        if fm.get("type") != "book-note":
            continue
        rec = {"file": fn[:-3], "title": fm.get("title", fn[:-3])}
        for k in SCALARS:
            rec[k] = fm.get(k, "")
        for k in LISTS:
            v = fm.get(k, [])
            rec[k] = v if isinstance(v, list) else [v]
        out.append(rec)
    return out


def fmt_int(v):
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return 0


def print_table(books):
    order = {"reading": 0, "to-read": 1, "read": 2, "abandoned": 3}
    books = sorted(books, key=lambda b: (
        order.get(b["status"], 9),
        fmt_int(b["priority"]) or 999,
        b["title"].lower(),
    ))
    cur = None
    for b in books:
        if b["status"] != cur:
            cur = b["status"]
            print(f"\n## {cur or 'unspecified'}")
        author = ", ".join(b["author"]) if b["author"] else "?"
        form = "/".join(b["categories"]) if b["categories"] else "?"
        pages = b["pages"] or "?"
        lang = b["language"] or "?"
        pr = f" pr{b['priority']}" if str(b["priority"]).strip() else ""
        extra = []
        if b["position"]:
            extra.append(f"at {b['position']}")
        if b["started"]:
            extra.append(f"started {b['started']}")
        if b["finished"]:
            extra.append(f"finished {b['finished']}")
        if str(b["rating"]).strip():
            extra.append(f"{b['rating']}★")
        if b["list"]:
            extra.append(f"[{b['list']}]")
        tail = ("  · " + " · ".join(extra)) if extra else ""
        print(f"- {b['title']} — {author} · {pages}pp · {lang} · {form}{pr}{tail}")
        print(f"    file: {b['file']}")


def main():
    ap = argparse.ArgumentParser(description="Scan the reading shelf.")
    ap.add_argument("--status", help="filter: to-read | reading | read | abandoned")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--vault", help="vault root (auto-detected if omitted)")
    args = ap.parse_args()

    vault = find_vault(args.vault)
    books = load_books(vault)
    if args.status:
        books = [b for b in books if b["status"] == args.status]

    if args.json:
        print(json.dumps(books, ensure_ascii=False, indent=2))
        return

    counts = {}
    for b in books:
        counts[b["status"]] = counts.get(b["status"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    print(f"Shelf @ {vault} — {len(books)} books ({summary})")
    print_table(books)


if __name__ == "__main__":
    main()
