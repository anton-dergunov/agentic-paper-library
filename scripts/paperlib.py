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
import difflib
import functools
import gzip
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import unicodedata
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

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
# Hand-maintained data the scripts read: the declared topic tree and the papers
# deliberately not added.
CATALOG_DIR = _path(CONFIG.get("catalog", "catalog"), _BASE)
TOPICS_FILE = CATALOG_DIR / "topics.yaml"
SKIPPED_FILE = CATALOG_DIR / "skipped.yaml"
TOPIC_PATH = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$")
# Agent memory about papers: notes/<stem>.md, one per paper, keyed by the stem.
NOTES_DIR = _path(CONFIG.get("notes", "notes"), _BASE)
# Conversion problems: issues/<stem>.yaml for a paper that has any, keyed by the stem
# like the notes. Each holds a list of records, one problem each, whose `kind` is the id
# of a ticket in the engine's tickets/ (one ticket per cause), or `new` until triage
# gives it one.
ISSUES_DIR = _path(CONFIG.get("issues", "issues"), _BASE)
# Hand corrections: corrections/<stem>.yaml for a paper corrected by hand, keyed by the
# stem like the notes. `paperlib reconvert` converts the paper afresh and applies them
# again (apply_corrections below).
CORRECTIONS_DIR = _path(CONFIG.get("corrections", "corrections"), _BASE)
# The tickets: the active ones (open, or fixed and waiting for a reconversion) at the top
# of tickets/, the closed ones in tickets/done/ and tickets/wont-fix/, whose folder is their
# status. TICKETS_DIR overrides it (the tests use a copy).
TICKETS_DIR = Path(os.environ.get("TICKETS_DIR") or ENGINE_ROOT / "tickets")
TICKET_FOLDERS = ("done", "wont-fix")
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
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


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
    # An icon keeps its name ("[check-mark]"); a picture without one is "[figure]".
    body = re.sub(r"!\[([^\]]*)\]\([^)]*\)", lambda m: f"[{m.group(1).strip() or 'figure'}]", body)
    def img(m):
        alt = re.search(r'\balt="([^"]*)"', m.group(0))
        return f"[{(alt.group(1) if alt else '').strip() or 'figure'}]"
    body = re.sub(r"<img\b[^>]*>", img, body)
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
            "categories": [c.get("term") for c in entry.findall("a:category", ATOM)],
            "comment": " ".join(entry.findtext("arxiv:comment", "", ATOM).split()),
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


def fetch(url, attempts=4, fresh=False):
    """GET a URL and return its body as bytes, or None on 404 or repeated failure.

    Downloads go through curl, like the add scripts: arXiv's HTML server
    answers Python's own HTTP client with 406 for anything not already in its
    cache. Throttled requests (errors or an empty body) are retried with
    backoff. arXiv HTML pages, their figures and LaTeX sources are served from
    CACHE_DIR when already there (unless `fresh`), and stored there when downloaded.
    """
    cached = cache_path(url)
    if cached and cached.exists() and not fresh:
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
                ["curl", "-sL", "--max-time", "600", "--speed-limit", "1024", "--speed-time", "60",
                 "-o", out.name, "-w", "%{http_code}", url],
                capture_output=True, text=True,
            )
            status = result.stdout.strip()
            if status == "404":
                return None
            # A transfer cut short (a time limit, a dropped connection) still
            # reports the 200 it began with; only curl's exit status tells.
            if status == "200" and result.returncode == 0:
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


# A symbol or a logo a paper sets as a small picture, in a table cell or a sentence.
ICON_PROMPT = (
    "This small picture is set inline in a research paper, in a table cell or a sentence. Reply with "
    "only what a reader sees in it: one Unicode symbol when one fits (✓ ✗ ○ ● ◐ ★ ☆ ▲ ▼ ❄ 🔥 🔒); for a "
    "plain coloured shape (a dot, a square, a bar) its colour and the shape (\"green ●\"); else a word or "
    "two naming a logo, an emoji, or the letter or number drawn in it. Reply - if it is blank.")
# Which model reads them (`icon_model` in paper-library.yaml); "off" leaves them as pictures.
ICON_MODEL = os.environ.get("PAPERLIB_ICONS") or CONFIG.get("icon_model", "haiku")


