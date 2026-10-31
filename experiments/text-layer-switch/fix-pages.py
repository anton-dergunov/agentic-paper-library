#!/usr/bin/env python3
"""Correct the prose page citations of notes read from the old markdown (README.md, "Afterwards").

    PAPER_LIBRARY=<library> uv run python fix-pages.py <mode>

    measure                         score the rules on known answers
    apply [margin]                  the rules, on every note; results/pages.tsv, pages-left.tsv
    measure-model [n] [margin] [model]   the model's pick on n known answers the rules leave open
    apply-model [model]             the model's pick for what `apply` left open; results/pages-model.tsv
    reviews [model] [--write]       the rules, then the model, on reviews' prose links; results/pages-reviews.tsv

`paperlib check-pages --fix` corrects the tables and figures first.

The markdown the notes were read from (until 26 Oct 2026) marked pages only on headings:
`### 4.3 Title (p. 6)` gave the page a section starts on, so a note's "(p. 6)" is the first
page of the section the claim came from, and the claim may be printed a page or more later.
The markdown is still in the library's git history (kept by the ref refs/archive/markdown,
and found for each note through git filter-repo's commit map), so each note is matched
against the version it was read from:

- the old markdown is cut into passages (sentences, merged to 12 words or more), each with
  its heading's page, and each passage is placed on the text layer's page(s) that print its
  word 4-grams;
- a citation "(p. N)" can only come from the passages under headings marked p. N. Rules, in
  order: `quote` (a quote of three or more words in the claim is printed on one page),
  `section` (every placed passage under p. N is on one page), `words` (the passage
  sharing the claim's rarest words wins by a margin).

What the rules leave open goes to a model (Haiku): the claim and the passages under its
heading, numbered; it names the passage the claim states, and the claim takes that passage's
page when the passage is placed on one page. Tables and figures are `paperlib check-pages`'s;
page ranges and the notes read from the text layer are left alone. The `measure` modes score
on the citations that `quote` settles, with the quote taken out of the claim.
"""

import collections
import importlib.util
import math
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
sys.path.insert(0, str(ENGINE / "scripts"))

from paperlib import LIBRARY_DIR, LIBRARY_ROOT, NOTES_DIR, paper_files, paper_stem, read_paper  # noqa: E402

