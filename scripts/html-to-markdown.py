#!/usr/bin/env python3
"""Convert an arXiv HTML rendering (LaTeXML) into the library's markdown.

    ./scripts/html-to-markdown.py <paper.html> <body.md> <images-dir> <basename>

Writes the paper body (no frontmatter) to <body.md> and any inline figures to
<images-dir>/<basename>-figNN.<ext>. Used by add-arxiv-paper.sh.

1. Keep only the article: arXiv wraps it in <div class="ltx_page_content">;
   everything outside is site navigation.
2. pandoc to GitHub markdown with scripts/arxiv-html.lua, which unwraps
   arXiv's div/span noise so that the few tables markdown cannot express
   (merged cells) come out as HTML tables rather than a "[TABLE]" placeholder.
   Math is written as $...$ and $$...$$, which VS Code, GitHub and Obsidian all
   render (pandoc's default $`...`$ form renders almost nowhere).
3. Figures arXiv inlines as SVG or base64 images become files in images/. The
   SVGs are repaired on the way out: arXiv serves them inside an HTML page, so
   they lack the XML namespaces a standalone .svg needs and the HTML parser
   lowercased their camelCase names (viewBox, foreignObject), which leaves them
   blank in any viewer.
4. Code listings become fenced code blocks, from the exact source LaTeXML
   embeds in each listing (see convert_listings).
5. Raster figures, whether inlined or hosted next to the rendering on arXiv,
   become files in images/ too, downscaled and stored as WebP (see
   paperlib.to_webp). Hosted SVG figures are stored as they are. A hosted
   figure that fails to download keeps a link to arXiv.
6. Figures LaTeXML embeds as <object data="..."> (SVG plots, mostly) become
   <img>s first; pandoc drops <object> elements without a trace.
7. Tables inside \\resizebox or \\scalebox, which LaTeXML writes as <span>s,
   become real tables (see span_tabulars_to_tables).
8. Boxed text (definitions, findings, prompt templates), which LaTeXML draws
   as an SVG frame with the text inside, becomes a quote, and small text
   badges become their text (see picture_text).
9. Trees drawn with the forest package, which LaTeXML cannot render, are
   taken from the paper's LaTeX source as nested lists (see forest_trees).
10. Cross-references LaTeXML could not resolve keep their label as text.
"""

import base64
import functools
import gzip
import html
import html.entities
import io
import re
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import quote
from pathlib import Path

from lxml import etree

from paperlib import fetch, localize_figures, to_webp

FILTER = Path(__file__).with_name("arxiv-html.lua")
EXTS = {"svg+xml": "svg", "png": "png", "jpeg": "jpg", "gif": "gif", "webp": "webp"}

# SVG names that are camelCase in XML but lowercased by an HTML parser
# (the HTML5 spec's "adjust SVG attributes/tag names" tables).
SVG_TAGS = """altGlyph altGlyphDef altGlyphItem animateColor animateMotion
animateTransform clipPath feBlend feColorMatrix feComponentTransfer feComposite
feConvolveMatrix feDiffuseLighting feDisplacementMap feDistantLight feDropShadow
feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge
feMergeNode feMorphology feOffset fePointLight feSpecularLighting feSpotLight
feTile feTurbulence foreignObject glyphRef linearGradient radialGradient
textPath""".split()
SVG_ATTRS = """attributeName attributeType baseFrequency baseProfile calcMode
clipPathUnits diffuseConstant edgeMode filterUnits glyphRef gradientTransform
gradientUnits kernelMatrix kernelUnitLength keyPoints keySplines keyTimes
lengthAdjust limitingConeAngle markerHeight markerUnits markerWidth
maskContentUnits maskUnits numOctaves pathLength patternContentUnits
patternTransform patternUnits pointsAtX pointsAtY pointsAtZ preserveAlpha
preserveAspectRatio primitiveUnits refX refY repeatCount repeatDur
requiredExtensions requiredFeatures specularConstant specularExponent
spreadMethod startOffset stdDeviation stitchTiles surfaceScale systemLanguage
tableValues targetX targetY textLength viewBox viewTarget xChannelSelector
yChannelSelector zoomAndPan""".split()
VOID = "area base br col embed hr img input link meta source track wbr".split()
# An opening tag, skipping over quoted attribute values (which may contain ">").
TAG = re.compile(r"""<([a-zA-Z][\w:.-]*)((?:[^>"']|"[^"]*"|'[^']*')*?)(/?)>""")
# One attribute: a name, optionally "=" and a quoted or bare value.
ATTR = re.compile(r"""\s+([^\s=/>"']+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+))?""")


