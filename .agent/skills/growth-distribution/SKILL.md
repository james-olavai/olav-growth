---
name: growth-distribution
description: "Review, bundle, and distribute marketing assets across channels. Manages human-in-the-loop gatekeeper approvals, exports standardized Release Packages for high-risk platforms (Xiaohongshu, WeChat), formats API queue payloads (Buffer/Metricool), and optimizes GEO (llms.txt) for AI answer engines."
argument-hint: "Optional: --package <topic-id> | --geo | --gate-check"
---

# Growth Distribution Skill: 分发合规与数据闭环

通用的营销资产交付、合规发布与增长归盘技能。执行**人机终审把关 (Gatekeeper)**，实现**双轨分流发布**（支持 API 的自动排程 vs 高风控平台的规范化人工发布包），并提供 **GEO (Generative Engine Optimization)** 索引优化。

---

## 核心职责

1. **Gatekeeper 2 人工终审**：核验事实、合规红线与落地页有效性。
2. **双轨分流交付**：
   - **轨道 A（API 自动化）**：Buffer / Metricool / Webhook 队列排程与 UTM 标记。
   - **轨道 B（高风控平台人工发布包）**：打包 `manifest.md`、序号高清 3:4 图、文案、发布时间建议，杜绝封号。
3. **GEO (生成式引擎优化)**：自动生成 `llms.txt` 和 `llms-full.txt`，优化 Perplexity、ChatGPT 等 AI 推荐收录。
4. **数据归盘与复利 (Content Snowball)**：将各平台反馈数据回填至 `memory.md`。

---

## 常用操作指引

### 1. 配置发布渠道 API 密钥与凭证
对外发布所需的 API Key 均存储在根目录 `.env` 中。支持通过命令行快捷工具直接写入并立即校验：
```bash
# 配置 Postiz API Key（在 Postiz Web 端注册后，于 Settings -> API Tokens 生成并填入）
python .agent/skills/growth-distribution/scripts/publish/set_key.py --postiz-key "你的_postiz_api_key"

# 或一键配置 Telegram Bot / Buffer / Slack
python .agent/skills/growth-distribution/scripts/publish/set_key.py \
  --telegram-token "123456:ABC..." --telegram-chat "123456789"
```

### 2. 发布渠道与 API 连接性诊断
在正式发布前，一键测试当前配置的所有渠道状态（Postiz, Buffer, Telegram, Slack 等）：
```bash
python .agent/skills/growth-distribution/scripts/publish/publish_api.py --test-connection
```

### 3. 打包高风控平台人工发布包 (Tier 2 规避封号)
```bash
python .agent/skills/growth-distribution/scripts/package_release.py --topic-id "TOPIC-20260920-01"
```

### 4. 原生 API / Webhook 自动分发 (Tier 1 主力推荐)
```bash
# 通过 Postiz 排程或直发 (支持 LinkedIn, X, IG, Pinterest, YouTube 等)
python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
  --channel postiz \
  --file content/campaigns/20260920-topic-01/posts/linkedin.md \
  --schedule "2026-09-25T14:00:00Z"

# 通过 Buffer 原生 API 排程分发
python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
  --channel buffer \
  --file content/campaigns/20260920-topic-01/posts/linkedin.md

# 通过 n8n Webhook 触发自动化流水线
python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
  --channel n8n \
  --file content/campaigns/20260920-topic-01/posts/x-thread.md
```

### 5. 生成/更新 AI 搜索引擎索引 (GEO llms.txt)
```bash
python .agent/skills/growth-distribution/scripts/generate_llms_txt.py \
  --root . \
  --out ./public
```

### 6. 持久化浏览器会话与 Cookie 自动同步 (中文平台 Tier 3/4)
在宿主机启动持久化 Chromium 容器（`./deploy-browser.sh`）后，通过 Web VNC (`http://localhost:3000`) 扫码登录小红书/知乎，随后自动通过 CDP 协议同步凭据至根目录 `.env`：
```bash
# 查看当前浏览器运行状态与活动标签页
python .agent/skills/growth-distribution/scripts/publish/sync_browser_cookies.py --status

# 一键捕获小红书与知乎登录态并写入根目录 .env
python .agent/skills/growth-distribution/scripts/publish/sync_browser_cookies.py --sync-all
```

---

## 发布分级阶梯指引 (Publishing Hierarchy)
关于为什么 Chrome DevTools MCP 是最后一招，以及各平台的成熟 API / 专用 MCP 选型，请参阅：
- [四级发布阶梯与 MCP 选型指南](references/publishing-hierarchy.md)
- [Speed-to-Lead 与私信导流安全白皮书](references/speed-to-lead.md)
