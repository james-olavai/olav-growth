# Social Publishing Hierarchy: 四级发布阶梯与 MCP 选型指南

> **核心原则**：
> **原生 API / Webhook 是主力，专用官方 MCP 是加速器，规范化人工发布包是防封底线，而 Chrome DevTools MCP 永远是最后一招兜底。**

---

## 一、为什么 Chrome DevTools MCP 是最后一招？

| 维度 | 原生 API / Webhook (主力) | 浏览器 CDP 自动化 (最后一招) |
| :--- | :--- | :--- |
| **稳定性** | 极高（官方接口与版本化协议，不受页面改版影响） | 极脆弱（任何前端 class/DOM 改动、弹窗、验证码都会打断） |
| **环境依赖** | 纯 HTTP 请求，支持命令行、服务器、CI/CD 与后台静默执行 | 依赖本地启动 Chrome 调试端口，无法在无头服务器优雅运行 |
| **风控风险** | 官方授权 Token，正常调用 | CDP 自动化操作极易触发各大平台的反爬指纹识别，导致账号被风控 |
| **耗时与资源** | 毫秒级返回 | 打开浏览器、等待渲染、模拟输入，单平台耗时常达数十秒 |

---

## 二、四级发布架构阶梯 (The 4-Tier Ladder)

```
┌──────────────────────────────────────────────────────────────┐
│ Tier 1: 聚合调度 API (Buffer / Metricool / n8n Webhook) [主力]   │
│ 适用于：LinkedIn, X (Twitter), Facebook, Instagram, Pinterest │
├──────────────────────────────────────────────────────────────┤
│ Tier 2: 官方原生 API & 专用成熟 MCP (GitHub, Slack, Telegram)    │
│ 适用于：技术发布、团队协同群播、开源生态公告                         │
├──────────────────────────────────────────────────────────────┤
│ Tier 3: 规范化人工交付包 (Standard Release Package) [防封隔离]   │
│ 适用于：小红书 (Xiaohongshu)、微信私域/朋友圈、高权重主号         │
├──────────────────────────────────────────────────────────────┤
│ Tier 4: 浏览器自动化 (Chrome DevTools / Playwright MCP) [最终兜底]│
│ 适用于：仅开放网页端且无任何开放 API 的国内专栏（知乎/掘金存草稿）  │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、各梯队实操工具与成熟 MCP 配置

### Tier 1：聚合 API (Buffer / n8n / Metricool) —— 推荐首选
* **原理**：只需一个统一的 API Token 或 Webhook URL，即可向所有绑定的主流海外社媒分发排程。
* **执行命令**：
  ```bash
  # 通过 Buffer API 原生排程
  python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
    --channel buffer \
    --file ./posts/linkedin-post.md \
    --schedule "2026-09-25T14:00:00Z"

  # 通过 n8n Webhook 触发
  python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
    --channel n8n \
    --file ./posts/x-thread.md
  ```

### Tier 2：成熟专用 MCP 与特定官方 API
在支持 MCP 的 Agent 环境中，优先使用成熟的专项官方 MCP，而不是通用网页自动化：
1. **GitHub MCP (`mcp_github_*`)**：
   - 官方支持管理 Repo Releases、Discussions 与 Issues，技术团队发布首选。
2. **Slack MCP (`mcp_slack_*`) / Discord Webhook**：
   - 官方通道推送社群更新与首发通知。
3. **Telegram Bot API**：
   - 最纯粹的 100% 成功率广播方式：
   ```bash
   python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
     --channel telegram \
     --text "📢 新版本发布！阅读完整更新日志..."
   ```

### Tier 3：高风控规范化人工发布包 (Release Package)
针对小红书和微信私域，绝不贪图脚本自动化的省事，坚决遵循课程防封号铁律：
* 导出标准目录（已核验的正文 `xhs-draft.md` + 3:4 高清 SVG/PNG 渲染卡 + 评论区暗号）。
* 人工在手机端官方 App 5 分钟内点选发布，安全保号。

### Tier 4：Chrome DevTools MCP / Playwright MCP (最后底线)
仅用于以下场景：
- 国内技术社区（知乎专栏、掘金、微信公众号后台）无任何对外发布 API。
- 策略：**仅用于将文章填写并保存到草稿箱 (Save Draft)**，绝不直接自动点击最终发布，保留人工最后一击审核。
