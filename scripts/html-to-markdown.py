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
11. The warnings a conference style file typesets when a paper changed its
    page layout are dropped (see drop_style_warnings).
12. Bold, italics and underlining are kept, and each footnote follows the
    paragraph or table it annotates (both in arxiv-html.lua). Cell shading
    is kept as <mark> where the caption refers to it (see mark_shading).
13. The names of macros LaTeXML did not know are dropped, a value and the
    deviation printed small after it are set apart, and a column title's
    raised line is read first (see drop_undefined_macros, tidy_cells).
14. A table panel gets the row labels it shares with the panel beside it,
    and a row label spanning a group of rows takes the group's last row
    (see share_panel_labels, extend_rowspans).
"""

import base64
import functools
import gzip
import html
import html.entities
import io
import os
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
    if not lines:
        # \lstinline in running text has no line elements, only its tokens.
        lines = [re.sub(r"\A<[^>]+>|</\w+\s*>\Z", "", block)]
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
    a symbol stacked over a letter (esvect's \\vv), a \\makecell line break.
    A cell spanning columns counts as that many, so a table with full-width
    group rows ("7B Models") is still a table."""
    rows = len(re.findall(r'class="ltx_tr\b', segment))
    cells = len(re.findall(r'class="ltx_td\b', segment))
    cells += sum(int(n) - 1 for n in re.findall(r"\bltx_colspan_(\d+)\b", segment))
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
    def splice(name, depth=0):
        text = files.get(name) or files.get(name + ".tex") or ""
        if depth > 10:
            return text
        return re.sub(
            r"\\(?:input|include|subfile)\s*\{([^}]+)\}",
            lambda m: splice(m.group(1).strip(), depth + 1),
            text,
        )

    # A source can hold a second document (an appendix or a reply compiled apart): the paper is the longest.
    return max((splice(n) for n, t in files.items() if r"\documentclass" in t), key=len, default=None)


MISSING_CITATION = re.compile(r'<span class="ltx_ref ltx_missing_citation[^"]*">([^<]+)</span>')
MISSING_LABEL = re.compile(r'<span class="ltx_ref ltx_missing_label[^"]*">LABEL:([^<]+)</span>')
# The same, with not even the label left: "(Table )".
EMPTY_LABEL = re.compile(r'<span class="ltx_ref ltx_missing_label[^"]*"[^>]*>\s*</span>')
TEX_REF = r"\\(?:ref|cref|Cref|autoref|vref)\*?\{([^}]+)\}"
TEX_CITE = r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}"
TEX_FLOAT = re.compile(r"\\begin\{(table|figure|algorithm)\*?\}")
TEX_CAPTION = re.compile(r"\\caption\*?\s*(?:\[[^\]]*\])?\s*\{")
# A citation command LaTeXML did not know leaves no key at all: "( ?)".
UNKNOWN_CITATION = re.compile(r"\(\s\?\)|\[\s?\?\]")
# What may stand between two words of a sentence in its LaTeX source.
TEX_GAP = r"(?:[^a-zA-Z0-9\\]|\\(?:begin|end|label)\{[^}]*\}|\\[a-zA-Z]+\*?|\\.)*"


