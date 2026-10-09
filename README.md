<p align="center">
  <img src="docs/images/logo.jpg" alt="A friendly three-eyed monster reading a long scroll of a research paper between two stacks of papers" width="420">
</p>

<h1 align="center">Agentic paper library</h1>

A way to read and organise research papers with a coding agent at the centre. Papers from arXiv, PDFs and web articles are converted to Markdown with equations as LaTeX, tables as tables, local figures and page-numbered headings. The agent can then read across the whole library and cite a claim by section and page. Claude Code skills add a paper and file it in your topic tree, write a short overview before you read it, keep notes on each paper, find the gaps in an area, and write a literature review of it.

This repository is the engine. Your library is a separate folder, usually its own private git repository, and you can keep several of them: a personal one, one per employer, one per project. The original PDFs stay outside git, for example in a synced folder you read on a tablet.

![One paper's way through the library. First, look and add: the /paper-info and /add-paper skills, or paperlib info and paperlib add with an arXiv id, put the DPO paper's markdown and index under library/ and its PDF under pdf/, at the same topic path. Second, the agent's copy: equation 7 as the authors' LaTeX, the heading of section 6.3 with its page, p. 9, and Table 1 with its merged header. Third, reading with the agent: asked whether DPO still beats PPO on text unlike what it was trained on, the agent answers with the win rates 0.36 and 0.26 and a link, p. 9, Table 1. Around the reading, five more skills: /overview, /literature-review, /fix-conversions, /expand-library and /reorganize. Along the bottom: 2,200 papers in the library it was built on; 66 of 488,925 equations fail to parse; 99.1% of numbered headings carry their page; 22 experiments behind the decisions.](assets/pictures/overview.png)

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

![Equation 7 and Table 1 of the DPO paper in three conversions. From the PDF's text layer the equation is a fraction spread over three lines and the table is woven into the paragraph beside it. From pymupdf4llm the equation is gone, with no placeholder and no warning, and the table's two-column header is split. From arXiv's HTML the equation is the authors' LaTeX, the table keeps its merged header, and the heading carries its page. Along the bottom: 35 of 35 display equations kept as exact LaTeX; formulas failing to parse fell from 830 to 6 of 35,000, and are 66 of 488,925 now; 40 random papers are 13.1% shorter without text a model cannot use; papers showing a conversion symptom fell from 1,370 to 362.](assets/pictures/conversion.png)

