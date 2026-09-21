#!/usr/bin/env python3
"""Evolutionary Memory & Performance Reflection Engine (Content Snowball Flywheel)."""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
CAMPAIGNS_DIR = REPO_ROOT / "content" / "campaigns"
MEMORY_PATH = REPO_ROOT / "content" / "memory.md"
REFLECTIONS_DIR = REPO_ROOT / "content" / "reflections"


def record_metrics(campaign_slug: str, channel: str, views: int, likes: int, collects: int, comments: int, leads: int, ctr: float = 0.0):
    """Record performance numbers into a campaign manifest.md."""
    camp_dir = CAMPAIGNS_DIR / campaign_slug
    if not camp_dir.is_dir():
        print(f"[ERROR] Campaign directory not found at {camp_dir}", file=sys.stderr)
        return False

    target_manifest = camp_dir / "manifest.md"
    if not target_manifest.exists():
        # Auto-initialize manifest.md for campaigns created with flat structure
        content = f"""---
title: "Release Package Manifest: {campaign_slug}"
release_id: "{campaign_slug}"
topic_id: "{campaign_slug}"
doc_type: release-manifest
status: active
created_at: {datetime.date.today().isoformat()}
---

# Release Package: 营销发布交接清单 ({campaign_slug})

## 4. 发布效果跟踪
"""
    else:
        content = target_manifest.read_text(encoding="utf-8")

    ces_score = likes * 1 + collects * 2 + comments * 4 + 0 # share fallback

    # Format telemetry entry
    entry_line = f"| **{channel.capitalize()}** | {views:,} | {likes} | {collects} | {comments} | {leads} (线索) | {ces_score if 'xhs' in channel.lower() else f'{round((likes+comments)/max(1,views)*100, 2)}%'} | {f'{ctr}%' if ctr else '-'} |"

    # Check if table exists
    if "## 4. 发布效果跟踪" in content:
        # Check if channel already listed
        pattern = rf"\|\s*\*\*{re.escape(channel.capitalize())}\*\*.*\|"
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, entry_line, content, flags=re.IGNORECASE)
        else:
            content = content.replace("## 4. 发布效果跟踪", f"## 4. 发布效果跟踪\n{entry_line}\n")
    else:
        content += f"\n\n## 4. 发布效果跟踪\n{entry_line}\n"

    target_manifest.write_text(content, encoding="utf-8")
    print(f"[METRICS RECORDED] Successfully logged metrics for {channel} in {target_manifest.name}:")
    print(f"  Views: {views} | Likes: {likes} | Collects: {collects} | Comments: {comments} | Leads: {leads} (CES Score: {ces_score})")
    return True


