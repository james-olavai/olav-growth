---
name: content-strategist
description: "Evaluate candidate topics using a 5-dimensional scoring matrix (Relevance, Timing, Discussion, Evidence, Risk), formulate campaign angles (Demand-led, Launch spike, Case study, Thought leadership), and output a standardized campaign brief. Use when the user asks to plan a campaign, pick topics, prioritize marketing angles, or run topic scoring."
argument-hint: "Optional: --title <string> | --mode Demand-Led | Launch-Spike | Case-Study | Thought-Leadership"
---

# Content Strategist Skill: 选题决策引擎

通用的营销战役策略与选题立项决策技能。基于外部候选信号与内部底层事实，通过定量 5 维评分模型输出高胜率的战役企划简报（`campaign-brief.md`）。

---

## 核心流程

```
候选信号 / 热点 / 提问 ──► [5维定量评分] ──► [匹配战役模式与切角] ──► [人工审批闸门] ──► Campaign Brief
```

### 1. 5 维评分模型
$$\text{Topic Score} = \frac{\text{相关性} \times \text{时效性} \times \text{讨论度} \times \text{证据充分度}}{\text{风控等级 (1-5)}}$$
* **Score ≥ 40**：立即立项执行（GO）。
* **20 ≤ Score < 40**：纳入观察清单（WATCH）。
* **Score < 20**：果断放弃（DROP），避免制造无效信息噪音。

### 2. 四大战役模式与渠道适配
1. **Demand-Led (需求/痛点驱动)**：抓取用户当前急迫痛点，适配小红书、Reddit、知乎。
2. **Launch Spike (首发/里程碑更新)**：规划发布日前置预热与当日集中引爆，适配 Product Hunt、Show HN、X。
3. **Case Study (深度案例复盘)**：拆解真实客户成效与架构细节，适配 LinkedIn、公众号、博客。
4. **Thought Leadership (行业反思与洞察)**：打破思维定势，输出独家判断，适配 X Threads、LinkedIn 长帖。

---

## 常用操作指引

### 1. 证据充分度检索 (Evidence Gathering)
在为“证据充分度”打分前，可使用联合搜索模块 (`tools/union-search`) 快速拉取三方行业基准与事实佐证：
```bash
# 从百科与通用搜索拉取技术背景与行业定义 (免 Key)
python tools/union-search/union_search_cli.py platform wikipedia "Agentic Workflow" --limit 2
python tools/union-search/union_search_cli.py platform duckduckgo_html "Marketing Automation benchmark stats 2026" --limit 3

# 从 AI 搜索引擎抓取结构化事实 (需配置 TAVILY_API_KEY 或 METASO_API_KEY)
python tools/union-search/union_search_cli.py platform tavily "multi-platform social media posting limits" --limit 3
```

### 2. 运行评分并自动生成战役企划
```bash
python .agent/skills/content-strategist/scripts/score_topics.py \
  --title "解决多平台发布封号难题的合规双轨架构" \
  --relevance 5 \
  --timing 4 \
  --discussion 4.5 \
  --evidence 4.5 \
  --risk 1.5 \
  --mode Demand-Led \
  --out ./campaign-plan.md
```
