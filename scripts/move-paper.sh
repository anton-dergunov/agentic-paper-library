#!/usr/bin/env bash
#
# Move a paper to another topic, keeping its text and PDF together.
#
#   ./scripts/move-paper.sh <library/.../Title.txt> <new-topic>
#
#   ./scripts/move-paper.sh "library/llm/memory/agent/Zep. A Temporal Knowledge Graph Architecture for Agent Memory.txt" llm/memory/graphs
#
# Moves library/<old>/<Title>.txt (or the .md of a web article) and
# $PDF_ROOT/<old>/<Title>.pdf to the same places under <new-topic>, removes
# folders left empty in either tree, then regenerates the indexes. Never move
# a paper by hand: its text and its PDF must stay at mirrored paths.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

if [ $# -ne 2 ]; then
  echo "usage: $0 <paper.txt> <new-topic>" >&2
  exit 1
fi

SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
NEW_TOPIC="$2"
validate_topic "$NEW_TOPIC"

if [ ! -f "$SRC" ]; then
  echo "error: no such file: $1" >&2
  exit 1
fi
case "$SRC" in
  *.txt|*.md) ;;
  *) echo "error: $1 is not a paper file (.txt, or .md for a web article)" >&2; exit 1 ;;
esac
case "$SRC" in
  "$LIBRARY_DIR"/*) ;;
  *) echo "error: $1 is not under $LIBRARY_DIR" >&2; exit 1 ;;
esac

EXT="${SRC##*.}"
STEM="$(basename "$SRC" ".$EXT")"
OLD_DIR="$(dirname "$SRC")"
OLD_TOPIC="${OLD_DIR#"$LIBRARY_DIR"/}"

if [ "$OLD_TOPIC" = "$NEW_TOPIC" ]; then
  echo "error: already in $NEW_TOPIC" >&2
  exit 1
fi

NEW_DIR="$LIBRARY_DIR/$NEW_TOPIC"
OLD_PDF="$PDF_ROOT/$OLD_TOPIC/$STEM.pdf"
NEW_PDF="$PDF_ROOT/$NEW_TOPIC/$STEM.pdf"

if [ -e "$NEW_DIR/$STEM.txt" ] || [ -e "$NEW_DIR/$STEM.md" ] || [ -e "$NEW_PDF" ]; then
  echo "error: $NEW_TOPIC already has a paper named '$STEM'" >&2
  exit 1
fi

mkdir -p "$NEW_DIR" "$PDF_ROOT/$NEW_TOPIC"
mv "$SRC" "$NEW_DIR/$STEM.$EXT"

if [ -f "$OLD_PDF" ]; then
  mv "$OLD_PDF" "$NEW_PDF"
else
  echo "warning: no PDF at $OLD_PDF" >&2
fi

# Remove folders the move emptied, in both trees. In library/ a folder holding
# only a generated README.md counts as empty.
prune() {
  local dir="$1" root="$2"
  while [ "$dir" != "$root" ] && [ -d "$dir" ]; do
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