def read_icon(data):
    """What a small picture (SVG or raster bytes) shows, as text: "✓", "OpenAI"; "" when
    it draws nothing; None when it could not be read (the picture then stays a picture).

    One request to a vision model per distinct picture, through `claude -p` with the
    picture in the message, its reply cached by the picture's hash under CACHE_DIR/icons,
    so a reconversion asks nothing again.
    """
    import base64
    import hashlib

    from PIL import Image

    if ICON_MODEL == "off":
        return None
    cached = CACHE_DIR / "icons" / (hashlib.sha256(data).hexdigest() + ".txt")
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    try:
        if is_svg(data):
            data = subprocess.run(["rsvg-convert", "--height", "64", "--keep-aspect-ratio", "--background-color", "white"],
                                  input=data, capture_output=True, check=True, timeout=60).stdout
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception:
        return None
    image = image.convert("RGBA")
    flat = Image.new("RGBA", image.size, "white")
    flat.alpha_composite(image)
    flat = flat.convert("RGB")
    if flat.getextrema() and all(lo == hi for lo, hi in flat.getextrema()):
        text = ""  # one colour throughout: nothing drawn
    else:
        if max(flat.size) < 64:
            flat = flat.resize((max(1, flat.width * 64 // max(flat.size)), max(1, flat.height * 64 // max(flat.size))))
        png = io.BytesIO()
        flat.save(png, "PNG")
        message = {"type": "user", "message": {"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                         "data": base64.b64encode(png.getvalue()).decode()}},
            {"type": "text", "text": ICON_PROMPT}]}}
        env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
        with tempfile.TemporaryDirectory() as empty:
            done = subprocess.run(
                ["claude", "-p", "--model", ICON_MODEL, "--tools", "", "--input-format", "stream-json",
                 "--output-format", "stream-json", "--verbose", "--no-session-persistence",
                 "--system-prompt", "You say what small pictures show."],
                input=json.dumps(message) + "\n", capture_output=True, text=True, cwd=empty, env=env, timeout=180)
        replies = [json.loads(line) for line in done.stdout.splitlines() if line.startswith("{")]
        result = next((r for r in replies if r.get("type") == "result"), {})
        text = " ".join(str(result.get("result") or "").split()).strip("\"'`.")
        if result.get("is_error") or not text or len(text) > 30 or len(text.split()) > 3:
            return None
        text = "" if text == "-" else text
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(text, encoding="utf-8")
    return text


def filing_prompts(topics):
    """(system prompt, paper template) for a filing request: guide/filing-prompt.md.

    The rules and the topic tree are the system prompt, the same for every paper of a run,
    so the requests after the first read them from the prompt cache. The template takes
    `title` and `abstract`.
    """
    rules, the_paper = (ENGINE_ROOT / "guide" / "filing-prompt.md").read_text(encoding="utf-8").split("THE PAPER")
    tree = "\n".join(f"{folder}: {scope}" for folder, scope in topics.items())
    # A few summaries already in the library, spread over it, for the model to match.
    summaries = [s for s in (" ".join(str(read_paper(p)[0].get("summary") or "").split())
                             for p in paper_files()) if s]
    style = "\n".join("- " + s for s in summaries[::max(1, len(summaries) // 3)][:3]) or "(none yet)"
    system = "You are a careful research librarian.\n\n" + rules.format(topics=tree, style=style).strip()
    return system, "THE PAPER" + the_paper


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


def find_by_title(words, titles):
    """The keys of `titles` (key -> title) whose title holds all the words given."""
    wanted = norm_title(words).split()
    return [key for key, title in titles.items() if wanted and all(w in norm_title(title).split() for w in wanted)]


class _NoAliases(yaml.SafeDumper):
    """Write a shared value (the date) in full each time: appended anchors would clash."""

    def ignore_aliases(self, data):
        return True


def append_skipped(entries):
    """Add entries (dicts with title, reason, date, ...) to the end of the skipped list.

    Appended as text, so the file's header comments stay as they are; the `[]` of a
    list that is still empty gives way to the entries.
    """
    text = SKIPPED_FILE.read_text(encoding="utf-8") if SKIPPED_FILE.exists() else ""
    text = re.sub(r"^\[\][ \t]*\n?\Z", "", text, flags=re.M)
    if text and not text.endswith("\n"):
        text += "\n"
    text += yaml.dump(entries, Dumper=_NoAliases, sort_keys=False, allow_unicode=True, width=100)
    SKIPPED_FILE.parent.mkdir(parents=True, exist_ok=True)
    SKIPPED_FILE.write_text(text, encoding="utf-8")


def note_path(paper):
    return NOTES_DIR / f"{Path(paper).stem}.md"


def has_digest(paper):
    """Whether a paper (a path or a stem) has been read: its note holds a digest."""
    note = NOTES_DIR / f"{paper_stem(paper)}.md"
    return note.exists() and "## Digest" in note.read_text(encoding="utf-8")


# A note to read again: "reread: <why> (<date>)" among the lines above its digest, set when
# a fix reaches a part of the paper its findings rest on (a key-content record closed), or
# by hand. Reading the paper again writes a new note, which drops it.
_REREAD = re.compile(r"^reread: (.*)$", re.M)


def reread_reason(paper):
    """Why a paper's note is to be read again, or "" when it is not."""
    note = NOTES_DIR / f"{paper_stem(paper)}.md"
    if not note.exists():
        return ""
    head = note.read_text(encoding="utf-8").split("\n## Digest", 1)[0]
    m = _REREAD.search(head)
    return m.group(1).strip() if m else ""


def flag_reread(paper, reason=None, today=None):
    """Mark a paper's note to be read again (reason None takes the mark off). Returns
    False when the paper has no note with a digest, which a reading will write anyway."""
    note = NOTES_DIR / f"{paper_stem(paper)}.md"
    if not has_digest(paper):
        return False
    text = note.read_text(encoding="utf-8")
    head, digest = text.split("\n## Digest", 1)
    head = _REREAD.sub("", head).rstrip("\n")
    head = re.sub(r"\n{3,}", "\n\n", head)
    if reason:
        reason = " ".join(str(reason).split())
        head += f"\nreread: {reason} ({today or datetime.date.today().isoformat()})"
    note.write_text(head + "\n\n## Digest" + digest, encoding="utf-8")
    return True


# A conversion problem's record, in issues/<stem>.yaml. `kind` is a ticket id, or `new`
# with `suggested` naming the cause; `key-content` is set when a part the paper's findings
# rest on is missing or wrong (a results table, the main equation, a section), so a note
# written from the paper may be wrong too; `by` says who found it; `wont-fix` gives the
# reason a problem is left as it is.
ISSUE_FIELDS = ["kind", "suggested", "where", "what", "key-content", "by", "found", "wont-fix"]
ISSUE_SOURCES = {"reader", "session", "symptoms"}
TICKET_STATUSES = {"open", "fixed", "done", "wont-fix"}
TICKET_TAKES = {"engine", "reconvert", "reread", "by-hand"}


def paper_stem(paper):
    """The stem a paper is keyed by in notes/ and issues/: a path's stem, or a stem as given
    (titles hold dots, so a bare stem is never split at one)."""
    text = str(paper)
    return Path(text).stem if text.endswith(".md") else Path(text).name


def issues_path(paper):
    return ISSUES_DIR / f"{paper_stem(paper)}.yaml"


def load_issues(paper):
    """The conversion-problem records of a paper (a path or a stem); [] when it has none."""
    path = issues_path(paper)
    if not path.exists():
        return []
    return [r for r in yaml.safe_load(path.read_text(encoding="utf-8")) or [] if isinstance(r, dict)]


def save_issues(paper, records):
    """Write a paper's records, fields in their usual order; delete the file when none is left."""
    path = issues_path(paper)
    if not records:
        path.unlink(missing_ok=True)
        return
    ordered = [{**{k: r[k] for k in ISSUE_FIELDS if r.get(k) not in (None, "", False)},
                **{k: v for k, v in r.items() if k not in ISSUE_FIELDS}} for r in records]
    ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")


def all_issues(stems=None):
    """{stem: records} for every paper with an issues file, or only for the stems given."""
    if not ISSUES_DIR.is_dir():
        return {}
    wanted = set(stems) if stems is not None else None
    found = {}
    for path in sorted(ISSUES_DIR.glob("*.yaml")):
        if wanted is None or path.stem in wanted:
            records = load_issues(path.stem)
            if records:
                found[path.stem] = records
    return found


_WONT_FIX_TICKETS = None


def wont_fix_reason(record):
    """Why a problem is left as it is: its own `wont-fix`, or that of its ticket when the
    whole cause is wont-fix; "" for an open problem."""
    global _WONT_FIX_TICKETS
    if record.get("wont-fix"):
        return str(record["wont-fix"])
    if _WONT_FIX_TICKETS is None:
        _WONT_FIX_TICKETS = {tid: str(t.get("reason") or "the ticket is wont-fix")
                             for tid, t in load_tickets().items() if t.get("status") == "wont-fix"}
    reason = _WONT_FIX_TICKETS.get(record.get("kind"))
    return f"ticket: {reason}" if reason else ""


def is_open(record):
    return not wont_fix_reason(record)


def describe_issue(record):
    """A record on one line: where · kind · what, with its flags."""
    kind = record.get("kind", "?")
    if kind == "new" and record.get("suggested"):
        kind = f"new:{record['suggested']}"
    reason = wont_fix_reason(record)
    flags = (" · KEY CONTENT" if record.get("key-content") else "") + \
            (f" · wont-fix: {reason}" if reason else "")
    return f"{record.get('where', '?')} · {kind}{flags} · {' '.join(str(record.get('what', '')).split())}"


def load_tickets():
    """{id: ticket} from the engine's tickets/: the frontmatter (id, title, converter, takes,
    status, cost, `reason` for a wont-fix one, `closed` for a closed one) plus `body` and
    `path`. A ticket in done/ or wont-fix/ has that status; `declared` keeps the status its
    frontmatter gives, if any, for the check."""
    tickets = {}
    if not TICKETS_DIR.is_dir():
        return tickets
    paths = [p for p in sorted(TICKETS_DIR.glob("*.md")) if p.name != "README.md"]
    for folder in TICKET_FOLDERS:
        paths += sorted((TICKETS_DIR / folder).glob("*.md"))
    for path in paths:
        meta, body = read_paper(path)
        meta = dict(meta or {})
        meta.setdefault("id", path.stem)
        meta["declared"] = meta.get("status")
        folder = path.parent.name if path.parent != TICKETS_DIR else None
        meta["status"] = folder or meta.get("status") or "open"
        tickets[meta["id"]] = {**meta, "body": body, "path": path}
    return tickets


# A hand correction, in corrections/<stem>.yaml, replaces the converter's text `was` with
# `now` (an empty `was` inserts `now` after the line `prev`; an empty `now` deletes).
# `was` is the anchor: the converter's own text, matched line by line after
# normalising (_norm_line), so a change elsewhere in the paper never moves it. When it
# repeats, or the converter changed it slightly, the landmarks decide: `section` (the
# heading above), `prev` and `next` (the first 80 normalised characters of the lines
# around it) and `label` (its table, figure or equation). `where` and `why` are for
# people and sessions and are never matched. `drifted` and `stale` record the last
# reconversion that matched it only approximately (cleared by a later exact match), or not
# at all. Each reapplication also brings `now` onto the converter's new text (rebase_now).
CORRECTION_FIELDS = ["where", "why", "section", "label", "prev", "next", "was", "now", "by", "added",
                     "drifted", "stale"]
# The marker an applied correction leaves in the paper, also when it carries a note:
# "<!-- hand-edited: Table 4 rewritten from the PDF page -->".
HAND_EDITED = re.compile(r"<!--\s*hand-edited\b")
HAND_EDITED_COMMENT = re.compile(r"<!--\s*hand-edited\b.*?-->", re.S)
# How close the converter's new text must be to `was`, where the landmarks place it, for
# the correction to replace it (experiments/hand-edit-corrections).
DRIFT_MIN = 0.9
# ... or this close, where `prev` and `next` both bound it, so its place is certain.
DRIFT_BOUNDED_MIN = 0.5
_PAGE_MARK = re.compile(r"\s*\((?:p|pp)\.\s[^)]*\)\s*$")
_LABEL = re.compile(r"\b(Table|Figure|Fig\.|Algorithm)\s+([0-9]+[a-z]?|[IVXLC]+)\b")
_EQ_TAG = re.compile(r"\\tag\{([^}]+)\}|\((\d+[a-z]?)\)\s*\$\$\s*$")


class _BlockDumper(yaml.SafeDumper):
    """Writes multi-line strings as literal blocks, so tables stay readable in the file."""


_BlockDumper.add_representer(
    str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|" if "\n" in s else None))


def corrections_path(paper):
    return CORRECTIONS_DIR / f"{paper_stem(paper)}.yaml"


def load_corrections(paper):
    """The hand corrections of a paper (a path or a stem); [] when it has none."""
    path = corrections_path(paper)
    if not path.exists():
        return []
    return [c for c in yaml.safe_load(path.read_text(encoding="utf-8")) or [] if isinstance(c, dict)]


def save_corrections(paper, corrections):
    """Write a paper's corrections, fields in their usual order; delete the file when none is left."""
    path = corrections_path(paper)
    if not corrections:
        path.unlink(missing_ok=True)
        return
    ordered = []
    for c in corrections:
        c = {k: ("\n".join(line.rstrip() for line in v.split("\n")) if isinstance(v, str) else v)
             for k, v in c.items()}  # a trailing space would force a quoted string
        ordered.append({**{k: c[k] for k in CORRECTION_FIELDS if c.get(k) not in (None, "")},
                        **{k: v for k, v in c.items() if k not in CORRECTION_FIELDS}})
    CORRECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(ordered, Dumper=_BlockDumper, allow_unicode=True, sort_keys=False, width=100),
                    encoding="utf-8")


def all_corrections():
    """{stem: corrections} for every paper with a corrections file."""
    if not CORRECTIONS_DIR.is_dir():
        return {}
    return {p.stem: load_corrections(p.stem) for p in sorted(CORRECTIONS_DIR.glob("*.yaml"))}


def correction_images(corrections):
    """The figure files a paper's corrections link (a crop from the PDF), which a
    reconversion must keep."""
    return {Path(unquote(m)).name for c in corrections
            for m in re.findall(r"\]\((?:\./)?images/([^)\s]+)\)", c.get("now") or "")}


def _norm_line(line):
    """A line as the matching compares it: Unicode NFC, whitespace collapsed, table cells
    stripped of their padding (any separator row alike), headings without their (p. N)."""
    line = unicodedata.normalize("NFC", line).strip()
    if line.startswith("|"):
        parts = line.strip().strip("|").split("|")
        cells = [_norm_cell(c) if len(parts) == 1 else " ".join(c.split()) for c in parts]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c) and any(cells):
            cells = ["-"] * len(cells)
        return "|" + "|".join(cells) + "|"
    if line.startswith("#"):
        line = _PAGE_MARK.sub("", line)
    # An image's alt text is the converter's ("Refer to caption"); its target is the figure.
    line = re.sub(r"!\[[^\]]*\]\(", "![](", line)
    return " ".join(line.split())


def _plain(norm):
    """A normalised line without emphasis or escapes, which a converter adds and drops."""
    return " ".join(re.sub(r"[*_`\\]", "", norm).split())


def _fingerprint(norm):
    """A landmark line as compared: its first 80 characters, plain (a caption's bold title)."""
    return _plain(norm)[:80]


def _norm_cell(cell):
    """The cell of a one-column table (an algorithm set as a table) without its padding,
    but with its indentation beyond the one space every cell starts with: the loop body's.
    In a wider table, leading space is a table writer's alignment and is dropped."""
    text = " ".join(cell.split())
    indent = len(cell) - len(cell.lstrip(" \u00a0"))
    return " " * (indent - 1) + text if indent > 1 and text else text


def is_marker(line):
    """A line holding only a hand-edited marker (and other comments), or a pointer to a
    correction that was not applied: never part of what a correction matches."""
    stripped = line.strip()
    if stripped.startswith("> A hand correction of ") and "could not be re-applied" in stripped:
        return True
    return bool(HAND_EDITED.search(stripped)) and not re.sub(r"<!--.*?-->", "", stripped).strip()


def _strip_markers(text):
    """`text` without its marker lines and leading or trailing blank lines."""
    lines = [line for line in (text or "").split("\n") if not is_marker(line)]
    return "\n".join(lines).strip("\n")


def content_lines(text):
    """The normalised non-blank lines of `text`, markers left out: what is matched."""
    return [_norm_line(line) for line in (text or "").split("\n") if line.strip() and not is_marker(line)]


class BodyLines:
    """A paper body as the matching sees it: its raw lines, and for each non-blank,
    non-marker line its index, normalised text and the heading above it."""

    def __init__(self, text):
        self.raw = text.split("\n")
        self.idx, self.seq, self.section, self.fp = [], [], [], []
        heading = ""
        for i, line in enumerate(self.raw):
            if not line.strip() or is_marker(line):
                continue
            norm = _norm_line(line)
            self.idx.append(i)
            self.seq.append(norm)
            self.fp.append(_fingerprint(norm))
            self.section.append(heading)
            if norm.startswith("#"):
                heading = norm.lstrip("#").strip()

    def find(self, pattern):
        k = len(pattern)
        if not k:
            return []
        return [i for i in range(len(self.seq) - k + 1) if self.seq[i] == pattern[0] and self.seq[i:i + k] == pattern]

    def landmarks(self, i, k):
        """(section, prev, next) around the span of k content lines starting at i."""
        return (self.section[i] if i < len(self.section) else (self.section[-1] if self.section else ""),
                self.fp[i - 1] if i > 0 else "",
                self.fp[i + k] if i + k < len(self.seq) else "")

    def text(self, i, k):
        """The raw text of the span of k content lines starting at i."""
        return "\n".join(self.raw[self.idx[i]:self.idx[i + k - 1] + 1])


def _score(correction, landmarks):
    section, prev, nxt = landmarks
    return ((bool(correction.get("section")) and correction["section"] == section)
            + (bool(correction.get("prev")) and _fingerprint(correction["prev"]) == prev)
            + (bool(correction.get("next")) and _fingerprint(correction["next"]) == nxt))


def _best(correction, lines, spans):
    """The one span, of (start, length) pairs, whose landmarks agree best; None if tied."""
    scored = sorted(((_score(correction, lines.landmarks(i, k)), i, k) for i, k in spans), reverse=True)
    if not scored or (len(scored) > 1 and scored[0][0] == scored[1][0]):
        return None
    return scored[0][1], scored[0][2]


def _drifted(correction, lines, was):
    """(start, length, similarity, bounded) of the region the landmarks place `was` in, the
    one most like it: `bounded` when it lies exactly between `prev` and `next`. None when
    there is none, or a second region, apart from it, is as like."""
    k, seq = len(was), lines.seq
    prev, nxt = _fingerprint(correction.get("prev") or ""), _fingerprint(correction.get("next") or "")
    starts, after_prev = set(), set()
    for j, line in enumerate(lines.fp):
        if prev and line == prev:
            starts.add(j + 1)
            after_prev.add(j + 1)
        if correction.get("label") and line.startswith(correction["label"]):
            starts.update((j, j + 1))
    ends = {j for j, line in enumerate(lines.fp) if nxt and line == nxt}
    candidates = set()
    for s in starts:
        candidates.update((s, n) for n in range(max(1, k - 3), k + 4) if s + n <= len(seq))
        candidates.update((s, e - s) for e in ends if 0 < e - s <= 2 * k + 3)
    for e in ends:
        candidates.update((e - n, n) for n in range(max(1, k - 3), k + 4) if e - n >= 0)
    target = "\n".join(was)
    found = []
    for s, n in candidates:
        if s >= len(seq) or correction.get("section") and lines.section[s] != correction["section"]:
            continue
        bounded = s in after_prev and s + n in ends
        floor = DRIFT_BOUNDED_MIN if bounded else DRIFT_MIN
        matcher = difflib.SequenceMatcher(None, "\n".join(seq[s:s + n]), target, autojunk=False)
        if matcher.real_quick_ratio() >= floor and matcher.quick_ratio() >= floor:
            found.append((matcher.ratio(), bounded, s, n))
    if not found:
        return None
    found.sort(reverse=True)
    ratio, bounded, s, n = found[0]
    # A second region as good, not overlapping the first, makes the place ambiguous.
    if any(r >= ratio - 0.01 and (s2 + n2 <= s or s2 >= s + n) for r, _, s2, n2 in found[1:]):
        return None
    return s, n, ratio, bounded


def block_start(raw, i):
    """The first line of the block holding raw line i (the line after the blank before it)."""
    while i > 0 and raw[i - 1].strip() and not is_marker(raw[i - 1]):
        i -= 1
    return i


def marker_line(correction):
    why = " ".join(str(correction.get("why") or "").split()).replace("-->", "→")
    return f"<!-- hand-edited: {why} -->" if why else "<!-- hand-edited -->"


def _replace(raw, start, end, correction):
    """raw lines with lines start..end-1 replaced by the correction's `now` (start == end
    inserts), and its marker before the block that holds them."""
    now = _strip_markers(correction.get("now"))
    new = now.split("\n") if now else []
    block = block_start(raw, start) if start < len(raw) and raw[start].strip() else start
    inside = block < start  # the edit is part of a block (rows of a table): no blank lines
    if inside:
        return raw[:block] + [marker_line(correction)] + raw[block:start] + new + raw[end:]
    before = [] if block == 0 or not raw[block - 1].strip() else [""]
    after = [""] if new and end < len(raw) and raw[end].strip() else []
    if not new:  # a deletion leaves only its marker, saying what stood there
        return raw[:block] + before + [marker_line(correction)] + after + raw[end:]
    return raw[:block] + before + [marker_line(correction), ""] + new + after + raw[end:]


def _edits(base, other):
    """The changes that turn `base` into `other`, as (start, end, new text) on `base`."""
    matcher = difflib.SequenceMatcher(None, base, other, autojunk=False)
    return [(i1, i2, other[j1:j2]) for op, i1, i2, j1, j2 in matcher.get_opcodes() if op != "equal"]


def _merge_line(base, fresh, hand):
    """`hand` with the converter's own changes from `base` to `fresh` made in it too: a
    three-way merge by characters. None when the two change the same characters, or
    insert different text at one place."""
    ours, theirs = _edits(base, fresh), _edits(base, hand)
    for a1, a2, at in ours:
        for b1, b2, bt in theirs:
            if (a1, a2, at) == (b1, b2, bt):
                continue
            if max(a1, b1) < min(a2, b2) or a1 == a2 == b1 == b2 \
                    or a1 == a2 and b1 < a1 < b2 or b1 == b2 and a1 < b1 < a2:
                return None
    edits = sorted(set(ours) | set(theirs), key=lambda e: (e[0], e[1] != e[0]))
    out, pos = [], 0
    for i1, i2, text in edits:
        out += [base[pos:i1], text]
        pos = i2
    return "".join(out) + base[pos:]


def rebase_now(was, fresh, now):
    """A correction's `now` brought onto the converter's new text for the same place.

    `was` is the converter's text the correction was made against, `fresh` the text a new
    conversion writes there, `now` the corrected text. A line of `now` the hand left as it
    was in `was` becomes its line in `fresh`, so the converter's later improvements (bold,
    escapes, a cell's padding) are kept rather than overwritten by an old copy; a line the
    hand changed gets the converter's changes to it as well where they touch other
    characters (_merge_line), and is kept as it is where they overlap or the converter
    changed only a table's padding. A line of `was` is
    paired with one of `fresh` when the two are alike after normalising, or stand at the
    same place in a run of changed lines of the same length."""
    was, fresh, now = was.split("\n"), fresh.split("\n"), now.split("\n")
    pair = {}
    norm = difflib.SequenceMatcher(None, [_norm_line(x) for x in was], [_norm_line(x) for x in fresh],
                                   autojunk=False)
    for op, i1, i2, j1, j2 in norm.get_opcodes():
        if op == "equal" or op == "replace" and i2 - i1 == j2 - j1:
            pair.update(zip(range(i1, i2), range(j1, j2)))
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, was, now, autojunk=False).get_opcodes():
        if op == "equal":
            out += [fresh[pair[i]] if i in pair else was[i] for i in range(i1, i2)]
        elif op == "replace" and i2 - i1 == j2 - j1:
            for i, j in zip(range(i1, i2), range(j1, j2)):
                # A change only to a table's padding would misalign the hand's columns.
                padding = i in pair and _norm_line(was[i]) == _norm_line(fresh[pair[i]])
                merged = _merge_line(was[i], fresh[pair[i]], now[j]) if i in pair and not padding else None
                out.append(now[j] if merged is None else merged)
        else:
            out += now[j1:j2]
    return "\n".join(out)


def apply_corrections(body, corrections, pointer=None, today=None):
    """Apply a paper's hand corrections to a fresh conversion of its body.

    Returns (body, corrections, outcomes): the corrected body; the corrections to keep,
    their landmarks and `was` taken afresh from the new conversion where they applied, an
    obsolete one left out; and one (correction, outcome, similarity) per correction, the
    outcome one of `exact`, `landmarks` (`was` repeats; the landmarks chose), `drifted`
    (placed by the landmarks, `similarity` like `was`), `obsolete` (`was` is gone and `now`
    is there already: the converter makes the fix itself) or `stale` (not applied). For
    each stale one, a line naming `pointer` (the corrections file) goes under the
    paper's conversion note, so that a reader of the paper knows to look there.
    """
    today = today or datetime.date.today().isoformat()
    kept, outcomes = [], []
    for given in corrections:
        c = dict(given)
        lines = BodyLines(body)
        was, now = content_lines(c.get("was")), content_lines(c.get("now"))
        span, outcome, similarity = None, "stale", None
        # `now` already there means the converter makes the fix; a short `now` could be
        # there by chance.
        fixed = any(len(now) >= 2 or sum(map(len, now)) >= 40 or _score(c, lines.landmarks(i, len(now)))
                    for i in lines.find(now))
        if was:
            hits = lines.find(was)
            if len(hits) == 1:
                span, outcome = (hits[0], len(was)), "exact"
            elif hits:
                span = _best(c, lines, [(i, len(was)) for i in hits])
                outcome = "landmarks" if span else "stale"
            elif fixed:
                outcome = "obsolete"
            else:
                drift = _drifted(c, lines, was)
                if drift:
                    similarity = round(drift[2], 3)
                if drift and (drift[2] >= DRIFT_MIN or drift[3] and drift[2] >= DRIFT_BOUNDED_MIN):
                    span, outcome = drift[:2], "drifted"
                elif not now and not drift:  # a deletion whose text the converter no longer writes
                    outcome = "obsolete"
        elif fixed:
            outcome = "obsolete"
        else:  # an insertion: after `prev`, or else before `next`
            prev, nxt = _fingerprint(c.get("prev") or ""), _fingerprint(c.get("next") or "")
            spots = [(j + 1, 0) for j, line in enumerate(lines.fp) if prev and line == prev]
            if not spots:
                spots = [(j, 0) for j, line in enumerate(lines.fp) if nxt and line == nxt]
            span = spots[0] if len(spots) == 1 else _best(c, lines, spots) if spots else None
            outcome = "exact" if span else "stale"
        outcomes.append((given, outcome, similarity))
        if outcome == "obsolete":
            continue
        if outcome == "stale":
            kept.append({**c, "stale": today})
            continue
        i, k = span
        c["section"], c["prev"], c["next"] = lines.landmarks(i, k)
        if k:
            fresh = lines.text(i, k)
            if c.get("now") and fresh != c.get("was"):
                c["now"] = rebase_now(c["was"], fresh, c["now"])
            c["was"] = fresh
            start, end = lines.idx[i], lines.idx[i + k - 1] + 1
        else:  # an insertion after content line i - 1
            start = end = lines.idx[i - 1] + 1 if i > 0 else 0
            if i > 0:  # past the end of the block that line is in, unless `now` continues it
                continues = (_strip_markers(c.get("now")).lstrip().startswith("|")
                             and lines.raw[start - 1].lstrip().startswith("|"))
                while not continues and start < len(lines.raw) and lines.raw[start].strip():
                    start = end = start + 1
        c.pop("stale", None)
        c.pop("drifted", None)
        if outcome == "drifted":
            c["drifted"] = f"{today}, similarity {similarity}"
        body = "\n".join(_replace(lines.raw, start, end, c))
        kept.append(c)
    stale = [c for c, outcome, _ in outcomes if outcome == "stale"]
    if stale and pointer:
        body = _add_pointers(body, [c.get("where") or c.get("label") or "part of the paper" for c in stale], pointer)
    return re.sub(r"\n{3,}", "\n\n", body), kept, outcomes


def _add_pointers(body, wheres, pointer):
    """A line for each correction not applied, under the conversion note (a blockquote at
    the top of the body), or at the top when there is none."""
    note = "\n".join(f"> A hand correction of {w} could not be re-applied to this conversion: "
                     f"it is in {pointer}." for w in wheres)
    lead = len(body) - len(body.lstrip("\n"))
    rest = body[lead:]
    if rest.startswith(">"):
        m = re.search(r"\n(?!>)", rest)
        cut = m.start() if m else len(rest)
        return body[:lead] + rest[:cut] + "\n\n" + note + "\n" + rest[cut:]
    return body[:lead] + note + "\n\n" + rest


def _label(lines):
    """The table, figure or equation a block of lines is or captions: "Table 4", "Eq. (3)"."""
    for line in lines:
        m = _LABEL.match(line.lstrip("*_ "))
        if m:
            return f"{m.group(1)} {m.group(2)}"
    for line in lines:
        m = _EQ_TAG.search(line)
        if m:
            return f"Eq. ({m.group(1) or m.group(2)})"
    return ""


def _page(raw, i):
    """The page of raw line i, from the nearest heading above with a (p. N)."""
    for line in reversed(raw[:i + 1]):
        m = re.match(r"#+ .*\((p\. [^)–-]+)", line)
        if m:
            return m.group(1)
    return ""


def _marker_above(lines, j):
    """The marker that covers line j from above: in its block, or above it with at most a
    short block (a caption) between; None if there is none."""
    own, between = True, 0
    for x in reversed(lines[:j]):
        if HAND_EDITED.search(x):
            return x
        if not x.strip():
            own = False
        elif not own:
            between += 1
            if between > 2:
                return None
    return None


def _is_table(line):
    return line.lstrip().startswith(("|", "<table"))


def _block_end(raw, i):
    """The line after the block that starts at raw line i (its blank line, or the end)."""
    while i < len(raw) and raw[i].strip():
        i += 1
    return i


def diff_corrections(base, edited, marked_only=False, why="", where="", by="session", today=None):
    """The hand corrections that turn `base` (a paper body as converted) into `edited`.

    Each run of changed lines is one correction, so an edit of two blocks is two; in a
    table, the changed rows only, unless half its rows or more changed, when the whole
    table is. With `marked_only`, only the runs a hand-edited marker covers (in their
    block, or just above it) are kept: the rest is the converter's own drift. The marker's note, or the comment
    beside it, is the `why` unless one is given.
    """
    today = today or datetime.date.today().isoformat()
    a, b = base.split("\n"), edited.split("\n")
    key = lambda lines: [("\0marker" if is_marker(x) else _norm_line(x)) for x in lines]
    ops = difflib.SequenceMatcher(None, key(a), key(b), autojunk=False).get_opcodes()
    hunks = [[i1, i2, j1, j2] for tag, i1, i2, j1, j2 in ops if tag != "equal"]
    hunks = [h for h in hunks if any(x.strip() for x in a[h[0]:h[1]] + b[h[2]:h[3]])]

    # Changed lines of one block close together (two rows apart at most: three lines, or
    # eight in an HTML table, whose row takes four) are one correction; a table is taken
    # whole when half its lines or more changed.
    groups = []
    for h in hunks:
        block = block_start(a, h[0]) if h[0] < len(a) and a[h[0]].strip() else None
        reach = 8 if block is not None and a[block].lstrip().startswith("<table") else 3
        if groups and block is not None and groups[-1][0] == block and h[0] - groups[-1][1][1] <= reach:
            groups[-1][1][1], groups[-1][1][3] = h[1], h[3]
        else:
            groups.append((block, list(h)))
    by_block, out = {}, []
    for n, (block, h) in enumerate(groups):
        by_block.setdefault(block if block is not None else ("alone", n), []).append(h)
    for block, group in by_block.items():
        if isinstance(block, int) and _is_table(a[block]):
            end = _block_end(a, block)
            changed = sum(max(h[1] - h[0], h[3] - h[2]) for h in group)
            if changed * 2 >= end - block:
                out.append([block, end, group[0][2] - (group[0][0] - block), group[-1][3] + (end - group[-1][1])])
                continue
        out.extend(group)
    corrections, lines = [], BodyLines(base)
    for i1, i2, j1, j2 in sorted(out):
        new = b[j1:j2]
        was, now = "\n".join(a[i1:i2]).strip("\n"), _strip_markers("\n".join(new))
        if not content_lines(was) and not content_lines(now):
            continue  # only a marker: it marks the run below, or an edit the base has already
        marker_lines = [x for x in new if HAND_EDITED.search(x)]
        if not marker_lines:
            above = _marker_above(b, j1)
            marker_lines = [above] if above else []
        if marked_only and not marker_lines:
            continue
        note = why
        if not note:
            for m in marker_lines:
                tagged = re.search(r"<!--\s*hand-edited\s*:\s*(.*?)\s*-->", m, re.S)
                beside = re.findall(r"<!--\s*(.*?)\s*-->", HAND_EDITED_COMMENT.sub("", m), re.S)
                note = (tagged.group(1) if tagged else beside[0] if beside else "").strip()
                if note:
                    break
        content_before = [n for n, idx in enumerate(lines.idx) if idx < i1]
        i = content_before[-1] + 1 if content_before else 0
        k = len(content_lines(was))
        section, prev, nxt = lines.landmarks(i, k) if lines.seq else ("", "", "")
        # A table is labelled by its caption just above or below it; anything else by its
        # own lines, the line before it or the caption above its block.
        top = block_start(a, i1) if i1 < len(a) and a[i1].strip() else i1
        if top < len(a) and _is_table(a[top]):
            bottom = _block_end(a, top)
            near = [x for x in a[max(0, top - 4):top] + a[bottom:bottom + 4] if x.strip()]
            label = _label([x for x in near if re.match(r"[*_ ]*(Table|Tab\.)", x)])
        else:
            caption = [x for x in a[max(0, top - 4):top] if x.strip()][-2:]
            label = _label(a[i1:i2] + new + ([lines.raw[lines.idx[i - 1]]] if i > 0 else []) + caption)
        page = _page(a, i1)
        corrections.append({
            "where": where or ", ".join(x for x in (page, label) if x) or section,
            "why": note, "section": section, "label": label, "prev": prev, "next": nxt,
            "was": was, "now": now, "by": by, "added": today,
        })
    return corrections


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


def paper_index():
    """Map paper file -> frontmatter, for every paper in the library, without reading them all.

    Reading and parsing 2,000 papers takes seconds, and a lookup needs only their
    frontmatter. It is kept in one file in the cache with each paper's size and modification
    time, and only a new or changed paper is read again, and then only its head. The values
    are as JSON holds them: a date is a string. Delete the file to rebuild it.
    """
    saved_at = CACHE_DIR / "index" / f"{LIBRARY_ROOT.name}.json"
    try:
        saved = json.loads(saved_at.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        saved = {}
    saved = saved if saved.get("library") == str(LIBRARY_DIR) else {}
    known, papers, changed = saved.get("papers") or {}, {}, False
    for path in paper_files():
        stat = path.stat()
        stamp = [stat.st_mtime_ns, stat.st_size]
        entry = known.get(str(path))
        if not entry or entry[0] != stamp:
            with open(path, encoding="utf-8") as file:
                head = file.read(8192)
                meta = split_frontmatter(head if _FRONTMATTER.match(head) else head + file.read())[0]
            entry, changed = [stamp, json.loads(json.dumps(meta, default=str))], True
        papers[str(path)] = entry
    if changed or len(papers) != len(known):
        saved_at.parent.mkdir(parents=True, exist_ok=True)
        partial = saved_at.with_suffix(f".{os.getpid()}.tmp")
        partial.write_text(json.dumps({"library": str(LIBRARY_DIR), "papers": papers}, ensure_ascii=False),
                           encoding="utf-8")
        os.replace(partial, saved_at)
    return {Path(path): entry[1] for path, entry in papers.items()}


def library_arxiv_ids():
    """Map arXiv id -> paper file, for every paper in the library that has one."""
    return {str(meta["arxiv"]): path for path, meta in paper_index().items() if meta.get("arxiv")}


def styled(text, *codes):
    """`text` with ANSI codes (1 bold, 2 dim, 32 green, ...) when a person reads it on a terminal.

    Unchanged when the output is piped, redirected or read by a script or an agent, or when
    NO_COLOR is set, so no caller has to strip anything.
    """
    if not codes or not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return text
    return f"\033[{';'.join(map(str, codes))}m{text}\033[0m"


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


def png_without_bad_chunks(data):
    """A PNG without the ancillary chunks (text, metadata) whose checksum is wrong, or None
    if it has none. draw.io rewrites the diagram it keeps in a text chunk but not the
    checksum, and Pillow then refuses the whole image."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    out, i, dropped = [data[:8]], 8, False
    while i + 12 <= len(data):
        n = int.from_bytes(data[i:i + 4], "big")
        chunk = data[i:i + 12 + n]
        kind, body, crc = chunk[4:8], chunk[8:8 + n], chunk[8 + n:]
        if kind[:1].islower() and len(crc) == 4 and int.from_bytes(crc, "big") != zlib.crc32(kind + body):
            dropped = True
        else:
            out.append(chunk)
        i += 12 + n
    return b"".join(out) if dropped else None


SOURCE_IMAGES =(".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".svg")


@functools.lru_cache(maxsize=4)
def source_files(version):
    """The image, PDF and TeX files of a paper's arXiv source (its e-print): {path: bytes}."""
    data = fetch(f"https://arxiv.org/e-print/{version}")
    files = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data or b""), mode="r:*") as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.lower().endswith(SOURCE_IMAGES + (".pdf", ".tex")):
                    files[member.name.removeprefix("./")] = tar.extractfile(member).read()
    except tarfile.TarError:
        pass
    return files


def source_images(version):
    """The image files of a paper's arXiv source: {path: bytes}."""
    return {path: data for path, data in source_files(version).items() if path.lower().endswith(SOURCE_IMAGES)}


def _tex_group(text, i):
    """The end (just past its "}") of the brace group opening at text[i], or None."""
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{" and text[j - 1] != "\\":
            depth += 1
        elif text[j] == "}" and text[j - 1] != "\\":
            depth -= 1
            if not depth:
                return j + 1
    return None


def tex_resolved(text):
    """TeX source with its simple switches resolved: `\\ifthenelse{\\boolean{x}}{a}{b}` (x
    set by `\\setboolean`) and `\\ifx a \\else b \\fi` (x declared by `\\newif`, set by
    `\\xtrue`); the last setting in the text wins, and a switch never set is false. Comments
    are dropped first. Enough to tell which of two figure directories the paper uses."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    booleans = {m.group(1): m.group(2) == "true"
                for m in re.finditer(r"\\setboolean\{(\w+)\}\{(true|false)\}", text)}
    pattern = re.compile(r"\\ifthenelse\s*\{\s*\\boolean\{(\w+)\}\s*\}\s*")
    while m := pattern.search(text):
        first = m.end()
        end_a = _tex_group(text, first) if text[first:first + 1] == "{" else None
        rest = end_a and end_a + len(text[end_a:]) - len(text[end_a:].lstrip())
        end_b = _tex_group(text, rest) if end_a and text[rest:rest + 1] == "{" else None
        if not end_b:
            break
        taken = text[first + 1:end_a - 1] if booleans.get(m.group(1)) else text[rest + 1:end_b - 1]
        text = text[:m.start()] + taken + text[end_b:]
    for name in re.findall(r"\\newif\s*\\if(\w+)", text):
        sets = re.findall(rf"\\{name}(true|false)\b", text)
        on = bool(sets) and sets[-1] == "true"
        text = re.sub(rf"\\if{name}\b(.*?)(?:\\else(.*?))?\\fi",
                      lambda m: m.group(1) if on else m.group(2) or "", text, flags=re.S)
    return text


def source_figure(version, name):
    """A figure of arXiv's HTML (`name`, as its rendering links it) found in the paper's
    LaTeX source: the file at that path; else one with that path or file name and another
    extension, in any directory (LaTeXML links `figs/6_diff.pdf` as `6_diff.png`). A PDF
    is rendered to PNG. Where several different files fit, the one in a directory the TeX
    names once its switches are resolved (an author's colour variants); None when that
    does not settle it."""
    files = source_files(version)
    if name.lower().endswith(SOURCE_IMAGES) and name in files:
        return files[name]
    stem = name.rsplit(".", 1)[0]
    kinds = [p for p in files if p.lower().endswith(SOURCE_IMAGES + (".pdf",))]
    found = [p for p in kinds if p.rsplit(".", 1)[0] == stem] \
        or [p for p in kinds if p.rsplit("/", 1)[-1].rsplit(".", 1)[0] == stem.rsplit("/", 1)[-1]]
    distinct = {files[p]: p for p in sorted(found)}
    if len(distinct) > 1:
        tex = "\n".join(tex_resolved(files[p].decode("utf-8", "replace")) for p in files if p.endswith(".tex"))
        def named_in_tex(path):
            # The directory, or its last parts (under a \graphicspath), as a whole path.
            parts = path.split("/")[:-1]
            return any(re.search(rf"(?<![\w.-]){re.escape('/'.join(parts[k:]))}/", tex) for k in range(len(parts)))

        named = [p for p in distinct.values() if named_in_tex(p)]
        distinct = {files[p]: p for p in named} if len(named) == 1 else {}
    if len(distinct) != 1:
        return None
    path = next(iter(distinct.values()))
    return render_pdf_figure(files[path]) if path.lower().endswith(".pdf") else files[path]


def render_pdf_figure(data):
    """The first page of a PDF figure as PNG, its longer side FIGURE_MAX_SIDE; None if it
    does not open."""
    import pymupdf

    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            page = doc[0]
            zoom = FIGURE_MAX_SIDE / max(page.rect.width, page.rect.height)
            return page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False).tobytes("png")
    except Exception:
        return None


def localize_figures(body, save, pause=0.2):
    """Download every arXiv-hosted figure in a markdown body.

    A raster image goes through to_webp and then `save(data, "webp")`; an SVG
    is passed on unchanged as `save(data, "svg")`, unless it is larger than
    SVG_MAX_BYTES, when it is rasterized to WebP. `save` writes the file and
    returns the link to put in its place.

    arXiv's rendering links some files its server lacks or serves cut off, so a
    figure that will not decode is taken from the cache's copy downloaded again
    (it may predate the checks on downloads), then from the paper's LaTeX source
    (source_figure: under the same path or file name, a PDF rendered), then with a
    PNG's bad text chunks dropped. One that fails
    all of them keeps an absolute arXiv link: a cut-off file is not decoded as far
    as it goes, since the missing part would read as part of the figure.
    Returns (new body, number failed).
    """
    saved, failed = {}, set()

    def store(data):
        if is_svg(data) and len(data) > SVG_MAX_BYTES:
            try:
                return save(svg_to_webp(data), "webp")
            except Exception:
                return save(data, "svg")
        if is_svg(data):
            return save(data, "svg")
        return save(to_webp(data), "webp")

    def copies(path):
        url = f"https://arxiv.org/html/{path}"
        cached = cache_path(url)
        was_cached = bool(cached and cached.exists())
        data = fetch(url)
        time.sleep(pause)
        yield data
        if was_cached:
            data = fetch(url, fresh=True)
            time.sleep(pause)
            yield data
        version, _, name = path.partition("/")
        yield source_figure(version, name)

    def localize(path):
        tried = []
        for data in copies(path):
            if not data:
                continue
            tried.append(data)
            try:
                return store(data)
            except Exception:
                pass
        for data in filter(None, map(png_without_bad_chunks, tried)):
            try:
                return store(data)
            except Exception:
                pass
        return None

    def replace(m):
        path = m.group(2)
        if path not in saved:
            saved[path] = localize(path)
            if saved[path] is None:
                failed.add(path)
        return m.group(1) + (saved[path] or f"https://arxiv.org/html/{path}")

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
