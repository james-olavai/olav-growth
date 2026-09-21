#!/usr/bin/env python3
"""Bridge from Viral Recipe Brief to Content Factory: Generate native drafts and 3:4 cards."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parents[2]
FACTORY_SCRIPTS = REPO_ROOT / ".agent" / "skills" / "content-factory" / "scripts"
CAMPAIGNS_DIR = REPO_ROOT / "content" / "campaigns"

if str(FACTORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(FACTORY_SCRIPTS))

try:
    from card_renderer import render_svg_card, THEMES
    from prompt_chain import inject_fuzzy_variables, scan_for_grease
except ImportError as e:
    print(f"[-] Warning: Failed to import factory scripts: {e}", file=sys.stderr)
    render_svg_card = None
    inject_fuzzy_variables = lambda lang="zh": {"emotion": "真实实操复盘", "filler": "说实话"}
    scan_for_grease = lambda t, c=None: []


THEME_MAP = {
    "dark_tech": "dark_tech",
    "cyber_blue": "dark_tech",
    "warm_editorial": "warm_editorial",
    "clean_business": "clean_business",
    "emerald_growth": "clean_business",
    "sunset_gradient": "warm_editorial",
    "deep_purple": "deep_purple"
}


def build_platform_drafts(brief: Dict[str, Any], fuzzy: Dict[str, str], card_rel_path: str) -> Dict[str, str]:
    slots = brief["mapped_slots"]
    formula = brief["formula"]
    top_hook = brief["generated_hooks"][0]
    steps = slots.get("steps", [])
    step_texts = [re.sub(r"^步骤\s*\d+\s*[：:]\s*", "", s) for s in steps]
    lead_magnet = slots.get("lead_magnet", "评论区回复【领取】免费获取自查表")

    role_tag = re.sub(r"[^\w\u4e00-\u9fa5]+", "", slots.get("target_role", "干货分享"))[:8]
    tags_list = [f"#{role_tag}" if role_tag else "#实操分享", "#避坑指南", "#干货复盘", "#经验沉淀", "#行业洞察"]
    tags_str = " ".join(tags_list)

    # 1. Xiaohongshu (小红书)
    xhs_title = top_hook[:20] if len(top_hook) > 20 else top_hook
    xhs_content = f"""# {xhs_title}

{fuzzy['filler']}，关于【{slots['action']}】，市面上很多流传的信息都在把人往坑里带！
今天作为一线实干者，把真正踩过坑、验证过的底层真相拆开来说透。

---

📌 **【为什么传统的做法必死？】**
{slots['common_mistake']}
⚠️ **底层真相**：{slots['hidden_truth']}

---

🛠️ **【亲测有效的破局三步法】**
💡 **01. {steps[0] if len(steps) > 0 else '事实锚定'}**
💡 **02. {steps[1] if len(steps) > 1 else '去油精炼'}**
💡 **03. {steps[2] if len(steps) > 2 else '稳健闭环'}**

---

🎯 **【极简避坑自查】**
{lead_magnet}

💬 互动：你在【{slots['action']}】上遇到过最大的阻碍是什么？欢迎在评论区留言交流！

{tags_str}
"""

    # 2. X (Twitter) 5-Tweet Thread
    x_thread = f"""🧵 1/5
{top_hook}

大多数人在做【{slots['action']}】时，一直在被【{slots['common_mistake'][:25]}】所困扰。
花3分钟读完这篇，帮你省掉大量试错成本：👇

---

2/5
🚨 致命误区：
{slots['common_mistake']}

现实很残酷：{slots['hidden_truth']}
单纯靠战术勤奋掩盖底层逻辑缺失，只会在错误的路径上越跑越偏。

---

3/5
真正的破局路径只有3步：

1️⃣ {steps[0] if len(steps) > 0 else 'Step 1'}
2️⃣ {steps[1] if len(steps) > 1 else 'Step 2'}
3️⃣ {steps[2] if len(steps) > 2 else 'Step 3'}

---

4/5
关键在于“借壳不借肉”：
借用全网验证过的高转化互动节拍，但所有事实、案例与数据100%锚定自己的真实业务资产（SOT）。
既能保持极强的吸引力与留存，又能彻底杜绝虚假宣传与同质化。

---

5/5
完整实操自查指南与落地资料已整理完毕。
转发并回复【领取】，免费发送给你。
"""

    # 3. LinkedIn Thought Leadership
    linkedin_post = f"""{top_hook}

