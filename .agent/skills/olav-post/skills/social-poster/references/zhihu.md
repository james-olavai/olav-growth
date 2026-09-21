# 知乎文章/想法 Workflow

## 内容指引

读 [content-strategy.md](../../content-writer/references/content-strategy.md) → 知乎 部分再写内容。

**语气**：结构化、学术但易读、书面中文，第一人称反思 OK。

**知乎有两种发布形式**：
- **想法（Idea）**：短文，400 字以内，类似推文，适合小更新
- **文章（Article）**：长文，有标题、标签、分类，适合功能介绍或技术深度分析

本 workflow 默认使用**文章**形式（发布 draft）。

---

## 内容生成（浏览器操作前必须完成）

草稿在 `olav-post/archive/YYYY-MM-DD/zhihu.md` — 由 `content-writer` 生成。
读取草稿，确认通过以下自查项目后再打开浏览器。

### 强制自查

```
[ ] 没有"赋能"、"助力"、"全面"、"深度"、"智能化"、"业界领先"、"无缝"、"强大"
[ ] 开头不是功能列表，而是一个具体问题或场景
[ ] 至少一处解释了"为什么"做这个决策（而非只说"做了什么"）
[ ] 至少一处有具体数据（时间、行数、次数等）
[ ] 至少一处承认了当前的局限
[ ] 用书面语（书面中文），无网络口语
[ ] 标题在 50 字以内
[ ] 内容与其他平台草稿无重复段落
```

---

## Browser Workflow（Chrome DevTools MCP）

### 1. 打开知乎写文章页面

```
mcp_chrome-devtoo_navigate_page → url: "https://zhuanlan.zhihu.com/write"
mcp_chrome-devtoo_wait_for → text: ["请输入正文", "草稿备份", "创作助手"]
mcp_chrome-devtoo_take_snapshot → 确认登录状态
```

**注意**：该页面加载较慢，使用 `wait_for` 而非 `take_screenshot` 避免超时。  
**登录检查**：如果 URL 跳转至 `https://www.zhihu.com/signin`，停止，提示用户手动登录后继续。  
**已登录标识**：页面标题 "写文章 - 知乎"，正文区出现 "请输入正文" 占位符。

### 2. 填写标题

```
mcp_chrome-devtoo_take_snapshot → 找标题输入框（placeholder "请输入标题"）
mcp_chrome-devtoo_click → 标题框 ref
mcp_chrome-devtoo_type_text → 准备好的标题
```

### 3. 填写正文

知乎编辑器基于 Draft.js，推荐先尝试直接点击编辑区域再输入。

```
mcp_chrome-devtoo_take_snapshot → 找正文编辑区（class 包含 "editor" 或 contenteditable）
mcp_chrome-devtoo_click → 正文区域 ref
mcp_chrome-devtoo_type_text → 准备好的文章正文（纯文本，不含 Markdown 格式）
```

> 注意：知乎编辑器不原生支持 Markdown。粘贴 Markdown 符号会显示为字面字符。
> 如果文章有格式需求（标题、加粗），需要在输入后手动通过工具栏设置，或使用键盘快捷键（Ctrl+B 加粗）。

### 4. 插入架构图（可选，推荐）

在正文合适位置插入图表（在文字输入后执行）：

> [!CAUTION]
> **严禁点击**编辑器工具栏中的"图片"图标。点击会打开系统文件管理器，导致 Chrome MCP 挂起。

**正确流程：**
1. `mcp_chrome-devtools_take_snapshot` (verbose: true) → 寻找隐藏的 `<input type="file">` 元素。注意：知乎的 input 元素可能带有 `accept="image/*"`。
2. `mcp_chrome-devtools_upload_file` (UID: `<input type="file"> ref`)
3. `mcp_chrome-devtools_wait_for` → text: ["图片上传完成", "插入成功"]

**进阶方案（Fetch POST）：** 若找不到 input，可读取本地图片 base64 后通过 `evaluate_script` 发送：
```javascript
// 注意：以下 endpoint 可能随知乎改版变化
const b64 = "data:image/webp;base64,..."; 
const blob = await (await fetch(b64)).blob();
const formData = new FormData();
formData.append('picture', blob); // 知乎的字段名通常是 picture 或 image
fetch('/api/v4/articles/upload_image', { method: 'POST', body: formData });
```
如果工具栏图片按钮找不到或上传失败，跳过——提醒用户手动插入图片。

### 5. 保存草稿（禁止发布）

```
mcp_chrome-devtoo_take_snapshot → 找"保存草稿"或右上角的草稿按钮
mcp_chrome-devtoo_click → 保存草稿 ref
mcp_chrome-devtoo_wait_for → 出现"草稿已保存"提示
mcp_chrome-devtoo_take_screenshot → 确认保存成功
```

如果找不到草稿按钮，尝试：`Ctrl+S` 快捷键。

**绝对禁止点击 "发布" 按钮。** 管理员必须手动审查。

### 6. 视觉确认 + 汇报用户

```
mcp_chrome-devtoo_take_screenshot → 截图草稿当前状态（标题+正文可见）
```

立即汇报用户：
- 截图（标题、正文均可见）
- 草稿保存状态：是/否
- 草稿管理地址：`https://www.zhihu.com/creator/manage/creation/article`
- 确认信息："草稿已保存，请前往知乎草稿箱审查后手动发布。"

---

## 故障排查

| 问题 | 处理方式 |
|---|---|
| 编辑器加载失败 | 刷新页面后重试 |
| 文字输入但不显示 | 先点击编辑区域 focus，再尝试 `mcp_chrome-devtoo_fill` |
| 跳转到登录页 | 停止，提示用户登录 |
| 标题框有字数限制 | 知乎标题最多 50 字，超出需要截断 |

## 备注

- 知乎文章草稿保存后 URL 格式：`https://zhuanlan.zhihu.com/p/<draft_id>`
- 发布前可以先预览，预览不等于发布
