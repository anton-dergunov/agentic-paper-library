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

# A topic is a folder declared in catalog/topics.yaml: a relative path of
# lowercase, hyphenated names, e.g. llm/memory/agent. Rejecting anything else
# keeps a typo from creating a stray folder in both trees; a new folder is
# added to the catalog first.
validate_topic() {
  if ! [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$ ]]; then
    echo "error: topic must be a path of lowercase hyphenated names (e.g. llm/memory/agent), got '$1'" >&2
    exit 1
  fi
  if ! python3 -c '
import sys, yaml
sys.exit(0 if sys.argv[2] in (yaml.safe_load(open(sys.argv[1])) or {}) else 1)
' "$REPO_ROOT/catalog/topics.yaml" "$1"; then
    echo "error: '$1' is not a folder in catalog/topics.yaml; declare it there first" >&2
    exit 1
  fi
}

# Clean a paper title into a filename: keep its casing and words, drop
# characters that are not legal in filenames, and cap the length at 100
# characters on a word boundary. A question mark inside a title ends a
# sentence, so it becomes a full stop ("Is Model Collapse Inevitable. Breaking
# ..."); one at the very end is dropped.
title_to_filename() {
  python3 -c '
import re, sys
title = sys.argv[1].strip()
title = re.sub(r"\?+$", "", title)
title = re.sub(r"\?+(?=\s)", ".", title)
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
