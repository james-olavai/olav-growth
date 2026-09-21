#!/usr/bin/env python3
"""Fast metadata + full-text search over the documents under ROOT.

No embeddings/vector store — this walks the frontmatter added by
add_frontmatter.py and greps body text, filtered by metadata. At ~220 files /
~3MB this is fast enough to run fresh on every call.

Examples:
    python search_docs.py "example query"
    python search_docs.py "term" --category "example-category"
    python search_docs.py --doc-type example --status draft
    python search_docs.py --related-to 12345
    python search_docs.py --list-categories
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

import classify

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = classify.ROOT
SKILL_DIR = classify.SKILL_DIR
SYNONYMS_PATH = SKILL_DIR / "synonyms.yaml"
MISS_LOG_PATH = SKILL_DIR / "query_misses.jsonl"
MISS_THRESHOLD = 1  # log queries that return this many hits or fewer


def load_synonym_groups() -> list:
    if not SYNONYMS_PATH.is_file():
        return []
    data = yaml.safe_load(SYNONYMS_PATH.read_text(encoding="utf-8")) or {}
    groups = data.get("groups", [])
    return [[str(term).lower() for term in group] for group in groups]


def expand_query(query: str, groups: list):
    """If `query` exactly matches a synonym-group member, return a regex
    pattern matching ANY member of that group, plus the matched terms.
    Otherwise return (query, None) unchanged — query is used as-is (regex)."""
    q_lower = query.strip().lower()
    for group in groups:
        if q_lower in group:
            pattern = "|".join(re.escape(term) for term in group)
            return pattern, group
    return query, None


def log_miss(query: str, expanded_terms, hit_count: int, args):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "expanded_terms": expanded_terms,
        "hits": hit_count,
        "category": args.category,
        "doc_type": args.doc_type,
    }
    with open(MISS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def split_frontmatter(text: str):
    if text.startswith("---\n") or text.startswith("---\r\n"):
        end = re.search(r"\n---\s*\n", text[4:])
        if end:
            fm_text = text[4:4 + end.start()]
            body = text[4 + end.end():]
            try:
                fm = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                fm = {}
            return fm, body
    return {}, text


def load_docs():
    docs = []
    config = classify.load_config()
    for d in config["scan_dirs"]:
        base = ROOT / d
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name == "CLAUDE.md":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            fm, body = split_frontmatter(text)
            docs.append({
                "path": path.relative_to(ROOT).as_posix(),
                "fm": fm,
                "body": body,
            })
    return docs


def matches_filters(doc, args):
    fm = doc["fm"]
    if args.category and (fm.get("category") or "").lower() != args.category.lower():
        return False
    if args.doc_type and (fm.get("doc_type") or "").lower() != args.doc_type.lower():
        return False
    if args.status and args.status.lower() not in (fm.get("status") or "").lower():
        return False
    if args.page_id and fm.get("page_id") != args.page_id:
        return False
    if args.related_to:
        related = set(fm.get("related_page_ids") or [])
        if fm.get("page_id") != args.related_to and args.related_to not in related:
            return False
    return True


def print_doc_row(doc):
    fm = doc["fm"]
    print(f"{doc['path']}")
    print(f"  title: {fm.get('title', '(no title)')}")
    meta_bits = [f"category={fm.get('category', '-')}", f"doc_type={fm.get('doc_type', '-')}"]
    if fm.get("status"):
        meta_bits.append(f"status={fm['status'][:80]}")
    if fm.get("page_id"):
        meta_bits.append(f"page_id={fm['page_id']}")
    print(f"  {' | '.join(meta_bits)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default=None, help="free-text search over document body (regex ok)")
    parser.add_argument("--category", default=None)
    parser.add_argument("--doc-type", default=None)
    parser.add_argument("--status", default=None, help="substring match against the status field")
    parser.add_argument("--page-id", type=int, default=None)
    parser.add_argument("--related-to", type=int, default=None, help="page_id: find this page plus anything referencing/referenced by it")
    parser.add_argument("--list-categories", action="store_true")
    parser.add_argument("-i", "--ignore-case", action="store_true", default=True)
    parser.add_argument("--max-matches", type=int, default=3, help="max matching lines to show per file")
    parser.add_argument("--no-expand", action="store_true", help="disable synonym-group query expansion")
    parser.add_argument("--no-log", action="store_true", help="don't append low-hit queries to query_misses.jsonl")
    args = parser.parse_args()

    docs = load_docs()

    if args.list_categories:
        cats = {}
        for doc in docs:
            c = doc["fm"].get("category", "Uncategorized")
            cats[c] = cats.get(c, 0) + 1
        for c, n in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"{n:4d}  {c}")
        return

    filtered = [d for d in docs if matches_filters(d, args)]

    if not args.query:
        print(f"{len(filtered)} matching file(s):\n")
        for doc in filtered:
            print_doc_row(doc)
            print()
        return

    expanded_terms = None
    query_pattern = args.query
    if not args.no_expand:
        groups = load_synonym_groups()
        query_pattern, expanded_terms = expand_query(args.query, groups)

    pattern = re.compile(query_pattern, re.IGNORECASE if args.ignore_case else 0)
    hits = 0
    for doc in filtered:
        lines = doc["body"].splitlines()
        matching = [(i + 1, ln) for i, ln in enumerate(lines) if pattern.search(ln)]
        if not matching:
            continue
        hits += 1
        print_doc_row(doc)
        for lineno, ln in matching[: args.max_matches]:
            print(f"    {lineno}: {ln.strip()[:150]}")
        if len(matching) > args.max_matches:
            print(f"    ... and {len(matching) - args.max_matches} more match(es)")
        print()

    if expanded_terms:
        print(f"(expanded '{args.query}' to synonym group: {', '.join(expanded_terms)})")
    print(f"--- {hits} file(s) matched '{args.query}' ---")

    if not args.no_log and hits <= MISS_THRESHOLD:
        log_miss(args.query, expanded_terms, hits, args)


if __name__ == "__main__":
    main()
