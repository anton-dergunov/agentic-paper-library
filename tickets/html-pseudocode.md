---
id: html-pseudocode
title: "Pseudocode in arXiv-HTML papers runs together"
converter: html
takes: [engine, reconvert]
status: open
cost: "engine: medium, a fixture; reconvert the papers"
---

# Pseudocode in arXiv-HTML papers runs together

`engine` `reconvert` · html · open

**Broken.** An algorithm from arXiv's HTML is flattened into run-on text or a one-column table, or broken into fragments, with its loop and condition nesting lost. LaTeXML also numbers the Input and Output lines, so a line the prose cites ("line 8") lands two lines early (the P³ privacy paper, Rich-Item Recommendations).

**Fix.** Write LaTeXML's algorithm blocks as fenced code, one line per line, keeping the indentation and inline mathematics, and number the lines from the first statement, as the PDF does. The PDF side is `pdf-pseudocode`.

**What it gives.** Algorithms an agent can follow step by step.

**Cost.** Engine: medium, a fixture; reconvert the papers.

**Examples.** Larimar Algorithm 1; "AdaGReS…" Algorithm 1; "The Entropy Mechanism of Reinforcement Learning…" p. 12; Phi-4 Figure 4.
