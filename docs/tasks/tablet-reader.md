# Task: read a paper on a tablet with Claude Code beside it, in one app

Reading with the agent works well in VS Code: the PDF on one side, Claude Code on the other, and a citation in the answer opens the PDF at its page ([docs/vscode.md](../vscode.md)). It needs a desk. On a tablet the fallback is Remote Control in the Claude app beside a PDF app, and in practice it costs 5–10 minutes before every sitting:

- Split View has to be set up by hand each time, with several taps, and it works differently on the iPad and on the Android e-ink tablet.
- `claude remote-control` has to be started on the laptop first, so a sitting has to be planned in advance.
- PDF apps are cluttered, the opposite of calm reading, and getting papers into them from a synced folder (Yandex Disk) is fiddly.
- A citation in the answer does not open the PDF; the reader finds the page by hand.

The goal is one installed web app, served from the laptop (later the NAS) over Tailscale: tap a paper, and its PDF opens with a chat under it that is ready for a question. The Claude Code session runs on the server, where the library, the engine and the PDFs are; the tablet only shows it. Starting a sitting takes seconds instead of minutes, so the reader reads more papers, and away from the desk. [Lectern](../../../../tools/lectern/) is the model for the app around the reading: installed on the Home Screen, served over Tailscale, started at login, at home on e-ink.

## Decisions already taken

- **The chat is drawn by the app, not copied from the VS Code extension.** The Claude Code panel in VS Code is a closed, minified bundle (6 MB, "© Anthropic PBC. All rights reserved") that talks to the extension through a private message format which changes with every release. Hosting it outside VS Code would break with every update and cannot be redistributed.
- **The session is Claude Code itself, through the Agent SDK** (`claude-agent-sdk`, Python). It runs the same engine as the terminal and the VS Code panel (tools, skills, the library's `AGENTS.md` and guide, permissions) and reports each step as typed, documented messages: reply text as it streams, tool calls and results, thinking, permission requests. A Claude Code update is an SDK version bump.
- **A terminal in the browser is not the chat.** The point of the VS Code panel is how it shows an answer: tables as tables, tool calls folded away. A terminal draws a table in box characters.
- **The reader's own subscription.** The SDK on the reader's own Pro/Max plan, for their own use, is individual use and counts against the plan's usage limits. Anthropic has paused a change to how the SDK is billed; check [their support page](https://support.claude.com/en/articles/15036540-use-the-agent-sdk-with-your-claude-plan) before relying on any particular arrangement.
- **Python, in its own repository: [carrel](../../../carrel/).** It is an app with its own frontend, deployment and update rhythm, like vscode-pdf-viewer. The server imports `scripts/paperlib.py` from the engine checkout, so the library is read exactly as the scripts read it, with no third copy beside `editors/vscode/src/library.ts`. Lectern is Python too, and its serving code was borrowed.
- **Who connects: only the reader, through `tailscale serve`.** The server listens on 127.0.0.1 only; `tailscale serve` publishes it over HTTPS on the tailnet and adds the caller's Tailscale login, and the server admits only the reader's (a tagged device carries none). Host and Origin checks stop a web page in the tablet's browser from driving it. No password.
- **What the agent may do: Claude Code's default tools, bounded by its sandbox, and the reader asked for the rest.** The same tools as the terminal and the panel, which is what the reading-formats experiments measured. Bash runs in Claude Code's sandbox, which writes only in the library, the PDFs, the engine's cache and the note folders, and reaches only listed domains; inside it a command runs without asking. Web search and fetch, `paperlib`, and writing notes run without asking. Anything else, including leaving the sandbox or reaching another host, is put to the reader as Allow / Deny on the tablet. A login protects nothing against prompt injection from a fetched page; the sandbox does.
- **What runs without asking is widened from use, not guessed.** `carrel tools` tallies the tools carrel's sessions used (Claude Code's transcripts, `entrypoint: sdk-py`) and what the reader was asked and answered.

## Shape

```
tablet (installed web app)                         laptop or NAS
┌────────────────────────────┐                     ┌───────────────────────────────────┐
│ PDF, drawn with PDF.js     │ ◄── GET the PDF ─── │ server (Python, editors/web/)     │
│                            │                     │  library: paperlib.py             │
├────────────────────────────┤                     │  PDFs: the configured PDF folder  │
│ chat, drawn by the app     │ ◄── WebSocket ────► │  sessions: claude-agent-sdk,      │
│ [ ask about this page… ]   │   messages, with    │   cwd = the library               │
└────────────────────────────┘   sequence numbers  └───────────────────────────────────┘
```

## 1. Prototype: one paper, one question, on the iPad (about a day)

The smallest thing that proves the idea, before any polish.

- A server that serves one page, one PDF from the library's PDF folder, and a WebSocket that starts an SDK session in the library and passes its messages through.
- Allow / Deny for permission requests, moved here from part 2: without them the agent could not leave the reading rules at all.
- A page with the PDF on top (PDF.js) and the chat underneath: the reply as rendered markdown with GFM tables, everything else as plain one-line rows.
- A citation link in the answer moves the PDF to its page instead of opening a new tab. The link format is the one the guide already tells agents to write, and that vscode-pdf-viewer reads (`page=`, `dest=`, in `src/shared/linkFormat.ts`); port that parser rather than inventing a format.

