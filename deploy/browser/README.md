# Marketing Persistent Browser (Chromium + Web VNC + CDP)

本目录提供了一个专为营销自动化、创作者多平台登录与 MCP 自动化操作设计的持久化 Chromium 环境。

---

## 核心特性

1. **内置 Web VNC (免客户端)**：
   直接在任何浏览器访问 `http://localhost:3000`，即可打开图形化 Chromium 桌面。
   支持鼠标点击、拖拽滑块拼图验证码、手机微信/小红书 App 扫码登录。
2. **会话永久持久化**：
   所有登录状态、Cookie、LocalStorage、缓存与插件配置全部保存在宿主机挂载的 `./chrome-profile` 目录中。
   容器重启或电脑关机后，重新拉起依然保持登录，**无需重复扫码**。
3. **CDP 远程调试 (Port 9222)**：
   原生暴露 Chrome DevTools Protocol 端口，支持：
   - Antigravity / Claude 的 Chrome DevTools MCP (`@modelcontextprotocol/server-puppeteer`) 接入
   - 本地脚本自动读取已登录网站的 Cookie（如小红书 `a1` / `web_session`）并同步到根目录 `.env`。
   - 自动化文章、图片与草稿写入。

---

## 快速启动

在根目录执行快捷启动脚本：
```bash
./deploy-browser.sh
```

---

## 使用流程

1. **在浏览器中打开 Web 桌面**：
   * **局域网跨设备访问（推荐）**：打开 **`https://<YOUR_SERVER_IP>:3001`**（必须使用 HTTPS，浏览器提示证书风险时点击“高级”➔“继续前往”）。
   * **宿主机本机访问**：打开 `http://localhost:3000` 或 `https://localhost:3001`。
   *(注：现代浏览器 WebCodecs 音画串流技术要求必须在安全上下文 (Secure Context) 下运行，因此局域网 IP 访问必须使用 HTTPS 3001 端口，否则会提示 requires a secure connection)*。
2. 在打开的 Chromium 桌面中输入你要绑定的创作者平台：
   - 小红书创作者中心：`https://creator.xiaohongshu.com`
   - 微信公众平台：`https://mp.weixin.qq.com`
   - 知乎专栏：`https://zhuanlan.zhihu.com`
3. 拿出手机扫码登录，完成滑块拖动校验。
4. 登录成功后，即可直接关闭 `http://localhost:3000` 网页。
5. 在项目根目录执行 Cookie 同步工具：
   ```bash
   python .agent/skills/growth-distribution/scripts/publish/sync_browser_cookies.py
   ```
   脚本将自动通过 9222 CDP 端口获取小红书/知乎等平台的最新有效 Cookie，并直接更新至根目录 `.env`。
