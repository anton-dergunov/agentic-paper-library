# Task: PDF viewer extension with page links from the Claude chat

A small personal VS Code extension that opens a paper's PDF **inside VS Code at a given page or
section**. Two ways in:

1. **Clickable links in the Claude Code chat panel.** Claude writes
   `[p. 7, Table 2](http://paper.link/open?file=...&page=7&dest=table.2)`. Clicking it opens the PDF
   tab at that spot, not a browser tab.
2. **An agent action.** Claude runs `scripts/open-pdf <file> --page 7` via Bash, which opens the same
   tab.

It is for desktop only. Install it locally from a `.vsix`; it is not for the marketplace.

## Why it has to be built this way

These were established on 2026-09-29 by reading the source of the installed extensions:
`anthropic.claude-code` 2.1.284 and `tomoki1207.pdf` 1.2.2, both in `~/.vscode/extensions/`.
Re-check them if the Claude Code extension version has moved on.

**File-path links can't open a PDF viewer.**

- The Claude panel sends a clicked file link to `openFile()`.
- `openFile()` calls `vscode.window.showTextDocument` first. It only falls back to `vscode.open`, which
  respects custom editors, if that call throws.
- For a PDF, the call doesn't throw, so the PDF opens as binary text. Confirmed by clicking.
- `#page=N` on a file link is dropped as well.

**Only some link types survive.** The panel's HTML sanitizer allows `http(s)`, `mailto`, `tel`,
`callto`, `sms`, `cid`, `xmpp` and scheme-less paths. It strips `vscode://`, `file://` and `skim://`.
So a clickable link must be `http(s)`.

**Where http links go.** Clicked `http(s)` links go through the extension's `openURL()`:

- It honours `$BROWSER` only when `vscode.env.remoteName` is set, i.e. in remote sessions.
- Locally it calls `vscode.env.openExternal`.
- `openExternal` goes through VS Code's opener service, which respects the
  `workbench.externalUriOpeners` setting. **That is the hook for clickable links.**

**The existing viewer ignores page numbers.** `tomoki1207.pdf` builds its pdf.js webview from the
document URI and ignores any fragment. It also has no highlight saving.

**Tested alternatives.**

- A pdf.js generic viewer served over http honours `#page=7` and `#nameddest=table.2`. But links
  to it open in the browser, and the user rejected that.
- `vscode-pdf-editor` (yasin-dev) rendered poorly.
- **PDF Phoenix** (`harshankur.pdf-phoenix`) is the best existing one: pdf.js, highlights saved into
  the file. But it has no page-link entry point.

## What to build

1. **Custom editor for `*.pdf`**, based on pdf.js:
   - Open at a page, a named destination, or a search term.
   - Highlight tool; save the annotations **into the PDF file** (pdf.js `saveDocument()`), since the
     user's highlights live in the PDF.
   - Reload when the file changes on disk.
   - If an open tab is asked for a new page, navigate it rather than opening a second tab.
   - Start by checking PDF Phoenix's licence. If a fork is allowed, adding an entry point to it is
     likely the shortest path. Otherwise build on the pdf.js generic viewer (Apache-2.0).
2. **Command** `paperViewer.open` with arguments `{ file, page?, dest?, search? }`.
3. **URI handler** (stable API `window.registerUriHandler`):
   `vscode://<publisher>.<name>/open?file=...&page=7&dest=table.2`.
   Plus `scripts/open-pdf`, which builds that URI and runs `open` on it. The agent uses this script.
4. **External URI opener for `http://paper.link/open?...`**, which makes chat links clickable.
   - This is the risky part. `window.registerExternalUriOpener` is a *proposed* API.
   - Enable it for this one extension through `~/.vscode/argv.json`:
     `"enable-proposed-api": ["<publisher>.<name>"]`.
   - Map the host with `"workbench.externalUriOpeners": { "paper.link": "<opener id>" }`.
   - **Build this first, as a spike**, with a stub that just shows the parsed URL. Confirm that a
     link clicked in the Claude panel reaches the opener without opening a browser tab. Only then
     build the rest.
   - If the proposed API can't be enabled, report back rather than working around it.
5. **Resolving `file`.** Accept an absolute path, or a path relative to a configurable PDF root.
   Papers live outside the repo, in `~/Yandex.Disk.localized/Papers/<topic path>/`, mirroring
   `library/`. Default `paperViewer.pdfRoot` to that folder. Links should use paths relative to
   it, so they keep working on another machine.

Prefer `dest` over `page` when both are given. arXiv PDFs built with hyperref carry named
destinations (`section.4.3`, `subsection.4.3`, `table.2`, `figure.3`), so the agent can link a
section straight from the section number in the markdown. `page` is the fallback for PDFs without
them.

## Fallback idea: Skim

If the clickable links in item 4 can't be made to work, Skim gives a weaker version outside VS
Code. Skim is installed and registers `skim://`: `open "skim:///abs/path/file.pdf#page=7"` opens
Skim at that page. Fragments can be combined with `&`, and `search=<term>` also works. Opening
Zep at page 7 this way was confirmed on 2026-09-29.

The chat panel strips `skim://` links, so this only works as an agent action: Claude runs the
`open` command itself, and only when Anton asks it to open a paper. If it comes to that, give
`scripts/open-pdf` a `--skim` flag. Until this task is done, `AGENTS.md` says nothing about
opening PDFs.

## Test fixture

Use Zep (arXiv 2501.13956), at `llm/memory/agent/Zep A Temporal Knowledge Graph Architecture for Agent Memory.pdf` under the PDF root. It has 12 pages and 70 named
destinations. Its markdown in `library/` carries the same page numbers on its headings.

| Target | Page | Named destination |
|---|--:|---|
| §2.2.3 Temporal extraction and edge invalidation | 3 | `subsubsection.2.2.3` |
| §3.1 Search | 4 | `subsection.3.1` |
| Table 1: Deep Memory Retrieval | 6 | `table.1` |
| §4.3 LongMemEval | 6 | `subsection.4.3` |
| Table 2: LongMemEval results | 7 | `table.2` |
| §6.1 Graph construction prompts | 8 | `subsection.6.1` |

## Done when

- A link written in the Claude chat panel opens Zep at Table 2 in a VS Code tab, with no browser
  tab. For example: `[Table 2](http://paper.link/open?file=llm/memory/agent/Zep%20A%20Temporal%20Knowledge%20Graph%20Architecture%20for%20Agent%20Memory.pdf&dest=table.2)`.
- `scripts/open-pdf "llm/memory/agent/Zep A Temporal Knowledge Graph Architecture for Agent Memory.pdf" --page 3` does the same from a terminal.
- A highlight made in the tab is saved into the PDF and is visible in Skim or Preview afterwards.
- A short section in `AGENTS.md` tells the agent the link format and when to use it.
