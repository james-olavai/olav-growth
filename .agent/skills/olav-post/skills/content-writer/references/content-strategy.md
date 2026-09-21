# Content Strategy — Voice Per Platform

How to write each platform draft in `olav-post/archive/YYYY-MM-DD/`.
For format templates (what fields to fill in each file), see [platform-drafts.md](./platform-drafts.md).

---

## Core Principle: Each Platform Gets a Different Angle

The same update must be framed differently for each audience. Never cross-post identical text.
Violating this causes SEO duplication penalties and platform-specific engagement drops.

---

## Anti-AI Writing Rules (applies to ALL platforms)

Before writing any post, internalize these rules:

**Remove:**
- Opening phrases: "In this post", "Today I want to share", "Let's explore", "Here's how", "Excited to announce"
- Adjective inflation: "powerful", "seamless", "comprehensive", "robust", "innovative", "revolutionize", "game-changing", "incredible"
- Hype closers: "Try it today!", "Check it out!", "Game changer!", "See it in action!"
- Bullet lists of abstract benefits (use concrete specifics instead)
- Section headers in short-form posts ("## The Problem", "## Key Benefits")
- Hashtag stacks (max 2, only if culturally expected)
- Redundant adjectives: "really", "truly", "absolutely", "excellent"
- Emoji used for emphasis or decoration

**Add:**
- A specific number or measurement ("dropped latency from 800ms to 120ms", "3-line config")
- A thing that didn't work before and does now (concrete before/after)
- One acknowledged limitation or trade-off — this is the single biggest humanizer
- Your personal opinion or preference ("by my standards", "I'd rather do X than Y")
- A genuine question that invites real discussion — not a rhetorical one
- Proper punctuation for transitions: semicolons and em-dashes, not hyphens surrounded by spaces
- Disclaimers when recommending tools ("not affiliated, it just saved me hours")

**Vary:**
- Sentence length: mix short punchy sentences with longer ones
- Don't start consecutive sentences with "I" or "The"
- Use semicolons and dashes — not just periods — to break up rhythm

**The core test**: Does each sentence teach or show something specific? If a sentence could appear in any tech post about any project, cut or rewrite it.

---

## Self-Review Checklist (run before every post)

After generating a draft, check line by line:

```
[ ] No "excited/proud/thrilled/happy to share"
[ ] No adjective inflation (powerful, seamless, robust...)
[ ] At least one concrete number or measurement
[ ] At least one acknowledged limitation
[ ] Opening sentence is NOT a restatement of the title
[ ] No two consecutive sentences start with the same word
[ ] Each sentence teaches something — none are pure filler
[ ] Platform language is correct (EN: LinkedIn/HN/Reddit | ZH: 知乎/掘金/微信)
[ ] No identical sentence exists in any other platform's draft
```

If any box is unchecked, rewrite before completing the content-writer workflow.

---

## Platform Voice Guide

### LinkedIn
- **Audience**: IT managers, infrastructure architects, tech leads
- **Tone**: Professional, first-person narrative, story not feature list
- **Length**: 400–700 words — this is a full professional article, not a caption
- **Format**: Plain prose, 5–7 paragraphs. No bullets. No hashtags (max 2 very specific ones at end if relevant).
- **Structure**: Problem → what you tried → what failed → what works now → concrete outcome → one limitation
- **Angle**: What problem this solves for the team, organizational impact
- **Opening**: Start with the problem or the moment of realization — not "I'm excited to announce"
- **Required**: At least one specific number/measurement. One acknowledged limitation. One genuine moment of doubt or failure.

**Good:**
```
Last week a client asked why their runbook automation kept hallucinating interface names.
The answer was mundane: the LLM had no live state to validate against.

olav now runs a schema check before any CLI command executes — if the generated flag
doesn't match the device's actual capability set, it stops and asks. Not elegant, but
it's caught three bad commands in our own ops environment this month.

Still not bulletproof on edge cases with vendor-specific syntax. Working on it.

https://olavai.com/blog/<slug>
```

