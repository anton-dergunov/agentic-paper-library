# Working with papers: design

How papers are stored, read and discussed, and why this is built rather than taken from an
existing tool. Written 2026-09-29 for my own library and updated as decisions were made; on
2026-10-03 the engine (scripts, skills, conventions) was split from the library into this
repository, so the same workflow can run more than one library. Out of scope here: paper
discovery. How to use a library is in the [user guide](user-guide.md).

## The main requirement: few tokens

Besides doing its job (keeping papers where an agent can read them, and helping me read
them), the library has one requirement above the others: **an agent should answer questions
about papers with as few tokens as possible**, quickly and without re-deriving what was done
before. The engine exists to save tokens. Work that spends more than it saves is the wrong
work.

- **Keep the paper as it is, and read only what is needed.** The PDF is the paper; its text
  layer, with a line `[page N]` at each page, is how an agent greps and reads it, and the
  agent opens a page of the PDF for what the text lacks. Nothing is converted, so nothing
  has to be fixed, re-converted or checked against the PDF ahead of time
  ([experiments/reading-formats](../experiments/reading-formats/README.md)).
- **Don't do work ahead of time.** I will discuss perhaps three papers a day, and most
  papers in the library never. A session that reads a paper for nobody's question costs
  a lot; notes are written once, for the areas I review, and kept.
- **Sessions are what cost.** What wastes tokens is a session redoing work: re-reading the
  same papers, re-deriving what a note or a review already says.

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
│  reads + highlights   │  Remote Control ──┼──────┼─▶ reads  library/ text, PDF pages    │
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
| Text (for the agent) | `~/papers/library/<topic path>/<Title>.txt` | The frontmatter, then the PDF's text layer with a line `[page N]` at each page ([text-layer.md](text-layer.md)); a web article is `<Title>.md`. Same path as the PDF. |
| Indexes | a generated `README.md` per folder | Lets the agent (and me) find papers without reading them all. |
| Workflow | this repository: `scripts/` behind `paperlib`, `skills/`, `guide/` | Adding, moving and checking papers. Linked into each library (`paperlib init`). |
| Library config and instructions | `~/papers/paper-library.yaml`, `~/papers/AGENTS.md` | Where this library's PDFs and notes are, and who reads it. |
| Paper notes | Obsidian `10 Knowledge/ML & AI/Papers/<Title>.md` | Overview plus what I took from the paper. Named after the library file; flat, grouped by a `topic` property. |
| Agent memory | `~/papers/notes/<Title>.md` | What the agent learned about a paper (digest, related papers, Q&A), so later sessions don't re-read it. |
| Conversations | Claude Code session transcripts | The durable part goes into Obsidian at the end of a session. |
| Backlog | `INBOX.txt` | Links and titles waiting to be added. |

The library is a private GitHub repo of its own. Git gives history for
reorganisations and is how a second host such as the NAS gets and returns changes. GitHub's
10 GB repo limit is far away: 2,275 papers' text takes about 300 MB on disk; `.git` holds
1.8 GB, most of it the markdown and figures of before 2026-10-26. The repo
lives at `~/papers`, not in Dropbox or Yandex, because git repos inside sync folders get
corrupted.

## The reading loop

1. **Add.** Paste an arXiv link into a session; `add-paper` fetches it, files it under a topic,
   and writes the summary.
2. **Decide.** Read the overview, then drop, skim or read. For most papers the overview is the
   whole reading. `paperlib remove` drops one.
3. **Read with the agent.** It says what is new compared with papers I already have, which
   sections matter, and which prerequisites to explain first. Then I ask as I read: "explain
   eq. 4 without the notation", "how is this different from MemGPT". Answers cite pages
   ("p. 7, Table 2"), which works in any PDF app.
4. **Wrap.** The agent writes what I took from the paper into the Obsidian note: the idea, the
   mechanism, connections, what I would reuse. This comes from the conversation, not copied
   highlights.
5. **Across papers.** Sessions with no single paper: "what do my papers say about temporal
   knowledge graphs for memory".

The `overview` skill covers step 2. Steps 3 and 4 work in any session today; the `read` and
`wrap` skills that would give them a fixed form are not written yet.

## Decisions log

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
- **Instructions cost tokens on every turn, so each rule lives where it is used (2026-10-07).**
  The guide, a library's `AGENTS.md` and the skill list load into every session and subagent
  and are re-read each turn; a skill's files load when it runs. Rules only one workflow needs
  moved from the guide into that skill, duplicates went, and history moved to the docs: the
  library's share of a session's start fell from 8.3K to 5.5K tokens, with no rule lost and
  no change found in notes, answers, overviews or adds. Skills are not split further, since
  reading another file costs a turn. `paperlib read` and `add` keep the user's CLAUDE.md files
  out of their requests and send what an area shares as a cached system prompt: a read cost
  24% less on six papers, and twenty sessions of seven tasks showed no change in behaviour
  ([experiments/prompt-trim](../experiments/prompt-trim/README.md)).