def label_in_source(before, tex, command=TEX_REF, least=3):
    """The label of the \\ref (or the keys of the \\cite, given TEX_CITE) that
    follows the words `before` in the LaTeX source: the last five of them,
    then fewer, down to `least`."""
    said = plain_words(re.sub(r"<math\b.*?</math>", " ", before, flags=re.S))[-5:]
    while len(said) >= least:
        found = {m.group(1) for m in re.finditer(TEX_GAP.join(map(re.escape, said)) + TEX_GAP + command, tex, re.I)}
        if len(found) == 1:
            return found.pop()
        if found:
            return None  # the same words lead to two different floats
        said = said[1:]
    return None


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
    the float whose caption follows that \\label in the source, one to a
    section the number of the section the label follows (see
    section_numbers), or else it shows the label's name. Where not even the label is left ("Table "), it
    is the one the same sentence refers to in the source.
    """
    keys = list(dict.fromkeys(k.strip() for k in MISSING_CITATION.findall(article)))
    labels_missing = MISSING_LABEL.search(article) or EMPTY_LABEL.search(article)
    unknown = UNKNOWN_CITATION.search(article)
    if not keys and not labels_missing and not unknown:
        return article
    version = paper_version(page)
    files = source_files(version) if version else {}

    if unknown:
        article = unknown_citations(article, latex_source(version) or "" if version else "",
                                    "\n".join(text for name, text in files.items() if name.endswith(".bib")))

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

        sections = section_numbers(article, tex)

        def opening(caption):
            """The first words of a caption in the source, none from what follows a short one."""
            end = tex_group_end(tex, caption.end() - 1) or len(tex)
            return plain_words(tex[caption.end():min(end, caption.end() + 200)])[:5]

        def number(label):
            if label in sections:
                return sections[label][0]
            at = tex.find(f"\\label{{{label}}}")
            # The caption of the float the label sits in: the nearest one before
            # the label within the float, else the first after it. A label outside
            # a float (an equation's, an appendix's) has no caption.
            opened = max(TEX_FLOAT.finditer(tex, 0, at), key=lambda m: m.start(), default=None) if at >= 0 else None
            closed = re.compile(r"\\end\{%s\*?\}" % opened.group(1)).search(tex, opened.end()) if opened else None
            end = closed.start() if closed else len(tex)
            caption = None
            if opened and at < end:
                caption = (max(TEX_CAPTION.finditer(tex, opened.end(), at), key=lambda m: m.start(), default=None)
                           or TEX_CAPTION.search(tex, at, end))
            if caption:
                start = opening(caption)
                same = [tag for tag, body in captions if start and body[:len(start)] == start]
                if len(same) > 1:
                    # Captions that open alike ("… results in \\flickr") are told apart by their order in the source.
                    alike = [m.start() for m in TEX_CAPTION.finditer(tex) if opening(m) == start]
                    same = [same[alike.index(caption.start())]] if len(alike) == len(same) else []
                if same:
                    return same[0].split()[-1]  # "Table 3" -> "3", after the "Table" already in the text
            return label.split(":", 1)[-1]

        def from_source(m):
            label = label_in_source(article[max(0, m.start() - 400):m.start()], tex)
            return number(label) if label else m.group(0)

        article = EMPTY_LABEL.sub(from_source, article)
        article = MISSING_LABEL.sub(lambda m: number(m.group(1)), article)
    return article


def unknown_citations(article, tex, bib):
    """Name the papers behind each "( ?)": the keys of the \\cite that follows the
    same words in the LaTeX source, labelled from the paper's .bib. One whose
    words are not found once in the source, or whose keys the .bib lacks, stays."""
    if not tex or not bib:
        return article
    cited = {}
    for m in UNKNOWN_CITATION.finditer(article):
        # From the end of a tag, so that no attribute is taken for words. Two
        # words are enough for a catalogue's "BART ... Reference: ( ?)".
        before = re.sub(r"\A[^<]*>", "", article[max(0, m.start() - 1500):m.start()])
        found = label_in_source(before, tex, TEX_CITE, least=2)
        if found:
            cited[m.start()] = [k.strip() for k in found.split(",")]
    labels, _ = citations_from_bibtex(list(dict.fromkeys(k for keys in cited.values() for k in keys)), bib)

    def name(m):
        keys = cited.get(m.start())
        if not keys or any(k not in labels for k in keys):
            return m.group(0)
        return m.group(0)[0] + "; ".join(labels[k] for k in keys) + m.group(0)[-1]

    return UNKNOWN_CITATION.sub(name, article)


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
# A cross-reference ("\S\ref{sec:x}"), with the section sign or word before it.
REF = re.compile(r"(?:\\S|§|Sec(?:tion|\.)?)?~?\s*\\(?:ref|autoref|cref|Cref|eqref)\{([^}]*)\}")
SECTIONING = re.compile(r"\\(chapter|(?:sub){0,2}section)\*?\s*(?:\[[^\]]*\])?\s*\{")
NUMBERED_HEADING = re.compile(
    r'<section\b[^>]*\bid="([^"]+)"[^>]*>\s*<h\d\b[^>]*>\s*'
    r'<span class="ltx_tag ltx_tag_(\w+)">((?:<span\b[^>]*>[^<]*</span>|[^<])*)</span>(.*?)</h\d>', re.S)


def section_numbers(article, tex):
    """{label: (number, id)} for the sections of the LaTeX source the HTML numbers.

    A \\label belongs to the \\section it directly follows; the section is
    found in the HTML by its level and title. Sections that share both are
    paired in order when the source and the HTML have as many of them.
    """
    headings, labels = {}, {}
    for sid, level, number, title in NUMBERED_HEADING.findall(article):
        number = re.sub(r"<[^>]+>", "", number).strip().rstrip(".")
        words = tuple(plain_words(html.unescape(re.sub(r"<math\b.*?</math>|<[^>]+>", " ", title, flags=re.S))))
        if number:
            headings.setdefault((level, words), []).append((number, sid))
    for m in SECTIONING.finditer(tex):
        depth, end = 1, m.end()
        while end < len(tex) and depth:
            depth += {"{": 1, "}": -1}.get(tex[end], 0)
            end += 1
        label = re.match(r"(?:\s|\\vspace\*?\{[^}]*\})*\\label\{([^}]+)\}", tex[end:])
        title = re.sub(r"\$[^$]*\$|\\(?:text)?color\{[^}]*\}", " ", tex[m.end():end - 1])
        labels.setdefault((m.group(1), tuple(plain_words(title))), []).append(label.group(1) if label else None)
    return {label: found
            for key, names in labels.items() if len(names) == len(headings.get(key, []))
            for label, found in zip(names, headings[key]) if label}


def forest_html(trees, macros, sections=None):
    """Nested <ul>s for parsed trees, the node text converted from LaTeX by pandoc.

    A reference to a section ("\\S\\ref{sec:x}") becomes a link showing its
    number when `sections` ({label: (number, id)}) has the label; other
    references are dropped, with brackets they leave empty.
    """
    texts, links = [], []

    def reference(m):
        if m.group(1) not in (sections or {}):
            return ""
        links.append(sections[m.group(1)])
        return f"FORESTREF{len(links) - 1}X"

    def collect(n):
        # "\\ \\ \\ Context \\\\ \\ \\ Processing": line breaks and the spaces that centre the lines.
        text = re.sub(r"(?:\\ |\\\Z|\s)+", " ", re.sub(r"\{,\s*\}", ", ", n[0]).replace("\\\\", " "))
        text = re.sub(r"\s+~\s*|~\s+", "~", text)  # a space beside a tie adds nothing
        text = re.sub(r"(?<=[\w.,;])(?=FORESTREF)", " ", REF.sub(reference, text))
        # Citations go when the node names its papers anyway ("MemGPT \cite{x}").
        if re.sub(r"[\W\d_]", "", CITE.sub("", text).replace("\\", "")):
            text = CITE.sub("", text)
        else:
            text = CITE.sub(lambda m: m.group(1).replace(",", ", "), text)
        if "()" not in n[0]:  # brackets that held only a reference; "forward()" stays
            text = re.sub(r"[\s~]*\(\s*\)", "", text)
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
    parts = [re.sub(r"FORESTREF(\d+)X",
                    lambda m: '<a href="#{1}">§{0}</a>'.format(*links[int(m.group(1))]), p) for p in parts]
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
    lists = iter(forest_html(trees, macros, section_numbers(article, tex)))
    return placeholder.sub(lambda m: f"<div {LIFT}>{next(lists)}</div>", article)


BIBITEM = re.compile(r'<li\b[^>]*\bid="(bib\.[^"]+)"[^>]*\bclass="[^"]*\bltx_bibitem\b[^"]*"[^>]*>(.*?)</li>', re.S)


def first_author(names):
    """ "Mihaylov et al." from a reference's author list, in whichever order
    it writes names ("Mihaylov, T.; Clark, P.", "T. Mihaylov and P. Clark")."""
    names = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(names)).split()).rstrip(". ")
    if not names:
        return None
    first = re.split(r"[;,]| and ", names)[0].split()
    surname = [w for w in first if not re.fullmatch(r"(?:[A-Z]\.)+|[A-Z]", w)] or first
    several = bool(re.search(r"[;,].*[;,]| and |&| et al", names))
    return " ".join(surname) + (" et al." if several else "")


def bare_year_citations(article):
    """Put the author back on citations that show only a year.

    A bibliography style LaTeXML does not know leaves each reference's tag
    as "[2018]", so every citation reads "[2018, 2018, 2018]". The first
    author is taken from the reference itself.
    """
    authors = {}
    for ref, item in BIBITEM.findall(article):
        if not re.search(r'ltx_tag_bibitem">\s*\[?\d{4}[a-z]?\]?\s*<', item):
            continue
        block = re.search(r'<span class="ltx_bibblock">(.*?)</span>\s*(?=<span class="ltx_bibblock">|\Z)', item, re.S)
        name = first_author(block.group(1)) if block else None
        if name:
            authors[ref] = name
    if not authors:
        return article
    return re.sub(
        r'(<a\b[^>]*\bhref="#(bib\.[^"]+)"[^>]*>)(\d{4}[a-z]?)(</a>)',
        lambda m: f"{m.group(1)}{authors[m.group(2)]} {m.group(3)}{m.group(4)}" if m.group(2) in authors else m.group(0),
        article,
    )


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


def drop_invisible(article):
    """Remove text LaTeX set only for its width.

    \\phantom{5} arrives as a hidden span that still holds the "5", which
    would print after the number it pads ("+0%5"). A \\parbox given a zero
    width in an algorithm line arrives holding a TeX length as its text.
    """
    out, pos = [], 0
    for m in re.finditer(r'<span\b[^>]*\bclass="[^"]*\bltx_phantom\b[^"]*"[^>]*>', article):
        if m.start() < pos:
            continue
        end = balanced_end(article, m.start(), "span")
        if end:
            out.append(article[pos:m.start()])
            pos = end
    article = "".join(out) + article[pos:]
    # "pass\\^{}k": an accent over nothing, set between the two words.
    # One class for the spaces: \s matches \xa0 too, and as two alternatives a run of them backtracks forever.
    article = re.sub(r'(?:[\s\xa0]|&nbsp;)*<math\b(?:(?!</math>).)*?>\\hat\{\}</annotation>\s*</semantics>\s*</math>'
                     r'(?:[\s\xa0]|&nbsp;)*', "^", article, flags=re.S)
    # "\\~55%": the tilde meant "about" but landed on the first digit as an accent.
    article = re.sub("(\\d)\u0303", r"~\1", article)
    return re.sub(r'<span\b[^>]*\bclass="ltx_p"[^>]*>\s*-?\d+(?:\.\d+)?pt\s*</span>', "", article)


# A TikZ picture inside a formula, as LaTeXML leaves it in the formula's TeX.
PICTURE = re.compile(r"\\hbox to\s*[\d.]+pt\s*\{\\vbox to\s*[\d.]+pt\s*\{\\pgfpicture")
TEX_SPECIAL = re.compile(r"[\\{}#$%&_^~]")


def tex_group_end(tex, begin):
    """Index just past the brace group that opens at `begin`, or None."""
    depth, i = 0, begin
    while i < len(tex):
        if tex[i] == "\\":
            i += 1
        elif tex[i] == "{":
            depth += 1
        elif tex[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


def picture_label(svg):
    """The TeX for what a picture in a formula shows: the formulas and words set in it."""
    parts = []
    for block in foreign_objects(svg):
        for piece in re.split(r'(<math\b[^>]*>.*?</math>)', block, flags=re.S):
            alt = re.match(r'<math\b[^>]*\balttext="([^"]*)"', piece)
            text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", piece)).split())
            if alt:
                # The strut and the style only made the picture's box.
                parts.append("{" + re.sub(r"\A(?:\\(?:display|text|script|scriptscript)style|\\mathstrut|\s)+", "",
                                          html.unescape(alt.group(1))) + "}")
            elif text and not piece.startswith("<math"):
                parts.append("\\text{" + TEX_SPECIAL.sub(lambda c: "\\" + c.group(0) if c.group(0) in "#$%&_" else " ", text) + "}")
    return " ".join(parts) or "\\text{[picture]}"


def clean_math(article):
    """Rebuild the formulas that hold a picture or a block of HTML.

    A TikZ picture set in a formula (a boxed token name, a highlighted
    symbol) leaves its drawing commands in the formula's TeX, thousands of
    characters each, and the picture itself as an <svg> in the MathML. The
    commands are replaced by what the picture shows. A formula holding a
    <div> (a \\scalebox) is cut short by pandoc, the rest set as loose text.
    Both are written again as their TeX alone.
    """
    out, pos = [], 0
    for m in re.finditer(r"<math\b[^>]*>", article):
        if m.start() < pos:
            continue
        end = balanced_end(article, m.start(), "math")
        if end is None:
            continue
        element = article[m.start():end]
        if "<svg" not in element and "<div" not in element:
            continue
        alt = re.search(r'\balttext="([^"]*)"', m.group(0))
        if not alt:
            continue
        tex = html.unescape(alt.group(1))
        svgs, at = [], 0
        while (begin := element.find("<svg", at)) >= 0:
            at = balanced_end(element, begin, "svg") or len(element)
            svgs.append(element[begin:at])
        for labels in ([picture_label(svg) for svg in svgs], []):
            parts, done, used = [], 0, 0
            for pic in PICTURE.finditer(tex):
                if pic.start() < done:
                    continue
                begin, stop = pic.start(), tex_group_end(tex, tex.index("{", pic.start()))
                if tex.endswith("\\mathchoice{", 0, begin):  # the same picture at four sizes
                    begin -= len("\\mathchoice{")
                    stop = begin + len("\\mathchoice")
                    for _ in range(4):
                        stop = tex_group_end(tex, stop) if stop is not None and tex.startswith("{", stop) else None
                if stop is None:
                    continue
                parts += [tex[done:begin], labels[used] if used < len(labels) else "\\text{[picture]}"]
                done, used = stop, used + 1
            if used == len(labels) or not labels:
                break
        tex = "".join(parts) + tex[done:]
        display = re.search(r'\bdisplay="(\w+)"', m.group(0))
        out += [article[pos:m.start()],
                f'<math display="{display.group(1) if display else "inline"}"><semantics><mrow></mrow>'
                f'<annotation encoding="application/x-tex">{html.escape(tex, quote=False)}</annotation></semantics></math>']
        pos = end
    return "".join(out) + article[pos:]


CELL = re.compile(r"<(t[dh])\b[^>]*>.*?</\1\s*>", re.S)
# A span with a size or colour of its own, set straight after a number.
ANNOTATION = re.compile(r'(\d|</math>)(<span\b[^>]*\bstyle="[^"]*(?:font-size:\s*\d+%|--ltx-fg-color)[^"]*"[^>]*>)(?=[-+−±↑↓(]?\d)')
RAISED = re.compile(r'(<span\b[^>]*>[^<]*</span>)\s*'
                    r'(<span\b[^>]*\bstyle="[^"]*position:relative;\s*bottom:(\d+(?:\.\d+)?)pt[^"]*"[^>]*>[^<]*</span>)')
# \captionof stays: caption-numbers.py gives the caption after it its number.
UNDEFINED_MACRO = re.compile(r'<span\b[^>]*\bclass="ltx_ERROR[^"]*\bundefined"[^>]*>\\(?!captionof\b)[a-zA-Z@_:]+\*?</span>')
# A colour macro of a package LaTeXML lacks, and the colour's name set after it as text.
UNDEFINED_COLOUR = re.compile(r'<span\b[^>]*\bclass="ltx_ERROR[^"]*\bundefined"[^>]*>\\(?:cell|row|column)color</span>'
                              r'(\s*(?:<span\b[^>]*>)?)([^<\s]*)')
# xcolor's mix of a colour with white or another colour ("gray!10", "blue!20!white"), which ends where a letter follows a percentage.
COLOUR_MIX = re.compile(r"[A-Za-z][\w-]*(?:!\d+(?:\.\d+)?(?:![A-Za-z][\w-]*(?=!))?)+(?=[^\d.!])")
# Text of an element, with the tag that opens it; code and a formula's TeX are not prose.
TEXT_NODE = re.compile(r"(<(?!code\b|pre\b|annotation\b|/?math\b)[^>]*>)([^<]+)")
RAW_CITE = re.compile(r"\\cite\[cite[pt]\]\{\(?\\@@bibref\{[^}]*\}\{([^}]*)\}\{\\@@citephrase\{[^}]*\}\}\{\}\)?\}")
DIAGHEAD = re.compile(r"\\diaghead\([^)]*\)\{[^}]*\}" + r"\{\{?(?:\\shortstack\[\w\])?\{?([^{}]*)\}?\}?\}" * 2)
CAPTION_TYPE = re.compile(r'<span\b[^>]*\bclass="ltx_ERROR undefined"[^>]*>\\DeclareCaptionType</span>\s*'
                          r'<p\b[^>]*>[^<]*\[[^<]*</p>')


def tidy_cells(article):
    """Set apart what LaTeX placed with a size, a colour or a raise.

    A deviation or a gain printed small or in colour after a table's value
    arrives with no space between them ("0.340.01", "70.9+2.3"); it gets one.
    A column title set on two lines arrives lower line first, the upper one
    raised above it ("Pro" then "Gemini 2.5"); the raised line goes first.
    """
    article = CELL.sub(lambda cell: ANNOTATION.sub(r"\1 \2", cell.group(0)), article)
    return RAISED.sub(lambda m: f"{m.group(2)} {m.group(1)}" if float(m.group(3)) >= 8 else m.group(0), article)


def drop_undefined_macros(article):
    """Remove the names of macros LaTeXML did not know ("\\sans", "\\rotate").

    It prints the name where the macro stood and then sets the arguments as
    text, so only the name goes. \\DeclareCaptionType in the body goes with
    the paragraph of its arguments ("listing[Listing][List of Listings]").
    Run after the steps that read such a macro (forest_trees, unresolved_refs).
    """
    # The name runs into the cell's text ("c5-item-bkgVCG Bench", "gray!10ANLI").
    # A mix ends by its syntax; another name is learnt where a tag follows it,
    # unless that is a known name with a one-word cell after it.
    found = [(m.group(2), article.startswith("<", m.end())) for m in UNDEFINED_COLOUR.finditer(article)]
    names = {mix.group(0) for text, _ in found if (mix := COLOUR_MIX.match(text))}
    whole = {text for text, tagged in found if text and tagged}
    names |= {text for text in whole if not any(text != n and text.startswith(n) for n in names | whole)}
    names = sorted(names, key=len, reverse=True)

    def colour(m):
        name = next((n for n in names if m.group(2).startswith(n)), "")
        return m.group(1) + m.group(2)[len(name):]

    article = UNDEFINED_COLOUR.sub(colour, article)
    return UNDEFINED_MACRO.sub("", CAPTION_TYPE.sub("", article))


def drop_tex_residue(article):
    """Remove TeX that LaTeXML set as text.

    A \\par in a macro's argument is printed in each heading, caption and
    author it reached ("4 \\parExperiments"). A number set by siunitx can
    arrive with "\\par" as its TeX and the digits only in the MathML; the
    digits are taken. A bibliography style's "\\citeauthoryearBengio et
    al.2003" is the author and year, a glossary's "\\cite[citep]{...}"
    its keys, and a "\\diaghead" the two titles of a split header cell.
    """
    article = re.sub(
        r'(<math\b[^>]*>\s*<semantics>)((?:(?!</math>).)*?)(<annotation encoding="application/x-tex">)\\par(</annotation>)',
        lambda m: m.group(1) + m.group(2) + m.group(3)
        + re.sub(r"[\u2009\u2006\u202f]", r"\\,", html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()) + m.group(4),
        article, flags=re.S)

    def prose(m):
        text = re.sub(r"\s*\\par\b(?![a-zA-Z])\s*", " ", m.group(2)) if "\\par" in m.group(2) else m.group(2)
        if "\\cite" in text:
            text = re.sub(r"\\citeauthoryear(.*?)\s*(\d{4}[a-z]?)\Z", r"\1 \2", text)
            text = RAW_CITE.sub(r"(\1)", text)
        if "\\diaghead" in text:
            text = DIAGHEAD.sub(r"\1 / \2", text)
        return m.group(1) + text

    return TEXT_NODE.sub(prose, article)


def fix_text_encoding(article):
    """A ">" or "<" typed in text comes out as "¿" or "¡" (the text font's
    encoding). Standing alone they are the comparison; before a letter they
    are Spanish and stay."""
    article = re.sub(r"(?<=[\s>])¿(?=[\s<])", "&gt;", article)
    return re.sub(r"(?<=[\s>])¡(?=[\s<])", "&lt;", article)


BACKGROUND = re.compile(r"--ltx-bg-color:\s*#[0-9A-Fa-f]{6}")
SHADED_SPAN = re.compile(r"<span\b[^>]*--ltx-bg-color[^>]*>(.*?)</span>", re.S)
TABLE_FLOAT = re.compile(r'<figure\b[^>]*\bclass="[^"]*\bltx_table\b[^"]*"[^>]*>')
TABLE_ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr\s*>", re.S)
TABLE_CELL = re.compile(r"<(t[dh])\b([^>]*)>(.*?)</\1\s*>", re.S)
NAMES_SHADING = re.compile(r"colou?r|shad|highlight|gr[ae]y|background|\b(?:green|red|blue|yellow|orange|purple|pink|cyan)\b")
# Which shading is marked: "caption" (where the caption refers to it; the rule
# in use), "all" (wherever it picks out some rows or cells) or "none". The
# other two are for measuring the rule (experiments/table-emphasis).
SHADING = os.environ.get("PAPERLIB_SHADING", "caption")


def cell_text(fragment):
    return re.sub(r"<[^>]+>", "", fragment).strip()


def shaded_cells(float_html):
    """A table float's rows as lists of (start, end, shaded) for each cell's
    content. A cell is shaded when it has a background colour, or nearly all
    its text sits in a span that has one."""
    rows = []
    for row in TABLE_ROW.finditer(float_html):
        cells = []
        for cell in TABLE_CELL.finditer(row.group(1)):
            text = cell_text(cell.group(3))
            inner = "".join(cell_text(span) for span in SHADED_SPAN.findall(cell.group(3)))
            shaded = bool(BACKGROUND.search(cell.group(2))) or (bool(text) and len(inner) >= 0.8 * len(text))
            cells.append((row.start(1) + cell.start(3), row.start(1) + cell.end(3), shaded))
        if cells:
            rows.append(cells)
    return rows


def shading_pattern(rows):
    """What a table's shading picks out, from rows of booleans: "whole table",
    "header row", "alternate rows", "some rows", "whole columns", "some cells"
    or "many cells" (over a third). A row is shaded when all its cells are, or
    all but its label."""
    total, shaded = sum(map(len, rows)), sum(map(sum, rows))
    if shaded == total:
        return "whole table"
    full = [all(r) or (len(r) > 1 and all(r[1:])) for r in rows]
    if full == [any(r) for r in rows]:
        at = [i for i, f in enumerate(full) if f]
        if at == [0]:
            return "header row"
        if len(at) >= 3 and all(b - a == 2 for a, b in zip(at, at[1:])):
            return "alternate rows"
        return "some rows"
    width = max(map(len, rows))
    columns = [[r[c] for r in rows if len(r) == width] for c in range(width)]
    if sum(sum(c) for c in columns if sum(c) >= 0.8 * len(c)) >= 0.9 * shaded:
        return "whole columns"
    return "some cells" if shaded <= total / 3 else "many cells"


def mark_shading(article, rule=None):
    """Keep the cell shading that says something, as <mark>.

    Markdown has no cell colour, and most shading says nothing a reader of
    the whole paper lacks: a header, every other row, the paper's own method.
    It is kept only where the caption refers to it ("gray rows are ..."),
    since the caption would otherwise point at nothing: a shaded cell's
    content is marked, a row shaded from end to end on its first cell only,
    a shaded column on its top cell. A table shaded in several colours is
    left alone, as one mark cannot say which colour a cell had.
    """
    rule = rule or SHADING
    if rule == "none":
        return article
    out, pos = [], 0
    for m in TABLE_FLOAT.finditer(article):
        end = balanced_end(article, m.start(), "figure")
        if m.start() < pos or end is None:
            continue
        body = article[m.start():end]
        rows = shaded_cells(body) if "--ltx-bg-color" in body else []
        if not any(shaded for row in rows for _, _, shaded in row):
            continue
        flags = [[shaded for _, _, shaded in row] for row in rows]
        pattern = shading_pattern(flags)
        caption = cell_text(" ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S))).lower()
        named = bool(NAMES_SHADING.search(caption))
        if rule == "caption":
            colours = {c.lower() for c in BACKGROUND.findall(body)}
            wanted = (named and len(colours) == 1
                      and pattern in ("some rows", "some cells", "many cells", "whole columns"))
        else:
            wanted = pattern in ("some rows", "some cells", "many cells")
        if not wanted:
            continue
        marks = []
        if pattern == "whole columns":
            width = max(map(len, rows))
            for c in range(width):
                column = [row[c] for row in rows if len(row) == width]
                if sum(shaded for _, _, shaded in column) >= 0.8 * len(column):
                    marks.append(column[0][:2])
        else:
            for row, row_flags in zip(rows, flags):
                if len(row) > 1 and all(row_flags[1:]):
                    marks.append(row[0][:2])
                else:
                    marks += [(a, b) for a, b, shaded in row if shaded]
        for a, b in sorted(marks, reverse=True):
            if cell_text(body[a:b]):
                body = f"{body[:a]}<mark>{body[a:b]}</mark>{body[b:]}"
        out.append(article[pos:m.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


FIRST_CELL = re.compile(r"\s*<(t[dh])\b([^>]*)>(.*?)</\1\s*>", re.S)


def extend_rowspans(article):
    """Let a row label that spans a group of rows take the group's last row too.

    A \\multirow counted one row short leaves the group's last row starting
    with an empty cell, which reads as a row belonging to no group. The
    spanning cell is extended over it and the empty cell dropped.
    """
    out, pos = [], 0
    for table in re.finditer(r"<table\b", article):
        end = balanced_end(article, table.start(), "table")
        if table.start() < pos or end is None:
            continue
        body = article[table.start():end]
        if 'rowspan="' not in body or body.count("<table") > 1:
            continue
        rows = [[m.start(1), m.end(1)] for m in TABLE_ROW.finditer(body)]
        edits = []  # (start, end, replacement), in the table
        i = 0
        while i < len(rows):
            first = FIRST_CELL.match(body, rows[i][0], rows[i][1])
            span = first and re.search(r'\browspan="(\d+)"', first.group(2))
            if not span or not cell_text(first.group(3)):
                i += 1
                continue
            n = int(span.group(1))
            while i + n < len(rows):
                after = FIRST_CELL.match(body, rows[i + n][0], rows[i + n][1])
                if not after or "span=" in after.group(2) or cell_text(after.group(3)) or "<img" in after.group(3):
                    break
                # A row with one cell filled is a heading for what follows, not the group's last row.
                if sum(bool(cell_text(c.group(3))) for c in TABLE_CELL.finditer(body, *rows[i + n])) < 2:
                    break
                edits.append((after.start(), after.end(), ""))
                n += 1
            if n != int(span.group(1)):
                at = first.start(2) + span.start(1)
                edits.append((at, at + len(span.group(1)), str(n)))
            i += n
        if not edits:
            continue
        for a, b, text in sorted(edits, reverse=True):
            body = body[:a] + text + body[b:]
        out.append(article[pos:table.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


PANEL = re.compile(r'<figure\b[^>]*\bclass="[^"]*\bltx_figure_panel\b[^"]*"[^>]*>')


def panel_rows(table):
    """A panel table's rows as lists of whole cells, or None when a cell spans rows or columns."""
    if re.search(r'\b(?:row|col)span="', table):
        return None
    return [(row.start(1), [cell.group(0) for cell in TABLE_CELL.finditer(row.group(1))])
            for row in TABLE_ROW.finditer(table)]


