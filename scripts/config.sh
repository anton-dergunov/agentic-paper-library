# Shared paths for the library scripts. Sourced, not run.
#
# LIBRARY_DIR holds the markdown copies (committed); PDF_ROOT holds the PDFs
# (outside the repo, synced by Yandex Disk). The two trees mirror each other:
#
#   $LIBRARY_DIR/<topic path>/<Title>.md
#   $PDF_ROOT/<topic path>/<Title>.pdf
#
# Both can be overridden from the environment, e.g. on a machine where Yandex
# Disk is mounted somewhere else.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIBRARY_DIR="${LIBRARY_DIR:-$REPO_ROOT/library}"
PDF_ROOT="${PDF_ROOT:-$HOME/Yandex.Disk.localized/Papers}"

# A topic is a relative path of lowercase, hyphenated folder names, e.g.
# llm/memory/agent. Rejecting anything else keeps a typo from creating a stray
# top-level folder in both trees.
validate_topic() {
  if ! [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$ ]]; then
    echo "error: topic must be a path of lowercase hyphenated names (e.g. llm/memory/agent), got '$1'" >&2
    exit 1
  fi
}

# Clean a paper title into a filename: keep its casing and words, drop
# characters that are not legal in filenames, and cap the length at 100
# characters on a word boundary.
title_to_filename() {
  python3 -c '
import sys
title = sys.argv[1]
bad = "/\\:*?<>|" + chr(34)
name = "".join(" " if c in bad else c for c in title)
name = " ".join(name.split())
if len(name) > 100:
    cut = name[:100]
    name = cut[: cut.rfind(" ")] if " " in cut else cut
    # A cut that lands just after a comma or dash leaves it dangling at the end
    # of the filename, which reads like a typo rather than a truncation.
    name = name.rstrip(" ,;:.-–—")
print(name)
' "$1"
}
