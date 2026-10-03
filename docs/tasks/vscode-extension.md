# Task: a "Paper library" VS Code extension

**Status.** Done 2026-10-03: `editors/vscode/`, installed with `paperlib install-vscode`. How to use it: [vscode.md](../vscode.md). The follow-ups below are open.

## Why

In VS Code, a library was browsed through its generated indexes and the explorer. That works, but the two quick ways to reach a paper were noisy:

- **⌘P by name** lists every paper twice, once as markdown and once as PDF, because the two trees share a filename stem.
- **⇧⌘F** searches files, not papers, and knows nothing of titles, summaries or topics.

The reader usually wants the PDF. The markdown is the agent's copy and is opened mostly to check a conversion.

## What was built

The extension is active in any folder that has a `paper-library.yaml`. It reads the config as `paperlib.py` does, and the frontmatter of every paper on first use: about 0.4 s for 2,200 papers. Any change under `library/` makes it read them again on the next command.

- **Open Paper** (⌥⌘P): a quick pick over every paper. The label is the title, the description is the topic and year, and the detail is the summary. It matches on title and topic only, because matching summaries brings up too many papers. Papers opened recently come first. Enter opens the PDF with `vscode.open`, which [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer) claims. The PDF is opened through `pdf_link` when one is set, so it sits in the workspace. Buttons on each item open the markdown and the notes, and reveal the paper in the Explorer.
- **Reveal in Library**: from a PDF (a custom-editor tab), the markdown or the notes, a list of the paper's other files and its topic index, counterpart first. A PDF is recognised under `pdf_link`, `pdf_root`, or the real path of either.
- **Search Library Text**: a pre-filled `workbench.action.findInFiles` over `library/**/*.md` without the indexes. Results are grouped by file, and the filename is the title stem.

The extension only finds papers and hands their PDFs to the viewer. The viewer stays generic, because it is useful outside libraries.

## Later, each measured first in `experiments/`

- **Search grouped by paper title**, with a custom results view instead of the search view, if the search view proves too noisy.
- **Fuzzy and semantic search.** Embedding search over titles, summaries, notes and reviews, compared with BM25 on real questions before it is adopted.
- **An MCP server**, so that agents outside Claude Code can search the library, look up a paper and read notes.
- **Graph-based navigation** from the "Related in library" links in notes and the paper maps in reviews.
