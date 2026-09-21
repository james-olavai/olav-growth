#!/usr/bin/env python3
"""Unified Trend Scout: Scans Google Trends & Tech forums, matches against brand SOT keywords, and generates Signal Cards."""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
SIGNALS_DIR = REPO_ROOT / "content" / "candidate_signals"

from fetch_google_trends import fetch_google_trends, emit_signal_cards as emit_gt_cards
from fetch_tech_trends import fetch_hackernews, emit_signal_cards as emit_hn_cards


def extract_keywords_from_sot(sot_path: Path):
    """Extract brand keywords and ICP pain points from BUSINESS-SOT.md."""
    if not sot_path.is_file():
        return ["AI", "agent", "marketing", "automation", "workflow", "saas", "growth"]

    text = sot_path.read_text(encoding="utf-8")
    keywords = set()
    for line in text.splitlines():
        if any(marker in line for marker in ["定位", "关键词", "卖点", "ICP", "痛点", "核心主张"]):
            words = re.findall(r'[\w\u4e00-\u9fa5]{2,}', line)
            for w in words:
                if len(w) >= 2 and w not in ["产品", "核心", "定位", "用户", "方案", "客户", "痛点"]:
                    keywords.add(w.lower())

    if not keywords:
        keywords = {"ai", "agent", "marketing", "automation", "workflow", "growth", "saas"}
    return list(keywords)


def main():
    parser = argparse.ArgumentParser(description="Multi-Source Trend Radar & Signal Generator")
    parser.add_argument("--sot", default=str(REPO_ROOT / "content" / "BUSINESS-SOT.md"), help="Path to BUSINESS-SOT.md")
    parser.add_argument("--geos", default="US,TW,SG", help="Comma-separated Google Trends geo codes")
    parser.add_argument("--hn-types", default="top,show", help="Comma-separated Hacker News types")
    parser.add_argument("--limit-per-source", type=int, default=10, help="Max candidates per source")
    parser.add_argument("--keywords", nargs="*", help="Override keywords (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Print matches without writing Signal Cards")

    args = parser.parse_args()
    sot_p = Path(args.sot)

    if args.keywords:
        target_kws = args.keywords
    else:
        target_kws = extract_keywords_from_sot(sot_p)

    print("==================================================")
    print(" 📡 Trend Radar: Multi-Source Signal Scout")
    print(f" Target Keywords: {', '.join(target_kws[:12])}...")
    print("==================================================")

    matched_gt = []
    for geo in [g.strip().upper() for g in args.geos.split(",") if g.strip()]:
        print(f"[SCAN] Checking Google Trends ({geo})...")
        trends = fetch_google_trends(geo=geo, limit=args.limit_per_source, filter_kw=target_kws)
        matched_gt.extend(trends)

    matched_hn = []
    for htype in [h.strip().lower() for h in args.hn_types.split(",") if h.strip()]:
        print(f"[SCAN] Checking Hacker News ({htype.upper()})...")
        stories = fetch_hackernews(story_type=htype, limit=args.limit_per_source, filter_kw=target_kws)
        matched_hn.extend(stories)

    print("\n--------------------------------------------------")
    print(f" Found {len(matched_gt)} Google Trends matches & {len(matched_hn)} Tech Community matches.")
    print("--------------------------------------------------")

    for idx, t in enumerate(matched_gt, 1):
        print(f"  [GT-{t['geo']}] {t['query']} ({t['approx_traffic']})")

    for idx, h in enumerate(matched_hn, 1):
        print(f"  [HN] [{h['score']} pts] {h['title']}")

    if not args.dry_run and (matched_gt or matched_hn):
        emitted_gt = emit_gt_cards(matched_gt, out_dir=SIGNALS_DIR)
        emitted_hn = emit_hn_cards(matched_hn, out_dir=SIGNALS_DIR)
        total = len(emitted_gt) + len(emitted_hn)
        print(f"\n[SIGNALS SAVED] Generated {total} Signal Cards in:")
        print(f"  📂 {SIGNALS_DIR}")
        print("\nNext step: Run `content-strategist` to score these topics:")
        print(f"  python .agent/skills/content-strategist/scripts/score_topics.py --title \"<Topic>\"")


if __name__ == "__main__":
    main()