When analyzing why most initiatives around {slots['action']} fail, the pattern is surprisingly consistent.

The uncomfortable truth?
"{slots['hidden_truth']}"

Here is what fails:
❌ {slots['common_mistake']}
❌ Relying on generic buzzwords and surface-level tactics without verifiable facts
❌ Rushing to scale before validating the core execution pipeline

Here is the 3-pillar framework that actually drives sustainable results:

1. Ground Truth First (Single Source of Truth)
Never build on assumptions or hype. Anchor every claim, metric, and step to verified reality.

2. De-greasing & Candor
Eliminate corporate fluff and empty jargon. Speak honestly with transparent operational details and real parameters.

3. Resilient Delivery Loop
Build standardized, repeatable workflows that eliminate single points of failure and deliver predictable value.

{lead_magnet}

What has been your team's biggest operational bottleneck this quarter? Let's discuss in the comments.

#Strategy #Operations #Execution #Leadership #BusinessGrowth
"""

    # 4. WeChat / Blog Long-form
    blog_post = f"""# {top_hook}

> **调性基调**：{fuzzy['emotion']} | **去油审核**：通过

{fuzzy['filler']}，在任何行业中，只要深入一线实操，就会发现很多流传甚广的“常识”实际上经不起推敲。

## 一、为什么旧的套路正在加速失效？

很多团队以为只要紧跟热门概念，按部就班地套用大众模板，就能轻松拿到理想结果。
然而现实非常残酷：
- **大量投入资源却得不到真实反馈**；
- **表面忙碌繁荣，底层交付却漏洞百出**；
- **更严重的是，沉淀的长期资产容易因为脆弱的机制瞬间归零**。

底层根因究竟是什么？
{slots['hidden_truth']}。

## 二、从混乱到确定的“三步交付法”

经过系统性复盘与实操验证，我们梳理出了这套稳健、可复用的核心闭环：

### 1. {steps[0] if len(steps) > 0 else '第一步'}
建立唯一的事实锚点，确保所有对外输出与内部执行均百分之百有据可依，杜绝未经核验的自嗨。

### 2. {steps[1] if len(steps) > 1 else '第二步'}
注入一线真实实操数据与细节，系统级扫描并剔除假大空空洞套话与公文黑话，让表达回归务实与诚恳。

### 3. {steps[2] if len(steps) > 2 else '第三步'}
落实标准化合规作业与稳健执行机制，以可控的确定性流程替代侥幸试错。

## 三、写在最后

市场从不奖励盲目的战术盲从，只奖励直面底层规则的清醒者。
{lead_magnet}。
"""

    return {
        "xhs": xhs_content,
        "x": x_thread,
        "linkedin": linkedin_post,
        "blog": blog_post
    }


def main():
    parser = argparse.ArgumentParser(description="Bridge Viral Recipe Brief to Content Factory")
    parser.add_argument("--brief", required=True, help="Path to Viral Recipe Brief (.json)")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    if not brief_path.exists():
        print(f"[-] Error: Brief file not found: {brief_path}", file=sys.stderr)
        return 1

    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    recipe_id = brief["recipe_id"]
    campaign_dir = CAMPAIGNS_DIR / recipe_id
    campaign_dir.mkdir(parents=True, exist_ok=True)

    fuzzy = inject_fuzzy_variables("zh")
    print(f"[*] Injected Fuzzy Tone: [{fuzzy['emotion']}] (Filler: '{fuzzy['filler']}')")

    top_hook = brief["generated_hooks"][0]
    badge = brief["formula"].get("card_badge", "实战复盘")
    theme_key = THEME_MAP.get(brief["formula"].get("visual_theme", "dark_tech"), "dark_tech")
    
    card_path = campaign_dir / "cover_card.svg"
    card_rel = "./cover_card.svg"

    steps = brief["mapped_slots"].get("steps", [])
    bullet_points = [re.sub(r"^步骤\s*\d+\s*[：:]\s*", "", s)[:22] for s in steps[:3]]

    if render_svg_card:
        try:
            svg_content = render_svg_card(
                title=top_hook[:24],
                badge=badge,
                subtitle=f"{brief['formula']['name']} · 实操解构",
                bullet_points=bullet_points,
                footer_note=brief["mapped_slots"].get("lead_magnet", "评论区免费领自查表")[:25],
                theme_name=theme_key
            )
            card_path.write_text(svg_content, encoding="utf-8")
            print(f"[✓] 3:4 Visual Card rendered: {card_path}")
        except Exception as e:
            print(f"[-] Warning: Failed to render visual card: {e}", file=sys.stderr)

    drafts = build_platform_drafts(brief, fuzzy, card_rel)

    for p_name, text in drafts.items():
        violations = scan_for_grease(text)
        if violations:
            print(f"[!] Warning: Found grease words in {p_name}: {violations}", file=sys.stderr)

    posts_dir = campaign_dir / "posts"
    images_dir = campaign_dir / "images"
    posts_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    # Save drafts to both campaign root and posts/ for backward compatibility
    for fname, draft_key in [("xhs_post.md", "xhs"), ("x_thread.md", "x"), ("linkedin_post.md", "linkedin"), ("blog_post.md", "blog")]:
        (campaign_dir / fname).write_text(drafts[draft_key], encoding="utf-8")
        (posts_dir / fname).write_text(drafts[draft_key], encoding="utf-8")

    # Mirror visual card into images/
    if card_path.exists():
        (images_dir / "cover_card.svg").write_text(card_path.read_text(encoding="utf-8"), encoding="utf-8")

    # Generate standard manifest.md compatible with Gatekeeper and evolve_memory.py
    today_str = datetime.now().strftime("%Y-%m-%d")
    manifest_md = f"""---
