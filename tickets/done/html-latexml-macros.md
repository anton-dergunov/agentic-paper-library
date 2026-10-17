---
id: html-latexml-macros
title: LaTeXML's macros left in formulas
converter: html
takes: [engine, reconvert]
closed: '2026-10-18'
cost: 'engine: small, fixtures; reconvert 20 papers'
---

# LaTeXML's macros left in formulas

`engine` `reconvert` · html · done

**Broken.** `\operatorname{mathbfcal}`, `displaystyleh`, `textsubscript`, the physics package's `quantity` and `expectationvalue`, and `[1.0]{-}` for a minus sign: 396 in 20 papers when filed. `0pt` appears in 88 papers and may be a length or a lost symbol ("depth $0pt$" where L was meant).

**Fix.** Done in `arxiv-html.lua` (2026-10-18), with fixtures:

- TeX character codes (`\mathchar 58\relax`, `\delimiter 67273472`, `\char 95\relax`) are decoded through Computer Modern's font tables into the character or command.
- Fonts loaded under another name (`pazocal`, `mathscrsfs`, `mdmathbb`, `widebar`, `mathbfcal`, `sumop`) become the usual ones.
- Size and box wrappers (`cramped`, `vbox`, `makebox`, `mathmakebox`, `mspace`, `scalebox{s}[s]`, `vrule`, `pagecolor`) are dropped, keeping what they hold.
- The physics package's `quantity`, `bqty`, `pqty` and `expectationvalue` are written out.
- `\textsubscript` and `\textsuperscript` in an equation become scripts, and the old switch `\sc` is dropped.
- A command run into the next letter (`\mids` → `\mid s`, `\displaystyleh`) is split again for `mid`, `forall`, `quad` and the style switches only. A general prefix rule would split the papers' own macros (`\supp`, `\topk`).
- `true` between digit groups of any length is dropped, and the raw number rounded.
- `paperlib symptoms` counts all of these under `macro` and `true-digits`.

Left as they are:

- `0pt`: in "Three Mechanisms of Weight Decay" the paper's depth symbol `\depth` was expanded by LaTeXML as TeX's box dimension, so its value 0pt stands where L was meant ("$\frac{1}{0pt+1}$"). The HTML alone cannot recover it. The other `0pt` hits are lengths.
- Papers' own macros (`\probsymb`, `\Reg`) keep showing as their name upright, by design.

**What it gives.** Formulas that render and read cleanly; a few lost symbols back.

**Cost.** Engine: small, fixtures; reconvert 20 papers.

**Examples.** See `paperlib symptoms` for the papers. TableShift's tables (Tables 1, 3, 13–15): `true` between digit groups, from a number-formatting macro (`-34.485true838`), in 182 numbers.
