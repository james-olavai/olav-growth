#!/usr/bin/env python3
"""3:4 Visual Card Generator (1080x1440) compliant with Course Visual SOP.

Visual Architecture:
- Canvas: 1080 x 1440 px (3:4 aspect ratio)
- Top Safe Zone: 0 - 210px (avoids mobile status bar & navigation)
- Bottom Safe Zone: 1180 - 1440px (avoids platform avatar, likes, comments)
- Active Center: 210 - 1180px (Big poster headline + key points + contrast focus)
"""

import argparse
import html
import sys
from pathlib import Path

THEMES = {
    "dark_tech": {
        "bg": "#0d1117",
        "card_bg": "#161b22",
        "primary": "#58a6ff",
        "accent": "#f78166",
        "text": "#f0f6fc",
        "subtext": "#8b949e",
        "border": "#30363d",
    },
    "warm_editorial": {
        "bg": "#faf8f5",
        "card_bg": "#ffffff",
        "primary": "#d9532f",
        "accent": "#2f5233",
        "text": "#1f2421",
        "subtext": "#6c757d",
        "border": "#e8e5e0",
    },
    "clean_business": {
        "bg": "#f8fafc",
        "card_bg": "#ffffff",
        "primary": "#0284c7",
        "accent": "#0f172a",
        "text": "#0f172a",
        "subtext": "#64748b",
        "border": "#e2e8f0",
    },
    "deep_purple": {
        "bg": "#0f0c20",
        "card_bg": "#1a1636",
        "primary": "#a855f7",
        "accent": "#ec4899",
        "text": "#ffffff",
        "subtext": "#94a3b8",
        "border": "#2e285a",
    }
}