- **A review is a map, not evidence (2026-10-05, measured again 2026-10-06).** Sessions
  find reviews and notes on their own. Told to start from the review, a session answered a
  synthesis question from it alone: a third of the tokens and more misreadings. The guide
  now tells sessions to search the review, then check the note or the paper before stating
  a number or its meaning. With that rule, over five questions and three sessions each,
  they do, and their answers have as few wrong statements as answers written without
  reviews. They are not more complete, and on a question the review covers they are
  narrower; the fifth of the tokens saved is within the run-to-run differences. A stronger
  wording (notes and papers first) cost half again as much for a gain within those
  differences, so the rule stays. Reviews are written for the reader; an agent gains a way
  in to an area, not a better answer. Answers from the papers alone, without notes, were as
  good ([experiments/review-usefulness](../experiments/review-usefulness/README.md)).
- **Filing a paper is one request to Sonnet (2026-10-05).** Adding a paper through the
  `add-paper` skill took 228K tokens in a Sonnet session, nearly all of it the session's
  context sent five times, for a choice of folder and one sentence. Given the topic tree,
  the title and the abstract in a single request, Sonnet chose a folder a blind judge
  graded best for 53 of 60 papers (Opus 57, Haiku 49, the folders the papers were in 47)
  and wrote summaries level with Opus's
  ([experiments/skill-models](../experiments/skill-models/README.md)). `paperlib add` does
  that and never creates a folder; the skill stays for new folders, titles, PDFs and the
  inbox. Each skill now names its model in its frontmatter: Sonnet for `add-paper` and
  `expand-library`, Opus for the rest. Only the reader and the filing model are measured.
- **A quick look at a paper reports and does not recommend (2026-10-09).** Papers now arrive
  one at a time, and most need a look before they are worth adding. The first design gave
  a verdict (`add`, `skip` or `read first`) from the abstract, citation data, the folder's
  papers and a file of the reader's interests. On 72 papers of known fate it did not
  separate the papers I had skipped from those I kept: Sonnet would add 22 of 30 skipped
  and 28 of 42 kept
  ([experiments/paper-vetting](../experiments/paper-vetting/README.md)). The cause is not
  the model: why I want a paper (a colleague passed it on, a project touches it) is not in
  any file, so a recommendation can only be invented. `paperlib info` therefore reports
  along fixed axes and leaves the decision to me, or to a tool that knows my plans:
  whether the library has the paper and where its files are, its venue and citations with
  a fixed grade of the citation rate, which library papers name it, what it proposes, its
  type, and the nearest papers of its folder. `--json` is the same for another program;
  `--facts` skips the two model requests. A library paper is answered with no network. The
  `paper-info` skill only runs it.
- **Lookups read a saved index of frontmatter (2026-10-10).** Every `paperlib info` took
  seconds, saved answer or not: finding a paper by arXiv id read and parsed all 2,200
  papers, and finding it by title did so twice. The frontmatter is now kept in one file in
  the cache with each paper's size and modification time, and only a changed paper is read
  again. In my library: a paper in the library 2.7 s → 0.4 s, a saved answer 3.6 s → 0.4 s,
  title words 5.7 s → 0.4 s, of which 0.3 s is starting Python through uv. Title words also
  find a paper outside the library that was looked at before. On a terminal the row names
  are bold and the status coloured; piped, redirected or run by a script the output is
  plain, so nothing has to strip it. `paperlib -C <library>` names the library as
  `git -C` does. Other tools read `info --json` (a capture inbox adds it to items about
  papers), so its keys are an interface: add keys, do not rename them.
- **A paper is tried by adding it, and dropped with `paperlib remove` (2026-10-11).** After
  `paperlib info`, the next step for a paper of some interest is to read a little of it with
  the agent, before deciding to keep it. A staging area was considered: convert into the
  cache, chat, add later. It would give a paper a second state, and the notes, `info`'s
  neighbours and the VS Code extension all assume a paper is in `library/<topic>/`. It would also cover only the paper tried today, not a
  duplicate, a wrong match or a paper added a year ago. An add is already close to a trial,
  since nothing is committed until I commit. So `remove` deletes the paper's text, its PDF
  and the agent's note, and with `--reason` records the paper in `catalog/skipped.yaml`; it
  leaves my overview note, and reports the reviews and notes that still name the paper. It
  lists all this and asks before it deletes, since a PDF may hold highlights and is not in
  git.
