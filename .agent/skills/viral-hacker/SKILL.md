---
name: viral-hacker
description: "Reverse-engineer viral social media posts, extract winning hooks and story beats into pure structural formulas, and hijack live trending topics via semantic bridging with BUSINESS-SOT.md. Outputs standardized Viral Recipe Briefs and connects seamlessly to content-factory."
argument-hint: "Optional: --url <viral_url> | --search <keyword> | --topic <live_trend> | --to-factory"
---

# Viral Hacker Skill: 爆款模仿与借势破圈引擎

> **定位**：营销增长的**逆向解构情报官与模具铸造师**。  
> 专门负责从全网爆款（URL 或搜索结果）以及突发实时热搜中，**剥离原文字表象（去肉），提取底层心理学公式与叙事节奏（留骨）**，并与品牌底层事实源（`BUSINESS-SOT.md`）进行语义槽位映射，输出标准化的《爆款配方指令单 (Viral Recipe Brief)》，随后移交给 `content-factory` 极速灌装成文并渲染 3:4 视觉大字报。

---

## 一、核心架构与协作链路

```
    [全网爆款 URL / 实时热搜]
                 │
                 ▼  (借助 union-search / Jina Reader)
  ┌────────────────────────────────────────────────────────┐
  │         viral-hacker (逆向情报官 / 模具铸造师)          │
  │  1. 剥离原文表象，提取 4 维爆款基因 (Hook + 情绪 + 节拍)  │
  │  2. 匹配 6 大爆款公式库 / 4 大借势切角                 │
  │  3. 语义搭桥：注入 BUSINESS-SOT.md 品牌真实槽位        │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼ 输出《爆款配方指令单 (VRB-*.json & .md)》
  ┌────────────────────────────────────────────────────────┐
  │       content-factory (内容车间 / 事实灌装工)          │
  │  1. 填充品牌事实与客户案例 (Data In)                  │
  │  2. 注入随机情绪垫词与去油自检 (De-grease)              │
  │  3. 调用 card_renderer.py 自动生成 3:4 黄金比例大字报   │
  │  4. 原生化适配多平台草稿 (小红书、X Thread、LinkedIn)   │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
                [高互动、抗风控、全原创的多端矩阵草稿]
```

---

## 二、支持的 6 大经典爆款模具库 (`viral_formulas.json`)

系统内置了经过各平台数十万互动检验的高胜率内容模具：

| 模具 ID | 模具名称 | 核心心理学机制 | 适用平台与场景 |
| :--- | :--- | :--- | :--- |
| `ANTI_COMMON_SENSE` | **反常识认知差 / 击碎伪行规** | 醒脑震撼 + 避坑紧迫感 | 小红书封面大字报、知乎深度回答、X 揭秘 Thread |
| `BEFORE_AFTER_GAP` | **前后巨大反差 / 绝望触底反弹** | 逆袭共情 + 可复制渴望 | 个人 IP 破圈、独立开发经验复盘、创业心路 |
| `FAILURE_POSTMORTEM` | **踩坑自爆 / 血泪实操复盘** | 极度信任 + 同理心共鸣 | 技术团队避坑、出海踩坑分享、业务决策复盘 |
| `CURATED_GOLDMINE` | **极客藏宝箱 / 生产力神器清单** | 白嫖获得感 + 立即收藏欲 | 开源工具推广、高密度干货交付、自研工具发布 |
| `TROJAN_HORSE_CASE` | **借壳深扒 / 标杆爆款底层拆解** | 揭秘欲 + 商业启发 | 竞品拆解、商业模式深扒、技术架构剖析 |
| `CONTRARIAN_HOTTAKE` | **逆风执言 / 暴击浮躁狂热** | 清醒理性 + 行业反思 | LinkedIn 商业思考、X 锐评、行业深度长文 |

---

## 三、实时热点借势的 4 大切角 (`trend_jack_angles.json`)

针对全网突发热点，绝不搞令人反感的硬蹭（Cringe Hijack），而是通过**语义搭桥**选择最优切入点：

1. **打假避坑型 (The Truth-Teller)**：全网都在吹 [热点]，一线实测 7 天后，我们发现的 3 个致命隐患……
2. **平替救火型 (The Rescuer)**：[竞品/大厂] 刚刚宣布全线涨价/宕机，手把手教你开源 10 分钟平替！
3. **底层架构深扒型 (The Architect)**：为什么 [新产品] 能一夜爆火？扒开它的底层架构与技术选型。
4. **借梗吐槽共鸣型 (The Satirist)**：看完今天关于 [热搜] 的讨论，做技术的同行直接笑不出来了……

---

## 四、常用 CLI 指令速查

统一脚本位于 `.agent/skills/viral-hacker/scripts/`：

### 1. 拆解外部任意爆款链接并映射自品牌
```bash
# 从任意爆款 URL 提取骨架，并自动生成《爆款配方简报》
python .agent/skills/viral-hacker/scripts/extract_recipe.py \
  --url "https://twitter.com/example/status/123456"

# 一键打通全流水线：提取骨架 ➔ 映射 SOT ➔ 自动让 content-factory 产出四端草稿与 3:4 大字报
python .agent/skills/viral-hacker/scripts/extract_recipe.py \
  --url "https://twitter.com/example/status/123456" \
  --to-factory
```

### 2. 通过联合搜索寻找特定主题爆款并逆向
```bash
# 全网搜索“自动化营销”最新高赞贴并复刻其结构
python .agent/skills/viral-hacker/scripts/extract_recipe.py \
  --search "自动化营销避坑" \
  --to-factory
```

### 3. 突发热点借势与流量拦截 (Trend Jacking)
```bash
# 针对突发事件快速生成借势简报并交付工厂成文
python .agent/skills/viral-hacker/scripts/trend_jack.py \
  --topic "知名SaaS服务突发大面积宕机" \
  --angle rescuer \
  --to-factory
```

### 4. 手动将配方简报推入内容工厂
```bash
python .agent/skills/viral-hacker/scripts/bridge_to_factory.py \
  --brief content/campaigns/viral-briefs/VRB-20260921-xxxx.json
```

---

## 五、产出成果规范

执行 `--to-factory` 后，产出物完整收拢至：
`content/campaigns/<recipe_id>/`：
- `cover_card.svg`：严格遵循 1080x1440 黄金比例与避让区的 3:4 视觉大字报。
- `xhs_post.md`：符合小红书 CES 算法的高留存正文与互动暗号。
- `x_thread.md`：高信息密度的 5 屏推特 Threads。
- `linkedin_post.md`：适合 B2B 与出海商业认知的思考长文。
- `blog_post.md`：结构严谨的方法论深度长文。
- `campaign.json`：可直接推入 Postiz / Buffer 进行矩阵发布的战役清单。
