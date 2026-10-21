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
12. Bold, italics, underlining and striking out are kept, and each footnote
    follows the paragraph or table it annotates (both in arxiv-html.lua).
    Cell shading and coloured text are kept as <mark> where the caption
    refers to them, with the colour's name when there are several (see
    mark_shading).
13. The names of macros LaTeXML did not know are dropped, a value and the
    deviation printed small after it are set apart, and a column title's
    raised line is read first (see drop_undefined_macros, tidy_cells).
14. A table panel gets the row labels it shares with the panel beside it,
    a row label spanning a group of rows takes the group's last row, a
    group's label every row of the group, a \\multirow LaTeXML dropped its
    span from the LaTeX source, and a cell's text continued on a row of its
    own joins it (see share_panel_labels, extend_rowspans, span_group_labels,
    source_row_spans, merge_continuation_rows).
15. A symbol set as a small picture becomes its file's name or what a vision
    model reads in it (see small_pictures, picture_text), and a link to the
    paper's own arXiv page an in-page link (see local_links).
"""

import base64
import collections
import colorsys
import functools
import gzip
import html
import html.entities
import io
import math
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import quote
from pathlib import Path

from lxml import etree

from paperlib import fetch, localize_figures, read_icon, to_webp

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
        # A badge set right after a value (a rank on a score, "42.0" ranked 3) would join it: "42.03".
        attached = re.sub(r"<[^>]*>", "", article[max(pos, begin - 300):begin])[-1:].isalnum()
        out.append(picture_text(article[begin:end], save, attached))
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


# The largest side, in pixels or points, of a picture that is a symbol in the text rather than a figure.
ICON_SIDE = 40


def icon_html(data):
    """A small picture as text (see paperlib.read_icon): a symbol as it is, a name as a
    label ("[OpenAI]"), "" for one that draws nothing; None when it was not read."""
    text = read_icon(data)
    if text is None:
        return None
    return html.escape(text if len(text) <= 2 else f"[{text}]")


def small_pictures(article, version):
    """Read the small pictures LaTeXML sets as <img> or <object> (a check mark in a
    table cell, a logo before a model's name), whose alt text is a placeholder.

    A file name that says what the picture is ("yes", "bert_bw") becomes its alt
    text; arXiv gives an <object> none at all, and pandoc drops it. Otherwise the
    picture is read by a vision model (icon_html) and replaced by what it shows.
    """
    def replace(m):
        tag, kind = m.group(0), m.group(1) or m.group(2)
        size = [int(v) for v in re.findall(r'\b(?:width|height)="(\d+)"', tag[:tag.index(">")])]
        src = re.search(r'\b(?:src|data)="([^"]+)"', tag)
        if len(size) != 2 or max(size) > ICON_SIDE or not src:
            return tag
        if kind == "img" and 'alt="[Uncaptioned image]"' not in tag:
            return tag
        path = html.unescape(src.group(1))
        name = Path(path).stem if not path.startswith("data:") else ""
        if name and not GENERIC_NAME.fullmatch(name):
            return tag if kind == "img" else f'<img src="{src.group(1)}" alt="{html.escape(name)}" />'
        if path.startswith("data:"):
            data = base64.b64decode(path.partition(",")[2] or "")
        elif re.match(r"\d{4}\.\d{4,5}v\d+/", path) or version:
            data = fetch("https://arxiv.org/html/" + (path if re.match(r"\d{4}\.\d{4,5}v\d+/", path) else f"{version}/{path}"))
        else:
            data = None
        reading = icon_html(data) if data else None
        return tag if reading is None else reading

    return re.sub(r'<(img)\b[^>]*>|<(object)\b[^>]*\btype="image/[^"]*"[^>]*>.*?</object\s*>',
                  replace, article, flags=re.S)


def picture_text(svg, save, attached=False):
    """What to put in the markdown for one LaTeXML picture.

    LaTeX boxes (tcolorbox and the like: definitions, findings, takeaways,
    prompt templates) come out of LaTeXML as an <svg> frame whose text sits in
    <foreignObject>s, so as an image their text would be lost. A picture
    is such a box when its text is mostly one block of at least twelve words,
    or when it is a plain frame (a few shapes) around a few blocks of text: it
    becomes a quote, its title (a short first block) in bold. Drawn with more
    than a few shapes, it is a diagram that holds a text block, and the image
    is kept too. A tiny picture holding a few words (a badge such as
    "+ MaTTS" in a table) becomes its text, in brackets when it is `attached`
    to the word before it ("42.0 (3)"). Anything else is saved as an image.
    """
    def image():
        return f'<img src="{save("svg+xml", svg.encode("utf-8"))}" alt="" />'

    kind = picture_kind(svg)
    # A TikZ node or a box sets its text in the medium series, which says nothing of the bold around it.
    blocks = [re.sub(r"\bltx_font_medium\b", "", block) for block in foreign_objects(svg)]
    if kind == "badge":
        return f"<span> ({' '.join(blocks)})</span>" if attached else f"<span>{' '.join(blocks)}</span>"
    if kind == "image":
        size = [float(v) for v in re.findall(r'\b(?:width|height)="([\d.]+)"', re.match(r"<svg\b[^>]*>", svg).group(0))]
        if len(size) == 2 and max(size) <= ICON_SIDE and not any(map(words, blocks)):
            # The same drawing used twice differs only in its ids.
            reading = icon_html(repair_svg(re.sub(r'\s(?:xml:)?id="[^"]*"', "", svg)).encode("utf-8"))
            if reading is not None:
                return reading
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


def close_runaway_floats(article):
    """End a float where the sections it has swallowed begin.

    A table LaTeXML could not close (a longtable at the end of a section)
    takes the rest of the paper into its <figure>: the following sections,
    the references, the appendices. pandoc prints a float's caption after its
    content, here after the paper's last line. The float is closed before the
    first of those sections, with the containers it opened; their closing
    tags, which end the float, go.
    """
    out, pos = [], 0
    for m in re.finditer(r"<figure\b[^>]*>", article):
        if m.start() < pos:
            continue
        end = balanced_end(article, m.start(), "figure")
        section = article.find("<section", m.end(), end) if end else -1
        if section < 0:
            continue
        head, tail = article[m.start():section], article[section:end]
        closing = re.search(r"((?:</div\s*>\s*)*)</figure\s*>$", tail)
        opened = len(re.findall(r"<div\b", head)) - len(re.findall(r"</div\s*>", head))
        swallowed = tail[:closing.start()]
        if ("<figcaption" not in head or opened != closing.group(1).count("</div")
                or len(re.findall(r"<section\b", swallowed)) != len(re.findall(r"</section\s*>", swallowed))
                or len(re.findall(r"<figure\b", head)) != len(re.findall(r"</figure\s*>", head)) + 1):
            continue
        out += [article[pos:m.start()], head, "</div>" * opened, "</figure>", swallowed]
        pos = end
    return "".join(out) + article[pos:]


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


def tabular_widths(segment):
    """The width of each of a span tabular's own rows, not those of the tabulars
    nested in its cells (a multi-line cell). A cell spanning columns counts as
    that many, and one spanning rows counts in each of them."""
    widths, kinds, below = [], [], {}  # below: row index -> width spanned into it from above
    for t in SPAN_TAG.finditer(segment):
        if t.group(0).startswith("</"):
            if kinds:
                kinds.pop()
            continue
        classes = re.search(r'\bclass="([^"]*)"', t.group(1))
        classes = classes.group(1).split() if classes else []
        kind = next((k for c, k in (("ltx_tabular", "tabular"), ("ltx_tr", "tr"), ("ltx_td", "td"))
                     if c in classes), None)
        if kinds.count("tabular") == 1:
            if kind == "tr":
                widths.append(below.pop(len(widths), 0))
            elif kind == "td" and widths:
                cols = re.search(r"\bltx_colspan_(\d+)\b", t.group(1))
                rows = re.search(r"\bltx_rowspan_(\d+)\b", t.group(1))
                cols, rows = int(cols.group(1)) if cols else 1, int(rows.group(1)) if rows else 1
                widths[-1] += cols
                for r in range(len(widths), len(widths) + rows - 1):
                    below[r] = below.get(r, 0) + cols
        kinds.append(kind)
    return widths


def is_layout_tabular(opening, segment):
    """Whether a span tabular is layout inside running text or math, not a table:
    a symbol stacked over a letter (esvect's \\vv), a \\makecell line break,
    one column of lines. A table has at least two columns in most of its rows,
    full-width group rows ("7B Models") and rows under a \\multirow included."""
    widths = tabular_widths(segment)
    return ("ltx_markedasmath" in opening or len(widths) < 2
            or sum(w >= 2 for w in widths) * 2 <= len(widths))


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


def local_links(article, version):
    """Make a link to a place in the paper's own arXiv page ("https://arxiv.org/html/2302.07730v4#S1.SS1",
    any version) the in-page link "#S1.SS1". Some renderings write their table of contents and
    cross-references that way, and they would leave the markdown."""
    if not version:
        return article
    paper = re.escape(version.rpartition("v")[0])
    return re.sub(rf'(<a\b[^>]*\bhref=")https?://arxiv\.org/html/{paper}(?:v\d+)?/?(?=#)', r"\1", article)


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


# ulem's \uline takes one token: "\uline 80.84" underlines the "8" alone.
PART_UNDERLINED = re.compile(r'(<span\b[^>]*\bclass="[^"]*\bltx_ulem_uu?line\b[^"]*"[^>]*>[\d.,]+)</span>([\d.,]*\d)')


def tidy_cells(article):
    """Set apart what LaTeX placed with a size, a colour or a raise.

    A deviation or a gain printed small or in colour after a table's value
    arrives with no space between them ("0.340.01", "70.9+2.3"); it gets one.
    A column title set on two lines arrives lower line first, the upper one
    raised above it ("Pro" then "Gemini 2.5"); the raised line goes first.
    A number underlined from its first digit only ("\\uline 80.84") is
    underlined whole.
    """
    article = PART_UNDERLINED.sub(r"\1\2</span>", article)
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


# "reduced by ~50%": a tilde typed for "about" after a space, which LaTeX sets
# as a non-breaking space, so the PDF prints none and the markdown a double space.
TYPED_TILDE = re.compile("(?<=[A-Za-z,;:]) \xa0(?=\\d)")


def fix_text_encoding(article):
    """A ">" or "<" typed in text comes out as "¿" or "¡" (the text font's
    encoding). Standing alone they are the comparison; before a letter they
    are Spanish and stay. A "~" typed between a word and a number is "about"
    in the prose; in a reference list ("pp. ~12") and a number's tag
    ("SuppFigure ~1") it is a space."""
    article = re.sub(r"(?<=[\s>])¿(?=[\s<])", "&gt;", article)
    article = re.sub(r"(?<=[\s>])¡(?=[\s<])", "&lt;", article)
    bib = re.search(r'<section\b[^>]*\bclass="[^"]*\bltx_bibliography\b', article)
    begin = bib.start() if bib else len(article)
    end = (balanced_end(article, begin, "section") or len(article)) if bib else begin

    def prose(text):
        return TEXT_NODE.sub(lambda m: m.group(0) if "ltx_tag" in m.group(1)
                             else m.group(1) + TYPED_TILDE.sub(" ~", m.group(2)), text)

    return prose(article[:begin]) + article[begin:end] + prose(article[end:])


BACKGROUND = re.compile(r"--ltx-bg-color:\s*#[0-9A-Fa-f]{6}")
SHADED_SPAN = re.compile(r"<span\b[^>]*--ltx-bg-color[^>]*>(.*?)</span>", re.S)
# Text set in a colour; black is no colour.
TEXT_COLOUR = re.compile(r"--ltx-fg-color:\s*#(?!000000)[0-9A-Fa-f]{6}")
COLOURED_SPAN = re.compile(r"<span\b[^>]*--ltx-fg-color:\s*#(?!000000)[^>]*>(.*?)</span>", re.S)
TABLE_FLOAT = re.compile(r'<figure\b[^>]*\bclass="[^"]*\bltx_table\b[^"]*"[^>]*>')
# An algorithm float, whose lines a caption may tell apart by colour, as a table's cells.
ALGORITHM_FLOAT = re.compile(r'<figure\b[^>]*\bclass="[^"]*\bltx_float_algorithm\b[^"]*"[^>]*>')
TABLE_ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr\s*>", re.S)
TABLE_CELL = re.compile(r"<(t[dh])\b([^>]*)>(.*?)</\1\s*>", re.S)
NAMES_SHADING = re.compile(r"colou?r|shad|highlight|gr[ae]y|background|\b(?:green|red|blue|yellow|orange|purple|pink|cyan)\b")
# Which shading is marked: "caption" (where the caption refers to it; the rule
# in use), "all" (wherever it picks out some rows or cells) or "none". The
# other two are for measuring the rule (experiments/table-emphasis).
SHADING = os.environ.get("PAPERLIB_SHADING", "caption")


def cell_text(fragment):
    return re.sub(r"<[^>]+>", "", fragment).strip()


def shaded_cells(float_html, colour=BACKGROUND, span=SHADED_SPAN):
    """A table float's rows as lists of (start, end, shaded) for each cell's
    content. A cell is shaded when it has a background colour, or nearly all
    its text sits in a span that has one. With TEXT_COLOUR and COLOURED_SPAN,
    the same for the colour of the text."""
    rows = []
    for row in TABLE_ROW.finditer(float_html):
        cells = []
        for cell in TABLE_CELL.finditer(row.group(1)):
            text = cell_text(cell.group(3))
            inner = "".join(cell_text(part) for part in span.findall(cell.group(3)))
            shaded = bool(colour.search(cell.group(2))) or (bool(text) and len(inner) >= 0.8 * len(text))
            cells.append((row.start(1) + cell.start(3), row.start(1) + cell.end(3), shaded))
        if cells:
            rows.append(cells)
    return rows


def table_only(float_html):
    """A table float without its captions, where a word may be coloured too."""
    return re.sub(r"<figcaption\b.*?</figcaption>", "", float_html, flags=re.S)


def table_columns(rows):
    """A table's columns, from rows of cells: those of its rows of full width."""
    width = max(map(len, rows))
    return [[r[c] for r in rows if len(r) == width] for c in range(width)]


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
    columns = table_columns(rows)
    # Under labels spanning several rows most rows are short, and a column of the few
    # full ones ("Prior" under each model) is not the table's column.
    if (2 * len(columns[0]) >= len(rows)
            and sum(sum(c) for c in columns if sum(c) >= 0.8 * len(c)) >= 0.9 * shaded):
        return "whole columns"
    return "some cells" if shaded <= total / 3 else "many cells"


# The colour words a caption names a table's colours by.
COLOUR_WORD = re.compile(r"\b(red|pink|orange|yellow|gold|green|olive|lime|cyan|teal|turquoise|blue|navy|purple"
                         r"|violet|magenta|brown|gr[ae]y)(?:ed|ish)?\b", re.I)
COLOUR_SYNONYMS = {"grey": "gray", "gold": "yellow", "olive": "green", "lime": "green", "teal": "cyan",
                   "turquoise": "cyan", "navy": "blue", "violet": "purple", "magenta": "pink"}
# The hues next to each that a caption may mean by it: "red" for a light red the hue calls pink.
NEAR_HUES = {"red": ("pink", "orange", "brown"), "pink": ("red", "purple"), "orange": ("red", "yellow", "brown"),
             "yellow": ("orange",), "brown": ("orange", "red"), "green": ("cyan",), "cyan": ("green", "blue"),
             "blue": ("cyan", "purple"), "purple": ("blue", "pink"), "gray": ()}
# A caption about the colour of the numbers rather than of the cells ("gray numbers", "grayed out").
TEXT_IN_COLOUR = re.compile(r"\b(?:red|pink|orange|yellow|gold|green|cyan|teal|blue|purple|violet|brown|gr[ae]y)"
                            r"\s+(?:numbers?|text|font|values?|entries|scores?|words?)\b|\bgr[ae]yed\b", re.I)
LAYER_COLOUR = {"bg": re.compile(r"--ltx-bg-color:\s*(#[0-9A-Fa-f]{6})"),
                "fg": re.compile(r"--ltx-fg-color:\s*(#[0-9A-Fa-f]{6})")}
# Colours that mark nothing: black or white, as text or as a fill. White text and a
# black fill go with a fill or a text of another colour, which is the one marked.
NO_COLOUR = ("white", "black")


def hue_name(hex_colour):
    """The plain name of a colour ("#B22222" is "red", "#E6E6E6" "gray")."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, saturation = colorsys.rgb_to_hls(r, g, b)
    hue *= 360
    if saturation < 0.15 or max(r, g, b) - min(r, g, b) < 0.08:
        return "black" if light < 0.12 else "white" if light > 0.97 else "gray"
    for bound, name in ((15, "red"), (45, "orange"), (70, "yellow"), (165, "green"), (195, "cyan"),
                        (255, "blue"), (290, "purple"), (345, "pink"), (361, "red")):
        if hue < bound:
            if name == "red" and light > 0.8:
                return "pink"
            return "brown" if name == "orange" and light < 0.35 else name


MATH_ELEMENT = re.compile(r"<math\b([^>]*)>(.*?)</math>", re.S)
MATH_TOKEN = re.compile(r"<(m[ino]|mtext)\b([^>]*)>(.*?)</\1>", re.S)


def math_colour(attrs, inner, layer):
    """The colour a formula is set in, from its own style or from the colour of most of
    its symbols, or None. LaTeXML colours each symbol of a \\textcolor'd formula, and
    may set one back in black ("+15%" with the "%" in black)."""
    own = LAYER_COLOUR[layer].search(attrs)
    if own and hue_name(own.group(1)) not in NO_COLOUR:
        return own.group(1).lower()
    lengths, total = {}, 0
    for token in MATH_TOKEN.finditer(inner):
        size = len(re.sub("[\u200b\u2061-\u2064]", "", cell_text(token.group(3))))  # invisible operators
        total += size
        colour = LAYER_COLOUR[layer].search(token.group(2))
        if colour and hue_name(colour.group(1)) not in NO_COLOUR:
            lengths[colour.group(1).lower()] = lengths.get(colour.group(1).lower(), 0) + size
    best = max(lengths, key=lengths.get, default=None)
    return best if best and lengths[best] >= 0.5 * total else None


def coloured_spans(fragment, layer):
    """(start, end, colour) of each span of a fragment set in a colour, its content's
    bounds, and of each formula set in one, the whole <math> element's."""
    out = []
    for m in re.finditer(rf'<span\b[^>]*--ltx-{layer}-color:\s*(#[0-9A-Fa-f]{{6}})[^>]*>', fragment):
        end = balanced_end(fragment, m.start(), "span")
        colour = m.group(1).lower()
        # A \phantom in a text colour shows nothing; in a background colour it is a box.
        if end and hue_name(colour) not in NO_COLOUR and not (layer == "fg" and "ltx_phantom" in m.group(0)):
            out.append((m.end(), fragment.rindex("</span", 0, end), colour))
    for m in MATH_ELEMENT.finditer(fragment):
        colour = math_colour(m.group(1), m.group(2), layer) if f"--ltx-{layer}-color" in m.group(0) else None
        if colour:
            out.append((m.start(), m.end(), colour))
    return sorted(out)


def cell_colours(float_html, layer):
    """A table float's rows as lists of (start, end, colour) for each cell's content:
    the colour of its background ("bg") or text ("fg"), or None. A cell has a colour
    when its own style sets it, or nearly all its text sits in spans of that colour."""
    rows = []
    for row in TABLE_ROW.finditer(float_html):
        cells = []
        for cell in TABLE_CELL.finditer(row.group(1)):
            own = LAYER_COLOUR[layer].search(cell.group(2))
            colour = own.group(1).lower() if own else None
            if colour is None or hue_name(colour) in NO_COLOUR:
                colour, text = None, len(cell_text(cell.group(3)))
                inner = {}
                for a, b, c in coloured_spans(cell.group(3), layer):
                    inner[c] = inner.get(c, 0) + len(cell_text(cell.group(3)[a:b]))
                best = max(inner, key=inner.get, default=None)
                if best and text and inner[best] >= 0.8 * text:
                    colour = best
            cells.append((row.start(1) + cell.start(3), row.start(1) + cell.end(3), colour))
        if cells:
            rows.append(cells)
    return rows


def caption_colours(caption, colours, inside=()):
    """{(layer, colour): name} for the table's colours the caption refers to: those it
    names ("the red denotes the highest"), by its own word, and those its own text is
    set in (a legend: "✓ explicitly covered" with the ✓ in green), by their hue. A word
    is matched to the colours of whole cells first, and to colours `inside` cells (a
    word, a formula) only when it fits none of those: "red" is the light red of the
    best cells, not a model's name set in a brand red."""
    words = dict.fromkeys(w.group(1).lower() for w in COLOUR_WORD.finditer(cell_text(caption)))
    referred = {}
    for pool in (colours, inside):
        named = set(referred.values())
        for near in (False, True):
            for word in words:
                base = COLOUR_SYNONYMS.get(word, word)
                if word in named or (near and word in referred.values()):
                    continue
                for key in pool:
                    if key not in referred and hue_name(key[1]) in (NEAR_HUES.get(base, ()) if near else (base,)):
                        referred[key] = word
    # A legend's box may be text in the colour the cells are shaded in ("◼ data").
    every = set(colours) | set(inside)
    for layer, other in (("bg", "fg"), ("fg", "bg")):
        for _, _, colour in coloured_spans(caption, layer):
            key = next((k for k in ((layer, colour), (other, colour)) if k in every), None)
            if key and key not in referred:
                referred[key] = hue_name(colour)
    # A colour named for both the cells and their text is the one the caption's words point at.
    by_label = {}
    for (layer, colour), label in referred.items():
        by_label.setdefault(label, set()).add(layer)
    keep = "fg" if TEXT_IN_COLOUR.search(cell_text(caption)) else "bg"
    return {key: label for key, label in referred.items() if len(by_label[label]) == 1 or key[0] == keep}


def table_notes(body):
    """(start, end) of each note set under a table in its float ("Note: ... The red bold
    is used when ..."), outside the table and its caption."""
    tables = [(m.start(), balanced_end(body, m.start(), "table") or m.end()) for m in re.finditer(r"<table\b", body)]
    notes = []
    for m in re.finditer(r"<p\b[^>]*>", body):
        end = balanced_end(body, m.start(), "p")
        if end and not any(a <= m.start() < b for a, b in tables) and re.match(r"\s*notes?\b", cell_text(body[m.end():end]), re.I):
            notes.append((m.start(), end))
    return notes


# A caption that tells shades of a colour apart: "dark green", "darker red", "the shade of the fonts".
SHADE_WORDS = re.compile(r"\b(?:dark|deep|light|pale)(?:er|est)?\b|\bshades?\b|\bintensity\b|\bgradient\b", re.I)
# The names of n shades of one colour, darkest first.
SHADES = {2: ("dark", "light"), 3: ("dark", "", "light"), 4: ("darkest", "dark", "light", "lightest"),
          5: ("darkest", "dark", "", "light", "lightest")}


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def shade_names(referred, caption):
    """Tell apart the shades of one colour the caption refers to by one name ("green"
    for the best and the second best) by their lightness, "dark-green" and
    "light-green", where the caption tells shades apart ("the dark green ... the light
    green", "darker red means more") or shows each in a legend of its own; else they
    keep the one name. Beside a plain "green" in the caption, "light green" leaves the
    darker shade plain "green". Up to five shades are named, darkest to lightest."""
    by_label = {}
    for (_, colour), label in referred.items():
        by_label.setdefault(label, set()).add(colour)
    text = cell_text(caption).lower()
    legend = {c for layer in ("fg", "bg") for _, _, c in coloured_spans(caption, layer)}
    names = {}
    for label, colours in by_label.items():
        # Over five shades, a scale of the values the cells hold anyway.
        if not 2 <= len(colours) <= 5 or not (SHADE_WORDS.search(text) or colours <= legend):
            continue
        colours = sorted(colours, key=luminance)
        shades = [f"{shade}-{label}" if shade else label for shade in SHADES[len(colours)]]
        if len(colours) == 2 and re.search(rf"\b{label}\b", re.sub(rf"\b(?:dark|deep|light|pale)(?:er)?\s+{label}\b", "", text)):
            dark, light = (re.search(rf"\b(?:{w})(?:er)?\s+{label}\b", text) for w in ("dark|deep", "light|pale"))
            shades = [label if light and not dark else shades[0], label if dark and not light else shades[1]]
        names.update(zip(colours, shades))
    return {key: names.get(key[1], label) for key, label in referred.items()}


def mark_named_colours(body, borrowed=""):
    """Mark the cells of each colour a table's caption refers to, with the colour's
    name where the table has several (<mark class="red">), or None if it refers to none.
    Colour on part of a cell (a word, a formula, a bullet) is marked where it is, as is
    colour in a float without cells (an algorithm's lines). A note under the table
    counts as caption; `borrowed` is the caption of the table a caption names no
    colours of its own for ("The color format is the same as in Table 2")."""
    layers = {layer: cell_colours(body, layer) for layer in ("bg", "fg")}
    captions = [(m.start(), m.end()) for m in re.finditer(r"<figcaption\b.*?</figcaption>", body, re.S)]
    captions = sorted(captions + (table_notes(body) if TABLE_FLOAT.match(body) else []))
    caption = " ".join(body[a:b] for a, b in captions)
    if borrowed and not COLOUR_WORD.search(cell_text(caption)):
        caption += " " + borrowed
    parts = {layer: [(a, b, c) for a, b, c in coloured_spans(body, layer)
                     if not any(x <= a < y for x, y in captions)] for layer in layers}
    colours = {(layer, c) for layer, rows in layers.items() for row in rows for _, _, c in row if c}
    inside = {(layer, c) for layer, found in parts.items() for _, _, c in found} - colours
    referred = shade_names(caption_colours(caption, colours, inside), caption)
    colours |= inside
    marks = []  # (start, end, label), and "■" for a legend's empty box
    for (layer, colour), label in referred.items():
        cells = layers[layer]
        flags = [[c == colour for _, _, c in row] for row in cells]
        pattern = shading_pattern(flags)
        found = []
        if pattern == "whole columns":
            for column in table_columns(cells):
                if sum(c == colour for _, _, c in column) >= 0.8 * len(column):
                    found.append((*column[0][:2], label))
        # A header row is marked too when the caption names its colour ("Orange section: ...").
        elif pattern in ("some rows", "some cells", "many cells", "header row"):
            for row, row_flags in zip(cells, flags):
                if len(row) > 1 and all(row_flags[1:]):
                    found.append((*row[0][:2], label))
                else:
                    found += [(a, b, label) for a, b, c in row if c == colour]
        whole = [(a, b) for row in cells for a, b, c in row if c == colour]
        found += [(a, b, label) for a, b, c in parts[layer] if c == colour and not any(x <= a < y for x, y in whole)]
        if not found:
            continue
        marks += found
        # A legend in the caption: its coloured mark (an empty box is "■") says which is which.
        for a, b in captions:
            for x, y, c in coloured_spans(body[a:b], "fg") + coloured_spans(body[a:b], "bg"):
                if c == colour and not re.search(rf"\b{label.split('-')[-1]}", cell_text(body[a + x:a + y]), re.I):
                    marks.append((a + x, a + y, label, "■"))
    if not marks:
        return None
    plain = len({m[2] for m in marks}) == 1 and len(colours) == 1
    kept, reach = [], -1
    for mark in sorted(set(marks)):
        if mark[0] >= reach:  # a span inside one already marked is not marked again
            kept.append(mark)
            reach = mark[1]
    for a, b, label, *box in reversed(kept):
        shown = re.sub(r'<span style="visibility:hidden">.*?</span>', "", body[a:b], flags=re.S)
        inner = body[a:b] if cell_text(shown) else "".join(box)
        if inner:
            tag = "<mark>" if plain else f'<mark class="{label}">'
            body = f"{body[:a]}{tag}{inner}</mark>{body[b:]}"
    return body


def mark_shading(article, rule=None):
    """Keep the cell shading that says something, as <mark>.

    Markdown has no cell colour, and most shading says nothing a reader of
    the whole paper lacks: a header, every other row, the paper's own method.
    It is kept only where the caption refers to it ("gray rows are ..."),
    since the caption would otherwise point at nothing: a shaded cell's
    content is marked, a row shaded from end to end on its first cell only,
    a shaded column on its top cell. Where the caption names a colour, or
    shows it in a legend of its own ("✓ explicitly covered" with the ✓ in
    green), the cells in that colour are marked, the colour's name added
    when the table has several (<mark class="red">), and the legend's marks
    too (see mark_named_colours): coloured words or formulas inside a cell
    as well, and an algorithm's lines whose colours its caption shows.
    Several colours the caption does not refer to are left alone, as one
    mark cannot say which colour a cell had.

    A table without shading whose caption refers to the colour of its text
    ("excluded topics are in gray") is treated the same: its cells set
    wholly in the one colour are the shaded ones.
    """
    rule = rule or SHADING
    if rule == "none":
        return article
    out, pos = [], 0
    floats = sorted([*TABLE_FLOAT.finditer(article), *ALGORITHM_FLOAT.finditer(article)], key=lambda m: m.start())
    # Each table's caption by its anchor, for a caption that names another table's colours.
    table_captions = {}
    for m in TABLE_FLOAT.finditer(article):
        anchor = re.search(r'\bid="([^"]+)"', m.group(0))
        caption = re.search(r"<figcaption\b.*?</figcaption>", article[m.start():balanced_end(article, m.start(), "figure") or m.end()], re.S)
        if anchor and caption:
            table_captions[anchor.group(1)] = caption.group(0)
    for m in floats:
        end = balanced_end(article, m.start(), "figure")
        if m.start() < pos or end is None:
            continue
        body = article[m.start():end]
        caption = " ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S))
        borrowed = ""
        if NAMES_SHADING.search(cell_text(caption).lower()) and not COLOUR_WORD.search(cell_text(caption)):
            borrowed = next((table_captions[a] for a in re.findall(r'href="#([^"]+)"', caption) if a in table_captions), "")
        named = mark_named_colours(body, borrowed) if rule == "caption" else None
        if named is not None:
            out += [article[pos:m.start()], named]
            pos = end
            continue
        if ALGORITHM_FLOAT.match(m.group(0)):
            continue
        colour = BACKGROUND
        rows = shaded_cells(body) if "--ltx-bg-color" in body else []
        if not rows and "--ltx-fg-color" in body:
            colour = TEXT_COLOUR
            rows = shaded_cells(body, TEXT_COLOUR, COLOURED_SPAN)
        if not any(shaded for row in rows for _, _, shaded in row):
            continue
        flags = [[shaded for _, _, shaded in row] for row in rows]
        pattern = shading_pattern(flags)
        caption = cell_text(" ".join(re.findall(r"<figcaption\b.*?</figcaption>", body, re.S))).lower()
        named = bool(NAMES_SHADING.search(caption))
        if rule == "caption":
            # A caption names the colour of text in that colour ("in gray").
            colours = {c.lower() for c in colour.findall(body if colour is BACKGROUND else table_only(body))}
            wanted = (named and len(colours) == 1
                      and pattern in ("some rows", "some cells", "many cells", "whole columns"))
        else:
            wanted = pattern in ("some rows", "some cells", "many cells")
        if not wanted:
            continue
        marks = []
        if pattern == "whole columns":
            for column in table_columns(rows):
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
    spanning cell is extended over it and the empty cell dropped. A rule ends
    the group, and several empty cells above a lone label are that label's
    group (a \\multirow{-n} on its last row; see span_group_labels).
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
            dropped = []
            while i + n < len(rows):
                after = FIRST_CELL.match(body, rows[i + n][0], rows[i + n][1])
                if (not after or "span=" in after.group(2) or re.search(r"\bltx_border_tt?\b", after.group(2))
                        or cell_text(after.group(3)) or "<img" in after.group(3)):
                    break
                # A row with one cell filled is a heading for what follows, not the group's last row.
                if sum(bool(cell_text(c.group(3))) for c in TABLE_CELL.finditer(body, *rows[i + n])) < 2:
                    break
                dropped.append((after.start(), after.end(), ""))
                n += 1
            below = FIRST_CELL.match(body, *rows[i + n]) if i + n < len(rows) else None
            if len(dropped) > 1 and below and "span=" not in below.group(2) and cell_text(below.group(3)):
                n, dropped = int(span.group(1)), []
            if dropped:
                at = first.start(2) + span.start(1)
                edits += dropped + [(at, at + len(span.group(1)), str(n))]
            i += n
        if not edits:
            continue
        for a, b, text in sorted(edits, reverse=True):
            body = body[:a] + text + body[b:]
        out.append(article[pos:table.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


def head_through(body, first, last):
    """Edits that make a table's head the rows from `first` to `last` (offsets
    in the table): the head's end moved there, or a head opened."""
    close = re.search(r"</thead\s*>\s*<tbody\b[^>]*>", body)
    if close:
        return [(close.start(), close.end(), ""), (last, last, close.group(0))] if close.start() < last else []
    tbody = re.search(r"<tbody\b[^>]*>\s*$", body[:first])
    if tbody:
        return [(tbody.start(), tbody.end(), "<thead>"), (last, last, "</thead><tbody>")]
    end = body.rindex("</table")
    return [(first, first, "<thead>"), (last, last, "</thead><tbody>"), (end, end, "</tbody>")]


# A number as a table prints it: "1e-5", "336M", "-0.3%", "~10K".
NUMBER = r"[-+−~≈<>]?\d[\d.,]*(?:[eE][-+−]?\d+)?\s*[%KMBTkx×]?"


def table_grid(body):
    """Where each cell of a table sits: {(row, column): (row, column, cell, rows, columns)}
    for every position a cell covers, its own first among them, and the table's rows."""
    rows = list(TABLE_ROW.finditer(body))
    at = {}
    for r, row in enumerate(rows):
        col = 0
        for cell in TABLE_CELL.finditer(body, row.start(1), row.end(1)):
            while (r, col) in at:
                col += 1
            down, across = (int(m.group(1)) if (m := re.search(rf'\b{k}span="(\d+)"', cell.group(2))) else 1
                            for k in ("row", "col"))
            for i in range(min(down, len(rows) - r)):
                for j in range(across):
                    at.setdefault((r + i, col + j), (r, col, cell, down, across))
            col += across
    return rows, at


def span_group_labels(article):
    """Give a row group's label to every row of the group.

    A rule marks off a group of rows, and its label is written once: on the
    group's last row by a \\multirow{-2} (which reaches up, the way to span
    rows that have a \\rowcolor), on its middle row by an author centring it
    by hand, or with a \\multirow counted short ("Coupling" over five rows of
    seven). LaTeXML leaves it there, so it names one row or a few and the
    others read as belonging to no group. In each column, a group between two
    rules whose only filled cell is a word (not a "✓" or a number) spans the
    group from its first row; in a table without spans, which stays a pipe
    table, the label moves to the first row instead. Outside the first column
    only a label below the first row or spanning short is moved: one typed on
    the first row may be the first of a list. It is done only in a column
    where other groups have labels too and no group mixes several filled
    cells with empty ones (results left blank). A header
    written that way ("Metric" under an empty cell) is raised only in a table
    with spans, of up to five rows, taking the header's rows into the head
    with it (see head_through): pandoc cuts a span where the head ends.
    """
    def rule_above(at, r, c):
        own = at.get((r, c))
        above = at.get((r - 1, c))
        return r == 0 or bool(own and own[0] == r and re.search(r"\bltx_border_tt?\b", own[2].group(2))
                              or above and above[0] + above[3] == r and re.search(r"\bltx_border_bb?\b", above[2].group(2)))

    def filled(cell):
        return bool(cell_text(cell.group(3)) or "<img" in cell.group(3))

    def is_label(fragment, column):
        """A word, not a mark ("✓") or a formula; outside the first column, where a group
        is named "4B", not a number either ("1e-5", "336M")."""
        text = cell_text(re.sub(r"<math\b.*?</math>", " ", fragment, flags=re.S))
        return bool(re.search(r"[^\W\d_]", text)) and not (column and re.fullmatch(NUMBER, text))

    out, pos = [], 0
    for table in re.finditer(r"<table\b", article):
        end = balanced_end(article, table.start(), "table")
        if table.start() < pos or end is None:
            continue
        body = article[table.start():end]
        if "ltx_border_t" not in body or body.count("<table") > 1:
            continue
        rows, at = table_grid(body)
        spans = bool(re.search(r'\b(?:row|col)span="(?!1")\d+"', body))
        edits = []
        for c in range(1 + max((col for _, col in at), default=-1)):
            starts = [r for r in range(len(rows)) if rule_above(at, r, c)] + [len(rows)]
            groups = []  # (first row, end row, the group's cells in this column, top to bottom)
            for a, b in zip(starts, starts[1:]):
                owners = [at.get((r, c)) for r in range(a, b)]
                if all(o and o[1] == c and o[4] == 1 for o in owners):
                    groups.append((a, b, list(dict.fromkeys((o[0], o[2], o[3]) for o in owners))))
                else:
                    groups.append((a, b, None))
            # Several filled cells and empty ones in one group: blanks there are values left out.
            mixed = any(cells and 1 < sum(filled(x) for _, x, _ in cells) < len(cells) for a, _, cells in groups if a > 0)
            for a, b, cells in groups:
                if not cells or b - a < 2 or (a == 0 and c > 0) or (a > 0 and mixed):
                    continue
                labels = [(r, x, n) for r, x, n in cells if filled(x)]
                if len(labels) != 1 or (labels[0][0] == a and labels[0][2] >= b - a):
                    continue
                r, label, n = labels[0]
                # Outside the first column, an entry on its group's first row is as the author typed it:
                # shared by the rows, or the first of a list beside a longer one.
                if c > 0 and r == a and n == 1:
                    continue
                if a == 0 and (not spans or b - a > 5 or b == len(rows) or r + n != b or n > 1):
                    continue
                if a > 0 and (not is_label(label.group(3), c)
                              or not any(filled(x) for d, _, others in groups if d > 0 and d != a and others
                                         for _, x, _ in others)):
                    continue
                top = cells[0][1]
                if spans or a == 0:
                    edits += [(x.start(), x.end(), "") for _, x, _ in cells[1:]]
                    if top is not label:
                        edits.append((top.start(3), top.end(3), label.group(3)))
                    old = re.search(r'\s*\browspan="\d+"', top.group(2))
                    at_attr = top.start(2) + old.start() if old else top.start(2)
                    edits.append((at_attr, top.start(2) + old.end() if old else at_attr, f' rowspan="{b - a}"'))
                elif top is not label:
                    edits += [(top.start(3), top.end(3), label.group(3)), (label.start(3), label.end(3), "")]
                if a == 0:
                    edits += head_through(body, rows[0].start(), rows[b - 1].end())
        if not edits:
            continue
        for a, b, text in sorted(edits, reverse=True):
            body = body[:a] + text + body[b:]
        out.append(article[pos:table.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


# A cell's text that goes on in the next row ("Factivity,", "(Fine-", "Human &") or
# carries on from the row before ("& Generative", "grained)"); a whole parenthesis
# is a citation or a note on the row above ("(Socher et al., 2013b)", "(O/E +1.84%)"),
# but "[73] - image classification" and "(r) cut text" are items of their own.
GOES_ON = re.compile(r"(?:[,/&(\[;-]|\b(?:and|or|of|with|for|the|a|in|to|on|by))$")
CARRIES_ON = re.compile(r"^(?:[&,;)\]]|\([^()]*\)$|\[[^\[\]]*\]$)")


def merge_continuation_rows(article):
    """Join a cell's text that an author continued on a new table row.

    A long cell is broken by starting a new row with the other cells empty: a
    citation under a model's name, the second line of a column title ("PlaNet"
    over "MobileNet"), a list going on under a row label. LaTeXML keeps those
    rows, which read as rows of their own. A row with no rule above it, no
    number or mark, and text in at most half the columns, is joined to the row
    above it, cell to cell, when each fragment and the text it joins read as
    one: the upper ends as if it goes on ("Factivity,", "Human &") or the
    lower starts as if it carries on ("(Socher et al., 2013b)", "& Generative");
    to the row below instead when that is how the fragment reads with it
    ("Pointwise, Pairwise," over "& Generative"). Separate items under a
    spanning label ("Synchronization", "Mood") stay rows, and so does a cell
    spanning columns or rows, a formula or a picture. In a header (the
    <thead>, or the rows above a rule under the first few) a fragment joins
    the title above it whatever it reads like, in every column but the first
    (where "CIFAR-10" under "Model" is a sub-heading), both being
    short as titles are: "Error rate" over "(Fine-" over "grained)", "PlaNet"
    over "MobileNet". A table of one
    column, a box of text, keeps its lines. The joined row's spans shrink by
    one.
    """
    def text(cell):
        return cell_text(re.sub(r"<math\b.*?</math>", " M ", cell.group(3), flags=re.S))

    def ruled(cell, side):
        return bool(re.search(rf"\bltx_border_{side}{side}?\b", cell.group(2)))

    def join(upper, lower):
        upper, lower = upper.strip(), lower.strip()
        if not upper or not lower:
            return upper or lower
        glue = "" if re.search(r"[-/(]$", cell_text(upper)) else " "
        return upper + glue + lower

    def merge_once(body):
        rows, at = table_grid(body)
        width = 1 + max((c for _, c in at), default=-1)
        if width < 2:
            return None  # a box of text (a prompt), its lines in rows
        # The header: the rows above the rule under the first few (a rule above a row's cells,
        # below the last row's, or drawn as a row of its own), and at least a <thead>'s.
        thead = re.search(r"<thead\b.*?</thead\s*>", body, re.S)
        head = max(sum(1 for row in rows if row.start() < thead.end()) if thead else 0,
                   next((r for r in range(1, min(len(rows), 5)) if any(
                       ruled(o[2], "t") and o[0] == r or ruled(o[2], "b") and o[0] + o[3] == r
                       for (i, c), o in at.items() if i in (r, r - 1) and (i == r) == (o[0] == r))
                       or "ltx_rule" in rows[r].group(1) and not cell_text(rows[r].group(1))), 0))
        for f in range(len(rows)):
            own = {c: o for (r, c), o in at.items() if r == f and o[0] == f and o[1] == c}
            if not own or any(o[3] > 1 or o[4] > 1 for o in own.values()):
                continue
            filled = {c: o[2] for c, o in own.items() if text(o[2]) or re.search(r"<(?:img|svg|object|math)\b", o[2].group(3))}
            if (not filled or (f >= head and len(filled) > max(1, width // 2)) or any(ruled(o[2], "t") for o in own.values())
                    or any(re.search(r"<(?:img|svg|object|math)\b", x.group(3)) or not re.search(r"[^\W\d_]", text(x))
                           or re.fullmatch(NUMBER, text(x)) for x in filled.values())):
                continue
            # A fragment going on downwards, else the row above it continued; in the body,
            # each fragment and the text it joins must read as one ("Factivity," | "Symmetry").
            down = f + 1 < len(rows) and all(
                (o := at.get((f + 1, c))) and o[0] == f + 1 and o[1] == c and o[3] == 1 and not ruled(o[2], "t")
                and text(o[2]) and (GOES_ON.search(text(x)) or CARRIES_ON.match(text(o[2])))
                for c, x in filled.items())
            m = f + 1 if down else f - 1
            if m < 0 or (not down and any(ruled(at[(f - 1, c)][2], "b") for c in range(width) if (f - 1, c) in at)):
                continue
            targets = {c: at.get((m, c)) for c in filled}
            if not all(o and o[0] == m and o[1] == c and o[3] == 1 and o[4] == 1 for c, o in targets.items()):
                continue
            # In a header only the first column, the row labels' title, needs it: a word under
            # "Model" there is a sub-heading ("CIFAR-10") as often as the title's second line.
            if not down and not all(text(targets[c][2]) and (GOES_ON.search(text(targets[c][2]))
                                                             or CARRIES_ON.match(text(x)))
                                    for c, x in filled.items() if f >= head or c == 0 and text(targets[c][2])):
                continue
            # A column title is short; a header that holds an example's text is not one to join.
            if f < head and not all(len(text(x)) <= 25 and len(text(x).split()) <= 3
                                    and len(text(t[2])) <= 40 and len(text(t[2]).split()) <= 5
                                    for c, x in filled.items() for t in [targets[c]]):
                continue
            edits = []
            for c, x in filled.items():
                t = targets[c][2]
                merged = join(x.group(3), t.group(3)) if down else join(t.group(3), x.group(3))
                edits.append((t.start(3), t.end(3), merged))
            row = rows[f]
            edits.append((row.start(), row.end(), ""))
            for (r, c), o in at.items():
                if (r, c) == (o[0], o[1]) and o[0] < f < o[0] + o[3]:
                    span = re.search(r'\browspan="(\d+)"', o[2].group(2))
                    edits.append((o[2].start(2) + span.start(), o[2].start(2) + span.end(),
                                  f'rowspan="{o[3] - 1}"' if o[3] > 2 else ""))
            for a, b, new in sorted(edits, reverse=True):
                body = body[:a] + new + body[b:]
            return body
        return None

    out, pos = [], 0
    for table in re.finditer(r"<table\b", article):
        end = balanced_end(article, table.start(), "table")
        if table.start() < pos or end is None:
            continue
        body = article[table.start():end]
        if body.count("<table") > 1:
            continue
        changed = False
        for _ in range(200):
            merged = merge_once(body)
            if merged is None:
                break
            body, changed = merged, True
        if not changed:
            continue
        out.append(article[pos:table.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


TEX_TABULAR = re.compile(r"\\(begin|end)\{(tabular\*?|tabularx|tabulary|longtable\*?|NiceTabular\*?)\}")
# What may open a row of a tabular before its first cell: rules, colours, spacing.
TEX_ROW_PREFIX = re.compile(
    r"\s*(?:\\(?:hline|toprule|midrule|bottomrule|endhead|endfirsthead|endfoot|endlastfoot|hdashline|Xhline|"
    r"tabucline|morecmidrules)\b(?:\{[^}]*\})?|\\(?:cline|hhline|arrayrulecolor|specialrule|rowcolor|cdashline)"
    r"(?:\[[^\]]*\])?(?:\{[^}]*\})+|\\cmidrule\s*(?:\([^)]*\))?\s*\{[^}]*\}|\\addlinespace\b(?:\[[^\]]*\])?|"
    r"\\noalign\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\[[-\d.]+\s*(?:pt|em|ex|mm|cm)\])")


def tex_argument(tex, at):
    """The text of the braced argument opening at `at` (skipping blanks), and where it ends; or (None, at)."""
    while at < len(tex) and tex[at] in " \t\n":
        at += 1
    if at >= len(tex) or tex[at] != "{":
        return None, at
    depth = 0
    for i in range(at, len(tex)):
        depth += {"{": 1, "}": -1}.get(tex[i], 0) if tex[i - 1] != "\\" else 0
        if depth == 0:
            return tex[at + 1:i], i + 1
    return None, at


def tex_split(tex, separator):
    """`tex` cut at each `separator` ("\\\\" or "&") outside braces and nested tabulars."""
    parts, start, depth, nested, i = [], 0, 0, 0, 0
    while i < len(tex):
        ch = tex[i]
        if ch == "\\":
            env = TEX_TABULAR.match(tex, i)
            if env:
                nested += 1 if env.group(1) == "begin" else -1
                i = env.end()
                continue
            if separator == "\\\\" and tex.startswith("\\\\", i) and depth == 0 and nested == 0:
                parts.append(tex[start:i])
                i += 2
                start = i
                continue
            if tex.startswith("\\tabularnewline", i) and separator == "\\\\" and depth == 0 and nested == 0:
                parts.append(tex[start:i])
                i += len("\\tabularnewline")
                start = i
                continue
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == separator and depth == 0 and nested == 0:
            parts.append(tex[start:i])
            start = i + 1
        i += 1
    parts.append(tex[start:])
    return parts


def tex_tabulars(tex):
    """The tabulars of a LaTeX source, each its rows, each row its cells as
    (column, columns spanned, rows spanned by a \\multirow or 0 without one, label words)."""
    out, stack = [], []
    for m in TEX_TABULAR.finditer(tex):
        if m.group(1) == "begin":
            stack.append(m)
            continue
        if not stack:
            continue
        begin = stack.pop()
        if stack:
            continue  # a tabular inside a cell is part of that cell
        at = begin.end()
        if re.match(r"\s*\[", tex[at:]):
            at = tex.index("]", at) + 1
        for _ in range(2 if begin.group(2).rstrip("*") in ("tabular", "tabularx", "tabulary") and "*" in begin.group(2)
                       or begin.group(2) in ("tabularx", "tabulary") else 1):
            _, at = tex_argument(tex, at)
        rows = []
        for raw in tex_split(tex[at:m.start()], "\\\\"):
            raw = re.sub(r"^\*?", "", raw)
            while (prefix := TEX_ROW_PREFIX.match(raw)) and prefix.end() > 0:
                raw = raw[prefix.end():]
            if not raw.strip():
                continue
            cells, col = [], 0
            for cell in tex_split(raw, "&"):
                across, inner = 1, cell
                multicolumn = re.match(r"\s*\\multicolumn\s*\{\s*(\d+)\s*\}", cell)
                if multicolumn:
                    across = int(multicolumn.group(1))
                    _, after = tex_argument(cell, multicolumn.end())
                    inner = tex_argument(cell, after)[0] or ""
                down, label = 0, None
                multirow = re.search(r"\\multirow\s*(?:\[[^\]]*\])?\s*\{\s*(-?[\d.]+)\s*\}", inner)
                if multirow:
                    try:
                        down = float(multirow.group(1))
                    except ValueError:
                        down = 0
                    after = multirow.end()
                    after = re.match(r"\s*(?:\[[^\]]*\])?", inner[after:]).end() + after
                    _, after = tex_argument(inner, after)
                    after = re.match(r"\s*(?:\[[^\]]*\])?", inner[after:]).end() + after
                    label = tex_argument(inner, after)[0]
                rows_spanned = (1 if down > 0 else -1) * math.ceil(abs(down) - 0.01) if label is not None else 0
                cells.append((col, across, rows_spanned, plain_words(re.sub(r"\$[^$]*\$", " ", label or ""))))
                col += across
            rows.append(cells)
        out.append(rows)
    return out


def source_row_spans(article, page):
    """Give back the \\multirow spans LaTeXML dropped, from the paper's LaTeX source.

    LaTeXML drops every \\multirow{-n} (typed on a group's last row, reaching
    up) and some \\multirow{n}, leaving the label in one cell and the rows it
    covers with nothing in its column; without a rule to mark the group off,
    the label's rows cannot be told from the table alone (span_group_labels,
    run before, settles the groups that rules mark off). The source is fetched
    when a column has two words each under an empty cell, the shape a lost
    \\multirow{-n} leaves: its tabular with the same number of rows,
    whose labels sit at the same places, gives each label's rows. As in
    span_group_labels, the label spans them from the first, or moves to the
    first in a table without spans.
    """
    def own(at, r, c):
        o = at.get((r, c))
        return o[2] if o and o[:2] == (r, c) and o[3] == o[4] == 1 else None

    def closes_blanks(body):
        """Whether a column has two words each on the row after an empty cell."""
        rows, at = table_grid(body)
        found = collections.Counter()
        for r, c in at:
            cell, above = own(at, r, c), own(at, r - 1, c)
            if (cell and above is not None and not cell_text(above.group(3))
                    and re.search(r"[^\W\d_]", cell_text(re.sub(r"<math\b.*?</math>", " ", cell.group(3), flags=re.S)))):
                found[c] += 1
        return any(n >= 2 for n in found.values())

    def words(fragment):
        return plain_words(html.unescape(re.sub(r"<math\b.*?</math>", " ", fragment, flags=re.S)))

    tables = [(t.start(), balanced_end(article, t.start(), "table")) for t in re.finditer(r"<table\b", article)]
    tables = [(a, b) for a, b in tables if b and article.count("<table", a, b) == 1]
    if not any(closes_blanks(article[a:b]) for a, b in tables):
        return article
    version = paper_version(page)
    tex = latex_source(version) if version else None
    if not tex or "\\multirow" not in tex:
        return article
    tabulars = [t for t in tex_tabulars(tex) if any(cell[2] for row in t for cell in row)]
    out, pos = [], 0
    for a, b in tables:
        body = article[a:b]
        rows, at = table_grid(body)
        spans = bool(re.search(r'\b(?:row|col)span="(?!1")\d+"', body))
        edits = None
        for tabular in tabulars:
            if len(tabular) != len(rows):
                continue
            labels = [(r, cell) for r, row in enumerate(tabular) for cell in row if cell[2] and cell[3]]
            placed = [(r, cell, at.get((r, cell[0]))) for r, cell in labels]
            if not placed or not all(o and o[0] == r and o[1] == cell[0] and words(o[2].group(3)) == cell[3]
                                     for r, cell, o in placed):
                continue
            edits = []
            for r, (c, across, n, _), (_, _, label, down, _) in placed:
                first, last = (r, r + n - 1) if n > 0 else (r + n + 1, r)
                if down > 1 or first < 0 or last >= len(rows) or first == last:
                    continue
                owners = [at.get((i, c)) for i in range(first, last + 1)]
                if not all(o and o[1] == c and o[3] == 1 and o[4] == across
                           and (o[2] is label or not (cell_text(o[2].group(3)) or "<img" in o[2].group(3)))
                           for o in owners):
                    continue
                top = owners[0][2]
                if spans:
                    edits += [(o[2].start(), o[2].end(), "") for o in owners[1:]]
                    if top is not label:
                        edits.append((top.start(3), top.end(3), label.group(3)))
                    edits.append((top.start(2), top.start(2), f' rowspan="{last - first + 1}"'))
                elif top is not label:
                    edits += [(top.start(3), top.end(3), label.group(3)), (label.start(3), label.end(3), "")]
            tabulars.remove(tabular)
            break
        if not edits:
            continue
        for x, y, text in sorted(edits, reverse=True):
            body = body[:x] + text + body[y:]
        out.append(article[pos:a])
        out.append(body)
        pos = b
    return "".join(out) + article[pos:]


def end_guessed_heads(article):
    """Give back to the body the rows of results LaTeXML took for header rows.

    Without a header marked in the source, LaTeXML guesses one (the table's
    class says "ltx_guessed_headers") and can take in rows below the rule
    under the header: "CIFAR-10" spanning three rows, then the first row's
    results. pandoc ends the head at the last <th> row and cuts the label's
    span there, so the rows under it come out a column short. Leading <th>
    rows from a ruled-off row with a cell spanning past them become <td>s.
    """
    out, pos = [], 0
    for table in re.finditer(r'<table\b[^>]*\bltx_guessed_headers\b[^>]*>', article):
        end = balanced_end(article, table.start(), "table")
        if table.start() < pos or end is None:
            continue
        body = article[table.start():end]
        if 'rowspan="' not in body or body.count("<table") > 1:
            continue
        rows = [list(TABLE_CELL.finditer(body, m.start(1), m.end(1))) for m in TABLE_ROW.finditer(body)]
        head = next((i for i, cells in enumerate(rows) if not cells or any(c.group(1) == "td" for c in cells)), len(rows))
        start = next((i for i in range(1, head)
                      if re.search(r"\bltx_border_tt?\b", rows[i][0].group(2))
                      and any(i + int(n) > head for c in rows[i] for n in re.findall(r'\browspan="(\d+)"', c.group(2)))),
                     None)
        if start is None:
            continue
        edits = []
        for cells in rows[start:head]:
            for cell in cells:
                close = cell.start() + cell.group(0).rindex("</") + 2
                edits += [cell.start(1), close]
        for at in sorted(edits, reverse=True):
            body = body[:at] + "td" + body[at + 2:]
        out.append(article[pos:table.start()])
        out.append(body)
        pos = end
    return "".join(out) + article[pos:]


def span_header_rows(article):
    """Make the rows a header cell spans header rows too.

    LaTeXML marks the first row of a two-row header as <th> ("Method" over
    both rows, "Sent-lvl" over three columns) and leaves the second as <td>.
    pandoc ends the head where the <th> rows end and cuts the span there, so
    "Method" would sit over the first sub-column. The spanned rows' cells
    become <th>.
    """
    out, pos = [], 0
    for table in re.finditer(r"<table\b", article):
        end = balanced_end(article, table.start(), "table")
        if table.start() < pos or end is None:
            continue
        body = article[table.start():end]
        if 'rowspan="' not in body or "<thead" in body or body.count("<table") > 1:
            continue
        rows = list(TABLE_ROW.finditer(body))
        head, i = 0, 0  # rows the header reaches; the row looked at
        while i < min(len(rows), 3):
            cells = list(TABLE_CELL.finditer(rows[i].group(1)))
            if i >= head and not (cells and all(c.group(1) == "th" for c in cells)):
                break
            spans = [int(n) for c in cells for n in re.findall(r'\browspan="(\d+)"', c.group(2))]
            head = max([head, i + 1] + [i + n for n in spans])
            i += 1
        if head > min(len(rows) - 1, 3):
            continue
        edits = []
        for row in rows[:head]:
            for cell in TABLE_CELL.finditer(row.group(1)):
                if cell.group(1) == "td":
                    edits += [(row.start(1) + cell.start(1), "th"),
                              (row.start(1) + cell.start() + cell.group(0).rindex("</") + 2, "th")]
        if not edits:
            continue
        for at, tag in sorted(edits, reverse=True):
            body = body[:at] + tag + body[at + 2:]
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
    article = local_links(article, paper_version(page))
    article = clean_math(article)
    article = drop_invisible(article)
    article = close_runaway_floats(article)
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
    article = span_group_labels(article)
    article = source_row_spans(article, page)
    article = merge_continuation_rows(article)
    article = end_guessed_heads(article)
    article = span_header_rows(article)
    article = share_panel_labels(article)
    article = mark_shading(article)
    article = bare_year_citations(article)
    article = extract_svgs(article, save)
    article = lift_blocks(article)
    article = small_pictures(article, paper_version(page))
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