Done when, on the iPad over Tailscale, a question about the open paper gets a streamed answer with a table drawn as a table, and tapping its citation moves the PDF to that page.

## 2. A chat that reads like the VS Code panel (2–4 days)

- Markdown: GFM tables that wrap to the screen, code, maths (KaTeX), links.
- Tool calls as folded one-line rows ("Read DPO.txt, pages 8–9", "Grep 'win rate' in library/"), opened by a tap. Thinking folded.
- Permission requests show Claude Code's own wording and reason (done in part 1, with Allow / Deny).
- Stop: interrupts the turn.
- A message type the app does not know is shown as a plain folded row with its type name, so an SDK update never breaks the chat; it only looks plainer until the app learns the new type.
- Slash commands typed in the box work as in the terminal, and the skills that make sense while reading (`/paper-info`, `/overview`) are also buttons.

Done when a dozen real questions from VS Code sittings, asked again in the app, read as well as they did in the panel.

## 3. The PDF and the chat know about each other (1–2 days)

- Chat → PDF: every citation link moves the viewer to its page or destination. When [precise-pdf-locations](precise-pdf-locations.md) lands, its `rect=` highlight comes along.
- PDF → chat: each message carries a short line saying which paper and which page is open, and the selected text if any, so the agent does not search for the paper. A few tokens per message.
- Select a passage, tap "Ask": the passage goes into the box as a quote.
- Links to another paper in the library open it in the viewer; a link outside the library opens the browser.

## 4. The library around the reading (1–2 days)

- A view of the topic tree, from the indexes `build-index.py` already writes: titles, year, authors, one-line summary, whether there are notes, reading status.
- A paper's page: its metadata, notes and overview if written, buttons for Read (PDF and chat), Overview, Remove.
- Add a paper by arXiv id or URL: runs `paperlib add` on the server and shows its output. Remove: runs `paperlib remove` after a confirmation.
- Search by title and summary.

Done when a paper goes from "heard of it" to open and asked about without touching the laptop.

## 5. Sessions, started and stopped from the tablet (about a day)

- "Ask about this paper" starts a fresh session scoped to that paper. Short sessions that start from the paper's notes cost less than one long session.
- Past sessions of a paper are listed with their first question and can be resumed. Resuming after an hour pays for loading the whole context again (the prompt cache lasts an hour), so the list shows how long ago a session last ran.
- The server keeps every session's messages, numbered. A tablet that slept or lost the network reconnects and catches up from its last number. A turn that is still running keeps running on the server.
- A session left idle (30 minutes, configurable) is closed by the server. Nothing runs for long unattended.

## 6. Lectern's comforts (2–3 days, as wanted)

- Installed on the Home Screen, full screen, reopening on the paper and page where the reader stopped.
- Themes (Solarized light and dark, black and white), text size for the chat, and where the split sits, remembered on each device.
- E-ink: chosen by itself, nothing animated, the PDF turned by page instead of scrolled, the chat's streaming shown in a few large updates rather than per word.
- Start the server at login (launchd, as Lectern does), and serve it on the tailnet.

## 7. On the NAS (later)

- A Docker image with Python, uv, poppler (for `paperlib`) and the SDK, logged in with a long-lived token from `claude setup-token`.
- The library and engine repositories checked out on the NAS, and the PDF folder reachable there, synced from Yandex Disk or moved.
- The same app, at the NAS's Tailscale address.

## Keeping it working

- An SDK version bump is the usual update. After one, ask the dozen questions of part 2 again.
- When a config key, the frontmatter or the layout of the trees changes, the server follows by itself, since it reads the library through `paperlib.py`.
- Tests run in carrel (`uv run pytest`, `node --test tests/links.test.mjs`): the link parser (its cases are vscode-pdf-viewer's; one shared table later), the library listing and PDF lookup, admission, permissions, the message serialisation. A recorded SDK stream per message type for the renderer is still to come.
- Once it is past the prototype, a page in `docs/` for setting it up, beside `docs/vscode.md`.

## Found while building part 1

- **Claude Code asks about the agent's everyday reading commands.** `cd …; f="…"; grep … "$f"` gets "Quoted text in this command can't be checked before it runs", sandbox or not: three asks in one answer. The sandbox is the boundary, so carrel allows a sandboxed Bash command itself and asks only when a command would leave the sandbox.
- **A connection to an unlisted host comes to the permission callback as its own request** (`SandboxNetworkAccess`, naming the host), so the domain list can grow from the reader's answers.
- **The SDK bundles its own Claude Code** (0.2.174 ships 2.1.310), not the one on the PATH; the canary is run on that one.
- **Sessions follow the library's conventions**, including adding Q&A to a paper's note: the first test question wrote seven lines to a note. That is the guide working; git is the undo.

## Open questions

- One session per paper, or one per sitting across several papers?
- Highlights and notes on the PDF, as Lectern does on its pages, kept beside the paper in the library? Useful, but a later part, and it touches the notes format.
- Does the PDF fit the e-ink tablet's screen above a chat, or does e-ink want the chat as a sheet pulled up over the page?

## Done when

From the tablet, with nothing done on the laptop beforehand: open the app, tap a paper, and ask a question within about ten seconds. Answers read as they do in VS Code, and each citation moves the PDF to its page. It works on both the iPad and the e-ink tablet, and a month of daily reading needs nothing but SDK updates.
