#!/usr/bin/env python3
"""Multi-format ingestion for docs-kb: turn office documents and spreadsheets
into the .md / .csv companion files the other scripts already index.

This is the front stage for formats `ocr_extract.py` doesn't cover:
    .pdf / .docx / .pptx  -> markitdown text extraction -> "<name>.md"
    .xlsx                 -> openpyxl per-sheet export -> "<name>.<sheet>.csv"
                             plus a workbook index "<name>.md"
A `.pdf` that markitdown returns ~0 characters for (scanned / image-only) is
handed off to `ocr_extract.ocr_pdf()` instead — that script already does real
OCR, so this one never re-implements it. Standalone images are not this
script's job; run `ocr_extract.py` for those.

Dedup, report-only (never deletes or merges anything, matching
check_taxonomy_drift.py's philosophy):
  - Exact duplicates (identical sha256) are extracted once; every other path
    with the same hash gets a short stub companion pointing at the extracted
    one (`duplicate_of: <path>` frontmatter) instead of a second full copy —
    that keeps a later `add_frontmatter.py`/`search_docs.py` run from
    surfacing the same content twice.
  - Near-duplicates (different files, similar extracted text — e.g. the same
    document exported as both .docx and .pdf) are only reported, e.g. as
    "these two probably say the same thing" — dropping the "worse" copy is a
    judgment call (which format extracted more cleanly, which is newer)
    that this script won't make for you.

Run before `add_frontmatter.py`; the companion files then go through the
normal classification flow like any other .md.

Usage:
    python extract_docs.py              # process every not-yet-done source file
    python extract_docs.py --force      # re-extract and overwrite existing companions
"""
import argparse
import hashlib
import os
import re
import sys
from collections import Counter
from pathlib import Path

import openpyxl
import yaml
from markitdown import MarkItDown

import add_frontmatter
import classify
import ocr_extract

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = classify.ROOT

DOC_SUFFIXES = (".pdf", ".docx", ".pptx")
SHEET_SUFFIXES = (".xlsx",)
SOURCE_SUFFIXES = DOC_SUFFIXES + SHEET_SUFFIXES

# Below this many extracted characters, treat a .pdf as scanned/image-only
# and defer to ocr_extract's real OCR instead of trusting markitdown's (near
# empty) output.
MIN_EXTRACTED_CHARS = 20

# Near-duplicate report threshold: fraction of shared lines (see `jaccard`).
# Below this, two documents are treated as unrelated, not flagged.
NEAR_DUPLICATE_THRESHOLD = 0.85


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def companion_path(source: Path) -> Path:
    """report.docx -> report.docx.md (same convention as ocr_extract.py —
    keeps the original extension so same-stem files in a folder can't
    collide, and the companion's origin is unambiguous from its name)."""
    return source.with_name(source.name + ".md")


def sheet_csv_path(source: Path, sheet_name: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9 _.-]", "_", sheet_name).strip().replace(" ", "_")
    return source.with_name(f"{source.name}.{safe}.csv")


def sheet_csv_paths(source: Path, sheet_names):
    """One collision-free CSV path per sheet name, in the given order.

    `sheet_csv_path` sanitizes the sheet name ('Q1 2026' -> 'Q1_2026'), so two
    distinct sheets in one workbook can land on the same file — the later
    write then silently destroys the earlier sheet's export while the index
    .md still advertises both. Keep the plain sanitized name when it is unique
    (the common case: no behavior change), and disambiguate every sheet that
    shares one with a short digest of its *original* name. A digest rather
    than an occurrence counter so the filename stays stable if the sheets are
    reordered between runs (a counter would shift and leave a stale .csv
    behind); `reserved` also keeps a digest from ever colliding with another
    sheet's natural sanitized name."""
    base = [sheet_csv_path(source, name) for name in sheet_names]
    counts = Counter(base)
    reserved = set(base)
    used = set()
    paths = []
    for name, path in zip(sheet_names, base):
        if counts[path] > 1:
            attempt = 0
            while path in reserved or path in used:
                attempt += 1
                digest = hashlib.sha256(f"{name}\x00{attempt}".encode("utf-8")).hexdigest()[:8]
                path = path.with_name(path.name[: -len(".csv")] + f".{digest}.csv")
        used.add(path)
        paths.append(path)
    return paths


def find_sources(scan_dirs):
    sources = set()
    for name in scan_dirs:
        base = ROOT / name
        if not base.is_dir():
            continue
        for suffix in SOURCE_SUFFIXES:
            sources.update(base.rglob(f"*{suffix}"))
    return sorted(sources)


def render_output(rel_source: str, extracted_via: str, text: str, extra_frontmatter=None) -> str:
    frontmatter = {"extracted_source": True, "extracted_source_file": rel_source, "extracted_via": extracted_via}
    if extra_frontmatter:
        frontmatter.update(extra_frontmatter)
    fm_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{fm_text}---\n\n{text}\n"


