# HackerNews Post Workflow

## Content Guidelines

Read [content-strategy.md](../../content-writer/references/content-strategy.md) → HackerNews section before writing.

**Voice**: Dry, technical, zero hype. The HN community downvotes obvious marketing instantly.

**Title rules**:
- Use "Show HN:" prefix for project announcements
- Format: `Show HN: <Name> – <One plain-English sentence>`
- No exclamation marks, no adjectives like "powerful" or "amazing"
- Include the primary language/technology in parens if relevant: `(Python, BSL)`

**Body (text field)**:
- 2–4 sentences max
- State: what technical problem it solves, one interesting implementation detail, one limitation or gotcha
- Link to GitHub or blog post is fine but don't lead with it

---

## Content Generation (run before browser workflow)

The draft is in `olav-post/archive/YYYY-MM-DD/hackernews.md` — written by `content-writer`.
Read it and verify it passes the checklist below before opening the browser.

### Self-review (mandatory gate)

```
[ ] Title has no exclamation mark, no "excited/amazing/powerful/revolutionary"
[ ] Title follows "Show HN: Name – Description (stack)" format
[ ] Title is under 80 characters
[ ] Body is 2–4 sentences max
[ ] Body names the actual mechanism (not "uses AI to...")
[ ] Body includes one concrete limitation or gotcha
[ ] No marketing phrases anywhere
[ ] No emoji
```

---

## Browser Workflow (Chrome DevTools MCP)

### 1. Navigate to HN submit page

```
mcp_chrome-devtoo_navigate_page → url: "https://news.ycombinator.com/submit"
mcp_chrome-devtoo_take_snapshot → verify login state
```

**Login check**: If snapshot body contains "You have to be logged in to submit.", stop and ask user to log in.  
**Verified login indicator**: Page shows form with title/url/text fields directly (no redirect).

### 2. Fill title field

```
mcp_chrome-devtoo_take_snapshot → find first textbox (title field, focusable focused)
mcp_chrome-devtoo_click → title input ref
mcp_chrome-devtoo_type_text → the prepared HN title
```

### 3. Fill URL field (if submitting a link)

```
mcp_chrome-devtoo_take_snapshot → find second textbox (url field)
mcp_chrome-devtoo_click → url input ref
mcp_chrome-devtoo_type_text → "https://olavai.com/blog/..." or GitHub URL
```

### 4. Fill text field (if "text" post, no URL)

```
mcp_chrome-devtoo_take_snapshot → find multiline textbox (text field)
mcp_chrome-devtoo_click → text area ref
mcp_chrome-devtoo_type_text → the 2-4 sentence body
```

Note: HackerNews does not allow both URL and text in the same post — choose one.
For "Show HN" with a project: use URL field for the GitHub/site link, put context in the **text** field (HN allows text alongside URL for Show HN submissions).

### 5. STOP — Visual confirmation + report to user

HackerNews has **no draft feature**. Do not click the "submit" button.

```
mcp_chrome-devtoo_take_screenshot → capture the filled form for user review
```

Report to user immediately:
- Screenshot of the filled form (title, URL, text fields visible)
- Confirm: "Form is filled and ready. Please review the screenshot and click Submit manually."
- Remind: best submission time is 8am–12pm US Eastern, Monday–Thursday

## Timing Notes

- Best time to post on HN: 8am–12pm US Eastern (Monday–Thursday)
- Avoid Fridays and weekends for Show HN submissions
- Don't post the same URL twice — HN flags duplicate submissions

## Troubleshooting

| Issue | Fix |
|---|---|
| Redirected to login | Stop, ask user to log in manually |
| "You've already submitted this URL" | Use a different URL (blog post vs GitHub) or rephrase as text post |
| Text not appearing in field | Try `mcp_chrome-devtoo_fill` instead of `type_text` |
