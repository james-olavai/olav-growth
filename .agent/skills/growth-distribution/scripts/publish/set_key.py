#!/usr/bin/env python3
"""Convenient CLI helper to update API keys in .env and verify connection immediately."""

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = SKILL_DIR.parent.parent
ENV_PATH = REPO_ROOT / ".env"


def update_env_key(key_name: str, key_value: str):
    if not ENV_PATH.exists():
        print(f"[ERROR] .env file not found at {ENV_PATH}", file=sys.stderr)
        return False

    content = ENV_PATH.read_text(encoding="utf-8")
    pattern = rf'^{re.escape(key_name)}=.*$'
    new_line = f'{key_name}={key_value}'

    if re.search(pattern, content, re.MULTILINE):
        updated = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    else:
        updated = content.rstrip() + f"\n{new_line}\n"

    ENV_PATH.write_text(updated, encoding="utf-8")
    print(f"[UPDATED] {key_name} saved into {ENV_PATH.name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Save API keys to .env and verify")
    parser.add_argument("--postiz-key", help="Postiz API Key")
    parser.add_argument("--buffer-token", help="Buffer Access Token")
    parser.add_argument("--telegram-token", help="Telegram Bot Token")
    parser.add_argument("--telegram-chat", help="Telegram Chat ID")
    parser.add_argument("--slack-url", help="Slack Webhook URL")
    parser.add_argument("--discord-url", help="Discord Webhook URL")
    parser.add_argument("--verify", action="store_true", default=True, help="Run test-connection immediately")

    args = parser.parse_args()
    modified = False

    if args.postiz_key:
        update_env_key("POSTIZ_API_KEY", args.postiz_key)
        modified = True
    if args.buffer_token:
        update_env_key("BUFFER_ACCESS_TOKEN", args.buffer_token)
        modified = True
    if args.telegram_token:
        update_env_key("TELEGRAM_BOT_TOKEN", args.telegram_token)
        modified = True
    if args.telegram_chat:
        update_env_key("TELEGRAM_CHAT_ID", args.telegram_chat)
        modified = True
    if args.slack_url:
        update_env_key("SLACK_WEBHOOK_URL", args.slack_url)
        modified = True
    if args.discord_url:
        update_env_key("DISCORD_WEBHOOK_URL", args.discord_url)
        modified = True

    if not modified:
        parser.print_help()
        sys.exit(1)

    if args.verify:
        print("\n[VERIFYING] Running connection diagnostic...")
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "test_connections.py")])


if __name__ == "__main__":
    main()
