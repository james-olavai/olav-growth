#!/usr/bin/env python3
"""Trend Jacker: Scan real-time trending topics and build high-urgency Semantic Bridge briefs."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parents[2]
ANGLES_PATH = SKILL_ROOT / "references" / "trend_jack_angles.json"
SOT_PATH = REPO_ROOT / "content" / "BUSINESS-SOT.md"
BRIEFS_DIR = REPO_ROOT / "content" / "campaigns" / "viral-briefs"


def load_angles() -> List[Dict[str, Any]]:
    with open(ANGLES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sot_keywords() -> Dict[str, Any]:
    """Dynamically parse product keywords, ICP, proof points, and offer from SOT."""
    if not SOT_PATH.exists():
        return {
            "product": "我们的品牌",
            "keywords": ["专业交付", "效率提升", "长效避坑", "稳健增长"],
            "offer": "《完整实操避坑手册》",
            "root_cause": "缺乏真实事实源支撑的盲目跟风是失败根本原因",
            "target_role": "行业从业者与决策人"
        }

    text = SOT_PATH.read_text(encoding="utf-8")
    
    product_name = "我们的品牌"
    m_name = re.search(r"产品/服务全称[：:]\s*([^\n]+)", text)
    if m_name:
        product_name = m_name.group(1).strip("* ")

    icp = "行业从业者与决策人"
    m_icp = re.search(r"身份/角色[：:]\s*([^\n]+)", text)
    if m_icp:
        icp = m_icp.group(1).strip("* ")

    offer = "《完整实操落地指南》"
    m_offer = re.search(r"\$0 Offer 名称[：:]\s*([^\n]+)", text)
    if m_offer:
        offer = m_offer.group(1).strip("* ")

    root_cause = "缺乏单一事实源支撑的盲目盲从是导致低质交付与受阻的元凶"
    m_proofs = re.search(r"已验证事实与硬核数据.*?\n((?:\s*-\s*[^\n]+\n)+)", text)
    if m_proofs:
        proof_lines = re.findall(r"-\s*([^\n]+)", m_proofs.group(1))
        if proof_lines:
            root_cause = proof_lines[0].strip()

    # Dynamically extract all core keywords from SOT text
    keywords = set()
    for line in text.splitlines():
        if any(marker in line for marker in ["定位", "关键词", "ICP", "痛点", "核心价值", "全称"]):
            words = re.findall(r'[\w\u4e00-\u9fa5]{2,}', line)
            for w in words:
                if len(w) >= 2 and w not in ["产品", "核心", "定位", "用户", "方案", "客户", "痛点", "业务"]:
                    keywords.add(w)

    return {
        "product": product_name,
        "keywords": list(keywords)[:15] if keywords else ["标准化交付", "去油自检", "真实可追溯"],
        "offer": offer,
        "root_cause": root_cause,
        "target_role": icp.split("/")[0].strip() if "/" in icp else icp
    }


def pick_best_angle(topic: str, angles: List[Dict[str, Any]], forced_angle: str = None) -> Dict[str, Any]:
    if forced_angle:
        for a in angles:
            if a["id"] == forced_angle:
                return a

    t_lower = topic.lower()
    if any(k in t_lower for k in ["涨价", "宕机", "下架", "封禁", "限制", "停服", "收费", "outage", "pricing", "ban"]):
        return next(a for a in angles if a["id"] == "rescuer")
    elif any(k in t_lower for k in ["爆火", "登顶", "融资", "开源", "破纪录", "架构", "增长", "launch", "star"]):
        return next(a for a in angles if a["id"] == "architect")
    elif any(k in t_lower for k in ["吐槽", "梗", "笑死", "打工人", "破防", "离谱", "meme"]):
        return next(a for a in angles if a["id"] == "satirist")
    return next(a for a in angles if a["id"] == "truth_teller")


def build_trend_brief(topic: str, angle: Dict[str, Any], sot: Dict[str, Any]) -> Dict[str, Any]:
    today = datetime.now().strftime("%Y%m%d")
    clean_topic = re.sub(r"[^\w\u4e00-\u9fff]+", "-", topic).strip("-")
    slug = clean_topic[:24].rstrip("-").lower() or "trend-topic"
    recipe_id = f"VRB-{today}-trend-{slug}"

    hook = angle["hook_formula"].format(trend_keyword=topic)
    target_role = sot.get("target_role", "行业从业者与决策人")
    
    slots = {
        "target_role": target_role,
        "action": f"紧跟【{topic}】热点浪潮",
        "common_mistake": "盲目跟风硬蹭，内容空洞缺乏事实支撑被用户反感",
        "hidden_truth": f"借势的核心不是盲从热点，而是透过【{topic}】借道输出我们自有的硬核生产力方法论（{sot.get('root_cause')}）",
        "steps": [
            f"第一步 (借势切入): 借【{topic}】引发全行业关注的关键痛点破冰",
            f"第二步 (穿透拆解): 揭示背后的底层规则与行业真相（{sot.get('root_cause')}）",
            f"第三步 (落地解法): 交付一套可直接落地执行的稳健避坑闭环"
        ],
        "lead_magnet": f"评论区发送【{topic[:4]}】，立即免费获取完整自查方案与{sot['offer']}"
    }

    brief = {
        "recipe_id": recipe_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": {
            "title": f"实时热点侦测: {topic}",
            "url": "live_trend",
            "excerpt": f"针对全网突发热点【{topic}】构建的快速借势战役"
        },
        "formula": {
            "id": f"TREND_JACK_{angle['id'].upper()}",
            "name": f"借势蹭流量 · {angle['name']}",
            "emotional_driver": angle["description"],
            "visual_theme": angle["visual_theme"],
            "card_badge": angle["card_badge"]
        },
        "mapped_slots": slots,
        "story_beats": angle["narrative_arc"],
        "generated_hooks": [
            hook,
            f"关于【{topic}】，说点大多数人不敢公开讲的大实话……",
            f"看懂【{topic}】背后的这套底层逻辑，普通人也能直接复用"
        ],
        "target_sot": {
            "product_name": sot["product"],
            "offer": sot["offer"]
        }
    }
    return brief


def save_brief(brief: Dict[str, Any]) -> Path:
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    recipe_id = brief["recipe_id"]
    json_path = BRIEFS_DIR / f"{recipe_id}.json"
    md_path = BRIEFS_DIR / f"{recipe_id}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)

    slots = brief["mapped_slots"]
    hooks_md = "\n".join([f"- **Hook {i+1}**: {h}" for i, h in enumerate(brief["generated_hooks"])])
    beats_md = "\n".join([f"- {b}" for b in brief["story_beats"]])
    steps_md = "\n".join([f"  {s}" for s in slots["steps"]])

    md_content = f"""---
