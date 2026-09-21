#!/usr/bin/env python3
"""Viral Recipe Extractor: Deconstruct viral posts into pure structural formulas and map to BUSINESS-SOT.md slots."""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parents[2]
FORMULAS_PATH = SKILL_ROOT / "references" / "viral_formulas.json"
SOT_PATH = REPO_ROOT / "content" / "BUSINESS-SOT.md"
BRIEFS_DIR = REPO_ROOT / "content" / "campaigns" / "viral-briefs"


def load_sot() -> Dict[str, Any]:
    """Parse key facts dynamically from BUSINESS-SOT.md without industry hardcoding."""
    if not SOT_PATH.exists():
        return {
            "product_name": "我们的品牌",
            "tagline": "专业高效的行业垂直解决方案",
            "icp": "行业从业者 / 业务决策人 / 团队负责人",
            "pain_points": ["市面方案成本高且流程繁琐", "缺乏真实事实支撑容易踩坑", "规则多变成效难保证"],
            "proof_points": ["核心架构经过实践验证稳定可靠", "数据与内容真实可追溯"],
            "offer": "《完整实操架构与避坑指南》"
        }

    text = SOT_PATH.read_text(encoding="utf-8")
    
    product_name = "我们的产品"
    tagline = "专业高效的行业垂直解决方案"
    icp = "行业从业者 / 业务决策人"
    pain_points = []
    proof_points = []
    offer = "《实操避坑自查清单》"

    m_name = re.search(r"产品/服务全称[：:]\s*([^\n]+)", text)
    if m_name:
        product_name = m_name.group(1).strip("* ")

    m_tagline = re.search(r"一句话定位\s*\(Tagline\)[：:]\s*([^\n]+)", text)
    if m_tagline:
        tagline = m_tagline.group(1).strip("* ")

    m_icp = re.search(r"身份/角色[：:]\s*([^\n]+)", text)
    if m_icp:
        icp = m_icp.group(1).strip("* ")

    raw_pains = re.findall(r"痛点\s*\d+[：:]\s*[“\"]([^”\"]+)[”\"]", text)
    if raw_pains:
        pain_points = raw_pains

    # Extract proof points from SOT
    m_proofs = re.search(r"已验证事实与硬核数据.*?\n((?:\s*-\s*[^\n]+\n)+)", text)
    if m_proofs:
        proof_lines = re.findall(r"-\s*([^\n]+)", m_proofs.group(1))
        proof_points = [p.strip() for p in proof_lines if p.strip()]

    m_offer = re.search(r"\$0 Offer 名称[：:]\s*([^\n]+)", text)
    if m_offer:
        offer = m_offer.group(1).strip("* ")

    if not pain_points:
        pain_points = ["市面方案成本高且执行繁琐", "虚假宣传多、落地效果差"]
    if not proof_points:
        proof_points = ["经过生产实测检验具备高稳定性", "内容与方案全流程可追溯"]

    return {
        "product_name": product_name,
        "tagline": tagline,
        "icp": icp,
        "pain_points": pain_points,
        "proof_points": proof_points,
        "offer": offer
    }


def fetch_url_content(url: str) -> Dict[str, str]:
    """Fetch webpage text and title using Jina Reader (free, no token needed)."""
    jina_url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(
        jina_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode("utf-8")
            title = ""
            m_title = re.search(r"^Title:\s*(.+)$", content, re.MULTILINE)
            if m_title:
                title = m_title.group(1).strip()
            return {"title": title, "content": content}
    except Exception as e:
        print(f"[-] Jina Reader fetch failed: {e}. Falling back to basic request...", file=sys.stderr)
        try:
            req_direct = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_direct, timeout=15) as resp:
                raw_html = resp.read().decode("utf-8", errors="ignore")
                m_title = re.search(r"<title>(.*?)</title>", raw_html, re.IGNORECASE)
                title = m_title.group(1).strip() if m_title else url
                clean_text = re.sub(r"<[^>]+>", " ", raw_html)
                clean_text = re.sub(r"\s+", " ", clean_text)[:2000]
                return {"title": title, "content": clean_text}
        except Exception as e2:
            return {"title": url, "content": f"Failed to fetch {url}: {e2}"}


