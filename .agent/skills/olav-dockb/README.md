# docs-kb

A Claude Code skill that turns a folder of mixed documents into a searchable, classified markdown corpus an LLM agent can query directly — without hardcoding a single project's folder layout or file formats into the code.

This matters specifically because of how an LLM agent works with a large local corpus: it can't read binary PDFs/Office files directly, it has a limited context window, and it can't tell on its own that two differently-named files say the same thing. This skill addresses all three: everything lands as markdown the agent can actually parse; classification + full-text search return the handful of relevant documents instead of requiring the whole corpus to be read into context; and dedup means the agent is never handed the same fact twice under two filenames and led to treat it as independent corroboration (or a contradiction). Net effect: fewer tokens spent per query, and less surface area for hallucination traceable to duplicate or unindexed source material.

Everything project-specific lives in one human-negotiated `config.yaml`; the scripts stay generic and can be pointed at any document store via `DOCS_KB_ROOT`.

## What it does

- **Ingest mixed file types** — PDF, DOCX, PPTX, XLSX, and scanned PDFs/images — into markdown (plus per-sheet CSV for spreadsheets), so an agent never has to parse binary formats itself.
- **Dedup on the way in**: exact (sha256) duplicates are stubbed instead of indexed twice; near-duplicates (e.g. the same document as both `.docx` and `.pdf`) are flagged in a report rather than silently left for an agent to trip over as two "different" sources of the same fact.
- **Search** the resulting corpus by metadata (category, doc type, status, source page id) or full text, with synonym expansion for free-text queries — an agent gets back the handful of relevant hits instead of reading the whole corpus into context.
- **Classify and file** new documents against a taxonomy that a human has already negotiated — never guesses vocabulary ahead of evidence.
- **Keep frontmatter in sync** after new content is pulled in, idempotently.
- **Detect drift** between where a file physically lives and what the content classifier says it should be, report-only.

The frontmatter schema is Obsidian-compatible out of the box: nested tags and path-qualified `[[wikilinks]]` work in Obsidian's Properties panel, tag pane, graph view, and the Dataview plugin with zero extra setup.

## Core concepts

Every document is described along two independent axes: `doc_type` (what kind of document it is, e.g. a reference doc vs. internal tracking) and `category` (which taxonomy chapter it belongs to). `category_confidence` records *how* that category was assigned — an exact title match, a keyword-signal score, or nothing (`none`/`not-applicable`) — so low-confidence filing is always visible rather than silently treated as certain. `status` tracks the document's own lifecycle (e.g. `draft`) independently of both. See [`SKILL.md`](SKILL.md) for the full schema and the two-stage classification algorithm behind it.

## Files

| File | Purpose |
|---|---|
| `config.yaml` | Scan dirs, doc-type path rules, category taxonomy source + fallback signal keywords, which collections allow physical file moves, confidence thresholds |
| `synonyms.yaml` | Search-time query expansion groups |
| `scripts/classify.py` | Shared classification logic, imported by the other scripts |
| `scripts/add_frontmatter.py` | Writes frontmatter; idempotent |
| `scripts/search_docs.py` | Metadata + full-text search |
| `scripts/check_taxonomy_drift.py` | Report-only: flags files whose folder disagrees with the content classifier |
| `scripts/init_config.py` | Detects a starting `config.yaml` draft for a new project |
| `scripts/ocr_extract.py` | OCR for scanned PDFs/images (pytesseract + pypdfium2) |
| `scripts/extract_docs.py` | Ingests `.pdf`/`.docx`/`.pptx` (markitdown) and `.xlsx` (openpyxl); hands image-only PDFs to `ocr_extract`; report-only dedup |
| `query_misses.jsonl` / `classification_misses.jsonl` | Append-only logs used to grow `synonyms.yaml` / `config.yaml` from real gaps, not guesses |

See [`SKILL.md`](SKILL.md) for full usage, the frontmatter schema, the classification algorithm, and the init checklist for onboarding a new project.

## Install

```bash
pip install pyyaml pillow pytesseract pypdfium2 openpyxl 'markitdown[pdf,docx,pptx]'
cp -r . ~/.claude/skills/docs-kb   # or into <project>/.claude/skills/docs-kb
```

`pytesseract` also requires the Tesseract OCR binary to be installed separately on the host.

## Quick start

```bash
# Point the engine at a real document store (defaults to this repo's own root otherwise)
export DOCS_KB_ROOT=/path/to/your/docs

# If the corpus isn't markdown yet, ingest it first
python scripts/extract_docs.py          # pdf/docx/pptx/xlsx -> .md/.csv
python scripts/ocr_extract.py           # scanned pdfs + standalone images -> .md

# Dry run first
python scripts/add_frontmatter.py

# Then apply
python scripts/add_frontmatter.py --apply

# Search
python scripts/search_docs.py "example query"
python scripts/search_docs.py --list-categories

# Check for drift between folder placement and classification
python scripts/check_taxonomy_drift.py
```

For a brand-new project, run `scripts/init_config.py` first — it detects an existing "labeled" folder structure and prints a draft `config.yaml` rather than writing one for you. See `SKILL.md`'s "Init checklist" before adapting `config.yaml` to a different project.
