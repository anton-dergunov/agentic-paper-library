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
    paperlib.py shell-config

The first two print a complete YAML frontmatter block (with the --- fences) to
stdout; set-summary and set-type rewrite the paper's `summary:` or `type:` field
in place; filename prints the filename stem for a title; fetch downloads a URL
with fetch()'s retries, writing an empty file on 404 or repeated failure;
shell-config prints the library's paths as shell assignments for config.sh,
and fails outside a library.
"""

import datetime
import gzip
import io
import json
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

# The engine: these scripts, the skills and the guide. Everything a library
# holds is found from the library root instead (see below).
SCRIPTS_DIR = Path(__file__).resolve().parent
ENGINE_ROOT = SCRIPTS_DIR.parent

# A library is a folder with a paper-library.yaml at its root (usually its own
# git repository): the markdown tree, the catalog, notes and reviews live under
# it, and the config says where its PDFs are. The root is $PAPER_LIBRARY, or
# the nearest folder at or above the working directory that has the config.
CONFIG_NAME = "paper-library.yaml"


def find_library_root(start=None):
    """The library root for `start` (default: the working directory), or None."""
    if os.environ.get("PAPER_LIBRARY"):
        return Path(os.environ["PAPER_LIBRARY"]).expanduser().resolve()
    here = Path(start or Path.cwd()).resolve()
    for folder in [here, *here.parents]:
        if (folder / CONFIG_NAME).is_file():
            return folder
    return None


def load_config(root):
    """The library's paper-library.yaml as a dict ({} when there is none)."""
    path = Path(root) / CONFIG_NAME if root else None
    if not path or not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _path(value, base):
    """A configured path: ~ expanded, relative paths taken from the library root."""
    value = Path(os.path.expanduser(str(value)))
    return value if value.is_absolute() else base / value


# Scripts that only convert (html-to-markdown, the tests) work without a
# library; the paths below then point into the working directory, unused.
IN_LIBRARY = find_library_root()
CONFIG = load_config(IN_LIBRARY)
LIBRARY_ROOT = _BASE = IN_LIBRARY or Path.cwd()

# The markdown copies (committed) and the PDFs (kept outside git, often in a
# synced folder). The two trees mirror each other. Environment variables
# override the config, e.g. on a machine where the PDFs are mounted elsewhere.
LIBRARY_DIR = Path(os.environ.get("LIBRARY_DIR") or _path(CONFIG.get("library", "library"), _BASE))
PDF_ROOT = Path(os.environ.get("PDF_ROOT") or _path(CONFIG.get("pdf_root", "pdfs"), _BASE))
# A link inside the library root that points at PDF_ROOT (a symlink made by
# `paperlib init`, kept out of git), so an editor opened on the library shows
# both trees and the indexes link each paper's PDF with a relative path. Off
# unless `pdf_link:` names it in the config.
PDF_LINK_DIR = _path(CONFIG["pdf_link"], _BASE) if CONFIG.get("pdf_link") else None
# Downloads from arXiv's HTML renderings (pages and figures) and LaTeX sources
# are kept here (about 10 GB for 2,000 papers), shared by every library, so a
# later reconversion needs no network. Delete a file, or the folder, to fetch
# it again; failed downloads are never kept.
CACHE_DIR = Path(os.environ.get("PAPERS_CACHE") or _path(CONFIG.get("cache", "~/.cache/papers"), _BASE))
# Hand-maintained data the scripts read: the declared topic tree, the papers
# deliberately not added, and the papers whose conversion needs fixing.
CATALOG_DIR = _path(CONFIG.get("catalog", "catalog"), _BASE)
TOPICS_FILE = CATALOG_DIR / "topics.yaml"
SKIPPED_FILE = CATALOG_DIR / "skipped.yaml"
CONVERSION_ISSUES_FILE = CATALOG_DIR / "conversion-issues.yaml"
TOPIC_PATH = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$")
# Agent memory about papers: notes/<stem>.md, one per paper, keyed by the stem.
NOTES_DIR = _path(CONFIG.get("notes", "notes"), _BASE)
# Literature reviews, one per scope (a declared folder): reviews/<scope>.md, or
# reviews/<scope>/index.md plus section files once a review is split. Partial
# reading results live in reviews/.work/ (ignored) until the review is written.
REVIEWS_DIR = _path(CONFIG.get("reviews", "reviews"), _BASE)
# Papers waiting to be added: raw links or titles, one per line.
INBOX_FILE = _path(CONFIG.get("inbox", "INBOX.txt"), _BASE)
# The reader's own notes on papers (the overview skill writes one per paper),
# e.g. a folder in an Obsidian vault. Optional.
OVERVIEW_DIR = _path(CONFIG["overview_dir"], _BASE) if CONFIG.get("overview_dir") else None
# Page links that open a paper's PDF at a page or section in the VS Code PDF
# viewer (see the guide): http://pdf.invalid/<path under PDF_ROOT>?page=N.
PDF_LINK_BASE = "http://pdf.invalid/"

