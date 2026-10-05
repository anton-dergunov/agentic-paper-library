# Working with papers: design

How papers are stored, read and discussed, and why this is built rather than taken from an
existing tool. Written 2026-09-29 for my own library and updated as decisions were made; on
2026-10-03 the engine (scripts, skills, conventions) was split from the library into this
repository, so the same workflow can run more than one library. Out of scope here: paper
discovery.

## The finding that shapes everything

What I want next to a PDF is not a chat box. It is an agent that can:

- read the paper I am on,
- read the other papers in my library,
- read my Obsidian notes (and org plans),
- write into Obsidian while we talk,
- run my own skills, and keep the conversation so I can come back to it.

Claude Code already does that on the desktop. Every "AI PDF reader" does less:

- **PaperNook** runs Claude Code with every tool switched off (`claude -p --safe-mode --tools
  "" --strict-mcp-config ...`). Its chat is Q&A about one paper, grounded in text extracted from
  the PDF. It cannot open a markdown library, touch Obsidian, or use skills.
- **Open Paper, pdfpal, Khoj and NotebookLM** have the same shape: the chat sits inside the app.

So the hub is a Claude Code session, and the PDF reader is whatever reads PDFs best. The tablet
reaches the session through **Remote Control**: `claude remote-control` on a host, driven from
the Claude app on iPad or Android.

## Setup

```
 iPad                                               host (Mac now, NAS later)
┌───────────────────────┬───────────────────┐      ┌──────────────────────────────────────┐
│ PDF app               │ Claude app        │      │ claude remote-control  (in ~/papers) │
│  reads + highlights   │  Remote Control ──┼──────┼─▶ reads  library/ markdown           │
│  the PDF from cloud   │  session          │      │   reads  Obsidian, org, projects     │
└──────────┬────────────┴───────────────────┘      │   writes Obsidian notes              │
           │                                       │   runs   skills                      │
           ▼                                       └──────────────┬───────────────────────┘
   Yandex Disk  Papers/<topic path>/<Title>.pdf ◀─────────────────┘ (add-paper downloads here)
```

- **Desk:** VS Code with the Claude Code panel in `~/papers`. PDFs open in my own VS Code PDF
  viewer, [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer), where page
  links in the chat land. See [vscode.md](vscode.md).
- **iPad:** a native PDF app for reading and highlighting, plus the Claude app on a Remote
  Control session. They can be side by side, switched between, or on two devices: the iPad Air
  for the PDF and the iPad mini for the chat.
- **E-ink tablet:** read there, with the session on the iPad or phone.

## Storage

| What | Where | Why |
|---|---|---|
| PDFs (for me) | Yandex Disk `Papers/<topic path>/<Title>.pdf` | Synced to every tablet and to the NAS (Cloud Sync). Highlights live in the PDF. Not in git. |
| Markdown (for the agent) | `~/papers/library/<topic path>/<Title>.md` + `images/` | Converted from arXiv HTML, which is measurably better than PDF text for maths and tables ([conversion.md](conversion.md)). Same path as the PDF. |
| Indexes | a generated `README.md` per folder | Lets the agent (and me) find papers without reading them all. |
| Workflow | this repository: `scripts/` behind `paperlib`, `skills/`, `guide/` | Adding, moving and checking papers. Linked into each library (`paperlib init`). |
| Library config and instructions | `~/papers/paper-library.yaml`, `~/papers/AGENTS.md` | Where this library's PDFs and notes are, and who reads it. |
| Paper notes | Obsidian `10 Knowledge/ML & AI/Papers/<Title>.md` | Overview plus what I took from the paper. Named after the library file; flat, grouped by a `topic` property. |
| Agent memory | `~/papers/notes/<Title>.md` | What the agent learned about a paper (digest, related papers, Q&A), so later sessions don't re-read it. |
| Conversations | Claude Code session transcripts | The durable part goes into Obsidian at the end of a session. |
| Backlog | `INBOX.txt` | Links and titles waiting to be added. |

The library is a private GitHub repo of its own. Git gives history for
reorganisations and is how a second host such as the NAS gets and returns changes. GitHub's
10 GB repo limit is far away: 2,200 papers take 2.6 GB on disk and 1.4 GB in `.git`. The repo
lives at `~/papers`, not in Dropbox or Yandex, because git repos inside sync folders get
corrupted.

## The reading loop

1. **Add.** Paste an arXiv link into a session; `add-paper` fetches it, files it under a topic,
   and writes the summary.