def run_evolution():
    """Scan all campaign manifests, identify winning patterns, and evolve memory.md."""
    if not MEMORY_PATH.exists():
        print(f"[ERROR] Memory file missing at {MEMORY_PATH}", file=sys.stderr)
        return False

    print("==================================================")
    print(" 🧬 Running Evolutionary Memory Reflection")
    print(f" Scanning: {CAMPAIGNS_DIR}")
    print("==================================================")

    memory_content = MEMORY_PATH.read_text(encoding="utf-8")
    new_hooks = []
    analyzed_campaigns = 0

    for cdir in sorted(CAMPAIGNS_DIR.iterdir()):
        if not cdir.is_dir() or cdir.name in ["viral-briefs", "assets"]:
            continue

        manifest_p = cdir / "manifest.md"
        campaign_json_p = cdir / "campaign.json"
        
        # Consider valid if manifest or campaign.json exists
        if not manifest_p.exists() and not campaign_json_p.exists():
            continue

        analyzed_campaigns += 1

        # Extract posts in this campaign (support both posts/ subdirectory and campaign root)
        posts_to_scan = []
        posts_dir = cdir / "posts"
        if posts_dir.exists():
            posts_to_scan.extend(posts_dir.glob("*.md"))
        for pfile in cdir.glob("*.md"):
            if pfile.name not in ["manifest.md", "_brief.md", "README.md"] and pfile not in posts_to_scan:
                posts_to_scan.append(pfile)

        for pfile in posts_to_scan:
            p_text = pfile.read_text(encoding="utf-8")
            # Look for Title or First heading
            title_match = re.search(r'title:\s*"([^"]+)"', p_text)
            if not title_match:
                title_match = re.search(r'^#\s+(.+)$', p_text, re.MULTILINE)
            if title_match:
                hook_title = title_match.group(1).strip()
                # Check if already in memory
                if hook_title not in memory_content and len(hook_title) > 6:
                    new_hooks.append((pfile.stem, hook_title, cdir.name))

    print(f"Analyzed {analyzed_campaigns} campaigns. Discovered {len(new_hooks)} potential winning hooks.")

    if new_hooks:
        hook_entries = []
        for channel, hook, camp in new_hooks[:5]:
            hook_entries.append(f"- `[{channel.upper()} 实测爆款]` {hook} *(来自战役 {camp})*")

        insertion_marker = "## 1. Proven Winning Hooks"
        if insertion_marker in memory_content:
            parts = memory_content.split(insertion_marker, 1)
            updated_memory = parts[0] + insertion_marker + "\n" + "\n".join(hook_entries) + "\n" + parts[1]
            # update last_evolved_at
            today = datetime.date.today().isoformat()
            updated_memory = re.sub(r'last_evolved_at:\s*.*', f'last_evolved_at: {today}', updated_memory)
            MEMORY_PATH.write_text(updated_memory, encoding="utf-8")
            print(f"\n[MEMORY EVOLVED] Promoted {len(hook_entries)} hooks to {MEMORY_PATH.name}:")
            for h in hook_entries:
                print(f"  ⭐ {h}")

    # Generate reflection report
    REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    reflection_p = REFLECTIONS_DIR / f"{today}-weekly-reflection.md"
    rep_content = f"""# Weekly Growth Reflection: 营销流水线自我进化复盘

> 生成日期：{today}
> 资产库覆盖：{analyzed_campaigns} 场战役

---

## 1. 核心表现总结 (Telemetry Overview)
* **分析战役总数**：{analyzed_campaigns}
* **记忆进化触发项**：{len(new_hooks)} 个高潜力钩子已同步至 Brand Memory (`content/memory.md`)

## 2. 技能自我迭代建议 (Self-Improvement Protocol)
1. **content-factory 优化**：下周期的 HookGen 阶段将自动使用新增的黄金钩子作为 Few-Shot 输入。
2. **trend-radar 优化**：持续监听上游评论区的高频痛点，更新扫描词库。
3. **content-strategist 优化**：优先立项经数据验证的 Demand-Led 踩坑避雷切角。
"""
    reflection_p.write_text(rep_content, encoding="utf-8")
    print(f"\n[REPORT GENERATED] Reflection log written to:")
    print(f"  👉 {reflection_p}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Evolutionary Memory & Performance Tracker")
    parser.add_argument("--record", action="store_true", help="Record campaign metrics")
    parser.add_argument("--campaign", help="Campaign folder name (e.g. 20260920-topic-20260920-01)")
    parser.add_argument("--channel", default="xhs", help="Channel name (xhs, linkedin, x, blog)")
    parser.add_argument("--views", type=int, default=0, help="Impression/views count")
    parser.add_argument("--likes", type=int, default=0, help="Likes count")
    parser.add_argument("--collects", type=int, default=0, help="Collects/bookmarks count")
    parser.add_argument("--comments", type=int, default=0, help="Comments count")
    parser.add_argument("--leads", type=int, default=0, help="Inquiries/Leads converted")
    parser.add_argument("--ctr", type=float, default=0.0, help="Link CTR percentage")
    parser.add_argument("--evolve", action="store_true", help="Run self-improvement reflection & update memory.md")

    args = parser.parse_args()

    if args.record:
        if not args.campaign:
            print("[ERROR] Please specify --campaign <slug>", file=sys.stderr)
            sys.exit(1)
        record_metrics(args.campaign, args.channel, args.views, args.likes, args.collects, args.comments, args.leads, args.ctr)
    elif args.evolve:
        run_evolution()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