def render_svg_card(
    title: str,
    badge: str = "实测复盘",
    subtitle: str = "",
    bullet_points: list[str] = None,
    footer_note: str = "评论区回复【暗号】获取完整自查表",
    theme_name: str = "dark_tech",
    page_num: str = "01/05"
) -> str:
    t = THEMES.get(theme_name, THEMES["dark_tech"])
    points = bullet_points or [
        "踩坑 3 次总结的系统化避坑框架",
        "单源多产出：1 份核心事实跑通 8 大平台",
        "拒绝机器爹味，注入真实人话感与口语垫词"
    ]

    title_escaped = html.escape(title)
    badge_escaped = html.escape(badge)
    subtitle_escaped = html.escape(subtitle)
    footer_escaped = html.escape(footer_note)

    # Build bullet point boxes
    items_svg = []
    y_start = 660
    for idx, pt in enumerate(points[:4]):
        item_text = html.escape(pt)
        items_svg.append(f"""
        <g transform="translate(80, {y_start + idx * 115})">
            <rect width="920" height="92" rx="16" fill="{t['card_bg']}" stroke="{t['border']}" stroke-width="2"/>
            <circle cx="48" cy="46" r="18" fill="{t['primary']}" fill-opacity="0.15"/>
            <text x="48" y="53" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="20" font-weight="bold" fill="{t['primary']}" text-anchor="middle">{idx + 1}</text>
            <text x="90" y="54" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="28" font-weight="500" fill="{t['text']}">{item_text}</text>
        </g>
        """)

    items_block = "\n".join(items_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1440" width="1080" height="1440">
    <defs>
        <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{t['bg']}"/>
            <stop offset="100%" stop-color="{t['card_bg']}"/>
        </linearGradient>
    </defs>

    <!-- Canvas Background -->
    <rect width="1080" height="1440" fill="url(#bg-grad)"/>

    <!-- Decorative Top Wave / Grid -->
    <circle cx="1080" cy="0" r="400" fill="{t['primary']}" fill-opacity="0.06"/>
    <circle cx="0" cy="1440" r="350" fill="{t['accent']}" fill-opacity="0.04"/>

    <!-- ================= TOP SAFE ZONE (0-210px) ================= -->
    <!-- Brand / Badge Header (Safe from device status bar) -->
    <g transform="translate(80, 180)">
        <rect width="160" height="42" rx="21" fill="{t['primary']}" fill-opacity="0.15" stroke="{t['primary']}" stroke-width="1.5"/>
        <text x="80" y="27" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="20" font-weight="600" fill="{t['primary']}" text-anchor="middle">{badge_escaped}</text>
        <text x="920" y="27" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="20" font-weight="500" fill="{t['subtext']}" text-anchor="end">{page_num}</text>
    </g>

    <!-- ================= ACTIVE CENTER (210-1180px) ================= -->
    <!-- Big Poster Headline (大字报核心痛点) -->
    <g transform="translate(80, 320)">
        <text font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="64" font-weight="800" fill="{t['text']}" line-height="1.2">
            <tspan x="0" y="0">{title_escaped[:15]}</tspan>
            <tspan x="0" y="82" fill="{t['accent']}">{title_escaped[15:32]}</tspan>
        </text>
    </g>

    <!-- Subtitle / Hook context -->
    <text x="80" y="520" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="30" font-weight="400" fill="{t['subtext']}">
        {subtitle_escaped or "实战干货拆解 · 拒绝正确的废话"}
    </text>

    <!-- Divider -->
    <line x1="80" y1="580" x2="1000" y2="580" stroke="{t['border']}" stroke-width="2"/>

    <!-- Structured Content Blocks -->
    {items_block}

    <!-- ================= BOTTOM SAFE ZONE (1180-1440px) ================= -->
    <!-- Soft CTA / Funnel Hook (Above bottom reaction buttons) -->
    <g transform="translate(80, 1220)">
        <rect width="920" height="72" rx="14" fill="{t['card_bg']}" stroke="{t['primary']}" stroke-width="2" stroke-dasharray="8 6"/>
        <text x="460" y="45" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', PingFang SC, sans-serif" font-size="24" font-weight="600" fill="{t['primary']}" text-anchor="middle">
            👉 {footer_escaped}
        </text>
    </g>
</svg>
"""
    return svg.strip()


def export_svg_to_png(svg_path: Path, png_path: Path) -> bool:
    """Convert rendered SVG to PNG using cairosvg or system tools if available."""
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=1080, output_height=1440)
        print(f"[CONVERTED] PNG Card saved to: {png_path}")
        return True
    except ImportError:
        pass

    # Try system tools like rsvg-convert
    import shutil
    import subprocess
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        try:
            subprocess.run([rsvg, "-w", "1080", "-h", "1440", str(svg_path), "-o", str(png_path)], check=True)
            print(f"[CONVERTED] PNG Card saved via rsvg-convert to: {png_path}")
            return True
        except Exception:
            pass

    print(f"[INFO] SVG generated at {svg_path}. To convert to PNG, install cairosvg: `pip install cairosvg` or use the browser VNC.")
    return False


def main():
    parser = argparse.ArgumentParser(description="3:4 Visual Card Generator")
    parser.add_argument("--title", required=True, help="Main title/pain point for card")
    parser.add_argument("--badge", default="实战干货", help="Badge tag (e.g. 避坑指南/案例拆解)")
    parser.add_argument("--subtitle", default="", help="Subtitle or context line")
    parser.add_argument("--points", nargs="+", help="Up to 4 structured points")
    parser.add_argument("--cta", default="评论区回复【清单】领取完整自查表", help="Footer CTA text")
    parser.add_argument("--theme", default="dark_tech", choices=list(THEMES.keys()), help="Visual theme")
    parser.add_argument("--page", default="01/05", help="Page indicator (e.g. 01/05)")
    parser.add_argument("--out", required=True, help="Output SVG file path")
    parser.add_argument("--png", action="store_true", help="Also export PNG alongside SVG")

    args = parser.parse_args()

    svg_content = render_svg_card(
        title=args.title,
        badge=args.badge,
        subtitle=args.subtitle,
        bullet_points=args.points,
        footer_note=args.cta,
        theme_name=args.theme,
        page_num=args.page
    )

    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(svg_content, encoding="utf-8")
    print(f"[RENDERED] 3:4 SVG Card saved to: {out_p}")

    if args.png:
        png_path = out_p.with_suffix(".png")
        export_svg_to_png(out_p, png_path)


if __name__ == "__main__":
    main()