**Bad:**
```
Excited to announce a major update to olav! 🚀

Our powerful new schema validation feature seamlessly prevents AI hallucinations,
making your infrastructure automation more robust and reliable than ever.

Key benefits:
- Stops invalid commands before execution
- Comprehensive validation coverage
- Game-changing for your ops team

Try it today! #DevOps #AI #Innovation
```

### HackerNews
- **Audience**: Engineers, skeptical hackers, startup founders
- **Tone**: Extremely dry, technical, no marketing. The community HATES hype.
- **Length**: Title (max 80 chars) + 80–150 words context text. Short by design — depth belongs in the comments.
- **Format**: Plain text. "Show HN: <name> — <one-line description>" title. 2–4 sentences of context.
- **Angle**: The implementation challenge or architectural decision, not the product pitch
- **Opening**: "Show HN: <name> — <one-line description>" or just link + 2-sentence context
- **Do NOT**: Use exclamation marks, "excited", "proud", "amazing"

**Good:**
```
Show HN: olav – AI agent runtime for infra ops (Python, BSL)

Built this to replace runbook Word docs that no one reads. Uses DuckDB as the
audit/state store; all write ops require HITL approval before execution.
Main limitation: the LLM still occasionally hallucinates CLI flag names —
we added a schema validation layer but it's not bulletproof yet.

https://github.com/james-olavai/olav
```

**Bad:**
```
Show HN: olav – The Revolutionary AI Infrastructure Automation Platform!

I'm incredibly excited to share olav, a powerful and comprehensive AI agent
runtime that will revolutionize how your team handles infrastructure operations!

Try it today: https://github.com/james-olavai/olav
```

### Reddit (r/selfhosted, r/devops, r/homelab, r/networking)
- **Audience**: Practitioners who've been burned by overhyped tools
- **Tone**: Community peer, casual, self-deprecating OK, invite discussion
- **Length**: 500–900 words — enough for real technical depth, not a tweet expanded
- **Format**: Short intro, what it does, concrete example with before/after, what doesn't work, genuine question at end
- **Structure**: Hook (1 paragraph) → problem being solved (2 paragraphs) → how it works technically (2–3 paragraphs) → real limitations/caveats (1 paragraph) → open question to community
- **Angle**: How it fits into real workflows, compare to alternatives honestly
- **Opening**: State what it is plainly. "Built a tool that..." not "I'm thrilled to share..."
- **Sub choice**: Pick the most specific sub. Cross-post sparingly. Add OC/self-post flair.
- **Acknowledge**: Known limitations, alpha/beta state, what you'd do differently

**Good:**
```
Built an AI agent runtime for infra ops — wanted to share how I handled the
"LLM hallucinates CLI flags" problem since I've seen it come up here before.

The approach: every generated command gets validated against a device capability
schema before execution. If the flag doesn't exist on that firmware version, it
stops and asks. Caught three bad commands in our test env last week alone.

It's not perfect — vendor-specific syntax still trips it up, and the schema files
need manual maintenance. We're using DuckDB as the audit store so every action
is queryable, which has been more useful than I expected for post-incident review.

Code: https://github.com/james-olavai/olav (BSL licensed, not MIT — worth reading
the license if you're considering it for commercial use)

Curious how others are handling LLM validation in infra automation — are you
pre-validating or catching errors after the fact?
```

### 知乎 (Zhihu)
- **Audience**: Chinese technical professionals, researchers, senior engineers
- **Tone**: Structured academic, authoritative but accessible, first-person reflection OK
- **Length**: **2000–5000 汉字** — 知乎读者预期完整的技术文章，而不是微博扩充版
- **Format**: 标题 → 摘要（2-3句）→ 正文（多个 H2 段落）→ 局限性 → 参考资料
- **Required sections**: 
  - 背景/问题（为什么要做这个，之前的方案有什么缺陷）
  - 核心设计（架构图 + 设计决策过程，包括被放弃的方案）
  - 关键实现（代码或伪代码，解释为什么这样写）
  - 性能/效果（具体数据，不是形容词）
  - 局限性与已知问题（越诚实越好）
  - 延伸思考（给读者留下一个开放问题）