spec = importlib.util.spec_from_file_location("check_pages", ENGINE / "scripts" / "check-pages.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

RESULTS = HERE / "results"
ARCHIVE_REF = "refs/archive/markdown"
K = 4  # words in a shingle
MIN_PASSAGE = 12  # words
HEADING = re.compile(r"^#{1,6} .*?\(p\. (\d+)\)\s*$")
ANY_HEADING = re.compile(r"^#{1,6} ")
TABLE = re.compile(r"<t[dhr][ >]|^\|.*\|", re.M)
QUOTE = re.compile(r"[\"“]([^\"”]+)[\"”]")
STOP = set("""this that with from their these which have been were they than more also into only each when
other over such both does used uses using show shows shown table figure paper authors same between under
about while there most within where after before across without because being through them then those
some what would could should very much many like just make makes made data model models method methods
result results report reports reported""".split())


def git(*args):
    done = subprocess.run(["git", "-C", str(LIBRARY_ROOT), *args], capture_output=True)
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def words(text):
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?%?", unicodedata.normalize("NFKC", text).lower())


def terms(text):
    """The words of a claim that can tell passages apart: numbers, and words of four letters
    or more that are not common."""
    return {w for w in words(text) if (any(c.isdigit() for c in w) and len(w.strip("%")) >= 2)
            or (len(w) >= 4 and w not in STOP)}


def folded(text):
    return "".join(c for c in unicodedata.normalize("NFKC", text).lower() if c.isalnum())


# --- the old markdown each note was read from -------------------------------------------

def old_versions():
    """{note stem: old commit}, for notes whose last change before the switch was made with the
    markdown; notes written from the text layer are left out."""
    lines = (LIBRARY_ROOT / ".git" / "filter-repo" / "commit-map").read_text().split("\n")[1:]
    old_of = {new: old for old, new in (l.split() for l in lines if l.strip())}
    tip_old = git("rev-parse", ARCHIVE_REF).strip()
    tip_new = next(new for new, old in old_of.items() if old == tip_old)
    found, commit = {}, None
    for line in git("log", "--format=@%H", "--name-only", tip_new, "--", "notes").splitlines():
        if line.startswith("@"):
            commit = line[1:]
        elif line.strip() and Path(line).stem not in found:
            found[Path(line).stem] = commit
    # The tip replaced four notes with ones read from the text layer.
    return {stem: old_of[new] for stem, new in found.items() if new != tip_new and new in old_of}


_trees = {}


def old_markdown(commit, paper):
    """The paper's markdown at an old commit, found by its path or else by its stem."""
    rel = paper.relative_to(LIBRARY_ROOT).with_suffix(".md").as_posix()
    text = git("show", f"{commit}:{rel}")
    if text is not None:
        return text
    if commit not in _trees:
        listing = git("ls-tree", "-r", "--name-only", commit, "--", "library") or ""
        _trees[commit] = {paper_stem(p): p for p in listing.splitlines() if p.endswith(".md")}
    path = _trees[commit].get(paper_stem(paper))
    return git("show", f"{commit}:{path}") if path else None


# --- passages and where they are printed ------------------------------------------------

def passages(markdown):
    """[(heading's page, text)]: the markdown's prose cut at sentences, merged to MIN_PASSAGE words."""
    body = re.sub(r"\A---\n.*?\n---\n", "", markdown, flags=re.S)
    out, page = [], None
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        first = block.splitlines()[0]
        if ANY_HEADING.match(first):
            m = HEADING.match(first)
            page = int(m.group(1)) if m else page
            continue
        if page is None:
            continue
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", " ".join(block.split()))
        cur = []
        for s in sentences:
            cur.append(s)
            if len(words(" ".join(cur))) >= MIN_PASSAGE:
                out.append((page, " ".join(cur)))
                cur = []
        if cur:
            if out and out[-1][0] == page and len(words(" ".join(cur))) < MIN_PASSAGE:
                out[-1] = (page, out[-1][1] + " " + " ".join(cur))
            else:
                out.append((page, " ".join(cur)))
    return out


class TextLayer:
    """A paper's text layer: its pages, and the pages each word 4-gram is printed on."""

    def __init__(self, path):
        self.pages = cp.text_pages(read_paper(path)[1])
        self.folded = {n: folded(t) for n, t in self.pages.items()}
        self.grams = collections.defaultdict(set)
        for n, text in self.pages.items():
            for line in text.splitlines():
                for seg in cp._COLUMN_GAP.split(line.strip()):
                    w = words(seg)
                    for i in range(len(w) - K + 1):
                        self.grams[" ".join(w[i:i + K])].add(n)
            # Across lines too, for 4-grams that a column's line break splits.
            w = words(text)
            for i in range(len(w) - K + 1):
                self.grams[" ".join(w[i:i + K])].add(n)

    def place(self, text):
        """The pages that print a passage: those holding at least two of its 4-grams that
        are printed on one page only, and a quarter of the best page's count."""
        w = words(text)
        votes = collections.Counter()
        for i in range(len(w) - K + 1):
            where = self.grams.get(" ".join(w[i:i + K]))
            if where and len(where) == 1:
                votes[next(iter(where))] += 1
        if not votes:
            return set()
        top = max(votes.values())
        return {p for p, v in votes.items() if v >= 2 and v >= top / 4}

    def quote_pages(self, quote):
        q = folded(quote)
        return [n for n, t in self.folded.items() if q and q in t]


class Paper:
    """A note's paper: its placed passages and the rarity of their words."""

    def __init__(self, path, markdown):
        self.layer = TextLayer(path)
        # A table's cells are not placed: its words are spread across the text layer's lines,
        # and its numbers match a claim's best of all.
        self.passages = [(n, text, set() if TABLE.search(text) else self.layer.place(text), terms(text))
                         for n, text in passages(markdown)]
        df = collections.Counter(t for *_, ts in self.passages for t in ts)
        total = len(self.passages) or 1
        self.idf = {t: math.log(total / c) for t, c in df.items()}


# --- the rules --------------------------------------------------------------------------

def claims(text):
    """(Ref, claim) for each single-page prose citation in a note: the claim is the text
    between the previous citation on its line (or the line's start) and this one."""
    out = []
    refs = cp.note_refs(text)
    groups = list(cp._GROUP.finditer(text))
    for i, g in enumerate(groups):
        line_start = text.rfind("\n", 0, g.start()) + 1
        prev = [h for h in groups[:i] if h.end() >= line_start]
        start = prev[-1].end() if prev else line_start
        claim = re.sub(r"^\s*[-*]\s+|^\s*\d+\.\s+", "", text[start:g.start()])
        out += [(r, claim) for r in refs
                if g.start() <= r.start < g.end() and not r.floats and r.first == r.last]
    return out


def decide(paper, page, claim, use_quote=True, margin=None):
    """(new page or None, rule, score): a rule that settles the citation, or None."""
    if use_quote:
        for q in QUOTE.findall(claim):
            if len(q.split()) < 3:
                continue
            hits = paper.layer.quote_pages(q)
            if len(hits) == 1:
                return hits[0], "quote", 0.0
    under = [(placed, ts) for n, _, placed, ts in paper.passages if n == page]
    placed = set().union(*(p for p, _ in under)) if under else set()
    if not placed:
        return None, "no passages", 0.0
    if len(placed) == 1 and all(p for p, _ in under):
        return next(iter(placed)), "section", 0.0
    if margin is None:
        return None, "open", 0.0
    want = terms(QUOTE.sub(" ", claim) if not use_quote else claim)
    # The best passage on each page. A passage printed across a page break counts for both
    # pages, and one that could not be placed counts for none (key None): when it wins, the
    # claim's page is unknown.
    best = collections.defaultdict(float)
    for where, ts in under:
        score = sum(paper.idf.get(t, 0) for t in want & ts)
        for p in where or [None]:
            best[p] = max(best[p], score)
    ranked = sorted(best.items(), key=lambda kv: -kv[1])
    top, second = ranked[0], ranked[1][1] if len(ranked) > 1 else 0.0
    if top[0] is not None and top[1] - second >= margin and top[1] > 0:
        return top[0], "words", top[1] - second
    return None, "open", top[1] - second


# --- the model's pick -------------------------------------------------------------------

MODEL_SYSTEM = """You match claims from a reader's note on a research paper to the passages of the paper they \
came from. Each claim names a section by its id; the section's passages are numbered. For each claim, list \
the passages that state what the claim says (numbers, findings, wording), most relevant first, at most three. \
If no passage states it, give an empty list. Reply with JSON only: {"<claim id>": [<passage numbers>], ...}"""


def model_request(paper, items):
    """The prompt for one note's open citations: [(claim id, page, claim)]. Returns the
    prompt and {(page, passage number): placed pages}."""
    sections, placed = {}, {}
    for _, page, _ in items:
        if page not in sections:
            under = [(text, where) for n, text, where, _ in paper.passages if n == page]
            sections[page] = under
            for i, (_, where) in enumerate(under, 1):
                placed[(page, i)] = where
    parts = []
    for page, under in sections.items():
        parts.append(f"## Section S{page}\n" + "\n".join(f"[{i}] {text[:1200]}" for i, (text, _) in enumerate(under, 1)))
    parts.append("## Claims\n" + "\n".join(f"{cid} (section S{page}): {claim.strip()}" for cid, page, claim in items))
    return "\n\n".join(parts), placed


def model_pages(reply, items, placed):
    """{claim id: page or None}: the page of the passages named, when they are placed on one page."""
    import json
    m = re.search(r"\{.*\}", reply, re.S)
    picks = json.loads(m.group(0)) if m else {}
    out = {}
    for cid, page, _ in items:
        pages = set()
        for n in picks.get(cid, [])[:1]:
            pages |= placed.get((page, int(n)), set())
        out[cid] = next(iter(pages)) if len(pages) == 1 else None
    return out


def ask(paper, items, model="haiku"):
    from paperlib import ask_model
    prompt, placed = model_request(paper, items)
    reply, usage = ask_model(model, MODEL_SYSTEM, prompt)
    return model_pages(reply, items, placed), usage


def measure_model(limit, margin, model="haiku", workers=4):
    """The model's pick on citations a quote settles but the other rules leave open, the
    quote taken out of the claim: right, wrong, unsure, and the cost."""
    import concurrent.futures
    jobs = []
    for note, path, markdown in notes_with_papers():
        text = note.read_text(encoding="utf-8")
        found = [(r, c) for r, c in claims(text) if any(len(q.split()) >= 3 for q in QUOTE.findall(c))]
        if not found:
            continue
        paper = Paper(path, markdown)
        items, truths = [], {}
        for i, (ref, claim) in enumerate(found):
            truth, rule, _ = decide(paper, ref.first, claim)
            if rule != "quote":
                continue
            page, rule, _ = decide(paper, ref.first, claim, use_quote=False, margin=margin)
            if page is None and rule == "open":
                cid = f"c{i}"
                items.append((cid, ref.first, QUOTE.sub("…", claim)))
                top, _, _ = decide(paper, ref.first, claim, use_quote=False, margin=0)
                truths[cid] = (truth, ref.first, top)
        if items:
            jobs.append((note.stem, paper, items, truths))
        if sum(len(j[2]) for j in jobs) >= limit:
            break
    tally, cost, tokens = collections.Counter(), 0.0, 0
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(ask, paper, items, model): (stem, truths) for stem, paper, items, truths in jobs}
        for f in concurrent.futures.as_completed(futures):
            stem, truths = futures[f]
            try:
                pages, usage = f.result()
            except Exception as e:  # noqa: BLE001
                tally["request failed"] += 1
                print(f"{stem}: {e}", file=sys.stderr)
                continue
            cost += usage.get("usd") or 0
            tokens += usage["input"]
            for cid, (truth, cited, top) in truths.items():
                page = pages.get(cid)
                for name, pick in (("model", page), ("model and words agree", page if page == top else None)):
                    if pick is None:
                        tally[f"{name}: unsure"] += 1
                    elif pick == cited:
                        tally[f"{name}: kept, right" if pick == truth else f"{name}: kept, a fix missed"] += 1
                    elif pick == truth:
                        tally[f"{name}: moved, fixed"] += 1
                    else:
                        tally[f"{name}: moved, broke a right page" if truth == cited else f"{name}: moved, still wrong"] += 1
    n = sum(len(j[2]) for j in jobs)
    print(f"{n} citations in {len(jobs)} requests, ${cost:.2f}, {tokens:,} input tokens")
    for k, v in sorted(tally.items()):
        print(f"{k}\t{v}")