title: "Trend-Jack Brief: {brief['recipe_id']}"
recipe_id: "{brief['recipe_id']}"
formula: "{brief['formula']['name']}"
created_at: {brief['created_at']}
status: ready_for_factory
---

# 实时借势配方简报 (Trend-Jack Brief): {brief['recipe_id']}

> **借势突发热点**：`{brief['source']['title']}`  
> **采用切角类型**：`{brief['formula']['name']}`  
> **视觉主题与徽标**：`{brief['formula']['card_badge']}` | `{brief['formula']['visual_theme']}`

---

## 1. 闪电首发钩子 (Instant Hooks)
{hooks_md}

---

## 2. 借势叙事节拍器 (Narrative Arc)
{beats_md}

---

## 3. 语义搭桥事实槽位 (Semantic Bridge Slots)
- **核心论点**: {slots['hidden_truth']}
- **实操转化清单**:
{steps_md}
- **时效引流暗号**: {slots['lead_magnet']}

---

## 4. 下一步交接指令 (Handoff to Content Factory)
```bash
python .agent/skills/viral-hacker/scripts/bridge_to_factory.py --brief content/campaigns/viral-briefs/{json_path.name}
```
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return json_path


def main():
    parser = argparse.ArgumentParser(description="Trend Jacker: Fast Semantic Bridge for Live Trends")
    parser.add_argument("--topic", required=True, help="Live trending event or keyword to hijack")
    parser.add_argument("--angle", choices=["truth_teller", "rescuer", "architect", "satirist"], help="Specific trend-jack angle")
    parser.add_argument("--to-factory", action="store_true", help="Immediately invoke bridge_to_factory to generate drafts and card")
    args = parser.parse_args()

    angles = load_angles()
    sot = load_sot_keywords()

    angle = pick_best_angle(args.topic, angles, args.angle)
    print(f"[*] Analyzing Trend: '{args.topic}'")
    print(f"[+] Selected Hijack Angle: {angle['name']}")
    print(f"[+] Theme: {angle['visual_theme']} | Badge: {angle['card_badge']}")

    brief = build_trend_brief(args.topic, angle, sot)
    json_path = save_brief(brief)
    md_path = json_path.with_suffix(".md")

    print(f"\n[✓] Trend-Jack Brief generated successfully!")
    print(f"    • JSON: {json_path}")
    print(f"    • Markdown: {md_path}")
    print(f"\n[★] Golden Blitz Hook:")
    print(f"    \"{brief['generated_hooks'][0]}\"")

    if args.to_factory:
        bridge_script = SKILL_ROOT / "scripts" / "bridge_to_factory.py"
        if bridge_script.exists():
            import subprocess
            print(f"\n[*] Handoff to Content Factory...")
            subprocess.run([sys.executable, str(bridge_script), "--brief", str(json_path)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
