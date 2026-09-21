# OLAV Marketing Skills

Five Claude Code skills that run OLAV's own content/marketing pipeline —
this is the tooling OLAV's team uses to market OLAV, published here as a
reusable package. They live day-to-day under a project's local Claude Code
skill directory (this repo's own working copy keeps them at `.agent/skills/`,
gitignored); this `skills/` package is the publishable, path-adjusted copy.

## Pipeline

```
marketing-analytics  →  marketing-strategist  →  content-writer  →  social-poster
  (fetch metrics)        (plan the campaign)      (write assets)     (deploy + post)

seo-geo-optimizer  (independent — run before a production olav-web build)
```

| Skill | Does | Reads | Writes |
|---|---|---|---|
| `marketing-analytics` | Fetch GitHub stars/forks/traffic + published-post engagement | GitHub API | `marketing-metrics.json` |
| `marketing-strategist` | Evaluate metrics, pick the next campaign angle | `marketing-metrics.json` | `campaign-plan.md` |
| `content-writer` | Turn a code change / campaign angle into a blog post + platform-native drafts (LinkedIn, HN, Reddit, 知乎, 掘金, 微信公众号) | git history, `campaign-plan.md` | `archive/YYYY-MM-DD/*` |
| `seo-geo-optimizer` | Audit/optimize for search engines and AI answer engines (Perplexity, ChatGPT, Gemini, Claude) | site content | `llms.txt`, `llms-full.txt` |
| `social-poster` | Deploy the blog and post the drafts via browser automation (Chrome DevTools MCP, Playwright MCP fallback) | `archive/YYYY-MM-DD/*` | live posts |

## Install into another project

```bash
cp -r skills/<name> /path/to/your/project/.agent/skills/<name>
```

Each `SKILL.md` is self-contained (front-matter `name`/`description`/
`argument-hint`, a `scripts/` subprocess, and `references/` for anything too
long to keep in the main body) — the same packaging convention as any other
Claude Code skill. **Paths inside them are OLAV-specific**
(`olav-post/archive/`, `olav-web/public/`, the `olav.md`/platform-draft
filenames) — adjust those for your own project's layout before use.

## Prerequisites

- `marketing-analytics` — a GitHub API token with read access to the target repo.
- `content-writer` — image-generation credentials for `gen_blog_images.py` / `process_gemini_image.py` (Gemini).
- `social-poster` — Chrome running with `--remote-debugging-port=9222` (Chrome DevTools MCP), or Playwright MCP as a fallback.
- `seo-geo-optimizer` — none beyond the site content itself.

## What is not in this package

`archive/`, `reports/`, `images/`, `marketing-metrics.json` and
`campaign-plan.md` are this repo's own **operational output** — the actual
drafts, metrics, and campaign history — and stay untracked in this repo's own
`.gitignore`. Only the skill packages themselves (`skills/**`) are published.