def write_text_atomic(out_path: Path, content: str):
    resolved = out_path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError(f"output path escapes ROOT: {resolved}")
    tmp_path = out_path.with_name(out_path.name + f".tmp{os.getpid()}")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(out_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def extract_office_doc(path: Path) -> str:
    """PDF / DOCX / PPTX -> plain text via markitdown."""
    result = MarkItDown(enable_plugins=False).convert(str(path))
    return result.text_content or ""


def extract_xlsx(path: Path):
    """Returns (index_markdown, [(csv_path, rows)]) — caller writes the files
    so this function stays a pure transform, easy to test without touching disk."""
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = []
    for name in wb.sheetnames:
        ws = wb[name]
        rows, last_row, last_col = [], 0, 0
        for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            rows.append(row)
            for c_idx, v in enumerate(row, start=1):
                if v is not None and (not isinstance(v, str) or v.strip()):
                    last_row = r_idx
                    last_col = max(last_col, c_idx)
        if last_row == 0:
            continue  # truly empty sheet
        trimmed = [["" if v is None else v for v in row[:last_col]] for row in rows[:last_row]]
        sheets.append((name, trimmed))

    lines = [f"| Sheet | Rows | Cols |", "|---|---|---|"]
    for name, rows in sheets:
        cols = len(rows[0]) if rows else 0
        lines.append(f"| {name} | {len(rows)} | {cols} |")
    index_md = "\n".join(lines)
    return index_md, sheets


def rows_to_csv_text(rows) -> str:
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf)
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


def jaccard(a_lines: set, b_lines: set) -> float:
    if not a_lines or not b_lines:
        return 0.0
    return len(a_lines & b_lines) / len(a_lines | b_lines)


def significant_lines(text: str) -> set:
    return {line.strip() for line in text.splitlines() if len(line.strip()) >= 20}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="re-extract and overwrite existing companion files")
    parser.add_argument("--no-dedup-report", action="store_true", help="skip the near-duplicate report pass")
    args = parser.parse_args()

    if classify.ROOT_IS_DEFAULT:
        print(
            "Refusing to run: DOCS_KB_ROOT is unset, so ROOT defaults to this skill's "
            "own repository root. Running here would generate companion files for "
            "whatever documents already exist in the repo. Set DOCS_KB_ROOT to the "
            "real directory you want to index, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    config = classify.load_config()
    sources = find_sources(config["scan_dirs"])

    hashes = {}
    for source in sources:
        hashes.setdefault(sha256_of(source), []).append(source)

    succeeded = 0
    skipped = 0
    failed = 0
    duplicates_stubbed = 0
    extracted_texts = {}  # rel_source -> text, for the near-duplicate report

    for digest, paths in hashes.items():
        canonical, *dupes = sorted(paths)
        out_path = companion_path(canonical)
        rel_source = canonical.relative_to(ROOT).as_posix()

        if out_path.exists():
            if args.force:
                existing_fm, _ = add_frontmatter.split_existing_frontmatter(
                    out_path.read_text(encoding="utf-8", errors="replace")
                )
                if not existing_fm.get("extracted_source"):
                    failed += 1
                    print(
                        f"WARNING: refusing to overwrite {out_path.relative_to(ROOT).as_posix()} "
                        "(not an extraction-generated file)",
                        file=sys.stderr,
                    )
                    continue
            else:
                skipped += 1
                continue

        try:
            if canonical.suffix in SHEET_SUFFIXES:
                index_md, sheets = extract_xlsx(canonical)
                csv_paths = sheet_csv_paths(canonical, [name for name, _rows in sheets])
                for (_name, rows), csv_path in zip(sheets, csv_paths):
                    write_text_atomic(csv_path, rows_to_csv_text(rows))
                write_text_atomic(out_path, render_output(rel_source, "openpyxl", index_md))
                extracted_texts[rel_source] = index_md
            else:
                text = extract_office_doc(canonical)
                if canonical.suffix == ".pdf" and len(text.strip()) < MIN_EXTRACTED_CHARS:
                    text = ocr_extract.ocr_pdf(canonical)
                    via = "ocr_extract (scanned pdf)"
                else:
                    via = "markitdown"
                write_text_atomic(out_path, render_output(rel_source, via, text))
                extracted_texts[rel_source] = text
            succeeded += 1
            print(f"OK: {rel_source} -> {out_path.relative_to(ROOT).as_posix()}")
        except Exception as exc:
            failed += 1
            print(f"WARNING: extraction failed for {rel_source}: {exc}", file=sys.stderr)
            continue

        for dupe in dupes:
            dupe_out = companion_path(dupe)
            if dupe_out.exists():
                if args.force:
                    existing_fm, _ = add_frontmatter.split_existing_frontmatter(
                        dupe_out.read_text(encoding="utf-8", errors="replace")
                    )
                    if not existing_fm.get("extracted_source"):
                        failed += 1
                        print(
                            f"WARNING: refusing to overwrite {dupe_out.relative_to(ROOT).as_posix()} "
                            "(not an extraction-generated file)",
                            file=sys.stderr,
                        )
                        continue
                else:
                    continue
            dupe_rel = dupe.relative_to(ROOT).as_posix()
            stub = f"Identical content to [{rel_source}]({out_path.name}) (sha256 match) — not re-extracted.\n"
            write_text_atomic(dupe_out, render_output(dupe_rel, "sha256-duplicate", stub, {"duplicate_of": rel_source}))
            duplicates_stubbed += 1
            print(f"DUP: {dupe_rel} -> stub referencing {rel_source}")

    print(
        f"\nExtraction summary: {succeeded} succeeded, {skipped} skipped (companion exists), "
        f"{failed} failed, {duplicates_stubbed} exact duplicates stubbed"
    )

    if not args.no_dedup_report and len(extracted_texts) > 1:
        print("\nNear-duplicate report (different files, similar extracted text):")
        items = list(extracted_texts.items())
        line_sets = {rel: significant_lines(text) for rel, text in items}
        found_any = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                rel_a, _ = items[i]
                rel_b, _ = items[j]
                score = jaccard(line_sets[rel_a], line_sets[rel_b])
                if score >= NEAR_DUPLICATE_THRESHOLD:
                    found_any = True
                    print(f"  {score:.0%} similar: {rel_a}  <->  {rel_b}")
        if not found_any:
            print("  (none above threshold)")


if __name__ == "__main__":
    main()