title: "Release Package Manifest: {recipe_id}"
release_id: "{recipe_id}"
topic_id: "{recipe_id}"
doc_type: release-manifest
status: pending-review
created_at: {today_str}
tags:
  - doc/manifest
  - status/pending-review
---

# Release Package: 营销发布交接清单 (Release Manifest)

> **战役来源**：`{brief_path.name}`
> **核心黄金开口**：{top_hook}
> **生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. 发布包基础元数据
* **Recipe ID**：`{recipe_id}`
* **调性基调**：{fuzzy['emotion']} (垫词："{fuzzy['filler']}")
* **大字报主题**：{theme_key} ({badge})

---

## 2. 渠道发布资产清单 (Assets Checklist)
- [ ] **小红书 (Xiaohongshu)**：`posts/xhs_post.md` (封面卡：`cover_card.svg`)
- [ ] **X (Twitter)**：`posts/x_thread.md` (5屏推文串)
- [ ] **LinkedIn**：`posts/linkedin_post.md` (深度专业长帖)
- [ ] **博客/微信公众号**：`posts/blog_post.md` (完整长文)

---

## 3. 人工发布前最终审查 (Gatekeeper 2 Check)
- [ ] **事实核验**：所有论点及数据 100% 严格锚定 BUSINESS-SOT.md。
- [ ] **去油自检**：无假大空公文套话及违禁词。
- [ ] **引流核验**：私信暗号已配置合规落地页，无直接外链违规。
- [ ] **审批签署人**：__________________ 日期：______________

---

## 4. 发布效果跟踪
| 渠道 | 展现量 | 点赞 | 收藏 | 评论 | 转化线索 | CES/互动率 | CTR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    (campaign_dir / "manifest.md").write_text(manifest_md, encoding="utf-8")

    def to_rel_path(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(REPO_ROOT.resolve()))
        except Exception:
            return str(p)

    manifest = {
        "recipe_id": recipe_id,
        "brief_source": to_rel_path(brief_path),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "visual_card": to_rel_path(card_path),
        "drafts": {
            "xiaohongshu": to_rel_path(campaign_dir / "posts" / "xhs_post.md"),
            "x_twitter": to_rel_path(campaign_dir / "posts" / "x_thread.md"),
            "linkedin": to_rel_path(campaign_dir / "posts" / "linkedin_post.md"),
            "blog": to_rel_path(campaign_dir / "posts" / "blog_post.md")
        }
    }
    (campaign_dir / "campaign.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[✓] Campaign Package successfully synthesized in: {campaign_dir}")
    print(f"    • Release Manifest: {campaign_dir / 'manifest.md'}")
    print(f"    • 3:4 Visual Card:  {card_path}")
    print(f"    • 小红书原生文案:   {campaign_dir / 'xhs_post.md'} (and posts/xhs_post.md)")
    print(f"    • X (Twitter) 线程: {campaign_dir / 'x_thread.md'}")
    print(f"    • LinkedIn 专业贴:  {campaign_dir / 'linkedin_post.md'}")
    print(f"    • 微信/博客长文:    {campaign_dir / 'blog_post.md'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