def fill_valueless_attrs(tag):
    """<a href="x" download> -> <a href="x" download="download">."""
    name, rest, slash = tag.group(1), tag.group(2), tag.group(3)
    attrs = []
    for a in ATTR.finditer(rest):
        value = a.group(2)
        if value is None:
            value = f'"{a.group(1)}"'
        elif value[0] not in "\"'":
            value = f'"{value}"'
        attrs.append(f" {a.group(1)}={value}")
    return f"<{name}{''.join(attrs)}{slash}>"
XML_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}


def extract_article(page):
    start = re.search(r"<div[^>]*\bltx_page_content\b[^>]*>", page)
    if not start:
        sys.exit("error: no ltx_page_content in the HTML — no rendering for this paper?")
    pos, depth = start.end(), 1
    for m in re.finditer(r"<div\b|</div>", page[pos:]):
        depth += -1 if m.group() == "</div>" else 1
        if depth == 0:
            return page[start.start():pos + m.end()]
    sys.exit("error: unbalanced <div> in the arXiv HTML")


def repair_svg(svg):
    """Make an SVG cut out of an HTML page valid as a standalone file."""
    for name in SVG_TAGS:
        svg = re.sub(rf"(</?){name.lower()}(?=[\s/>])", rf"\g<1>{name}", svg)
    for name in SVG_ATTRS:
        svg = re.sub(rf"(\s){name.lower()}=", rf"\g<1>{name}=", svg)
    if 'xmlns="http://www.w3.org/2000/svg"' not in svg[:500]:
        svg = re.sub(
            r"<svg\b",
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"',
            svg,
            count=1,
        )
    # HTML inside <foreignObject> (the figure's text) must be in the XHTML
    # namespace, and any MathML in the MathML namespace, or it isn't drawn.
    svg = re.sub(
        r"(<foreignObject\b[^>]*>\s*<)([a-zA-Z][\w-]*)(?![^>]*\bxmlns=)",
        r'\1\2 xmlns="http://www.w3.org/1999/xhtml"',
        svg,
    )
    svg = re.sub(r"<math\b(?![^>]*\bxmlns=)", '<math xmlns="http://www.w3.org/1998/Math/MathML"', svg)
    # HTML-isms XML rejects: valueless attributes (<a download>), unclosed
    # void elements, and named entities.
    svg = TAG.sub(fill_valueless_attrs, svg)
    svg = re.sub(rf"<({'|'.join(VOID)})\b([^>]*?)(?<!/)>", r"<\1\2/>", svg)
    svg = re.sub(
        r"&([a-zA-Z][a-zA-Z0-9]*);",
        lambda m: m.group(0)
        if m.group(1) in XML_ENTITIES or m.group(1) not in html.entities.name2codepoint
        else f"&#{html.entities.name2codepoint[m.group(1)]};",
        svg,
    )
    return svg


def is_valid_xml(svg):
    try:
        etree.fromstring(svg.encode("utf-8"))
        return True
    except etree.XMLSyntaxError:
        return False


def extract_svgs(article, save):
    """Replace each top-level <svg>...</svg> with an <img> of a saved file.

    Done here rather than left to pandoc because LaTeXML nests pictures (an
    <svg> inside another's <foreignObject>), and pandoc's HTML reader ends the
    outer picture at the inner one's </svg>, truncating the file.

    A picture that is a frame around text (see picture_text) is replaced by
    the text instead.
    """
    out, pos = [], 0
    tokens = re.compile(r"<svg\b|</svg\s*>")
    while True:
        start = re.search(r"<svg\b", article[pos:])
        if not start:
            out.append(article[pos:])
            return "".join(out)
        begin = pos + start.start()
        depth, end = 0, None
        for m in tokens.finditer(article, begin):
            depth += 1 if m.group().startswith("<svg") else -1
            if depth == 0:
                end = m.end()
                break
        if end is None:
            out.append(article[pos:])
            return "".join(out)
        out.append(article[pos:begin])
        out.append(picture_text(article[begin:end], save))
        pos = end


FOREIGN = re.compile(r"<foreignObject\b[^>]*>|</foreignObject\s*>|<svg\b|</svg\s*>", re.I)


def foreign_objects(svg):
    """The inner HTML of each foreignObject of a picture, not of pictures nested in it."""
    found, depth, start = [], 0, None
    fo_depth = 0
    for m in FOREIGN.finditer(svg):
        tag = m.group().lower()
        if tag.startswith("<svg"):
            depth += 1
        elif tag.startswith("</svg"):
            depth -= 1
        elif tag.startswith("<foreignobject"):
            fo_depth += 1
            if depth == 1 and fo_depth == 1:
                start = m.end()
        else:
            fo_depth -= 1
            if depth == 1 and fo_depth == 0 and start is not None:
                found.append(svg[start:m.start()])
                start = None
    return found