# Field order in every paper's frontmatter. `summary` is written by whoever
# files the paper (the add-paper skill), so the add scripts leave it empty.
FIELDS = ["title", "authors", "published", "arxiv", "url", "source", "type", "summary", "added"]
REQUIRED = ["title", "source", "summary", "added"]
SOURCES = {"html", "pdf-text", "web"}
# Kind of paper, set by the overview skill when it classifies one (optional).
TYPES = {"method", "survey", "benchmark", "study", "system", "position", "theory"}

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


def split_frontmatter(text):
    """Return (frontmatter dict, body) for a paper's text; ({}, text) if none."""
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def read_paper(path):
    """Return (frontmatter dict, body) for a paper file; ({}, text) if none."""
    return split_frontmatter(Path(path).read_text(encoding="utf-8"))


_REFERENCES = re.compile(r"^#{1,3} +(References|Bibliography|REFERENCES)\b.*$", re.M)


def read_view(meta, body, appendix=False):
    """A paper as a reader needs it: main text only, without link targets or inline tags.

    With `appendix`, the sections after the reference list are kept (for a paper whose
    main results live there) and only the list itself is cut.

    Cuts at the references heading, turns image links into "[figure]", and ends with a
    line saying what was left out, so a reader does not report the missing references
    and appendices as a broken conversion. Headings keep their (p. N), tables stay.
    """
    cut = _REFERENCES.search(body)
    after = ""
    if cut:
        body, after = body[:cut.start()], body[cut.end():]
        if appendix:
            following = re.search(r"^#{1,3} ", after, re.M)
            body, after = body + (after[following.start():] if following else ""), ""
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "[figure]", body)
    body = re.sub(r"\]\((#|https?://)[^)]*\)", "]", body)
    # A superscript without its tag reads as a digit of the number: "10<sup>4</sup>" as 104.
    for tag, mark in (("sup", "^"), ("sub", "_")):
        body = re.sub(rf"<{tag}>((?:(?!</?{tag}>)[^\n])+)</{tag}>",
                      lambda m: mark + (m.group(1) if len(m.group(1)) == 1 else f"{{{m.group(1)}}}"), body)
    body = re.sub(r"</?(span|sup|sub|a|div)\b[^>]*>", "", body)
    body = re.sub(r' (class|style|id)="[^"]*"', "", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    left_out = "the references"
    later = [h.strip("# ").strip() for h in re.findall(r"^#{1,2} .*$", after, re.M)]
    if later:
        sections = "1 section" if len(later) == 1 else f"{len(later)} sections"
        left_out += f" and {sections} after them (first: {later[0]})"
    if cut and appendix:
        left_out = "the reference list only; the appendices are included"
    note = (f"[End of the main text. Left out of this view: {left_out}.]" if cut
            else "[No references heading found: this is the whole paper.]")
    title = " ".join(str(meta.get("title") or "").split())
    return f"# {title}\n\nsource: {meta.get('source', '?')}\n\n{body}\n\n{note}\n"


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


def ask_model(model, system, prompt):
    """One request to a Claude model through `claude -p`, with no tools.

    Returns (reply text, usage dict); raises RuntimeError on failure.

    The environment keeps the user's CLAUDE.md files and background requests out of the
    request: they are about 800 of its 1,400 fixed tokens (experiments/prompt-trim).
    """
    env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
           "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", system,
             "--output-format", "json", "--no-session-persistence"],
            input=prompt, capture_output=True, text=True, cwd=empty, env=env)
    try:
        reply = json.loads(done.stdout)
    except ValueError:
        raise RuntimeError((done.stderr or done.stdout or "no output").strip()[:300])
    if reply.get("is_error") or not reply.get("result"):
        raise RuntimeError(str(reply.get("result") or reply.get("subtype") or "no reply")[:300])
    usage = reply.get("usage", {})
    return reply["result"], {
        "input": sum(usage.get(k, 0) or 0 for k in
                     ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "output": usage.get("output_tokens", 0), "usd": reply.get("total_cost_usd")}


def filing_choice(reply, topics):
    """(folder, reason, summary) from a filing model's JSON reply.

    The folder is None when the model found none, or named one that is not declared: a
    script never creates a folder, that is the reader's decision.
    """
    try:
        answer = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
    except ValueError:
        raise RuntimeError("the filing model did not reply with JSON: " + reply.strip()[:200])
    folder = str(answer.get("folder") or "").strip().strip("/")
    summary = " ".join(str(answer.get("summary") or "").split())
    return (folder if folder in topics else None), str(answer.get("reason") or "").strip(), summary


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


def append_conversion_issues(entries):
    """Add entries (dicts with paper, problem, found) to the end of the catalog file.

    Appended as text, so the file's header comments stay as they are.
    """
    text = CONVERSION_ISSUES_FILE.read_text(encoding="utf-8") if CONVERSION_ISSUES_FILE.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    text += yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=100)
    CONVERSION_ISSUES_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONVERSION_ISSUES_FILE.write_text(text, encoding="utf-8")


