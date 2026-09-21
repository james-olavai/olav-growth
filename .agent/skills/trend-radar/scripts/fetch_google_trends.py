#!/usr/bin/env python3
"""Fetch trending searches from Google Trends RSS feeds without requiring API keys."""

import argparse
import datetime
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
SIGNALS_DIR = REPO_ROOT / "content" / "candidate_signals"

SUPPORTED_GEOS = {
    "US": "United States",
    "TW": "Taiwan",
    "HK": "Hong Kong",
    "SG": "Singapore",
    "JP": "Japan",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France"
}


def fetch_google_trends(geo="US", limit=20, filter_kw=None):
    url = f"https://trends.google.com/trending/rss?geo={geo.upper()}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read()
    except Exception as e:
        print(f"[ERROR] Failed to fetch Google Trends for geo={geo}: {e}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(content)
    except Exception as e:
        print(f"[ERROR] XML parsing error: {e}", file=sys.stderr)
        return []

    ns = {"ht": "https://trends.google.com/trending/rss"}
    results = []

    for item in root.findall(".//item"):
        title_el = item.find("title")
        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        if not title:
            continue

        traffic_el = item.find("ht:approx_traffic", ns)
        traffic = traffic_el.text.strip() if traffic_el is not None and traffic_el.text else "N/A"

        pub_date_el = item.find("pubDate")
        pub_date = pub_date_el.text.strip() if pub_date_el is not None and pub_date_el.text else ""

        news_items = []
        for news in item.findall("ht:news_item", ns):
            ntitle_el = news.find("ht:news_item_title", ns)
            nurl_el = news.find("ht:news_item_url", ns)
            nsource_el = news.find("ht:news_item_source", ns)
            ntitle = ntitle_el.text.strip() if ntitle_el is not None and ntitle_el.text else ""
            nurl = nurl_el.text.strip() if nurl_el is not None and nurl_el.text else ""
            nsource = nsource_el.text.strip() if nsource_el is not None and nsource_el.text else ""
            if ntitle:
                news_items.append({"title": ntitle, "url": nurl, "source": nsource})

        # Apply keyword filtering if provided
        if filter_kw:
            target_text = (title + " " + " ".join(n["title"] for n in news_items)).lower()
            if not any(k.lower() in target_text for k in filter_kw):
                continue

        results.append({
            "query": title,
            "geo": geo.upper(),
            "approx_traffic": traffic,
            "pub_date": pub_date,
            "news": news_items
        })

        if len(results) >= limit:
            break

    return results


def emit_signal_cards(trends, out_dir=SIGNALS_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().strftime("%Y%m%d")
    emitted = []

    for idx, t in enumerate(trends, 1):
        slug = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]+', '-', t["query"].lower()).strip('-')
        sig_id = f"SIG-{today}-GT{idx:02d}"
        file_path = out_dir / f"{sig_id.lower()}-{slug}.md"

        news_lines = "\n".join(f"  - [{n['source']}] [{n['title']}]({n['url']})" for n in t["news"][:3])
        top_news_url = t["news"][0]["url"] if t["news"] else f"https://trends.google.com/trends/explore?q={t['query']}"

        card_content = f"""---
title: "Signal Card: {t['query']} (Google Trends {t['geo']})"
signal_id: "{sig_id}"
doc_type: candidate-signal
status: candidate
created_at: {datetime.date.today().isoformat()}
source_type: "google-trends"
geo: "{t['geo']}"
traffic: "{t['approx_traffic']}"
tags:
  - doc/signal
  - status/candidate
  - source/google-trends
---

# Signal Card: {t['query']}

> 来源：Google Trends ({t['geo']} 每日热搜榜，预估热度：{t['approx_traffic']})

---

* **Signal ID**：`{sig_id}`
* **录入日期**：{datetime.date.today().isoformat()}
* **信号来源类型**：Google Trends 热搜榜
* **来源链接 / 证据凭证**：<{top_news_url}>
* **原始热点新闻 / 搜索词**：
{news_lines if news_lines else "  - (无直接附带新闻项)"}
* **核心痛点/情绪标签**：[时事热点 / 行业变局 / 公众好奇]
* **关联业务核心**：[待 content-strategist 关联业务 SOT]
* **初步切入设想**：从【{t['query']}】引发的关注延伸至我们能提供的解决方案或行业洞察。
"""
        file_path.write_text(card_content, encoding="utf-8")
        emitted.append(file_path)

    return emitted


def main():
    parser = argparse.ArgumentParser(description="Google Trends Daily Search Feed Fetcher")
    parser.add_argument("--geo", default="US", help=f"Country code ({', '.join(SUPPORTED_GEOS.keys())})")
    parser.add_argument("--limit", type=int, default=15, help="Number of trend items")
    parser.add_argument("--filter", nargs="*", help="Filter keywords")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--emit-signals", action="store_true", help="Save as Signal Cards in content/candidate_signals/")

    args = parser.parse_args()
    trends = fetch_google_trends(geo=args.geo, limit=args.limit, filter_kw=args.filter)

    if args.json:
        print(json.dumps(trends, ensure_ascii=False, indent=2))
        return

    print(f"\n==================================================")
    print(f"  Google Trends ({args.geo.upper()} - {SUPPORTED_GEOS.get(args.geo.upper(), 'Unknown')})")
    print(f"  Fetched {len(trends)} trending items")
    print(f"==================================================")

    for idx, t in enumerate(trends, 1):
        print(f"\n{idx}. [{t['approx_traffic']}] {t['query']}")
        for n in t["news"][:2]:
            print(f"   • {n['title']} ({n['source']})")

    if args.emit_signals:
        saved = emit_signal_cards(trends)
        print(f"\n[SIGNALS GENERATED] Successfully created {len(saved)} Signal Cards in {SIGNALS_DIR}:")
        for s in saved:
            print(f"  - {s.name}")


if __name__ == "__main__":
    main()
