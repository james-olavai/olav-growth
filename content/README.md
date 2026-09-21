# Content Vault: 营销内容资产库与目录规范

> 本目录是全项目营销内容的**唯一资产库 (Content Vault)**。
> 所有由 `content-strategist` 规划、`content-factory` 生产、`growth-distribution` 分发的内容均在此统一归档。
> 结构规范与 Frontmatter 设计**天然兼容 Obsidian 知识图谱**与 **docs-kb** 全文检索。

---

## 一、目录层级约定 (Directory Convention)

```
content/
├── README.md                      # 目录使用规范说明（本文档）
├── config.yaml                    # docs-kb 知识库分类规则与扫描配置
├── campaigns/                     # 按“营销战役/选题”归档的独立包
│   └── YYYY-MM-DD-<topic-slug>/   # 单次战役全套资产包
│       ├── _brief.md              # 战役简报（来自 content-strategist）
│       ├── xhs.md                 # 小红书图文文案（含 Frontmatter）
│       ├── linkedin.md            # LinkedIn 商业长帖
│       ├── x-thread.md            # X 核心 Hook 与 Threads
│       ├── blog.md                # 微信公众号 / 博客深度长文
│       ├── youtube.md             # 视频口播脚本与时间戳分镜
│       ├── reddit.md              # 社区技术干货帖
│       ├── images/                # 3:4 视觉大字报 (SVG / WebP / PNG)
│       │   ├── 01-cover.svg
│       │   └── 02-slide.svg
│       └── manifest.md            # 发布交接单与状态监控 (来自 growth-distribution)
└── templates/                     # 各平台 Markdown 原生草稿标准骨架
```

---

## 二、标准 Frontmatter Schema 规范

资产库中每一个内容 Markdown 文件顶部均携带标准 YAML Frontmatter，支持状态流转、渠道过滤与自动化工具读取：

```yaml
---
title: "多平台发布总被限流？3招打造自动化获客机器"
topic_id: "TOPIC-20260920-01"
campaign_mode: Demand-Led       # Demand-Led | Launch-Spike | Case-Study | Thought-Leadership
channel: xhs                   # xhs | linkedin | x | blog | youtube | reddit | instagram | pinterest
status: draft                  # draft (初稿) | reviewing (待审) | approved (已过审) | scheduled (已排期) | published (已发布)
created_at: 2026-09-20
publish_date: 2026-09-25
author: "Olav Growth Team"
target_url: "https://example.com/start"
cta_keyword: "【自查】"
tags:
  - channel/xhs
  - campaign/demand-led
  - status/draft
doc_type: marketing-post
category: social-media
images:
  - images/01-cover.svg
  - images/02-slide.svg
---
```

---

## 三、Obsidian 与 Dataview 兼容性

本目录可作为独立的 **Obsidian Vault** 或现有知识库的一个文件夹直接打开：
1. **Properties 属性面板**：打开任意文章，右侧自动渲染状态徽章、发布渠道与发布日期。
2. **嵌套标签 (Nested Tags)**：通过 `channel/xhs`、`status/draft` 可以在 Obsidian 左侧标签栏一键过滤所有特定平台或草稿状态的帖子。
3. **Dataview 自动化看板**：
   在 Obsidian 中新建笔记写入以下代码，即可自动生成排期跟踪表：
   ```dataview
   TABLE status, channel, publish_date, cta_keyword
   FROM "content/campaigns"
   WHERE doc_type = "marketing-post"
   SORT publish_date DESC
   ```

---

## 四、与 docs-kb 检索协同

由于规范统一，`docs-kb` 可以无缝检索、分类与查重整个 `content/` 资产库：
```bash
# 检索所有涉及“限流”或“去油”的已发布营销文案
python .agent/skills/olav-dockb/scripts/search_docs.py "限流" --status published

# 检查资产库内容是否出现语义漂移
python .agent/skills/olav-dockb/scripts/check_taxonomy_drift.py
```
