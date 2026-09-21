# 微信公众号文章 Workflow

## 内容指引

读 [content-strategy.md](../../content-writer/references/content-strategy.md) → 微信公众号 部分再写内容。

**语气**：叙事性，故事驱动，面向更广泛的技术读者（不一定是专家），有温度。

---

## 内容生成（浏览器操作前必须完成）

草稿在 `olav-post/archive/YYYY-MM-DD/wechat-mp.md` — 由 `content-writer` 生成。
读取草稿，确认通过以下自查项目后再打开浏览器。

### 强制自查

```
[ ] 没有"赋能"、"助力"、"全面"、"深度"、"智能化转型"、"业界领先"、"无缝对接"
[ ] 开头是具体场景，不是"随着AI技术的发展..."
[ ] 没有功能列表（•）
[ ] 没有外链（微信屏蔽外链）——博客/GitHub 链接只放在文末"阅读原文"
[ ] 至少一个类比解释了复杂技术概念
[ ] 结尾是问题或反思，不是"赶快试试吧！"
[ ] 字数在 1000–2500 之间
[ ] 与知乎/掘金草稿是完全不同的叙事角度（微信讲故事，知乎讲逻辑，掘金讲操作）
```

---

## Browser Workflow（Chrome DevTools MCP）

微信公众号需要在**微信公众平台网页版**操作。

### 1. 打开公众号主页，进入写文章入口

```
mcp_chrome-devtoo_navigate_page → url: "https://mp.weixin.qq.com/"
mcp_chrome-devtoo_wait_for → text: ["新的创作", "OlavAI"]
mcp_chrome-devtoo_take_snapshot → 确认登录状态
```

**登录检查**：微信公众平台使用微信扫码登录，无法自动化登录过程。  
如页面显示扫码登录界面，停止，提示用户**用微信 App 扫码登录**，登录后通知继续。  
**已登录标识**：页面出现 "新的创作" 标题，账号名 "OlavAI" 显示在侧边栏。

### 2. 点击"文章"，进入图文编辑器

```
mcp_chrome-devtoo_take_snapshot → 找 "新的创作" 区域下的 "文章" 文字元素
mcp_chrome-devtoo_click → "文章" StaticText ref（位于 "新的创作" heading 下方）
mcp_chrome-devtoo_wait_for → text: ["请在这里输入标题", "保存草稿"]
mcp_chrome-devtoo_list_pages → 选择新打开的编辑器页面（URL 含 appmsg_edit_v2）
```

**注意**：点击"文章"会打开新标签页，URL 格式为：  
`https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token=TOKEN`  
token 是会话级别的，不要硬编码。

### 3. 填写标题

```
mcp_chrome-devtoo_take_snapshot → 找标题输入框（placeholder "请在这里输入标题"）
mcp_chrome-devtoo_click → 标题框 ref
mcp_chrome-devtoo_type_text → 准备好的文章标题
```

### 4. 填写正文

微信编辑器是自定义富文本编辑器（非 contenteditable 标准实现）。

```
mcp_chrome-devtoo_take_snapshot → 找正文编辑区（通常 class 包含 "rich_media_content" 或 id="ueditor_0"）
mcp_chrome-devtoo_click → 正文区域 ref（点击激活编辑器）
mcp_chrome-devtoo_type_text → 准备好的文章内容
```

> **注意**：微信编辑器对 MCP 的 `type_text` 响应可能不稳定。
> 备选方案：将文章内容复制到系统剪贴板（需用户手动 Ctrl+V 粘贴），
> 或使用 `mcp_chrome-devtoo_evaluate_script` 注入内容：
> ```javascript
> // 仅作为最终备用方案
> document.querySelector('.rich_media_content').focus();
> document.execCommand('insertText', false, '文章内容');
> ```

### 5. 设置封面图（必须）

微信公众号文章**必须设置封面图**，否则无法发布。

> [!IMPORTANT]
> **绝对不可点击** "选择封面" 或 "添加图片" 按钮。这会触发文件浏览器。

**正确做法：**
1. `mcp_chrome-devtools_take_snapshot` (verbose: true) → 在右侧封面图区域下方搜寻隐藏的 `<input type="file" name="file">`。
2. `mcp_chrome-devtools_upload_file` (UID: `<input type="file"> ref`)
3. `mcp_chrome-devtools_wait_for` → text: ["上传成功", "使用来自图片库"]

**进阶：使用 POST 上传（Fetch）**
如果 UI 元素难以定位，可以使用 `fetch` 将图片直接 POST 到微信后台素材接口（需要 token）：
```javascript
// 注意：必须从当前页面 URL 中提取 token 参数
const token = new URLSearchParams(window.location.search).get('token');
const b64 = "data:image/webp;base64,...";
const blob = await (await fetch(b64)).blob();
const formData = new FormData();
formData.append('file', blob);
fetch(`/cgi-bin/filetransfer?action=upload_material&token=${token}`, { method: 'POST', body: formData });
```
如果找到"裁剪"对话框，选择默认裁剪后确认。  
如果找不到上传方式，截图后提示用户手动上传封面图。

### 6. 保存草稿（禁止发布）

**绝对禁止点击 "发布" 或 "群发" 按钮。** 管理员必须在手机端或网页端手动审查后群发。


```
mcp_chrome-devtoo_take_snapshot → 找"保存草稿"按钮（通常在顶部工具栏）
mcp_chrome-devtoo_click → 保存草稿 ref
mcp_chrome-devtoo_wait_for → 出现"保存成功"提示
mcp_chrome-devtoo_take_screenshot → 确认草稿已保存
```

### 7. 视觉确认 + 汇报用户

```
mcp_chrome-devtoo_take_screenshot → 截图草稿当前状态（标题+正文可见）
```

立即汇报用户：
- 截图（标题、正文均可见，账号名 OlavAI 可见）
- 草稿保存状态：已保存 / 未保存
- 提醒：草稿箱入口在微信公众号后台→内容管理→草稿箱
- 确认信息："草稿已保存，请在微信公众号草稿箱审查后手动群发。"

**绝对禁止点击"群发"或"预览"后的"发送"按钮。**

---

## 故障排查

| 问题 | 处理方式 |
|---|---|
| 需要扫码登录 | 停止，提示用户扫码，等用户确认后继续 |
| 编辑器无响应 | 截图给用户，建议手动粘贴内容 |
| 找不到"保存草稿"按钮 | 微信后台改版频繁，重新 snapshot 确认最新 DOM |
| 内容输入后消失 | 微信编辑器可能需要先点击一次激活，再输入 |

## 备注

- 推荐先在**安全模式**下测试（草稿预览）
- 内容不能包含外链（微信会屏蔽或转为灰字）——博客链接只能作为文末"阅读原文"添加
- 字数建议 800–2500 字；低于 300 字会影响展示效果