def words(html_text):
    """Words of text in an HTML fragment, a formula counting as one."""
    text = re.sub(r"<math\b.*?</math>", " x ", html_text, flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", text).split())


# How the spans LaTeXML writes inside a picture's text read as blocks.
BLOCK_SPANS = {
    "ltx_p": "p", "ltx_item": "p",
    "ltx_para": "div", "ltx_inline-block": "div", "ltx_minipage": "div",
    "ltx_foreignobject_container": "div", "ltx_foreignobject_content": "div",
    "ltx_itemize": "div", "ltx_enumerate": "div", "ltx_description": "div",
    "ltx_logical-block": "div", "ltx_inline-logical-block": "div", "ltx_parbox": "div",
}


def spans_to_blocks(html_text):
    """Turn paragraph and list spans into <p>/<div>, so a box's paragraphs and
    list items stay apart. Inside a list item (a <p>) everything stays inline."""
    stack = []  # closing tag of each open span, and whether it opened an item

    def rename(t):
        if t.group(0).startswith("</"):
            return stack.pop()[0] if stack else t.group(0)
        in_item = any(item for _, item in stack)
        classes = re.search(r'\bclass="([^"]*)"', t.group(1) or "")
        block = None
        if not in_item:
            block = next((BLOCK_SPANS[c] for c in (classes.group(1).split() if classes else [])
                          if c in BLOCK_SPANS), None)
        if not block:
            stack.append(("</span>", False))
            return t.group(0)
        stack.append((f"</{block}>", "ltx_item" in classes.group(1).split()))
        return f"<{block}{t.group(1)}>"

    return SPAN_TAG.sub(rename, html_text)


def picture_kind(svg):
    """What a LaTeXML picture is: "box", "diagram" (a drawing holding a text
    block), "badge" or "image"; see picture_text."""
    blocks = foreign_objects(svg)
    counts = [words(b) for b in blocks]
    total = sum(counts)
    paths = len(re.findall(r"<path\b", svg))
    height = re.match(r"\s*<svg\b[^>]*?\bheight=\"([\d.]+)", svg)
    height = float(height.group(1)) if height else 1000
    if total and total < 8 and len(blocks) <= 2 and paths <= 4 and height < 25:
        return "badge"
    simple_frame = paths <= 6 and len(blocks) <= 4 and total >= 6
    one_block = bool(counts) and max(counts) >= 12 and max(counts) >= 0.6 * total
    if not (simple_frame or one_block):
        return "image"
    return "diagram" if paths > 15 else "box"


def picture_text(svg, save):
    """What to put in the markdown for one LaTeXML picture.

    LaTeX boxes (tcolorbox and the like: definitions, findings, takeaways,
    prompt templates) come out of LaTeXML as an <svg> frame whose text sits in
    <foreignObject>s, so as an image their text would be lost. A picture
    is such a box when its text is mostly one block of at least twelve words,
    or when it is a plain frame (a few shapes) around a few blocks of text: it
    becomes a quote, its title (a short first block) in bold. Drawn with more
    than a few shapes, it is a diagram that holds a text block, and the image
    is kept too. A tiny picture holding a few words (a badge such as
    "+ MaTTS" in a table) becomes its text. Anything else is saved as an image.
    """
    def image():
        return f'<img src="{save("svg+xml", svg.encode("utf-8"))}" alt="" />'

    kind = picture_kind(svg)
    blocks = foreign_objects(svg)
    if kind == "badge":
        return f"<span>{' '.join(blocks)}</span>"
    if kind == "image":
        return image()
    parts = []
    for k, block in enumerate(blocks):
        n = words(block)
        if not n:
            continue
        if k == 0 and len(blocks) > 1 and n < 12:
            title = re.sub(r"<[^>]+>", " ", re.sub(r"<annotation\b.*?</annotation>", "", block, flags=re.S))
            parts.append(f"<p><strong>{' '.join(title.split())}</strong></p>")
        else:
            # A list item's label ("1.") is a span of its own; keep it apart from the text.
            block = re.sub(r'(<span\b[^>]*class="ltx_tag\b[^"]*"[^>]*>[^<]*</span>)', r"\1 ", block)
            parts.append(f"<div>{spans_to_blocks(extract_svgs(block, save))}</div>")
    quote = f"<blockquote {LIFT}>{''.join(parts)}</blockquote>"
    return image() + quote if kind == "diagram" else quote


PYTHON = re.compile(r"^\s*(def \w+\(.*\):\s*$|import \w|from [\w.]+ import \w|class \w+.*:\s*$)", re.M)
# A listing that is itself a markdown code block (model output shown verbatim).
FENCED = re.compile(r"\A[`\u201c\u2018\u201d\u2019]{3}\s*(\w*)\s*\n(.*)\n\s*[`\u201d\u2019]{3}\s*\Z", re.S)


def balanced_end(article, begin, tag):
    """Index just past the </tag> that closes the <tag> starting at `begin`."""
    depth = 0
    for m in re.compile(rf"<{tag}\b|</{tag}\s*>").finditer(article, begin):
        depth += 1 if m.group().startswith(f"<{tag}") else -1
        if depth == 0:
            return m.end()
    return None


def listing_source(block):
    """The source text of one LaTeXML code listing.

    LaTeXML puts the listing's exact source in a "download" link as a base64
    data URI; failing that, the text is rebuilt from its per-line <div>s.
    """
    m = re.search(r'href="data:text/plain;base64,([A-Za-z0-9+/=]+)"', block)
    if m:
        try:
            return base64.b64decode(m.group(1)).decode("utf-8").rstrip("\n")
        except (ValueError, UnicodeDecodeError):
            pass
    lines = re.findall(r'<(div|span)[^>]*\bltx_listingline\b[^>]*>(.*?)</\1>', block, re.S)
    lines = [line for _, line in lines]
    text = [html.unescape(re.sub(r"<[^>]+>", "", line)).strip("\n") for line in lines]
    return "\n".join(text).rstrip("\n")


def convert_listings(article):
    """Replace each code listing with <pre><code>, which pandoc makes a fenced block.

    Left to pandoc, a listing becomes a "⬇" link carrying the whole source as a
    base64 data URI, followed by its lines as escaped paragraphs with the
    indentation lost. Algorithm blocks (ltx_listing without ltx_lstlisting) hold
    math and convert well as they are, so they are left alone.
    """
    out, pos = [], 0
    start = re.compile(r'<(div|span)[^>]*class="([^"]*\bltx_lstlisting\b[^"]*)"[^>]*>')
    while True:
        m = start.search(article, pos)
        end = balanced_end(article, m.start(), m.group(1)) if m else None
        if end is None:
            out.append(article[pos:])
            return "".join(out)
        source = listing_source(article[m.start():end])
        # A class makes pandoc write a fenced block (an indented one otherwise):
        # the language LaTeXML recorded, else "python" for code that looks like
        # it, else "text".
        lang = re.search(r"\bltx_lst_language_(\w+)", m.group(2))
        lang = lang.group(1).lower() if lang else "python" if PYTHON.search(source) else "text"
        fenced = FENCED.match(source)
        if fenced:
            source, lang = fenced.group(2), fenced.group(1) or lang
        out.append(article[pos:m.start()])
        if m.group(1) == "span" and "\n" not in source.strip():
            # An inline listing (in running text or a table cell) stays inline.
            out.append(f"<code>{html.escape(source.strip(), quote=False)}</code>")
        else:
            out.append(f'<pre><code class="{lang}">{html.escape(source, quote=False)}</code></pre>')
        pos = end


TABULAR_PARTS = {
    "ltx_tabular": "table", "ltx_thead": "thead", "ltx_tbody": "tbody", "ltx_tfoot": "tfoot",
    "ltx_tr": "tr", "ltx_td": "td", "ltx_th": "th",
}
SPAN_TAG = re.compile(r"<span\b([^>]*)>|</span\s*>")


def tabular_tag(attrs):
    """The table element a LaTeXML <span> stands for, with its spans, or None."""
    classes = re.search(r'\bclass="([^"]*)"', attrs)
    classes = classes.group(1).split() if classes else []
    tag = next((TABULAR_PARTS[c] for c in ("ltx_th", "ltx_td", "ltx_tr", "ltx_thead",
                                           "ltx_tbody", "ltx_tfoot", "ltx_tabular")
                if c in classes), None)
    if not tag:
        return None
    extra = "".join(
        f' {kind}span="{n}"'
        for kind, n in re.findall(r"\bltx_(col|row)span_(\d+)\b", " ".join(classes))
    )
    return f"<{tag}{attrs}{extra}>", f"</{tag}>"


def span_tabulars_to_tables(article):
    """Rewrite tables LaTeXML wrote as <span>s into real <table>s.

    A tabular inside \\resizebox or \\scalebox sits in an inline context, so
    LaTeXML builds it from <span class="ltx_tabular">, "ltx_tr" and "ltx_td"
    spans, which pandoc unwraps into one line of text. The table also has to
    leave the <p> it sits in (see lift_blocks).
    """
    out, pos = [], 0
    start = re.compile(r'<span\b[^>]*\bclass="[^"]*\bltx_tabular\b[^"]*"[^>]*>')
    while True:
        m = start.search(article, pos)
        end = balanced_end(article, m.start(), "span") if m else None
        if end is None:
            out.append(article[pos:])
            return "".join(out)
        out.append(article[pos:m.start()])
        stack = []

        def rename(t):
            if t.group(0).startswith("</"):
                return stack.pop() if stack else t.group(0)
            tag = tabular_tag(t.group(1))
            stack.append(tag[1] if tag else "</span>")
            return tag[0] if tag else t.group(0)

        segment = article[m.start():end]
        if is_layout_tabular(m.group(0), segment):
            out.append(segment)
        else:
            segment = SPAN_TAG.sub(rename, segment)
            out.append(segment.replace("<table", f"<table {LIFT}", 1))
        pos = end


def is_layout_tabular(opening, segment):
    """Whether a span tabular is layout inside running text or math, not a table:
    a symbol stacked over a letter (esvect's \\vv), a \\makecell line break."""
    rows = len(re.findall(r'class="ltx_tr\b', segment))
    cells = len(re.findall(r'class="ltx_td\b', segment))
    return "ltx_markedasmath" in opening or rows < 2 or cells < 2 * rows


LIFT = 'data-lift="1"'
# A <p> or <span> whose whole content is a marked block or an already lifted wrapper.
WRAPPER = re.compile(rf"<(p|span)\b([^>]*)>(\s*)(?=<(?:table|blockquote|div) {LIFT})")


def lift_blocks(article):
    """Turn the inline wrappers around a rewritten table or box into <div>s.

    A table or quote inside a paragraph is not a block to pandoc. Each <p> or
    <span> that holds nothing but such a block (or a wrapper already lifted)
    becomes a <div>, innermost first; pandoc unwraps divs (arxiv-html.lua).
    """
    while True:
        out, pos = [], 0
        for m in WRAPPER.finditer(article):
            if m.start() < pos:
                continue
            end = balanced_end(article, m.start(), m.group(1))
            if end is None:
                continue
            inner = re.sub(rf"</{m.group(1)}\s*>\Z", "", article[m.end():end])
            tag = re.match(r"<(table|blockquote|div)\b", inner).group(1)
            if balanced_end(inner, 0, tag) != len(inner.rstrip()):
                continue
            out.append(article[pos:m.start()])
            out.append(f"<div {LIFT}{m.group(2)}>{m.group(3)}{inner}</div>")
            pos = end
        if not out:
            return article.replace(f" {LIFT}", "")
        out.append(article[pos:])
        article = "".join(out)


def paper_version(page):
    """The arXiv id and version a rendering is of ("2505.00675v3"), or None."""
    for pattern in (
        r'<base href="/html/(\d{4}\.\d{4,5}v\d+)/"',
        r"(\d{4}\.\d{4,5}v\d+) \[[\w.-]+\]",  # the stamp in the margin
        r'"(\d{4}\.\d{4,5}v\d+)/[^"]+"',      # a figure's path
    ):
        m = re.search(pattern, page)
        if m:
            return m.group(1)
    return None


@functools.cache
def source_files(version):
    """The text files of a paper's arXiv source (.tex, .bib, .bbl): {name: text}."""
    data = fetch(f"https://arxiv.org/e-print/{version}")
    if not data:
        return {}
    files = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith((".tex", ".bib", ".bbl")):
                    files[member.name.removeprefix("./")] = tar.extractfile(member).read()
    except tarfile.TarError:
        try:
            files["main.tex"] = gzip.decompress(data)  # a single .tex file
        except OSError:
            return {}
    return {name: text.decode("utf-8", "replace") for name, text in files.items()}


def latex_source(version):
    """The paper's LaTeX, \\input files spliced in and comments removed, or None."""
    files = {name: re.sub(r"(?<!\\)%.*", "", text)
             for name, text in source_files(version).items() if name.endswith(".tex")}
    main = next((n for n, t in files.items() if r"\documentclass" in t), None)
    if not main:
        return None

    def splice(name, depth=0):
        text = files.get(name) or files.get(name + ".tex") or ""
        if depth > 10:
            return text
        return re.sub(
            r"\\(?:input|include|subfile)\s*\{([^}]+)\}",
            lambda m: splice(m.group(1).strip(), depth + 1),
            text,
        )

    return splice(main)


MISSING_CITATION = re.compile(r'<span class="ltx_ref ltx_missing_citation[^"]*">([^<]+)</span>')
MISSING_LABEL = re.compile(r'<span class="ltx_ref ltx_missing_label[^"]*">LABEL:([^<]+)</span>')


def citations_from_bibtex(keys, bib):
    """Author-year labels and reference entries for BibTeX keys, by pandoc's citeproc.

    Returns ({key: "Jiang et al. 2025"}, {key: entry as HTML}); a key the
    .bib file lacks is in neither.
    """
    with tempfile.TemporaryDirectory() as tmp:
        bib_path = Path(tmp) / "paper.bib"
        bib_path.write_text(bib, encoding="utf-8")
        run = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html", "--wrap=none", "--citeproc", "--bibliography", str(bib_path)],
            input="\n\n".join(f"[@{key}]" for key in keys), capture_output=True, text=True,
        )
    labels = {}
    for key, text in re.findall(r'<span class="citation" data-cites="([^"]+)">(.*?)</span>', run.stdout, re.S):
        text = re.sub(r"<[^>]+>", "", text).strip()
        if "?" not in text:  # citeproc writes "(key?)" for a key it does not know
            labels[key] = text.removeprefix("(").removesuffix(")")
    entries = dict(re.findall(r'<div id="ref-([^"]+)" class="csl-entry"[^>]*>\s*(.*?)\s*</div>', run.stdout, re.S))
    return labels, entries


