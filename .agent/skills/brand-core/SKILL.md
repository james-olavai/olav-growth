---
name: brand-core
description: "Manage the brand's single source of truth (BUSINESS-SOT.md), evolutionary memory (memory.md), and candidate signals. Use when onboarding a new project/brand, updating core product facts, reviewing de-grease forbidden words, adding candidate signals, or initializing the brand brain."
argument-hint: "Optional: --init | --validate | --add-signal"
---

# Brand Core Skill: 品牌大脑与记忆中枢

通用的品牌真相源管理与记忆沉淀技能。为后续所有选题策划、内容生成与营销分发提供**唯一可信的底层事实（Single Source of Truth, SoT）**，从源头杜绝大模型营销幻觉。

---

## 核心职责

1. **维护 `BUSINESS-SOT.md` (品牌大脑)**：
   - 固化 5 大核心字段：`Product Core`、`Target ICP & Pain Points`、`Brand Voice & Forbidden Words`、`No-Cost Offer`、`Primary CTA`。
2. **维护 `memory.md` (记忆右脑)**：
   - 记录历史高转化钩子、高频用户原声、风控防封号避坑经验。
3. **沉淀候选信号池 (Signal Intake)**：
   - 录入真实用户吐槽、竞品评论区原话、社区趋势。

---

## 常用操作指引

### 1. 首次运行冷启动与品牌入驻 (Brand Onboarding)
当用户首次启动项目时，无需手动从头编写 Markdown。支持通过官网、GitHub 仓库、个人 IP 定位或本地资料一键提炼初始化 `content/BUSINESS-SOT.md`：

```bash
# 模式 A：从官网落地页一键爬取并提炼（自动提取 Slogan、特性与 CTA）
python .agent/skills/brand-core/scripts/onboard_brand.py --url "https://myproduct.com"

# 模式 B：从 GitHub 开源仓库提炼（读取 README、定位与特性）
python .agent/skills/brand-core/scripts/onboard_brand.py --github "owner/repo"

# 模式 C：个人 IP / 创作者 / 咨询顾问定位建模
python .agent/skills/brand-core/scripts/onboard_brand.py --persona "出海独立开发者，专注于用 AI Agent 搭建自动化获客系统，分享实战踩坑与开源工具"

# 模式 D：从已有本地文档/BP 资料目录批量导入
python .agent/skills/brand-core/scripts/onboard_brand.py --docs-dir "docs/"
```

### 2. 交互式访谈引导 (Agent Conversational Onboarding)
若用户资料较少，Agent 可通过 4 步结构化提问快速补齐：
1. **产品与核心解法**：项目/产品叫什么？帮谁解决了什么痛点？
2. **目标受众 (ICP)**：最希望对话的精准人群与核心诉求？
3. **$0 免费钩子 (Lead Magnet)**：评论区可以送出的微小高价值交付物（如避坑清单、架构图、配置脚本）？
4. **语气与转化动作**：希望展现什么风格（如实诚同行、幽默极客）？落地页链接是什么？

### 3. 校验事实源完整性
在运行内容生成或策略规划前，检查 `content/BUSINESS-SOT.md` 是否缺失关键字段：
```bash
python .agent/skills/brand-core/scripts/init_brand.py --validate
```

### 4. 人机共建清单 (Human-in-the-Loop)
在正式启动内容工厂前，需与用户共同确认 `BUSINESS-SOT.md`：
- **去油禁词清单**：是否包含该行业常见的爹味商业套话？
- **$0 免费钩子**：是否准备了低门槛的高价值交付物（清单/模板/自查表）？
- **转化承接路径**：是否明确了安全落地页，避开直接留联系方式的封号红线？
