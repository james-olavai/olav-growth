"""Shared classification logic for the docs-kb skill.

Reads config.yaml so nothing here is project-specific. Used by
add_frontmatter.py, search_docs.py, and check_taxonomy_drift.py.

Classification is two-stage, cheapest/most-certain first:
  1. Exact title match against the taxonomy folder tree (config.categories.source_folder)
     -> confidence "title-match" (equivalent to 1.0)
  2. Fallback keyword scoring against config.categories.signals
     -> confidence "high" / "medium", or ("Uncategorized", "none") if nothing matched
Files whose doc_type isn't in classifiable_doc_types are always
("Uncategorized", "not-applicable") — that's by design, not a gap.
"""
import os
import re
from pathlib import Path

import yaml

_root_override = os.environ.get("DOCS_KB_ROOT", "").strip()
ROOT = Path(_root_override).resolve() if _root_override else Path(__file__).resolve().parents[4]
ROOT_IS_DEFAULT = not _root_override
SKILL_DIR = Path(__file__).resolve().parents[1]

def resolve_config_path() -> Path:
    env_cfg = os.environ.get("DOCS_KB_CONFIG", "").strip()
    if env_cfg and Path(env_cfg).is_file():
        return Path(env_cfg).resolve()
    if (ROOT / "config.yaml").is_file():
        return (ROOT / "config.yaml").resolve()
    if (ROOT / "content" / "config.yaml").is_file():
        return (ROOT / "content" / "config.yaml").resolve()
    return (SKILL_DIR / "config.yaml").resolve()

CONFIG_PATH = resolve_config_path()


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def classify_doc_type(rel_path: Path, config: dict) -> str:
    if rel_path.name.startswith("_"):
        return "internal-tracking"
    rel_str = rel_path.as_posix()
    for prefix, doc_type in config["doc_type_rules"]:
        if prefix == "." or rel_str == prefix or rel_str.startswith(prefix + "/"):
            return doc_type
    return "other"


def get_matched_prefix(rel_path: Path, config: dict):
    """Return the doc_type_rules prefix this file matched (or None), used to
    look up materialize_tree eligibility. Ignores the "_" internal-tracking
    override so a file's underlying collection is still identifiable."""
    rel_str = rel_path.as_posix()
    for prefix, _doc_type in config["doc_type_rules"]:
        if prefix == "." or rel_str == prefix or rel_str.startswith(prefix + "/"):
            return prefix
    return None


def normalize_title(raw: str) -> str:
    t = raw.strip()
    t = re.sub(r"^[a-z]{2,5}\d?:\s*", "", t, flags=re.IGNORECASE)
    t = t.replace("&amp;", "&")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def clean_stem(stem: str) -> str:
    return re.sub(r"^\d+[a-z]?_\s*", "", stem)


def slugify(name: str) -> str:
    """Obsidian-safe tag/slug: lowercase, alnum + hyphens only (tags can't
    contain spaces or most punctuation)."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def extract_title(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def build_title_alias_map(config: dict) -> dict:
    """Map normalized title -> category, derived from the source_folder tree.

    A file sitting directly inside source_folder/<Category>/... maps to
    <Category>. A file sitting flat in source_folder (no subfolder) maps to
    its own title. Subfolder names are also registered so section-header
    chapters (whose title equals a category name) resolve.
    """
    mapping = {}
    source_folder = config["categories"]["source_folder"]
    if not source_folder:
        return mapping
    source = ROOT / source_folder
    if not source.is_dir():
        return mapping

    for path in source.rglob("*.md"):
        rel = path.relative_to(source)
        parts = rel.parts
        if len(parts) == 1 and path.stem.lower() == "readme":
            continue  # top-level taxonomy index, not a chapter category
        category = parts[0] if len(parts) > 1 else path.stem
        title = extract_title(path.read_text(encoding="utf-8", errors="replace")) or path.stem
        mapping[normalize_title(title)] = category
        mapping[normalize_title(path.stem)] = category

    for sub in source.iterdir():
        if sub.is_dir():
            mapping[normalize_title(sub.name)] = sub.name

    return mapping


def score_signals(body: str, config: dict):
    """Fallback keyword scoring. Returns (category, tier, detail) where tier
    is 'high' / 'medium' / 'none'. Only distinct-term presence counts, not
    frequency, so long documents don't win just by repetition."""
    signals = config["categories"].get("signals", {})
    if not signals:
        return "Uncategorized", "none", {}

    scores = {}
    for category, terms in signals.items():
        hits = [t for t in terms if re.search(re.escape(t), body, re.IGNORECASE)]
        if hits:
            scores[category] = hits

    if not scores:
        return "Uncategorized", "none", {}

    min_hits = config.get("confidence_thresholds", {}).get("min_hits", 1)
    scores = {cat: hits for cat, hits in scores.items() if len(hits) >= min_hits}
    if not scores:
        return "Uncategorized", "none", {}

    ranked = sorted(scores.items(), key=lambda kv: -len(kv[1]))
    best_cat, best_hits = ranked[0]
    best_ratio = len(best_hits) / len(signals[best_cat])
    runner_up_len = len(ranked[1][1]) if len(ranked) > 1 else 0
    margin = (len(best_hits) / runner_up_len) if runner_up_len else float("inf")

    th = config.get("confidence_thresholds", {})
    if best_ratio >= th.get("high_min_ratio", 0.4) and margin >= th.get("high_min_margin", 2.0):
        tier = "high"
    else:
        tier = "medium"
    return best_cat, tier, {"hits": best_hits, "ratio": round(best_ratio, 2), "margin": margin}


def classify(title: str, body: str, doc_type: str, config: dict, title_alias_map: dict, filename_title: str = None):
    """Returns (category, confidence) where confidence is one of:
    'not-applicable', 'title-match', 'high', 'medium', 'none'.

    Tries the document's H1 title first, then its filename-derived title
    (e.g. "13_Layer 3 Protocol Design.md" -> "Layer 3 Protocol Design") —
    some collections have a generic first heading like "Overview" that isn't
    the real chapter title, so the H1 alone is not reliable enough to trust
    over the filename convention."""
    if doc_type not in config["classifiable_doc_types"]:
        return "Uncategorized", "not-applicable"

    candidates = [title, filename_title]
    if filename_title:
        # some collections append a genre suffix the source taxonomy doesn't
        # use (e.g. "... Design" or "... Configuration Overview")
        stripped = re.sub(r"\s+(Design|Configuration Overview)$", "", filename_title, flags=re.IGNORECASE)
        if stripped != filename_title:
            candidates.append(stripped)

    for candidate in candidates:
        if not candidate:
            continue
        norm = normalize_title(candidate)
        if norm in title_alias_map:
            return title_alias_map[norm], "title-match"

    category, tier, _detail = score_signals(body, config)
    return category, tier
