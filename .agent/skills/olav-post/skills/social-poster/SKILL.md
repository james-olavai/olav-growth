---
name: social-poster
description: "Deploy olav blog and post to social media platforms using browser automation. Use when content is ready in olav-post/archive/ and the user says 'post to social', 'social push', 'publish post', 'post update', '发帖', '推送更新', or 'push this to social'. Reads draft content from olav-post/archive/YYYY-MM-DD/. Requires content-writer to have been run first."
argument-hint: "Platform(s) to post to: all | linkedin | hackernews | reddit | zhihu | juejin | wechat-mp. Default: all."
---

# Social Poster Skill

Deploy the olav blog update and post platform drafts from `olav-post/archive/` via Chrome DevTools MCP.

## Scope

This skill **only deploys and posts**. It does NOT write content.
Content must be ready in `olav-post/archive/YYYY-MM-DD/` — run `content-writer` first if it isn't.

## Browser Tool

This skill uses **Chrome DevTools MCP** (`mcp_chrome-devtoo_*`).
The user must have Chrome running with remote debugging enabled:

```bash
# Linux/macOS
google-chrome --remote-debugging-port=9222 &

# Windows
start chrome --remote-debugging-port=9222
```

Fallback: if Chrome DevTools MCP is unavailable, use Playwright MCP (`mcp_playwright_browser_*`) — most interaction patterns are the same; substitute `mcp_playwright_browser_navigate` for `mcp_chrome-devtoo_navigate_page`, etc.

---

## Step-by-Step Procedure

### Step 0 — Load Archive

Find the most recent `olav-post/archive/YYYY-MM-DD/` directory:

```bash
ls -d /path/to/project/olav-post/archive/*/  | sort | tail -1
```

Read `_meta.md` from that directory. Extract:
- **Blog Slug** (e.g., `olav-v010-launch`)
- **Blog URL EN** (e.g., `https://olavai.com/blog/olav-v010-launch`)
- **Blog URL ZH** (e.g., `https://olavai.com/zh/blog/olav-v010-launch`)
- Which platform files exist (check which of `linkedin.md`, `hackernews.md`, `reddit.md`, `zhihu.md`, `juejin.md`, `wechat-mp.md` are present)

If `_meta.md` doesn't exist or the archive is empty, stop and ask user to run `content-writer` first.

### Step 1 — Deploy Blog

Read and follow: [blog-deploy.md](./references/blog-deploy.md)

Do NOT proceed to Step 2 until:
1. `npm run build && npm run worker:deploy` (or git push CI build & deploy) completes without error
2. Blog live URL is visually confirmed correct via browser MCP

If deploy fails, stop and report the error. Do not post to any platform with a broken blog URL.

### Step 2 — Post to Each Platform

For each platform with a draft file in the archive, follow the platform workflow in order:

| Priority | File | Platform / Community | Workflow |
|---|---|---|---|
| 1 | `hackernews.md` | HackerNews (Show HN) | [hackernews.md](./references/hackernews.md) |
| 2 | `netbox-community.md` | NetBox Community (Slack / Forum) | [netbox-community.md](./references/netbox-community.md) |
| 3 | `v2ex.md` | V2EX (/go/create) | [v2ex.md](./references/v2ex.md) |
| 4 | `linkedin.md` | LinkedIn | [linkedin.md](./references/linkedin.md) |
| 5 | `reddit.md` | Reddit (r/netbox, r/networkautomation) | [reddit.md](./references/reddit.md) |
| 6 | `zhihu.md` | 知乎 | [zhihu.md](./references/zhihu.md) |
| 7 | `juejin.md` | 掘金 | [juejin.md](./references/juejin.md) |
| 8 | `wechat-mp.md` | 微信公众号 | [wechat-mp.md](./references/wechat-mp.md) |

**Per platform:**
1. Read the platform draft from `olav-post/archive/YYYY-MM-DD/<platform>.md`
2. Follow the browser workflow in the reference file above
3. Take screenshot confirming draft/form state
4. Report to user before moving to next platform

**Compliance & Security Firewalls:**
- **Vendor Forums (Cisco / Juniper / Arista):** NEVER create automated standalone threads. Disallowed by community rules.
- **Reddit `r/networking` main feed:** NEVER automate single-topic posts. Only interact via weekly vendor threads manually.
- **Channel Isolation:** On Slack/Discourse, ONLY post to designated channels (`#show-and-tell`, `#integrations`, `#tooling`, `Community Projects`). Posting in `#general` is strictly forbidden.

**Critical rules:**
- **NEVER click "Upload", "Browse", or image icons** that open a system file picker. Chrome MCP cannot interact with system dialogs and the automation will hang.
- **Use `mcp_chrome-devtools_upload_file`** directly on the hidden `<input type="file">` element. Finding this element often requires inspecting the DOM for hidden inputs.
- **Advanced: Use Direct POST** via `mcp_chrome-devtools_evaluate_script` for platforms with complex upload flows. To get the base64 data, run:
  ```bash
  uv run python -c "import base64; print(f'data:image/webp;base64,{base64.b64encode(open(\"path/to/image.webp\", \"rb\").read()).decode()}')"
  ```
  Pass this string to `evaluate_script` and perform a `fetch(..., {method: 'POST'})` to the site's upload endpoint.
- **Publishing Policy:**
    - **Chinese Platforms (知乎, 掘金, 微信公众号, V2EX):** ABSOLUTELY NO automatic publishing. Drafts only. Administrator manual review required.
    - **Global Platforms & Slack Communities:** Can be published automatically if requested, or kept as drafts.
- If login is required, pause and ask user to log in manually, then resume
- If a platform fails, report the error and move to the next one — do not abort everything

### Step 3 — Update _meta.md

After all platforms are complete, update `olav-post/archive/YYYY-MM-DD/_meta.md`:

```markdown
## Posting Status
- [x] Blog deployed — YYYY-MM-DD HH:MM UTC
- [x] HackerNews — draft saved / form ready
- [x] LinkedIn — draft saved
- [x] Reddit — draft saved in r/X
- [x] 知乎 — draft saved
- [x] 掘金 — draft auto-saved
- [x] 微信公众号 — draft saved
```

### Step 4 — Summary Report

Output a final table:

```
Blog deployed:  https://olavai.com/blog/<slug>
Archive:        olav-post/archive/YYYY-MM-DD/

Platform / Community  Status     Notes
──────────────────────────────────────────────────────────
HackerNews            ✅ ready   Form filled (Show HN), awaiting submit
NetBox Community      ✅ draft   Slack #show-and-tell / Discourse ready
V2EX                  ✅ draft   草稿已准备 (/go/create)
LinkedIn              ✅ draft   Draft saved, awaiting manual publish
Reddit                ✅ draft   r/netbox / r/networkautomation draft
知乎                   ✅ draft   草稿已保存，请审查后手动发布
掘金                   ✅ draft   草稿自动保存，请审查后手动发布
微信公众号              ✅ draft   草稿已保存，请审查后手动群发
```

Include screenshots for any platforms where something was unexpected.

---

## If Only Specific Platforms Were Requested

If user specified specific platforms (e.g., "post to LinkedIn and HackerNews only"):
- Skip Step 1 (deploy blog) only if blog is already live — verify first
- Run only the requested platform workflows in Step 2
- Update `_meta.md` for the completed platforms only