def numeric_share(cells):
    """The share of a column's filled cells that hold a number."""
    texts = [t for t in (cell_text(re.sub(r"<math\b.*?</math>", "0", c, flags=re.S)) for c in cells) if t]
    return sum(bool(re.fullmatch(r"[-+−±<>≈~]?\$?\d[\d.,]*\s*[%KMBkx×]?", t)) for t in texts) / max(len(texts), 1)


def share_panel_labels(article):
    """Give a table panel the row labels it shares with the panel beside it.

    A float of several tables side by side often names the rows in the left
    panel only: the right one has the same rows in the same order and one
    column fewer, and read on its own its numbers belong to nothing. Each
    such panel gets the first column of the last panel that had one, when
    that column is names and the panel's own first column is numbers.
    """
    out, pos = [], 0
    labelled = None  # (end of its float, rows) of the last panel with a label column
    for m in PANEL.finditer(article):
        end = balanced_end(article, m.start(), "figure")
        table = re.search(r"<table\b", article[m.start():end or m.start()])
        if m.start() < pos or end is None or not table:
            continue
        begin = m.start() + table.start()
        table_end = balanced_end(article, begin, "table")
        rows = panel_rows(article[begin:table_end]) if table_end else None
        if not rows or len(rows) < 3 or len({len(cells) for _, cells in rows}) != 1:
            labelled = None
            continue
        width = len(rows[0][1])
        # Panels of one float follow each other with only layout between them.
        beside = labelled and not re.search(r"<(?:p|h\d|section)\b", article[labelled[0]:m.start()])
        if (beside and len(labelled[1]) == len(rows) and len(labelled[1][0][1]) == width + 1
                and numeric_share(cells[0] for _, cells in labelled[1]) < 0.2
                and numeric_share(cells[0] for _, cells in rows) > 0.6):
            body = article[begin:table_end]
            for (at, _), (_, cells) in reversed(list(zip(rows, labelled[1]))):
                body = body[:at] + cells[0] + body[at:]
            out.append(article[pos:begin])
            out.append(body)
            pos = table_end
            labelled = (end, labelled[1])
        else:
            labelled = (end, rows)
    return "".join(out) + article[pos:]


