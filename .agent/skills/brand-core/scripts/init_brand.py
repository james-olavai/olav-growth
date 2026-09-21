#!/usr/bin/env python3
"""Initialize or validate Brand Brain (BUSINESS-SOT.md) and Memory (memory.md)."""

import argparse
import os
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", Path.cwd()))

MANDATORY_SOT_SECTIONS = [
    "Product Core",
    "Target ICP & Pain Points",
    "Brand Voice & Forbidden Words",
    "No-Cost Offer",
    "Primary CTA",
]


DEFAULT_TARGET = (WORKSPACE_ROOT / "content") if (WORKSPACE_ROOT / "content").is_dir() else WORKSPACE_ROOT


def init_files(target_dir: Path, force: bool = False):
    sot_target = target_dir / "BUSINESS-SOT.md"
    mem_target = target_dir / "memory.md"

    sot_tmpl = TEMPLATES_DIR / "BUSINESS-SOT.template.md"
    mem_tmpl = TEMPLATES_DIR / "memory.template.md"

    if not sot_target.exists() or force:
        shutil.copy(sot_tmpl, sot_target)
        print(f"[CREATED] {sot_target}")
    else:
        print(f"[EXISTS]  {sot_target} (use --force to overwrite)")

    if not mem_target.exists() or force:
        shutil.copy(mem_tmpl, mem_target)
        print(f"[CREATED] {mem_target}")
    else:
        print(f"[EXISTS]  {mem_target} (use --force to overwrite)")


def validate_sot(target_dir: Path) -> bool:
    sot_target = target_dir / "BUSINESS-SOT.md"
    if not sot_target.exists() and (target_dir / "content" / "BUSINESS-SOT.md").exists():
        sot_target = target_dir / "content" / "BUSINESS-SOT.md"

    if not sot_target.exists():
        print(f"[ERROR] Missing {sot_target}", file=sys.stderr)
        return False

    content = sot_target.read_text(encoding="utf-8")
    missing = [sec for sec in MANDATORY_SOT_SECTIONS if sec.lower() not in content.lower()]

    if missing:
        print(f"[WARNING] BUSINESS-SOT.md is missing mandatory sections: {missing}", file=sys.stderr)
        return False

    print("[SUCCESS] BUSINESS-SOT.md contains all 5 mandatory sections.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Brand Brain Management Tool")
    parser.add_argument("--init", action="store_true", help="Scaffold BUSINESS-SOT.md & memory.md")
    parser.add_argument("--validate", action="store_true", help="Validate existing BUSINESS-SOT.md")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing files")
    parser.add_argument("--dir", default=str(DEFAULT_TARGET), help="Target directory (defaults to content/ if present)")

    args = parser.parse_args()
    target_dir = Path(args.dir).resolve()

    if args.init:
        init_files(target_dir, args.force)
    elif args.validate:
        ok = validate_sot(target_dir)
        sys.exit(0 if ok else 1)
    else:
        # Default behavior: validate if exists, else init
        sot_target = target_dir / "BUSINESS-SOT.md"
        if sot_target.exists():
            validate_sot(target_dir)
        else:
            print("[INFO] No BUSINESS-SOT.md found. Initializing templates...")
            init_files(target_dir, False)


if __name__ == "__main__":
    main()
