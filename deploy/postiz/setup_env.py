#!/usr/bin/env python3
"""Automated Postiz Setup & Cryptographic Key Generator."""

import argparse
import os
import re
import secrets
import shutil
import sys
from pathlib import Path

POSTIZ_DIR = Path(__file__).resolve().parent
REPO_ROOT = POSTIZ_DIR.parent.parent
POSTIZ_ENV = POSTIZ_DIR / ".env"
POSTIZ_EXAMPLE = POSTIZ_DIR / ".env.example"
ROOT_ENV = REPO_ROOT / ".env"


def generate_secure_keys():
    jwt_secret = secrets.token_hex(32)
    db_password = secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:16]
    return jwt_secret, db_password


def setup_postiz_env(host_ip="0.0.0.0", port=5000, force=False):
    if not POSTIZ_EXAMPLE.exists():
        print(f"[ERROR] Template not found: {POSTIZ_EXAMPLE}", file=sys.stderr)
        return False

    if POSTIZ_ENV.exists() and not force:
        print(f"[EXISTS] {POSTIZ_ENV} already configured. Use --force to regenerate keys.")
        return True

    jwt_secret, db_password = generate_secure_keys()
    tmpl = POSTIZ_EXAMPLE.read_text(encoding="utf-8")

    # Replace keys
    filled = re.sub(
        r'JWT_SECRET="[^"]*"',
        f'JWT_SECRET="{jwt_secret}"',
        tmpl
    )
    filled = re.sub(
        r'POSTGRES_PASSWORD="[^"]*"',
        f'POSTGRES_PASSWORD="{db_password}"',
        filled
    )
    filled = re.sub(
        r'postgresql://postiz:[^@]+@postiz-postgres:5432/postiz_db',
        f'postgresql://postiz:{db_password}@postiz-postgres:5432/postiz_db',
        filled
    )

    POSTIZ_ENV.write_text(filled, encoding="utf-8")
    print("==================================================")
    print(" 🚀 Postiz Environment Initialized Successfully!")
    print("==================================================")
    print(f" Target File:      {POSTIZ_ENV}")
    print(f" JWT_SECRET:       {jwt_secret[:12]}... (64-char secure random)")
    print(f" Database Pass:    {db_password[:6]}... (Auto-configured)")
    print(f" Port Binding:     {host_ip}:{port} (0.0.0.0 accessible)")
    print("==================================================")

    # Sync with root .env
    if ROOT_ENV.exists():
        root_content = ROOT_ENV.read_text(encoding="utf-8")
        if "POSTIZ_API_URL=" in root_content:
            new_root = re.sub(
                r'POSTIZ_API_URL=.*',
                f'POSTIZ_API_URL=http://localhost:{port}/api/public/v1',
                root_content
            )
            ROOT_ENV.write_text(new_root, encoding="utf-8")
            print(f"[ROOT SYNC] Updated POSTIZ_API_URL in {ROOT_ENV.name}")

    print("\n💡 接下来启动步骤：")
    print("1. 获取并配置 Cloudflare Tunnel（必须）：")
    print("   - 登录 Cloudflare Zero Trust (https://one.dash.cloudflare.com/) ➔ Networks ➔ Tunnels")
    print("   - 创建 Tunnel 并配置 Public Hostname 规则: HTTP -> postiz:5000")
    print(f"   - 在 {POSTIZ_ENV.name} 中填入 CLOUDFLARE_TUNNEL_TOKEN 与 MAIN_URL")
    print("\n2. 在宿主机终端启动容器集群：")
    print("   ./deploy-postiz.sh")
    print("\n3. 启动后浏览器访问你的域名：https://<你的公网域名>")
    print("   注册管理员账号 ➔ 前往 Settings ➔ API Tokens 复制 Key。")
    print("\n4. 运行连接诊断验证：")
    print("   python .agent/skills/growth-distribution/scripts/publish/publish_api.py --test-connection")
    return True


def main():
    parser = argparse.ArgumentParser(description="Automated Postiz Setup & Secret Generator")
    parser.add_argument("--force", action="store_true", help="Force regenerate secrets and overwrite .env")
    parser.add_argument("--port", type=int, default=5000, help="Host port (default: 5000)")
    parser.add_argument("--ip", default="0.0.0.0", help="Binding IP (default: 0.0.0.0)")

    args = parser.parse_args()
    setup_postiz_env(host_ip=args.ip, port=args.port, force=args.force)


if __name__ == "__main__":
    main()
