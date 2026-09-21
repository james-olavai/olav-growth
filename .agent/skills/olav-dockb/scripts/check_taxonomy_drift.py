#!/usr/bin/env python3
"""Report-only: flag files whose physical folder disagrees with what the
content classifier says, for a collection where folder placement is
supposed to encode category (config.categories.source_folder).

Never writes anything. Folder placement wins on anything less than a
confident content classification — the folder tree here mirrors the source
system's own page tree, which is itself a strong signal that a weak content score
shouldn't override.

Usage:
    python check_taxonomy_drift.py
"""
import sys
from pathlib import Path

import classify

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = classify.ROOT


def folder_implied_category(path: Path, source: Path):
    rel = path.relative_to(source)
    parts = rel.parts
    if len(parts) == 1:
        return None  # flat file directly in source_folder isn't inside a category folder
    return parts[0]


def main():
    config = classify.load_config()
    source_folder = config["categories"]["source_folder"]
    if not source_folder:
        print("categories.source_folder is empty, nothing to check")
        return
    title_alias_map = classify.build_title_alias_map(config)
    source = ROOT / source_folder

    if not source.is_dir():
        print(f"source_folder {source} does not exist, nothing to check")
        return

    flagged = 0
    checked = 0
    for path in sorted(source.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        folder_cat = folder_implied_category(path, source)
        if folder_cat is None:
            continue
        checked += 1

        text = path.read_text(encoding="utf-8", errors="replace")
        m_body = text.split("\n---\n", 1)
        body = m_body[1] if text.startswith("---\n") and len(m_body) > 1 else text
        title = classify.extract_title(body) or classify.clean_stem(path.stem)
        filename_title = classify.clean_stem(path.stem)

        rel_path = path.relative_to(ROOT)
        doc_type = classify.classify_doc_type(rel_path, config)
        content_cat, confidence = classify.classify(title, body, doc_type, config, title_alias_map, filename_title)

        # Folder placement wins unless the content classifier is confident
        # AND disagrees with where the file currently sits.
        if confidence in ("title-match", "high") and content_cat != folder_cat:
            flagged += 1
            print(f"DRIFT  {rel_path.as_posix()}")
            print(f"       folder says:  {folder_cat}")
            print(f"       content says: {content_cat} ({confidence})")
            print()

    print(f"Checked {checked} files under {config['categories']['source_folder']}; {flagged} drift flag(s)")


if __name__ == "__main__":
    main()
