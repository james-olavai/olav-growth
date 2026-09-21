# Postiz 本地/私有化部署指南 (开源 Buffer 替代品)

> **Postiz** (原 GitRoom) 是目前 GitHub 上星标最多 (16k+ Stars) 的开源社媒排程管理平台。
> 本目录提供了生产级 `docker-compose.yml`，让你彻底摆脱 Buffer 的月费、3个渠道上限与队列限制。

---

## 一、核心优势

1. **零渠道收费**：连接 20 个社交账号也不收一分钱。
2. **原生 MCP 支持**：自带官方 Model Context Protocol (MCP)，AI Agent 可直接通过工具调度发帖。
3. **支持 30+ 平台**：X (Twitter)、LinkedIn、Reddit、Instagram、TikTok、YouTube、Pinterest、Facebook、Threads、Bluesky 等。
4. **与本项目无缝联动**：启动后，项目中的 `publish_api.py --channel postiz` 可以直接通过 REST API 调度发布。

---

## 二、3 步快速启动

### 步骤 1：获取 Cloudflare Tunnel Token（必须）
为了支持海外社交平台（X / LinkedIn / Meta / Reddit 等）的 OAuth 回调，并解决局域网与移动端访问的 Cookie 认证，Postiz 必须通过权威公网 HTTPS 访问：
1. 登录 [Cloudflare Zero Trust 控制台](https://one.dash.cloudflare.com/) ➔ **Networks** ➔ **Tunnels**。
2. 点击 **Create a Tunnel**（选择 Cloudflared），复制生成的 Tunnel Token（以 `ey...` 开头的一长串字符）。
3. 在该 Tunnel 的 **Public Hostname** 配置一条路由规则：
   * **Domain**: 你的公网域名（例如 `postiz.yourdomain.com`）
   * **Service Type**: `HTTP`
   * **URL**: `postiz:5000`

### 步骤 2：配置环境变量
打开 `deploy/postiz/.env` 填入你的公网域名与 Tunnel Token：
```bash
MAIN_URL="https://postiz.yourdomain.com"
FRONTEND_URL="https://postiz.yourdomain.com"
NEXT_PUBLIC_BACKEND_URL="https://postiz.yourdomain.com/api"
NOT_SECURED="false"

CLOUDFLARE_TUNNEL_TOKEN="你的_Cloudflare_Tunnel_Token"
```

### 步骤 3：一键启动 Docker 生产集群
在项目根目录或宿主机终端执行：
```bash
./deploy-postiz.sh
```
*启动完成后：*
- 入站流量全自动通过 Cloudflare Tunnel (`postiz-cloudflared`) 承接并转发至 Postiz。
- 本地端口 `127.0.0.1:5000` 供本机 Python CLI 自动化发布脚本调用，对局域网其他设备隐藏以防端口扫描。
- 打开浏览器访问你的公网域名 `https://postiz.yourdomain.com` 即可直接进入 Postiz Web 界面！

---

## 三、与本项目 Agent 联动配置

在 Postiz 界面左侧导航栏：
1. 前往 **Settings** ➔ **API Keys** ➔ 生成并复制 API Key。
2. 将该 Key 填入项目根目录的 `.env`：
   ```bash
   POSTIZ_API_URL="http://localhost:5000/api/public/v1"
   POSTIZ_API_KEY="你的_postiz_api_key"
   ```
3. 即可使用本项目的原生分发脚本一键发布：
   ```bash
   python .agent/skills/growth-distribution/scripts/publish/publish_api.py \
     --channel postiz \
     --file ./releases/release-01/posts/linkedin.md \
     --profiles "int_linkedin_xxx"
   ```

---

## 四、出站加速代理配置 (可选)

若宿主机网络处于受限环境，无法直接访问 `api.twitter.com`、`api.linkedin.com` 等海外 API，可启用集成的出站代理容器：
1. 在 `.env` 中配置你的上游代理：
   ```bash
   UPSTREAM_ENCRYPTED_PROXY="socks5://127.0.0.1:1080"
   HTTP_PROXY="http://outbound-proxy:7890"
   HTTPS_PROXY="http://outbound-proxy:7890"
   ```
2. 启动时带代理参数：
   ```bash
   ./deploy-postiz.sh --with-proxy
   ```

