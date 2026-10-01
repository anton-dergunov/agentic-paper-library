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
# which comes through far cleaner than PDF text extraction — see
# docs/library.md. The PDF and the HTML are fetched
# at the same arXiv version. scripts/html-to-markdown.py does the conversion:
# math as $...$, complex tables as HTML, figures saved to images/ as repaired
# standalone SVGs. Existing files are left alone unless --force is given, and a
# paper already in the library under another topic is refused.
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
# /abs/ or /pdf/ URL, and reduces it to the bare "YYMM.NNNNN" id. A version
# given explicitly is the one fetched; otherwise the latest.
read -r ID PINNED_VERSION < <(python3 -c '
import re, sys
raw = sys.argv[1]
m = re.search(r"(\d{4}\.\d{4,5})(?:v(\d+))?", raw)
if not m:
    sys.exit("error: could not find an arXiv id in " + repr(raw))
print(m.group(1), m.group(2) or "")
' "$RAW_ID")

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

read -r VERSION TITLE < <(python3 -c '
import re, sys, xml.etree.ElementTree as ET
ns = {"a": "http://www.w3.org/2005/Atom"}
root = ET.parse(sys.argv[1]).getroot()
entry = root.find("a:entry", ns)
if entry is None or entry.find("a:title", ns) is None:
    sys.exit("error: arXiv id not found (no <entry> in API response)")
version = re.search(r"v(\d+)$", entry.find("a:id", ns).text.strip()).group(1)
print(version, " ".join(entry.find("a:title", ns).text.split()))
' "$WORK/meta.xml")
if [ -z "${VERSION:-}" ] || [ -z "${TITLE:-}" ]; then
  echo "error: could not read the version and title for arXiv:$ID" >&2
  exit 1
fi
[ -n "${PINNED_VERSION:-}" ] && VERSION="$PINNED_VERSION"
# The PDF and the HTML are fetched at the same version, so the page numbers
# written onto the markdown's headings match the PDF being read.
VID="${ID}v${VERSION}"

FILENAME="$(title_to_filename "$TITLE")"

echo "Title:    $TITLE (v$VERSION)"
echo "Filename: $FILENAME"

PDF="$ORIG_DIR/$FILENAME.pdf"
MD="$MD_DIR/$FILENAME.md"

is_pdf() { [ "$(head -c 5 "$1" 2>/dev/null)" = "%PDF-" ]; }

if [ -f "$PDF" ] && [ "$FORCE" != true ] && is_pdf "$PDF"; then
  echo "skip (exists): $PDF"
else
  # A withdrawn version is served as an HTML notice rather than a PDF. Step
  # back to the latest version that has a PDF (unless one was asked for), and
  # use that version for the HTML too.
  echo "Downloading PDF..."
  while :; do
    curl -sL "https://arxiv.org/pdf/$VID" -o "$WORK/paper.pdf"
    if is_pdf "$WORK/paper.pdf"; then
      mv "$WORK/paper.pdf" "$PDF"
      break
    fi
    if [ -n "${PINNED_VERSION:-}" ] || [ "$VERSION" -le 1 ]; then
      echo "error: arXiv served no PDF for $VID (withdrawn?)" >&2
      exit 1
    fi
    echo "  $VID has no PDF (withdrawn?), trying v$((VERSION - 1))" >&2
    VERSION=$((VERSION - 1))
    VID="${ID}v${VERSION}"
  done
fi

if [ -f "$MD" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $MD"
else
  if [ "$FROM_PDF" = true ]; then
    SOURCE=pdf
    echo "Skipping the HTML rendering as asked (--from-pdf)."
  else
    echo "Fetching HTML rendering..."
    curl -sL "https://arxiv.org/html/$VID" -o "$WORK/paper.html"

    SOURCE=html
    if ! grep -q 'ltx_page_content' "$WORK/paper.html"; then
      SOURCE=pdf
      echo "No HTML rendering for arXiv:$ID — falling back to the PDF text layer."
    fi
  fi
fi

if [ "${SOURCE:-}" = html ]; then
  # Article extraction, pandoc, figure extraction and SVG repair: see the
  # docstring of html-to-markdown.py for what each step fixes.
  python3 "$REPO_ROOT/scripts/html-to-markdown.py" "$WORK/paper.html" "$WORK/body.md" "$IMAGES_DIR" "$FILENAME"

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
