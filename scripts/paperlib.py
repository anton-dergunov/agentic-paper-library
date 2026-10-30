#!/usr/bin/env python3
"""Shared helpers for the library scripts: paths, the catalog, frontmatter, the
text layer, arXiv metadata and downloads.

Also usable from the shell scripts:

    paperlib.py frontmatter-arxiv <meta.xml> <arxiv-id> <source>
    paperlib.py frontmatter-manual <title> <source> [<url>]
    paperlib.py text-layer <paper.pdf>
    paperlib.py text-paper <paper.txt> <paper.pdf> < frontmatter
    paperlib.py find-arxiv <arxiv-id>
    paperlib.py set-summary <paper> <summary>
    paperlib.py filename <title>
    paperlib.py set-type <paper> <type>
    paperlib.py fetch <url> <out-file>
    paperlib.py shell-config

The first two print a complete YAML frontmatter block (with the --- fences) to
stdout, and text-layer prints a PDF's text layer as a paper file holds it;
text-paper writes a paper file from the frontmatter piped to it and the PDF, as
the add scripts do; find-arxiv prints the paper file of an arXiv id, or an empty
line. set-summary and set-type rewrite
the paper's `summary:` or `type:` field in place; filename prints the filename
stem for a title; fetch downloads a URL with fetch()'s retries, writing an empty
file on 404 or repeated failure; shell-config prints the library's paths as
shell assignments for config.sh, and fails outside a library.
"""

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

# The engine: these scripts, the skills and the guide. Everything a library
# holds is found from the library root instead (see below).
SCRIPTS_DIR = Path(__file__).resolve().parent
ENGINE_ROOT = SCRIPTS_DIR.parent

# A library is a folder with a paper-library.yaml at its root (usually its own
# git repository): the papers' text, the catalog, notes and reviews live under
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


# Scripts that need no library (filename, the tests) work outside one; the paths
# below then point into the working directory, unused.
IN_LIBRARY = find_library_root()
CONFIG = load_config(IN_LIBRARY)
LIBRARY_ROOT = _BASE = IN_LIBRARY or Path.cwd()

# The papers as the agent reads them (committed), and the PDFs (kept outside git,
# often in a synced folder). The two trees mirror each other. Environment variables
# override the config, e.g. on a machine where the PDFs are mounted elsewhere.
LIBRARY_DIR = Path(os.environ.get("LIBRARY_DIR") or _path(CONFIG.get("library", "library"), _BASE))
PDF_ROOT = Path(os.environ.get("PDF_ROOT") or _path(CONFIG.get("pdf_root", "pdfs"), _BASE))
# A link inside the library root that points at PDF_ROOT (a symlink made by
# `paperlib init`, kept out of git), so an editor opened on the library shows
# both trees and the indexes link each paper's PDF with a relative path. Off
# unless `pdf_link:` names it in the config.
PDF_LINK_DIR = _path(CONFIG["pdf_link"], _BASE) if CONFIG.get("pdf_link") else None
# The saved index of the papers' frontmatter and the log of `paperlib read`, shared by
# every library.
CACHE_DIR = Path(os.environ.get("PAPERS_CACHE") or _path(CONFIG.get("cache", "~/.cache/papers"), _BASE))
# Hand-maintained data the scripts read: the declared topic tree and the papers
# deliberately not added.
CATALOG_DIR = _path(CONFIG.get("catalog", "catalog"), _BASE)
TOPICS_FILE = CATALOG_DIR / "topics.yaml"
SKIPPED_FILE = CATALOG_DIR / "skipped.yaml"
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
FIELDS = ["title", "authors", "published", "arxiv", "url", "source", "type", "text-layer", "summary", "added"]
REQUIRED = ["title", "source", "summary", "added"]
# `pdf`: the paper file holds the PDF's text layer. `web`: an article published as a web
# page, its file holds the page converted to markdown, and its PDF is the page printed.
SOURCES = {"pdf", "web"}
# Kind of paper, set by the overview skill when it classifies one (optional).
TYPES = {"method", "survey", "benchmark", "study", "system", "position", "theory"}
# `text-layer: broken` marks a paper whose text layer cannot be read (a scan, a garbled
# font): the agent reads its PDF pages instead.
TEXT_LAYER_STATES = {"broken"}
# A paper file is <stem>.txt (the text layer) or <stem>.md (a web article).
PAPER_SUFFIXES = (".txt", ".md")

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def paper_files(root=None):
    """Every paper file under the library: text layers and web articles, not the indexes."""
    root = Path(root or LIBRARY_DIR)
    return sorted(p for suffix in PAPER_SUFFIXES for p in root.rglob("*" + suffix) if p.name != "README.md")