- **Angle**: Deep explanation of _why_ the design decision was made, the thinking behind architecture
- **Opening**: Frame as answering a question or sharing a research finding — start mid-story
- **Language**: 正式书面语，但不生硬。允许第一人称反思。禁止口语化/网络语

**Good:**
```
## 为什么我们用 DuckDB 而不是 PostgreSQL 做审计存储？

在设计 olav 的状态管理层时，我们面临一个经典选择：OLTP 数据库 vs. 列存引擎。
最终选 DuckDB，原因不是性能，而是查询表达能力。

运维审计的核心需求是"事后溯源"：给定一次故障，找出前24小时内所有涉及该设备的
操作，以及每个操作的前置状态。这是一个典型的分析型查询，JOIN 多张宽表，时间窗口
过滤，聚合结果。DuckDB 的问题是并发写入限制——它不是为高并发设计的。olav 的
场景是单 agent 顺序操作，这个限制不是瓶颈。
```

### 掘金 (Juejin)
- **Audience**: Chinese frontend/backend/infra developers, mid-level engineers
- **Tone**: Practical tutorial, straight to the point, show the useful parts
- **Length**: **1500–3000 汉字**（含代码）— 要够让读者照着做一遍
- **Format**: 开头说清楚"这篇文章教你做什么" → 背景/问题 → 实现思路 → 核心代码 → 踩坑 → 结论
- **Required**: 至少2个代码片段（可以是 CLI 命令），1个踩坑/意外发现，1个实际运行结果或截图描述
- **Angle**: What developers can learn from or use directly. Code > prose.
- **Opening**: State the tech problem then show the fix
- **Include**: At least one code snippet or CLI example, one "坑" (pitfall) encountered
- **Tags**: Use official Juejin tags (后端, 运维, DevOps, Python, AI) — 3–5 max
- **Language**: 技术口语化 — 可以用"咱们"、"搞定"、"踩坑"，但不能太随意

### 微信公众号 (WeChat Official Account)
- **Audience**: Broader Chinese tech community, non-specialist managers, team leads
- **Tone**: Story-driven narrative, accessible, educational without being condescending
- **Length**: **2000–4000 汉字** — 公众号读者愿意读长文，但要每段都有料
- **Format**: 强钩子开头（1段）→ 问题展开（2-3段）→ 解决方案叙事（3-4段，用类比）→ 具体效果（1-2段，有数据）→ 局限与展望（1段）→ 结尾反问
- **Required sections**:
  - 开头钩子：一个具体场景，要有画面感（不是"今天介绍一个工具"）
  - 问题叙事：为什么这个问题重要，用比喻让非专业读者也能理解
  - 技术解法：用类比解释核心机制，**加粗**关键术语，避免代码块（最多1个简短示例）
  - 真实效果：有具体数字，不是形容词
  - 诚实的局限性：让读者相信你不是在卖东西
  - 结尾问题：让读者有所思考，不是CTA
- **Angle**: Tell the story of why this exists — the frustration, the journey, the solution
- **Opening**: Hook with a scenario ("凌晨两点，运维工程师盯着报警大屏...")
- **Closing**: End with a question or reflection, not a CTA
- **Extra avoid (中文AI腔黑名单)**: "赋能"、"助力"、"全面"、"深度"、"智能化转型"、"业界领先"、"无缝对接"、"强大"

---

## Content Variance Checklist

Before finishing, verify each platform post is distinct:

- [ ] Different opening sentence (not paraphrase — completely different angle)
- [ ] Different framing (product vs. technical vs. community vs. educational)
- [ ] Different length (not just trimmed — different structure entirely)
- [ ] Language appropriate (EN for LinkedIn/HN/Reddit, ZH for 知乎/掘金/微信)
- [ ] No identical paragraphs across any two posts
- [ ] Each post has at least one detail the others don't mention
