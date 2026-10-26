#!/usr/bin/env bash
#
# Fetch an arXiv paper and add it to the library: the original PDF, and its
# text layer for the agent to read.
#
#   ./scripts/add-arxiv-paper.sh <arxiv-url-or-id> <topic> [--force]
#
#   ./scripts/add-arxiv-paper.sh https://arxiv.org/abs/2501.13956 llm/memory/agent
#   ./scripts/add-arxiv-paper.sh 2501.13956v1 llm/memory/agent
#
# <topic> is a folder path under library/, e.g. llm/memory/agent. The paper's
# title, authors and date come from arXiv's export API; the filename is the
# cleaned-up title. Writes:
#
#   $PDF_ROOT/<topic>/<Title>.pdf
#   library/<topic>/<Title>.txt
#
# The text file starts with YAML frontmatter (`summary:` left empty for whoever
# files the paper to write), then the PDF's text layer with a line "[page N]"
# where each page starts (docs/text-layer.md). Existing files are left alone
# unless --force is given, and a paper already in the library under another
# topic is refused.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

if [ $# -lt 2 ]; then
  echo "usage: $0 <arxiv-url-or-id> <topic> [--force]" >&2
  exit 1
fi

RAW_ID="$1"
TOPIC="$2"
shift 2
validate_topic "$TOPIC"

FORCE=false
while [ $# -gt 0 ]; do
  case "$1" in
    --force)    FORCE=true; shift ;;
    *) echo "error: unknown argument $1" >&2; exit 1 ;;
  esac
done

for cmd in curl pdftotext python3; do
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
EXISTING="$(python3 "$SCRIPTS_DIR/paperlib.py" find-arxiv "$ID")"
if [ -n "$EXISTING" ] && [ "$FORCE" != true ]; then
  echo "error: arXiv:$ID is already in the library: $EXISTING" >&2
  exit 1
fi

ORIG_DIR="$PDF_ROOT/$TOPIC"
TXT_DIR="$LIBRARY_DIR/$TOPIC"
mkdir -p "$ORIG_DIR" "$TXT_DIR"

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
VID="${ID}v${VERSION}"

FILENAME="$(title_to_filename "$TITLE")"

echo "Title:    $TITLE (v$VERSION)"
echo "Filename: $FILENAME"

PDF="$ORIG_DIR/$FILENAME.pdf"
TXT="$TXT_DIR/$FILENAME.txt"

is_pdf() { [ "$(head -c 5 "$1" 2>/dev/null)" = "%PDF-" ]; }

if [ -f "$PDF" ] && [ "$FORCE" != true ] && is_pdf "$PDF"; then
  echo "skip (exists): $PDF"
else
  # A withdrawn version is served as an HTML notice rather than a PDF. Step
  # back to the latest version that has a PDF (unless one was asked for).
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

if [ -f "$TXT" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $TXT"
else
  python3 "$SCRIPTS_DIR/paperlib.py" frontmatter-arxiv "$WORK/meta.xml" "$ID" pdf \
    | python3 "$SCRIPTS_DIR/paperlib.py" text-paper "$TXT" "$PDF"
fi

echo "Done: $PDF"
echo "      $TXT"
