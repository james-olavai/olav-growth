#!/usr/bin/env python3
"""Fetch tech & startup discussions from Hacker News and GitHub trending."""

import argparse
import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
SIGNALS_DIR = REPO_ROOT / "content" / "candidate_signals"


def fetch_hackernews(story_type="top", limit=15, filter_kw=None):
    """story_type: 'top', 'new', 'best', 'ask', 'show'"""
    endpoint = f"https://hacker-news.firebaseio.com/v0/{story_type}stories.json"
    req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[ERROR] Failed to fetch HN stories: {e}", file=sys.stderr)
        return []

    results = []
    for sid in story_ids[:limit * 3]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        try:
            with urllib.request.urlopen(urllib.request.Request(item_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=5) as r:
                item = json.loads(r.read().decode())
        except Exception:
            continue

        if not item or "title" not in item:
            continue

        title = item.get("title", "")
        url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")
        score = item.get("score", 0)
        comments = item.get("descendants", 0)

        if filter_kw:
            if not any(k.lower() in title.lower() for k in filter_kw):
                continue

        results.append({
            "title": title,
            "url": url,
            "score": score,
            "comments": comments,
            "hn_link": f"https://news.ycombinator.com/item?id={sid}",
            "source": f"HackerNews ({story_type.upper()})"
        })

        if len(results) >= limit:
            break

    return results


def emit_signal_cards(trends, out_dir=SIGNALS_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().strftime("%Y%m%d")
    emitted = []

    for idx, t in enumerate(trends, 1):
        slug = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]+', '-', t["title"].lower()).strip('-')[:40]
        sig_id = f"SIG-{today}-HN{idx:02d}"
        file_path = out_dir / f"{sig_id.lower()}-{slug}.md"

        card_content = f"""---
title: "Signal Card: {t['title']}"
signal_id: "{sig_id}"
doc_type: candidate-signal
status: candidate
created_at: {datetime.date.today().isoformat()}
source_type: "community-trend"
platform: "HackerNews"
score: {t['score']}
comments: {t['comments']}
tags:
  - doc/signal
  - status/candidate
  - source/hackernews
---

# Signal Card: {t['title']}

> 来源：{t['source']} (👍 {t['score']} points, 💬 {t['comments']} comments)

---

* **Signal ID**：`{sig_id}`
* **录入日期**：{datetime.date.today().isoformat()}
* **信号来源类型**：技术社区热议
* **来源链接 / 证据凭证**：<{t['url']}>
* **讨论地址**：<{t['hn_link']}>
* **核心痛点/情绪标签**：[技术选型 / 生产力工具 / 踩坑反思]
* **关联业务核心**：[待 content-strategist 关联业务 SOT]
* **初步切入设想**：从该技术议题在社区引发的讨论痛点切入，提炼可复用的方法论或架构思考。
"""
        file_path.write_text(card_content, encoding="utf-8")
        emitted.append(file_path)

    return emitted


def main():
    parser = argparse.ArgumentParser(description="Tech & Startup Trend Scraper")
    parser.add_argument("--type", default="top", choices=["top", "show", "ask", "best"], help="HN Feed type")
    parser.add_argument("--limit", type=int, default=10, help="Number of items")
    parser.add_argument("--filter", nargs="*", help="Filter keywords")
    parser.add_argument("--emit-signals", action="store_true", help="Save as Signal Cards in content/candidate_signals/")

    args = parser.parse_args()
    trends = fetch_hackernews(story_type=args.type, limit=args.limit, filter_kw=args.filter)

    print(f"\n==================================================")
    print(f"  Hacker News Trending ({args.type.upper()})")
    print(f"  Fetched {len(trends)} items")
    print(f"==================================================")

    for idx, t in enumerate(trends, 1):
        print(f"{idx}. [{t['score']} pts | {t['comments']} cmts] {t['title']}")
        print(f"   Link: {t['url']}")

    if args.emit_signals:
        saved = emit_signal_cards(trends)
        print(f"\n[SIGNALS GENERATED] Successfully created {len(saved)} Signal Cards in {SIGNALS_DIR}:")
        for s in saved:
            print(f"  - {s.name}")


if __name__ == "__main__":
    main()
