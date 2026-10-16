---
id: hand-edited-stale
title: "A hand-edited paper keeps an older converter's flaws"
converter: any
takes: [by-hand, reconvert]
status: open
cost: "by hand: reconvert with --force, then put the hand edit back"
---

# A hand-edited paper keeps an older converter's flaws

`by-hand` `reconvert` · any · open

**Broken.** A paper marked `<!-- hand-edited -->` is skipped by `paperlib reconvert`, so it keeps flaws a later converter fixes.

**Fix.** Reconvert it with `--force`, then redo the hand edit on the new conversion.

**What it gives.** The paper gets the converter's later fixes.

**Cost.** By hand: reconvert with --force, then put the hand edit back.

**Examples.** "Memory in the Age of AI Agents": keeps "§ what-memory" for Section 3; a reconversion with `--force` resolves such references from the LaTeX source; its cropped Figure 1 has to be put back after.
