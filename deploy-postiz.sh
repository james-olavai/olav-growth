#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTIZ_DIR="${SCRIPT_DIR}/deploy/postiz"

echo "=================================================="
echo " 🚀 Launching Postiz Social Publishing Stack"
echo "=================================================="

# 1. Check if deploy/postiz/.env exists, if not generate it
if [ ! -f "${POSTIZ_DIR}/.env" ]; then
    echo "[INFO] Initializing secrets and environment..."
    python3 "${POSTIZ_DIR}/setup_env.py"
fi

cd "${POSTIZ_DIR}"

# Check if Cloudflare Tunnel Token is configured and non-empty (MANDATORY)
CF_TOKEN=$(grep -E '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=' "${POSTIZ_DIR}/.env" 2>/dev/null | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')
MAIN_URL=$(grep -E '^\s*MAIN_URL\s*=' "${POSTIZ_DIR}/.env" 2>/dev/null | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')

if [ -z "${CF_TOKEN}" ]; then
    echo "=================================================="
    echo " ❌ [ERROR] 缺少必填项：CLOUDFLARE_TUNNEL_TOKEN"
    echo "=================================================="
    echo "Postiz 排期系统必须配合 Cloudflare Tunnel (HTTPS) 运行："
    echo "  1. 社交平台 OAuth (X/LinkedIn/Meta) 强制要求权威公网 HTTPS 回调；"
    echo "  2. 彻底杜绝浏览器跨设备访问时的 Cookie 鉴权失效与网络拦截。"
    echo ""
    echo "👉 快速配置步骤（仅需 2 分钟）："
    echo "  1. 登录 Cloudflare Zero Trust 控制台: https://one.dash.cloudflare.com/"
    echo "  2. 进入 Networks ➔ Tunnels ➔ 点击 'Create a Tunnel' (选择 Cloudflared)"
    echo "  3. 复制生成的 Tunnel Token (通常为长字符串 ey...)"
    echo "  4. 在 Tunnel 的 'Public Hostname' 页面添加一条路由："
    echo "     - Subdomain / Domain: 你的公网域名 (例如 postiz.yourdomain.com)"
    echo "     - Service Type:       HTTP"
    echo "     - URL:                postiz:5000"
    echo "  5. 打开 ${POSTIZ_DIR}/.env 填入："
    echo "     CLOUDFLARE_TUNNEL_TOKEN=\"你的_Token\""
    echo "     MAIN_URL=\"https://你的公网域名\""
    echo "     FRONTEND_URL=\"https://你的公网域名\""
    echo "     NEXT_PUBLIC_BACKEND_URL=\"https://你的公网域名/api\""
    echo "     NOT_SECURED=\"false\""
    echo ""
    echo "配置完成后，重新运行: ./deploy-postiz.sh"
    echo "=================================================="
    exit 1
fi

if [[ "${MAIN_URL}" == *"yourdomain.com"* ]] || [[ "${MAIN_URL}" == *"localhost"* ]]; then
    echo "[WARNING] ⚠️  检测到 MAIN_URL 当前为: ${MAIN_URL}"
    echo "           如果尚未修改为你实际的 Cloudflare 域名，社媒 OAuth 授权将无法跳转！"
    echo "           请确保 ${POSTIZ_DIR}/.env 中的 MAIN_URL 与 Cloudflare Public Hostname 一致。"
fi

echo "[INFO] 🛡️ Cloudflare Tunnel Token 已检测到。准备启动生产集群..."
echo "[INFO] 启动服务: postiz + postiz-postgres + postiz-redis + postiz-cloudflared"

COMPOSE_ARGS=""
if [ "$1" == "--with-proxy" ]; then
    echo "[INFO] 🌐 启用海外出站加速代理容器 (outbound-proxy)..."
    COMPOSE_ARGS="--profile proxy"
fi

echo "[INFO] 拉取并启动 Docker 容器..."
if docker compose version >/dev/null 2>&1; then
    docker compose ${COMPOSE_ARGS} up -d
elif docker-compose version >/dev/null 2>&1; then
    docker-compose ${COMPOSE_ARGS} up -d
else
    echo "[ERROR] 未检测到 docker compose 或 docker-compose 命令，请检查 Docker 安装。"
    exit 1
fi

echo "=================================================="
echo " ✅ Postiz 生产集群启动成功！"
echo "    - 🌐 公网 Web 访问:  ${MAIN_URL:-https://your-domain.com}"
echo "    - 🛡️ 安全入站网关:   Cloudflare Tunnel (postiz-cloudflared 运行中)"
echo "    - 💻 本地内部 API:   http://127.0.0.1:5000 (供本机 Python CLI 分发)"
echo "    - 🗄️ 核心数据库:     PostgreSQL (15-alpine)"
echo "    - ⚡ 缓存队列:       Redis (7-alpine)"
echo "=================================================="
echo "查看容器实时日志: cd deploy/postiz && docker compose logs -f"
echo "检查运行状态:     docker ps | grep postiz"
