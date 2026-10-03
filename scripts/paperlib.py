#!/usr/bin/env python3
"""Shared helpers for the library scripts: paths, the catalog, frontmatter,
arXiv metadata, downloads and figures.

Also usable from the shell scripts:

    paperlib.py frontmatter-arxiv <meta.xml> <arxiv-id> <source>
    paperlib.py frontmatter-manual <title> <source> [<url>]
    paperlib.py set-summary <paper.md> <summary>
    paperlib.py filename <title>
    paperlib.py set-type <paper.md> <type>
    paperlib.py fetch <url> <out-file>

The first two print a complete YAML frontmatter block (with the --- fences) to
stdout; set-summary and set-type rewrite the paper's `summary:` or `type:` field
in place; filename prints the filename stem for a title; fetch downloads a URL
with fetch()'s retries, writing an empty file on 404 or repeated failure.
"""

import datetime
import gzip
import io
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_DIR = Path(os.environ.get("LIBRARY_DIR", REPO_ROOT / "library"))
PDF_ROOT = Path(
    os.environ.get("PDF_ROOT", Path.home() / "Yandex.Disk.localized" / "Papers")
)
# Downloads from arXiv's HTML renderings (pages and figures) and LaTeX sources
# are kept here (outside the repo, about 10 GB for the whole library), so a
# later reconversion needs no network. Delete a file, or the folder, to fetch
# it again; failed downloads are never kept.
CACHE_DIR = Path(os.environ.get("PAPERS_CACHE", Path.home() / ".cache" / "papers"))
# Hand-maintained data the scripts read: the declared topic tree and the papers
# deliberately not added.
CATALOG_DIR = REPO_ROOT / "catalog"
TOPICS_FILE = CATALOG_DIR / "topics.yaml"
SKIPPED_FILE = CATALOG_DIR / "skipped.yaml"
TOPIC_PATH = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$")

# Field order in every paper's frontmatter. `summary` is written by whoever
# files the paper (the add-paper skill), so the add scripts leave it empty.
FIELDS = ["title", "authors", "published", "arxiv", "url", "source", "type", "summary", "added"]
REQUIRED = ["title", "source", "summary", "added"]
SOURCES = {"html", "pdf-text", "web"}
# Kind of paper, set by the overview skill when it classifies one (optional).
TYPES = {"method", "survey", "benchmark", "study", "system", "position", "theory"}
# Agent memory about papers: notes/<stem>.md, one per paper, keyed by the stem.
NOTES_DIR = REPO_ROOT / "notes"
# Literature reviews, one per scope (a declared folder): reviews/<scope>.md, or
# reviews/<scope>/index.md plus section files once a review is split. Partial
# reading results live in reviews/.work/ (ignored) until the review is written.
REVIEWS_DIR = REPO_ROOT / "reviews"
# Papers whose markdown conversion needs fixing, keyed by stem like notes/.
CONVERSION_ISSUES_FILE = CATALOG_DIR / "conversion-issues.yaml"
# Page links that open a paper's PDF in Anton's viewer (see AGENTS.md).
PDF_LINK_BASE = "http://pdf.invalid/"

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


def cache_path(url):
    """Where a download from arXiv's HTML or e-print service is cached, or None."""
    m = re.match(r"https://arxiv\.org/(html|e-print)/([^?#]+?)/?$", url)
    if not m or ".." in m.group(2):
        return None
    rel = m.group(2)
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", rel) and m.group(1) == "html":
        rel += "/index.html"  # the page itself, next to its figures
    return CACHE_DIR / "arxiv" / m.group(1) / (rel + ".gz")


def fetch(url, attempts=4):
    """GET a URL and return its body as bytes, or None on 404 or repeated failure.

    Downloads go through curl, like the add scripts: arXiv's HTML server
    answers Python's own HTTP client with 406 for anything not already in its
    cache. Throttled requests (errors or an empty body) are retried with
    backoff. arXiv HTML pages, their figures and LaTeX sources are served from
    CACHE_DIR when already there, and stored there when downloaded.
    """
    cached = cache_path(url)
    if cached and cached.exists():
        return gzip.decompress(cached.read_bytes())
    data = download(url, attempts)
    if cached and data:
        cached.parent.mkdir(parents=True, exist_ok=True)
        tmp = cached.with_name(f".{cached.name}.{os.getpid()}.{threading.get_ident()}")
        tmp.write_bytes(gzip.compress(data, 6))
        tmp.replace(cached)  # atomic, so parallel reconversions never read half a file
    return data


