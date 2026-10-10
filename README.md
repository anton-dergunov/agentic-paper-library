<p align="center">
  <img src="docs/images/logo.jpg" alt="A friendly three-eyed monster reading a long scroll of a research paper between two stacks of papers" width="420">
</p>

<h1 align="center">Agentic paper library</h1>

A way to read and organise research papers with a coding agent at the centre. Papers from arXiv, PDFs and web articles are converted to Markdown with equations as LaTeX, tables as tables, local figures and page-numbered headings. The agent can then read across the whole library and cite a claim by section and page. Claude Code skills add a paper and file it in your topic tree, write a short overview before you read it, keep notes on each paper, find the gaps in an area, and write a literature review of it.

This repository is the engine. Your library is a separate folder, usually its own private git repository, and you can keep several of them: a personal one, one per employer, one per project. The original PDFs stay outside git, for example in a synced folder you read on a tablet.

![Read a paper with Claude Code beside it. A VS Code window on a library: the explorer shows papers in folders by topic, under library/ as Markdown and under pdfs/ as PDF; the middle pane shows page 9 of the DPO paper with Table 1 highlighted; in the Claude Code panel the question "Does DPO still beat PPO on text unlike what it was trained on?" is answered with the table's win rates and the link "DPO, p. 9, Table 1". Below the window: the same section as the Markdown Claude Code reads, with the heading "6.3 Generalization to a new input distribution (p. 9)", and the skills /paper-info, /add-paper, /overview, /literature-review, /expand-library and /reorganize. Design choices were measured in 22 experiments, kept in the repository under experiments/ with their scripts and results.](assets/pictures/reading.png)

## Why it exists

I wanted an agent next to the PDF I am reading, not a chat box inside a PDF app. It should read the paper I'm on and every other paper I keep, use my notes, and run my own workflows. Every "AI PDF reader" I tried (PaperNook, Open Paper, pdfpal, NotebookLM, Zotero with llm-for-zotero) keeps the chat inside its app and its own storage. Claude Code already does the rest, so I built the missing piece:

- a library the agent can read well;
- conventions it follows;
- skills for the work around reading.

It began on 29 September 2026 with 240 papers from a project on LLM memory. Within a week it held 2,200 papers across machine learning. The design notes are in [docs/design.md](docs/design.md).

## What the agent gets

- **Markdown it can actually read.** arXiv's HTML rendering (LaTeXML) is converted with pandoc, so equations stay the author's TeX and merged-cell tables stay tables. Papers without an HTML rendering go through docling's layout analysis, with each equation read from the page image by marker's model. Web articles are rendered in headless Chrome. Every choice here was measured; see [Conversion](docs/conversion.md) and [experiments/](experiments/README.md).
- **Page numbers on every heading**, as in `### 4.3 LongMemEval (p. 6)`. Answers can cite "p. 7, Table 2", and with [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer) the citation is a link that opens the PDF at that table.
- **A declared topic tree.** Every folder has a written scope in `catalog/topics.yaml`, and each folder's index is generated from the papers' frontmatter. So filing a paper means choosing from a list, and the agent can find papers without reading them all.
- **Memory that accumulates.** A per-paper notes file (digest, related papers, Q&A) and a literature review per area, which later sessions read before they open any paper.
- **Rules for agents.** A guide rendered into each library sets them: add papers only through `paperlib`, read the markdown rather than the PDF, flag broken conversions, never re-propose a paper you skipped.

![Each paper is converted to Markdown for the agent. An equation and a table of the DPO paper, each shown three ways. On the PDF page they are typeset. In the text taken from the PDF the equation has lost its fractions and brackets and the table is mixed into the paragraph beside it. In the library's Markdown the equation is LaTeX with its number, the table is a table, and the heading carries the PDF page so an answer can link to it. The Markdown is made from arXiv's HTML where a paper has one, otherwise from the PDF with a layout model and an equation model. Measured: 99.99% of 489,000 equations in 2,200 papers parse as LaTeX.](assets/pictures/markdown.png)

## Reading with the agent

Open the library in VS Code with the PDF on one side and Claude Code on the other, or read on a tablet with the session on Remote Control. Ask as you read; the answers cite the page and the table, and in VS Code the citation opens the PDF there. [Working in VS Code](docs/vscode.md) has the setup.

## Skills

| Skill | What it does |
|---|---|
| `/add-paper` | Looks up a paper (arXiv id or URL, title, web page or PDF), picks its topic folder, adds it, writes a one-line summary, rebuilds the indexes. `/add-paper inbox` drains `INBOX.txt`. |
| `/overview` | A 3–5 minute pre-read for a paper you're about to read: the intuition, the mechanism, what is new against your library. Written to your notes folder (an Obsidian vault works well). |
| `/expand-library` | Finds the papers missing from an area, has you strike what you don't want, and adds the rest in bulk. |
| `/literature-review` | Writes or updates the review of an area: the kinds of approaches, what the papers find, how they relate, where the evidence is weak. |
| `/fix-conversions` | Works through the conversion problems the notes report: fixes recurring ones in the converter, reconverts or fixes papers by hand from the PDF, reads again the papers whose key content was broken, and marks what can't be fixed. Run it between reading an area and writing its review. |
| `/reorganize` | Proposes moves, splits and merges of topic folders as the library grows, and carries out the ones you approve. |
| `/paper-info` | A quick look at a paper before you add it: where it was published, how often it is cited, which papers in the library mention it and which are nearest. It reports and does not recommend. |

![A quick look at a paper. In Claude Code, /paper-info 2405.14734; or in a terminal, paperlib info 2405.14734. For SimPO, which is not in the library, the report gives when it was submitted to arXiv, its venue, citations (1207 in total, 502.9 a year, 243 where the citing paper builds on it), uptake, how many library papers and notes name it, the folder it would go to, what it proposes, its evidence, and the nearest library paper, DPO, with how the two differ. It reads the abstract and public records, not the paper, and gives no verdict. Measured on 72 papers: a model's advice to add or skip did not match what the reader had decided, so the command gives none.](assets/pictures/paper-info.png)

![Add a paper. In Claude Code, /add-paper 2305.18290; or in a terminal, paperlib add 2305.18290. The topic is chosen from your topics, each a folder with a scope: here llm/post-training/preference-learning. Three things are added: the PDF for you to read, the paper as Markdown for Claude Code to read, and a line in the topic's index with a one-sentence summary. Measured on 60 papers: a blind judge graded the chosen folder the best one for 53, and choosing it takes one request of about 4 seconds.](assets/pictures/add-paper.png)

![Overview before reading. /overview Direct Preference Optimization writes a note to your own notes folder, to read in 3 to 5 minutes before the paper. The note shown opens with a one-sentence abstract, then Setting, Motivation with the key insight, Method as three steps and Why it works, and goes on to results, evidence, novelty and concepts. It ends by handing the lead back to you: three questions to ask of the paper, and follow-ups to read and to try.](assets/pictures/overview.png)

![Literature review of a topic. /literature-review on a topic works in three steps: the topic's papers as Markdown; a note for each paper, written for Claude Code as an intermediate step, read once in full and keeping the page of every number (the example is a note on the Gemma 3 Technical Report); and one review written from the notes, with the sections Kinds of methods, The map, How the field got here, Findings, Where the papers disagree and In practice. Measured on six papers: of five models compared as readers, the one used made 1 error in its notes and the cheapest made 35.](assets/pictures/literature-review.png)

![Find missing papers, reorganise topics. /expand-library on a topic proposes a numbered reading list with a reason for each paper; you strike what you don't want and the rest are added, and a struck paper is not proposed again. /reorganize on a topic proposes splits, merges and moves with reasons; here one folder is split into three subfolders, and each paper moves with its PDF, Markdown and figures. Both propose first and change nothing until you choose.](assets/pictures/grow.png)

![Conversion errors are reported and fixed, in three steps. Reported while reading: each note says what the conversion broke and on which page. Fixed where it starts: /fix-conversions fixes a problem seen in several papers in the converter, with a test, and a single one from the PDF. Converted again: every paper with the same problem is corrected at once. A note records the conversion in one of three ways: ok; a flaw with its page; or key-content-broken, when the paper's findings rest on the broken part, and only those papers are read again after the fix. An example: authors pad a number with an invisible digit so that a column lines up, so a table cell that reads 3.4 in the PDF was 53.4 in the Markdown and is 3.4 now; one fix removed the digit from 29 papers. Measured: after the 22 problems reported during one literature review were fixed, papers showing a known symptom fell from 761 to 379.](assets/pictures/fix-conversions.png)

### Which model

Each skill sets its model for the turn it runs in, so a session on another model switches by itself. To change one, edit the `model:` line of its `SKILL.md`.

| Use | Model | What that rests on |
|---|---|---|
| `/add-paper`, `paperlib add` | Sonnet | Measured: in one request Sonnet files and summarises a paper about as well as Opus ([experiment](experiments/skill-models/README.md)). |
| `/expand-library` | Sonnet | Not measured. The session mostly runs scripts, and the reading lists and summaries were written by Sonnet subagents when the skill was built. |
| `/literature-review` | Opus | Reading is measured: Opus's notes had 1 error in six papers, Sonnet's 6 ([experiment](experiments/reading-models/README.md)). Writing the review is not measured. |
| `/overview`, `/reorganize`, `/fix-conversions` | Opus | Not measured. They are short or run rarely, and you read or approve the result. |
| Questions about papers | Opus | Measured: Sonnet matches Opus on a detail of one paper, and makes about half the points on a synthesis of an area, at a third of the tokens ([experiment](experiments/review-usefulness/README.md)). |

## Quick start

You need [uv](https://docs.astral.sh/uv/), pandoc, librsvg (`rsvg-convert`) and, for web articles, Google Chrome.

```bash
git clone https://github.com/anton-dergunov/agentic-paper-library ~/projects/agentic-paper-library
ln -s ~/projects/agentic-paper-library/bin/paperlib ~/.local/bin/paperlib

paperlib init ~/papers --pdf-root ~/Dropbox/Papers   # a new library: config, folders, skills, VS Code settings
cd ~/papers
paperlib setup-equations                             # optional: marker's equation model for PDF-only papers
paperlib install-vscode                              # optional: the VS Code extension that opens papers by title
```

Declare a topic or two in `catalog/topics.yaml`, then add papers, from the shell or by asking Claude Code (`/add-paper 2305.18290`):

```bash
paperlib add 2305.18290                              # a model picks the folder and writes the summary
paperlib add-arxiv 2305.18290 llm/post-training      # or name the folder yourself
paperlib add-pdf ~/Downloads/paper.pdf ml/classics --title "..."
paperlib add-web https://distill.pub/2017/momentum/ deep-learning/optimization
paperlib build-index && paperlib check
```

`paperlib init` links the skills into the library's `.claude/skills/`, so Claude Code opened there has them. To use the skills from other folders, install them as a plugin instead: `/plugin marketplace add anton-dergunov/agentic-paper-library`. They still need `paperlib` on your PATH.

[examples/library](examples/library/) is a small library made this way: three openly licensed papers, one through each converter (DPO from arXiv HTML, Larimar from its PDF, Distill's "Why Momentum Really Works" from the web).

## How it was designed

Every change to a converter, a prompt or a skill is measured on real papers before it is kept, and some were dropped. The write-ups, with their results and limits, are in [experiments/](experiments/README.md).

![Design choices were measured. Six of the 22 experiments, each as question, measurement and decision. Convert from arXiv's HTML or from the PDF: the HTML kept 35 of 35 equations as exact LaTeX and a layout-aware PDF tool kept 1, so HTML first. Which converter for papers that are only a PDF: of four compared on six papers, docling with surya put 100% of table numbers in tables and read 71% of equations closely, against 83% and 68% for marker alone, so docling for layout and tables and surya to read each equation. Keep bold and underline: kept, at 0.6% more text. Keep the shading of table cells: 11 of 15 questions answered correctly without it and 15 of 15 with it, three of the four gains being stated in the paper's text anyway, so it is kept only where the caption refers to it. Which model reads a paper into its note: five models were tested as the reader on the same six papers, and the errors found when their notes were checked against the papers numbered 1 for Opus, 6 for Sonnet, 7 for Gemini Pro, 9 for Gemini Flash and 35 for Haiku, so Opus reads. Answer from the review or from the papers: sessions that start from the review and then check the paper made 4.7 wrong statements over three questions with 22% fewer tokens, against 6.3 without reviews and 3.3 without reviews or notes, and answers no more complete, so start from the review and check the paper before stating a number. Each row names its folder under experiments/.](assets/pictures/experiments.png)

## Documentation

- [Conversion](docs/conversion.md): how each kind of paper is converted, and why.
- [Design](docs/design.md): the reading workflow, where things live, and the tools considered.
- [Working in VS Code](docs/vscode.md): one window on the library, PDFs beside the markdown, papers opened by title, page links from the chat.
- [Experiments](experiments/README.md): the measurements behind the converters.
- [Configuration](docs/configuration.md): `paper-library.yaml`.
- The agent guide: [guide/library-guide.md](guide/library-guide.md), rendered into each library as `.claude/library-guide.md`.
- [assets/pictures/](assets/pictures/): the HTML sources of the pictures on this page, and `render.sh` to redraw them.

## Next

- Conversion follow-ups: incomplete arXiv renderings, equations a model misread in a PDF, tables that are images ([list](docs/tasks/conversion-follow-ups.md)).
- Running a library from Claude Code on the web, which needs the engine installed by a setup step.
- `read` and `wrap` skills for reading a paper with the agent and keeping what you took from it.

## License

MIT. See [LICENSE](LICENSE). The example papers are © their authors and are included under CC BY 4.0, as noted in [examples/library](examples/library/README.md).
