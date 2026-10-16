# User guide

How to use a paper library, in the order you will need it: install the engine, create a library, add papers, read them with the agent, write literature reviews, and keep the library healthy. Why it is built this way is in [design.md](design.md) and [conversion.md](conversion.md).

Two kinds of command appear below:

- `paperlib <command>` runs in a terminal, anywhere inside a library. `paperlib --help` lists every command.
- `/<skill>` runs in a Claude Code session opened on the library.

| I want to | Go to |
|---|---|
| Install the engine | [1. Install](#1-install) |
| Start a new library | [2. Create a library](#2-create-a-library) |
| Understand the folders | [3. What is in a library](#3-what-is-in-a-library) |
| Set up the editor | [4. Set up VS Code](#4-set-up-vs-code) |
| Look at a paper before adding it | [5. Look at a paper](#5-look-at-a-paper) |
| Add papers | [6. Add papers](#6-add-papers) |
| Remove or move papers | [7. Remove, move and reorganise](#7-remove-move-and-reorganise) |
| Read a paper with the agent | [8. Read a paper with the agent](#8-read-a-paper-with-the-agent) |
| Write a literature review | [9. Write a literature review](#9-write-a-literature-review) |
| Check that the library is in good shape | [10. Check the library's health](#10-check-the-librarys-health) |
| Find a command | [11. Commands and skills](#11-commands-and-skills) |

## 1. Install

You need:

| Tool | For |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Runs `paperlib`; it creates the Python environment on first use. |
| pandoc, librsvg (`rsvg-convert`) | Converting papers and their figures. |
| [Claude Code](https://claude.com/claude-code) (`claude`) | The skills, and the commands that ask a model: `paperlib add`, `info` and `read`. |
| Google Chrome or Chromium | Web articles only. |
| Node.js and VS Code's `code` command | The VS Code extension only. |
| llama.cpp (`brew install llama.cpp`) | Equations in papers that exist only as a PDF. |

```bash
git clone https://github.com/anton-dergunov/agentic-paper-library ~/projects/agentic-paper-library
ln -s ~/projects/agentic-paper-library/bin/paperlib ~/.local/bin/paperlib

paperlib --help              # the first run creates the environment
paperlib setup-equations     # optional: the equation model for PDF-only papers
paperlib test                # optional: the engine's own tests
```

Without `setup-equations`, a paper converted from its PDF has its equations as the PDF's raw text, and the paper says so at the top. Papers from arXiv's HTML are not affected.

To update the engine later: `git pull` in its folder, then `paperlib init` in each library (see below).

## 2. Create a library

```bash
paperlib init ~/papers --pdf-root ~/Dropbox/Papers
cd ~/papers
git init
```

A library is a folder with `paper-library.yaml` at its root. `init` creates that file, the folders, `AGENTS.md`, the links to the skills, the `pdf/` link and the VS Code settings, then builds the indexes. It creates only what is missing, so run it again after updating the engine or on a new machine.

- **`--pdf-root`** is where the original PDFs go. Choose a synced folder (Dropbox, iCloud, Yandex Disk) to read them on a tablet. Without the option they go to `pdfs/` inside the library. PDFs are never committed.
- **Keep the library itself out of synced folders.** It is a git repository, and those get corrupted there. A private repository on GitHub works well.

Then do three things by hand:

1. **Say who reads it**, in `AGENTS.md`: your focus and how you like papers explained. It is loaded into every session, so keep it short.
2. **Declare your topics** in `catalog/topics.yaml`, one line per folder with its scope. Parents are declared too:

   ```yaml
   llm: Large language models — how they are built, adapted, used and evaluated.
   llm/post-training: Adapting pretrained models after pretraining.
   llm/post-training/preference-learning: RLHF, reward models, DPO and other preference-optimization methods.
   ```

   A paper can only be added to a declared folder. The scope is what the model reads when it files a paper, so write what belongs there.
3. **Optionally set `overview_dir`** in `paper-library.yaml`: a folder for your own note per paper, for example in an Obsidian vault. `/overview` writes there.

[Configuration](configuration.md) lists every key.

**Several libraries.** Each is its own folder. `paperlib` uses the library it is run in. From elsewhere, name it: `paperlib -C ~/papers info 2305.18290`, or set `PAPER_LIBRARY`.

[examples/library](../examples/library/) is a small library made this way, with three papers.

## 3. What is in a library

```
~/papers/
├── paper-library.yaml        configuration
├── AGENTS.md, CLAUDE.md      your instructions for the agent
├── INBOX.txt                 links and titles waiting to be added
├── catalog/
│   ├── topics.yaml           every topic folder with its scope
│   └── skipped.yaml          papers you decided not to add, with the reason
├── library/
│   ├── README.md             index of everything (generated)
│   └── llm/post-training/
│       ├── README.md         index of this folder (generated)
│       ├── <Title>.md        the paper as Markdown, for the agent
│       └── images/           its figures
├── pdf/ → your PDF folder
│   └── llm/post-training/<Title>.pdf   the paper, for you
├── notes/<Title>.md          the agent's note on a paper
├── issues/<Title>.yaml       what the conversion broke in a paper, one record per problem
├── reviews/<topic>.md        literature review of an area
└── .claude/                  the agent guide (generated) and the skills (links)
```

| What | Who writes it | In git |
|---|---|---|
| `paper-library.yaml`, `AGENTS.md`, `catalog/topics.yaml`, `INBOX.txt` | You | Yes |
| `library/**/<Title>.md` and `images/` | `paperlib`, when a paper is added | Yes |
| `library/**/README.md`, `.claude/library-guide.md` | `paperlib build-index`; never edit them | Yes |
| PDFs | `paperlib`, when a paper is added | No |
| `notes/`, `reviews/` | The agent | Yes |
| `issues/` | `paperlib read`, and the agent | Yes |
| `catalog/skipped.yaml` | `paperlib` and the agent | Yes |

Three things are worth knowing:

- **A paper's Markdown and PDF have the same topic path and file name.** That is why papers are moved and removed only with `paperlib`, never by hand.
- **You read the PDF; the agent reads the Markdown.** The Markdown has equations as LaTeX, tables as tables, and the PDF page on every heading, as in `### 4.3 LongMemEval (p. 6)`. That is how an answer can cite "p. 6".
- **Each paper starts with a few fields**: `title`, `authors`, `published`, `arxiv`, `url`, `source` (`html`, `pdf-text` or `web`: how it was converted), `summary` (the one sentence the indexes show) and `added`.

Nothing is committed for you. After a change, look at `git status` and commit.

## 4. Set up VS Code

```bash
code ~/papers                # open the library folder itself
paperlib install-vscode      # once per machine: the Paper Library extension
```

Also install [vscode-pdf-viewer](https://github.com/anton-dergunov/vscode-pdf-viewer), which opens PDFs and makes page citations in the chat clickable; its README has the setup.

The working layout is the PDF on one side and the Claude Code panel on the other. What you will use daily:

| To | Do |
|---|---|
| Open a paper by its title | ⌥⌘P (Ctrl+Alt+P), then type words from the title or topic. Enter opens the PDF. |
| Switch between a paper's PDF, Markdown and note | **Paper Library: Reveal in Library** from the command palette, then Enter. |
| Jump to the page an answer cites | Click the citation in the chat, such as "p. 7, Table 2". |
| Browse by topic | Open `library/README.md` in the Markdown preview (⇧⌘V) and follow the links. |
| Search the text of all papers | **Paper Library: Search Library Text**. |

[Working in VS Code](vscode.md) has the details.

## 5. Look at a paper

```bash
paperlib info 2405.14734                 # an arXiv id or URL
paperlib info direct preference          # or words from a title
```

In a session: `/paper-info 2405.14734`.

For a paper **in the library** it answers at once, with no network: where the Markdown, the note and the review are, and the summary.

For a paper **not in the library** it reports:

- when it was submitted, its venue and citation counts, with a grade of how fast it is being cited;
- which papers, notes and reviews in the library name it;
- the folder it would be filed in;
- what it proposes, what kind of paper it is, and how it differs from the nearest papers in that folder.

It reads the abstract and public records, not the paper. It never says whether to add the paper: that is your decision. A paper you skipped earlier is answered with your reason.

| Option | Effect |
|---|---|
| `--facts` | Skips the two model requests: metadata, citations and mentions only, in about two seconds. |
| `--abstract` | Shows the abstract too. |
| `--again` | Ignores the saved answer and looks the paper up afresh. |
| `--json` | One JSON object per paper, for another program. |

## 6. Add papers

```bash
paperlib add 2305.18290                                  # a model picks the folder and writes the summary
paperlib add 2305.18290 --dry-run                        # show the folder and the summary, add nothing
paperlib add-arxiv 2305.18290 llm/post-training          # or name the folder yourself
paperlib add-pdf ~/Downloads/paper.pdf ml/classics --title "The Exact Title"
paperlib add-web https://distill.pub/2017/momentum/ deep-learning/optimization
```

Each one writes the PDF, the Markdown and the figures. `paperlib add` also writes the summary, rebuilds the indexes and runs the check. After the other three, do that yourself:

```bash
paperlib build-index && paperlib check
```

Which to use:

| Situation | Use |
|---|---|
| One or a few arXiv papers | `paperlib add <id> ...` (several ids at once are fine). It never creates a folder; a paper that fits none is reported and left out. |
| A title, a paper that needs a new folder, a PDF or web article that should get a summary | `/add-paper <link, id, title or file>` in a session. It proposes a new folder and waits for you. |
| Links collected over time | Paste them into `INBOX.txt`, one entry per paragraph, then `/add-paper inbox`. It proposes a folder for each and waits. |
| Tens of papers in an area | `/expand-library <topic>`: it proposes a numbered reading list, you strike what you don't want, the rest are added. Struck papers go to `catalog/skipped.yaml` and are not proposed again. |

Notes:

- **A paper already in the library, or skipped earlier, is not added again.** To add a skipped paper after all, remove its entry from `catalog/skipped.yaml` first.
- **A PDF is copied**, so the file in `Downloads` stays. Some publishers block scripts (ACM, Wiley, Springer, SSRN, OpenReview): download the PDF in a browser and use `add-pdf`.
- **arXiv papers are converted from arXiv's HTML.** A paper without one is converted from the PDF, which is slower and less exact; its `source` is then `pdf-text`. If the Markdown of an arXiv paper looks like a conference template instead of the paper, add it again with `--from-pdf --force`.

## 7. Remove, move and reorganise

```bash
paperlib remove 2305.18290 --reason "not for me"     # by arXiv id, title words or path
paperlib move "library/llm/memory/Zep. A Temporal Knowledge Graph.md" llm/memory/graphs
paperlib rename                                       # after correcting a title
```

**Remove** lists what it will delete (the Markdown, the figures, the PDF, the agent's note, its conversion problems) and asks before it does. It keeps your own overview note, and it names the reviews and notes that still mention the paper. With `--reason` the paper is recorded in `catalog/skipped.yaml`, so it is not proposed again; leave the reason out for a duplicate or a mistake. The PDF is not in git, so highlights in it are gone for good.

Adding a paper is also how you try one: add it, read a little with the agent, and remove it if it is not worth keeping.

**Move** takes the Markdown, the figures and the PDF together and rebuilds the indexes. The target folder must be declared in `catalog/topics.yaml`.

**Reorganise** a folder that has grown too large with `/reorganize <topic>`. It proposes splits, merges and moves with reasons, and changes nothing until you choose.

## 8. Read a paper with the agent

1. **Before reading:** `/overview <title words>` writes a note to read in 3–5 minutes: the setting, the idea, why it works, the evidence, and what is new against your library. It goes to `overview_dir`. For many papers this is all the reading they need.
2. **While reading:** open the PDF, and ask in the Claude Code panel. For example: "explain eq. 4 without the notation", "how is this different from DPO", "what do my papers say about temporal knowledge graphs". Answers cite the page and the table, and in VS Code the citation opens the PDF there.
3. **What is kept:** when a session settles something worth keeping, the agent adds it to the Q&A of `notes/<Title>.md`. Later sessions read that note before the paper.

**On a tablet:** read the PDF from the synced folder in any PDF app, and reach the session with Remote Control: run `claude remote-control` in the library on your computer and open it from the Claude app.

## 9. Write a literature review

A review covers one topic folder and everything under it, and is written to `reviews/<topic>.md`. Below, `<topic>` is a folder such as `llm/memory`.

It takes two steps. Each can be run on its own day.

### Step 1. Read the papers into notes (terminal)

```bash
paperlib review-status <topic>            # how many papers have no note yet
paperlib read <topic> --limit 30          # read 30 of them; run again to continue
paperlib review-status <topic>            # done when no paper is "not read"
```

- **Each paper is one request**, read in full by Opus, and the result is `notes/<Title>.md`. A paper costs about 35K tokens, so about 100 papers can use up a usage window. `--limit` keeps a run within a budget; leave it out to read everything that is left.
- **It is resumable.** Papers that already have a note are skipped, so the same command continues after any stop.
- **Exit code 3** means the usage limit was reached. The message gives the reset time; the notes written so far are kept.
- **`--jobs N`** sets how many papers are read at once (default 4).
- **Results in an appendix.** When a note says the paper's main numbers are in an appendix, read that paper again with the appendix: `paperlib read --redo --appendix <paper.md>`.
- **A focus file** is optional: 5 to 10 lines on the themes the review will have and what it will ask of each paper, passed with `--focus <file>`. `/literature-review read <topic> 30` in a session drafts one from the folder's summaries and then runs the same command.

Each line the command prints ends with how many conversion problems the reader found in that paper; they are recorded in `issues/` (section 10).

### Step 2. Write the review (a new session)

```
/literature-review <topic>
```

It writes the review from the notes: the kinds of approaches, a map of the papers, how the field got here, the findings with the strength of their evidence, where the papers disagree, and what to do in practice. Use a new session, because this one loads every note, and discuss or correct the review in another new session for the same reason.

### Other ways to run it

| To | Run |
|---|---|
| Do both steps in one go | `/literature-review <topic>`. It reads what is missing, then writes. Good for a small folder. |
| Update a review after adding papers | `paperlib read <topic>`, then `/literature-review update <topic>`. |
| See which reviews are behind | `paperlib review-status`, or `/literature-review status`. |

## 10. Check the library's health

```bash
paperlib check                       # is everything consistent?
paperlib review-status               # which reviews miss papers or have broken links?
paperlib issues --counts             # which conversion problems are known, by cause?
paperlib symptoms --counts           # how many papers show a known conversion flaw?
```

| Command | What it tells you |
|---|---|
| `paperlib check` | Every paper has its fields, its PDF and its figures; every paper is in a declared folder; no PDF is in git; notes, issues, reviews and the catalog name papers that exist; links in reviews resolve. It prints the problems and exits non-zero on any. Run it after every change. |
| `paperlib build-index` | Rebuilds the indexes and the agent guide. Run it before `check` after adding, moving or removing by hand, or after editing `catalog/`. |
| `paperlib review-status` | For each review, the papers of its area it does not cover and its broken links. `paperlib review-status <topic>` adds which papers have no note and counts the conversion problems. `--fix-links` repairs links to papers that moved. |
| `paperlib issues` | The conversion problems recorded in `issues/`, one line each, those with key content broken first. Give a topic or a paper to narrow it; `--counts` totals them per ticket. |
| `paperlib symptoms` | Papers whose Markdown shows a flaw the converter now fixes, one line each. `--counts` gives totals per flaw, `--katex` lists equations that cannot be drawn, `--pages` lists papers missing three or more PDF pages. |

To repair a paper:

```bash
paperlib reconvert <paper.md>                            # convert it again with the current converter
paperlib reconvert --pdf-text --inline-math <paper.md>   # the same for a paper converted from its PDF
```

The summary and the PDF are kept. A paper you corrected by hand is skipped when the correction is marked `<!-- hand-edited -->`.

### Conversion problems

Problems are fixed where they start, in the converter, so that one fix repairs every paper with the flaw and every paper added later. The library records them; the engine holds what to do about them.

- **Recorded.** While reading, the reader writes each problem it finds to `issues/<Title>.yaml`: where it is, what is broken, and whether the paper's findings rest on it (key content). The agent records one you notice in a session with `paperlib issues add <paper.md> <kind> "<what>" --where "p. 4, Table 2"`. `paperlib info` shows a paper's open problems.
- **Filed under tickets.** A ticket is one cause, a file in the engine's `tickets/`, labelled with what it takes: an engine fix, a reconversion, notes read again, or a hand edit. `paperlib tickets` lists them with the papers each touches. `/triage-conversions` files new problems under tickets and proposes which to fix together.
- **Fixed.** `/fix-conversions <ticket> ...` fixes tickets in the converter, checks the fix on a few papers, and gives the commands for the rest, to run overnight:

```bash
caffeinate -i nice -n 19 paperlib reconvert --issue <ticket> --jobs 1 --state ~/.cache/papers/reconvert-<ticket>.jsonl
paperlib issues close <ticket> --state ~/.cache/papers/reconvert-<ticket>.jsonl   # then read again the notes it names
```

Only notes whose key content was broken are read again. A paper is edited by hand only when the problem is isolated or no program could fix it.

## 11. Commands and skills

In a terminal (`paperlib --help` has the full list):

| Command | Does | Section |
|---|---|---|
| `init` | Creates or refreshes a library | [2](#2-create-a-library) |
| `install-vscode`, `setup-equations` | One-time installs | [1](#1-install), [4](#4-set-up-vs-code) |
| `info` | A quick look at a paper | [5](#5-look-at-a-paper) |
| `add`, `add-arxiv`, `add-pdf`, `add-web` | Add a paper | [6](#6-add-papers) |
| `remove`, `move`, `rename` | Take out, refile, rename | [7](#7-remove-move-and-reorganise) |
| `read` | Reads papers into notes | [9](#9-write-a-literature-review) |
| `review-status` | Review coverage and unread papers | [9](#9-write-a-literature-review), [10](#10-check-the-librarys-health) |
| `build-index`, `check` | Rebuild the indexes, check consistency | [10](#10-check-the-librarys-health) |
| `issues`, `tickets`, `symptoms`, `reconvert` | Find and repair conversion problems | [10](#10-check-the-librarys-health) |

In a Claude Code session:

| Skill | Does | Section |
|---|---|---|
| `/paper-info` | A quick look at a paper | [5](#5-look-at-a-paper) |
| `/add-paper` | Adds a paper from any source, or the inbox | [6](#6-add-papers) |
| `/expand-library` | Finds and adds the papers missing from an area | [6](#6-add-papers) |
| `/reorganize` | Proposes splits, merges and moves of folders | [7](#7-remove-move-and-reorganise) |
| `/overview` | A short note to read before a paper | [8](#8-read-a-paper-with-the-agent) |
| `/triage-conversions` | Files conversion problems under tickets, proposes what to fix | [10](#10-check-the-librarys-health) |
| `/fix-conversions` | Fixes tickets in the converter | [10](#10-check-the-librarys-health) |
| `/literature-review` | Writes or updates the review of an area | [9](#9-write-a-literature-review) |

The skills are available in a session opened on the library. To use them from other folders, install them as a plugin: `/plugin marketplace add anton-dergunov/agentic-paper-library`.
