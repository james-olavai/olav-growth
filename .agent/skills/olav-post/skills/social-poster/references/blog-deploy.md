# Blog Deploy Workflow

Deploy the olav-web blog to Cloudflare Workers Static Assets and verify the live post.

---

## Prerequisites

1. Content ready in `olav-post/archive/YYYY-MM-DD/` (run `content-writer` first)
2. Blog posts written in:
   - `olav-web/src/content/blog/<slug>.md` (EN)
   - `olav-web/src/content/blog-zh/<slug>.md` (ZH)
3. Mermaid images generated in `olav-web/public/blog-images/<slug>/`

---

## Step 1 — Verify Blog Files Exist

```bash
# Get slug from _meta.md
SLUG=$(grep "Blog Slug" /path/to/project/olav-post/archive/YYYY-MM-DD/_meta.md | awk '{print $NF}')

ls /path/to/project/olav-web/src/content/blog/${SLUG}.md
ls /path/to/project/olav-web/src/content/blog-zh/${SLUG}.md
ls /path/to/project/olav-web/public/blog-images/${SLUG}/og-image.webp
```

If EN blog file is **missing**, copy from archive:

```bash
cp /path/to/project/olav-post/archive/YYYY-MM-DD/olav.md \
   /path/to/project/olav-web/src/content/blog/${SLUG}.md
```

If ZH blog file is missing, the ZH URL will 404. Continue with EN only — note this in the report.

If `og-image.webp` is missing, run image generation:

```bash
cd /path/to/project
uv run python .agent/skills/content-writer/scripts/gen_blog_images.py ${SLUG}
```

---

## Step 2 — Deploy via Git Push (Automated)

olav-web uses **GitHub Actions** for automated deployment. Push the new blog file to `main` and CI handles build + deploy:

```bash
cd /path/to/project/olav-web
git add src/content/blog/${SLUG}.md src/content/blog-zh/${SLUG}.md
git add public/blog-images/${SLUG}/
git commit -m "content: add blog post ${SLUG}"
git push origin main
```

GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
1. `npm ci`
2. `npm run build`
3. `npm run worker:deploy` (using `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` secrets)

**Monitor CI run:**
```
https://github.com/james-olavai/olav-web/actions
```

Wait for the workflow to show ✅ (typically 2–3 min) before verifying the live URL.

**If CI fails:**
- Check Actions log for TypeScript errors or missing frontmatter fields (`pubDate`, `description`, `ogImage`)
- Fix the blog file, commit and push again
- Secrets `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` must be set in repo Settings → Secrets

**Manual fallback** (if CI is broken or secrets not yet configured):
```bash
cd /path/to/project/olav-web
npm run build
CLOUDFLARE_API_TOKEN=<token> CLOUDFLARE_ACCOUNT_ID=<id> npm run worker:deploy
```

---

## Step 3 — Verify Live URL via Browser MCP

Wait ~30 seconds for propagation, then verify:

```
mcp_chrome-devtoo_navigate_page → url: "https://olavai.com/blog/<slug>"
mcp_chrome-devtoo_wait_for → text: ["<first few words of blog title>"]
mcp_chrome-devtoo_take_screenshot → capture the live blog post
```

**Verification checklist:**
- [ ] Blog post loads without 404
- [ ] Title is correct
- [ ] OG image renders in the hero area
- [ ] Mermaid diagrams are visible as images (not raw code)
- [ ] ZH version at `https://olavai.com/zh/blog/<slug>` loads (if ZH file exists)

If the page returns 404 or shows wrong content, wait 60s more and retry. If still failing, check the deployment output and stop — do not proceed to platform posting.

---

## Step 4 — Report Deployment

Report to user:
- Screenshot of live blog post
- EN URL: `https://olavai.com/blog/<slug>`
- ZH URL (if applicable): `https://olavai.com/zh/blog/<slug>`
- Deploy succeeded: Yes/No
- Visual check: Pass/Fail + notes

Only proceed to platform posting after deploy is confirmed live.
