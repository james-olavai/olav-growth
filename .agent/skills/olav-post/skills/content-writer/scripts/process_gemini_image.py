#!/usr/bin/env python3
"""
process_gemini_image.py — Process a Gemini-generated image for the blog.
Converts to WebP and resizes to 1200x630.

Usage:
    uv run python .agent/skills/content-writer/scripts/process_gemini_image.py <slug> <local_image_path>
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[4]
QUALITY = 85
WIDTH = 1200
HEIGHT = 630

def main():
    if len(sys.argv) < 3:
        print("Usage: process_gemini_image.py <slug> <local_image_path>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1]
    input_path = Path(sys.argv[2])
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    out_dir = REPO_ROOT / "olav-web" / "public" / "blog-images" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find most recent archive dir for mirrors
    import glob
    archives = sorted(glob.glob(str(REPO_ROOT / "olav-post" / "archive" / "*")), reverse=True)
    archive_img_dir: Path | None = None
    if archives:
        archive_img_dir = Path(archives[0]) / "images"
        archive_img_dir.mkdir(parents=True, exist_ok=True)

    # Output path as artistic-1.webp (default for Gemini images)
    out_webp = out_dir / "artistic-1.webp"
    
    print(f"Processing Gemini image: {input_path.name}")
    print(f"  Target: {out_webp.relative_to(REPO_ROOT)}")

    # Convert and resize using cwebp
    try:
        result = subprocess.run(
            [
                "cwebp", 
                "-q", str(QUALITY),
                "-resize", str(WIDTH), str(HEIGHT),
                str(input_path), 
                "-o", str(out_webp)
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Error: cwebp failed: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
            
        size_kb = out_webp.stat().st_size // 1024
        print(f"  → Success: {out_webp.name} ({size_kb} KB)")

        # Also set as og-image if requested or if it's the first image
        # (For Gemini, we usually want it as og-image if it's generated for that purpose)
        og_image = out_dir / "og-image.webp"
        shutil.copy2(out_webp, og_image)
        print(f"  og-image.webp ← artistic-1.webp")

        # Mirror to archive
        if archive_img_dir:
            shutil.copy2(out_webp, archive_img_dir / out_webp.name)
            shutil.copy2(out_webp, archive_img_dir / "og-image.webp")
            print(f"  Mirrored to archive: {archive_img_dir.relative_to(REPO_ROOT)}/")

    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
