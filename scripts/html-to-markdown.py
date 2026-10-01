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
"""

import base64
import html.entities
import re
import subprocess
import sys
from urllib.parse import quote
from pathlib import Path

from lxml import etree

from paperlib import localize_figures, to_webp

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
        out.append(f'<img src="{save("svg+xml", article[begin:end].encode("utf-8"))}" alt="" />')
        pos = end


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
    article = extract_svgs(article, save)
    article = objects_to_images(article)
    body = subprocess.run(
        [
            "pandoc", "-f", "html", "-t", "gfm-tex_math_gfm+tex_math_dollars",
            "--wrap=none", "--lua-filter", str(FILTER),
        ],
        input=article, capture_output=True, text=True, check=True,
    ).stdout

    # Raster figures arXiv inlines as base64 data URIs.
    body = re.sub(
        r"!\[[^\]]*\]\(data:image/([a-zA-Z0-9+.-]+);base64,([A-Za-z0-9+/=]+)\)",
        lambda m: f"![]({save_raster(m.group(1), base64.b64decode(m.group(2)))})",
        body,
    )
    if base:
        body = re.sub(
            r'(!\[[^\]]*\]\(|<img\s[^>]*?src=")(?![a-z]+:|images/|/|\d{4}\.\d{4,5}v\d+/)([^)"\s]+)',
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