STYLE_WARNING = re.compile(
    r"(?:\w+ has been altered\.|The page layout violates the \w+ style\."
    r"|Please do not change the page layout, or include packages like[^.]*\."
    r"|We.re not able to reliably undo arbitrary changes to the style\."
    r"|Please remove the offending package\(s\), or layout-changing commands and try again\.|\s)+")


def drop_style_warnings(article):
    """Remove what a conference style file prints when a paper changed its margins.

    The ICML and UAI styles typeset "marginparsep has been altered. ... The
    page layout violates the ICML style." into the page; LaTeXML keeps the
    lines as the paper's first paragraphs, above the title.
    """
    def keep(m):
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(0))).split())
        return m.group(0) if not text or not STYLE_WARNING.fullmatch(text) else ""

    return re.sub(r'<div\b[^>]*class="ltx_para[^"]*"[^>]*>\s*<p\b[^>]*>(?:(?!</p>).)*</p>\s*</div>', keep, article, flags=re.S)


AUTHOR_NOTES = re.compile(r'<span\b[^>]*\bclass="ltx_author_notes"[^>]*>')
# Notes this long are a shared list (every affiliation of the paper), not one author's own.
SHARED_NOTES = 100


def tidy_authors(article):
    """Make the author block readable.

    A paper that sets all its affiliations in one \\thanks has the whole list
    after every author; a list already shown is dropped. An author macro
    LaTeXML does not know leaves "name=Ada Lovelace" and "affiliation=1" as
    separate authors; they become the name and its superscript.
    """
    begin = article.find('<div class="ltx_authors">')
    end = balanced_end(article, begin, "div") if begin >= 0 else None
    if end is None:
        return article
    block = article[begin:end]
    seen, out, pos = set(), [], 0
    for m in AUTHOR_NOTES.finditer(block):
        if m.start() < pos:
            continue
        close = balanced_end(block, m.start(), "span")
        if close is None:
            continue
        text = " ".join(re.sub(r"<[^>]+>", " ", block[m.start():close]).split())
        if len(text) >= SHARED_NOTES and text in seen:
            out.append(block[pos:m.start()])
            pos = close
        seen.add(text)
    block = "".join(out) + block[pos:]
    block = re.sub(r'(<span class="ltx_personname">\s*)name=', r"\1", block)
    block = re.sub(
        r'\s*</span>\s*</span>\s*<span class="ltx_author_before">\s*</span>\s*<span class="ltx_creator ltx_role_author">'
        r'\s*<span class="ltx_personname">\s*affiliation=([\d,\s]+?)\s*(?=</span>)',
        r"<sup>\1</sup>", block)
    return article[:begin] + block + article[end:]


