# Task: PDF viewer extension with page links from the Claude chat

**Status (2026-10-01):** built. The last check is still to do: Anton clicks a link in the real Claude
panel. The extension is `~/projects/prototypes/vscode-pdf-viewer` (`anton.vscode-pdf-viewer`); its
README has the link format and the setup. `AGENTS.md` ("Linking to a place in a paper") tells the
agent how to write the links.

## What it does

- A pdf.js-based custom editor for `*.pdf`. It has highlighting saved into the PDF, search, and
  zoom. It reloads when the file changes on disk (e.g. highlights synced from the tablets). A tab
  with unsaved highlights is left alone, with a warning.
- **Clickable links in the Claude chat:**
  `[p. 7, Table 2](http://pdf.invalid/<topic path>/<Title>.pdf?dest=table.2&page=7)`.
  - Clicking one opens the PDF at that spot in a VS Code tab, next to the chat if the chat is an
    editor tab. A link to an open paper navigates its tab.
  - Papers open as regular tabs, not preview tabs, so opening another paper doesn't replace one.
  - `search=<phrase>` marks a phrase on that page.
- `dest` is preferred; `page` is the fallback when the name is not in the PDF.
- The same links also work as `vscode://anton.vscode-pdf-viewer/<path>?…`, for notes outside VS Code.
  VS Code asks once before letting the extension open them.
- No agent action and no Skim: Anton opens links himself, and the agent never opens PDFs.

## How chat links reach the viewer

Checked on 2026-10-01 against `anthropic.claude-code` 2.1.286 and VS Code 1.138, by reading
their code and by clicking links in a webview in a test instance. Re-check after big updates of
either.

- **The panel's link handling.** The panel renders markdown links as
  `<a href target="_blank">` with its own click handler (`qc0` in `webview/index.js`).
  - That handler acts only on hrefs it parses as file paths (`path`, `path:12`, `path#L12`,
    `path#heading`). Those go to `openFile()` → `showTextDocument`, which opens a PDF as binary
    text and drops `#page`.
  - Any `http(s)` URL falls through to the browser's default navigation. VS Code's webview host
    catches that and opens the link with `openerService.open(link, { allowContributedOpeners: true })`.
- **Correction to the 2026-09-29 notes.** Chat links do *not* go through the extension's
  `openURL()` → `vscode.env.openExternal`. That route would not work: `openExternal` without
  `allowContributedOpeners` never consults extension openers.
- **Claiming the link.** An extension can claim the link with `window.registerExternalUriOpener`,
  a **proposed** API.
  - Stable VS Code allows it for one extension listed in `~/.vscode/argv.json`:
    `"enable-proposed-api": ["anton.vscode-pdf-viewer"]`.
  - With `ExternalUriOpenerPriority.Preferred` no `workbench.externalUriOpeners` setting is needed.
- **The host is `pdf.invalid`, not `*.localhost`.** VS Code 1.138's integrated browser
  (`workbench.browser.openLocalhostLinks`, on by default) claims `localhost` and `*.localhost`
  links before any extension opener sees them. `.invalid` is reserved and never resolves.
- **The file goes in the URL path, not a `file=` query parameter.** `vscode.Uri` hands the query
  over already percent-decoded, so `%26` becomes `&`. 14 PDFs have `&` or `+` in their names
  ("Wide & Deep …"). Paths are decoded separately and are safe.
- **The extension activates on startup.** It does not wait for `onOpenExternalUri:http`, so the
  opener is registered before the first click.

## Named destinations

- Of 40 sampled library PDFs, 34 have named destinations. LaTeX/hyperref names sections
  `section.4`, `subsection.4.3` and `subsubsection.2.2.3`, and appendices `appendix.A` and
  `subsection.A.1`.
- `table.N` and `figure.N` exist in many papers. Others only have `figure.caption.N`, a running
  counter that does not match the figure number. So links always carry `page` too.

## Test fixture

Zep (arXiv 2501.13956), `llm/memory/agent/Zep. A Temporal Knowledge Graph Architecture for Agent
Memory.pdf` under the PDF root: 12 pages, 70 named destinations (`pdfinfo -dests`; pdf.js's
`getDestinations()` lists none for it, but `getDestination(name)` resolves each one).

| Target | Page | Named destination |
|---|--:|---|
| §2.2.3 Temporal extraction and edge invalidation | 3 | `subsubsection.2.2.3` |
| §3.1 Search | 4 | `subsection.3.1` |
| Table 1: Deep Memory Retrieval | 6 | `table.1` |
| §4.3 LongMemEval | 6 | `subsection.4.3` |
| Table 2: LongMemEval results | 7 | `table.2` |
| §6.1 Graph construction prompts | 8 | `subsection.6.1` |

## Left to check

- A link written by Claude in the real chat panel opens Zep at Table 2 with no browser tab. This
  needs the `argv.json` line and the installed `.vsix`.
- A highlight saved in the viewer shows in Preview or Skim, and survives a round trip through
  the tablets.
