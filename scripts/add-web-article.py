#!/usr/bin/env python3
"""Add a paper published as a web article (Distill, transformer-circuits.pub, a blog post).

    ./scripts/add-web-article.py <url> <topic> [--title "..."] [--authors "A; B"]
                                 [--published YYYY-MM-DD] [--force]

Writes the same pair of files as the other add scripts:

    $PDF_ROOT/<topic>/<Title>.pdf     the page printed by headless Chrome, for the reader
    library/<topic>/<Title>.md        the article as markdown, for the agent

1. Chrome renders the page (scripts run, so the maths and lazily loaded parts are
   in the DOM) and dumps it.
2. Defuddle extracts the article and writes it as markdown (web/to-markdown.mjs,
   chosen in experiments/web-articles): maths as TeX, footnotes as footnotes. No
   images are kept; the markdown says so at the top and links to the original,
   where an agent can look at a figure or an interactive part.
3. Chrome prints the page to the PDF, unless a PDF is there already: the reader's
   highlights live in it.

The frontmatter says `source: web`. Title, authors and date come from the
page's metadata when it has them; the options override them. With --force, an
article already in the library is converted again and keeps its frontmatter.
"""

import copy
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import lxml.html

from paperlib import CONFIG, LIBRARY_DIR, PDF_ROOT, load_topics, read_paper, render_frontmatter, title_to_filename

SCRIPTS = Path(__file__).resolve().parent
WEB = SCRIPTS / "web"
# Headless Chrome prints the page to PDF and dumps its rendered DOM. Set
# `chrome:` in paper-library.yaml (or $CHROME) where it is installed elsewhere.
CHROME = (os.environ.get("CHROME") or CONFIG.get("chrome")
          or shutil.which("google-chrome") or shutil.which("chromium")
          or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
# Headless Chrome announces itself as "HeadlessChrome", which Cloudflare-fronted
# blogs (Medium, the Netflix Tech Blog) answer with a bot check; a desktop
# user agent gets the article.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
BOT_CHECK = re.compile(r"Attention Required! \| Cloudflare|Just a moment\.\.\.|Access denied")


def chrome(url, *args):
    """Run headless Chrome and return its stdout.

    Chrome writes the dump (or the PDF) once the virtual-time budget is spent,
    but pages with animations keep it running afterwards, so it is stopped
    after a fixed wait and whatever it wrote is kept.
    """
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
             f"--user-data-dir={profile}", f"--user-agent={USER_AGENT}",
             "--virtual-time-budget=20000", *args, url],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        )
        try:
            out, _ = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, _ = proc.communicate()
        return out


def meta(doc, *names):
    for name in names:
        for attr in ("name", "property"):
            vals = [m.get("content") for m in doc.xpath(f'//meta[@{attr}="{name}"]') if m.get("content")]
            if vals:
                return vals
    return []


def front_matter(doc):
    for s in doc.xpath('//d-front-matter/script[@type="text/json"]'):
        try:
            return json.loads(s.text or "{}")
        except json.JSONDecodeError:
            pass
    return {}


def to_markdown(dom, url):
    """The rendered page's article as markdown, by Defuddle (installed on first use)."""
    if not shutil.which("node"):
        sys.exit("error: add-web needs Node.js (https://nodejs.org) for its converter")
    if not (WEB / "node_modules").is_dir():
        subprocess.run(["npm", "ci", "--prefix", str(WEB), "--no-audit", "--no-fund"], check=True,
                       stdout=subprocess.DEVNULL)
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8") as page:
        page.write(dom)
        page.flush()
        done = subprocess.run(["node", str(WEB / "to-markdown.mjs"), page.name, url],
                              capture_output=True, text=True)
    if done.returncode != 0 or not done.stdout.strip():
        sys.exit(f"error: the converter failed on {url}: {done.stderr.strip()[-300:]}")
    for line in done.stderr.splitlines():
        if line.startswith("warning:"):
            print(line, file=sys.stderr)
    return done.stdout


