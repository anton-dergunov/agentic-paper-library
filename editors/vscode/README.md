# Paper Library for VS Code

Open a paper of an [agentic paper library](../../README.md) by its title, in a VS Code window on the library (a folder with `paper-library.yaml`). The PDFs open in [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer), which is installed separately.

- **Paper Library: Open Paper** (⌥⌘P). Each paper is listed once, by title, with its topic, year and summary. Type words from the title or the topic. Enter opens the PDF. The buttons on a paper open its markdown or notes, or reveal it in the Explorer. Papers opened recently are listed first.
- **Paper Library: Reveal in Library**. From a paper's PDF, markdown or notes, open its other files or its topic index. The first choice opens the counterpart, so the command followed by Enter switches between the PDF and the markdown. It is also on the Explorer's context menu.
- **Paper Library: Search Library Text**. The search view, limited to the papers' markdown (indexes aside) and filled with the selected text.

The commands appear only in a library window. The list of papers is read from the papers' frontmatter on first use and read again after any paper changes.

## Install

From the engine, with Node.js and VS Code's `code` command on the PATH:

```bash
paperlib install-vscode
```

This builds `paper-library.vsix` and installs it. Run it again after updating the engine.

## Develop

```bash
npm install
npm run check   # type check
npm test        # unit tests, against examples/library
npm run package # build paper-library.vsix
```
