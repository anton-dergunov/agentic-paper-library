#!/usr/bin/env python3
"""Shared helpers for the library scripts: paths, frontmatter, arXiv metadata.

Also usable from the shell scripts:

    paperlib.py frontmatter-arxiv <meta.xml> <arxiv-id> <source>
    paperlib.py frontmatter-manual <title> <source> [<url>]

Each prints a complete YAML frontmatter block (with the --- fences) to stdout.
"""

import datetime
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_DIR = Path(os.environ.get("LIBRARY_DIR", REPO_ROOT / "library"))
PDF_ROOT = Path(
    os.environ.get("PDF_ROOT", Path.home() / "Yandex.Disk.localized" / "Papers")
)

# Field order in every paper's frontmatter. `summary` is written by whoever
# files the paper (the add-paper skill), so the add scripts leave it empty.
FIELDS = ["title", "authors", "published", "arxiv", "url", "source", "summary", "added"]
REQUIRED = ["title", "source", "summary", "added"]
SOURCES = {"html", "pdf-text"}

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def paper_files(root=None):
    """Every paper markdown file under the library, excluding the indexes."""
    root = Path(root or LIBRARY_DIR)
    return sorted(p for p in root.rglob("*.md") if p.name != "README.md")


def pdf_path_for(md_path):
    """The PDF that mirrors a library markdown file."""
    rel = Path(md_path).resolve().relative_to(LIBRARY_DIR.resolve())
    return PDF_ROOT / rel.with_suffix(".pdf")


def read_paper(path):
    """Return (frontmatter dict, body) for a paper file; ({}, text) if none."""
    text = Path(path).read_text(encoding="utf-8")
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def render_frontmatter(meta):
    """Block-style YAML in FIELDS order, with lists (authors) kept on one line."""
    keys = [k for k in FIELDS if k in meta] + [k for k in meta if k not in FIELDS]
    opts = {"allow_unicode": True, "width": 10_000, "sort_keys": False}
    lines = []
    for k in keys:
        v = meta[k]
        if isinstance(v, list):
            flow = yaml.safe_dump(v, default_flow_style=True, **opts).strip()
            lines.append(f"{k}: {flow}\n")
        else:
            lines.append(yaml.safe_dump({k: v}, default_flow_style=False, **opts))
    return "---\n" + "".join(lines) + "---\n"


def write_paper(path, meta, body):
    Path(path).write_text(render_frontmatter(meta) + body, encoding="utf-8")


def parse_arxiv_entries(xml_text):
    """Map bare arXiv id -> metadata dict from an export-API Atom response."""
    root = ET.fromstring(xml_text)
    out = {}
    for entry in root.findall("a:entry", ATOM):
        raw_id = entry.findtext("a:id", default="", namespaces=ATOM)
        m = re.search(r"(\d{4}\.\d{4,5})", raw_id)
        if not m:
            continue
        title = " ".join((entry.findtext("a:title", "", ATOM)).split())
        authors = [
            " ".join(a.findtext("a:name", "", ATOM).split())
            for a in entry.findall("a:author", ATOM)
        ]
        published = entry.findtext("a:published", "", ATOM)[:10]
        out[m.group(1)] = {
            "title": title,
            "authors": authors,
            "published": datetime.date.fromisoformat(published) if published else None,
        }
    return out


def arxiv_meta(arxiv_id, entry, source):
    return {
        "title": entry["title"],
        "authors": entry["authors"],
        "published": entry["published"],
        "arxiv": arxiv_id,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "source": source,
        "summary": "",
        "added": datetime.date.today(),
    }


def _main(argv):
    if len(argv) >= 5 and argv[1] == "frontmatter-arxiv":
        xml_path, arxiv_id, source = argv[2], argv[3], argv[4]
        entries = parse_arxiv_entries(Path(xml_path).read_text(encoding="utf-8"))
        if arxiv_id not in entries:
            sys.exit(f"error: arXiv:{arxiv_id} not in API response")
        sys.stdout.write(render_frontmatter(arxiv_meta(arxiv_id, entries[arxiv_id], source)))
    elif len(argv) >= 4 and argv[1] == "frontmatter-manual":
        title, source = argv[2], argv[3]
        meta = {"title": title}
        if len(argv) > 4 and argv[4]:
            meta["url"] = argv[4]
        meta.update({"source": source, "summary": "", "added": datetime.date.today()})
        sys.stdout.write(render_frontmatter(meta))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    _main(sys.argv)
