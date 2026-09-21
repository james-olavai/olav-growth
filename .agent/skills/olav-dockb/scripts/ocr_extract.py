#!/usr/bin/env python3
"""OCR pre-processing for docs-kb: turn scanned PDFs / images into the .md
companion files the other scripts already index.

The four consumer scripts all `rglob("*.md")`, so a scanned PDF or a photo of
a page is invisible to them from the scan stage — not "misclassified", simply
never seen. This script is the missing front stage: it walks the same
`scan_dirs` from config.yaml, looks for `*.pdf`/`*.png`/`*.jpg`/`*.jpeg`/
`*.tiff`, and writes `<original name including extension>.md` next to each
source. Run it before `add_frontmatter.py`; the companion files then go
through the normal classification flow like any other .md.

The output filename keeps the original extension (`scan.pdf` -> `scan.pdf.md`)
so `scan.pdf`/`scan.docx` in the same folder can't collide on `scan.md`, and so
the companion's origin is unambiguous from its name alone.

Each output starts with a minimal YAML frontmatter block recording provenance
(`ocr_source: true`, `ocr_source_file: <path relative to ROOT>`); the rest is
the recognized text. Those two keys are not in add_frontmatter.py's managed
key list, so a later add_frontmatter.py run preserves them untouched.

Usage:
    python ocr_extract.py              # process every not-yet-done source file
    python ocr_extract.py --force      # re-OCR and overwrite existing companions
"""
import argparse
import os
import sys
from pathlib import Path

import pytesseract
import pypdfium2 as pdfium
import yaml
from PIL import Image

import add_frontmatter
import classify

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = classify.ROOT

PDF_SUFFIX = ".pdf"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tiff")
SOURCE_SUFFIXES = (PDF_SUFFIX,) + IMAGE_SUFFIXES

# PDF pages are rasterized at this scale before OCR: pypdfium2's default
# scale=1 renders at 72 DPI, which is too low for tesseract to read reliably.
PDF_RENDER_SCALE = 2
_RAPID_OCR_INSTANCE = None


def companion_path(source: Path) -> Path:
    """scan.pdf -> scan.pdf.md (keep the original extension, don't replace
    it — see the module docstring)."""
    return source.with_name(source.name + ".md")


def _ocr_pil_image(img: Image.Image) -> str:
    try:
        text = pytesseract.image_to_string(img)
        if text.strip():
            return text
    except Exception:
        pass

    try:
        from rapidocr_onnxruntime import RapidOCR
        global _RAPID_OCR_INSTANCE
        if _RAPID_OCR_INSTANCE is None:
            _RAPID_OCR_INSTANCE = RapidOCR()
        res, _ = _RAPID_OCR_INSTANCE(img)
        if res:
            return "\n".join([line[1] for line in res])
        return ""
    except Exception:
        # If rapidocr also fails, raise or return empty
        raise


def ocr_pdf(path: Path) -> str:
    pdf = pdfium.PdfDocument(str(path))
    try:
        pages = []
        for i in range(len(pdf)):
            bitmap = pdf[i].render(scale=PDF_RENDER_SCALE)
            pages.append(_ocr_pil_image(bitmap.to_pil()))
        return "\n\n".join(pages)
    finally:
        pdf.close()


def ocr_image(path: Path) -> str:
    with Image.open(path) as img:
        return _ocr_pil_image(img)


def render_output(rel_source: str, text: str) -> str:
    frontmatter = {"ocr_source": True, "ocr_source_file": rel_source}
    fm_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{fm_text}---\n\n{text}\n"


def find_sources(scan_dirs):
    sources = set()
    for name in scan_dirs:
        base = ROOT / name
        if not base.is_dir():
            continue
        for suffix in SOURCE_SUFFIXES:
            sources.update(base.rglob(f"*{suffix}"))
    return sorted(sources)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="re-OCR and overwrite existing companion files")
    args = parser.parse_args()

    if classify.ROOT_IS_DEFAULT:
        print(
            "Refusing to run: DOCS_KB_ROOT is unset, so ROOT defaults to this skill's "
            "own repository root. Running here would generate companion files for "
            "whatever images/PDFs already exist in the repo. Set DOCS_KB_ROOT to the "
            "real directory you want to index, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    config = classify.load_config()
    sources = find_sources(config["scan_dirs"])

    succeeded = 0
    skipped = 0
    failed = 0

    for source in sources:
        out_path = companion_path(source)
        rel_source = source.relative_to(ROOT).as_posix()
        if out_path.exists():
            if args.force:
                existing_fm, _ = add_frontmatter.split_existing_frontmatter(
                    out_path.read_text(encoding="utf-8", errors="replace")
                )
                if not existing_fm.get("ocr_source"):
                    failed += 1
                    print(
                        f"WARNING: refusing to overwrite {out_path.relative_to(ROOT).as_posix()} "
                        "(not an OCR-generated file)",
                        file=sys.stderr,
                    )
                    continue
            else:
                skipped += 1
                continue

        try:
            if source.suffix == PDF_SUFFIX:
                text = ocr_pdf(source)
            else:
                text = ocr_image(source)
            resolved = out_path.resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                raise ValueError(f"companion path escapes ROOT: {resolved}")
            tmp_path = out_path.with_name(out_path.name + f".tmp{os.getpid()}")
            try:
                tmp_path.write_text(render_output(rel_source, text), encoding="utf-8")
                tmp_path.replace(out_path)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
            succeeded += 1
            print(f"OK: {rel_source} -> {out_path.relative_to(ROOT).as_posix()}")
        except Exception as exc:
            failed += 1
            print(f"WARNING: OCR failed for {rel_source}: {exc}", file=sys.stderr)

    print(f"\nOCR summary: {succeeded} succeeded, {skipped} skipped (companion exists), {failed} failed")


if __name__ == "__main__":
    main()