FIGURE_PARTS = re.compile(r"<figure\b[^>]*>|</figure\s*>|<figcaption\b[^>]*>|</figcaption\s*>")


def split_captions(article):
    """Keep each caption by its own table when one float holds several.

    Four tables set in one float, each with a \\caption, arrive as one
    <figure> with four <figcaption>s. pandoc takes them together as the
    figure's caption, so all four would follow the last table. They become
    paragraphs, which stay where they are.
    """
    stack, captions = [], []  # open figures: [number of own captions]; (start, end, figure)
    figure_id = 0
    for m in FIGURE_PARTS.finditer(article):
        tag = m.group(0)
        if tag.startswith("<figure"):
            figure_id += 1
            stack.append([figure_id, 0])
        elif tag.startswith("</figure"):
            if stack:
                stack.pop()
        elif stack:
            if tag.startswith("<figcaption"):
                stack[-1][1] += 1
            captions.append((m.start(), m.end(), stack[-1][0], tag.startswith("</")))
    counts = {}
    for _, _, figure, closing in captions:
        counts[figure] = counts.get(figure, 0) + (not closing)
    out, pos = [], 0
    for start, end, figure, closing in captions:
        if counts[figure] < 2:
            continue
        out.append(article[pos:start])
        out.append("</p>" if closing else '<p class="ltx_p">')
        pos = end
    return "".join(out) + article[pos:]