def paper_file_for(path):
    """The paper file at a path under the library with any suffix (or none): the .txt or
    .md that exists, else the .txt it would be."""
    path = Path(path)
    bare = path.with_name(paper_stem(path))
    for suffix in PAPER_SUFFIXES:
        if bare.with_name(bare.name + suffix).exists():
            return bare.with_name(bare.name + suffix)
    return bare.with_name(bare.name + ".txt")


def pdf_path_for(paper):
    """The PDF that mirrors a paper file."""
    rel = Path(paper).resolve().relative_to(LIBRARY_DIR.resolve())
    return PDF_ROOT / rel.parent / (paper_stem(rel) + ".pdf")


def split_frontmatter(text):
    """Return (frontmatter dict, body) for a paper's text; ({}, text) if none."""
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def read_paper(path):
    """Return (frontmatter dict, body) for a paper file; ({}, text) if none."""
    return split_frontmatter(Path(path).read_text(encoding="utf-8"))


def text_layer(pdf):
    """A PDF's text layer as a paper file holds it: `pdftotext -layout`, with a line
    "[page N]" where page N starts (experiments/reading-formats). Two-column pages keep
    their columns side by side. Raises RuntimeError when pdftotext fails or is missing."""
    text = _pdftotext(pdf)
    # Pages are split at form feeds; a glyph the PDF maps to one would shift every later
    # page number, so the count is checked, and such a PDF is read a page at a time.
    count = page_count(pdf)
    if count and len(_pages(text)) != count:
        return "".join("[page %d]\n%s\n" % (n, _pdftotext(pdf, n).replace("\f", " ").rstrip("\n") + "\n")
                       for n in range(1, count + 1))
    return pages_text(text)


def _pdftotext(pdf, page=None):
    pages = ["-f", str(page), "-l", str(page)] if page else []
    try:
        done = subprocess.run(["pdftotext", "-layout", *pages, str(pdf), "-"], capture_output=True)
    except FileNotFoundError:
        raise RuntimeError("pdftotext is not installed (it comes with poppler: brew install poppler)")
    if done.returncode != 0:
        raise RuntimeError(f"pdftotext failed on {pdf}: {done.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return done.stdout.decode("utf-8", "replace")


def page_count(pdf):
    """A PDF's number of pages by pdfinfo, or None when it cannot tell."""
    done = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, errors="replace")
    m = re.search(r"^Pages:\s+(\d+)", done.stdout, re.M)
    return int(m.group(1)) if m else None


def _pages(text):
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pages_text(text):
    """pdftotext's output, pages separated by form feeds, with a "[page N]" line before each."""
    return "".join("[page %d]\n%s\n" % (n, page) for n, page in enumerate(_pages(text), 1))


PAGE_MARK = re.compile(r"^\[page (\d+)\]$", re.M)


def text_quality(text):
    """Why a text layer looks unreadable ("no text", "12% unmapped glyphs"), or "" when it
    looks fine. A PDF without a text layer (a scan) gives pages of nothing; a font without
    a character map gives "\ufffd" for its glyphs. A figure's labels or a few formulas in
    such a font leave the prose readable: in the author's library of 2,256 PDFs the most
    was 1.3%, in clumps beside clean text."""
    body = PAGE_MARK.sub("", text)
    letters = sum(c.isalnum() for c in body)
    pages = max(1, len(PAGE_MARK.findall(text)))
    if letters < 200 * pages * 0.2:
        return "no text"
    unmapped = body.count("\ufffd") / max(1, letters)
    return f"{unmapped:.0%} unmapped glyphs" if unmapped > 0.05 else ""


