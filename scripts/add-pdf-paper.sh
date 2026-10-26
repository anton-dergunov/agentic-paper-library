#!/usr/bin/env bash
#
# Add a paper that only exists as a local PDF — one that was never posted to
# arXiv, or that was published somewhere arXiv does not mirror.
#
#   ./scripts/add-pdf-paper.sh <file.pdf> <topic> [--title "..."] [--source "..."] [--force]
#
#   ./scripts/add-pdf-paper.sh ~/Downloads/some-paper.pdf llm/evaluation/benchmarks \
#       --title "Some Paper: A Benchmark" --source "https://example.org/paper.pdf"
#
# Writes the same pair of files as add-arxiv-paper.sh:
#
#   $PDF_ROOT/<topic>/<Title>.pdf
#   library/<topic>/<Title>.txt     frontmatter, then the PDF's text layer
#
# The filename comes from --title if given and from the PDF's own basename
# otherwise, cleaned and length-capped the same way as the arXiv script so that
# filenames stay consistent across the whole library. The source PDF is copied,
# not moved.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

if [ $# -lt 2 ]; then
  echo "usage: $0 <file.pdf> <topic> [--title \"...\"] [--source \"...\"] [--force]" >&2
  exit 1
fi

SRC_PDF="$1"
TOPIC="$2"
shift 2
validate_topic "$TOPIC"

TITLE=""
SOURCE_URL=""
FORCE=false
while [ $# -gt 0 ]; do
  case "$1" in
    --title)  TITLE="$2"; shift 2 ;;
    --source) SOURCE_URL="$2"; shift 2 ;;
    --force)  FORCE=true; shift ;;
    *) echo "error: unknown argument $1" >&2; exit 1 ;;
  esac
done

if [ ! -f "$SRC_PDF" ]; then
  echo "error: no such file: $SRC_PDF" >&2
  exit 1
fi

for cmd in pdftotext python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: $cmd is required but not found on PATH" >&2
    exit 1
  fi
done

ORIG_DIR="$PDF_ROOT/$TOPIC"
TXT_DIR="$LIBRARY_DIR/$TOPIC"
mkdir -p "$ORIG_DIR" "$TXT_DIR"

if [ -z "$TITLE" ]; then
  TITLE="$(basename "$SRC_PDF" .pdf)"
fi

FILENAME="$(title_to_filename "$TITLE")"

echo "Title:    $TITLE"
echo "Filename: $FILENAME"

PDF="$ORIG_DIR/$FILENAME.pdf"
TXT="$TXT_DIR/$FILENAME.txt"

if [ -f "$PDF" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $PDF"
else
  cp "$SRC_PDF" "$PDF"
fi

if [ -f "$TXT" ] && [ "$FORCE" != true ]; then
  echo "skip (exists): $TXT"
else
  python3 "$SCRIPTS_DIR/paperlib.py" frontmatter-manual "$TITLE" pdf "$SOURCE_URL" \
    | python3 "$SCRIPTS_DIR/paperlib.py" text-paper "$TXT" "$PDF"
fi

echo "Done: $PDF"
echo "      $TXT"
