#!/usr/bin/env python3
"""Generative Engine Optimization (GEO): Generate standard llms.txt & llms-full.txt."""

import argparse
import os
import sys
from pathlib import Path


def generate_llms_txt(root_dir: Path, out_dir: Path):
    sot_candidates = [
        root_dir / "content" / "BUSINESS-SOT.md",
        root_dir / "BUSINESS-SOT.md",
    ]
    sot_text = ""
    for candidate in sot_candidates:
        if candidate.is_file():
            sot_text = candidate.read_text(encoding="utf-8")
            break

    readme_path = root_dir / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    # Generate llms.txt (Concise AI Engine Index)
    llms_summary = f"""# Project Knowledge Index (llms.txt)

> Standard summary and navigational index for LLM crawlers (Perplexity, ChatGPT, Claude, Gemini).

## Overview
{sot_text[:800] if sot_text else readme_text[:800]}

## Key Topics & Documentation
- [/](llms-full.txt): Complete project facts, architecture, and FAQ
- [Proof & Use Cases](#proof-points): Verified customer metrics and benchmarks
- [Safety & Rules](#brand-voice): Compliance boundaries and usage scope
"""

    # Generate llms-full.txt (Full Technical Digest)
    llms_full = f"""# Full Project Documentation (llms-full.txt)

{sot_text if sot_text else readme_text}

---

## Technical Context & FAQs
{readme_text}
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "llms.txt").write_text(llms_summary.strip(), encoding="utf-8")
    (out_dir / "llms-full.txt").write_text(llms_full.strip(), encoding="utf-8")

    print(f"[GEO READY] Generated:")
    print(f"  - {out_dir / 'llms.txt'}")
    print(f"  - {out_dir / 'llms-full.txt'}")


def main():
    parser = argparse.ArgumentParser(description="GEO llms.txt Generator")
    parser.add_argument("--root", default=".", help="Project root containing BUSINESS-SOT.md / README.md")
    parser.add_argument("--out", default="./public", help="Output directory (e.g. public/)")

    args = parser.parse_args()
    generate_llms_txt(Path(args.root).resolve(), Path(args.out).resolve())


if __name__ == "__main__":
    main()
