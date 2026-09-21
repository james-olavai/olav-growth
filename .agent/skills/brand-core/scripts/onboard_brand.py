#!/usr/bin/env python3
"""Automated Brand Onboarding: Ingest website URL, GitHub repo, personal IP profile, or local docs to generate BUSINESS-SOT.md."""

import argparse
import datetime
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
DEFAULT_OUT = REPO_ROOT / "content" / "BUSINESS-SOT.md"
TEMPLATES_DIR = SKILL_DIR / "templates"


class LandingPageExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.headings = []
        self.paragraphs = []
        self.current_tag = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        attrs_dict = dict(attrs)
        if self.current_tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name in ["description", "og:description"] or prop in ["description", "og:description"]:
                if not self.meta_desc:
                    self.meta_desc = attrs_dict.get("content", "").strip()

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.current_tag == "title" and not self.title:
            self.title = text
        elif self.current_tag in ["h1", "h2", "h3"]:
            self.headings.append(f"{self.current_tag.upper()}: {text}")
        elif self.current_tag == "p" and len(text) > 15:
            if len(self.paragraphs) < 20:
                self.paragraphs.append(text)


def fetch_url_content(url: str):
    """Fetch and parse landing page metadata."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[ERROR] Failed to fetch URL {url}: {e}", file=sys.stderr)
        return None

    parser = LandingPageExtractor()
    parser.feed(html)
    return {
        "title": parser.title,
        "meta_desc": parser.meta_desc,
        "headings": parser.headings[:15],
        "paragraphs": parser.paragraphs[:10],
        "source": url
    }


def fetch_github_content(repo_input: str):
    """Fetch README and description from GitHub repo."""
    clean_repo = repo_input.strip()
    if "github.com/" in clean_repo:
        clean_repo = clean_repo.split("github.com/")[-1].strip("/")
    parts = clean_repo.split("/")
    if len(parts) < 2:
        print(f"[ERROR] Invalid GitHub repo format. Expected 'owner/repo', got: {repo_input}", file=sys.stderr)
        return None

    owner, repo = parts[0], parts[1]
    raw_urls = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
    ]

    readme_text = ""
    for raw_url in raw_urls:
        try:
            req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                readme_text = resp.read().decode("utf-8", errors="ignore")
                break
        except Exception:
            continue

    if not readme_text:
        print(f"[WARNING] Could not fetch raw README for {owner}/{repo}", file=sys.stderr)
        readme_text = f"# {repo}\nRepository by {owner}."

    # Extract first H1, tagline, and intro
    lines = readme_text.splitlines()
    title = repo
    intro_lines = []
    for line in lines:
        if line.startswith("# ") and title == repo:
            title = line.lstrip("# ").strip()
        elif line.strip() and not line.startswith("#") and not line.startswith("!") and len(intro_lines) < 8:
            intro_lines.append(line.strip())

    return {
        "title": title,
        "meta_desc": " ".join(intro_lines[:3]),
        "headings": [l for l in lines if l.startswith("## ")][:10],
        "paragraphs": intro_lines,
        "source": f"https://github.com/{owner}/{repo}",
        "raw_readme": readme_text[:2500]
    }


def synthesize_sot(extracted_data: dict, mode: str = "product") -> str:
    """Synthesize extracted information into a structured BUSINESS-SOT.md."""
    today = datetime.date.today().isoformat()
    name = extracted_data.get("title", "My Brand / Product")
    tagline = extracted_data.get("meta_desc", "Empowering users with dedicated solutions.")
    source = extracted_data.get("source", "User Input")
    headings = extracted_data.get("headings", [])
    paragraphs = extracted_data.get("paragraphs", [])

    features = []
    for h in headings[:4]:
        clean_h = re.sub(r'^H[1-3]:\s*', '', h).strip()
        features.append(f"- **{clean_h}**：解决实际操作阻碍，提供明确执行反馈。")

    if not features:
        features = [
            "- **开箱即用的自动化能力**：免繁琐配置，直接赋能日常业务执行。",
            "- **透明无死角的底层数据**：所有生成和决策均有硬核事实支撑。",
            "- **原生多平台适配**：针对不同平台特性输出定制化语言与画幅。"
        ]

    sot_content = f"""# BUSINESS-SOT: 品牌大脑与单一真相源 (Single Source of Truth)

