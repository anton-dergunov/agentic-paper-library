# Task: reconvert the library with the fixed converters, then validate

On 2026-10-01 both converters were rebuilt (see "Conversion" in `docs/library.md`):

- **arXiv HTML** (`html-to-markdown.py`): boxed text and prompt templates as quotes, scaled
  tables, header rows, `forest` trees, prose inside equation tables, figure links, siunitx
  numbers, icon names, citations rebuilt from the `.bib`; page markers for IEEE and "1."
  heading numbers.
- **PDF-only papers** (`pdf-to-markdown.py`): docling's layout analysis for headings, tables
  and figures, with each equation read from its image by marker's model.

Pilots already in `main`: the 25 papers first listed in `catalog/conversion-issues.yaml`,
`llm/personalization`, and the six papers its review flagged. This task reconverts everything
else in one pass and checks the result.

## The run (Anton starts it, overnight)

In the worktree, so `~/papers` stays free for other sessions. A first partial pass with the
older converter was stopped at 1,359 papers; its downloads are in the cache, and its output is
committed on the branch only so that `main` merges cleanly. This run replaces it.

```sh
cd ~/papers-reconvert && caffeinate -i sh -c '
  python3 scripts/reconvert.py --all --jobs 3 --state ~/.cache/papers/reconvert-pass2.jsonl;
  python3 scripts/reconvert.py --all --jobs 3 --state ~/.cache/papers/reconvert-pass2.jsonl;
  python3 scripts/reconvert.py --all --pdf-text --state ~/.cache/papers/reconvert-pdf.jsonl'
```

1. Every arXiv-HTML paper, about 1,900: 2–3 hours. Downloads only for the ~840 papers not
   cached yet; the rest is re-encoding figures. PDF-only papers that arXiv now renders become
   `source: html` here.
2. The same command again retries what failed (HTML not fetched, a figure not downloaded, a
   conversion error) and skips the rest: minutes.
3. The ~280 PDF-only papers: about a minute each, 3–5 hours.

Each `--state` file records one JSON line per paper, so the same command resumes after an
interruption. Hand-edited papers and web articles are skipped. Everything downloaded is kept
in `~/.cache/papers/arxiv/` (about 10 GB), so reconverting again needs no network.

## Validation (a follow-up session, in `~/papers-reconvert`)

1. **Outcomes.** Summarise both state files by status (last record per paper wins):
   ```sh
   for f in pass2 pdf; do python3 -c "import json,collections,sys; d={}; [d.__setitem__(r['paper'], r) for r in map(json.loads, open(sys.argv[1]))]; print(sys.argv[1], collections.Counter(r['status'] for r in d.values())); [print(' ', r['status'], r['paper'], '|', r['message']) for r in d.values() if r['status'] in ('failed', 'partial')]" ~/.cache/papers/reconvert-$f.jsonl; done
   ```
   If the run did not finish, start it again. Rerun until only lasting failures are left: a
   figure arXiv serves broken stays `partial`; a paper moved in `main` during the run fails
   to find its PDF, and is left for after the merge. For PDF papers, list those whose message
   says "fell back to the text layer" or "equation model failed" and look at why.
2. **Tests:** `python3 scripts/test_conversion.py` passes.
3. **Symptoms:** `python3 scripts/conversion-symptoms.py --counts`. Before, 1,618 HTML papers
   had a symptom. Expect close to zero for `flat-table`, `forest`, `pt-residue`, `macro`,
   `figure-link`, `box`, `badge`, `digit-groups` and `raw-citations`. Some `empty-header`
   tables remain: a table with no rule under its header gives no cue. List the papers with
   what remains (drop `--counts`), open a few of each kind, and decide whether it is a
   converter bug (fix it, add a check to `test_conversion.py`, reconvert those papers) or
   arXiv's HTML lacking the content (add an entry to `catalog/conversion-issues.yaml`).
4. **Nothing lost:** `python3 scripts/conversion-symptoms.py --compare main` lists HTML papers
   whose prose shrank by more than 5%. Diff each against `main` (`git diff main -- <paper>`)
   and explain the loss or fix it. Placeholder alt text ("Refer to caption") is meant to go
   and is not counted. For PDF papers compare word counts with `main` the same way
   (`git show main:<path> | wc -w`): the new conversion should not be shorter by more than
   running headers and page numbers.
5. **Spot check against the PDFs** (`library/<topic>/<Title>.md` ↔
   `~/Yandex.Disk.localized/Papers/<topic>/<Title>.pdf`):
   - ten random HTML papers: boxes read as quotes, tables have their header, figures are
     local files, headings carry the right pages;
   - ten random PDF-only papers, at least five with equations: headings and their page
     numbers, one table's numbers cell by cell, two equations symbol by symbol, figures
     present with captions. Record how many of the checked equations were right; if fewer than
     about two in three, say so before merging.
6. **Merge.** Commit in the worktree (Anton commits), then in `~/papers`:
   `git merge reconvert-library`. Resolve conflicts in generated `README.md` files by
   rerunning `scripts/build-index.py`, which must be run after the merge anyway (PDF papers
   that became HTML change their `source`). Then `scripts/check-library.py` must pass.
   Remove the worktree: `git worktree remove ~/papers-reconvert && git branch -d reconvert-library`.
7. **Catalog.** Remove entries of `catalog/conversion-issues.yaml` that the run fixed
   (Meta-Learning's equations; check the others), and drop caveats in `reviews/` that no
   longer hold (search for "PDF-text").
8. Delete this file and remove the "Separately: conversion fixes" note from
   `docs/tasks/literature-review.md`, or reword it if entries remain.

## Left for later

- A repo `.venv` with the scripts' dependencies declared (docling, pymupdf, tqdm, pyyaml,
  lxml, pillow); marker stays in its own environment. Today the scripts run on the system
  Python, and marker lives in `~/.cache/papers/venvs/marker`.
- `Memory in the Age of AI Agents`: its `\Cref` targets could get section numbers the way
  `LABEL:` references now do; the paper is hand-edited, so it needs `--force` and its cropped
  Figure 1 put back.
