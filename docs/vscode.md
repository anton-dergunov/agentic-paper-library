# Working in VS Code

The desk setup: one VS Code window on the library, with the Claude Code panel beside the PDF you are reading.

## One window, both trees

Open the library folder itself, for example `code ~/papers`, rather than a multi-root workspace. `paperlib init` makes this work:

- **`pdf/`** is a symlink to `pdf_root`, and git ignores it. The explorer shows the PDFs next to the markdown: `library/` for the agent's copy, `pdf/` for the original, at the same topic path.
- **`.claude/skills/`** links the engine's skills, so the Claude Code panel in this window has `/add-paper`, `/overview` and the rest.
- **`.vscode/settings.json`**:
  - sets the PDF viewer's root to `pdf_root`, so that page links resolve;
  - keeps `images/` and the skill links out of quick open and search, and stops VS Code from applying `.gitignore` there, which would otherwise hide the PDFs (git ignores `*.pdf` and the `pdf/` link).

## Finding a paper

- **From the indexes.** Open `library/README.md` in the markdown preview (⇧⌘V) and follow the tree. Each paper row links the markdown (the title) and the PDF (**PDF**). A click on **PDF** opens it in the viewer.
- **By name.** ⌘P with words from the title. The markdown, the PDF and the paper's notes file match; the figures don't.
- **By content.** Ask the agent ("what do my papers say about X") or use ⇧⌘F, which searches the markdown, PDFs aside.

A command that opens a paper by title, without the duplicates, is planned: see [tasks/vscode-extension.md](tasks/vscode-extension.md).

## Reading with the agent

Install [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer), a separate extension. When the agent cites "p. 7, Table 2", the citation is a link: `http://pdf.invalid/<path>?dest=table.2&page=7`. A click opens the PDF at that spot in the viewer, next to the chat, and highlights you make there are saved in the PDF.

Links in the Claude Code chat need the viewer's preview-API setup, described in its README. The library guide tells the agent how to write these links, and never to open a PDF itself.

## Working on the engine

The engine is a separate repository. Its skills are symlinked into the library, so an edit to a skill applies in the next session; edits to the scripts apply on the next `paperlib` call. To change the engine with the agent, open the engine's folder in its own window, or add it to the library's window with **File → Add Folder to Workspace**.
