#!/usr/bin/env bash
#
# Move a paper to another topic, keeping its markdown, figures and PDF together.
#
#   ./scripts/move-paper.sh <library/.../Title.md> <new-topic>
#
#   ./scripts/move-paper.sh "library/llm/memory/agent/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.md" llm/memory/graphs
#
# Moves library/<old>/<Title>.md, library/<old>/images/<Title>-fig*, and
# $PDF_ROOT/<old>/<Title>.pdf to the same places under <new-topic>, removes
# folders left empty in either tree, then regenerates the indexes. Never move
# a paper by hand: the markdown and the PDF must stay at mirrored paths.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

if [ $# -ne 2 ]; then
  echo "usage: $0 <paper.md> <new-topic>" >&2
  exit 1
fi

SRC_MD="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
NEW_TOPIC="$2"
validate_topic "$NEW_TOPIC"

if [ ! -f "$SRC_MD" ]; then
  echo "error: no such file: $1" >&2
  exit 1
fi
case "$SRC_MD" in
  "$LIBRARY_DIR"/*) ;;
  *) echo "error: $1 is not under $LIBRARY_DIR" >&2; exit 1 ;;
esac

STEM="$(basename "$SRC_MD" .md)"
OLD_DIR="$(dirname "$SRC_MD")"
OLD_TOPIC="${OLD_DIR#"$LIBRARY_DIR"/}"

if [ "$OLD_TOPIC" = "$NEW_TOPIC" ]; then
  echo "error: already in $NEW_TOPIC" >&2
  exit 1
fi

NEW_DIR="$LIBRARY_DIR/$NEW_TOPIC"
OLD_PDF="$PDF_ROOT/$OLD_TOPIC/$STEM.pdf"
NEW_PDF="$PDF_ROOT/$NEW_TOPIC/$STEM.pdf"

if [ -e "$NEW_DIR/$STEM.md" ] || [ -e "$NEW_PDF" ]; then
  echo "error: $NEW_TOPIC already has a paper named '$STEM'" >&2
  exit 1
fi

mkdir -p "$NEW_DIR" "$PDF_ROOT/$NEW_TOPIC"
mv "$SRC_MD" "$NEW_DIR/$STEM.md"

shopt -s nullglob
figures=("$OLD_DIR/images/$STEM"-fig*)
if [ ${#figures[@]} -gt 0 ]; then
  mkdir -p "$NEW_DIR/images"
  mv "${figures[@]}" "$NEW_DIR/images/"
fi

if [ -f "$OLD_PDF" ]; then
  mv "$OLD_PDF" "$NEW_PDF"
else
  echo "warning: no PDF at $OLD_PDF" >&2
fi

# Remove folders the move emptied, in both trees. In library/ a folder holding
# only a generated README.md (or an empty images/) counts as empty.
prune() {
  local dir="$1" root="$2"
  while [ "$dir" != "$root" ] && [ -d "$dir" ]; do
    [ -d "$dir/images" ] && rmdir "$dir/images" 2>/dev/null || true
    local rest
    rest="$(find "$dir" -mindepth 1 -maxdepth 1 ! -name README.md ! -name .DS_Store | head -1)"
    [ -n "$rest" ] && break
    rm -f "$dir/README.md" "$dir/.DS_Store"
    rmdir "$dir"
    dir="$(dirname "$dir")"
  done
}
prune "$OLD_DIR" "$LIBRARY_DIR"
prune "$PDF_ROOT/$OLD_TOPIC" "$PDF_ROOT"

echo "Moved: $OLD_TOPIC/$STEM -> $NEW_TOPIC/"
python3 "$SCRIPTS_DIR/build-index.py"