def unresolved_citations(article, page):
    """Fill in the citations and table references arXiv's rendering left unresolved.

    A paper submitted with its .bib but without the compiled bibliography
    renders with every citation as its BibTeX key and no reference list.
    Both are rebuilt from the .bib in the paper's source. A reference to a
    table or figure LaTeXML lost ("Table LABEL:tab:x") gets its number from
    the float whose caption follows that \\label in the source, or else
    shows the label's name.
    """
    keys = list(dict.fromkeys(k.strip() for k in MISSING_CITATION.findall(article)))
    labels_missing = MISSING_LABEL.search(article)
    if not keys and not labels_missing:
        return article
    version = paper_version(page)
    files = source_files(version) if version else {}

    if keys:
        bib = "\n".join(text for name, text in files.items() if name.endswith(".bib"))
        labels, entries = citations_from_bibtex(keys, bib) if bib else ({}, {})
        article = MISSING_CITATION.sub(lambda m: labels.get(m.group(1).strip(), m.group(0)), article)
        cited = [entries[k] for k in keys if k in entries]
        if cited and "ltx_bibitem" not in article:
            listing = "<ul>" + "".join(f"<li>{entry}</li>" for entry in cited) + "</ul>"
            section = re.search(r'<section\b[^>]*class="[^"]*\bltx_bibliography\b', article)
            end = balanced_end(article, section.start(), "section") if section else None
            if end:
                cut = end - len("</section>")
                article = article[:cut] + listing + article[cut:]
            else:
                cut = article.rindex("</div>")
                article = article[:cut] + "<h2>References</h2>" + listing + article[cut:]
        if len(labels) < len(keys):
            print(f"warning: {len(keys) - len(labels)} of {len(keys)} unresolved citations not in the paper's .bib",
                  file=sys.stderr)

    if labels_missing:
        tex = latex_source(version) or "" if version else ""
        captions = [(re.sub(r"<[^>]+>", "", tag).strip(" :."), plain_words(re.sub(r"<math\b.*?</math>", " ", body, flags=re.S)))
                    for tag, body in re.findall(
                        r'<figcaption\b[^>]*>\s*<span class="ltx_tag[^"]*">(.*?)</span>(.*?)</figcaption>', article, re.S)]

        def number(m):
            label = m.group(1)
            at = tex.find(f"\\label{{{label}}}")
            # The caption of the float the label sits in: the nearest one before
            # the label within the float, else the first after it.
            begin = max(tex.rfind("\\begin{table", 0, at), tex.rfind("\\begin{figure", 0, at)) if at >= 0 else -1
            caption = re.search(r"\\caption\*?\s*(?:\[[^\]]*\])?\s*\{", tex[begin:]) if begin >= 0 else None
            if caption:
                start = plain_words(tex[begin + caption.end():begin + caption.end() + 200])[:5]
                for tag, body in captions:
                    if start and body[:len(start)] == start:
                        return tag.split()[-1]  # "Table 3" -> "3", after the "Table" already in the text
            return label.split(":", 1)[-1]

        article = MISSING_LABEL.sub(number, article)
    return article


