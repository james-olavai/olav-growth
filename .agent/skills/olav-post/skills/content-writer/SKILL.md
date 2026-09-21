---
name: content-writer
description: "Read git changes and produce all content assets for a release: update olav-web blog (EN+ZH), write the master olav.md post, generate mermaid diagram images, and write platform-native drafts for LinkedIn, HackerNews, Reddit, 知乎, 掘金, and 微信公众号. Use when the user says 'write post', 'write content', 'update blog', '写文章', '准备发布内容', or after making a code change they want to announce. Outputs go to olav-post/archive/YYYY-MM-DD/."
argument-hint: "Optional: target date (YYYY-MM-DD) or 'all platforms' / specific platforms to draft"
---

# Content Writer Skill

Read code changes → understand → write everything needed for a release announcement.
Output lands in `olav-post/archive/YYYY-MM-DD/` (gitignored, local-only).

## Scope

This skill **only writes content**. It does NOT deploy or post anything.
Hand off to the `social-poster` skill when content is ready.

---

## Execution Strategy: Progressive Disclosure (CRITICAL)

Do NOT execute all steps at once. You must follow a step-by-step interactive flow (渐进式披露) to prevent context overload and ensure high quality. 
**You MUST pause, report your progress, and ask the user for confirmation at the designated STOP points below.**

---

## Step-by-Step Procedure

### Phase 1: Context & Setup

**Do Step 1 and Step 2, then immediately proceed to Phase 2.**

### Step 1 — Understand the Update

```bash
git log --oneline -10
git diff HEAD~1 --stat
cat CHANGELOG.md | head -80
```

Extract:
- What feature/fix/change was made
- What behavior changed (before vs. after)
- Any performance numbers, config changes, or architecture changes
- Which version number this is

### Step 2 — Create Archive Directory

```python
# today's date
import datetime; print(datetime.date.today().isoformat())
```

Create: `olav-post/archive/YYYY-MM-DD/`

If that directory already exists, append `-2`, `-3`, etc.

Also create `_meta.md` immediately with the git summary:

```markdown
# Post Meta — YYYY-MM-DD

## Git Summary
<!-- paste git log --oneline -5 output -->

## What Changed
<!-- 2-3 sentences: the human-readable version of the diff -->

## Version
<!-- e.g., v0.10.1 -->

## Blog Slug
<!-- e.g., olav-v010-launch (existing) or new slug -->

## Blog URL (EN)
https://olavai.com/blog/<slug>

## Blog URL (ZH)
https://olavai.com/zh/blog/<slug>

## Generated Images
<!-- filled in after Step 5 -->

## Status
- [ ] olav.md written
- [ ] Blog EN updated
- [ ] Blog ZH updated
- [ ] Images generated
- [ ] linkedin.md written
- [ ] hackernews.md written
- [ ] reddit.md written
- [ ] netbox-community.md written
- [ ] ntc-slack.md written
- [ ] v2ex.md written
- [ ] zhihu.md written
- [ ] juejin.md written
- [ ] wechat-mp.md written
```

### Phase 2: Visual Assets Generation

**Do Step 3 and Step 4. Then 🛑 STOP and ask the user to review the generated diagrams and images BEFORE writing any full text.**

### Step 3 — Draft Skeleton `olav.md` (Mermaid Only)

Since the image generation script reads from `olav.md`, you must create a skeleton file first.
Write `olav-post/archive/YYYY-MM-DD/olav.md` containing **ONLY** the YAML frontmatter and the ```mermaid``` blocks (with brief placeholder text if needed).

```markdown
---
title: "..."
description: "..."
pubDate: YYYY-MM-DD
author: "OLAV Team"
tags: ["release", ...]
ogImage: /blog-images/<slug>/og-image.webp
---

[Intro placeholder]

```mermaid
...
```

[Body placeholder]
```

Rules:
- First Mermaid block = the architecture/flow diagram that will become `og-image.webp`
- At least one Mermaid diagram per post

### Step 4 — Generate Images

Read: [image-generation.md](./references/image-generation.md)

**Option A — Mermaid Diagrams (Baseline)**
Convert Mermaid blocks in the skeleton `olav.md` to WebP images:
```bash
uv run python .agent/skills/content-writer/scripts/gen_blog_images.py <slug>
```

**Option B — Gemini Artistic Images (Creative)**
Use the `generate_image` tool for covers or lifestyle shots that Mermaid can't handle.
Then process them using:
```bash
uv run python .agent/skills/content-writer/scripts/process_gemini_image.py <slug> <local_image_path>
```

After running:
- Update `_meta.md` → Generated Images section with file list

**🛑 STOP HERE AND ASK FOR USER REVIEW OF IMAGES.**

### Phase 3: Master Content Writing

**Do Step 5 and Step 6. Then 🛑 STOP and ask the user to review the master posts BEFORE proceeding to platform drafts.**

### Step 5 — Complete Master Post (`olav.md`)

Read: [blog-update.md](./references/blog-update.md)

Now expand the skeleton `olav.md` into the full canonical EN article.
Write the complete narrative around the existing mermaid blocks. Make sure `ogImage` is updated if needed.

### Step 6 — Update olav-web Blog Posts

Read: [blog-update.md](./references/blog-update.md) → sections 3 and 4.

Update (or create) both blog posts:
- `olav-web/src/content/blog/<slug>.md` — EN (can be copied from olav.md once written)
- `olav-web/src/content/blog-zh/<slug>.md` — ZH (independent translation, not copy)

