#!/usr/bin/env python3
"""Native Social Publishing CLI Script (Primary Tier 1/2 Distribution).

Directly publishes or schedules content via official REST APIs or Webhooks,
eliminating the fragility and maintenance burden of browser automation.

Supported Channels:
1. buffer      - Buffer REST API (multi-platform scheduling)
2. n8n         - n8n / Make workflow webhook trigger
3. telegram    - Telegram Bot Channel broadcast
4. slack       - Slack incoming webhook
5. discord     - Discord community webhook
6. webhook     - Generic custom JSON webhook
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def load_env_vars():
    """Load config from .env if present in workspace root or skill directory."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent.parent.parent / ".env",
    ]
    for p in candidates:
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v


def http_post_json(url: str, payload: dict, headers: dict = None) -> tuple[int, dict]:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            try:
                res_json = json.loads(body)
            except Exception:
                res_json = {"raw": body}
            return resp.status, res_json
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return e.code, {"error": err_body}
    except Exception as exc:
        return 500, {"error": str(exc)}


def publish_buffer(text: str, profile_ids: list[str], media_urls: list[str] = None, scheduled_at: str = None, dry_run: bool = False):
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if not token and not dry_run:
        return False, "Missing BUFFER_ACCESS_TOKEN in environment."

    if not profile_ids:
        env_profiles = os.environ.get("BUFFER_PROFILE_IDS")
        if env_profiles:
            profile_ids = [p.strip() for p in env_profiles.split(",") if p.strip()]

    if not profile_ids and dry_run:
        profile_ids = ["dry-run-channel-id"]

    if not profile_ids and not dry_run:
        try:
            q = "query { account { organizations { id } } }"
            req_org = urllib.request.Request(
                "https://api.buffer.com",
                data=json.dumps({"query": q}).encode("utf-8"),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_org, timeout=10) as r:
                od = json.loads(r.read().decode())
                org_id = od["data"]["account"]["organizations"][0]["id"]
                c_q = "query ($orgId: OrganizationId!) { channels(input: { organizationId: $orgId }) { id } }"
                req_ch = urllib.request.Request(
                    "https://api.buffer.com",
                    data=json.dumps({"query": c_q, "variables": {"orgId": org_id}}).encode("utf-8"),
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req_ch, timeout=10) as cr:
                    cd = json.loads(cr.read().decode())
                    profile_ids = [c["id"] for c in cd["data"]["channels"]]
        except Exception as e:
            return False, f"Failed to auto-detect Buffer channel: {e}"

    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            status
            dueAt
            text
          }
        }
        ... on InvalidInputError { message }
        ... on LimitReachedError { message }
        ... on UnauthorizedError { message }
        ... on UnexpectedError { message }
        ... on RestProxyError { message }
      }
    }
    """

    results = []
    for pid in profile_ids:
        mode = "customScheduled" if scheduled_at else "shareNow"
        variables = {
            "input": {
                "channelId": pid,
                "text": text,
                "mode": mode,
                "schedulingType": "automatic",
            }
        }
        if scheduled_at:
            variables["input"]["dueAt"] = scheduled_at

        if dry_run:
            print(f"[DRY-RUN Buffer GraphQL] POST https://api.buffer.com")
            print(f"Channel: {pid} | Mode: {mode}")
            print(f"Payload: {json.dumps(variables, indent=2, ensure_ascii=False)}")
            results.append({"status": "dry-run-success", "channelId": pid, "mode": mode})
            continue

        req = urllib.request.Request(
            "https://api.buffer.com",
            data=json.dumps({"query": mutation, "variables": variables}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "errors" in data:
                    results.append({"channelId": pid, "error": data["errors"]})
                else:
                    create_result = data.get("data", {}).get("createPost", {})
                    results.append({"channelId": pid, "result": create_result})
        except Exception as e:
            results.append({"channelId": pid, "error": str(e)})

    if dry_run:
        return True, results

    any_success = any("result" in r and "post" in r.get("result", {}) for r in results)
    return any_success, results


def publish_postiz(text: str, profile_ids: list[str], media_urls: list[str] = None, scheduled_at: str = None, dry_run: bool = False):
    """Publish/Schedule via open-source Postiz REST / Public API v1."""
    token = os.environ.get("POSTIZ_API_KEY")
    api_url = os.environ.get("POSTIZ_API_URL", "").rstrip("/")
    if not api_url:
        base_url = os.environ.get("POSTIZ_BASE_URL", "http://localhost:5000").rstrip("/")
        api_url = f"{base_url}/api/public/v1"

    if not token and not dry_run:
        return False, "Missing POSTIZ_API_KEY in environment."

    # Normalize api_url so that it always points to the posts endpoint
    if api_url.endswith("/posts"):
        url = api_url
    elif "/api/public/v1" in api_url:
        url = f"{api_url.split('/api/public/v1')[0]}/api/public/v1/posts"
    elif "/api/v1" in api_url:
        url = f"{api_url.split('/api/v1')[0]}/api/public/v1/posts"
    elif api_url.endswith("/api"):
        url = f"{api_url}/public/v1/posts"
    else:
        url = f"{api_url}/api/public/v1/posts"

    # Format for Postiz Public API v1
    posts_list = []
    target_ids = profile_ids or ["default"]
    for pid in target_ids:
        posts_list.append({
            "integration": {"id": pid},
            "value": [
                {
                    "content": text,
                    "image": [{"url": m} for m in (media_urls or [])]
                }
            ],
            "settings": {}
        })

    payload = {
        "type": "schedule" if scheduled_at else "draft",
        "posts": posts_list
    }
    if scheduled_at:
        payload["scheduledFor"] = scheduled_at

    if dry_run:
        print(f"[DRY-RUN Postiz] POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return True, {"status": "dry-run-success", "target": "postiz"}

    headers = {"Authorization": token}
    status, res = http_post_json(url, payload, headers=headers)
    return (status in (200, 201)), res



def publish_n8n(webhook_url: str, payload: dict, dry_run: bool = False):
    target_url = webhook_url or os.environ.get("N8N_WEBHOOK_URL")
    if not target_url and not dry_run:
        return False, "Missing N8N_WEBHOOK_URL."

    if dry_run:
        print(f"[DRY-RUN n8n] POST {target_url or 'https://your-n8n.com/webhook/marketing'}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return True, {"status": "dry-run-success", "target": "n8n"}

    status, res = http_post_json(target_url, payload)
    return (status == 200), res


def publish_telegram(text: str, dry_run: bool = False):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if (not token or not chat_id) and not dry_run:
        return False, "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID."

    url = f"https://api.telegram.org/bot{token or 'TOKEN'}/sendMessage"
    payload = {
        "chat_id": chat_id or "@example_channel",
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    if dry_run:
        print(f"[DRY-RUN Telegram] POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return True, {"status": "dry-run-success", "target": "telegram"}

    status, res = http_post_json(url, payload)
    return (status == 200), res


def publish_webhook(url: str, payload: dict, dry_run: bool = False):
    if not url and not dry_run:
        return False, "Missing webhook URL."

    if dry_run:
        print(f"[DRY-RUN Webhook] POST {url or 'https://webhook.site/test'}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return True, {"status": "dry-run-success", "target": "webhook"}

    status, res = http_post_json(url, payload)
    return (status in (200, 201, 204)), res


def main():
    load_env_vars()

    parser = argparse.ArgumentParser(description="Native Social Publishing API CLI")
    parser.add_argument("--test-connection", action="store_true", help="Run publishing system and API connectivity diagnostics")
    parser.add_argument("--channel", choices=["buffer", "postiz", "n8n", "telegram", "webhook", "slack", "discord"], help="Target publishing channel")
    parser.add_argument("--text", help="Post content text")
    parser.add_argument("--file", help="Path to markdown/text file containing draft")
    parser.add_argument("--title", help="Optional title/topic headline")
    parser.add_argument("--profiles", nargs="+", help="Profile / Integration IDs (for Buffer/Postiz)")
    parser.add_argument("--media", nargs="+", help="Public URLs to media/images")
    parser.add_argument("--schedule", help="ISO-8601 timestamp for scheduling (e.g. 2026-09-25T14:00:00Z)")
    parser.add_argument("--webhook-url", help="Override webhook URL")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without actually dispatching HTTP call")

    args = parser.parse_args()

    if args.test_connection:
        try:
            from test_connections import main as run_diag
            run_diag()
        except ImportError:
            import subprocess
            subprocess.run([sys.executable, str(Path(__file__).parent / "test_connections.py")])
        sys.exit(0)

    if not args.channel:
        print("[ERROR] Please specify --channel or run with --test-connection", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    content = args.text or ""
    if args.file:
        p = Path(args.file)
        if not p.is_file():
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        raw = p.read_text(encoding="utf-8")
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            content = parts[2].strip() if len(parts) >= 3 else raw.strip()
        else:
            content = raw

    if not content.strip():
        print("[ERROR] No content provided (use --text or --file).", file=sys.stderr)
        sys.exit(1)

    print(f"=== Dispatching via API: {args.channel.upper()} (Dry-run: {args.dry_run}) ===")

    success = False
    result = None

    if args.channel == "buffer":
        success, result = publish_buffer(content, args.profiles, args.media, args.schedule, args.dry_run)
    elif args.channel == "postiz":
        success, result = publish_postiz(content, args.profiles, args.media, args.schedule, args.dry_run)
    elif args.channel == "n8n":
        payload = {
            "title": args.title or "",
            "content": content,
            "media": args.media or [],
            "schedule": args.schedule or "now",
            "source": "growth-distribution-api"
        }
        success, result = publish_n8n(args.webhook_url, payload, args.dry_run)
    elif args.channel == "telegram":
        success, result = publish_telegram(content, args.dry_run)
    elif args.channel in ("webhook", "slack", "discord"):
        url = args.webhook_url or os.environ.get(f"{args.channel.upper()}_WEBHOOK_URL")
        payload = {"text": content, "title": args.title, "media": args.media}
        success, result = publish_webhook(url, payload, args.dry_run)

    if success:
        print(f"[SUCCESS] Dispatched successfully via {args.channel}!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    else:
        print(f"[FAILED] Error dispatching to {args.channel}: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