- **What to read next is a command, and re-reading is the exception (2026-10-19).** The rollout of the literature reviews lived in a hand-kept task file in
  the library: the order, a status per scope, how many papers had no note, and a list of
  39 notes to read again after a reconversion. Its counts went stale within days (it said
  42 of `llm/memory`'s papers had no note when all 70 had one). `paperlib reading` now
  computes the same from the library: per scope in the order of `review_scopes`, papers
  read and left, notes to read again, the API cost of reading them (fitted to 1,061 logged
  readings, $0.11 a paper plus $3.4 per million characters of reading view, median error
  11%; refitted for the text layer on 2026-10-26), and the review's state. A note to read
  again carries a `reread:` line, which `paperlib reread` writes: a reading costs about
  $0.30, and a session answering a question reads the paper as it is now anyway.
- **The agent's copy of a paper becomes its PDF's text layer, beside the PDF (2026-10-26).**
  The library's markdown was meant to answer questions better than the PDF; measured, it
  answers them no better ([experiments/reading-formats](../experiments/reading-formats/README.md)).
  - On 51 single-paper questions the PDF got 51, the text layer 43 and the markdown 43. The
    eight lost by both text forms are values drawn in a plot.
  - Across papers, an agent in a folder of text layers answered 13 questions as well as one
    in the library, for $0.30 a question against $0.42.
  - With the PDF beside the text layer, an agent opened the page for 9 of 9 drawn values and
    for 0 of 6 questions the text answers, unprompted. Where the text layer is broken, it
    opened the page for 5 of 9 passages and read through the rest.
  - Notes written from the text layer were preferred in 9 of 12 blind comparisons, with no
    wrong page against the markdown's 17.
  - The text layer keeps the numbers inside vector figures and has none of the converter's
    errors. The markdown's LaTeX bought nothing on 17 equation questions.
  So the text layer from `pdftotext -layout`, with a line `[page N]` at each page and the
  PDF beside it, replaces the markdown as what an agent reads. A paper is now
  `library/<topic>/<Title>.txt`: its frontmatter, then the text layer, committed, so that a
  session without the PDFs still reads every paper. Claude Code's habit of opening a page
  only when the text lacks the value is what this rests on, so `run.py canary` checks it on
  each release.

  What went with the markdown: the arXiv-HTML and PDF converters (docling, marker's
  equation model, OCR), page mapping, caption numbering, missing pages, KaTeX checks,
  conversion symptoms, reconversions and hand corrections; the conversion problems the
  reader recorded per paper (`issues/`, 799 records) and the tickets they were filed under
  (38 open, two of them, `page-markers-within-sections` and `figure-text-lost`, the cause
  of the markdown's wrong pages and missing figure numbers in the comparison above); the
  skills that triaged and fixed them; 2.6 GB of figure images; 25 experiments on the
  conversion; about 9,900 of the engine's 14,000 lines of scripts. The last engine with all of
  it is commit `6466cd2`. The notes and reviews written from the markdown stay: the notes
  lost only their line on conversion problems, and the guide says that a note written
  before the switch may call a part of the paper missing that the text layer has.

  Web articles stay markdown: a web page is made for the browser, and its printed PDF
  often loses pages. Their converter, which shared the arXiv-HTML one's code, is now
  Defuddle on the page as Chrome renders it; of three candidates on three articles it was
  the only one to keep the maths as TeX and the footnotes, and it covered the articles as
  fully as the old converter ([experiments/web-articles](../experiments/web-articles/README.md)).
  They keep no images, and their `url` leads to what is missing. The move of the author's library, and what it
  found (the reading view's cut rebuilt, two more web-converter fixes, and Claude Code refusing to read PDFs
  outside the library until their folder is allowed), is in
  [experiments/text-layer-switch](../experiments/text-layer-switch/README.md).
- **Other tools considered:** Open Paper (same shape as PaperNook), Khoj (meaning-based search;
  revisit if the library reaches thousands of papers), pdfpal (its CLI-plus-skill design is
  what this project does), Paperless-ngx (a document archive, not a reader).

## Next

1. Check what the switch left unmeasured, as it happens: a review of a whole area written
   from notes read off the text layer, its reading cost (the fit in `paperlib reading` is
   from four papers until 20 readings are logged), and papers whose text layer has a
   plausible wrong digit, which only a reader who opens the page catches.
2. The `read` and `wrap` skills.
3. Running a library from a cloud session (Claude Code on the web), which needs the engine
   installed by a setup step.
4. Link the Obsidian notes to library papers: concept notes and paper lists cite papers by
   arXiv id or title, and now nearly all of them have a library copy.
5. Make reading a paper cheaper without reading it less: trim the fixed part of the request,
   then test a cheaper reading for the thinly covered areas
   ([tasks/reading-cost.md](tasks/reading-cost.md)).
6. Run the session on the NAS, so it is always on:
   - install Claude Code there,
   - clone the engine, the library and the vault,
   - check that Cloud Sync is two-way for Yandex and Dropbox,
   - keep `claude remote-control` running.
