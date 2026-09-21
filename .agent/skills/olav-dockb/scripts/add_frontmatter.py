#!/usr/bin/env python3
"""Add/update YAML frontmatter on project docs, driven by config.yaml.

Idempotent: safe to re-run after an external source sync pulls new content. Only the
known frontmatter keys are recomputed from the document body each run; any
other keys already present in a file's frontmatter are preserved untouched.
The document body itself is never modified.

Usage:
    python add_frontmatter.py                 # dry run, prints a summary report
    python add_frontmatter.py --apply         # writes frontmatter to every file
    python add_frontmatter.py --apply --only some/subtree   # scope to one subtree
    python add_frontmatter.py --apply --materialize         # also physically
        move high-confidence files into their category folder, but ONLY for
        collections marked materialize_tree: true in config.yaml (off by
        default — see SKILL.md before ever passing this flag for real).
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

import classify

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = classify.ROOT
SKILL_DIR = classify.SKILL_DIR
MISS_LOG_PATH = SKILL_DIR / "classification_misses.jsonl"

FM_KEY_ORDER = [
    "title",
    "tags",
    "doc_type",
    "category",
    "category_confidence",
    "source_url",
    "page_id",
    "version",
    "status",
    "pulled",
    "related_page_ids",
    "related",
]


def extract_header_fields(text: str) -> dict:
    fields = {}
    m = re.search(r"\*Source:\*\s*(?:\[.*?\]\((\S+?)\)|(\S+))", text)
    if m:
        fields["source_url"] = m.group(1) or m.group(2)
    m = re.search(r"\*Page ID:\*\s*(\d+)", text)
    if m:
        fields["page_id"] = int(m.group(1))
    m = re.search(r"\*Version:\*\s*(\d+)", text)
    if m:
        fields["version"] = int(m.group(1))
    m = re.search(r"\*Status:\*\s*(.+)", text)
    if m:
        fields["status"] = m.group(1).strip().strip("*").strip()
    m = re.search(r"\*Pulled:\*\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    if m:
        fields["pulled"] = m.group(1)
    return fields


def extract_related_page_ids(text: str, own_page_id) -> list:
    ids = {int(pid) for pid in re.findall(r"pages/(\d+)", text)}
    ids.discard(own_page_id)
    return sorted(ids)


def split_existing_frontmatter(text: str):
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


def build_page_id_map(files) -> dict:
    """page_id -> vault-relative path (no .md extension), for Obsidian
    wikilinks. Path-qualified (not bare title) because a corpus can reuse
    the same chapter title/filename across several collections — a bare
    link would be ambiguous."""
    mapping = {}
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        _existing_fm, body = split_existing_frontmatter(text)
        header_fields = extract_header_fields(body)
        pid = header_fields.get("page_id")
        if pid is not None:
            mapping[pid] = path.relative_to(ROOT).with_suffix("").as_posix()
    return mapping


def build_frontmatter(rel_path: Path, config: dict, title_alias_map: dict, page_id_map: dict, existing_fm: dict, body: str) -> dict:
    title = classify.extract_title(body) or classify.clean_stem(Path(rel_path).stem)
    header_fields = extract_header_fields(body)
    fm = dict(existing_fm)
    fm["title"] = title
    doc_type = classify.classify_doc_type(rel_path, config)
    fm["doc_type"] = doc_type
    filename_title = classify.clean_stem(Path(rel_path).stem)
    category, confidence = classify.classify(title, body, doc_type, config, title_alias_map, filename_title)
    fm["category"] = category
    fm["category_confidence"] = confidence
    fm["tags"] = [f"category/{classify.slugify(category)}", f"doc-type/{classify.slugify(doc_type)}"]
    for key in ("source_url", "page_id", "version", "status", "pulled"):
        if key in header_fields:
            fm[key] = header_fields[key]
        else:
            fm.pop(key, None)
    related_ids = extract_related_page_ids(body, fm.get("page_id"))
    fm["related_page_ids"] = related_ids
    fm["related"] = [f"[[{page_id_map[pid]}]]" for pid in related_ids if pid in page_id_map]
    ordered = {k: fm[k] for k in FM_KEY_ORDER if k in fm}
    for k, v in fm.items():
        if k not in ordered:
            ordered[k] = v
    return ordered


def render_file(fm: dict, body: str) -> str:
    yaml_text = yaml.dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    if not body.startswith("\n"):
        body = "\n" + body
    return f"---\n{yaml_text}---\n{body}"


def log_classification_miss(rel_path: str, category: str, confidence: str):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": rel_path,
        "category": category,
        "confidence": confidence,
    }
    with open(MISS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def maybe_materialize(path: Path, rel_path: Path, config: dict, category: str, confidence: str, apply: bool):
    """If eligible, move `path` into its category folder. Returns the
    possibly-updated (path, rel_path). Never moves anything unless the
    collection is explicitly marked materialize_tree: true in config.yaml,
    and only for title-match/high confidence classifications.

    Files already sitting anywhere under source_folder are the taxonomy
    itself (however deeply nested) and are NEVER moved here: this
    function only auto-files genuinely new/unfiled documents into a
    top-level category folder. A misfiled file already inside source_folder
    is check_taxonomy_drift.py's job to report, not this one's to silently
    "fix" by flattening an existing sub-hierarchy."""
    if confidence not in ("title-match", "high") or category == "Uncategorized":
        return path, rel_path

    prefix = classify.get_matched_prefix(rel_path, config)
    if prefix is None or not config.get("materialize_tree", {}).get(prefix, False):
        return path, rel_path
    if prefix != config["categories"]["source_folder"]:
        return path, rel_path  # only reorganize within the collection that defines the taxonomy

    source_root = ROOT / prefix
    if source_root in path.parents:
        return path, rel_path  # already part of the taxonomy tree, however deeply nested

    target_dir = source_root / category

    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        new_path = target_dir / path.name
        print(f"  MOVE: {rel_path.as_posix()} -> {new_path.relative_to(ROOT).as_posix()}")
        shutil.move(str(path), str(new_path))
        return new_path, new_path.relative_to(ROOT)
    else:
        new_rel = (target_dir / path.name).relative_to(ROOT)
        print(f"  WOULD MOVE: {rel_path.as_posix()} -> {new_rel.as_posix()}")
        return path, rel_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    parser.add_argument("--only", default=None, help="scope to a subdirectory, e.g. some/subtree")
    parser.add_argument("--materialize", action="store_true", help="also physically move high-confidence files (see config.yaml materialize_tree)")
    args = parser.parse_args()

    if args.apply and classify.ROOT_IS_DEFAULT:
        print(
            "Refusing to run --apply: DOCS_KB_ROOT is unset, so ROOT defaults to this "
            "skill's own repository root. Running --apply here would rewrite this "
            "project's own files. Set DOCS_KB_ROOT to the real directory you want to "
            "index, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    config = classify.load_config()
    title_alias_map = classify.build_title_alias_map(config)

    scan_roots = [ROOT / args.only] if args.only else [ROOT / d for d in config["scan_dirs"]]

    files = []
    for d in scan_roots:
        if d.is_dir():
            files.extend(sorted(p for p in d.rglob("*.md") if p.name != "CLAUDE.md"))

    # Built from the full corpus (not just `--only`'s scope) so related/
    # wikilinks still resolve to pages outside a narrowed re-run.
    all_files = files
    if args.only:
        all_files = []
        for d in [ROOT / d for d in config["scan_dirs"]]:
            if d.is_dir():
                all_files.extend(p for p in d.rglob("*.md") if p.name != "CLAUDE.md")
    page_id_map = build_page_id_map(all_files)

    doc_type_counts = {}
    category_counts = {}
    confidence_counts = {}
    missing_page_id = []
    uncategorized = []

    for path in files:
        rel_path = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")
        existing_fm, body = split_existing_frontmatter(text)
        fm = build_frontmatter(rel_path, config, title_alias_map, page_id_map, existing_fm, body)

        doc_type_counts[fm["doc_type"]] = doc_type_counts.get(fm["doc_type"], 0) + 1
        category_counts[fm["category"]] = category_counts.get(fm["category"], 0) + 1
        confidence_counts[fm["category_confidence"]] = confidence_counts.get(fm["category_confidence"], 0) + 1
        if fm["doc_type"] in config.get("page_id_doc_types", []) and "page_id" not in fm:
            missing_page_id.append(rel_path.as_posix())
        if fm["category"] == "Uncategorized":
            uncategorized.append(rel_path.as_posix())
        if fm["category_confidence"] in ("medium", "none"):
            log_classification_miss(rel_path.as_posix(), fm["category"], fm["category_confidence"])

        write_path, write_rel = path, rel_path
        if args.materialize:
            write_path, write_rel = maybe_materialize(path, rel_path, config, fm["category"], fm["category_confidence"], args.apply)

        if args.apply:
            new_text = render_file(fm, body)
            if new_text != text or write_path != path:
                write_path.write_text(new_text, encoding="utf-8")

    print(f"Scanned {len(files)} files under {[str(d.relative_to(ROOT)) for d in scan_roots]}")
    print(f"Mode: {'APPLY (files written)' if args.apply else 'DRY RUN (no files changed)'}{' + MATERIALIZE' if args.materialize else ''}")
    print("\ndoc_type counts:")
    for k, v in sorted(doc_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\ncategory counts:")
    for k, v in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\ncategory_confidence counts:")
    for k, v in sorted(confidence_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nFiles without a parsed page_id (synced-source doc_types only): {len(missing_page_id)}")
    for p in missing_page_id[:20]:
        print(f"  {p}")
    if len(missing_page_id) > 20:
        print(f"  ... and {len(missing_page_id) - 20} more")
    print(f"\nUncategorized files: {len(uncategorized)}")
    for p in uncategorized[:20]:
        print(f"  {p}")
    if len(uncategorized) > 20:
        print(f"  ... and {len(uncategorized) - 20} more")


if __name__ == "__main__":
    main()
