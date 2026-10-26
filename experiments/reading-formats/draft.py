#!/usr/bin/env python3
"""Draft questions: one request per paper, from its PDF.

    PAPER_LIBRARY=<library> uv run python draft.py <paper> <id prefix> [...]           # tier B2: six kinds
    PAPER_LIBRARY=<library> uv run python draft.py --weak <paper> <id prefix> [...]    # tier G: at the issue records

Writes results/drafts/<paper>.yaml, which is checked by hand against the PDF (and with
`inputs.py check`) before its questions are copied into questions.yaml.
"""

import sys

import inputs
import run

DRAFTS = run.HERE / "results" / "drafts"
SYSTEM = "You write test questions about a research paper for an experiment on document formats. Reply with YAML only."
PROMPT = """Write six questions about this paper, to test whether a model given the paper in some form (the PDF, its text layer, or a markdown conversion) can answer them. Each needs one short, checkable gold answer taken from the paper, with the PDF page it is on.

The six, in this order:
1. table: a value (or two) from a results table, from a cell that the prose does not repeat.
2. table: a second table, or a comparison across rows or columns of one (which method is best on a column, and its value).
3. equation: the paper's central equation or objective, written out, with what its terms are.
4. appendix: a training or setup detail given only in the appendix (hyperparameters, data sizes).
5. figure: a value that can only be read off a plot: printed nowhere in the text, a table or a caption. Give the gold as approximate, and a tolerance a careful reader of the plot would meet.
6. unanswerable: a plausible question whose answer the paper does not report (a benchmark, model size or metric it does not use). The gold says it is not reported and what the paper reports instead.

Ask each question without naming its table, figure or page, as a reader would ("What accuracy does X get on Y?"). Avoid values stated in the abstract or introduction.

Reply with a YAML list in exactly this form, nothing else:
- {{id: {prefix}1, exp: E1, paper: {paper}, kind: table, page: 6,
   question: '...',
   gold: '... (Table 3).'}}
- {{id: {prefix}5, exp: E1, paper: {paper}, kind: figure, page: 7,
   question: '...',
   gold: 'About ... (Figure 4, left).', tolerance: '...'}}
- {{id: {prefix}6, exp: E1, paper: {paper}, kind: unanswerable, answerable: false, page: 9,
   question: '...',
   gold: 'Not reported: ...'}}
"""
# Tier G: the issue records say where the PDF's text layer misled the converter; the
# questions are aimed at those passages, so that a reader of the text layer meets them too.
PROMPT_WEAK = """The library's issue records say that this paper's PDF text layer is broken or flawed in these places:

{issues}

Write two questions about this paper whose answers depend on what is printed in those places, to test whether a model given the paper as its text layer, a markdown conversion, or the PDF can still answer them. Prefer the passages a reader would actually ask about (an equation, a table cell, a key definition or number) over cosmetic ones (a footnote number, a heading). Each needs one short, checkable gold answer taken from the paper as printed (read the page image, not the text), with its PDF page. If the printed page itself seems wrong, say so in the gold.

Ask each question without naming its table, figure or page, as a reader would. Reply with a YAML list in exactly this form, nothing else:
- {{id: {prefix}1, exp: E8, paper: {paper}, kind: equation, page: 4,
   question: '...',
   gold: '... (Eq. 3).', passage: 'which issue record it aims at, in a few words'}}
"""


def issues(paper):
    record = inputs.LIBRARY_ROOT / "issues" / (inputs.md_path(paper).stem + ".yaml")
    return record.read_text()


def draft(paper, prefix, weak=False):
    target = DRAFTS / ("%s.yaml" % paper)
    if target.exists():
        return
    prompt = (PROMPT_WEAK.format(issues=issues(paper), prefix=prefix, paper=paper) if weak
              else PROMPT.format(prefix=prefix, paper=paper))
    result, _ = run.request(SYSTEM, [run.document(inputs.pdf(paper)), {"type": "text", "text": prompt}])
    reply = (result.get("result") or "").strip()
    if reply.startswith("```"):
        reply = reply.split("\n", 1)[1].rsplit("```", 1)[0]
    DRAFTS.mkdir(parents=True, exist_ok=True)
    target.write_text("# Drafted from the PDF by %s, $%.2f; not yet checked\n%s\n" % (
        run.MODEL, result.get("total_cost_usd") or 0, reply))
    print("%s: $%.2f -> %s" % (paper, result.get("total_cost_usd") or 0, target), flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    weak = "--weak" in args
    args = [a for a in args if a != "--weak"]
    for paper, prefix in zip(args[::2], args[1::2]):
        draft(paper, prefix, weak)
