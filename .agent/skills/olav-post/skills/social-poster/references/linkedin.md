# LinkedIn Post Workflow

## Content Guidelines

Read [content-strategy.md](../../content-writer/references/content-strategy.md) → LinkedIn section before writing.

**Voice**: Professional peer, first-person narrative, problem-first, no hype.

**Template structure**:
```
[Problem or moment of realization — 1-2 sentences]

[What changed / what was built — 1-2 sentences, concrete]

[Why it matters technically or organizationally — 1 sentence]

[One honest limitation or what's next — 1 sentence]

[Link to blog post or GitHub]
```

---

## Content Generation (run before browser workflow)

The draft is in `olav-post/archive/YYYY-MM-DD/linkedin.md` — written by `content-writer`.
Read it and verify it passes the checklist below before opening the browser.

### Self-review (mandatory gate)

Run the checklist before proceeding. If any item fails, rewrite:

```
[ ] No "excited/proud/thrilled/happy to share/game-changing/seamless/powerful/robust"
[ ] No bullet list of abstract benefits
[ ] No section headers (## The Problem, ## Key Benefits...)
[ ] Opening sentence is NOT a restatement of the blog title
[ ] Contains at least one concrete number or measurement
[ ] Contains at least one acknowledged limitation or trade-off
[ ] Each sentence teaches something specific — no filler
[ ] No two consecutive sentences start with the same word
[ ] Max 2 hashtags, placed at the very end only
```

---

## Browser Workflow (Chrome DevTools MCP)

### 1. Navigate to LinkedIn feed

```
mcp_chrome-devtoo_navigate_page → url: "https://www.linkedin.com/feed/"
mcp_chrome-devtoo_take_snapshot → verify login state
```

**Login check**: If page title is "LinkedIn: Log In or Sign Up", stop and ask user to log in manually.  
**Verified login indicator**: Page title "Feed | LinkedIn" + "Start a post" button present in snapshot.

### 2. Open post composer

```
mcp_chrome-devtoo_take_snapshot → find button "Start a post"
mcp_chrome-devtoo_click → ref to "Start a post" button
mcp_chrome-devtoo_wait_for → text: ["Add a photo", "Anyone"]
```

### 3. Upload diagram image (optional but recommended)

If blog images were generated (see [image-generation.md](../../content-writer/references/image-generation.md)), attach `diagram-1.webp` to increase reach. 

> [!IMPORTANT]
> **DO NOT** click the "Add a photo" or camera icon button. This will open a system file browser that Chrome MCP cannot control. 

**Workflow:**
1. `mcp_chrome-devtools_take_snapshot` (verbose: true) → search for `<input type="file">`. LinkedIn usually hides it or only creates it on focus.
2. `mcp_chrome-devtools_upload_file` (UID: `<input type="file"> ref`)
3. `mcp_chrome-devtools_wait_for` → text: ["Photo added", "1 image"]

**Pro-Tip (Direct POST Upload):** 如果找不到 input, 可使用 `mcp_chrome-devtools_evaluate_script` 注入：
```javascript
// This simulates selecting the file via the site's own handler
const input = document.querySelector('input[type="file"]');
const b64 = "base64_data_here"; // Read image file first
const blob = await (await fetch(b64)).blob();
const file = new File([blob], 'diagram-1.webp', { type: 'image/webp' });
const dt = new DataTransfer();
dt.items.add(file);
input.files = dt.files;
input.dispatchEvent(new Event('change', { bubbles: true }));
```
If image upload not found or fails, skip — text-only post is acceptable.

### 4. Enter post content

```
mcp_chrome-devtoo_take_snapshot → find the text area (contenteditable or textarea)
mcp_chrome-devtoo_click → ref to text area
mcp_chrome-devtoo_type_text → the prepared LinkedIn post text
```

### 5. Save as draft (do NOT publish)

LinkedIn does not have an explicit "Save Draft" button in the modal. 
**Workaround**: Click outside the modal or press Escape — LinkedIn auto-saves drafts.

```
mcp_chrome-devtoo_press_key → key: "Escape"
mcp_chrome-devtoo_take_screenshot → verify draft saved (look for "Your draft has been saved")
```

Alternatively: maximize the window, leave the composer open, and ask the user to review before publishing.

### 6. Visual confirmation + report to user

```
mcp_chrome-devtoo_take_screenshot → capture the current state of the composer
```

Report to user immediately (do not wait for all platforms):
- Screenshot of draft content
- Draft saved: Yes/No (LinkedIn auto-saves when Escape is pressed)
- Direct compose link: `https://www.linkedin.com/post/new/` (no stable draft URL)
- Remind user to open LinkedIn and publish manually after review

## Troubleshooting

| Issue | Fix |
|---|---|
| "Start a post" not found | Try scrolling to top of feed; re-snapshot |
| Composer doesn't open | LinkedIn may require clicking the text input directly in the feed |
| Text not appearing | Use `mcp_chrome-devtoo_fill` instead of `type_text` for contenteditable areas |
| Login wall | Stop, ask user to log in, then retry |

## Notes

- LinkedIn's DOM changes frequently — always re-snapshot after each interaction
- Do NOT click "Post" button under any circumstances
- Max post length: 3000 characters
