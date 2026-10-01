#!/usr/bin/env python3
"""Add a paper published as a web article (Distill, transformer-circuits.pub, ...).

    ./scripts/add-web-article.py <url> <topic> [--title "..."] [--authors "A; B"]
                                 [--published YYYY-MM-DD] [--force]

Writes the same pair of files as the other add scripts:

    $PDF_ROOT/<topic>/<Title>.pdf     the page printed by headless Chrome
    library/<topic>/<Title>.md        the article converted to markdown
    library/<topic>/images/<Title>-figNN.<ext>

1. Chrome renders the page (scripts run, so figures and math are in the DOM)
   and dumps it; it also prints the page to the PDF for reading.
2. The article body is kept: <d-article> / <dt-article> (Distill and its
   descendants), else <article>, <main> or <body>.
3. Math becomes $...$ / $$...$$: <d-math> holds raw TeX, KaTeX output carries
   its TeX in an annotation. Citations become [key], footnotes are inlined in
   parentheses, and navigation, bibliography and scripts are dropped.
4. Raster images are downloaded as WebP and inline SVG figures saved as files,
   as in the arXiv conversion. Interactive figures (canvas, widgets) cannot be
   kept; the markdown says so at the top and links to the original.

The frontmatter says `source: web`. Title, authors and date come from the
page's metadata when it has them; the options override them.
"""

import base64
import copy
import datetime
import html
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote, urljoin

import lxml.html
from lxml import etree

from paperlib import (
    LIBRARY_DIR, PDF_ROOT, fetch, load_topics, render_frontmatter, title_to_filename, to_webp,
)

SCRIPTS = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Headless Chrome announces itself as "HeadlessChrome", which Cloudflare-fronted
# blogs (Medium, the Netflix Tech Blog) answer with a bot check; a desktop
# user agent gets the article.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
BOT_CHECK = re.compile(r"Attention Required! \| Cloudflare|Just a moment\.\.\.|Access denied")
DROP = ["script", "style", "noscript", "d-bibliography", "d-citation-list", "d-footnote-list",
        "d-contents", "d-title", "d-byline", "d-front-matter", "dt-byline", "dt-bibliography",
        "dt-fn-list", "dt-header", "dt-footer", "d-appendix", "dt-appendix", "nav", "canvas"]
# Blog chrome inside <article>: share buttons and related-post lists (WordPress/Jetpack).
DROP_CLASSES = ["sharedaddy", "sd-sharing", "jp-relatedposts"]

_spec = importlib.util.spec_from_file_location("h2m", SCRIPTS / "html-to-markdown.py")
h2m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h2m)


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


def math_span(tex, display):
    """MathML carrying the TeX as an annotation, which pandoc turns into $...$."""
    math = etree.Element("math", {"display": "block" if display else "inline"})
    semantics = etree.SubElement(math, "semantics")
    etree.SubElement(semantics, "mrow")
    annotation = etree.SubElement(semantics, "annotation", {"encoding": "application/x-tex"})
    annotation.text = tex.strip()
    return math


def replace(el, new):
    new.tail = el.tail
    el.getparent().replace(el, new)


def medium_body(body):
    """The story itself from a Medium page, without the page's widgets.

    Medium marks every block of the story (paragraph, heading, list item,
    caption) with data-selectable-paragraph; claps, follow and share buttons,
    tags and the newsletter box between sections carry no such mark. The
    story is rebuilt from the title and the marked blocks, taking whole
    lists, figures and code blocks around them.
    """
    def is_block(el):
        if el.get("data-testid") == "storyTitle":
            return True
        if el.tag in ("ol", "ul", "figure", "pre", "blockquote"):
            return bool(el.xpath(".//*[@data-selectable-paragraph] | .//img"))
        return el.get("data-selectable-paragraph") is not None and el.tag not in ("li", "figcaption")

    blocks = []
    for el in body.iter():
        if isinstance(el.tag, str) and is_block(el) and not any(a in blocks for a in el.iterancestors()):
            blocks.append(el)
    keep = lxml.html.Element("div")
    for el in blocks:
        el.tail = None
        keep.append(el)  # moves it out of the page; blocks are in document order
    for el in keep.xpath('.//*[contains(concat(" ", @class, " "), " speechify-ignore ")]'):
        el.drop_tree()  # "Press enter or click to view image in full size"
    return keep