**Do not deploy at this stage.** Deployment is handled by `social-poster`.

### Phase 4: Platform Drafts

**IMPORTANT**: Writing 6 lengthy drafts at once consumes massive context. Instruct the LLM to generate them progressively (e.g., english platforms first, then chinese platforms; or 2 at a time), and ask the user to review them iteratively.

### Step 7 — Write Platform Drafts

Read: [content-strategy.md](./references/content-strategy.md)
Read: [community-compliance.md](./references/community-compliance.md) for self-promotion rules, Open-Source Card requirements, and green-light channels.
Read: [platform-drafts.md](./references/platform-drafts.md) for structure of each file.

Generate one file per platform in `olav-post/archive/YYYY-MM-DD/`:

**Mandatory for Social Drafts**:
- **Open-Source Card**: Start with clear open-source maintainer status (no corporate/slick marketing tone).
- **Image Markers**: Every draft MUST include placeholders for images generated in Step 2.
- **Format**: `[IMAGE: ./images/filename.webp] (Note: Please upload this image at this position and DELETE this line.)`
- **Cover Image**: Add a marker for the `artistic-1.webp` cover at the beginning or appropriate context of the post.

| File | Platform / Community | Lang | Min length / Target |
|---|---|---|---|
| `linkedin.md` | LinkedIn | EN | 400 words |
| `hackernews.md` | HackerNews (Show HN) | EN | 80 words (short by design) |
| `reddit.md` | Reddit (r/netbox, r/networkautomation, r/selfhosted) | EN | 500 words |
| `netbox-community.md` | NetBox Community (Slack #show-and-tell / Discourse) | EN | 200 words |
| `ntc-slack.md` | Network to Code Slack (#tooling) | EN | 150 words |
| `v2ex.md` | V2EX (/go/create) | ZH | 800 汉字 |
| `zhihu.md` | 知乎 | ZH | 2000 汉字 |
| `juejin.md` | 掘金 | ZH | 1500 汉字 + 2 code blocks |
| `wechat-mp.md` | 微信公众号 | ZH | 2000 汉字 |

**Writing rules:**
- Only `olav.md` and `olav-web` blog posts support embedded Mermaid code blocks.
- **ALL platform drafts** (LinkedIn, Reddit, 知乎, etc.) MUST NOT contain raw Mermaid code. Use WebP placeholders instead.
- Each platform gets a **completely different angle** — not the same article in a different length
- No identical sentence across any two platforms
- Each article must be readable standalone — assume the reader has NOT seen the blog post
- Use `olav.md` as the source of facts, not as a template to shorten
- Images: use `https://olavai.com/blog-images/<slug>/diagram-N.webp` for inline image URLs (知乎, body text). Use local path for upload references in metadata.

**Per-article quality gate (mandatory before saving each file):**
1. Count the words/characters. If below minimum, expand — do not submit short articles.
2. Run the Self-Review Checklist from content-strategy.md.
3. Verify: does this article stand alone without the blog link? A reader who never sees olavai.com should still get full value.
4. Verify: does the opening sentence name something specific? If not, rewrite it.

### Phase 5: Finalization

### Step 8 — Update _meta.md

Tick all checkboxes in `_meta.md`. Fill in the Generated Images section.

### Step 8.5 — Refresh GEO Index (llms.txt)

Refresh the AI search engine index (`olav-web/public/llms.txt` and `llms-full.txt`):

```bash
uv run python .agent/skills/seo-geo-optimizer/scripts/generate_llms_txt.py
```

### Step 9 — Video Runsheet & Subtitle Alignment (Optional / Demo Pipeline)

If video production is requested or configured in campaign plan:
1. Generate `video-runsheet.md` in `olav-post/archive/YYYY-MM-DD/`.
2. Run timing alignment & subtitle generator:
   ```bash
   uv run python .agent/skills/content-writer/scripts/verify_and_align_runsheet.py \
     --runsheet olav-post/archive/YYYY-MM-DD/video-runsheet.md \
     --out-dir olav-post/archive/YYYY-MM-DD/video_assets/ \
     [--ssh user@demovm]
   ```

Outputs in `video_assets/`:
- `video-runsheet-aligned.md` (Runshet with `[00:00 - 00:12]` timing countdown markers)
- `subtitles.srt` (Millisecond-accurate SRT subtitles)

---

### Step 10 — Report to User

Output a summary table:

```
Content ready in: olav-post/archive/YYYY-MM-DD/

File                  Status   Notes
─────────────────────────────────────────────────────────────
_meta.md              ✅       Git summary + metadata
olav.md               ✅       Master EN post, mermaid inline
Blog EN               ✅       olav-web/src/content/blog/<slug>.md
Blog ZH               ✅       olav-web/src/content/blog-zh/<slug>.md
video-runsheet        ✅       video_assets/video-runsheet-aligned.md
subtitles.srt         ✅       video_assets/subtitles.srt
linkedin.md           ✅
hackernews.md         ✅
netbox-community.md   ✅
v2ex.md               ✅
```

Then ask: **"Content is ready. Run `social-poster` to deploy and post?"**

---

## Rules

1. Never deploy — writing only
2. Never post — browser automation is for `social-poster`
3. `olav.md` is the single source of truth for the blog post — platform files are derived from it, not from each other. Raw Mermaid code is permitted ONLY in `olav.md` and `olav-web` blog files.
4. Images MUST be generated and converted to WebP from Mermaid blocks in `olav.md` before writing platform files (LinkedIn, 知乎 use image links)
5. olav-post/archive/ is gitignored — never committed
