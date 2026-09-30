#!/usr/bin/env python3
"""Shared helpers for the library scripts: paths, frontmatter, arXiv metadata,
downloads and figures.

Also usable from the shell scripts:

    paperlib.py frontmatter-arxiv <meta.xml> <arxiv-id> <source>
    paperlib.py frontmatter-manual <title> <source> [<url>]
    paperlib.py set-summary <paper.md> <summary>

The first two print a complete YAML frontmatter block (with the --- fences) to
stdout; set-summary rewrites the paper's `summary:` field in place.
"""

import datetime
import io
import os
import re
import sys
import time
import urllib.error
import urllib.request
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
        version = re.search(r"v(\d+)$", raw_id.strip())
        out[m.group(1)] = {
            "title": title,
            "authors": authors,
            "published": datetime.date.fromisoformat(published) if published else None,
            "version": int(version.group(1)) if version else None,
            "abstract": " ".join(entry.findtext("a:summary", "", ATOM).split()),
        }
    return out


def fetch(url, attempts=4):
    """GET a URL and return its body as bytes, or None on 404 or repeated failure.

    arXiv answers throttled requests with errors or an empty body, so both are
    retried with backoff.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "papers-library/1.0"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as r:
                data = r.read()
            if data:
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except (urllib.error.URLError, TimeoutError):
            pass
        if attempt < attempts - 1:
            time.sleep(5 * (attempt + 1))
    return None


def library_arxiv_ids():
    """Map arXiv id -> paper file, for every paper in the library that has one."""
    out = {}
    for md in paper_files():
        arxiv_id = read_paper(md)[0].get("arxiv")
        if arxiv_id:
            out[str(arxiv_id)] = md
    return out


# Raster figures are stored as WebP no larger than this on the long side: that
# is still sharp on a laptop screen, and a fifth of the size of arXiv's PNGs.
FIGURE_MAX_SIDE = 1600
FIGURE_QUALITY = 85

# A raster figure on arXiv's HTML rendering, as pandoc writes it: a markdown
# image or an <img>, with the link either relative to the rendering
# ("2501.13956v1/x1.png") or already absolute.
ARXIV_FIGURE = re.compile(
    r"(!\[[^\]]*\]\(|<img\s[^>]*?src=\")"
    r"(?:https://arxiv\.org/html/)?(\d{4}\.\d{4,5}v\d+/[^)\"\s]+)"
)


def to_webp(data):
    """Downscale a raster image to FIGURE_MAX_SIDE and re-encode it as WebP."""
    from PIL import Image

    image = Image.open(io.BytesIO(data))
    image.load()
    if max(image.size) > FIGURE_MAX_SIDE:
        image.thumbnail((FIGURE_MAX_SIDE, FIGURE_MAX_SIDE))
    has_alpha = image.mode in ("RGBA", "LA", "PA") or "transparency" in image.info
    image = image.convert("RGBA" if has_alpha else "RGB")
    out = io.BytesIO()
    image.save(out, "WEBP", quality=FIGURE_QUALITY, method=6)
    return out.getvalue()


def localize_figures(body, save, pause=0.2):
    """Download every arXiv-hosted raster figure in a markdown body.

    Each image goes through to_webp and then `save(data)`, which writes it and
    returns the link to put in its place. A figure that cannot be downloaded or
    decoded keeps an absolute arXiv link. Returns (new body, number failed).
    """
    saved, failed = {}, set()

    def replace(m):
        path = m.group(2)
        url = f"https://arxiv.org/html/{path}"
        if path not in saved and path not in failed:
            data = fetch(url)
            time.sleep(pause)
            try:
                saved[path] = save(to_webp(data)) if data else None
            except Exception:
                saved[path] = None
            if saved[path] is None:
                failed.add(path)
        return m.group(1) + (saved.get(path) or url)

    return ARXIV_FIGURE.sub(replace, body), len(failed)


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
    elif len(argv) == 4 and argv[1] == "set-summary":
        path, summary = Path(argv[2]), " ".join(argv[3].split())
        meta, body = read_paper(path)
        if not meta:
            sys.exit(f"error: {path} has no frontmatter")
        meta["summary"] = summary
        write_paper(path, meta, body)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    _main(sys.argv)
