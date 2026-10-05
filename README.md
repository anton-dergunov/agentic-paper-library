# Agentic paper library

A way to read and organise research papers with a coding agent at the centre. Papers from arXiv, PDFs and web articles are converted to Markdown with equations as LaTeX, tables as tables, local figures and page-numbered headings. The agent can then read across the whole library and cite a claim by section and page. Claude Code skills add a paper and file it in your topic tree, write a short overview before you read it, keep notes on each paper, find the gaps in an area, and write a literature review of it.

This repository is the engine. Your library is a separate folder, usually its own private git repository, and you can keep several of them: a personal one, one per employer, one per project. The original PDFs stay outside git, for example in a synced folder you read on a tablet.

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

## Skills

| Skill | What it does |
|---|---|
| `/add-paper` | Looks up a paper (arXiv id or URL, title, web page or PDF), picks its topic folder, adds it, writes a one-line summary, rebuilds the indexes. `/add-paper inbox` drains `INBOX.txt`. |
| `/overview` | A 3–5 minute pre-read for a paper you're about to read: the intuition, the mechanism, what is new against your library. Written to your notes folder (an Obsidian vault works well). |
| `/expand-library` | Finds the papers missing from an area, has you strike what you don't want, and adds the rest in bulk. |
| `/literature-review` | Writes or updates the review of an area: the kinds of approaches, what the papers find, how they relate, where the evidence is weak. |
| `/reorganize` | Proposes moves, splits and merges of topic folders as the library grows, and carries out the ones you approve. |

### Which model

Each skill sets its model for the turn it runs in, so a session on another model switches by itself. To change one, edit the `model:` line of its `SKILL.md`.

| Use | Model | What that rests on |
|---|---|---|
| `/add-paper`, `paperlib add` | Sonnet | Measured: in one request Sonnet files and summarises a paper about as well as Opus ([experiment](experiments/skill-models/README.md)). |
| `/expand-library` | Sonnet | Not measured. The session mostly runs scripts, and the reading lists and summaries were written by Sonnet subagents when the skill was built. |
| `/literature-review` | Opus | Reading is measured: Opus's notes had 1 error in six papers, Sonnet's 6 ([experiment](experiments/reading-models/README.md)). Writing the review is not measured. |
| `/overview`, `/reorganize` | Opus | Not measured. Both are short, run rarely, and you read or approve the result. |
| Questions about papers | Opus | Not measured for other models; [planned](docs/tasks/review-usefulness-follow-up.md). |

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

## Documentation

- [Conversion](docs/conversion.md): how each kind of paper is converted, and why.
- [Design](docs/design.md): the reading workflow, where things live, and the tools considered.
- [Working in VS Code](docs/vscode.md): one window on the library, PDFs beside the markdown, papers opened by title, page links from the chat.
- [Experiments](experiments/README.md): the measurements behind the converters.
- [Configuration](docs/configuration.md): `paper-library.yaml`.
- The agent guide: [guide/library-guide.md](guide/library-guide.md), rendered into each library as `.claude/library-guide.md`.

## Next

- Conversion follow-ups: incomplete arXiv renderings, pictures inside equations, tables that are images ([list](docs/tasks/conversion-follow-ups.md)).
- Running a library from Claude Code on the web, which needs the engine installed by a setup step.
- `read` and `wrap` skills for reading a paper with the agent and keeping what you took from it.

## License

MIT. See [LICENSE](LICENSE). The example papers are © their authors and are included under CC BY 4.0, as noted in [examples/library](examples/library/README.md).
