# Browser & Interactive Search Playbook: 实时热点与高风控平台抓取指南

> 本指南介绍如何利用 Agent 自带的浏览器能力（交互式 `/browser` 指令）与内置检索工具（`search_web` / `read_url_content`），突破反爬与验证码限制，获取小红书、微博、百度风云榜、Twitter/X 等平台的实时热点与高互动评论。

---

## 1. 为什么需要浏览器能力？
很多国内主流社交平台（小红书、抖音、微信公众号、微博）具备极严的 WAF（Web Application Firewall）和滑块验证码机制，纯脚本 `curl` 无法直接拉取。
此时利用 Agent 的**浏览器环境**成为最合规、最稳定的热点探测手段。

---

## 2. 交互式 `/browser` 玩法（用户主导/协同）
用户可以在聊天框输入 `/browser` 启动浏览器交互模式：

### 场景 A：小红书热搜词与爆款笔记拆解
1. 在 `/browser` 中打开小红书网页版 (`https://www.xiaohongshu.com/explore`)。
2. 搜索品牌所在领域的核心关键词（例如：“外贸获客”、“独立站增长”、“AI办公”）。
3. 观察“综合”与“最热”排名前 5 的笔记：
   - 记录封面大字报的文案句式（提炼到 `HookGen` 候选池）。
   - 打开第一篇笔记的高赞评论区，寻找用户的真实吐槽与疑惑（提炼为 `Raw Quotes`）。
4. 将关键信息粘贴给 Agent，Agent 自动调用 `brand-core` 生成 `SIG-YYYYMMDD-XX.md` 信号卡。

### 场景 B：Google Trends 探索深度对比
1. 在 `/browser` 中访问 `https://trends.google.com/trends/explore?q=cursor,windsurf,trae`。
2. 观察过去 30 天的搜索热度走势、飙升相关查询 (Breakout Queries) 与地域分布。
3. 截图或导出 CSV，让 Agent 提取 Breakout 关键词作为时效性论据。

---

## 3. Agent 自动化检索工具链 (无需打开界面)
在日常自动化巡检中，Agent 无需弹出浏览器，直接使用原生工具即可完成热点侦测：

| 工具 | 适用场景 | 示例用法 |
| :--- | :--- | :--- |
| `search_web` | 检索实时趋势、突发新闻、行业政策、竞品动态 | `search_web(query="小红书 2026 算法 调整 获客")` |
| `read_url_content` | 将无强防爬的公开网页转为 Markdown 纯文本分析 | `read_url_content(Url="https://news.ycombinator.com")` |
| `fetch_google_trends.py` | 免鉴权拉取 Google 官方 20+ 国家/地区实时热搜榜 | `python fetch_google_trends.py --geo TW` |
| `fetch_tech_trends.py` | 抓取 Hacker News Show/Top 讨论并过滤关键词 | `python fetch_tech_trends.py --type show` |

---

## 4. 从热点到 Signal Card 的清洗规则
从任何渠道（浏览器、Google Trends、Hacker News）抓取到热点后，必须按以下三步去噪：
1. **剔除娱乐八卦**：过滤掉明星绯闻、单纯体育赛事、社会杂闻（除非业务直接相关）。
2. **提炼底层矛盾**：将热点表象转化为用户心智冲突（例如：“某大厂裁员” -> “副业出海获客工具需求上升”）。
3. **沉淀证据源**：必须附带原始新闻链接或截图，作为后续 `content-strategist` 打分中 `Evidence (证据度)` 的给分依据。