def download(url, attempts):
    for attempt in range(attempts):
        with tempfile.NamedTemporaryFile() as out:
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "60", "-o", out.name, "-w", "%{http_code}", url],
                capture_output=True, text=True,
            )
            status = result.stdout.strip()
            if status == "404":
                return None
            if status == "200":
                data = Path(out.name).read_bytes()
                if data:
                    return data
        if attempt < attempts - 1:
            time.sleep(5 * (attempt + 1))
    return None


def title_to_filename(title):
    """A paper's filename stem, from its title.

    Keeps the title's casing and words. A colon or a question mark inside the
    title ends a sentence, so each becomes a full stop ("Zep. A Temporal ...",
    "Is Model Collapse Inevitable. Breaking ..."); a question mark at the very
    end is dropped. LaTeX markup keeps its text (\\textit{X} -> X, \\infty ->
    infty). Other characters that are not legal in filenames become spaces, and
    the name is capped at 100 characters on a word boundary.
    """
    title = str(title).strip()
    title = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", title)
    title = re.sub(r"\\([a-zA-Z]+)\s*", r"\1", title).replace("$", "")
    title = re.sub(r"\?+$", "", title)
    title = re.sub(r"\s*[?:]+(?=\s)", ".", title)
    bad = '/\\:*?<>|"'
    name = "".join(" " if c in bad else c for c in title)
    name = " ".join(name.split())
    name = re.sub(r"\.(\s*\.)+", ".", name)
    if len(name) > 100:
        cut = name[:100]
        name = cut[: cut.rfind(" ")] if " " in cut else cut
        # A cut that lands just after a comma or dash leaves it dangling at the
        # end of the filename, which reads like a typo rather than a truncation.
        name = name.rstrip(" ,;:.-–—")
    return name


def load_topics():
    """The declared topic tree: {folder path: scope}, in file order."""
    if not TOPICS_FILE.exists():
        return {}
    return yaml.safe_load(TOPICS_FILE.read_text(encoding="utf-8")) or {}


def load_skipped():
    """The list of papers deliberately not added (dicts with title, reason, ...)."""
    if not SKIPPED_FILE.exists():
        return []
    return yaml.safe_load(SKIPPED_FILE.read_text(encoding="utf-8")) or []