# Font Awesome's style classes, which precede the icon's own "fa-<name>".
ICON = re.compile(r'<span\b[^>]*\bclass="[^"]*\bfa[srlbd]?\s[^"]*?\bfa-([a-z0-9-]+)[^"]*"[^>]*>\s*</span>')


def name_icons(article):
    """Write a Font Awesome icon as its name: an empty span "fas fa-lock" is
    "[lock]", so a table column of icons keeps what each cell says."""
    return ICON.sub(lambda m: f"[{m.group(1)}]", article)


def objects_to_images(article):
    """Replace each image <object data="..."> with an <img> of the same file."""
    return re.sub(
        r'<object\b[^>]*?\btype="image/[^"]*"[^>]*?\bdata="([^"]+)"[^>]*>.*?</object\s*>',
        r'<img src="\1" alt="" />',
        article,
        flags=re.S,
    )


HTML_BLOCK = re.compile(r"^<(table|dl)\b.*?^</\1>", re.S | re.M)
MARKED_MATH = re.compile("\ue000(.*?)\ue001|\ue002(.*?)\ue003", re.S)
PLAIN_NUMBER = re.compile(r"[-+−]?\d[\d.,]*%?")


def write_math(body):
    """Write each formula the filter marked (mark_math in arxiv-html.lua).

    In markdown it is $...$ or $$...$$. In a table written as HTML it is the
    same, where pandoc would render it into tags and lose what it cannot
    draw ("0.26 ± 0.002" came out as "0.26" and loose TeX); a plain number
    there is written bare, and a "<" that would open a tag is written "\\lt".
    """
    def tex(m, in_html=False):
        inline, display = m.group(1), m.group(2)
        if inline is None:
            return f"$${display}$$"
        if in_html:
            if PLAIN_NUMBER.fullmatch(inline.strip()):
                return inline.strip()
            inline = re.sub(r"<(?=[a-zA-Z/!])", r"\\lt ", inline)
        return f"${inline}$"

    body = HTML_BLOCK.sub(lambda block: MARKED_MATH.sub(lambda m: tex(m, True), block.group(0)), body)
    # A digit straight after the closing "$" would stop it closing the formula.
    body = MARKED_MATH.sub(lambda m: tex(m) + "\ue004", body)
    return re.sub("\ue004(?=\\d)", "<!-- -->", body).replace("\ue004", "")


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
    article = clean_math(article)
    article = drop_invisible(article)
    article = drop_style_warnings(article)
    article = name_icons(article)
    article = split_captions(article)
    article = tidy_authors(article)
    article = convert_listings(article)
    article = span_tabulars_to_tables(article)
    article = forest_trees(article, page)
    article = unresolved_refs(article)
    article = unresolved_citations(article, page)
    article = drop_undefined_macros(article)
    article = drop_tex_residue(article)
    article = fix_text_encoding(article)
    article = tidy_cells(article)
    article = extend_rowspans(article)
    article = share_panel_labels(article)
    article = mark_shading(article)
    article = bare_year_citations(article)
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
    body = write_math(body)
    # LaTeXML sometimes repeats a heading with nothing under the first copy
    # (an "Abstract" set both by the class and by the author).
    body = re.sub(r"^(#{1,6} .+)\n\n(?=\1\n)", "", body, flags=re.M)

    # In a table written as HTML, bold marks the result a row or column is
    # about, many times over: the short tag says the same in fewer tokens.
    body = re.sub(r"<(/?)strong>", r"<\1b>", body)

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