def write_text_paper(path, meta, pdf):
    """Write a paper file: `meta` as frontmatter, then the PDF's text layer. A text layer
    that looks unreadable (text_quality) is marked `text-layer: broken`, with a warning,
    so that an agent reads the PDF's pages. A mark already there stays: a text layer can be
    garbled in ways no check sees, and a person who marked it knows. Returns the reason,
    or ""."""
    text = text_layer(pdf)
    meta, problem = dict(meta), text_quality(text)
    if problem:
        meta["text-layer"] = "broken"
        print(f"warning: the text layer of {Path(pdf).name} looks unreadable ({problem}): "
              "marked `text-layer: broken`, so its PDF pages are read instead", file=sys.stderr)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    write_paper(path, meta, text)
    return problem


# The word that heads a reference list, also in small capitals, which the text layer spaces
# out ("R EFERENCES"); and what may stand before it on its line: a section number, and in
# two columns the other column's text, three spaces or more away.
_REFERENCES_WORD = re.compile(r"References|REFERENCES|R EFERENCES|Bibliography|BIBLIOGRAPHY|B IBLIOGRAPHY")
_SECTION_NUMBER = re.compile(r"[ \t]*(?:[\dA-Z]{1,2}\.?[ \t]+)?")
_AFTER_COLUMN = re.compile(r".*[ \t]{3}[ \t]*(?:[\dA-Z]{1,2}\.?[ \t]+)?")
# Where in the text a reference list may start: a long appendix can put it at a tenth of the
# paper. A heading counts only when years follow it, as they do in any reference list: the
# word alone is also a figure's label (WebGPT's example answers, a diagram's legend).
_REFERENCES_FROM = 0.1
_YEAR = re.compile(r"\b(?:19|20)\d\d\b")


def _reference_cut(body):
    """Where the main text of a text layer ends, and whether the whole reference list goes
    with what follows it: (offset, True) at a reference heading at the left margin, alone on
    its line or with the other column's text beside it, since everything after it on the page
    is references; (offset, False) after the page of a heading in the right column, whose
    left column below it is still main text; None when there is none.

    Found by the word, then its line checked: a pattern over the whole text backtracks on
    the long runs of spaces two columns leave."""
    for m in _REFERENCES_WORD.finditer(body, int(len(body) * _REFERENCES_FROM)):
        start = body.rfind("\n", 0, m.start()) + 1
        end = body.find("\n", m.end())
        end = len(body) if end < 0 else end
        before, after = body[start:m.start()], body[m.end():end]
        if after.strip() and not after.startswith("   "):
            continue  # "References" in a sentence, or a title like "References in Context"
        indent = len(before) - len(before.lstrip())
        if len(_YEAR.findall(body, end, end + 4000)) < 5:
            continue
        if _SECTION_NUMBER.fullmatch(before) and indent < 10:
            return start, True
        if _AFTER_COLUMN.fullmatch(before) or (_SECTION_NUMBER.fullmatch(before) and not after.strip()):
            following = PAGE_MARK.search(body, end)
            return (following.start() if following else len(body)), False
    return None


_MD_REFERENCES = re.compile(r"^#{1,3} +(References|Bibliography|REFERENCES)\b.*$", re.M)