def note_path(paper):
    return NOTES_DIR / f"{Path(paper).stem}.md"


# A note's `conversion:` line is `ok`, a description of what is broken in the paper's
# markdown, or `key-content-broken: <description>` when a part the paper's findings rest on
# is missing or wrong (so the note may be too).
_CONVERSION = re.compile(r"^conversion:[ \t]*(.*)$", re.M)


def note_conversion(text):
    """(state, description) from a note's text: state is "ok", "problem", "key-content-broken",
    or None when the note has no conversion line."""
    m = _CONVERSION.search(text)
    if not m:
        return None, ""
    value = m.group(1).strip()
    if re.fullmatch(r"ok\.?", value, re.I):
        return "ok", ""
    key = re.match(r"key-content-broken[ \t]*:[ \t]*(.*)$", value, re.I)
    if key:
        return "key-content-broken", key.group(1).strip()
    return "problem", value


# A markdown link's target, and the paper-map section of a review. Reviews use
# reference-style links ("[MMLU][mmlu]", defined once as "[mmlu]: <target>" at the
# end of the file), so that the long encoded paths stay out of the prose; inline
# links work too.
_LINK = re.compile(r"\]\(([^)\s]+)\)")
REF_USE = re.compile(r"\]\[([^\]\n]+)\]")
REF_DEF = re.compile(r"^\[([^\]\n]+)\]:[ \t]+(\S+)[ \t]*$", re.M)
_PAPER_MAP = re.compile(r"^## Paper map\s*$(.*?)(?=^## |\Z)", re.M | re.S)


def link_definitions(text):
    """A file's reference-link definitions: {label (lowercased): target}."""
    return {label.lower(): target for label, target in REF_DEF.findall(text)}


def link_targets(text, definitions=None):
    """Targets of the links in `text`: inline ones, then reference-style ones looked
    up in `definitions` (default: those defined in `text`). A reference to a label
    that is not defined comes back as "[label]", which resolves to nothing."""
    if definitions is None:
        definitions = link_definitions(text)
    return _LINK.findall(text) + [definitions.get(label.lower(), f"[{label}]")
                                  for label in REF_USE.findall(text)]


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
    text = Path(path).read_text(encoding="utf-8")
    # Definitions nothing refers to are checked as well, so a stale one is noticed.
    for target in dict.fromkeys(link_targets(text) + list(link_definitions(text).values())):
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
        text = Path(path).read_text(encoding="utf-8")
        definitions = link_definitions(text)
        for section in _PAPER_MAP.findall(text):
            for target in link_targets(section, definitions):
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
    elif len(argv) == 2 and argv[1] == "shell-config":
        if not IN_LIBRARY:
            sys.exit(f"error: not inside a paper library (no {CONFIG_NAME} here or above, "
                     "and PAPER_LIBRARY is not set)")
        import shlex
        for name, value in [("LIBRARY_ROOT", LIBRARY_ROOT), ("LIBRARY_DIR", LIBRARY_DIR),
                            ("PDF_ROOT", PDF_ROOT), ("TOPICS_FILE", TOPICS_FILE)]:
            print(f"{name}={shlex.quote(str(value))}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    _main(sys.argv)
