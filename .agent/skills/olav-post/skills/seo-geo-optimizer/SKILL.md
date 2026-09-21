---
name: seo-geo-optimizer
description: "Audit and optimize olav-web for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO) for AI search engines like Perplexity, ChatGPT, Gemini, and Claude. Generates olav-web/public/llms.txt and llms-full.txt. Use when the user says 'optimize SEO', 'optimize GEO', 'SEO check', 'GEO optimization', '生成 llms.txt', or before building olav-web for production."
argument-hint: "Optional: --generate-llms | --check-meta | --full-audit"
---

# SEO & GEO Optimizer Skill

Audit and optimize `olav-web` for traditional Search Engine Optimization (SEO) and Generative Engine Optimization (GEO) targeting AI search engines (Perplexity, ChatGPT Search, Claude, Google Gemini AI Overviews).

---

## Scope

1. **GEO Optimization (AI Search Engine Indexing)**:
   - Generate and update standard `olav-web/public/llms.txt` and `olav-web/public/llms-full.txt`.
   - Audit Answer Snippets and Entity definitions for AI RAG/search crawlers.
2. **SEO Optimization (Traditional Web Search Indexing)**:
   - Audit `olav-web` HTML title tags, meta descriptions, Open Graph (OG) tags, Canonical URLs, and JSON-LD (`SoftwareApplication` / `TechArticle`).

---

## Step-by-Step Procedure

### Step 1 — Generate `llms.txt` and `llms-full.txt`

Run the GEO text index generator script:

```bash
uv run python .agent/skills/seo-geo-optimizer/scripts/generate_llms_txt.py
```

This script parses `README.md`, `CHANGELOG.md`, and core architecture docs to generate:
- `olav-web/public/llms.txt` (Structured Markdown index for LLMs & AI Search Engine bots)
- `olav-web/public/llms-full.txt` (Full technical documentation for AI RAG ingestion)

### Step 2 — Run SEO & GEO Audit

Read: [seo-geo-checklist.md](./references/seo-geo-checklist.md)

Audit `olav-web` static pages:
1. Verify `title` and `description` meta tags on all Markdown blog posts and pages.
2. Ensure `og:image` links to generated WebP images.
3. Verify JSON-LD `SoftwareApplication` schema is present in `olav-web/src/layouts/Layout.astro` (or main layout).
4. Verify Answer Snippets formatting on blog posts (e.g., explicit Q&A headers for AI extraction).

### Step 3 — Report to User

Output an audit summary table:

```
SEO & GEO Optimization Summary

Item                            Status    Notes
─────────────────────────────────────────────────────────────
llms.txt                        ✅ ready  olav-web/public/llms.txt
llms-full.txt                   ✅ ready  olav-web/public/llms-full.txt
JSON-LD Schema                  ✅ active SoftwareApplication
Meta Descriptions & Titles      ✅ passed
Open Graph Tags                 ✅ passed
```
