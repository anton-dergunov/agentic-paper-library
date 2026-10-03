#!/usr/bin/env python3
"""Compare two copies of the library: symptoms per paper and prose words per paper.

    python3 before_after.py <old library/> <new library/> <old symptoms.tsv> <new symptoms.tsv>

The two library directories are checkouts of the markdown at two commits (for the
run: 4b0e0bc5, main before the run, and f8056ad3, after the run and its fixes). The
symptom files are the output of `scripts/conversion-symptoms.py` (no flags) over each,
one "<symptoms>\t<path>" line per affected paper. Prints JSON: how papers moved between
"has a symptom" and "has none", which symptoms appeared in papers that had none, and the
distribution of prose-word change for HTML papers present in both copies, and the
papers that shrank by more than 5% under three ways of counting:

  as_run      what `conversion-symptoms.py --compare <ref>` computed during the run: the
              old copy's whole file, frontmatter included, against the new copy's body
  bodies      body against body, the same word count otherwise
  bodies_tags body against body, and a tag is only `<letter...>` on one line, so a `<`
              inside an equation does not swallow the text up to the next `>`

Written after the run to re-derive its numbers from git, not part of the run itself.
`prose_words` is copied from `scripts/conversion-symptoms.py`.
"""

import collections
import json
import re
import statistics
import sys
from pathlib import Path


TAG = r"<[^>]+>"                      # as in conversion-symptoms.py
TAG_ONE_LINE = r"</?[A-Za-z][^>\n]*>"


def prose_words(body, tag=TAG):
    """Words outside markup: images, tags, table rules and pipes removed."""
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(tag, " ", body)
    body = re.sub(r"[|]|^[-:| ]+$", " ", body, flags=re.M)
    return len(body.split())


def html_papers(root):
    """{relative path: (whole file, body)} for papers converted from arXiv HTML."""
    out = {}
    for md in Path(root).rglob("*.md"):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        front = m.group(1)
        if re.search(r"^source: html\s*$", front, re.M) and re.search(r"^arxiv:", front, re.M):
            out[str(md.relative_to(root))] = (text, text[m.end():])
    return out


def symptoms(tsv):
    rows = {}
    for line in open(tsv, encoding="utf-8"):
        if "\t" in line:
            kinds, path = line.rstrip("\n").split("\t", 1)
            rows[path] = set(kinds.split(","))
    return rows


def main(old_root, new_root, old_tsv, new_tsv):
    old, new = html_papers(old_root), html_papers(new_root)
    s_old, s_new = symptoms(old_tsv), symptoms(new_tsv)
    both = sorted(set(old) & set(new))

    moves = collections.Counter()
    appeared = collections.Counter()
    for p in both:
        a, b = bool(s_old.get(p)), bool(s_new.get(p))
        moves[f"{'symptom' if a else 'clean'} -> {'symptom' if b else 'clean'}"] += 1
        for k in s_new.get(p, set()) - s_old.get(p, set()):
            appeared[k] += 1
    per_kind = {k: {"before": sum(k in v for p, v in s_old.items() if p in both),
                    "after": sum(k in v for p, v in s_new.items() if p in both)}
                for k in sorted(set().union(*s_old.values(), *s_new.values()))}

    changes = []
    shrank = {"as_run": [], "bodies": [], "bodies_tags": []}
    for p in both:
        counts = {
            "as_run": (prose_words(old[p][0]), prose_words(new[p][1])),
            "bodies": (prose_words(old[p][1]), prose_words(new[p][1])),
            "bodies_tags": (prose_words(old[p][1], TAG_ONE_LINE), prose_words(new[p][1], TAG_ONE_LINE)),
        }
        before, after = counts["bodies_tags"]
        if before:
            changes.append(after / before - 1)
        for how, (before, after) in counts.items():
            if before and after < 0.95 * before:
                shrank[how].append({"paper": p, "before": before, "after": after,
                                    "change": round(after / before - 1, 3)})
    q = statistics.quantiles(changes, n=20)
    print(json.dumps({
        "html_papers": {"old": len(old), "new": len(new), "in_both": len(both)},
        "papers_with_a_symptom": {"old": len(s_old), "new": len(s_new)},
        "moves_between_copies": dict(moves),
        "symptom_counts_in_both": per_kind,
        "symptoms_new_to_a_paper": dict(appeared),
        "prose_word_change_bodies_tags": {
            "median": round(statistics.median(changes), 4),
            "p5": round(q[0], 4), "p95": round(q[-1], 4),
            "grew_over_5pct": sum(c > 0.05 for c in changes),
        },
        "shrank_over_5pct": {how: sorted(rows, key=lambda r: r["change"]) for how, rows in shrank.items()},
    }, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:5])
