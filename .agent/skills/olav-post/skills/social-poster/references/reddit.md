# Reddit Post Workflow

## Content Guidelines

Read [content-strategy.md](../../content-writer/references/content-strategy.md) → Reddit section before writing.

**Voice**: Peer talking to peers. Honest about limitations. Invites discussion.

**Target subreddits** (pick the most relevant 1-2):
- r/selfhosted — for self-hosted/homelab deployments
- r/devops — for ops tooling and automation
- r/homelab — if hobbyist angle is strong
- r/networking — if network infra angle is primary
- r/Python — if the technical Python implementation is the focus
- r/MachineLearning or r/LocalLLaMA — if AI/LLM angle is primary

---

## Content Generation (run before browser workflow)

The draft is in `olav-post/archive/YYYY-MM-DD/reddit.md` — written by `content-writer`.
Read it and check the target subreddit selection in that file, then verify it passes the checklist.

### Self-review (mandatory gate)

```
[ ] Title contains no "excited/thrilled/amazing/powerful/game-changing"
[ ] Body does NOT start with "I'm excited/proud/happy to share"
[ ] Includes honest comparison to at least one alternative (or says there isn't one)
[ ] Includes at least one known limitation or alpha/beta caveat
[ ] Ends with a genuine question (not rhetorical)
[ ] No section headers (## The Problem, ## Solution...)
[ ] No bullet list of abstract benefits
[ ] License mentioned if BSL (Reddit users care about this)
[ ] Post is NOT a copy of any other platform's draft
```

---

## Browser Workflow (Chrome DevTools MCP)

### 1. Navigate to the target subreddit submit page

```
mcp_chrome-devtoo_navigate_page → url: "https://www.reddit.com/r/selfhosted/submit/?type=TEXT"
mcp_chrome-devtoo_take_snapshot → verify login state and subreddit rules banner
```

**Login check**: If redirected to `/login/`, stop and ask user to log in.  
**Verified login indicator**: Page title "Submit to r/selfhosted" + user avatar button present.  
Change `selfhosted` to the appropriate sub from the draft file.

### 2. Fill the title

```
mcp_chrome-devtoo_take_snapshot → find textbox "Title" (multiline required)
mcp_chrome-devtoo_click → title textbox ref
mcp_chrome-devtoo_type_text → prepared Reddit title
```

### 3. Fill the body (Switch to Markdown first)

New Reddit UI has a rich text editor. Switch to markdown mode for reliable MCP interaction:

```
mcp_chrome-devtoo_take_snapshot → find button "Switch to Markdown"
mcp_chrome-devtoo_click → "Switch to Markdown" button ref
mcp_chrome-devtoo_take_snapshot → find textbox "Post body text field" (now a plain textarea)
mcp_chrome-devtoo_click → body textarea ref
mcp_chrome-devtoo_type_text → prepared Reddit post body (markdown OK)
```

### 4. Save as draft

```
mcp_chrome-devtoo_take_snapshot → find button "Save Draft" (enabled only after title is filled)
mcp_chrome-devtoo_click → "Save Draft" button ref
mcp_chrome-devtoo_take_snapshot → confirm draft saved
```

**Do NOT click "Post" button.**

### 5. Visual confirmation + report to user

```
mcp_chrome-devtoo_take_screenshot → capture draft form with title and body visible
```

Report to user immediately:
- Screenshot of the draft (title, subreddit, body all visible)
- Draft saved: Yes/No
- Confirm: "Draft saved in r/X. Please review and submit manually."

## Troubleshooting

| Issue | Fix |
|---|---|
| "You need X karma to post here" | Skip this sub, try r/selfhosted or r/homelab |
| Rich text editor not working | Switch to markdown mode |
| Can't find draft button | Reddit redesign changes frequently; re-snapshot after scrolling |
| New Reddit vs Old Reddit | Navigate to `old.reddit.com/r/X/submit` for simpler DOM |
