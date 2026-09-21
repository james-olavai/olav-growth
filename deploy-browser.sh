#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BROWSER_DIR="${SCRIPT_DIR}/deploy/browser"

echo "=================================================="
echo " 🌐 Launching Marketing Persistent Chrome (Web VNC)"
echo "=================================================="

mkdir -p "${BROWSER_DIR}/chrome-profile"
cd "${BROWSER_DIR}"

echo "[INFO] Pulling and starting Chromium container..."
if docker compose version >/dev/null 2>&1; then
    docker compose up -d --force-recreate
elif docker-compose version >/dev/null 2>&1; then
    docker-compose up -d --force-recreate
else
    echo "[ERROR] Neither 'docker compose' nor 'docker-compose' found on system."
    exit 1
fi

HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
HOST_IP="${HOST_IP:-127.0.0.1}"

echo "=================================================="
echo " ✅ Marketing Browser is running!"
echo "    - 🖥️ 局域网直接访问 (HTTPS): https://${HOST_IP}:3001 (推荐)"
echo "    - 🖥️ 本机浏览器访问 (HTTP):  http://localhost:3000"
echo "    - 🤖 CDP 远程调试 (Agent):  http://127.0.0.1:9222 (由守护网桥自动代理)"
echo "    - 💾 会话存储目录:          ${BROWSER_DIR}/chrome-profile (持久化保存登录)"
echo "=================================================="
echo "⚠️  注意："
echo "如果是通过局域网 IP 跨设备访问，请务必使用 HTTPS 访问 3001 端口："
echo "👉 https://${HOST_IP}:3001"
echo "（浏览器提示证书风险时，点击'高级' ➔ '继续前往'即可）"
echo ""
echo "下一步操作："
echo "1. 在浏览器打开 https://${HOST_IP}:3001 (或 http://localhost:3000) 登录小红书/知乎/微信公众号。"
echo "2. 登录完成后运行 Cookie 提取工具："
echo "   python .agent/skills/growth-distribution/scripts/publish/sync_browser_cookies.py"
