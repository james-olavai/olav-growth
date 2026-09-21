#!/usr/bin/env python3
"""Package multi-platform drafts, visual assets, and checklists into a release bundle."""

import argparse
import datetime
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
REPO_ROOT = SKILL_DIR.parent.parent.parent
DEFAULT_OUT = (REPO_ROOT / "content" / "campaigns") if (REPO_ROOT / "content" / "campaigns").is_dir() else (REPO_ROOT / "releases")


def create_release_package(topic_id: str, out_dir: Path):
    today = datetime.date.today().strftime("%Y%m%d")
    pkg_dir = out_dir / f"{today}-{topic_id.lower()}"
    (pkg_dir / "posts").mkdir(parents=True, exist_ok=True)
    (pkg_dir / "images").mkdir(parents=True, exist_ok=True)
    (pkg_dir / "assets").mkdir(parents=True, exist_ok=True)

    tmpl = (TEMPLATES_DIR / "release-package.template.md").read_text(encoding="utf-8")
    filled = tmpl.replace("REL-YYYYMMDD-01", f"REL-{today}-01")
    filled = filled.replace("TOPIC-YYYYMMDD-01", topic_id)
    filled = filled.replace("YYYY-MM-DD", datetime.date.today().isoformat())

    manifest_path = pkg_dir / "manifest.md"
    manifest_path.write_text(filled, encoding="utf-8")

    print(f"[PACKAGE CREATED] Release bundle initialized at: {pkg_dir}")
    print(f"  - {pkg_dir / 'manifest.md'} (Checklist & Manifest)")
    print(f"  - {pkg_dir / 'posts'} (Platform text drafts)")
    print(f"  - {pkg_dir / 'images'} (3:4 visual cards)")
    print(f"  - {pkg_dir / 'assets'} (Downloadable PDFs / Documents)")
    return pkg_dir


def main():
    parser = argparse.ArgumentParser(description="Release Packaging Utility")
    parser.add_argument("--topic-id", default="TOPIC-01", help="Topic identifier")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output directory for release packages")

    args = parser.parse_args()
    create_release_package(args.topic_id, Path(args.out).resolve())


if __name__ == "__main__":
    main()
