#!/usr/bin/env python3
"""
gen_blog_images.py — Extract mermaid blocks from a blog post and render to WebP.

Usage:
    uv run python .agent/skills/content-writer/scripts/gen_blog_images.py <slug>
    uv run python .agent/skills/content-writer/scripts/gen_blog_images.py olav-v010-launch

Input:
    Reads olav.md from the most recent olav-post/archive/YYYY-MM-DD/ directory,
    falling back to olav-web/src/content/blog/<slug>.md if archive is not found.

Output:
    olav-web/public/blog-images/<slug>/
        og-image.webp     (= diagram-1.webp, the first mermaid block)
        diagram-1.webp
        diagram-2.webp
        ...

Requirements:
    - npx  (node.js — auto-installs @mermaid-js/mermaid-cli on first run)
    - cwebp  (sudo apt install webp)
"""

import subprocess
import sys
import os
import re
import glob
import tempfile
import shutil
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[4]   # .agent/skills/content-writer/scripts → repo root
QUALITY = 85
WIDTH = 1200
HEIGHT = 630

MERMAID_CLI = "mmdc"  # installed by @mermaid-js/mermaid-cli via npx


def find_source_file(slug: str) -> tuple[Path, Path | None]:
    """Find the most recent archive olav.md, or fall back to the blog file.
    Returns (source_path, archive_dir_or_None).
    """
    archives = sorted(glob.glob(str(REPO_ROOT / "olav-post" / "archive" / "*")), reverse=True)
    for archive in archives:
        candidate = Path(archive) / "olav.md"
        if candidate.exists():
            return candidate, Path(archive)
    fallback = REPO_ROOT / "olav-web" / "src" / "content" / "blog" / f"{slug}.md"
    if fallback.exists():
        return fallback, None
    raise FileNotFoundError(
        f"No olav.md found in olav-post/archive/ and no {fallback} exists."
    )


def extract_mermaid_blocks(md_path: Path) -> list[str]:
    """Extract all ```mermaid ... ``` blocks from a markdown file."""
    content = md_path.read_text(encoding="utf-8")
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", content, re.DOTALL)
    return [b.strip() for b in blocks]


def render_mermaid_to_png(diagram: str, output_png: Path) -> None:
    """Render a mermaid diagram string to a PNG via @mermaid-js/mermaid-cli."""
    with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", encoding="utf-8", delete=False) as f:
        f.write(diagram)
        tmp_mmd = f.name

    puppeteer_cfg = REPO_ROOT / "puppeteer_config.json"
    cmd = [
        "npx", "--yes", "@mermaid-js/mermaid-cli",
        "-i", tmp_mmd,
        "-o", str(output_png),
        "-w", str(WIDTH),
        "-H", str(HEIGHT),
        "-b", "white",
    ]
    if puppeteer_cfg.exists():
        cmd.extend(["-p", str(puppeteer_cfg)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"  [mermaid-cli stderr] {result.stderr.strip()}", file=sys.stderr)
            raise RuntimeError(f"mermaid-cli failed (exit {result.returncode})")
    finally:
        os.unlink(tmp_mmd)


def png_to_webp(png_path: Path, webp_path: Path) -> None:
    """Convert PNG to WebP using cwebp."""
    result = subprocess.run(
        ["cwebp", f"-q", str(QUALITY), str(png_path), "-o", str(webp_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cwebp failed: {result.stderr.strip()}")


def main():
    if len(sys.argv) < 2:
        print("Usage: gen_blog_images.py <slug>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1]
    out_dir = REPO_ROOT / "olav-web" / "public" / "blog-images" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find source
    source, archive_dir = find_source_file(slug)
    print(f"Source: {source.relative_to(REPO_ROOT)}")

    # Archive image dir (mirrors web output)
    archive_img_dir: Path | None = None
    if archive_dir is not None:
        archive_img_dir = archive_dir / "images"
        archive_img_dir.mkdir(parents=True, exist_ok=True)

    # Extract mermaid blocks
    blocks = extract_mermaid_blocks(source)
    if not blocks:
        print("No mermaid blocks found in source file.", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(blocks)} mermaid block(s)")

    with tempfile.TemporaryDirectory() as tmpdir:
        generated = []
        for i, block in enumerate(blocks, start=1):
            label = f"diagram-{i}"
            tmp_png = Path(tmpdir) / f"{label}.png"
            out_webp = out_dir / f"{label}.webp"

            print(f"  Rendering {label}...", end=" ", flush=True)
            render_mermaid_to_png(block, tmp_png)
            png_to_webp(tmp_png, out_webp)
            size_kb = out_webp.stat().st_size // 1024
            print(f"→ {out_webp.name} ({size_kb} KB)")
            generated.append(out_webp)

            # Mirror to archive
            if archive_img_dir is not None:
                shutil.copy2(out_webp, archive_img_dir / out_webp.name)

        # og-image = first diagram
        og_image = out_dir / "og-image.webp"
        shutil.copy2(generated[0], og_image)
        if archive_img_dir is not None:
            shutil.copy2(generated[0], archive_img_dir / "og-image.webp")
        print(f"  og-image.webp ← diagram-1.webp")

    print()
    print("─" * 60)
    print("Add to blog frontmatter:")
    print(f"  ogImage: /blog-images/{slug}/og-image.webp")
    print()
    print(f"Web output:  {out_dir.relative_to(REPO_ROOT)}/")
    for f in sorted(out_dir.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")
    if archive_img_dir is not None:
        print()
        print(f"Archive copy: {archive_img_dir.relative_to(REPO_ROOT)}/")
        for f in sorted(archive_img_dir.iterdir()):
            print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
