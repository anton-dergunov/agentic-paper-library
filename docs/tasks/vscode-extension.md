# Task: a "Paper library" VS Code extension

**Status.** Planned 2026-10-03, not started. Written so that a later session can pick it up.

## Why

In VS Code, a library is browsed through its generated indexes and the explorer. That works, but the two quick ways to reach a paper are noisy:

- **⌘P by name** lists every paper twice, once as markdown and once as PDF, because the two trees share a filename stem.
- **⇧⌘F** searches files, not papers, and knows nothing of titles, summaries or topics.

The reader usually wants the PDF. The markdown is the agent's copy and is opened mostly to check a conversion.

## What

A small extension in `editors/vscode/` of this repository, active in any folder that has a `paper-library.yaml`:

- **Paper library: Open paper.** A quick pick over every paper, with the title as the label, the topic path as the description and the summary as the detail. Read the frontmatter of `library/**/*.md`, or parse the generated indexes, which hold the same fields and are faster to read. Enter opens the PDF in [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer) (`vscode.open` on the PDF under `pdf_root`, which that viewer's custom editor claims). A second button on each item opens the markdown.
- **Paper library: Search library text.** Search within the markdown only, with the results grouped by paper title. It can start as a pre-filled search (`workbench.action.findInFiles` with `filesToInclude: library/**/*.md`) before anything custom.
- **Paper library: Reveal in library.** From an open PDF or markdown file, reveal its counterpart in the other tree, or its folder's index.

Keep the extension library-specific and keep vscode-pdf-viewer generic. The viewer is useful outside libraries and stays a separate project. This extension only finds papers and hands their PDFs to it.

## Later, each measured first in `experiments/`

- **Fuzzy and semantic search.** Embedding search over titles, summaries, notes and reviews, compared with BM25 on real questions before it is adopted.
- **An MCP server**, so that agents outside Claude Code can search the library, look up a paper and read notes.
- **Graph-based navigation** from the "Related in library" links in notes and the paper maps in reviews.
