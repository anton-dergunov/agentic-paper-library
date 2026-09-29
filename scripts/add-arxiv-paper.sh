#!/usr/bin/env bash
#
# Fetch an arXiv paper and add it to the library, both as the original PDF and
# as an agent-readable markdown conversion.
#
#   ./scripts/add-arxiv-paper.sh <arxiv-url-or-id> <topic> [--force] [--from-pdf]
#
#   ./scripts/add-arxiv-paper.sh https://arxiv.org/abs/2501.13956 llm/memory/agent
#   ./scripts/add-arxiv-paper.sh 2501.13956v1 llm/memory/agent
#
# <topic> is a folder path under library/, e.g. llm/memory/agent. The paper's
# title, authors and date come from arXiv's export API; the filename is the
# cleaned-up title. Writes:
#
#   $PDF_ROOT/<topic>/<Title>.pdf
#   library/<topic>/<Title>.md
#   library/<topic>/images/<Title>-fig01.<ext>  (if the paper has any)
#
# The markdown starts with YAML frontmatter; `summary:` is left empty for
# whoever files the paper to write. Afterwards, headings get the PDF page they
# start on (scripts/page-map.py).
#
# Markdown is converted from arXiv's own HTML rendering (arxiv.org/html/<id>),
# which comes through pandoc far cleaner than PDF text extraction — see
# docs/experiments/pdf-vs-html-conversion.md. Figures that arXiv's renderer
# inlines as embedded SVG/base64 images are pulled out into the images/ folder
# rather than left as data URIs in the markdown, since an inline base64 blob
# makes the file unreadable both for a human skimming it and for a coding
# agent. Existing files are left alone unless --force is given, and a paper
# already in the library under another topic is refused.
#
# A small number of papers have no usable HTML rendering on arXiv: PDF-only
# submissions get a stub page pointing back at the PDF, and a few LaTeXML runs
# pick the wrong root .tex and render the conference template instead of the
# paper. The stub case is detected automatically; the wrong-template case is not
# detectable from the outside, so pass --from-pdf when you spot one. Either way
# the fallback extracts the PDF's text layer, which is markedly worse — tables
# and figures do not survive — so the frontmatter says `source: pdf-text` and
# the markdown carries a warning at the top.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

if [ $# -lt 2 ]; then
  echo "usage: $0 <arxiv-url-or-id> <topic> [--force] [--from-pdf]" >&2
  exit 1
fi

RAW_ID="$1"
TOPIC="$2"
shift 2
validate_topic "$TOPIC"

FORCE=false
FROM_PDF=false
while [ $# -gt 0 ]; do
  case "$1" in
    --force)    FORCE=true; shift ;;
    --from-pdf) FROM_PDF=true; shift ;;
    *) echo "error: unknown argument $1" >&2; exit 1 ;;
  esac
done

for cmd in curl pandoc python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: $cmd is required but not found on PATH" >&2
    exit 1
  fi
done

# Accepts a bare id, an id with version ("2409.11901v1"), or a full
# /abs/ or /pdf/ URL, and reduces it to the bare "YYMM.NNNNN" id.
ID="$(python3 -c '
import re, sys
raw = sys.argv[1]
m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", raw)
if not m:
    sys.exit("error: could not find an arXiv id in " + repr(raw))
print(m.group(1))
' "$RAW_ID")"

# One paper, one place: refuse a paper that is already filed elsewhere.
EXISTING="$(grep -rlE --include='*.md' "^arxiv: ['\"]?$ID['\"]?$" "$LIBRARY_DIR" 2>/dev/null || true)"
if [ -n "$EXISTING" ] && [ "$FORCE" != true ]; then
  echo "error: arXiv:$ID is already in the library: $EXISTING" >&2
  exit 1
fi

ORIG_DIR="$PDF_ROOT/$TOPIC"
MD_DIR="$LIBRARY_DIR/$TOPIC"
IMAGES_DIR="$MD_DIR/images"
mkdir -p "$ORIG_DIR" "$MD_DIR"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "Looking up metadata for arXiv:$ID..."
# The export API rate-limits and answers with an empty body when it does, which
# is indistinguishable from a network blip — retry with backoff rather than
# failing the whole run on a throttle.
for attempt in 1 2 3 4 5; do
  curl -sL "http://export.arxiv.org/api/query?id_list=$ID" -o "$WORK/meta.xml"
  if [ -s "$WORK/meta.xml" ] && grep -q '<entry' "$WORK/meta.xml"; then
    break
  fi
  if [ "$attempt" = 5 ]; then
    echo "error: arXiv export API gave no usable response after 5 attempts" >&2
    exit 1
  fi
  echo "  empty response, retrying in $((attempt * 5))s..." >&2
  sleep $((attempt * 5))
done

TITLE="$(python3 -c '
import sys, xml.etree.ElementTree as ET
ns = {"a": "http://www.w3.org/2005/Atom"}
root = ET.parse(sys.argv[1]).getroot()
entry = root.find("a:entry", ns)
if entry is None or entry.find("a:title", ns) is None:
    sys.exit("error: arXiv id not found (no <entry> in API response)")
print(" ".join(entry.find("a:title", ns).text.split()))
' "$WORK/meta.xml")"

FILENAME="$(title_to_filename "$TITLE")"

echo "Title:    $TITLE"
echo "Filename: $FILENAME"

PDF="$ORIG_DIR/$FILENAME.pdf"
MD="$MD_DIR/$FILENAME.md"