# --- the commands -----------------------------------------------------------------------

def notes_with_papers():
    versions = old_versions()
    stems = {paper_stem(p): p for p in paper_files() if p.suffix == ".txt"}
    for note in sorted(NOTES_DIR.glob("*.md")):
        if note.stem in stems and note.stem in versions:
            markdown = old_markdown(versions[note.stem], stems[note.stem])
            if markdown:
                yield note, stems[note.stem], markdown


def measure(margins=(2, 4, 6, 8)):
    """Score `section` and `words` on the citations a quote settles, the quote taken out."""
    tally = collections.Counter()
    for note, path, markdown in notes_with_papers():
        text = note.read_text(encoding="utf-8")
        found = [(r, c) for r, c in claims(text)
                 if any(len(q.split()) >= 3 for q in QUOTE.findall(c))]
        if not found:
            continue
        paper = Paper(path, markdown)
        for ref, claim in found:
            truth, rule, _ = decide(paper, ref.first, claim)
            if rule != "quote":
                continue
            tally["known"] += 1
            tally["known, right as written" if truth == ref.first else "known, wrong as written"] += 1
            for m in margins:
                page, rule, _ = decide(paper, ref.first, claim, use_quote=False, margin=m)
                if page is None:
                    tally[f"margin {m}: open"] += 1
                    continue
                if page == ref.first:
                    outcome = "kept, right" if page == truth else "kept, a fix missed"
                elif page == truth:
                    outcome = "moved, fixed"
                else:
                    outcome = "moved, broke a right page" if truth == ref.first else "moved, still wrong"
                tally[f"margin {m}: {rule} {outcome}"] += 1
    for k, v in sorted(tally.items()):
        print(f"{k}\t{v}")


