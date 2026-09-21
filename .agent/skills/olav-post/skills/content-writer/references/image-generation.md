# Image Generation (Mermaid & Gemini)

Convert Mermaid diagrams or Gemini artistic images into uploadable WebP image files (1200×630 px).

## When to Run

After writing `olav.md` (Step 3 of content-writer), before writing platform drafts.

### Option A: Mermaid Diagrams (Standard)
```bash
uv run python .agent/skills/content-writer/scripts/gen_blog_images.py <slug>
```

### Option B: Gemini Artistic Images (Fallback)
If you need a realistic cover or an artistic illustration that Mermaid cannot handle:

1. Use the `generate_image` tool with a descriptive prompt (e.g., "A futuristic server room with holographic data flows, sleek dark aesthetic, 16:9").
2. Save the resulting image to a temporary file.
3. Convert and process it into the slug folder:
```bash
uv run python .agent/skills/content-writer/scripts/process_gemini_image.py <slug> <local_image_path>
```

## What it Does

1. Reads `olav-post/archive/YYYY-MM-DD/olav.md` (the master post)
2. Extracts all ` ```mermaid ``` ` blocks in order
3. Renders each to PNG via `@mermaid-js/mermaid-cli` (1200×630 px, white background)
4. Converts PNG → WebP at 85% quality via `cwebp`
5. Outputs to **two locations**:
   - `olav-web/public/blog-images/<slug>/` — web-serving copy (for the live site)
   - `olav-post/archive/YYYY-MM-DD/images/` — archive copy (self-contained, for social-poster uploads)
6. Prints the `ogImage` frontmatter line and a file report for both locations

## Output Structure

```
olav-web/public/blog-images/<slug>/
  og-image.webp        ← og:image + platform cover (from 1st mmd or gemini)
  diagram-1.webp       ← same as og-image (named for platform inline use)
  diagram-2.webp       ← from 2nd mmd block
  ...
  artistic-1.webp      ← from Gemini image(s) processed via script
```

## After Running

1. Add `ogImage` to frontmatter of both `olav.md` **and** `olav-web/src/content/blog/<slug>.md`:
   ```yaml
   ogImage: /blog-images/<slug>/og-image.webp
   ```
2. Update `_meta.md` → Generated Images section:
   ```
   ## Generated Images
   Archive: olav-post/archive/YYYY-MM-DD/images/
   - og-image.webp
   - diagram-1.webp
   - diagram-2.webp  (if present)
   ```

## Platform Image Usage

| Platform    | Image Support | What to Use |
|---|---|---|
| LinkedIn    | ✅ optional   | `diagram-1.webp` |
| 微信公众号  | ✅ required   | `og-image.webp` as cover; inline diagrams for body |
| 掘金        | ✅ cover      | `og-image.webp` as article cover |
| 知乎        | ✅ optional   | `diagram-N.webp` inline in article body |
| Reddit      | ❌ text-only  | Link to blog post instead |
| HackerNews  | ❌ URL-only   | URL post only |

## Upload via Chrome MCP (for social-poster)

```python
mcp_chrome-devtoo_upload_file(
    uid="<file-input ref from snapshot>",
    filePath="/path/to/project/olav-web/public/blog-images/<slug>/diagram-1.webp"
)
```

## Requirements

- `uv` — runs the Python script in the virtual environment
- `npx` (Node.js) — `mermaid-cli` auto-installed on first run (~30s)
- `cwebp` — `sudo apt install webp` (already installed on this machine)
- `scripts/puppeteer-config.json` — headless Chrome config (in olav-web/)
