---
name: docs-kb
description: Turn a folder of mixed documents (PDF, DOCX, PPTX, XLSX, scanned PDFs/images) into a searchable, classified markdown corpus, then search it by metadata (category, doc type, status, source page id) and full text, keep frontmatter in sync after new content lands, and classify/file new documents against a human-negotiated taxonomy. Use when asked to ingest/extract mixed documents, find/cross-check/list documents or decisions, sync frontmatter after new content has been pulled, or set this up in a new project.
---

# Docs KB: config-driven frontmatter + search + classification

Everything here is driven by [`config.yaml`](config.yaml) — no project-specific
paths are hardcoded in the scripts. `config.yaml` is a **human-negotiated
convention**, not something to regenerate blindly; see "Init checklist" below
before ever running this skill on a different project.

## Files

- `config.yaml` — scan dirs, doc_type path rules, the category taxonomy
  source folder + fallback signal keywords, which collections allow physical
  file moves (`materialize_tree`), confidence thresholds.
- `synonyms.yaml` — search-time query expansion groups (separate concern from
  classification — this is about finding documents, not filing them).
- `scripts/classify.py` — shared classification logic, imported by the rest.
- `scripts/add_frontmatter.py` — writes frontmatter; idempotent.
- `scripts/search_docs.py` — metadata + full-text search.
- `scripts/check_taxonomy_drift.py` — report-only: flags files whose
  physical folder disagrees with what the content classifier says.
- `scripts/init_config.py` — detection half of onboarding a new project (see
  below).
- `scripts/ocr_extract.py` — OCR pre-processing for scanned PDFs/images
  (pytesseract + pypdfium2, not docling); writes `<original name>.md`
  companions with `ocr_source`/`ocr_source_file` provenance fields. Refuses to
  run when `DOCS_KB_ROOT` is unset (writing without an explicit root would
  scan/write across whatever ROOT defaults to). Run before
  `add_frontmatter.py`.
- `scripts/extract_docs.py` — office-document ingestion: `.pdf`/`.docx`/`.pptx`
  via markitdown, `.xlsx` via openpyxl (per-sheet CSV + a workbook index
  `.md`). A `.pdf` markitdown can't get text out of is handed off to
  `ocr_extract.ocr_pdf()` instead of re-implementing OCR. Also does
  report-only dedup: exact (sha256) duplicates get a stub companion pointing
  at the one real extraction instead of a second copy; near-duplicates
  (different files, similar extracted text) are printed as a report, never
  auto-merged. Same `DOCS_KB_ROOT` gate as `ocr_extract.py`. Run before
  `add_frontmatter.py`.
- `query_misses.jsonl` / `classification_misses.jsonl` — append-only logs of
  low-hit searches / low-confidence classifications. Grow `synonyms.yaml` and
  `config.yaml`'s `signals` from these, not from guessing ahead of evidence.

### `DOCS_KB_ROOT`

All paths in `config.yaml` are resolved against `ROOT`. When `DOCS_KB_ROOT`
is unset (the default), `ROOT` is this skill's own repository root — handy
for checking/searching this repo during development. When you point the
skill at a real document store / workspace, set
`DOCS_KB_ROOT=<absolute path to that directory>`; the whole engine
(classification, frontmatter, search, drift check) then scans that
directory instead, with no script changes.

## Frontmatter schema

```yaml
---
title: "Example Document Title"
tags: [category/example-category, doc-type/example]
doc_type: example
category: example-category
category_confidence: title-match   # title-match | high | medium | none | not-applicable
source_url: https://example.invalid/pages/12345
page_id: 12345
version: 2
status: draft
related_page_ids: [12346, 12347]
related: ["[[examples/example-category/Example Document Title]]"]
---
```

`tags` and `related` exist for **Obsidian compatibility** — this folder already works as an Obsidian vault with zero setup (frontmatter shows up in its Properties panel, and the whole schema is queryable via the Dataview plugin as-is). `tags` mirrors `category`/`doc_type` in Obsidian's nested-tag format (`category/...`, `doc-type/...`) so its tag pane / graph view can filter without running any script. `related` mirrors `related_page_ids` as `[[wikilinks]]`, but **path-qualified**
(`[[examples/example-category/Example Document Title]]`, not bare `[[Example Document Title]]`) — a corpus
can reuse the same document title/filename across several collections, so a
bare wikilink would be ambiguous; Obsidian resolves a path-qualified link
correctly even when other files share its basename. A `related_page_ids`
entry with no matching local file (e.g. a source page never pulled) is simply
omitted from `related`, not linked.

`category_confidence`:
- `not-applicable` — this doc_type isn't in `classifiable_doc_types` (some
  collections have no chapter taxonomy to belong to; "Uncategorized" here is
  by design).
- `title-match` — the document's H1 (or filename, for collections whose H1
  is often a generic "Overview" rather than the real chapter title) exactly
  matched a category in the taxonomy tree. Equivalent to full confidence.
- `high` / `medium` — fallback keyword scoring (`config.categories.signals`)
  found a category when no exact title match existed. `high` requires a
  strong, clearly-ahead score (see `confidence_thresholds`); `medium` is a
  weaker signal — never auto-filed, always logged for review.
- `none` — nothing matched; stays "Uncategorized" and gets logged.

## Classifying (used by both add_frontmatter.py and check_taxonomy_drift.py)

Two-stage, cheapest/most-certain first (`classify.classify()`):
1. **Exact title match** against `config.categories.source_folder`'s folder
   tree (each subfolder name is a category; a flat file there
   self-categorizes under its own title) — scanned dynamically every run, so
   new chapters added to that folder are picked up automatically, nothing to
   maintain by hand.