def apply_model(model="haiku", workers=6):
    """The model's pick for the citations `apply` left open (results/pages.tsv), one request
    per note; its choices go to results/pages-model.tsv."""
    import concurrent.futures
    import csv
    open_by_note = collections.defaultdict(list)
    with open(RESULTS / "pages.tsv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    order = collections.defaultdict(list)
    for r in rows:
        order[r["note"]].append(r)
    jobs = []
    for note, path, markdown in notes_with_papers():
        if note.stem not in order:
            continue
        text = note.read_text(encoding="utf-8")
        found = claims(text)
        logged = order[note.stem]
        if len(found) != len(logged):
            print(f"{note.stem}: {len(found)} citations now, {len(logged)} logged; skipped", file=sys.stderr)
            continue
        items = [(f"c{i}", ref.first, claim) for i, ((ref, claim), r) in enumerate(zip(found, logged))
                 if r["rule"] == "open" and int(r["cited"]) == ref.first]
        if items:
            jobs.append((note, Paper(path, markdown), items))
    print(f"{sum(len(j[2]) for j in jobs)} open citations in {len(jobs)} notes", flush=True)
    tally, cost, out = collections.Counter(), 0.0, []
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(ask, paper, items, model): (note, items) for note, paper, items in jobs}
        for done, f in enumerate(concurrent.futures.as_completed(futures), 1):
            note, items = futures[f]
            try:
                pages, usage = f.result()
            except Exception as e:  # noqa: BLE001
                tally["request failed"] += len(items)
                print(f"{note.stem}: {e}", file=sys.stderr)
                continue
            cost += usage.get("usd") or 0
            text = note.read_text(encoding="utf-8")
            found = claims(text)
            fixes = []
            for cid, cited, _ in items:
                page = pages.get(cid)
                ref = found[int(cid[1:])][0]
                tally["unsure" if page is None else "kept" if page == cited else "moved"] += 1
                out.append((note.stem, cited, page or ""))
                if page and page != cited and ref.first == cited:
                    fixes.append((ref, ref.text(page, page)))
            if fixes:
                note.write_text(cp.apply(text, fixes), encoding="utf-8")
            if done % 100 == 0:
                print(f"{done} of {len(jobs)} notes, ${cost:.2f}", flush=True)
    with open(RESULTS / "pages-model.tsv", "w", encoding="utf-8") as f:
        f.write("note\tcited\tpage\n")
        f.writelines(f"{a}\t{b}\t{c}\n" for a, b, c in out)
    print(f"${cost:.2f}")
    for k, v in sorted(tally.items()):
        print(f"{k}\t{v}")


