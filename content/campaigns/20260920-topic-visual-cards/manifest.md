---
title: "Release Package Manifest: TOPIC-VISUAL-CARDS"
release_id: "REL-20260920-01"
topic_id: "TOPIC-VISUAL-CARDS"
doc_type: release-manifest
status: pending-review
created_at: 2026-09-20
tags:
  - doc/manifest
  - status/pending-review
---

# Release Package: 营销发布交接清单 (Release Manifest)

> 本交接包是针对**无官方 API 或高风控渠道**（如小红书、微信私域、特定专业社区等）的标准人工发布包。
> 严禁调用第三方私有反爬 API 强行自动发帖，防止高权重主号被降权或封禁。

---

## 1. 发布包基础元数据
* **Release ID**：`REL-20260920-01`
* **关联 Topic ID**：`TOPIC-VISUAL-CARDS`
* **发布执行日期**：2026-09-20
* **负责发布人**：[姓名/角色]

---

## 2. 渠道发布资产清单 (Assets Checklist)

### 渠道 1：小红书 (Xiaohongshu)
- [ ] **正文草稿**：`posts/xhs-draft.md`（已完成去油自检与第一人称校验）
- [ ] **视觉素材**：
  - `images/01-cover.png`（3:4 比例大字报封面）
  - `images/02-slide.png` ~ `images/05-slide.png`（3:4 内页解析卡）
- [ ] **文末 CTA 暗号**：确认暗号为【自查】，且私信自动回复已配置合规落地页
- [ ] **发布时间窗口**：建议 12:00-13:30 或 20:00-22:00

### 渠道 2：LinkedIn
- [ ] **长帖文案**：`posts/linkedin-post.md`
- [ ] **配图/Document**：`assets/framework.pdf`
- [ ] **首评预埋**：`comments/first-comment.md`（补充硬核数据与落地页链接）

### 渠道 3：微信公众号 / 博客
- [ ] **完整文章**：`posts/longform-article.md`
- [ ] **SEO 元数据**：`Title`、`Meta Description` 已符合 GEO 索引规范

---

## 3. 人工发布前最终审查 (Gatekeeper 2 Check)
- [ ] **事实核验**：未出现未经核实的数据或夸大宣传。
- [ ] **风控核验**：正文及配图绝无直接微信号、微信二维码等高危引流违禁词。
- [ ] **链接测试**：所有 Landing Page / Demo 链接经手机实机测试可正常打开。
- [ ] **审批签署人**：__________________ 日期：______________

---

## 4. 发布效果跟踪
| **Xhs** | 4,800 | 210 | 430 | 68 | 35 (线索) | 1342 | - |
 (Performance Telemetry)
> 记录 T+24h / T+72h 实际业务指标（用于回流与飞轮学习）：

| 渠道 | 浏览/展现量 | 点赞 | 收藏 | 评论 | 询盘/线索 (Leads) | CES得分 / 互动率 | 链接 CTR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **小红书** | [ ] | [ ] | [ ] | [ ] | [ ] (暗号回复数) | [CES=赞+2*藏+4*评+4*转] | - |
| **LinkedIn** | [ ] | [ ] | [ ] | [ ] | [ ] | [互动率 %] | [ ] |
| **X** | [ ] | [ ] | [ ] | [ ] | [ ] | [互动率 %] | [ ] |
| **微信/博客** | [ ] | [ ] | [ ] | [ ] | [ ] | [完读率 %] | [ ] |

---

## 5. 战役复盘与技能进化 (Evolution & Reflection)
* **胜出点 (What Worked)**：
  - [记录本次战役表现亮眼的 Hook、排版或切角]
* **踩坑点 (What Flopped / Bottlenecks)**：
  - [记录留存低、被限流或用户不感兴趣的原因]
* **反哺进化动作 (Evolution Trigger)**：
  - [ ] 高转化黄金钩子已提取至 `content/memory.md`
  - [ ] 评论区真实异议已沉淀为新一轮候选信号 (`content/candidate_signals/`)
  - [ ] 触发反爬/限流的词汇已追加至 `BUSINESS-SOT.md` 去油禁令中
