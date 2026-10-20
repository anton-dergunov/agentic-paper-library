# Task: re-read a flagged note from what the fix changed, not the whole paper

When a converter fix reaches a paper whose closed records broke key content, `paperlib issues close` marks its note `reread:` and `paperlib read --flagged` (or `--redo`) reads the whole paper again: one request with the full reading view, a new digest and related list, the Q&A kept, the reader's records replaced. It knows nothing of what the fix changed. For EuroBERT that is 28.9K input and 5.1K output tokens, $0.24 with Opus, while the fix touched 280 lines (7 KB of 135 KB), all in two tables, and a handful of the note's lines.

A patch mode would send the old note, the paper's diff since the note was written (whitespace ignored) and the `reread:` reason (ticket and place), and ask for the note with only what depends on the changed parts corrected: about 5–6K tokens instead of about 29K. Before building it, measure whether its notes are as good as a full re-read's.

## What a patch could lose

- **What the first reading left out.** Reading broken tables, the reader spent space on caveats and may have skipped analysis it would have made from clean numbers; a patch corrects what the note says, not what it omits.
- **A check of the fix.** A full re-read looks at the fixed part cold and records any problem left; today that is the only independent check that a fix landed in the paper.
- **Errors of the first reading.** Checking every claim that rests on the changed part can catch them: patching EuroBERT by hand (library commit `55b0bf43a`) found that the note had EuroBERT-2.1B in SeaHorse's best cluster "only on the European-language row", while the table, before and after the fix, has it alone there on both rows. A patch told only to repair what the fix touched would have kept that.

## The test set

In the author's library (`~/papers`), each case has the note written from the broken conversion, the paper before and after, and for one a full re-read already:

| Paper | Old note | Paper before → after | Reference |
|---|---|---|---|
| Glorot & Bengio, "Understanding the difficulty of training deep feedforward neural networks" (`pdf-table-bold`) | `8969b9e25^` | `8969b9e25^` → `8969b9e25` | full re-read in `a213941aa` |
| EuroBERT (`html-cell-attachments`, key content) | `ddddc4308` | `cee2da2b8` → `ddddc4308` | patched by hand in `55b0bf43a`; full re-read to do |
| Phi-3, Qwen3, Movie Gen (tables restored, `html-boxed-table-as-text`) | `ddddc4308` | `cee2da2b8` → `ddddc4308` | full re-read to do |
| SAM 2, Phi-4, Voicebox, "Continual Learning of Large Language Models" (row groups, `html-row-span-heuristics`) | same | same | same |
| Fixup, Nested Learning, The Harvard USPTO Patent Dataset (headers, `html-table-head-rows`) | same | same | same |

The other eight papers reconverted in `ddddc4308` changed little beyond cell padding; leave them out. Later `reread:` flags add cases with no extra work: run both modes on them as they come.

## The measurement

1. For each paper, write the patch-mode note: one request (the reading model, `claude -p` as `paperlib read` sends it) with the old note, `git diff -w <before> <after> -- <paper.md>`, the ticket's Fix and the record's place, asking for the note with what depends on the changed parts corrected and every claim resting on them checked against the new text.
2. Write the reference: `paperlib read --redo <paper.md>` on the after version. Keep both notes outside `notes/` until compared; the reference is committed at the end, as it is the better note either way.
3. Compare, per paper:
   - tokens and cost of each;
   - the digest's claims that differ: which the patch got right, missed, or got wrong, judged against the paper's markdown at the cited page;
   - errors of the old note each one fixed (the SeaHorse kind);
   - the conversion records each one filed.
4. Write it up in `experiments/patch-reread/` (format of [experiments/README.md](../../experiments/README.md)). Cost: about $0.24 a full re-read and a few cents a patch, about $3 for the twelve.

## Then

If the patch matches the full re-read on the claims that matter, add `--patch` to `paperlib read --flagged`: the diff is taken from git since the note's last change, and a diff over a share of the paper (20% to start, set from the measurement) falls back to a full read. Record the decision in `docs/design.md`. If it does not, record that and keep the full re-read. Either way, delete this file.