_MD_LINK = re.compile(r"\[((?:\\.|[^\]\\])*)\]\([^)\s]+\)")


def review_claims(inline):
    """(Ref, paper stem, link match, claim) for each single-page prose link in a review
    written inline; the claim is its sentence up to the link, links reduced to their text."""
    out = []
    links = list(cp._REVIEW_LINK.finditer(inline))
    for ref, stem, m in cp.review_link_refs(inline):
        if ref.floats or ref.first != ref.last:
            continue
        line_start = inline.rfind("\n", 0, m.start()) + 1
        start = max(line_start, inline.rfind(". ", line_start, m.start()) + 1,
                    max((l.end() for l in links if line_start <= l.end() <= m.start()), default=0))
        out.append((ref, stem, m, _MD_LINK.sub(r"\1", inline[start:m.start()])))
    return out


def fix_reviews(margin, model=None, write=False):
    """The rules, then the model if named, for the reviews' prose links; written with --write."""
    from paperlib import load_reviews
    rr = cp._review_refs_module()
    tip = git("rev-parse", ARCHIVE_REF).strip()
    stems = {paper_stem(p): p for p in paper_files() if p.suffix == ".txt"}
    papers, tally, rows = {}, collections.Counter(), []
    for review in [f for r in load_reviews().values() for f in r["files"]]:
        inline = rr.to_inline(review.read_text(encoding="utf-8"))
        decided, open_items = [], collections.defaultdict(list)
        for i, (ref, stem, m, claim) in enumerate(review_claims(inline)):
            if stem not in papers:
                md = old_markdown(tip, stems[stem]) if stem in stems else None
                papers[stem] = Paper(stems[stem], md) if md else None
            paper = papers[stem]
            page, rule, _ = decide(paper, ref.first, claim, margin=margin) if paper else (None, "no markdown", 0)
            if page is None and rule == "open" and model:
                open_items[stem].append((f"c{i}", ref.first, claim, ref, m))
                continue
            tally[f"{rule}, {'moved' if page and page != ref.first else 'kept' if page else 'left'}"] += 1
            rows.append((review.name, stem, ref.first, page or "", rule))
            if page and page != ref.first:
                decided.append((ref, m, ref.text(page, page), page))
        for stem, items in open_items.items():
            pages, usage = ask(papers[stem], [(c, p, cl) for c, p, cl, _, _ in items], model)
            for cid, cited, _, ref, m in items:
                page = pages.get(cid)
                tally[f"model, {'moved' if page and page != cited else 'kept' if page else 'left'}"] += 1
                rows.append((review.name, stem, cited, page or "", "model"))
                if page and page != cited:
                    decided.append((ref, m, ref.text(page, page), page))
        if write and decided:
            review.write_text(rr.to_references(cp.fix_review_text(inline, decided), review), encoding="utf-8")
    with open(RESULTS / "pages-reviews.tsv", "w", encoding="utf-8") as f:
        f.write("review\tpaper\tcited\tpage\trule\n")
        f.writelines("\t".join(map(str, r)) + "\n" for r in rows)
    for k, v in sorted(tally.items()):
        print(f"{k}\t{v}")


