#!/usr/bin/env python3
"""Synchronize authenticated cookies from persistent Chromium via Chrome DevTools Protocol (CDP)."""

import argparse
import base64
import json
import os
import re
import socket
import struct
import sys
import urllib.error
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
ENV_PATH = REPO_ROOT / ".env"


class MinimalCDPClient:
    """Zero-dependency WebSocket client for Chrome DevTools Protocol."""

    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        parts = ws_url.replace("ws://", "").split("/", 1)
        host_port = parts[0].split(":")
        self.host = host_port[0]
        self.port = int(host_port[1]) if len(host_port) > 1 else 80
        self.path = "/" + parts[1] if len(parts) > 1 else "/"
        self.sock = None
        self._msg_id = 1

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=5)
        key = base64.b64encode(os.urandom(16)).decode()
        handshake = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(handshake.encode())
        resp = self.sock.recv(4096).decode("utf-8", errors="ignore")
        if "101 Switching Protocols" not in resp:
            raise ConnectionError(f"WebSocket handshake failed: {resp[:100]}")

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def send_cmd(self, method: str, params: dict = None) -> dict:
        cur_id = self._msg_id
        self._msg_id += 1
        payload = {"id": cur_id, "method": method, "params": params or {}}
        raw_msg = json.dumps(payload).encode("utf-8")

        # Construct client-to-server masked frame
        mask = os.urandom(4)
        length = len(raw_msg)
        if length < 126:
            header = struct.pack("!BB", 0x81, 0x80 | length)
        elif length < 65536:
            header = struct.pack("!BBH", 0x81, 0x80 | 126, length)
        else:
            header = struct.pack("!BBQ", 0x81, 0x80 | 127, length)

        masked_body = bytes(b ^ mask[i % 4] for i, b in enumerate(raw_msg))
        self.sock.sendall(header + mask + masked_body)

        # Read response frame
        while True:
            head = self.sock.recv(2)
            if not head or len(head) < 2:
                raise ConnectionError("Connection lost while reading CDP response.")
            b1, b2 = struct.unpack("!BB", head)
            is_masked = bool(b2 & 0x80)
            pay_len = b2 & 0x7F
            if pay_len == 126:
                pay_len = struct.unpack("!H", self.sock.recv(2))[0]
            elif pay_len == 127:
                pay_len = struct.unpack("!Q", self.sock.recv(8))[0]

            server_mask = self.sock.recv(4) if is_masked else None
            data = bytearray()
            while len(data) < pay_len:
                chunk = self.sock.recv(pay_len - len(data))
                if not chunk:
                    break
                data.extend(chunk)

            if is_masked and server_mask:
                data = bytes(b ^ server_mask[i % 4] for i, b in enumerate(data))

            res = json.loads(data.decode("utf-8", errors="ignore"))
            if res.get("id") == cur_id:
                return res


def update_env_variable(key: str, value: str):
    """Write or update key=value in root .env file."""
    if not ENV_PATH.exists():
        ENV_PATH.write_text(f"{key}={value}\n", encoding="utf-8")
        return

    content = ENV_PATH.read_text(encoding="utf-8")
    pattern = rf"^{key}=.*$"
    if re.search(pattern, content, flags=re.MULTILINE):
        new_content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\n{key}={value}\n"
    ENV_PATH.write_text(new_content, encoding="utf-8")


def get_browser_info(host: str, port: int):
    url = f"http://{host}:{port}/json/version"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def get_open_tabs(host: str, port: int):
    url = f"http://{host}:{port}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return []


