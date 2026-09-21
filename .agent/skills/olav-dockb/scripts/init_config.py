#!/usr/bin/env python3
"""Draft a config.yaml for a new project. Detection only — never overwrites
an existing config.yaml, never asks the user anything itself (that's the
agent's job per SKILL.md's init checklist). Prints a draft to review.

What it can figure out on its own:
  - a labeled folder-per-category subtree, if one exists: a directory whose
    immediate subdirectories each contain multiple .md files. That becomes
    `categories.source_folder`; subfolder names become the category list
    (via classify.build_title_alias_map at runtime, same as today).
  - doc_type rules, from folder-name keyword conventions (archive/template/
    reference/quer*/comment/tool/script) plus a generic slug of any other
    top-level folder under each scan root.

What it CANNOT figure out (left as TODO in the draft, for a human/agent to
fill in via conversation — see SKILL.md "Init checklist"):
  - materialize_tree decisions (moving files is a judgment call)
  - the `signals` fallback keyword lists (must come from real content, not
    guessed vocabulary)
  - confidence thresholds tuning

Usage:
    python init_config.py [scan_dir ...]     # defaults to every top-level
                                              # directory in the project root
"""
import os
import re
import sys
from pathlib import Path

import yaml

_root_override = os.environ.get("DOCS_KB_ROOT", "").strip()
ROOT = Path(_root_override).resolve() if _root_override else Path(__file__).resolve().parents[4]
SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_DIR / "config.yaml"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOC_TYPE_KEYWORDS = [
    ("archive", "archive"),
    ("template", "template"),
    ("reference", "reference-site"),
    ("quer", "query-tracker"),   # query / queries
    ("comment", "comment-thread"),
    ("tool", "tool-doc"),
    ("script", "tool-doc"),
    ("bom", "bom-doc"),
    ("onboard", "onboarding"),
    ("meeting", "meeting-notes"),
]


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def find_labeled_subtree(scan_roots):
    """Return the directory most likely to already encode a category
    taxonomy: the one with the most subfolders that each contain >=1 .md
    file directly or in their own subfolders."""
    best = None
    best_score = 0
    for root in scan_roots:
        for d in root.rglob("*"):
            if not d.is_dir():
                continue
            subfolders_with_content = [
                sub for sub in d.iterdir()
                if sub.is_dir() and any(sub.rglob("*.md"))
            ]
            if len(subfolders_with_content) >= 2:
                score = len(subfolders_with_content)
                if score > best_score:
                    best_score = score
                    best = d
    return best


def draft_doc_type_rules(scan_roots):
    rules = []
    for root in scan_roots:
        if not root.is_dir():
            continue
        root_rel = root.relative_to(ROOT).as_posix()
        for sub in sorted(root.iterdir()):
            if not sub.is_dir():
                continue
            name_lower = sub.name.lower()
            doc_type = None
            for kw, dt in DOC_TYPE_KEYWORDS:
                if kw in name_lower:
                    doc_type = dt
                    break
            if doc_type is None:
                doc_type = slugify(sub.name)
            rules.append([f"{root_rel}/{sub.name}", doc_type])
        rules.append([root_rel, slugify(root.name)])
    return rules


def main():
    args = sys.argv[1:]
    scan_dir_names = args or [d.name for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")]
    scan_roots = [ROOT / d for d in scan_dir_names if (ROOT / d).is_dir()]

    if CONFIG_PATH.is_file():
        print(f"{CONFIG_PATH} already exists — not overwriting. Delete it first if you really want a fresh draft.")
        return

    labeled = find_labeled_subtree(scan_roots)

    draft = {
        "scan_dirs": scan_dir_names,
        "doc_type_rules": draft_doc_type_rules(scan_roots),
        "classifiable_doc_types": "TODO: list which doc_types above should get a category (usually the ones under the labeled subtree found below)",
        "categories": {
            "source_folder": labeled.relative_to(ROOT).as_posix() if labeled else "TODO: no folder-per-category subtree was auto-detected — ask the user what their category taxonomy is",
            "signals": "TODO: leave empty and grow from classification_misses.jsonl, don't guess ahead of evidence",
        },
        "materialize_tree": "TODO: ask the user which collections (if any) should allow auto-filing into category folders — default everything to false",
        "confidence_thresholds": {"high_min_ratio": 0.4, "high_min_margin": 2.0, "min_hits": 2},
    }

    print("=== Draft config.yaml (NOT written — review, fill in the TODOs, then save it yourself) ===\n")
    print(yaml.dump(draft, sort_keys=False, allow_unicode=True, default_flow_style=False))

    if labeled:
        print(f"# Detected likely taxonomy source: {labeled.relative_to(ROOT).as_posix()}")
        print("# (a folder whose subfolders each contain their own .md files)")
    else:
        print("# No labeled folder-per-category subtree was found under the given scan_dirs.")
        print("# This means there's no cheap bootstrap — the agent should ask the user directly")
        print("# what their document categories are (see SKILL.md's init checklist).")


if __name__ == "__main__":
    main()