if [ -f "$PDF" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $PDF"
else
  echo "Downloading PDF..."
  curl -sL "https://arxiv.org/pdf/$ID" -o "$PDF"
fi

if [ -f "$MD" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $MD"
else
  if [ "$FROM_PDF" = true ]; then
    SOURCE=pdf
    echo "Skipping the HTML rendering as asked (--from-pdf)."
  else
    echo "Fetching HTML rendering..."
    curl -sL "https://arxiv.org/html/$ID" -o "$WORK/paper.html"

    SOURCE=html
    if ! grep -q 'ltx_page_content' "$WORK/paper.html"; then
      SOURCE=pdf
      echo "No HTML rendering for arXiv:$ID — falling back to the PDF text layer."
    fi
  fi
fi

if [ "${SOURCE:-}" = html ]; then
  # arXiv's HTML page wraps the article body in a single
  # <div class="ltx_page_content">...</div>; everything outside it is site
  # nav/header/footer chrome that pandoc shouldn't see.
  python3 -c '
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
start_m = re.search(r"<div[^>]*\bltx_page_content\b[^>]*>", html)
if not start_m:
    sys.exit("error: could not find ltx_page_content in arXiv HTML — no HTML rendering for this paper?")
pos = start_m.end()
depth = 1
end = None
for m in re.finditer(r"<div\b|</div>", html[pos:]):
    if m.group() == "</div>":
        depth -= 1
        if depth == 0:
            end = pos + m.end()
            break
    else:
        depth += 1
if end is None:
    sys.exit("error: unbalanced <div> while extracting article content")
sys.stdout.write(html[start_m.start():end])
' "$WORK/paper.html" > "$WORK/article.html"

  # gfm-raw_html: without disabling the raw_html extension, pandoc falls back
  # to emitting arXiv's HTML tags (div/span wrappers with id/class attributes
  # on nearly every paragraph) verbatim instead of converting them, which
  # buries the prose in markup noise.
  pandoc "$WORK/article.html" -f html -t gfm-raw_html --wrap=none -o "$WORK/body.md"

  # Diagrams that arXiv's renderer draws as inline SVG (rather than linking a
  # raster figure) come out of pandoc as `![](data:image/svg+xml;base64,...)`
  # — pull each one out to a real file in images/ and point the markdown at
  # it instead of carrying the blob inline.
  python3 -c '
import base64, os, re, sys

body_path, images_dir, basename = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(body_path, encoding="utf-8").read()

exts = {"svg+xml": "svg", "png": "png", "jpeg": "jpg", "gif": "gif", "webp": "webp"}
counter = 0

def repl(m):
    global counter
    counter += 1
    mime, data = m.group(1), m.group(2)
    ext = exts.get(mime, "bin")
    fname = f"{basename}-fig{counter:02d}.{ext}"
    os.makedirs(images_dir, exist_ok=True)
    with open(os.path.join(images_dir, fname), "wb") as f:
        f.write(base64.b64decode(data))
    return f"![](images/{fname})"

text = re.sub(
    r"!\[[^\]]*\]\(data:image/([a-zA-Z0-9+.-]+);base64,([A-Za-z0-9+/=]+)\)",
    repl,
    text,
)

# Raster figures, by contrast, arXiv links relative to the HTML page
# ("2501.13956v1/x1.png"), which resolves nowhere once the markdown leaves
# arxiv.org. Point them at arXiv so they still render in a markdown preview.
text = re.sub(
    r"(!\[[^\]]*\]\()(\d{4}\.\d{4,5}v\d+/)",
    r"\1https://arxiv.org/html/\2",
    text,
)
open(body_path, "w", encoding="utf-8").write(text)
' "$WORK/body.md" "$IMAGES_DIR" "$FILENAME"

  # For submissions uploaded as a PDF rather than as LaTeX source, arXiv still
  # serves an HTML page — but its body is a one-line "see the PDF" pointer. The
  # wrapper div is there, so the check above passes; only the length gives it
  # away. Anything this short is a stub, never a paper.
  if [ "$(wc -c < "$WORK/body.md")" -lt 4000 ]; then
    echo "arXiv HTML for $ID is a stub, not a rendering — falling back to the PDF text layer."
    SOURCE=pdf
  else
    {
      python3 "$REPO_ROOT/scripts/paperlib.py" frontmatter-arxiv "$WORK/meta.xml" "$ID" html
      echo
      cat "$WORK/body.md"
    } > "$MD"
  fi
fi

if [ "${SOURCE:-}" = pdf ]; then
  # Last resort: the PDF's own text layer.
  python3 "$REPO_ROOT/scripts/pdf-to-markdown.py" "$PDF" "$WORK/body.md"

  {
    python3 "$REPO_ROOT/scripts/paperlib.py" frontmatter-arxiv "$WORK/meta.xml" "$ID" pdf-text
    echo
    echo "> **Converted from the PDF text layer**, because arXiv has no HTML"
    echo "> rendering for this paper. Section structure, tables and figures did"
    echo "> not survive the conversion; check the original PDF (same path under"
    echo "> \`Papers/\`) before relying on any number or table from this file."
    echo
    cat "$WORK/body.md"
  } > "$MD"
fi

if [ -n "${SOURCE:-}" ]; then
  python3 "$REPO_ROOT/scripts/page-map.py" "$PDF" "$MD"
fi

echo "Done: $PDF"
echo "      $MD"
