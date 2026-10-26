#!/usr/bin/env python3
"""What is left to read, area by area, and what it will cost; and the notes to read again.

    paperlib reading                 every review scope: papers, read, to read, to re-read,
                                     the estimated cost of reading them, and its review
    paperlib reading <scope>         one scope: the papers to read and to re-read, each with
                                     its cost, and the commands that read them
    paperlib reread <paper or stem> ... --reason "<why>"    mark notes to be read again
    paperlib reread <paper or stem> ... --clear             take the mark off

The review scopes, in the order to read them, are `review_scopes` in paper-library.yaml: a
list of folders, or groups of them ("Primary areas: [llm/evaluation, ...]"); without it,
the top-level folders. A paper is read when its note has a digest. A note is to be read
again when it carries a `reread:` line, set by `paperlib reread`; `paperlib read --flagged
<scope>` reads those papers again. Re-reading costs a model request a paper, so the mark is
for a note that is wrong or was written from a broken copy of its paper.

The cost is a model request per paper, estimated from its reading view (`paperlib
read-view`) with a line fitted to the readings logged in <cache>/read-papers.jsonl (dollars
of API price against the length of the view each was sent; a few dollars' error over an
area). A review is
`written <updated>` or, once the reader has gone through it, `checked <date>` (the
review's `checked:` frontmatter); `+N` counts the scope's papers the review does not cover.
"""

import json
import sys

from paperlib import (
    CACHE_DIR, CONFIG, LIBRARY_DIR, flag_reread, has_digest, load_reviews, load_topics, paper_files,
    paper_stem, read_paper, reread_reason, review_coverage, styled, text_view,
)

# Dollars a reading costs: a fixed part (the prompt, the note written) and a part per
# character of the reading view. Used until the log holds enough readings to fit them:
# fitted to the four first readings of text-layer notes in experiments/reading-formats
# (tier H, Opus 5.5).
DEFAULT_FIT = (0.144, 2.81e-6)


def review_scopes():
    """[(group, [scope, ...])] in reading order; group "" when the config lists no groups."""
    declared = CONFIG.get("review_scopes")
    if not declared:
        tops = sorted({t.split("/")[0] for t in load_topics()})
        return [("", tops)]
    groups, loose = [], []
    for item in declared:
        if isinstance(item, dict):
            groups += [(str(name), [str(s).strip("/") for s in scopes or []]) for name, scopes in item.items()]
        else:
            loose.append(str(item).strip("/"))
    return ([("", loose)] if loose else []) + groups


def cost_fit():
    """(fixed, per character) dollars of a reading, fitted to the logged readings."""
    log = CACHE_DIR / "read-papers.jsonl"
    if not log.exists():
        return DEFAULT_FIT
    xs, ys = [], []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        # Only readings that logged the length they were sent: the older ones read markdown.
        if entry.get("chars") and entry.get("usd"):
            xs.append(entry["chars"])
            ys.append(entry["usd"])
    if len(xs) < 20:
        return DEFAULT_FIT
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    spread = sum((x - mx) ** 2 for x in xs)
    if not spread:
        return DEFAULT_FIT
    per_char = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / spread
    return my - per_char * mx, per_char


def scope_state(scope, reviews, fit):
    """The counts of one scope, and its papers to read and to re-read with their costs."""
    papers = paper_files(LIBRARY_DIR / scope)
    unread, reread = [], []
    for p in papers:
        if not has_digest(p):
            unread.append(p)
        elif reread_reason(p):
            reread.append(p)
    cost = {p: fit[0] + fit[1] * len(text_view(*read_paper(p))) for p in unread + reread}
    review = reviews.get(scope)
    if review:
        meta = review["meta"]
        state = f"checked {meta['checked']}" if meta.get("checked") else f"written {meta.get('updated', '?')}"
        in_scope, listed = review_coverage(review)
        if in_scope - listed:
            state += f" +{len(in_scope - listed)}"
    else:
        state = "—"
    return {"papers": papers, "unread": unread, "reread": reread, "cost": cost, "review": state}