![Papers with no HTML rendering. What shipped: docling reads the layout and takes words and numbers from the PDF's text layer, a model reads each equation from the page image, and paragraphs with inline maths are read again under a guard. A table of four converters scored on six papers against arXiv's HTML: the text layer puts 0% of table numbers in a table and reads no equations; docling 100% and none; marker 83% and 68%; docling with surya 100% and 71%, in 28 to 148 seconds a paper. MinerU was installed but its run failed. Inline formulas reproduced closely rose from 0, 0 and 31% to 76, 84 and 98% on three papers. Along the bottom: about 3 in 10 equations read from a page differ from arXiv's, so the paper says to check the PDF; 112 of 112 re-read paragraphs passed the guard; a crash in 5 of 15 conversions was traced to OpenCV and pinned away.](assets/pictures/pdf-only.png)

## Reading with the agent

Open the library in VS Code with the PDF on one side and Claude Code on the other, or read on a tablet with the session on Remote Control. Ask as you read; the answers cite the page and the table, and in VS Code the citation opens the PDF there. [Working in VS Code](docs/vscode.md) has the setup.

![A drawn VS Code window on a library. On the left, page 9 of the DPO paper with Table 1 highlighted. On the right, the Claude Code chat: asked whether DPO still beats PPO on text unlike what it was trained on, the agent answers that GPT-4 preferred DPO's summary at a rate of 0.36 against 0.26 for PPO, with the link "p. 9, Table 1". Beside the window: the markdown heading that carries the page, the link the agent writes, and the /overview skill for a 3 to 5 minute note before reading. Along the bottom: 99.1% of numbered headings carry a page; 608 captions in 114 papers were renumbered to match the PDF; 90 page markers corrected in 16 of 1,911 papers; Sonnet matches Opus on a detail of one paper at a third of the tokens.](assets/pictures/reading.png)

## Skills

| Skill | What it does |
|---|---|
| `/add-paper` | Looks up a paper (arXiv id or URL, title, web page or PDF), picks its topic folder, adds it, writes a one-line summary, rebuilds the indexes. `/add-paper inbox` drains `INBOX.txt`. |
| `/overview` | A 3–5 minute pre-read for a paper you're about to read: the intuition, the mechanism, what is new against your library. Written to your notes folder (an Obsidian vault works well). |
| `/expand-library` | Finds the papers missing from an area, has you strike what you don't want, and adds the rest in bulk. |
| `/literature-review` | Writes or updates the review of an area: the kinds of approaches, what the papers find, how they relate, where the evidence is weak. |
| `/fix-conversions` | Works through the conversion problems the notes report: fixes recurring ones in the converter, reconverts or fixes papers by hand from the PDF, reads again the papers whose key content was broken, and marks what can't be fixed. Run it between reading an area and writing its review. |
| `/reorganize` | Proposes moves, splits and merges of topic folders as the library grows, and carries out the ones you approve. |

![Filing a paper is one request. In: the DPO paper's title and abstract, and the topic tree with every folder's scope. Out, from /add-paper or paperlib add: the folder llm/post-training/preference-learning and a one-line summary. The same choice took 228K tokens and 55 seconds as a skill in a session, and 9K tokens and 4 seconds as one request. Of 60 papers, a blind judge graded the folder best for 57 with Opus, 53 with Sonnet, 49 with Haiku and 47 as the papers were filed; summaries were graded 4.8, 4.8, 3.5 and 3.7 of 5. Along the bottom: Haiku's summary contradicted the abstract in 8 of 60; 723 of 819 titles were resolved without an API key.](assets/pictures/filing.png)

![Every paper read tests the converter, in five steps: paperlib read writes a conversion line into each note; paperlib conversion-issues collects the problems into the catalog; /fix-conversions sends a recurring flaw to the converter with a test fixture; paperlib reconvert regenerates the library and checks it; only papers whose key content was broken are read again. One case: a \phantom{5} that pads a column arrived from arXiv's HTML as a hidden span and printed "53.4" for 3.4; it was in 1,052 table cells of 29 papers and changed the value in 256. A bar shows 435 of 2,204 papers read into notes by 9 October 2026. Along the bottom: 46 of 91 papers of one area had a reported problem; papers with a symptom fell from 761 to 379; a later change touches a median 0.08% of a read paper.](assets/pictures/feedback.png)

### Which model

Each skill sets its model for the turn it runs in, so a session on another model switches by itself. To change one, edit the `model:` line of its `SKILL.md`.

| Use | Model | What that rests on |
|---|---|---|
| `/add-paper`, `paperlib add` | Sonnet | Measured: in one request Sonnet files and summarises a paper about as well as Opus ([experiment](experiments/skill-models/README.md)). |
| `/expand-library` | Sonnet | Not measured. The session mostly runs scripts, and the reading lists and summaries were written by Sonnet subagents when the skill was built. |
| `/literature-review` | Opus | Reading is measured: Opus's notes had 1 error in six papers, Sonnet's 6 ([experiment](experiments/reading-models/README.md)). Writing the review is not measured. |
| `/overview`, `/reorganize`, `/fix-conversions` | Opus | Not measured. They are short or run rarely, and you read or approve the result. |
| Questions about papers | Opus | Measured: Sonnet matches Opus on a detail of one paper, and makes about half the points on a synthesis of an area, at a third of the tokens ([experiment](experiments/review-usefulness/README.md)). |

![Each paper is read once, in one request. Before: one reading agent wrote 483K tokens to the cache for 10 papers and re-read 12.8M, as its context grew from 35K to as much as 480K tokens. Now: /literature-review or paperlib read sends each paper in one request and resumes at the next paper when cut off. In the middle, Opus's note on the Gemma 3 Technical Report: type, evidence and its strength, what the conversion broke, and digest lines that carry their page and table. On the right, errors a judge found in six notes: Opus 1, Sonnet 6, Gemini 3.1 Pro 7, Gemini 3.8 Flash 9, Haiku 35; and numbers citing a wrong page: 0 of 528, 5 of 648, 11 of 248, 4 of 443, 14 of 330. Along the bottom: reading was 70 to 80% of a review's tokens; a paper costs about 32K tokens in and 5K out; 24% cheaper with the shared prompt cached.](assets/pictures/notes.png)

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

## What the measurements ruled out

Every change to a converter, a prompt or a skill is measured on real papers before it is kept, and some were dropped. The write-ups, with their results and limits, are in [experiments/](experiments/README.md).

![Four designs that were built or tried and then dropped or narrowed. A verdict on each new paper: it said "add" for 22 of 30 papers the reader had skipped and 28 of 42 kept, so paperlib info reports and does not recommend. Answering from the literature review first: a third of the tokens and 8 wrong statements against 3, so a review is a map, not evidence. Equations from MathML: parse failures fell from 39 to 8 because what cannot be drawn was gone, and the author's macros were lost, so the author's TeX stays the source. Keeping every table's cell shading: a model answered 11 of 15 shading-dependent questions without it and 15 with it, three of the four gains being answers the whole paper gives, so shading is kept only where the caption refers to it. Along the bottom: pymupdf4llm kept 1 of 35 equation numbers; Haiku made 35 errors in six notes; tracking of out-of-date notes was built and removed the same day; MinerU was not compared.](assets/pictures/ruled-out.png)

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
