# Task: reconvert the library with the fixed converter, then validate

On 2026-10-01 the arXiv HTML converter learned to recover what it used to lose (see "Conversion"
in `docs/library.md`): boxed text and prompt templates, scaled tables, header rows, `forest`
trees, prose inside equation tables, figure links, IEEE and "1." heading numbers for page
markers. The 25 papers in `catalog/conversion-issues.yaml` and `llm/personalization` were
reconverted in `main` as pilots. This task reconverts everything else and checks the result.

## The run (Anton starts it)

It runs in a separate worktree, so other sessions can keep working in `~/papers`:

```sh
git -C ~/papers worktree add ~/papers-reconvert -b reconvert-library
cd ~/papers-reconvert
caffeinate -i python3 scripts/reconvert.py --all --jobs 3 --state ~/.cache/papers/reconvert-2026-10-01.jsonl
```

- About 1,900 papers, roughly 2–3 hours: most of the time is re-encoding figures.
- `--state` records each paper's outcome as a JSON line. Running the same command again
  skips papers that are done and retries the rest (HTML not fetched, figures not all
  downloaded, conversion errors). The pilots are already in that file, so they are skipped.
- Every download (pages, figures, LaTeX sources) is cached under `~/.cache/papers/arxiv/`
  (about 10 GB), so a rerun or a later reconversion needs no network. Failed downloads are
  not cached, so a rerun fetches them again.
- Hand-edited papers, web articles and PDF-text papers without arXiv HTML are skipped. A
  PDF-text paper that arXiv now renders becomes `source: html`.
- If arXiv throttles (many `failed` lines), stop with Ctrl-C and rerun with `--jobs 1`.

## Validation (a follow-up session, in `~/papers-reconvert`)

1. **Outcomes.** Summarise the state file by status (last record per paper wins):
   ```sh
   python3 -c "import json,collections; d={}; [d.__setitem__(r['paper'], r) for r in map(json.loads, open('$HOME/.cache/papers/reconvert-2026-10-01.jsonl'))]; print(collections.Counter(r['status'] for r in d.values())); [print(r['status'], r['paper'], r['message']) for r in d.values() if r['status'] in ('failed', 'partial')]"
   ```
   Rerun the reconvert command until only lasting failures are left. A figure that arXiv
   serves broken stays `partial`. A paper whose PDF moved in `main` during the run fails on
   page mapping: leave it for after the merge.
2. **Tests:** `python3 scripts/test_conversion.py` passes.
3. **Symptoms:** `python3 scripts/conversion-symptoms.py --counts`. Before the run, 1,618
   papers had a symptom. Expect close to zero for `flat-table`, `forest`, `pt-residue`,
   `macro`, `figure-link`, `box` and `badge`. Some `empty-header` tables remain: tables with
   no rule under the header give no cue. List the papers with what remains (drop `--counts`),
   open a few of each kind, and decide whether it is a converter bug (fix it, add a check to
   `test_conversion.py`, reconvert those papers) or arXiv's HTML lacking the content (add an
   entry to `catalog/conversion-issues.yaml`).
4. **Nothing lost:** `python3 scripts/conversion-symptoms.py --compare main` lists papers whose
   prose shrank by more than 5%. Diff each against `main` (`git diff main -- <paper>`) and
   explain the loss or fix it. Placeholder alt text ("Refer to caption") is meant to go, and
   is not counted.
5. **Spot check:** compare ten random reconverted papers with their PDFs (open them from the
   paths `library/<topic>/<Title>.md` → `~/Yandex.Disk.localized/Papers/<topic>/<Title>.pdf`):
   boxes read as quotes, tables have their header, figures are local files, headings carry
   correct pages.
6. **Merge.** Commit in the worktree (Anton commits), then in `~/papers`:
   `git merge reconvert-library`. Resolve conflicts in generated `README.md` files by
   rerunning `scripts/build-index.py`, which must be run after the merge anyway. Then run
   `scripts/check-library.py`, which must pass, and remove the worktree:
   `git worktree remove ~/papers-reconvert && git branch -d reconvert-library`.
7. Delete this file and remove the "Separately: conversion fixes" note from
   `docs/tasks/literature-review.md`, or reword it if entries remain.