def money(x):
    return f"${x:,.0f}" if x >= 10 else f"${x:,.2f}"


def overview():
    fit, reviews = cost_fit(), load_reviews()
    seen = set()
    width = max([len(s) for _, scopes in review_scopes() for s in scopes] + [10]) + 2
    header = f"  {'scope':{width}s}{'papers':>7s}{'read':>6s}{'to read':>9s}{'re-read':>9s}{'cost':>8s}   review"
    print(styled(header, 1))
    totals = [0, 0, 0, 0, 0.0]
    for group, scopes in review_scopes():
        if group:
            print(styled(group, 1))
        for scope in scopes:
            if not (LIBRARY_DIR / scope).is_dir():
                print(f"  {scope:{width}s}  not a folder of the library")
                continue
            s = scope_state(scope, reviews, fit)
            n, unread, reread = len(s["papers"]), len(s["unread"]), len(s["reread"])
            cost = sum(s["cost"].values())
            seen.update(s["papers"])
            line = (f"  {scope:{width}s}{n:7d}{n - unread:6d}{unread:9d}{reread or '':>9}"
                    f"{money(cost) if cost else '':>8s}   {s['review']}")
            print(styled(line, 2) if not unread and not reread else line)
            for i, v in enumerate((n, n - unread, unread, reread, cost)):
                totals[i] += v
    outside = [p for p in paper_files() if p not in seen]
    print(styled(f"  {'all scopes':{width}s}{totals[0]:7d}{totals[1]:6d}{totals[2]:9d}{totals[3] or '':>9}"
                 f"{money(totals[4]):>8s}", 1))
    if outside:
        print(f"{len(outside)} papers are in no review scope (review_scopes in paper-library.yaml).")
    print("Cost: API price of `paperlib read`, a request a paper. `paperlib reading <scope>` lists them.")


def one_scope(scope):
    if not (LIBRARY_DIR / scope).is_dir():
        sys.exit(f"reading: `{scope}` is not a folder of the library")
    s = scope_state(scope, load_reviews(), cost_fit())
    n, unread, reread = len(s["papers"]), s["unread"], s["reread"]
    print(f"{scope}: {n} papers, {n - len(unread)} read, {len(unread)} to read "
          f"({money(sum(s['cost'][p] for p in unread))}), {len(reread)} to re-read "
          f"({money(sum(s['cost'][p] for p in reread))}); review: {s['review']}")
    for p in unread:
        print(f"  to read   {money(s['cost'][p]):>6s}  {p.relative_to(LIBRARY_DIR)}")
    for p in reread:
        print(f"  re-read   {money(s['cost'][p]):>6s}  {p.relative_to(LIBRARY_DIR)}: {reread_reason(p)}")
    if unread:
        print(f"Read them: paperlib read {scope}  (--limit N to spend a known budget)")
    if reread:
        print(f"Read again: paperlib read --flagged {scope}")


def reread(argv):
    clear = "--clear" in argv
    reason = None
    if "--reason" in argv:
        i = argv.index("--reason")
        if i + 1 >= len(argv):
            sys.exit(__doc__)
        reason = argv[i + 1]
        del argv[i:i + 2]
    papers = [a for a in argv if not a.startswith("--")]
    if not papers or clear == bool(reason):
        sys.exit(__doc__)
    for paper in papers:
        if flag_reread(paper, None if clear else reason):
            print(f"reread: {'cleared' if clear else 'marked'} {paper_stem(paper)}")
        else:
            print(f"reread: {paper_stem(paper)} has no note with a digest; `paperlib read` reads it anyway")


def main(argv):
    if argv[:1] == ["reread"]:
        return reread(argv[1:])
    if any(a in ("-h", "--help") for a in argv) or len(argv) > 1:
        sys.exit(__doc__)
    if argv:
        one_scope(argv[0].strip("/"))
    else:
        overview()


if __name__ == "__main__":
    main(sys.argv[1:])