def main(argv):
    opts = {"--title": None, "--authors": None, "--published": None}
    force = "--force" in argv
    args = [a for a in argv if a != "--force"]
    for k in opts:
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    url, topic = args
    if topic not in load_topics():
        sys.exit(f"error: '{topic}' is not a folder in catalog/topics.yaml; declare it there first")

    print(f"Rendering {url} ...")
    dom = chrome(url, "--dump-dom")
    if len(dom) < 1000:
        sys.exit("error: Chrome returned no page")
    doc = lxml.html.fromstring(dom)
    if BOT_CHECK.search(doc.findtext(".//title") or ""):
        sys.exit(f"error: the site answered with a bot check ({doc.findtext('.//title').strip()})")
    fm = front_matter(doc)
    title = opts["--title"] or fm.get("title") or (meta(doc, "citation_title", "og:title") or [None])[0] \
        or (doc.findtext(".//title") or "").strip()
    authors = [a.strip() for a in opts["--authors"].split(";")] if opts["--authors"] else \
        meta(doc, "citation_author", "article:author") or \
        [a.get("author") or a.get("name") for a in fm.get("authors", []) if isinstance(a, dict)]
    published = opts["--published"] or (meta(doc, "article:published", "article:published_time",
                                              "citation_publication_date",
                                              "citation_date") or [fm.get("publishedDate")])[0]
    authors = [a for a in authors if a and not a.startswith("http")] or \
        [a for a in meta(doc, "author") if not a.startswith("http")]  # Medium: article:author is a URL
    # transformer-circuits.pub: a byline block (class "d-byline") with "authors" and
    # "published" parts; older pages have class="author" elements and an
    # "article-header" with "Published" followed by e.g. "Dec 22, 2021".
    byline = doc.xpath('//*[contains(concat(" ", @class, " "), " d-byline ")]')
    if not authors:
        names = [e.text_content() for e in doc.xpath('//*[contains(concat(" ", @class, " "), " author ")]')]
        if not names and byline:
            for part in byline[0].xpath('.//*[contains(concat(" ", @class, " "), " authors ")]'):
                part = copy.deepcopy(part)  # the byline stays intact for the article body
                for h in part.xpath(".//h3"):
                    h.drop_tree()
                for br in part.xpath(".//br"):
                    br.tail = ", " + (br.tail or "")
                names = part.text_content().split(",")
        names = [" ".join(n.split()).strip(" ,*∗†‡") for n in names]
        authors = list(dict.fromkeys(n for n in names if n))
    if not published:
        header = doc.xpath("//*[contains(@class, 'article-header')]") + byline
        text = " ".join(" ".join(e.text_content().split()) for e in header)
        m = re.search(r"Published\s+([A-Z][a-z]+) (\d{1,2})(?:st|nd|rd|th)?, (\d{4})", text)
        for fmt in ("%b %d %Y", "%B %d %Y"):
            try:
                published = datetime.datetime.strptime(" ".join(m.groups()), fmt).date().isoformat() if m else None
                break
            except ValueError:
                continue
    published = str(published or "").replace("/", "-")
    # "Last, First" (citation_author) -> "First Last"
    authors = [" ".join(reversed(a.split(", ", 1))) if a and a.count(",") == 1 else a for a in authors]
    if not title:
        sys.exit("error: no title found; pass --title")
    stem = title_to_filename(title)
    md_path = LIBRARY_DIR / topic / f"{stem}.md"
    pdf_path = PDF_ROOT / topic / f"{stem}.pdf"
    if md_path.exists() and not force:
        sys.exit(f"skip (exists): {md_path}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    text = to_markdown(dom, url).strip() + "\n"
    note = (f"> **A web article** ({url}), converted to markdown without its figures and interactive "
            f"parts; open the original for them.\n\n")
    meta_block = {
        "title": title,
        "authors": [a for a in authors if a] or None,
        "published": datetime.date.fromisoformat(str(published)[:10]) if published and
        re.match(r"\d{4}-\d{2}-\d{2}", str(published)) else None,
        "url": url,
        "source": "web",
        "summary": "",
        "added": datetime.date.today(),
    }
    meta_block = {k: v for k, v in meta_block.items() if v is not None}
    if md_path.exists():  # --force: converted again, its frontmatter kept
        meta_block = read_paper(md_path)[0] or meta_block
    # The article usually carries its own title as a heading; add one only if not.
    heading = "" if re.search(r"^#\s+\S", text[:2000], re.M) else f"# {title}\n\n"
    md_path.write_text(render_frontmatter(meta_block) + "\n" + heading + note + text, encoding="utf-8")

    if pdf_path.exists():
        print(f"kept (exists): {pdf_path}")
    else:
        print("Printing PDF ...")
        chrome(url, f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer")
        if not pdf_path.exists() or pdf_path.read_bytes()[:5] != b"%PDF-":
            sys.exit(f"error: Chrome did not print a PDF for {url}")
    print(f"Done: {pdf_path}\n      {md_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