def clean(body, base_url):
    for tag in DROP:
        for el in body.xpath(f"//{tag}"):
            el.drop_tree()
    for cls in DROP_CLASSES:
        for el in body.xpath(f'//*[contains(concat(" ", @class, " "), " {cls} ")]'):
            if el.getparent() is not None:
                el.drop_tree()
    # A <div> inside a heading makes pandoc split it into an empty heading and a paragraph.
    for el in body.xpath("(//h1 | //h2 | //h3 | //h4 | //h5 | //h6)//div"):
        el.drop_tag()
    # KaTeX output: the TeX source is in the MathML annotation.
    for el in body.xpath('//span[contains(concat(" ", @class, " "), " katex-display ")]'
                         ' | //span[contains(concat(" ", @class, " "), " katex ")]'):
        if el.getparent() is None:
            continue
        tex = el.xpath('.//annotation[@encoding="application/x-tex"]/text()')
        if tex:
            display = "katex-display" in el.get("class", "")
            replace(el, math_span(tex[0], display))
    for el in body.xpath("//d-math | //dt-math"):
        if el.getparent() is None:
            continue
        inner = el.xpath(".//math")
        if el.tag == "dt-math" and inner:  # already converted from KaTeX above
            el.drop_tag()
            continue
        replace(el, math_span(el.text_content(), el.get("block") is not None))
    for el in body.xpath("//d-cite | //dt-cite"):
        key = el.get("key") or el.get("data-key") or ""
        cite = etree.Element("span")
        cite.text = f"[{key.replace(',', ', ')}]" if key else ""
        replace(el, cite)
    for el in body.xpath("//d-footnote | //dt-fn"):
        note = etree.Element("span")
        note.text = f" ({' '.join(el.text_content().split())})"
        replace(el, note)
    for img in body.xpath("//img[@src]"):
        img.set("src", urljoin(base_url, img.get("src")))
    return body


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
    images_dir = md_path.parent / "images"
    for old in images_dir.glob(f"{stem}-fig*") if images_dir.exists() else []:
        old.unlink()  # from an earlier run (--force)

    body = None
    for tag in ("d-article", "dt-article", "article", "main", "body"):
        found = doc.xpath(f"//{tag}")
        if found:
            body = found[0]
            break
    if doc.xpath("//*[@data-selectable-paragraph]"):
        body = medium_body(body)
    body = clean(body, url)
    article = lxml.html.tostring(body, encoding="unicode")

    counter = 0

    def save(ext, data):
        nonlocal counter
        counter += 1
        name = f"{stem}-fig{counter:02d}.{ext}"
        images_dir.mkdir(parents=True, exist_ok=True)
        (images_dir / name).write_bytes(data)
        return f"images/{quote(name)}"

    def save_svg(mime, data):
        return save("svg", h2m.repair_svg(data.decode("utf-8")).encode("utf-8"))

    article = h2m.extract_svgs(article, save_svg)
    text = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars", "--wrap=none",
         "--lua-filter", str(SCRIPTS / "arxiv-html.lua")],
        input=article, capture_output=True, text=True, check=True,
    ).stdout

    def local(m):
        src = m.group(2)
        if src.startswith("data:image/"):  # inlined, possibly with URL-encoded line breaks
            try:
                data = base64.b64decode(re.sub(r"\s", "", unquote(src.split(",", 1)[1])))
            except (ValueError, IndexError):
                return m.group(0)
        elif src.startswith("http"):
            data = fetch(src)
        else:
            return m.group(0)
        if not data:
            return m.group(0)
        try:
            return m.group(1) + save("webp", to_webp(data)) + m.group(3)
        except Exception:
            ext = src.rsplit(".", 1)[-1].lower()
            return m.group(1) + save(ext if ext in ("png", "jpg", "jpeg", "gif", "svg") else "bin", data) + m.group(3)

    text = re.sub(r'(!\[[^\]]*\]\()([^)\s]+)(\))', local, text)
    text = re.sub(r'(<img\s[^>]*?src=")([^"]+)(")', local, text)

    note = (f"> **Converted from a web article** ({url}). Interactive figures and widgets "
            f"did not survive; open the original for them.\n\n")
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
    # The article usually carries its own title as a heading; add one only if not.
    heading = "" if re.search(rf"^#\s+{re.escape(title)}\s*$", text[:3000], re.M) else f"# {title}\n\n"
    md_path.write_text(render_frontmatter(meta_block) + "\n" + heading + note + text, encoding="utf-8")

    print("Printing PDF ...")
    chrome(url, f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer")
    if not pdf_path.exists() or pdf_path.read_bytes()[:5] != b"%PDF-":
        sys.exit(f"error: Chrome did not print a PDF for {url}")
    subprocess.run([sys.executable, SCRIPTS / "page-map.py", pdf_path, md_path])
    print(f"Done: {pdf_path}\n      {md_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