def sync_cookies(host: str, port: int, platforms: list[str]):
    info = get_browser_info(host, port)
    if not info:
        print(f"[ERROR] Cannot connect to Chromium at http://{host}:{port}")
        print("💡 请先启动浏览器容器：./deploy-browser.sh")
        return False

    ws_url = info.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[ERROR] No webSocketDebuggerUrl returned by browser.")
        return False

    print(f"[INFO] Connecting to CDP Browser Endpoint: {ws_url}")
    client = MinimalCDPClient(ws_url)
    try:
        client.connect()
    except Exception as e:
        print(f"[ERROR] Failed to connect WebSocket: {e}")
        return False

    target_domains = {
        "xhs": {
            "name": "小红书 (Xiaohongshu)",
            "urls": ["https://creator.xiaohongshu.com", "https://www.xiaohongshu.com"],
            "env_key": "XHS_COOKIE",
            "required_keys": ["a1", "web_session"]
        },
        "zhihu": {
            "name": "知乎 (Zhihu)",
            "urls": ["https://www.zhihu.com", "https://zhuanlan.zhihu.com"],
            "env_key": "ZHIHU_COOKIE",
            "required_keys": ["z_c0"]
        }
    }

    try:
        for pkey in platforms:
            cfg = target_domains.get(pkey)
            if not cfg:
                continue

            print(f"\n🔍 Querying cookies for {cfg['name']}...")
            res = client.send_cmd("Storage.getCookies", {})
            all_cookies = res.get("result", {}).get("cookies", [])
            
            matched = {}
            for c in all_cookies:
                domain = c.get("domain", "")
                if any(u.replace("https://", "").replace("http://", "").split("/")[0] in domain for u in cfg["urls"]):
                    matched[c["name"]] = c["value"]

            if not matched:
                print(f"⚠️  未找到 {cfg['name']} 的登录 Cookie。")
                print(f"👉 请访问 http://localhost:3000 打开浏览器，扫码登录后再试。")
                continue

            # Check key cookies
            found_keys = [k for k in cfg["required_keys"] if k in matched]
            print(f"✅ 成功捕获 {len(matched)} 项 Cookies (核心凭据: {', '.join(found_keys)})")

            cookie_str = "; ".join([f"{k}={v}" for k, v in matched.items()])
            update_env_variable(cfg["env_key"], f'"{cookie_str}"')
            print(f"💾 已同步更新至根目录 .env -> {cfg['env_key']}")
    finally:
        client.close()

    return True


def main():
    parser = argparse.ArgumentParser(description="Sync cookies from persistent Chromium via CDP")
    parser.add_argument("--host", default="127.0.0.1", help="CDP host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9222, help="CDP port (default: 9222)")
    parser.add_argument("--status", action="store_true", help="Display browser and tab status")
    parser.add_argument("--sync-xhs", action="store_true", help="Extract and sync Xiaohongshu cookies")
    parser.add_argument("--sync-zhihu", action="store_true", help="Extract and sync Zhihu cookies")
    parser.add_argument("--sync-all", action="store_true", help="Sync all supported platforms")

    args = parser.parse_args()

    if args.status or (not args.sync_xhs and not args.sync_zhihu and not args.sync_all):
        info = get_browser_info(args.host, args.port)
        if not info:
            print("==================================================")
            print(" ❌ Persistent Chromium is NOT RUNNING")
            print("==================================================")
            print("启动命令（在宿主机终端执行）：")
            print("  ./deploy-browser.sh")
            print("启动后访问 http://localhost:3000 进入 Web VNC 登录各平台。")
            return

        print("==================================================")
        print(" 🌐 Persistent Chromium Status (CONNECTED)")
        print("==================================================")
        print(f" Browser:   {info.get('Browser')}")
        print(f" Protocol:  {info.get('Protocol-Version')}")
        print(f" Web VNC:   http://localhost:3000")
        print(f" CDP URL:   http://{args.host}:{args.port}")

        tabs = get_open_tabs(args.host, args.port)
        print(f"\n📄 Active Tabs ({len(tabs)}):")
        for i, t in enumerate(tabs, 1):
            title = t.get("title", "Untitled")[:40]
            url = t.get("url", "")
            print(f" {i}. [{t.get('type')}] {title} -> {url}")
        print("==================================================")
        if not args.sync_xhs and not args.sync_zhihu and not args.sync_all:
            return

    platforms = []
    if args.sync_all:
        platforms = ["xhs", "zhihu"]
    else:
        if args.sync_xhs:
            platforms.append("xhs")
        if args.sync_zhihu:
            platforms.append("zhihu")

    if platforms:
        sync_cookies(args.host, args.port, platforms)


if __name__ == "__main__":
    main()