def text_view(meta, body, appendix=False):
    """A paper as a reader needs it: the main text, without the reference list and what
    follows it, ending with a line that says what was left out (so a reader does not report
    the missing appendices as lost).

    The cut is at the reference heading when it stands alone on its line; in two columns,
    where it shares a line with the other column or sits in the right one, after the page it
    is on, whichever comes first. A heading in the first tenth of the text does not count.
    With `appendix`, nothing is cut: a paper whose main results are in its appendix is read
    whole. A web article (markdown) is cut at its references heading the same way.
    """
    title = " ".join(str(meta.get("title") or "").split())
    head = f"# {title}\n\n"
    if appendix:
        return head + body.rstrip() + "\n\n[The whole paper: nothing was left out.]\n"
    if meta.get("source") == "web":
        cut = [m for m in _MD_REFERENCES.finditer(body) if m.start() > len(body) // 3]
        if not cut:
            return head + body.rstrip() + "\n\n[No references heading found: this is the whole article.]\n"
        return head + body[:cut[0].start()].rstrip() + "\n\n[End of the main text. Left out: the references and what follows them.]\n"
    found = _reference_cut(body)
    if not found or found[0] >= len(body.rstrip()):
        return head + body.rstrip() + "\n\n[End of the text layer. Nothing was left out: no reference list was found.]\n"
    cut, alone = found
    dropped = len(PAGE_MARK.findall(body[cut:]))
    what = "the references" if alone else "the rest of the references"
    return (head + body[:cut].rstrip() + "\n\n[End of the main text. Left out: %s and whatever follows them, %d page%s.]\n"
            % (what, dropped, "s" * (dropped != 1)))


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


def fetch(url, attempts=4):
    """GET a URL and return its body as bytes, or None on 404 or repeated failure.

    Downloads go through curl, like the add scripts: arXiv answers Python's own HTTP
    client with 406 at times. Throttled requests (errors or an empty body) are retried
    with backoff.
    """
    return download(url, attempts)


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


def review_scopes():
    """The areas to read and review, in their order: [(group, [scope, ...])], group "" when the
    config lists no groups (`review_scopes` in paper-library.yaml; without it, the top-level
    folders)."""
    declared = CONFIG.get("review_scopes")
    if not declared:
        tops = sorted({t.split("/")[0] for t in load_topics()})
        return [("", tops)]
    groups, loose = [], []
    for item in declared:
        if isinstance(item, dict):
            groups += [(str(name), [str(s).strip("/") for s in scopes or []]) for name, scopes in item.items()]
        else:
            loose.append(str(item).strip("/"))
    return ([("", loose)] if loose else []) + groups


def ask_model(model, system, prompt, effort=None):
    """One request to a Claude model through `claude -p`, with no tools.

    Returns (reply text, usage dict); raises RuntimeError on failure. The usage's `input` is
    all input tokens, of which `cache_write` were written to the prompt cache and
    `cache_read` read from it; `thinking` is the part of `output` spent thinking.

    The environment keeps the user's CLAUDE.md files and background requests out of the
    request: they are about 800 of its 1,400 fixed tokens (experiments/prompt-trim). It also
    keeps the cache to five minutes: `claude -p` writes the whole request, the paper too, to
    the cache, and a one-hour write costs twice the input price where a five-minute one costs
    1.25 times (docs/design.md).
    """
    env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
           "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "FORCE_PROMPT_CACHING_5M": "1"}
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", system,
             "--output-format", "json", "--no-session-persistence"]
            + (["--effort", effort] if effort else []),
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
        "output": usage.get("output_tokens", 0), "usd": reply.get("total_cost_usd"),
        "cache_write": usage.get("cache_creation_input_tokens", 0) or 0,
        "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
        "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0}


# The effort of `paperlib add` and `paperlib info`'s requests, set here rather than left to
# the user's Claude Code setting. Not measured: it is the level they ran at until now.
FILING_EFFORT = "high"


def filing_prompts(topics):
    """(system prompt, paper template) for a filing request: guide/filing-prompt.md.

    The rules and the topic tree are the system prompt, the same for every paper of a run,
    so the requests after the first read them from the prompt cache. The template takes
    `title` and `abstract`.
    """
    rules, the_paper = (ENGINE_ROOT / "guide" / "filing-prompt.md").read_text(encoding="utf-8").split("THE PAPER")
    tree = "\n".join(f"{folder}: {scope}" for folder, scope in topics.items())
    # A few summaries already in the library, spread over it, for the model to match.
    summaries = [s for s in (" ".join(str(meta.get("summary") or "").split())
                             for meta in paper_index().values()) if s]
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
    return NOTES_DIR / f"{paper_stem(paper)}.md"


def _note_head(paper):
    """A paper's note split at its digest: (the lines above it, what follows "## Digest").
    The digest is None when the note has none, and both are None when there is no note."""
    note = note_path(paper)
    if not note.exists():
        return None, None
    head, _, digest = note.read_text(encoding="utf-8").partition("\n## Digest")
    return head, (digest if _ else None)


def has_digest(paper):
    """Whether a paper (a path or a stem) has been read: its note holds a digest."""
    return _note_head(paper)[1] is not None


