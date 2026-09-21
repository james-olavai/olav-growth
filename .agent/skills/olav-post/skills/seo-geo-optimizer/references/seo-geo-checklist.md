# SEO & GEO Audit Checklist

Checklist and guidelines for Traditional SEO and Generative Engine Optimization (GEO).

---

## 1. GEO (Generative Engine Optimization) Rules

AI Search Engines (Perplexity, ChatGPT Search, Claude, Google Gemini AI Overviews) extract information differently than traditional spiders. Follow these rules to maximize AI Citation rate:

### Rule 1: The `llms.txt` Standard
Place a clean, plain-text Markdown file at `/public/llms.txt` (served at `https://olavai.com/llms.txt`).
- Must begin with `# OLAV` and a one-sentence Entity definition.
- Must provide bulleted links to main documentation sections with concise descriptions.
- Avoid HTML formatting, Javascript, or complex styling in `llms.txt`.

### Rule 2: Explicit Entity Definition (实体定义)
Always define OLAV clearly in the first paragraph of any doc or blog post:
> *"OLAV (Online Analytical Vertex for Agentic Operations) is an open-source Python CLI for autonomous infrastructure and network operations."*

### Rule 3: Answer Snippets (问答切片)
Structure technical explanations as direct Q&A pairs with H2/H3 headings. AI Search engines love pulling these snippets verbatim into AI Overviews:
- **Heading**: `## How does OLAV differ from Model Context Protocol (MCP)?`
- **First sentence**: Direct 1-sentence answer (*"Unlike MCP which requires running a separate server process per service, OLAV uses a single-command API registration (`olav registry register`) with zero runtime overhead."*)

---

## 2. Traditional SEO Checklist

### Meta & Title Tags
- `title`: 50–60 characters. Must contain primary keyword (e.g. `OLAV | AI-Native Infrastructure & Network Operations`).
- `description`: 150–160 characters. Concise value proposition with CTA.
- `canonical`: Explicit `<link rel="canonical" href="...">` on all pages to prevent duplicate content issues.

### JSON-LD Structured Data
Ensure `olav-web/src/layouts/Layout.astro` includes:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "OLAV",
  "operatingSystem": "Linux, macOS, Windows",
  "applicationCategory": "DevOpsApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "description": "AI-native platform for autonomous infrastructure operations."
}
</script>
```
