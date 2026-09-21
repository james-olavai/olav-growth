# Blog Update Workflow

Update the olav-web blog posts to reflect the latest code changes.
This is called from `content-writer` Step 3 (olav.md) and Step 4 (blog files).

## Blog Location

```
olav-web/src/content/blog/          ← EN posts  →  https://olavai.com/blog/<slug>
olav-web/src/content/blog-zh/       ← ZH posts  →  https://olavai.com/zh/blog/<slug>
```

Frontmatter schema:
```yaml
---
title: "..."
description: "..."
pubDate: YYYY-MM-DD
author: "OLAV Team"
tags: ["release", "platform", "AI"]
ogImage: /blog-images/<slug>/og-image.webp   ← add after image generation
---
```

---

## 1. Understand What Changed

```bash
git log --oneline -10
git diff HEAD~1 --stat
cat CHANGELOG.md | head -80
```

Identify: feature/fix name, what behavior changed, any metrics.

---

## 2. Decide: Update Existing or Create New Post

- **Patch / minor change** → update existing post (append a new section)
- **New feature / release milestone** → create a new `.md` file with a new slug

Current active slug: `olav-v010-launch`

New slug convention: `olav-vX-Y-Z-<short-name>` (e.g. `olav-v011-schema-validation`)

---

## 3. Write / Update the EN Post

The `olav.md` in `olav-post/archive/YYYY-MM-DD/` IS the EN blog post.

After `olav.md` is finalized:
- Copy it verbatim to `olav-web/src/content/blog/<slug>.md`
  - OR if updating an existing post, append the new section to the existing file

Checklist:
- [ ] `pubDate` updated to today
- [ ] `ogImage` frontmatter filled (after image generation)
- [ ] At least one Mermaid diagram (first = og-image)
- [ ] New content appended under a `## What's New in vX.Y.Z` section
- [ ] Existing content untouched

**Mermaid block naming** (used by gen_blog_images.py):
- `diagram-1.webp` ← 1st mermaid block → also `og-image.webp`
- `diagram-2.webp` ← 2nd mermaid block
- etc.

---

## 4. Write / Update the ZH Post

Edit or create `olav-web/src/content/blog-zh/<slug>.md`.

This is a **translation**, not a copy. Adapt idioms and technical terms for Chinese technical readers.
Mermaid node labels should be in Chinese where possible.

**Do not copy-paste the EN post and machine-translate** — rewrite key metaphors in Chinese idiom.

---

## 5. Do NOT Deploy Here

Deployment is handled by `social-poster` via `blog-deploy.md`.

The files in `olav-web/src/content/` can be staged but not deployed yet.