2. **Decide.** Read the overview, then drop, skim or read. For most papers the overview is the
   whole reading.
3. **Read with the agent.** It says what is new compared with papers I already have, which
   sections matter, and which prerequisites to explain first. Then I ask as I read: "explain
   eq. 4 without the notation", "how is this different from MemGPT". Answers cite pages
   ("p. 7, Table 2"), which works in any PDF app.
4. **Wrap.** The agent writes what I took from the paper into the Obsidian note: the idea, the
   mechanism, connections, what I would reuse. This comes from the conversation, not copied
   highlights.
5. **Across papers.** Sessions with no single paper: "what do my papers say about temporal
   knowledge graphs for memory".

Steps 2–4 depend on the note format and the `overview`, `read` and `wrap` skills, which are the
next piece of work.

## Decisions log

- **Claude Code is the hub; retire Zotero.** The llm-for-zotero plugin was tried. Its reader is
  good, but it is desktop only, citation clicks did not open at the right page, highlights are
  stored in Zotero's database rather than the PDF, its Claude Code mode is experimental, and
  building my topic structure in Zotero collections would take too much work.
- **PaperNook: not the hub.** Beyond the sandboxed chat, it owns its storage: one level of topic
  slugs, and papers only appear once imported through its own pipeline.
- **VS Code on the iPad: ruled out.** Tested in the browser and over a `code tunnel`: PDF
  rendering, pinch-zoom and highlighting were poor, and the Claude panel worked worse.
- **Page links from chat:** file-path links in the Claude panel open PDFs as text, and it strips
  every link type except `http(s)`. So page links are `http://pdf.invalid/<path>?page=…`
  URLs, which my PDF viewer extension claims and opens at the spot, next to the chat. Its
  [README](https://github.com/anton-dergunov/vscode-pdf-viewer) has the format and the setup.
- **Engine and library apart (2026-10-03).** I keep libraries in more than one context (my own,
  and one per employer or project), and the engine is worth sharing while the collection is
  not. The library is a folder with `paper-library.yaml`; the engine finds it from the working
  directory, links its skills in, and renders its conventions into `.claude/library-guide.md`.
  The library's own `AGENTS.md` holds what is personal: who reads it, their focus, where their
  notes are.
- **Papers are read one request each, by Opus, into notes (2026-10-05).** The first five
  literature reviews each used up a usage window. Their reading agents took 70–80% of the
  tokens, and two thirds of that was an agent re-reading the papers it had already finished
  ([experiments/review-token-cost](../experiments/review-token-cost/README.md)). `paperlib
  read` now sends each paper's main text in a single request and writes the note, so a
  review's reading is resumable and reusable, and every paper is read in full. Opus stays
  the reader: on six papers its notes had 1 error against 6 for Sonnet, 7 and 9 for two
  Gemini models and 35 for Haiku
  ([experiments/reading-models](../experiments/reading-models/README.md)).
- **A review is a map, not evidence (2026-10-05).** Sessions find reviews and notes on
  their own. With a review, a synthesis answer took a third of the tokens and had more
  misreadings, because the session never opened the papers; with notes and no review the
  answers were the most accurate
  ([experiments/review-usefulness](../experiments/review-usefulness/README.md)). The guide
  tells sessions to check the note or the paper before stating a number or its meaning.
- **Other tools considered:** Open Paper (same shape as PaperNook), Khoj (meaning-based search;
  revisit if the library reaches thousands of papers), pdfpal (its CLI-plus-skill design is
  what this project does), Paperless-ngx (a document archive, not a reader).

## Next

Done: the `overview` skill; the PDF viewer extension; the library expansion, which grew my
library from 240 LLM papers to 2,200 across the whole field (the `literature-pass` skill); the
`literature-review` skill; the split of the engine from the library; and the Paper Library
VS Code extension, which opens a paper by title ([tasks/vscode-extension.md](tasks/vscode-extension.md)).

1. The `read` and `wrap` skills.
2. Running a library from a cloud session (Claude Code on the web), which needs the engine
   installed by a setup step.
3. Link the Obsidian notes to library papers: concept notes and paper lists cite papers by
   arXiv id or title, and now nearly all of them have a library copy.
4. Run the session on the NAS, so it is always on:
   - install Claude Code there,
   - clone the engine, the library and the vault,
   - check that Cloud Sync is two-way for Yandex and Dropbox,
   - keep `claude remote-control` running.