def plain_words(text):
    """The words of a LaTeX or HTML fragment, lowercased, markup dropped."""
    text = re.sub(r"\\[a-zA-Z]+\*?|<[^>]+>|[{}$~]", " ", text)
    return re.findall(r"[a-z0-9]+", text.lower())


def forest_nodes(tex):
    """Parse one forest tree ("[Root, options [Child] [Child [Leaf]]]").

    Returns (text, children) for the root. A node's text runs to the first
    "," "[" or "]" outside braces ("{,}" is a literal comma); what follows a
    comma is options.
    """
    depth, i = 0, 0
    while i < len(tex) and not (tex[i] == "[" and depth == 0):  # skip the preamble
        depth += {"{": 1, "}": -1}.get(tex[i], 0)
        i += 1

    def node(i):
        i += 1
        text, depth = [], 0
        while i < len(tex) and not (depth == 0 and tex[i] in ",[]"):
            depth += {"{": 1, "}": -1}.get(tex[i], 0)
            text.append(tex[i])
            i += 1
        while i < len(tex) and not (depth == 0 and tex[i] in "[]"):  # options
            depth += {"{": 1, "}": -1}.get(tex[i], 0)
            i += 1
        children = []
        while i < len(tex) and tex[i] == "[":
            child, i = node(i)
            children.append(child)
            while i < len(tex) and tex[i].isspace():
                i += 1
        return ("".join(text).strip(), children), i + 1

    return node(i)[0] if i < len(tex) else None