def norm_title(title):
    """A title reduced to lowercase words, for matching across sources."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(title or "").lower()).split())


def load_conversion_issues():
    """The list of flagged conversion problems (dicts with paper, problem, found)."""
    if not CONVERSION_ISSUES_FILE.exists():
        return []
    return yaml.safe_load(CONVERSION_ISSUES_FILE.read_text(encoding="utf-8")) or []


# A markdown link's target, and the paper-map section of a review.
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_PAPER_MAP = re.compile(r"^## Paper map\s*$(.*?)(?=^## |\Z)", re.M | re.S)


def load_reviews():
    """Every literature review: {scope: {"main": path, "files": [paths], "meta": dict}}.

    A review is a markdown file under reviews/ whose frontmatter names a
    `scope`. A split review is reviews/<scope>/index.md; the other markdown files
    in its folder are its sections.
    """
    reviews = {}
    if not REVIEWS_DIR.exists():
        return reviews
    for path in sorted(REVIEWS_DIR.rglob("*.md")):
        if ".work" in path.relative_to(REVIEWS_DIR).parts:
            continue
        meta = read_paper(path)[0]
        if not meta.get("scope"):
            continue
        files = [path]
        if path.name == "index.md":
            files += sorted(p for p in path.parent.glob("*.md") if p != path)
        reviews[str(meta["scope"])] = {"main": path, "files": files, "meta": meta}
    return reviews


def review_links(path):
    """Links in a review file to local files: [(target, resolved path, exists)].

    Covers relative links (to papers, other reviews, docs) and pdf.invalid page
    links, which resolve to the paper's markdown. Web links and in-page anchors
    are left out.
    """
    from urllib.parse import unquote, urlsplit

    out = []
    for target in _LINK.findall(Path(path).read_text(encoding="utf-8")):
        if target.startswith(PDF_LINK_BASE):
            rel = unquote(urlsplit(target).path).lstrip("/")
            resolved = (LIBRARY_DIR / rel).with_suffix(".md")
        elif re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        else:
            resolved = (Path(path).parent / unquote(target.split("#")[0])).resolve()
        out.append((target, resolved, resolved.exists()))
    return out


def review_coverage(review):
    """(papers in the review's scope, those listed in its paper map)."""
    from urllib.parse import unquote

    in_scope = set(paper_files(LIBRARY_DIR / review["meta"]["scope"]))
    listed = set()
    for path in review["files"]:
        for section in _PAPER_MAP.findall(Path(path).read_text(encoding="utf-8")):
            for target in _LINK.findall(section):
                if not re.match(r"^[a-z]+:", target):
                    listed.add((path.parent / unquote(target.split("#")[0])).resolve())
    return in_scope, {p for p in in_scope if p.resolve() in listed}


def review_for(topic, reviews):
    """The review covering a folder: its own, or the nearest ancestor's."""
    parts = topic.split("/")
    for i in range(len(parts), 0, -1):
        scope = "/".join(parts[:i])
        if scope in reviews:
            return scope
    return None


def skipped_index():
    """Map arXiv id and normalised title -> skip record, for lookups."""
    by_id, by_title = {}, {}
    for entry in load_skipped():
        if entry.get("arxiv"):
            by_id[str(entry["arxiv"])] = entry
        by_title[norm_title(entry.get("title"))] = entry
    return by_id, by_title


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
# arXiv serves plots converted from PDF as SVG. Most are small and stay vector;
# a dense scatter plot can run to megabytes, so one larger than this is
# rasterized to WebP like the other figures (with rsvg-convert, from librsvg).
SVG_MAX_BYTES = 300_000

# A raster figure on arXiv's HTML rendering, as pandoc writes it: a markdown
# image or an <img>, with the link either relative to the rendering
# ("2501.13956v1/x1.png") or already absolute.
ARXIV_FIGURE = re.compile(
    r"(!\[(?:\\.|[^\]\\])*\]\(|<img\s[^>]*?src=\")"
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


def is_svg(data):
    head = data[:1000].lstrip().lower()
    return head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in head)


def svg_to_webp(data):
    png = subprocess.run(
        ["rsvg-convert", "--width", str(FIGURE_MAX_SIDE), "--keep-aspect-ratio"],
        input=data, capture_output=True, check=True, timeout=120,
    ).stdout
    return to_webp(png)


def localize_figures(body, save, pause=0.2):
    """Download every arXiv-hosted figure in a markdown body.

    A raster image goes through to_webp and then `save(data, "webp")`; an SVG
    is passed on unchanged as `save(data, "svg")`, unless it is larger than
    SVG_MAX_BYTES, when it is rasterized to WebP. `save` writes the file and
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
                if not data:
                    saved[path] = None
                elif is_svg(data) and len(data) > SVG_MAX_BYTES:
                    try:
                        saved[path] = save(svg_to_webp(data), "webp")
                    except Exception:
                        saved[path] = save(data, "svg")
                elif is_svg(data):
                    saved[path] = save(data, "svg")
                else:
                    saved[path] = save(to_webp(data), "webp")
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
    elif len(argv) == 3 and argv[1] == "filename":
        print(title_to_filename(argv[2]))
    elif len(argv) == 4 and argv[1] == "set-summary":
        path, summary = Path(argv[2]), " ".join(argv[3].split())
        meta, body = read_paper(path)
        if not meta:
            sys.exit(f"error: {path} has no frontmatter")
        meta["summary"] = summary
        write_paper(path, meta, body)
    elif len(argv) == 4 and argv[1] == "set-type":
        path, kind = Path(argv[2]), argv[3]
        if kind not in TYPES:
            sys.exit(f"error: unknown type `{kind}` (one of: {', '.join(sorted(TYPES))})")
        meta, body = read_paper(path)
        if not meta:
            sys.exit(f"error: {path} has no frontmatter")
        meta["type"] = kind
        write_paper(path, meta, body)
    elif len(argv) == 4 and argv[1] == "fetch":
        Path(argv[3]).write_bytes(fetch(argv[2]) or b"")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    _main(sys.argv)
