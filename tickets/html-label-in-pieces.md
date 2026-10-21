---
id: html-label-in-pieces
title: "A row label typed in pieces on the data rows it covers"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium, with the LaTeX source; reconvert the papers"
---

# A row label typed in pieces on the data rows it covers

`engine` `reconvert` · html · open

**Broken.** An author spreads a group's label over the rows of the group, a word or a line per row ("self-" / "Model" / "improvement", "Faster-RCNN" / "300"), and those rows hold values, so `merge_continuation_rows` (done 21 Oct 2026) leaves them: it joins only rows of text fragments. The label reads in pieces down the column, the words in the PDF's vertical order rather than the rows', and the group's boundaries are unclear. Gemini 2.5 Table 10 gives "Learning R&D [robot] Machine"; CapSpeech splits "Glass | breaking" over two cells and merges "Stutter Whispering" into one, and prints "Hand saw" twice in Table IV.

**Fix.** Where a ruled group's first column holds only words that read as one label once joined, join them on the group's first row and span the group, as `span_group_labels` does for a single word. The LaTeX source settles the order where a `\multirow` holds part of the label.

**What it gives.** One label per group, the rows under it read as one setting.

**Cost.** Engine: medium, with the LaTeX source; reconvert the papers.

**Examples.** "A Survey on Data Synthesis and Augmentation for Large Language Models" Tables 2–3 (pp. 8–9); MobileNets Table 13; Gemini 2.5 Table 10; CapSpeech Tables IV–V (pp. 4, 6).
