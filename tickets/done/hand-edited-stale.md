---
id: hand-edited-stale
title: A hand-edited paper keeps an older converter's flaws
converter: any
takes: [by-hand, reconvert]
closed: '2026-10-19'
cost: 'engine: done; a session for a correction a reconversion cannot place'
---

# A hand-edited paper keeps an older converter's flaws

`by-hand` `reconvert` · any · done

**Broken.** A paper marked `<!-- hand-edited -->` is skipped by `paperlib reconvert`, so it keeps flaws a later converter fixes.

**Fix.** Done 19 Oct 2026: a hand edit is a correction in the library's `corrections/<stem>.yaml` (`paperlib corrections capture`), which `paperlib reconvert` applies again to the new conversion: by the converter text it replaces, or by the landmarks around it when that text repeats or changed a little. One it cannot place is kept, marked stale, for `/reapply-corrections`. The library's 25 marked edits in 17 papers became 26 corrections in 15 papers; of the edits as made, applied to today's conversion, 27 of 29 were placed by the program and 2 needed a session, both where the converter now rewrites that very text. Left: Confident Learning, converted from its LaTeX source (`html-incomplete`). → [`experiments/hand-edit-corrections`](../experiments/hand-edit-corrections/README.md)

**What it gives.** The paper gets the converter's later fixes.

**Cost.** Engine: done; a session for a correction a reconversion cannot place.

**Examples.** "Memory in the Age of AI Agents": keeps "§ what-memory" for Section 3; a reconversion with `--force` resolves such references from the LaTeX source; its cropped Figure 1 has to be put back after.