2. **Signal scoring** (only when title match misses): distinct-term presence
   count against `config.categories.signals`, normalized and compared to a
   runner-up margin (`confidence_thresholds`). A lone incidental keyword
   mention in a broad/multi-topic document is not enough (`min_hits`) — this
   is what keeps a broadly-scoped document that only mentions a category's
   vocabulary in passing from getting force-filed into that category.

## Ingesting non-markdown documents

If the corpus isn't markdown yet — a folder that mixes PDFs, Word/PowerPoint/
Excel files, and scanned PDFs/images — run the extraction scripts first, then
the rest of the pipeline sees ordinary `.md` files like any other collection:

```bash
python .claude/skills/docs-kb/scripts/extract_docs.py       # pdf/docx/pptx/xlsx -> .md/.csv
python .claude/skills/docs-kb/scripts/ocr_extract.py         # scanned pdfs + standalone images -> .md
```

`extract_docs.py` uses markitdown for `.pdf`/`.docx`/`.pptx` and openpyxl for
`.xlsx` (per-sheet CSV plus a workbook-index `.md`); a `.pdf` it can't get
real text out of is handed off to `ocr_extract.py`'s OCR instead of guessing.
Both scripts share the same `DOCS_KB_ROOT` gate, write `<original name
including extension>.md` companions (so `report.docx` and `report.pdf` in the
same folder can't collide on `report.md`), and are safe to re-run — existing
companions are left alone unless `--force`.

Dedup is report-only, on purpose: `extract_docs.py` stubs out exact (sha256)
duplicates automatically (so the same content is never indexed twice), but
only *reports* near-duplicates — e.g. the same document exported as both
`.docx` and `.pdf` — because deciding which copy to keep needs a human
judgment call this skill won't make for you.

## Re-running after new content

```bash
python .claude/skills/docs-kb/scripts/add_frontmatter.py                 # dry run, prints a summary
python .claude/skills/docs-kb/scripts/add_frontmatter.py --apply         # writes frontmatter
python .claude/skills/docs-kb/scripts/add_frontmatter.py --apply --only some/subtree
```

`--apply` is refused (exit 1) unless `DOCS_KB_ROOT` is explicitly set to the real
directory being indexed — otherwise `ROOT` defaults to this skill's own repo root
and `--apply` would rewrite this project's own files. Dry runs are always allowed.

### `--materialize` (physically filing new documents)

```bash
python .claude/skills/docs-kb/scripts/add_frontmatter.py --apply --materialize
```

Off by default. When on, moves a file into `source_folder/<category>/` **only
if**: confidence is `title-match`/`high`, the file's collection is marked
`materialize_tree: true`, AND the file is not already located anywhere under
`source_folder` (however deeply nested). That last guard is load-bearing —
without it, an existing nested sub-hierarchy would be flattened into a
single level and two same-named files from different folders (e.g. several
`README.md`) could collide into one path. Always dry-run first
(`--materialize` without `--apply` prints `WOULD MOVE` lines) and read the
output before adding `--apply`.

## Drift checking

```bash
python .claude/skills/docs-kb/scripts/check_taxonomy_drift.py
```

For files already inside `source_folder`, compares the category their
physical folder implies against what the content classifier says,
independently. Only flags a disagreement when the content classifier is
confident (`title-match`/`high`) — a weak signal score never overrides
physical placement, since an established folder tree is itself a strong
signal. Report-only, never writes.

## Searching

```bash
python .claude/skills/docs-kb/scripts/search_docs.py "example query"
python .claude/skills/docs-kb/scripts/search_docs.py "term" --category "example-category"
python .claude/skills/docs-kb/scripts/search_docs.py --doc-type example --status draft
python .claude/skills/docs-kb/scripts/search_docs.py --related-to 12345
python .claude/skills/docs-kb/scripts/search_docs.py --list-categories
```

Query is a regex over the document body (frontmatter excluded), case-insensitive.
If it exactly matches a term in `synonyms.yaml`, it's expanded to an OR of
every term in that group first (`--no-expand` to disable). Queries returning
`<= 1` hits are appended to `query_misses.jsonl` unless `--no-log`.

## Init checklist (setting this up in a new/different project)

`config.yaml` should never be silently regenerated — it's the output of a
conversation, not a script. The steps:

1. Run `python scripts/init_config.py` (no `--apply`, it never writes
   `config.yaml` itself — it only detects and prints a draft). It looks for
   a folder whose immediate subfolders each already contain their own `.md`
   files (a "labeled" subtree) and, if found, sets that as
   `categories.source_folder` — such a subtree is found automatically.
   `doc_type_rules` get a first pass from folder-name keyword conventions
   (archive/template/reference/quer*/comment/tool/script) with a generic
   slug fallback otherwise.
2. If no labeled subtree was found, there's no cheap bootstrap — ask the
   user directly: what's this corpus about, is there an existing folder
   convention to preserve, where do new documents normally land, which
   folders are deliberately non-taxonomic (meeting notes, archives,
   templates)?
3. Leave `categories.signals` empty at first. Don't guess vocabulary ahead of
   evidence — let `classification_misses.jsonl` accumulate real gaps, then
   add signal terms (or new `synonyms.yaml` groups) from what actually shows
   up unclassified.
4. Ask explicitly before setting any `materialize_tree` entry to `true` —
   moving files is the one irreversible-ish action in this whole skill.
   Default everything to `false`.
5. Save the reviewed draft as `config.yaml`, then run `add_frontmatter.py`
   (dry run first) and sanity-check the doc_type/category counts before
   `--apply`.