CITE = re.compile(r"~?\\(?:cite|citep|citet|citealp|citeauthor|citeyear|parencite|textcite|autocite)\*?(?:\[[^\]]*\])*\{([^}]*)\}")
# A cross-reference ("\S\ref{sec:x}"): the HTML has no numbers to resolve it to.
REF = re.compile(r"(?:\\S|§)?~?\s*\\(?:ref|autoref|cref|Cref|eqref)\{[^}]*\}")


def forest_html(trees, macros):
    """Nested <ul>s for parsed trees, the node text converted from LaTeX by pandoc."""
    texts = []

    def collect(n):
        text = REF.sub("", re.sub(r"\{,\s*\}", ", ", n[0]).replace("\\\\", " "))
        # Citations go when the node names its papers anyway ("MemGPT \cite{x}").
        if re.sub(r"[\W\d_]", "", CITE.sub("", text).replace("\\", "")):
            text = CITE.sub("", text)
        else:
            text = CITE.sub(lambda m: m.group(1).replace(",", ", "), text)
        texts.append(re.sub(r"\s+(?=[,;.)])", "", text).strip())
        for c in n[1]:
            collect(c)

    for t in trees:
        collect(t)
    sep = "FORESTNODESEPARATOR"
    # The paper's own macros help (\method{}), unless a definition the
    # one-line grep cut short breaks the parse.
    for preamble in (macros, ""):
        html_out = subprocess.run(
            ["pandoc", "-f", "latex", "-t", "html", "--mathjax", "--wrap=none"],
            input=preamble + "\n\n" + f"\n\n{sep}\n\n".join(texts), capture_output=True, text=True,
        ).stdout
        parts = [re.sub(r"\A\s*<p>|</p>\s*\Z", "", p.strip()) for p in re.split(rf"<p>{sep}</p>", html_out)]
        if len(parts) == len(texts):
            break
    else:
        parts = [html.escape(t) for t in texts]
    parts = [
        re.sub(
            r'<span class="math inline">\\\((.*?)\\\)</span>',
            lambda m: '<math display="inline"><semantics><mrow></mrow>'
            f'<annotation encoding="application/x-tex">{m.group(1)}</annotation></semantics></math>',
            p,
        )
        for p in parts
    ]
    it = iter(parts)

    def render(n):
        label = next(it)
        kids = "".join(render(c) for c in n[1])
        return f"<li>{label}{f'<ul>{kids}</ul>' if kids else ''}</li>"

    return [f"<ul>{render(t)}</ul>" for t in trees]


