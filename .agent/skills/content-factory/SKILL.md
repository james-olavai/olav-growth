---
name: content-factory
description: "Generate multi-platform native content and visual assets from BUSINESS-SOT.md and campaign briefs. Implements the 3-stage prompt chain (Data In -> HookGen -> De-grease with FuzzyVariables), renders 3:4 visual cards, and formats native drafts for Xiaohongshu, LinkedIn, X, Blog/WeChat, YouTube, Reddit, and Product Hunt."
argument-hint: "Optional: --topic-brief <path> | --platforms all | xhs,linkedin,x,blog | --render-cards"
---

# Content Factory Skill: 单源多产出内容工厂

通用的内容生产与视觉渲染技能。基于底层真相源（`BUSINESS-SOT.md`）、战役简报（`campaign-brief.md`）或爆款配方指令单（由 `viral-hacker` 抽骨架生成的 `VRB-*.json`），执行**三段式 Prompt 链**与**模糊变量去油自检**，并生成标准化 3:4 视觉大字报卡片。

---

## 核心生产流水线

```
BUSINESS-SOT.md + Brief ──► [阶段1: 定词 Data In] ──► [阶段2: 10 Hooks] ──► [阶段3: 去油与模糊变量] ──► [视觉大字报] ──► 多平台原生变体草稿
```

### 1. 三段式 Prompt 链
1. **阶段 1：定词 (Data In)**：锚定底层事实与用户原声，锁定核心论点与 3 个论据。
2. **阶段 2：写题 (HookGen)**：批量生成 10 个钩子（反常识、数据反差、踩坑故事、干货清单）。
3. **阶段 3：去油自检 (De-grease)**：系统级扫描并剔除假大空公文词（赋能/一站式等），强制第一人称，注入随机情绪与口语垫词（FuzzyVariables）打破 AI 痕迹。

### 2. 3:4 视觉大字报生成
- 执行规范的 1080x1440 黄金比例。
- 避开顶部 15% 状态栏与底部 20% 交互区，视觉中心大字报突出痛点。

---

## 常用操作指引

### 1. 生成随机模糊变量与去油检测
```bash
# 生成一组随机情绪标签与口语垫词
python .agent/skills/content-factory/scripts/prompt_chain.py --fuzzy

# 检查文本是否含有禁用油腻词
python .agent/skills/content-factory/scripts/prompt_chain.py --check-text "为企业全面赋能并扬帆起航"
```

### 2. 批量渲染 3:4 视觉卡片
```bash
python .agent/skills/content-factory/scripts/card_renderer.py \
  --title "多平台发布总被限流？3招打造自动化获客" \
  --badge "实战避坑" \
  --subtitle "一线实操复盘 · 杜绝AI同质化降权" \
  --points "建立品牌单一事实源，杜绝事实幻觉" "注入模糊情绪变量，打破机械AI感" "3:4大字报视觉排版，首屏完成痛点停留" \
  --cta "评论区回复【获客】领取完整搭建自查表" \
  --theme "dark_tech" \
  --out ./output/card-01.svg
```

### 3. 创意素材与配图搜索下载 (18 平台)
使用联合搜索套件的图片引擎从 Bing、Unsplash、Pixabay、Pexels 等 18 个平台批量拉取高质感封面背景与灵感图：
```bash
python tools/union-search/union_search_cli.py image "minimalist workspace tech" \
  --platforms bing pixabay unsplash \
  --limit 3 \
  --output-dir content/campaigns/assets/
```

---

## 平台原生指引参考 (Platform References)
针对各平台的受众心智、视觉尺寸与转化链路，详见 `references/platforms/`：
- [小红书 (Xiaohongshu)](references/platforms/xhs.md) - 3:4 封面大字报、CES 算法互动与评论区对暗号
- [Instagram](references/platforms/instagram.md) - 复用 3:4 卡片制作 Carousel 多图轮播与 Reels 脚本
- [Pinterest](references/platforms/pinterest.md) - 复用 3:4 大字报做意图 Pin，挂载可点击直接外链
- [LinkedIn](references/platforms/linkedin.md) - 商业长帖与 PDF Document Carousel
- [X (Twitter)](references/platforms/x-twitter.md) - 短 Hook、Threads 与 Build in Public
- [微信公众号 / 博客](references/platforms/wechat-blog.md) - 深度长文与 SEO 沉淀
- [YouTube](references/platforms/youtube.md) - How-to 实操教程与时间戳分镜
- [Reddit](references/platforms/reddit.md) - 极客社区价值交付与反硬广原则
- [Product Hunt](references/platforms/product-hunt.md) - Maker 发声与 Launch Day 集中引爆

