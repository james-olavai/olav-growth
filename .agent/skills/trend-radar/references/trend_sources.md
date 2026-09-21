# Trend Sources Matrix: 全球与中文营销热点雷达数据源矩阵

> 本文档梳理了跨行业、多平台热点追踪的数据源清单、获取方式及风控注意事项。

---

## 1. 免 API Key 极速拉取数据源 (脚本级集成)

| 数据源 | 覆盖区域 | 获取机制 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **Google Trends Daily** | 全球 30+ 地区 (US, TW, HK, SG, JP 等) | 官方 RSS (`trends.google.com/trending/rss?geo=XX`) | 抓取突发高热词、大众搜索激增话题 |
| **Hacker News (Top/Show)** | 全球技术与极客圈 | Firebase 官方公开 JSON API | 开发者工具、开源项目、AI 应用、创业复盘 |
| **Reddit (r/technology, r/SaaS)** | 欧美 B2B / SaaS | JSON 终端 (`/r/{sub}/hot.json`) | 痛点挖掘、竞品吐槽、真实从业者提问 |
| **GitHub Trending** | 全球开源代码库 | 页面 HTML / RSS | 发现突发暴涨的 AI 智能体、开发工具 |

---

## 2. 需 Agent 浏览器 / 搜索工具协同的数据源 (防爬与国内主域)

| 数据源 | 平台特性 | 推荐获取方式 | 价值重点 |
| :--- | :--- | :--- | :--- |
| **小红书 (Xiaohongshu)** | 极严反爬与账号风控 | 使用 `/browser` 登录搜索行业词 | 爆款封面排版、标题句式、高赞评论吐槽 |
| **微信公众号爆文** | 封闭生态 | 微信搜一搜 + Agent `search_web` | 行业深度公关文、长线思考、企业成功案例 |
| **微博热搜榜** | 实时性极强，娱乐偏重 | 微博网页热搜榜 + 语义过滤 | 突发行业政策、公众情绪拐点 |
| **百度热搜 / 百度指数** | 国内大众下沉搜索 | 百度风云榜 (`top.baidu.com`) | 大众认知度对比、需求真伪验证 |
| **Twitter / X Trending** | 科技与 AI 圈第一手源头 | X 网页搜索 + `/browser` | 最前沿技术发布、创始人公开辩论 |

---

## 3. 热点筛选与业务对齐漏斗 (Funnel Protocol)

```
[原始抓取池] (每日 100+ 条热搜 / 帖子 / 新闻)
       │
       ▼
[硬规则过滤] (剔除娱乐八卦、纯政治争议、无解死结)
       │
       ▼
[SOT 业务匹配] (与 BUSINESS-SOT.md 中的 ICP痛点、功能标签做词义匹配)
       │
       ▼
[Signal Card] (输出 SIG-YYYYMMDD-XX.md 至 content/candidate_signals/)
       │
       ▼
[Content Strategist] (五维打分: Relevance * Timing * Discussion * Evidence / Risk)
```