def forest_trees(article, page):
    """Fill in the trees LaTeXML could not draw from the paper's LaTeX source.

    LaTeXML has no support for the forest package (taxonomy trees in surveys)
    and leaves an empty "{forest}" in their place. The trees are taken from
    the source on arXiv, in document order, as nested lists.
    """
    placeholder = re.compile(r'<span\b[^>]*class="ltx_ERROR[^"]*"[^>]*>\{forest\}</span>')
    found = placeholder.findall(article)
    if not found:
        return article
    version = paper_version(page)
    tex = latex_source(version) if version else None
    envs = re.findall(r"\\begin\{forest\}(.*?)\\end\{forest\}", tex or "", re.S)
    trees = [t for t in (forest_nodes(e) for e in envs) if t]
    if len(trees) != len(found):
        print(f"warning: {len(found)} forest trees, {len(trees)} in the LaTeX source; left out",
              file=sys.stderr)
        return article
    macros = "\n".join(re.findall(r"^\s*\\(?:re)?newcommand\b.*$|^\s*\\DeclareMathOperator\b.*$", tex, re.M))
    lists = iter(forest_html(trees, macros))
    return placeholder.sub(lambda m: f"<div {LIFT}>{next(lists)}</div>", article)


REF_KINDS = {"sec": "§", "ssec": "§", "subsec": "§", "app": "Appendix", "fig": "Figure",
             "tab": "Table", "eq": "Eq.", "alg": "Algorithm", "thm": "Theorem", "def": "Definition"}


def unresolved_refs(article):
    r"""A \Cref LaTeXML did not know ("\Cref" then the bare label "sec:what-memory")
    becomes "§ what-memory": the target's kind and name, as no number exists."""
    def label(m):
        kind, _, name = m.group(2).partition(":")
        return (m.group(1) or "") + (f"{REF_KINDS.get(kind, '')} {name}".strip() if name else m.group(2))

    return re.sub(
        r'<span\b[^>]*class="ltx_ERROR undefined"[^>]*>\\(?:[Cc]ref|autoref|vref)</span>(<span\b[^>]*>)?([\w:-]+(?:\.[\w-]+)*)',
        label, article,
    )


# A file name that says nothing about the picture: LaTeXML's own "x12.png",
# "image3", "fig_2".
GENERIC_NAME = re.compile(r"(?:x|img|image|fig|figure|icon|logo)?[-_ ]?\d*", re.I)