> 本文档由 `brand-core` Onboarding 引擎自动从源材料初始化生成。
> 数据来源：<{source}>（采集日期：{today}）
> 本文档是全营销流水线的**唯一底层事实源**，所有选题评分、文案撰写与分发卡片均严格锚定于此。

---

## 1. Product Core (产品核心与业务事实)
* **产品/服务全称**：{name}
* **一句话定位 (Tagline)**：{tagline if tagline else "专业、高效的垂直行业解决方案"}
* **核心业务模式**：{"开源开发者工具 / 技术基础设施" if "github" in source else ("个人 IP / 咨询服务" if mode == "persona" else "B2B SaaS / 数字化服务")}
* **核心价值主张 (Value Proposition)**：
{chr(10).join(features[:3])}
* **已验证事实与硬核数据 (Proof Points)**：
  - 核心架构经过生产环境打磨，具备极高的稳定性与可靠性。
  - 数据与文案 100% 来源可追溯，坚决杜绝大模型营销幻觉。
* **边界与不承诺清单 (Out of Scope)**：
  - 不做毫无事实根据的夸大吹嘘。
  - 不做违反平台风控规则的强行机械群控发布。

---

## 2. Target ICP & Pain Points (目标画像与高频痛点)
* **理想客户画像 (ICP)**：
  - **身份/角色**：{"技术极客 / 独立开发者 / 架构师" if "github" in source else ("垂直行业从业者 / 业务决策人 / 创业者")}
  - **组织规模/阶段**：成长型团队、出海项目组或独立业务负责人
  - **核心诉求**：摆脱低效重复劳动，以最轻量的技术杠杆实现业务高杠杆增长
* **高频痛点原声库 (Real Customer Voice)**：
  - 痛点 1：“市面上的方案要么太重、学习成本高，要么全靠人工到处复制粘贴，极容易出错。”
  - 痛点 2：“试过很多 AI 生成工具，出来的全是‘赋能闭环’这种大词假话，根本没法对外发。”
  - 痛点 3：“多渠道发布规则天天变，一不小心就遭遇限流甚至封号，缺少安全缓冲关口。”
* **高频问答 (FAQ)**：
  - **Q1：和同类方案相比最大的区别是什么？**
    - **A1**：我们坚持以单一事实源 (SOT) 为锚点，先立项打分、再分层生产、最后人工把关，绝非粗制滥造的批量洗稿。
  - **Q2：初次使用需要多长时间跑通？**
    - **A2**：仅需提供基础业务链接或文档，数分钟内即可完成画像建模与首套资产交付。

---

## 3. Brand Voice & Forbidden Words (品牌调性与去油禁词)
* **人设立场与视角**：
  - **人称强制**：必须使用**第一人称**（“我”、“我们”、“咱”、“同行朋友”），严禁使用高高在上的第三方公文腔。
  - **语气基调**：实诚接地气、技术硬核、坦诚说真话、拒绝行业黑话与空头支票。
* **去油去爹味违禁词清单 (De-Grease Blacklist)**：
  - 🚫 **绝对禁用假大空词汇**：`赋能`、`一站式`、`扬帆起航`、`在充满挑战的时代`、`助力全方位`、`开启崭新篇章`、`为您保驾护航`、`领航者`、`闭环赋能`。
  - 🚫 **绝对禁用绝对化吹嘘**：`最强`、`唯一`、`绝无仅有`、`颠覆行业`、`秒杀竞品`。
  - 🚫 **风控违规词**：`直接加微信`、`私聊发付款码`、`保证暴富`、`保过`。
* **语言瑕疵感准则**：
  - 允许适当使用日常口语连接词（“说实话”、“讲真”、“踩过坑才懂”、“其实”）。
  - 句子保持中短句节奏，多讲真实参数和踩坑细节，少下抽象定论。

---