def apply_rules(margin):
    RESULTS.mkdir(exist_ok=True)
    rows, tally, per_note = [], collections.Counter(), {}
    for note, path, markdown in notes_with_papers():
        text = note.read_text(encoding="utf-8")
        found = claims(text)
        if not found:
            continue
        paper = Paper(path, markdown)
        fixes, left = [], 0
        for ref, claim in found:
            page, rule, score = decide(paper, ref.first, claim, margin=margin)
            tally[f"{rule}, {'moved' if page and page != ref.first else 'kept' if page else 'left'}"] += 1
            rows.append((note.stem, ref.first, page or "", rule, f"{score:.1f}"))
            if page and page != ref.first:
                fixes.append((ref, ref.text(page, page)))
            left += page is None
        per_note[note.stem] = (len(found), len(fixes), left)
        if fixes:
            note.write_text(cp.apply(text, fixes), encoding="utf-8")
    with open(RESULTS / "pages.tsv", "w", encoding="utf-8") as f:
        f.write("note\tcited\tpage\trule\tscore\n")
        f.writelines("\t".join(map(str, r)) + "\n" for r in rows)
    with open(RESULTS / "pages-left.tsv", "w", encoding="utf-8") as f:
        f.write("note\tcitations\tmoved\tleft\n")
        f.writelines(f"{n}\t{a}\t{b}\t{c}\n" for n, (a, b, c) in sorted(per_note.items(), key=lambda kv: -kv[1][2]))
    for k, v in sorted(tally.items()):
        print(f"{k}\t{v}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["measure"]:
        measure()
    elif sys.argv[1:2] == ["reviews"]:
        args = [a for a in sys.argv[2:] if not a.startswith("--")]
        fix_reviews(4.0, args[0] if args else None, write="--write" in sys.argv)
    elif sys.argv[1:2] == ["apply-model"]:
        apply_model(sys.argv[2] if len(sys.argv) > 2 else "haiku")
    elif sys.argv[1:2] == ["measure-model"]:
        measure_model(int(sys.argv[2]) if len(sys.argv) > 2 else 200, float(sys.argv[3]) if len(sys.argv) > 3 else 6.0,
                      sys.argv[4] if len(sys.argv) > 4 else "haiku")
    elif sys.argv[1:2] == ["apply"]:
        apply_rules(float(sys.argv[2]) if len(sys.argv) > 2 else 4.0)
    else:
        sys.exit(__doc__)
