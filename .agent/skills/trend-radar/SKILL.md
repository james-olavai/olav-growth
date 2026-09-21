---
name: trend-radar
description: "Discover real-time trending topics, industry discussions, and market search spikes using Google Trends, developer/startup feeds, and agent browser workflows. Filters noise against BUSINESS-SOT.md and outputs standardized Signal Cards into content/candidate_signals/ for topic scoring."
argument-hint: "Optional: --geo <US|TW|SG|HK> | --keywords <words...> | --browser"
---

# Trend Radar Skill: 热点雷达与信号侦测器

> **定位**：营销自动化流水线的**最前置触手（Scout Layer）**。
> 负责从全球与区域级搜索趋势（Google Trends）、开发者与科技社区（Hacker News / GitHub）、以及社交平台（通过 Agent 浏览器能力）实时捕获公众关注焦点与讨论爆发点，并通过与品牌事实源（`BUSINESS-SOT.md`）的语义对齐，将噪音过滤为高价值的**候选信号卡 (Signal Cards)**。

---

## 一、核心工作流 (Workflow)

```
       [Google Trends 实时热搜] ──┐
   [Hacker News / Tech 社区讨论] ──┼──► [trend-radar 收集器]
   [Agent 浏览器 (/browser 交互)] ──┘             │
                                                  ▼
                                      [对齐 BUSINESS-SOT.md 过滤]
                                      (剔除娱乐八卦，保留痛点与契机)
                                                  │
                                                  ▼
                               [生成 content/candidate_signals/ 信号卡]
                                                  │
                                                  ▼
                               [移交 content-strategist 五维打分]
```

---

## 二、支持的数据源与指令

### 1. Google Trends 极速热搜侦测（免 API Key）
直接拉取 Google 官方热搜榜单，支持 20+ 国家/地区与关键词过滤：
```bash
# 查看台湾地区的最新搜索爆发词（适合中文/出海选题）
python .agent/skills/trend-radar/scripts/fetch_google_trends.py --geo TW --limit 10

# 查看美国市场热点，并自动将契合的条目转为 Signal Card 存入 content/candidate_signals/
python .agent/skills/trend-radar/scripts/fetch_google_trends.py --geo US --limit 10 --emit-signals
```

### 2. 科技与创业者社区热点（Hacker News / Show HN）
挖掘全球开发者和创业者目前正在讨论、造轮子或吐槽的技术：
```bash
# 查看 Show HN 最新的创业工具与讨论
python .agent/skills/trend-radar/scripts/fetch_tech_trends.py --type show --limit 10

# 过滤带特定关键词（如 AI, workflow, agent）的技术热点并生成信号卡
python .agent/skills/trend-radar/scripts/fetch_tech_trends.py --type top --filter AI agent --emit-signals
```

### 3. 一键联合侦测与业务匹配 (Unified Scout)
一键自动读取 `BUSINESS-SOT.md` 中的关键词，批量扫描 Google Trends 与技术社区：
```bash
python .agent/skills/trend-radar/scripts/scout_signals.py --geos US,TW,SG
```

### 4. Agent 浏览器协同与高风控平台捕获 (`/browser`)
对于小红书、微博热搜、微信公众号爆文等具备严格 WAF 与滑块验证码的国内平台：
- 用户输入 `/browser` 启动浏览器交互模式。
- 直接打开小红书 (`xiaohongshu.com/explore`) 或微博热搜榜，观察行业词的爆款笔记与高赞吐槽。
- Agent 通过 [browser_playbook.md](references/browser_playbook.md) 的指引，将用户捕获的高赞原声（Raw Quotes）快速结构化为标准 `SIG-YYYYMMDD-XX.md`。

### 5. 全网多平台联合侦测 (Union Search)
集成统一搜索套件 `tools/union-search`，实现无需 API Key 或多平台的跨端侦测：
```bash
# 开发者/科技社区搜索 (GitHub, Reddit)
python tools/union-search/union_search_cli.py search "AI Agent" --group dev --preset small

# 免 API Key 通用搜索侦测 (DuckDuckGo, 360, 搜狗)
python tools/union-search/union_search_cli.py platform duckduckgo_html "AI 自动化营销" --limit 5
python tools/union-search/union_search_cli.py platform so360_direct "多平台社媒自动化" --limit 5

# 社交媒体搜索 (Bilibili / 知乎 / Twitter / 抖音，需 TIKHUB_TOKEN)
python tools/union-search/union_search_cli.py platform bilibili "AI Agent" --limit 5
```

---

## 三、产出物标准

所有捕获并过筛的热点均保存至：
`content/candidate_signals/SIG-YYYYMMDD-<source>-<slug>.md`

自带规范 YAML Frontmatter（与 `docs-kb` 及 Obsidian 兼容）：
```yaml
---
title: "Signal Card: CUA-S1 – A System One Model for Computer Use"
signal_id: "SIG-20260920-HN01"
doc_type: candidate-signal
status: candidate
created_at: 2026-09-20
source_type: "community-trend"
tags:
  - doc/signal
  - status/candidate
  - source/hackernews
---
```