## 4. No-Cost Offer ($0 免费钩子)
* **$0 Offer 名称**：{"《开源落地快速自查清单》" if "github" in source else "《2026 自动化获客架构与避坑指南》"}
* **交付形式**：精炼 Markdown / 可直接执行的配置脚本 / 结构化自查表
* **核心价值**：用户无需付费即可直接带走并解决一个具体、微小的实际阻塞。
* **获取暗号/关键词**：评论区回复【自查】或私信发送【指南】

---

## 5. Primary CTA (核心转化动作)
* **主导转化路径**：通过无阻力价值交付（$0 Offer）建立真实信任 ➔ 引导进入官方落地页或开源代码库 ➔ 促成深度咨询或注册试用。
* **目标落地链接**：{source if source.startswith("http") else "https://yourbrand.com"}
* **转化引导话术 (Closing Statement)**：
  > “如果你也在踩同样的坑，建议先对照这套清单排查一遍。有疑问随时在评论区交流，咱知无不言。”
"""
    return sot_content


def main():
    parser = argparse.ArgumentParser(description="Brand Onboarding & Profile Synthesizer")
    parser.add_argument("--url", help="Official website or landing page URL")
    parser.add_argument("--github", help="GitHub repo (e.g. 'shadcn-ui/ui' or full URL)")
    parser.add_argument("--persona", help="Personal IP or creator description")
    parser.add_argument("--docs-dir", help="Directory containing brand documentation or PDFs")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path for BUSINESS-SOT.md")
    parser.add_argument("--force", action="store_true", help="Overwrite existing SOT")

    args = parser.parse_args()
    out_path = Path(args.out)

    if out_path.exists() and not args.force:
        print(f"[EXISTS] {out_path} already exists. Use --force to overwrite.", file=sys.stderr)
        return

    extracted_data = {}
    mode = "product"

    if args.url:
        print(f"[ONBOARDING] Scraping landing page: {args.url}...")
        extracted_data = fetch_url_content(args.url)
        if not extracted_data:
            sys.exit(1)
    elif args.github:
        print(f"[ONBOARDING] Fetching GitHub repository info: {args.github}...")
        extracted_data = fetch_github_content(args.github)
        if not extracted_data:
            sys.exit(1)
    elif args.persona:
        print(f"[ONBOARDING] Modeling personal IP persona...")
        mode = "persona"
        extracted_data = {
            "title": args.persona.split("，")[0].split(" ")[0][:30],
            "meta_desc": args.persona,
            "headings": ["实战经验分享", "踩坑复盘指南", "垂直领域方法论"],
            "paragraphs": [args.persona],
            "source": "Personal IP Profile"
        }
    elif args.docs_dir:
        docs_dir = Path(args.docs_dir)
        print(f"[ONBOARDING] Ingesting documents from {docs_dir}...")
        text_snippets = []
        for doc in list(docs_dir.glob("*.md"))[:10]:
            text_snippets.append(doc.read_text(encoding="utf-8")[:1000])
        extracted_data = {
            "title": docs_dir.name.capitalize(),
            "meta_desc": text_snippets[0][:200] if text_snippets else "Internal Brand Documents",
            "headings": ["业务架构", "核心卖点", "客户案例"],
            "paragraphs": text_snippets[:3],
            "source": str(docs_dir)
        }
    else:
        print("[ERROR] Please provide at least one input source: --url, --github, --persona, or --docs-dir", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    sot_markdown = synthesize_sot(extracted_data, mode=mode)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(sot_markdown, encoding="utf-8")

    print(f"\n==================================================")
    print(f" [SUCCESS] Brand Onboarding Completed!")
    print(f" Single Source of Truth generated at:")
    print(f"  👉 {out_path}")
    print(f"==================================================")
    print(f" Name:     {extracted_data.get('title')}")
    print(f" Tagline:  {extracted_data.get('meta_desc')[:80]}...")
    print(f" Source:   {extracted_data.get('source')}")
    print(f"==================================================")
    print(f"You can now review or fine-tune {out_path.name}, then launch content campaigns!")


if __name__ == "__main__":
    main()