def name_uncaptioned_images(article):
    """Give an image without a caption its file's name as alt text.

    Papers set icons inline (a check or cross mark in a table cell, a logo
    before a model's name) as small images. arXiv's alt text for them is the
    placeholder "[Uncaptioned image]", which leaves a table of identical
    pictures; the file name ("yes_emoji", "Octicons-mark-github") says which
    is which.
    """
    def rename(tag):
        src = re.search(r'\bsrc="([^"]+)"', tag.group(0))
        name = Path(html.unescape(src.group(1))).stem if src else ""
        if not name or src.group(1).startswith("data:") or GENERIC_NAME.fullmatch(name):
            return tag.group(0)
        return tag.group(0).replace('alt="[Uncaptioned image]"', f'alt="{html.escape(name)}"')

    return re.sub(r'<img\b[^>]*\balt="\[Uncaptioned image\]"[^>]*>', rename, article)


def objects_to_images(article):
    """Replace each image <object data="..."> with an <img> of the same file."""
    return re.sub(
        r'<object\b[^>]*?\btype="image/[^"]*"[^>]*?\bdata="([^"]+)"[^>]*>.*?</object\s*>',
        r'<img src="\1" alt="" />',
        article,
        flags=re.S,
    )


def main(html_path, body_path, images_dir, basename):
    images_dir = Path(images_dir)
    counter, invalid = 0, 0

    def save(mime, data, repair=True):
        """Write one figure to images/ and return its relative link."""
        nonlocal counter, invalid
        counter += 1
        ext = EXTS.get(mime, "bin")
        if ext == "svg" and repair:
            svg = repair_svg(data.decode("utf-8"))
            invalid += not is_valid_xml(svg)
            data = svg.encode("utf-8")
        name = f"{basename}-fig{counter:02d}.{ext}"
        images_dir.mkdir(parents=True, exist_ok=True)
        (images_dir / name).write_bytes(data)
        return f"images/{quote(name)}"

    def save_raster(mime, data):
        """Save an inlined raster figure as WebP, or as-is if it will not decode."""
        try:
            return save("webp", to_webp(data))
        except Exception:
            return save(mime, data)

    page = Path(html_path).read_text(encoding="utf-8")
    # Older renderings link figures relative to <base href="/html/<id>v<n>/">
    # ("x1.png", "extracted/..."); the figure download needs the full path.
    base = re.search(r'<base href="/html/(\d{4}\.\d{4,5}v\d+/)"', page)
    article = extract_article(page)
    article = convert_listings(article)
    article = span_tabulars_to_tables(article)
    article = forest_trees(article, page)
    article = unresolved_refs(article)
    article = unresolved_citations(article, page)
    article = extract_svgs(article, save)
    article = lift_blocks(article)
    article = objects_to_images(article)
    article = name_uncaptioned_images(article)
    body = subprocess.run(
        [
            "pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars",
            "--wrap=none", "--lua-filter", str(FILTER),
        ],
        input=article, capture_output=True, text=True, check=True,
    ).stdout
    # LaTeXML sometimes repeats a heading with nothing under the first copy
    # (an "Abstract" set both by the class and by the author).
    body = re.sub(r"^(#{1,6} .+)\n\n(?=\1\n)", "", body, flags=re.M)

    # Raster figures arXiv inlines as base64 data URIs.
    body = re.sub(
        r"!\[(?:\\.|[^\]\\])*\]\(data:image/([a-zA-Z0-9+.-]+);base64,([A-Za-z0-9+/=]+)\)",
        lambda m: f"![]({save_raster(m.group(1), base64.b64decode(m.group(2)))})",
        body,
    )
    if base:
        body = re.sub(
            r'(!\[(?:\\.|[^\]\\])*\]\(|<img\s[^>]*?src=")(?![a-z]+:|images/|/|\d{4}\.\d{4,5}v\d+/)([^)"\s]+)',
            lambda m: m.group(1) + base.group(1) + m.group(2),
            body,
        )
    # Figures arXiv hosts next to the rendering: rasters as WebP, SVGs as
    # served (standalone files, so they need no repair).
    body, failed = localize_figures(
        body, lambda data, ext: save("svg+xml" if ext == "svg" else ext, data, repair=False)
    )
    Path(body_path).write_text(body, encoding="utf-8")
    # A picture pandoc dropped along with its surroundings (a title-page logo)
    # would be left as an unreferenced file.
    for f in images_dir.glob(f"{basename}-fig*") if images_dir.exists() else []:
        if f"images/{quote(f.name)}" not in body:
            f.unlink()
    if invalid:
        print(f"warning: {invalid} of {counter} extracted SVGs are still not valid XML", file=sys.stderr)
    if failed:
        print(f"warning: {failed} figures could not be downloaded and still link to arXiv", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