def search_viral_candidate(query: str, platform: str = "duckduckgo_html") -> Dict[str, str]:
    """Use union_search_cli to search a viral candidate post."""
    cli_path = REPO_ROOT / "tools" / "union-search" / "union_search_cli.py"
    if not cli_path.exists():
        return {"title": f"Search: {query}", "content": f"Query: {query}"}

    import subprocess
    cmd = [
        sys.executable, str(cli_path), "platform", platform, query, "--limit", "3"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            items = data.get("data", {}).get("items", [])
            if items:
                first = items[0]
                return {
                    "title": first.get("title", ""),
                    "content": first.get("body", "") or first.get("description", ""),
                    "url": first.get("href", "") or first.get("html_url", "")
                }
    except Exception as e:
        print(f"[-] Search viral candidate failed: {e}", file=sys.stderr)
    return {"title": f"Viral Topic: {query}", "content": query, "url": ""}


def match_formula(title: str, content: str, formulas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Score and match content against known viral formulas."""
    text = (title + " " + content).lower()
    
    scores = {}
    for f in formulas:
        fid = f["id"]
        score = 0
        if fid == "ANTI_COMMON_SENSE":
            if any(k in text for k in ["为什么", "交智商税", "别再", "被骗", "真相", "其实", "大错特错", "why", "stop"]):
                score += 3
        elif fid == "BEFORE_AFTER_GAP":
            if any(k in text for k in ["从", "到", "戒掉", "突破", "月入", "翻倍", "30天", "before", "after"]):
                score += 3
        elif fid == "FAILURE_POSTMORTEM":
            if any(k in text for k in ["踩坑", "血泪", "自爆", "教训", "亏损", "后悔", "千万别", "mistake", "regret"]):
                score += 4
        elif fid == "CURATED_GOLDMINE":
            if any(k in text for k in ["神器", "清单", "私藏", "藏宝箱", "推荐", "工具箱", "tools", "curated", "list"]):
                score += 3
        elif fid == "TROJAN_HORSE_CASE":
            if any(k in text for k in ["拆解", "深扒", "复盘", "底层架构", "为什么能", "tear down", "case study"]):
                score += 3
        elif fid == "CONTRARIAN_HOTTAKE":
            if any(k in text for k in ["停止盲目", "泡沫", "残酷现实", "清醒", "逆风", "谎言"]):
                score += 3
        scores[fid] = score

    best_fid = max(scores, key=scores.get) if scores else "ANTI_COMMON_SENSE"
    if scores.get(best_fid, 0) == 0:
        best_fid = "ANTI_COMMON_SENSE"

    for f in formulas:
        if f["id"] == best_fid:
            return f
    return formulas[0]


def build_recipe_brief(
    source_title: str,
    source_content: str,
    source_url: str,
    formula: Dict[str, Any],
    sot: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate the complete Viral Recipe Brief mapping SOT to formula slots dynamically."""
    today = datetime.now().strftime("%Y%m%d")
    clean_title = re.sub(r"[^\w\u4e00-\u9fff]+", "-", source_title).strip("-")
    slug = clean_title[:28].rstrip("-").lower() or "viral-topic"
    recipe_id = f"VRB-{today}-{slug}"

    target_role = sot.get("icp", "").split("/")[0].strip() or "行业从业者"
    product_name = sot.get("product_name", "我们的方案")
    offer = sot.get("offer", "完整落地自查手册")
    pains = sot.get("pain_points", [])
    proofs = sot.get("proof_points", [])

    # Extract action dynamically
    action_candidate = "业务运营与落地交付"
    if "做" in source_title:
        m_act = re.search(r"做([^\s？?，,！!]+)", source_title)
        if m_act:
            action_candidate = m_act.group(1)[:15]
    elif "学" in source_title:
        m_act = re.search(r"学([^\s？?，,！!]+)", source_title)
        if m_act:
            action_candidate = m_act.group(1)[:15]

    common_mistake = pains[0] if pains else "盲目套用市面低效的伪捷径与套话"
    hidden_truth = proofs[0] if proofs else "真正起效的从来不是表面的跟风炒作，而是可追溯的底层真实事实与稳健闭环"

    step1 = f"步骤1 (事实锚定): 明确{product_name}核心事实源与交付边界，杜绝事实幻觉"
    step2 = f"步骤2 (去油精炼): 剔除假大空公文套话，注入真实参数与实操细节"
    step3 = f"步骤3 (稳健闭环): 落实标准化合规作业机制，实现长效确定性交付"

    if len(proofs) >= 1:
        step1 = f"步骤1 (锚定真相): {proofs[0]}"
    if len(proofs) >= 2:
        step2 = f"步骤2 (去油打散): {proofs[1]}"
    if len(pains) >= 3:
        step3 = f"步骤3 (稳健避坑): 针对“{pains[2]}”建立标准化安全关口"

    slots = {
        "target_role": target_role,
        "action": action_candidate,
        "common_mistake": common_mistake,
        "hidden_truth": hidden_truth,
        "rock_bottom": f"在{action_candidate}上投入大量精力与成本，却频繁遭遇低效与无结果",
        "peak_result": f"跑通可追溯的标准化交付流程，建立起可持续的确定性增长闭环",
        "common_focus": "无脑跟风虚热概念与盲目堆量",
        "real_lever": f"建立单一事实源支撑 + 诚恳去油表达 + 稳健执行架构",
        "benchmark_name": source_title[:25] or "标杆案例",
        "steps": [step1, step2, step3],
        "lead_magnet": f"评论区回复【领取】，免费获取{offer}"
    }

    # Generate customized hooks based on formula patterns
    generated_hooks = []
    for pat in formula.get("hook_patterns", []):
        try:
            hook = pat.format(**slots)
            generated_hooks.append(hook)
        except Exception:
            generated_hooks.append(pat)

    brief = {
        "recipe_id": recipe_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": {
            "title": source_title,
            "url": source_url,
            "excerpt": source_content[:300]
        },
        "formula": {
            "id": formula["id"],
            "name": formula["name"],
            "emotional_driver": formula["emotional_driver"],
            "visual_theme": formula.get("visual_theme", "dark_tech"),
            "card_badge": formula.get("card_badge", "实测避坑")
        },
        "mapped_slots": slots,
        "story_beats": formula.get("story_beats", []),
        "generated_hooks": generated_hooks,
        "target_sot": {
            "product_name": sot["product_name"],
            "tagline": sot["tagline"],
            "offer": sot["offer"]
        }
    }
    return brief


def save_brief(brief: Dict[str, Any]) -> Path:
    """Save brief as JSON and human-readable Markdown."""
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
title: "Viral Recipe Brief: {brief['recipe_id']}"
recipe_id: "{brief['recipe_id']}"
formula: "{brief['formula']['name']}"
created_at: {brief['created_at']}
status: ready_for_factory
---

# 爆款配方指令单 (Viral Recipe Brief): {brief['recipe_id']}

> **逆向解构来源**：[{brief['source']['title']}]({brief['source']['url'] or '#'})  
> **爆款公式类型**：`{brief['formula']['id']}` ({brief['formula']['name']})  
> **核心情绪激发**：{brief['formula']['emotional_driver']}  
> **大字报徽标与主题**：`{brief['formula']['card_badge']}` | `{brief['formula']['visual_theme']}`

---

## 1. 黄金开口钩子库 (Top Hooks)
{hooks_md}

---

## 2. 爆款叙事节奏骨架 (Story Beats)
{beats_md}

---

## 3. 品牌底层事实槽位映射 (SOT Slots)
- **受众角色 (target_role)**: {slots['target_role']}
- **受众行为 (action)**: {slots['action']}
- **大众误区 (common_mistake)**: {slots['common_mistake']}
- **底层真相 (hidden_truth)**: {slots['hidden_truth']}
- **硬核三步实操清单 (steps)**:
{steps_md}
- **转化诱饵 (lead_magnet)**: {slots['lead_magnet']}

---

## 4. 下一步交接指令 (Handoff to Content Factory)
请将本文档路径直接传递给内容工厂执行批量写作与 3:4 渲染：
```bash
python .agent/skills/viral-hacker/scripts/bridge_to_factory.py --brief content/campaigns/viral-briefs/{json_path.name}
```
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return json_path


def main():
    parser = argparse.ArgumentParser(description="Viral Recipe Extractor")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL of a viral post to reverse-engineer")
    group.add_argument("--text", help="Raw text of a viral post")
    group.add_argument("--file", help="Path to text file containing post")
    group.add_argument("--search", help="Search query to find a top viral candidate via union-search")

    parser.add_argument("--platform", default="duckduckgo_html", help="Search platform if --search is used")
    parser.add_argument("--formula", help="Force specific formula ID (ANTI_COMMON_SENSE, BEFORE_AFTER_GAP, etc.)")
    parser.add_argument("--to-factory", action="store_true", help="Immediately invoke bridge_to_factory to generate drafts and card")
    args = parser.parse_args()

    source_title = ""
    source_content = ""
    source_url = ""

    if args.url:
        print(f"[*] Fetching viral post from: {args.url} ...")
        res = fetch_url_content(args.url)
        source_title = res["title"]
        source_content = res["content"]
        source_url = args.url
    elif args.text:
        source_title = args.text.split("\n")[0][:50]
        source_content = args.text
    elif args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
        source_title = raw.split("\n")[0][:50]
        source_content = raw
    elif args.search:
        print(f"[*] Searching viral candidate on {args.platform} for: '{args.search}' ...")
        res = search_viral_candidate(args.search, args.platform)
        source_title = res["title"]
        source_content = res["content"]
        source_url = res.get("url", "")

    print(f"[+] Post Title: {source_title}")

    with open(FORMULAS_PATH, "r", encoding="utf-8") as f:
        formulas = json.load(f)

    sot = load_sot()

    if args.formula:
        formula = next((f for f in formulas if f["id"] == args.formula), formulas[0])
    else:
        formula = match_formula(source_title, source_content, formulas)

    print(f"[+] Matched Viral Formula: {formula['name']} ({formula['id']})")
    print(f"[+] Emotional Driver: {formula['emotional_driver']}")

    brief = build_recipe_brief(source_title, source_content, source_url, formula, sot)
    json_path = save_brief(brief)
    md_path = json_path.with_suffix(".md")

    print(f"\n[✓] Viral Recipe Brief generated successfully!")
    print(f"    • JSON: {json_path}")
    print(f"    • Markdown: {md_path}")
    print(f"\n[★] Top Generated Hook:")
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
