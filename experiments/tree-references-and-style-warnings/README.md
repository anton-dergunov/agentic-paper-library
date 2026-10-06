# Experiment · do section references in taxonomy trees resolve, and can style-file warnings go?

**Question.** A literature review of `llm/context` flagged "A Survey of Context Engineering for Large Language Models": its taxonomy tree (Figure 1) came out as a nested list whose nodes end in empty brackets, "Foundational Components ()", where the PDF prints the section that covers each branch. Earlier reviews had flagged two papers that open with "marginparsep has been altered. … The page layout violates the ICML style." above the title. Can the converter resolve the tree's references and drop the warnings, and does either change anything else?

**Status.** Run 6 Oct 2026 on the 58 papers of the author's library that have a `forest` tree (36) or the warnings (22), out of 1,916 cached arXiv renderings. **331 section references now show their number in 18 papers; the 156 empty brackets in 11 papers are gone; all 150 warning lines in 22 papers are gone.** No word of any paper was lost. Three catalog entries closed. Both changes shipped.

**Serves.** [`docs/conversion.md`](../../docs/conversion.md#arxiv-html).

## Method

- **Corpus.** [`papers.tsv`](papers.tsv): every arXiv-HTML paper of the library whose cached rendering contains LaTeXML's `{forest}` placeholder, or the text "has been altered" or "violates the … style". The renderings, the LaTeX sources and the markdown are not committed; titles are.
- **The tree change.** The converter already rebuilt `forest` trees from the paper's LaTeX source and deleted every `\ref` in a node, since the source has labels and the HTML has numbers. Now a label is tied to the `\section`, `\subsection` or `\subsubsection` it directly follows, and that section is found in the HTML by its level and title. Sections that share a level and a title are paired in order when the source and the HTML have equally many. A reference that resolves becomes a link, "([§4.1](#S4.SS1))"; one that does not is deleted with its brackets. The control spaces authors use to centre a node's lines ("\ \ \ Context \\ \ \ Processing") are collapsed.
- **The warning change.** A paragraph is dropped when all of its text is the warning lines of the ICML and UAI style files.
- **Apparatus.** The 58 papers were reconverted in the library with `paperlib reconvert`, and [`compare.py`](compare.py) diffed each against the library's last commit: lines removed and added, warning lines removed, tree lines changed, section links added, empty brackets before and after, and changed lines that are neither a tree line nor a warning.

  ```bash
  paperlib reconvert $(cut -f2 papers.tsv)          # in the library, from a clean tree
  python3 compare.py <library> papers.tsv > compare.tsv
  ```

## Results

Per paper in [`compare.tsv`](compare.tsv).

| | Papers | Changed | What changed |
|---|---|---|---|
| `forest` trees | 36 | 26 | 331 section links added in 18 papers; 156 empty brackets in 11 papers, none left; padding removed from 98 tree lines in 8 papers |
| Style warnings | 22 | 22 | 150 warning lines removed, with the 88 blank lines between them; nothing else |

- **Of the 498 references in the trees' sources, 347 resolve** (331 in the library: one of the 36 papers is hand-edited and was skipped). 146 of the 151 that do not are in one paper, "The Prompt Report", whose tree points at `\paragraph` and unnumbered headings: there is no number to show. The other five are labels that follow no section, or name none.
- **The first version resolved 284.** Reading the misses found four causes, each fixed and in the fixtures: IEEE-style numbers ("III-A", in a nested span), an `&` in a title, a title wrapped in `\textcolor`, and a `\vspace` between a title and its label. Same-titled sections ("Reward Modeling" as 2.2 and A.2) were the fifth, fixed by pairing in order.
- **No word was lost.** Over the 36 tree papers the only words removed are 19 of "Sec", written before a reference and now "§". The words added are section numbers.
- **A side effect, kept.** A node whose source has a blank line was a list item of two paragraphs; it is now one line (4 papers). A node is one box in the figure, so one line is the truer reading. In a fifth paper four nodes that were already debris (`\$\\`) lost a trailing backslash. These are the 27 changed lines that are not tree items.
- **Ten tree papers did not change**: one is hand-edited and was skipped, and the trees of the others gave the new code nothing to do.

## What the numbers do not say

The links were not checked against the PDFs' trees. The diffs of six papers were read, and in the Context Engineering survey each link's number is that of the heading with the node's title. A link is as right as the title match: a paper whose HTML and source disagree on a section's title gets no link, not a wrong one, but two sections of one level whose titles were swapped between source versions would be paired wrongly, and nothing here tests that. References to figures and tables inside a tree are still deleted.

## Findings

- A `forest` tree's section references resolve by title for every numbered section the trees of this library point at, bar five.
- The style warnings are a closed set of five sentences, and dropping whole paragraphs made only of them removed nothing else in 22 papers.
- Not fixed, recorded in [`docs/tasks/conversion-follow-ups.md`](../../docs/tasks/conversion-follow-ups.md): the review's other paper, AdaGReS, sets its algorithm as a one-column table indented with `\hspace`, which LaTeXML drops. Two of 1,916 renderings set an algorithm this way and the other keeps its indentation, so that paper was repaired by hand.
