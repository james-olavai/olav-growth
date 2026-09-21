#!/usr/bin/env python3
"""Publishing System Connection & Health Check Diagnostic Utility."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
ENV_PATH = REPO_ROOT / ".env"


def load_env():
    """Load variables from root .env."""
    if ENV_PATH.is_file():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k not in os.environ:
                os.environ[k] = v


def is_placeholder(val: str) -> bool:
    if not val:
        return True
    lower = val.lower()
    return any(p in lower for p in [
        "your_", "here", "123456", "sk-proj-", "sk-ant-", "abcdef",
        "xxxxxx", "yourdomain.com", "example.com"
    ])


def test_postiz():
    url = os.environ.get("POSTIZ_API_URL", "").rstrip("/")
    key = os.environ.get("POSTIZ_API_KEY", "")

    if is_placeholder(url) or is_placeholder(key):
        return "NOT CONFIGURED", "Default placeholder in .env. Need POSTIZ_API_URL and POSTIZ_API_KEY."

    # Normalize Postiz integrations endpoint URL
    if url.endswith("/integrations"):
        test_url = url
    elif "/api/public/v1" in url:
        test_url = f"{url.split('/api/public/v1')[0]}/api/public/v1/integrations"
    elif "/api/v1" in url:
        test_url = f"{url.split('/api/v1')[0]}/api/public/v1/integrations"
    elif url.endswith("/api"):
        test_url = f"{url}/public/v1/integrations"
    else:
        test_url = f"{url}/api/public/v1/integrations"

    # Postiz Public API v1 accepts raw token in Authorization header
    headers = {"Authorization": key, "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(test_url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            count = len(data) if isinstance(data, list) else 0
            return "CONNECTED", f"Success. Found {count} connected channel integrations."
    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            # Retry with Bearer prefix in case reverse proxy or middleware expects Bearer
            try:
                req_b = urllib.request.Request(test_url, headers={"Authorization": f"Bearer {key}", "User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_b, timeout=5) as resp_b:
                    data = json.loads(resp_b.read().decode())
                    count = len(data) if isinstance(data, list) else 0
                    return "CONNECTED", f"Success. Found {count} connected channel integrations."
            except Exception:
                pass
            return "AUTH FAILED", f"Service reachable, but invalid API Key (HTTP {e.code})."
        return "ERROR", f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return "UNREACHABLE", f"Cannot reach {url}. Is the docker container running? ({e})"


def test_buffer():
    token = os.environ.get("BUFFER_ACCESS_TOKEN", "")
    if is_placeholder(token):
        return "NOT CONFIGURED", "Default placeholder in .env. Need BUFFER_ACCESS_TOKEN."

    # Buffer modern GraphQL API
    query = """
    query {
      account {
        id
        email
        name
        organizations {
          id
          name
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://api.buffer.com",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if "errors" in data and not data.get("data"):
                return "AUTH FAILED", f"GraphQL Error: {data['errors'][0].get('message')}"

            account = data.get("data", {}).get("account", {})
            email = account.get("email", "Unknown")
            orgs = account.get("organizations", [])
            channel_info = ""

            if orgs:
                org_id = orgs[0]["id"]
                c_query = """
                query GetChannels($orgId: OrganizationId!) {
                  channels(input: { organizationId: $orgId }) {
                    id
                    name
                    service
                    displayName
                  }
                }
                """
                c_req = urllib.request.Request(
                    "https://api.buffer.com",
                    data=json.dumps({"query": c_query, "variables": {"orgId": org_id}}).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    },
                    method="POST"
                )
                try:
                    with urllib.request.urlopen(c_req, timeout=8) as c_resp:
                        c_data = json.loads(c_resp.read().decode())
                        channels = c_data.get("data", {}).get("channels", [])
                        if channels:
                            ch_desc = ", ".join([f"[{c['service']}] {c.get('displayName') or c['name']} (ID: {c['id']})" for c in channels])
                            channel_info = f" | Channels: {ch_desc}"
                except Exception:
                    pass

            return "CONNECTED", f"Success. User: {email}{channel_info}"
    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            return "AUTH FAILED", f"Invalid BUFFER_ACCESS_TOKEN (HTTP {e.code})."
        return "ERROR", f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return "ERROR", str(e)


def test_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if is_placeholder(token):
        return "NOT CONFIGURED", "Default placeholder in .env. Need TELEGRAM_BOT_TOKEN."

    test_url = f"https://api.telegram.org/bot{token}/getMe"
    req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                bot_user = data.get("result", {}).get("username", "Unknown")
                chat_info = f" (Chat ID: {chat_id})" if not is_placeholder(chat_id) else " (Chat ID unconfigured)"
                return "CONNECTED", f"Success. Bot: @{bot_user}{chat_info}"
            return "FAILED", "Telegram API returned ok=false"
    except urllib.error.HTTPError as e:
        if e.code == 404 or e.code == 401:
            return "AUTH FAILED", "Invalid TELEGRAM_BOT_TOKEN."
        return "ERROR", f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return "NETWORK ERROR", f"Cannot connect to Telegram API ({e}). Check proxy if in mainland China."


def test_webhook(channel_name: str, env_var: str):
    url = os.environ.get(env_var, "")
    if is_placeholder(url):
        return "NOT CONFIGURED", f"Default placeholder in .env ({env_var})."

    # Just validate URL structure without firing spam alerts
    if url.startswith("http://") or url.startswith("https://"):
        return "CONFIGURED", f"Valid webhook URL format: {url[:30]}..."
    return "INVALID URL", f"Invalid URL string in {env_var}"


def test_browser_cdp():
    cdp_url = os.environ.get("CHROME_CDP_URL", "http://localhost:9222").rstrip("/")
    vnc_url = os.environ.get("CHROME_VNC_URL", "http://localhost:3000")
    try:
        req = urllib.request.Request(f"{cdp_url}/json/version", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            browser = data.get("Browser", "Chromium")

            req_tabs = urllib.request.Request(f"{cdp_url}/json", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_tabs, timeout=3) as t_resp:
                tabs = json.loads(t_resp.read().decode())
                tab_count = len(tabs)
            return "CONNECTED", f"{browser} (Web VNC: {vnc_url} | Open Tabs: {tab_count})"
    except Exception:
        return "NOT RUNNING", f"Browser container offline. Start via: ./deploy-browser.sh (Web VNC: {vnc_url})"


def main():
    load_env()
    print("==================================================================")
    print(" 📡 Marketing OS: Publishing System & API Connectivity Diagnostic")
    print("==================================================================")
    print(f" Checking Environment File: {ENV_PATH}")
    print("------------------------------------------------------------------")

    tests = [
        ("Buffer GraphQL API", test_buffer),
        ("Postiz Gateway (Self-Hosted)", test_postiz),
        ("Telegram Bot (Mobile Gatekeeper)", test_telegram),
        ("Persistent Browser (CDP & VNC)", test_browser_cdp),
        ("Slack Webhook", lambda: test_webhook("Slack", "SLACK_WEBHOOK_URL")),
        ("Discord Webhook", lambda: test_webhook("Discord", "DISCORD_WEBHOOK_URL")),
        ("n8n Workflow Webhook", lambda: test_webhook("n8n", "N8N_WEBHOOK_URL")),
    ]

    results = []
    for name, fn in tests:
        status, detail = fn()
        results.append((name, status, detail))

    print(f"{'Platform / Service':<32} | {'Status':<15} | {'Details'}")
    print("-" * 80)
    for name, status, detail in results:
        icon = "✅" if status in ["CONNECTED", "CONFIGURED"] else ("⚠️" if status == "NOT CONFIGURED" else "❌")
        print(f"{icon} {name:<30} | {status:<15} | {detail}")
    print("=" * 80)

    # Next step guidance
    print("\n💡 诊断建议与操作指南：")
    unconf = [r[0] for r in results if r[1] == "NOT CONFIGURED"]
    if unconf:
        print(f"1. 当前以下服务尚未在 .env 中配置真实 API 密钥：")
        for u in unconf:
            print(f"   - {u}")
        print(f"   👉 打开 `.env` 填入真实 Key 即可激活。")

    print("\n2. 自建 Postiz 集群启动命令（在宿主机终端执行）：")
    print("   cd deploy/postiz && docker compose up -d")
    print("   启动后访问 http://localhost:5000 创建账号并生成 API Key。")


if __name__ == "__main__":
    main()
