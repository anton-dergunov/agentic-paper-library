# Working in VS Code

The desk setup: one VS Code window on the library, with the Claude Code panel beside the PDF you are reading. The [user guide](user-guide.md#4-set-up-vs-code) has the short version.

## One window, both trees

Open the library folder itself, for example `code ~/papers`, rather than a multi-root workspace. `paperlib init` makes this work:

- **`pdf/`** is a symlink to `pdf_root`, and git ignores it. The explorer shows the PDFs next to the papers' text: `library/` for the agent's copy, `pdf/` for the original, at the same topic path.
- **`.claude/skills/`** links the engine's skills, so the Claude Code panel in this window has `/add-paper`, `/overview` and the rest.
- **`.vscode/settings.json`**:
  - sets the PDF viewer's root to `pdf_root`, so that page links resolve;
  - keeps the skill links out of quick open and search, and stops VS Code from applying `.gitignore` there, which would otherwise hide the PDFs (git ignores `*.pdf` and the `pdf/` link).

## Finding a paper

Install the Paper Library extension once per machine, with `paperlib install-vscode` (it needs Node.js and VS Code's `code` command). Its commands are in the palette under **Paper Library**, in a window on a library only.

- **By title: ⌥⌘P** (Ctrl+Alt+P on Windows and Linux; Paper Library: Open Paper). Each paper is listed once, with its topic, year and summary, and the ones you opened recently come first. Type words from the title or the topic. Enter opens the PDF in the viewer. The buttons on a paper open its text, its notes when it has some, or reveal it in the explorer.
- **From a paper to its other files.** Paper Library: Reveal in Library, from the PDF, the text or the notes, also on the explorer's context menu. The first choice is the counterpart, so the command followed by Enter switches between the PDF and the text. The topic's index is in the list too.
- **From the indexes.** Open `library/README.md` in the markdown preview (⇧⌘V) and follow the tree. Each paper row links the text (the title) and the PDF (**PDF**). A click on **PDF** opens it in the viewer.
- **By content.** Ask the agent ("what do my papers say about X"), or run Paper Library: Search Library Text, which opens the search view limited to the papers' text (indexes aside), filled with the selected text.

⌘P still works, but it lists each paper twice, as text and as PDF, and it matches filenames, not titles.

## Reading with the agent

Install [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer), a separate extension. When the agent cites "p. 7, Table 2", the citation is a link: `http://pdf.invalid/<path>?page=7&rect=130,306,479,397`, which `paperlib locate` writes. A click opens the PDF in the viewer, next to the chat, with the table marked; a click on the page clears the mark. Highlights you make there are saved in the PDF; the mark never is.

Links in the Claude Code chat need the viewer's preview-API setup, described in its README. The library guide tells the agent how to write these links, and never to open the viewer itself; the agent reads a PDF's page with its own tools when the text lacks a value.

## Working on the engine

The engine is a separate repository. Its skills are symlinked into the library, so an edit to a skill applies in the next session; edits to the scripts apply on the next `paperlib` call. To change the engine with the agent, open the engine's folder in its own window, or add it to the library's window with **File → Add Folder to Workspace**.
