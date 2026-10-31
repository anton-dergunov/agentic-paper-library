<p align="center">
  <img src="docs/images/logo.jpg" alt="A friendly three-eyed monster reading a long scroll of a research paper between two stacks of papers" width="420">
</p>

<h1 align="center">Agentic paper library</h1>

A way to read and organise research papers with a coding agent at the centre. Each paper is kept as its PDF and the PDF's text, with a line marking each page, so the agent can grep and read across the whole library, open a page of the PDF for what the text lacks, and cite a claim by its page. Claude Code skills add a paper and file it in your topic tree, write a short overview before you read it, keep notes on each paper, find the gaps in an area, and write a literature review of it.

This repository is the engine. Your library is a separate folder, usually its own private git repository, and you can keep several of them: a personal one, one per employer, one per project. The original PDFs stay outside git, for example in a synced folder you read on a tablet.

![Read a paper with Claude Code beside it. A VS Code window on a library: the explorer shows papers in folders by topic, under library/ as text and under pdfs/ as PDF; the middle pane shows page 9 of the DPO paper with Table 1 highlighted; in the Claude Code panel the question "Does DPO still beat PPO on text unlike what it was trained on?" is answered with the table's win rates and the link "DPO, p. 9, Table 1". Below the window: the same page as the text Claude Code reads, a line [page 9], the heading 6.3 Generalization to a new input distribution, and the text with Table 1 beside it in its own column; and the skills /paper-info, /add-paper, /overview, /literature-review, /expand-library and /reorganize. Design choices were measured in 10 experiments, kept in the repository under experiments/ with their scripts and results.](assets/pictures/reading.png)

## Why it exists

I wanted an agent next to the PDF I am reading, not a chat box inside a PDF app. It should read the paper I'm on and every other paper I keep, use my notes, and run my own workflows. Every "AI PDF reader" I tried (PaperNook, Open Paper, pdfpal, NotebookLM) keeps the chat inside its app and its own storage. Claude Code already does the rest, so I built the missing piece:

- a library the agent can read well;
- conventions it follows;
- skills for the work around reading.

It began on 29 September 2026 with 240 papers from a project on LLM memory. Within a week it held 2,200 papers across machine learning. The design notes are in [docs/design.md](docs/design.md).

## What the agent gets

- **The paper as it is, and its text.** Each paper is its PDF and the PDF's text layer, with a line `[page N]` where each page starts. The agent greps and reads the text, and opens a page of the PDF for what the text lacks: a value drawn in a plot, a passage the text garbles. Measured against a careful Markdown conversion, the text answered as many questions and wrote better notes, with exact pages ([experiment](experiments/reading-formats/README.md)). Web articles are kept as markdown.
- **Page numbers on every page**, so answers cite "p. 7, Table 2", and with [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer) the citation is a link that opens the PDF at that table.
- **A declared topic tree.** Every folder has a written scope in `catalog/topics.yaml`, and each folder's index is generated from the papers' frontmatter. So filing a paper means choosing from a list, and the agent can find papers without reading them all.
- **Memory that accumulates.** A per-paper notes file (digest, related papers, Q&A) and a literature review per area, which later sessions read before they open any paper.
- **Rules for agents.** A guide rendered into each library sets them: add papers only through `paperlib`, read the text and open the PDF's page when it lacks something, start from the review and check the paper, never re-propose a paper you skipped.

## Reading with the agent

Open the library in VS Code with the PDF on one side and Claude Code on the other, or read on a tablet with the session on Remote Control. Ask as you read; the answers cite the page and the table, and in VS Code the citation opens the PDF there. [Working in VS Code](docs/vscode.md) has the setup.

## Skills

| Skill | What it does |
|---|---|
| `/add-paper` | Looks up a paper (arXiv id or URL, title, web page or PDF), picks its topic folder, adds it, writes a one-line summary, rebuilds the indexes. `/add-paper inbox` drains `INBOX.txt`. |
| `/overview` | A 3–5 minute pre-read for a paper you're about to read: the intuition, the mechanism, what is new against your library. Written to your notes folder (an Obsidian vault works well). |
| `/expand-library` | Finds the papers missing from an area, has you strike what you don't want, and adds the rest in bulk. |
| `/literature-review` | Writes or updates the review of an area: the kinds of approaches, what the papers find, how they relate, where the evidence is weak. |
| `/reorganize` | Proposes moves, splits and merges of topic folders as the library grows, and carries out the ones you approve. |
| `/paper-info` | A quick look at a paper before you add it: where it was published, how often it is cited, which papers in the library mention it and which are nearest. It reports and does not recommend. |

![A quick look at a paper. In Claude Code, /paper-info 2405.14734; or in a terminal, paperlib info 2405.14734. For SimPO, which is not in the library, the report gives when it was submitted to arXiv, its venue, citations (1207 in total, 502.9 a year, 243 where the citing paper builds on it), uptake, how many library papers and notes name it, the folder it would go to, what it proposes, its evidence, and the nearest library paper, DPO, with how the two differ. It reads the abstract and public records, not the paper, and gives no verdict. Measured on 72 papers: a model's advice to add or skip did not match what the reader had decided, so the command gives none.](assets/pictures/paper-info.png)

![Add a paper. In Claude Code, /add-paper 2305.18290; or in a terminal, paperlib add 2305.18290. The topic is chosen from your topics, each a folder with a scope: here llm/post-training/preference-learning. Three things are added: the PDF for you to read, the paper's text for Claude Code to read (the PDF's text layer, with a line for each page), and a line in the topic's index with a one-sentence summary. Measured on 60 papers: a blind judge graded the chosen folder the best one for 53, and choosing it takes one request of about 4 seconds.](assets/pictures/add-paper.png)

![Overview before reading. /overview Direct Preference Optimization writes a note to your own notes folder, to read in 3 to 5 minutes before the paper. The note shown opens with a one-sentence abstract, then Setting, Motivation with the key insight, Method as three steps and Why it works, and goes on to results, evidence, novelty and concepts. It ends by handing the lead back to you: three questions to ask of the paper, and follow-ups to read and to try.](assets/pictures/overview.png)

![Literature review of a topic. /literature-review on a topic works in three steps: the topic's papers as their PDFs' text; a note for each paper, written for Claude Code as an intermediate step, read once in full and keeping the page of every number (the example is a note on the Gemma 3 Technical Report); and one review written from the notes, with the sections Kinds of methods, The map, How the field got here, Findings, Where the papers disagree and In practice. Measured on six papers: of five models compared as readers, the one used made 1 error in its notes and the cheapest made 35.](assets/pictures/literature-review.png)

![Find missing papers, reorganise topics. /expand-library on a topic proposes a numbered reading list with a reason for each paper; you strike what you don't want and the rest are added, and a struck paper is not proposed again. /reorganize on a topic proposes splits, merges and moves with reasons; here one folder is split into three subfolders, and each paper moves with its PDF and its text. Both propose first and change nothing until you choose.](assets/pictures/grow.png)

### Which model

Each skill sets its model for the turn it runs in, so a session on another model switches by itself. To change one, edit the `model:` line of its `SKILL.md`.

| Use | Model | What that rests on |
|---|---|---|
| `/add-paper`, `paperlib add` | Sonnet | Measured: in one request Sonnet files and summarises a paper about as well as Opus ([experiment](experiments/skill-models/README.md)). |
| `/expand-library` | Sonnet | Not measured. The session mostly runs scripts, and the reading lists and summaries were written by Sonnet subagents when the skill was built. |
| `/literature-review` | Opus | Reading is measured: Opus's notes had 1 error in six papers, Sonnet's 6 ([experiment](experiments/reading-models/README.md)). Writing the review is not measured. |
| `/overview`, `/reorganize` | Opus | Not measured. They are short or run rarely, and you read or approve the result. |
| Questions about papers | Opus | Measured: Sonnet matches Opus on a detail of one paper, and makes about half the points on a synthesis of an area, at a third of the tokens ([experiment](experiments/review-usefulness/README.md)). |

## Quick start

You need [uv](https://docs.astral.sh/uv/), poppler (`brew install poppler`, for `pdftotext`) and, for web articles, Google Chrome and Node.js.

```bash
git clone https://github.com/anton-dergunov/agentic-paper-library ~/projects/agentic-paper-library
ln -s ~/projects/agentic-paper-library/bin/paperlib ~/.local/bin/paperlib

paperlib init ~/papers --pdf-root ~/Dropbox/Papers   # a new library: config, folders, skills, VS Code settings
cd ~/papers
paperlib install-vscode                              # optional: the VS Code extension that opens papers by title
```

Declare a topic or two in `catalog/topics.yaml`, then add a paper, from the shell or by asking Claude Code (`/add-paper 2305.18290`):

```bash
paperlib add 2305.18290                              # a model picks the folder and the type, and writes the summary
paperlib embed                                       # once: embeds the papers for paperlib meaning and similar
```

The [user guide](docs/user-guide.md) takes it from there, task by task: the layout of a library, VS Code, looking at a paper before adding it, adding and removing papers, reading with the agent, literature reviews, and checking the library's health.

`paperlib init` links the skills into the library's `.claude/skills/`, so Claude Code opened there has them. To use the skills from other folders, install them as a plugin instead: `/plugin marketplace add anton-dergunov/agentic-paper-library`. They still need `paperlib` on your PATH.

[examples/library](examples/library/) is a small library made this way: three openly licensed papers, DPO and Larimar from arXiv as their text layers, and Distill's "Why Momentum Really Works" as a web article.

## How it was designed

Every change to how papers are kept, a prompt or a skill is measured on real papers before it is kept, and some were dropped: the library converted every paper to Markdown until an experiment showed the PDF's text did as well. The write-ups, with their results and limits, are in [experiments/](experiments/README.md).

![Design choices were measured. Six of the 10 experiments, each as question, measurement and decision. What should the agent read, Markdown, the PDF or its text: on 51 questions about single papers the PDF answered 51, its text layer 43 and the converted Markdown 43, the eight lost being values drawn in plots, and across papers the text layers answered as well as the library at $0.30 a question against $0.42, so the PDF's text layer with the PDF beside it. Does the agent open the page when the text lacks a value: with the PDF beside its text it opened the page for 9 of 9 values drawn in figures and 0 of 6 questions the text answers, unprompted, so rely on it and check it on each Claude Code release. Which converter for web articles: Defuddle kept 94–99% of the text, every equation as TeX and the footnotes, Readability printed each formula twice and Trafilatura dropped every heading, so Defuddle on the page as Chrome renders it. Which model files a paper: a blind judge graded the folder best for 57 of 60 papers with Opus, 53 with Sonnet and 49 with Haiku, so Sonnet in one request. Which model reads a paper into its note: errors in the notes numbered 1 for Opus, 6 for Sonnet, 7 for Gemini Pro, 9 for Gemini Flash and 35 for Haiku, so Opus reads. Answer from the review or from the papers: starting from the review and then checking the paper made 4.7 wrong statements over three questions with 22% fewer tokens, against 6.3 without reviews and 3.3 without reviews or notes, so start from the review and check the paper before stating a number. Each row names its folder under experiments/.](assets/pictures/experiments.png)

## Documentation

- [User guide](docs/user-guide.md): installing, creating a library, and every task from adding a paper to writing a literature review.
- [A paper's text](docs/text-layer.md): how a paper's text is made from its PDF, web articles, and why.
- [Design](docs/design.md): the reading workflow, where things live, and the tools considered.
- [Working in VS Code](docs/vscode.md): one window on the library, PDFs beside their text, papers opened by title, page links from the chat.
- [Experiments](experiments/README.md): the measurements behind the design.
- [Configuration](docs/configuration.md): `paper-library.yaml`.
- The agent guide: [guide/library-guide.md](guide/library-guide.md), rendered into each library as `.claude/library-guide.md`.
- [assets/pictures/](assets/pictures/): the HTML sources of the pictures on this page, and `render.sh` to redraw them.

## Next

- Running a library from Claude Code on the web, which needs the engine installed by a setup step.
- `read` and `wrap` skills for reading a paper with the agent and keeping what you took from it.

## License

MIT. See [LICENSE](LICENSE). The example papers are © their authors and their text is included under CC BY 4.0, as noted in [examples/library](examples/library/README.md).