# The fields a reading writes above the digest (guide/reading-prompt.md), one per line.
_NOTE_FIELD = re.compile(r"^(type|family|evidence):[ \t]*(.*?)[ \t]*$", re.M)


_DIGEST_END = re.compile(r"^## ", re.M)


def read_note(paper):
    """A paper's note in one read, or None when it has none: {"fields": note_fields', "digest":
    the digest's text (up to the next `## ` section; None when the note has no digest),
    "reread": reread_reason's}."""
    head, digest = _note_head(paper)
    if head is None:
        return None
    if digest is not None:
        end = _DIGEST_END.search(digest)
        digest = (digest[:end.start()] if end else digest).strip("\n")
    reread = _REREAD.search(head)
    return {"fields": _fields(head), "digest": digest, "reread": reread.group(1).strip() if reread else ""}


def note_fields(paper):
    """What the note's head says of a paper: {type, family, evidence}, the ones it holds,
    or {} when the paper has no note. A type outside TYPES is left out."""
    return _fields(_note_head(paper)[0] or "")


def _fields(head):
    fields = {}
    for name, value in _NOTE_FIELD.findall(head):
        if value and name not in fields:
            fields[name] = value
    if fields.get("type", "").lower() not in TYPES:
        fields.pop("type", None)
    else:
        fields["type"] = fields["type"].lower()
    return fields


# A note to read again: "reread: <why> (<date>)" among the lines above its digest, set by
# `paperlib reread`. Reading the paper again writes a new note, which drops it.
_REREAD = re.compile(r"^reread: (.*)$", re.M)


def reread_reason(paper):
    """Why a paper's note is to be read again, or "" when it is not."""
    m = _REREAD.search(_note_head(paper)[0] or "")
    return m.group(1).strip() if m else ""


def flag_reread(paper, reason=None, today=None):
    """Mark a paper's note to be read again (reason None takes the mark off). Returns
    False when the paper has no note with a digest, which a reading will write anyway."""
    head, digest = _note_head(paper)
    if digest is None:
        return False
    note = note_path(paper)
    head = _REREAD.sub("", head).rstrip("\n")
    head = re.sub(r"\n{3,}", "\n\n", head)
    if reason:
        reason = " ".join(str(reason).split())
        head += f"\nreread: {reason} ({today or datetime.date.today().isoformat()})"
    note.write_text(head + "\n\n## Digest" + digest, encoding="utf-8")
    return True


def paper_stem(paper):
    """The stem a paper is keyed by in notes/: a path's stem, or a stem as given (titles hold
    dots, so a bare stem is never split at one). NFC, as a synced folder may hand back a
    title in another Unicode form."""
    text = unicodedata.normalize("NFC", str(paper))
    name = Path(text).name
    for suffix in (*PAPER_SUFFIXES, ".pdf"):
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


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
    links, which resolve to the paper's file. Web links and in-page anchors are
    left out.
    """
    from urllib.parse import unquote, urlsplit

    out = []
    text = Path(path).read_text(encoding="utf-8")
    # Definitions nothing refers to are checked as well, so a stale one is noticed.
    for target in dict.fromkeys(link_targets(text) + list(link_definitions(text).values())):
        if target.startswith(PDF_LINK_BASE):
            rel = unquote(urlsplit(target).path).lstrip("/")
            resolved = paper_file_for(LIBRARY_DIR / rel)
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
        partial = saved_at.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")  # threads share a pid
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
    elif len(argv) == 3 and argv[1] == "text-layer":
        try:
            sys.stdout.write(text_layer(argv[2]))
        except RuntimeError as e:
            sys.exit(f"error: {e}")
    elif len(argv) == 4 and argv[1] == "text-paper":
        meta = split_frontmatter(sys.stdin.read())[0]
        if not meta:
            sys.exit("error: text-paper reads the paper's frontmatter on stdin, and got none")
        try:
            write_text_paper(argv[2], meta, argv[3])
        except RuntimeError as e:
            sys.exit(f"error: {e}")
    elif len(argv) == 3 and argv[1] == "find-arxiv":
        print(library_arxiv_ids().get(argv[2], ""))
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
