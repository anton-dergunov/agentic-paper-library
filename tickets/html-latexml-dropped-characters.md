---
id: html-latexml-dropped-characters
title: "A character the PDF prints is missing from arXiv's HTML"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: large (align the text with the PDF's text layer); reconvert the papers it finds"
---

# A character the PDF prints is missing from arXiv's HTML

`engine` `reconvert` · html · open

**Broken.** LaTeXML loses a character the PDF prints, so the value changes with nothing to show it: siunitx output loses a range's dash ("448" for 4–48, MT3 Table 1) or moves a leading decimal point (".8 m" becomes "8.m", GAE p. 9); a ± between a mean and its error vanishes ("0.65 0.06", Deliberative Alignment Table 3); a font macro eats ℝ ("θ∈3" for θ∈ℝ³, Thompson Sampling tutorial). The converter copies arXiv's HTML faithfully; only the PDF or the source has the character. Most records that look like this are not it: of 28 checked on 23 Oct 2026, 24 were the papers' own slips, printed the same in the PDF or typed so in the author's TeX, and were deleted. Split from `html-symbols-lost` on 23 Oct 2026.

**Fix.** Not known yet. Two routes: (a) siunitx in the source (`\SI`, `\num`, `\numrange`, `\pm` inside a macro): re-expand those commands from the LaTeX source in place of LaTeXML's output, where the surrounding text locates them; (b) a check that aligns each paragraph and table cell with the PDF's text layer and reports a number or symbol that differs, as a symptom first and a fix only where the alignment is unambiguous. Route (b) also tells a paper's own slip (same in both) from a loss.

**What it gives.** Intervals, ranges and units that are right, and a way to find the losses no reader has noticed.

**Cost.** Engine: large (align the text with the PDF's text layer); reconvert the papers it finds.

**Examples.** MT3 Table 1 (p. 6); GAE §6.2 (p. 9); Deliberative Alignment Table 3 (p. 17); "A Tutorial on Thompson Sampling" Ch. 2.
