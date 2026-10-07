# Rule inventory

Every rule in the instructions this experiment trimmed: where it was before, and where it is now. "Guide" is `guide/library-guide.md` (rendered into each library as `.claude/library-guide.md`), "AGENTS" is the author's library's `AGENTS.md`, "memory" is that library's Claude Code memory. Rules stated the same way in both places are not listed. Wording changes that keep a rule are not listed either; `git diff` shows them.

## Library guide (loaded in every session in a library)

| Rule | Before | After |
|---|---|---|
| Layout table: where papers, figures, PDFs, indexes, catalog files, inbox, notes, reviews, the reader's notes and the config live | guide | guide |
| A paper's markdown and PDF share topic path and stem | guide | guide |
| Add papers only with paperlib | guide | guide (one line, naming `add-paper`, `paperlib add`, `expand-library`) |
| `add-arxiv` / `add-web` / `add-pdf` syntax and when to use each | guide + add-paper | add-paper |
| `paperlib add` chooses folder and summary, never creates a folder | guide | guide |
| `add-paper` drains the inbox and removes added entries | guide + add-paper | guide (inbox) + add-paper (draining) |
| `expand-library` adds tens of papers via `add-batch` | guide + expand-library | guide (pointer) + expand-library |
| Every add writes both files, the frontmatter and page numbers | guide | dropped: describes what the commands do; their output says it |
| Move only with `paperlib move`; a hand `mv` splits the trees | guide | guide |
| Filenames follow `paperlib filename`; colon becomes ". "; `paperlib rename` re-applies | guide | guide |
| Never put a PDF in git; `check` fails on one | guide | guide |
| Read the markdown, not the PDF; it keeps LaTeX and tables | guide | guide |
| `pdf-text` by layout analysis: check the PDF before quoting an equation or an odd table, say so | guide | guide |
| `pdf-text` from the text layer: unreliable; reconvert with `--pdf-text` | guide | guide |
| `web`: interactive figures missing, PDF is Chrome's print | guide | guide |
| Prefer the local copy to the web | guide | guide |
| Never edit an index; after changes run `build-index`, then `check` | guide | guide |
| Don't re-propose skipped papers; record new skips; remove the entry if the reader changes their mind | guide | guide |
| Prefer a better tool to a workaround; compare on real papers | guide + AGENTS + memory | guide (merged with the next rule) + AGENTS ("installing is fine; say so") |
| Conversion quality before speed; pragmatic only in bulk, say what was traded | guide + memory | guide (merged with the previous rule) |
| Flag broken conversions in the catalog; what "garbled" means; say so when quoting | guide | guide |
| `paperlib read` reports conversion problems; `conversion-issues` copies them; `fix-conversions` reads fixed papers again, sends recurring flaws to the converter, marks `wont-fix` | guide + fix-conversions | guide (pointer to the skill) + fix-conversions |
| `paperlib reconvert` regenerates a body; keeps frontmatter and PDF; refetches at the PDF's version | guide | guide (short) + fix-conversions (full) |
| Hand edits carry `<!-- hand-edited -->`; reconvert skips them | guide + fix-conversions | guide + fix-conversions |
| arXiv downloads are cached; `--jobs N --state`; `--all`; `paperlib symptoms` | guide | fix-conversions |
| Start from the review; the review is a map, not evidence; grep it, don't read it whole | guide | guide (wording kept: tuned by review-usefulness) |
| Append settled cross-paper points to the review's Q&A; offer to update a review after adds | guide | guide |
| `literature-review` writes reviews; `review-status` shows stale ones | guide + literature-review | guide (skill named) + literature-review |
| Check notes and the reader's note before answering about a paper; append settled points to the note's Q&A | guide | guide |
| Frontmatter fields and allowed values; `summary` is one neutral sentence on what the paper does | guide (YAML example) | guide (field list) |
| `type` is set by `/overview` | guide | overview |
| Body: KaTeX math, HTML tables for merged cells, figures in `images/`, `(p. N)` on headings, cite pages that way | guide | guide |
| Notes are flat, named by stem, for agents; written by `paperlib read`, `overview`, any session's Q&A | guide | guide |
| `check` fails on a note whose paper is not in the library | guide | dropped: `paperlib check` reports it with the note's name |
| Note format (header lines, Digest, Related, Q&A) | guide | guide |
| Q&A entries: multi-line, heading with date and question, tables and fenced blocks, mark invented content as ours | guide | guide |
| Q&A entries cost few tokens and are read by the reader too | guide | dropped: rationale |
| `review-status` lists papers without a note | guide + literature-review | literature-review |
| `family`, `evidence`, `conversion` are what reviews group and weigh by; older notes lack them | guide | dropped from the guide: literature-review's write step uses them |
| `key-content-broken`: what it means; check the PDF before leaning on the paper | guide + reading prompt + fix-conversions | guide + reading prompt + fix-conversions |
| `read: skim` vs `full`; open the paper before relying on a skim; `--skims` reads them; no line means full | guide | guide (shorter) |
| Merge into an existing note; never drop its Q&A | guide | guide |
| Topics: lowercase hyphenated paths, declared with a scope; `check` fails on undeclared folders | guide | guide |
| `build-index` creates declared folders in both trees; root README shows counts; folder README lists "Considered, not added" | guide | dropped: describes generated output, which is visible |
| How to file: read scopes; where the reader would look; general before specific (pre-LLM or all-of-ML methods go to the general area) | guide + AGENTS | add-paper, reorganize |
| Structure first; ~20 a folder is a heuristic; split only on a natural division | guide + reorganize | add-paper, reorganize |
| A new folder is the reader's decision: propose it with a scope; add/move refuse undeclared folders | guide + add-paper + reorganize | guide (one line) + add-paper + reorganize |
| Reorganising is expected: use `reorganize` | guide | the skill's description |
| Link a place in a paper with `pdf.invalid`: path, `page` always, `dest` names, `search`, link text style, several links fine, never open a PDF yourself | guide | guide |

## The author's library `AGENTS.md` and memory

| Rule | Before | After |
|---|---|---|
| Who the reader is and their focus areas | AGENTS | AGENTS |
| The engine's location; engine-wide changes go there; the guide is generated | AGENTS + memory (engine-library-split) | AGENTS |
| Run commands as `paperlib <cmd>`; skills are symlinks made by init; converters pinned; measurements go to the engine's experiments | memory (engine-library-split) | guide (commands) + engine `AGENTS.md` (the rest) |
| What the library repository holds; `docs/library.md` | AGENTS | AGENTS |
| PDFs sync to tablets; `pdf/` links there | AGENTS | AGENTS |
| Other places on this machine, and the rules for each (Obsidian: edit only when asked; mirror read only; career read only and sensitive; org files follow their own AGENTS.md) | AGENTS | `docs/places.md`, with a pointer in AGENTS naming each place |
| Installing things is fine; say so | AGENTS + memory (prefer-better-tools) | AGENTS |
| In a skill, do only its steps; report the result and a commit message; caveats only if really wrong; ignore other sessions' untracked papers | memory (skill-runs-lightweight) + overview | AGENTS + overview |
| Never commit; suggest a commit message | AGENTS + global CLAUDE.md | AGENTS |
| The twenty areas follow the org study plans (full list) | AGENTS | `docs/library.md` (already there), pointer in AGENTS |
| Primary folders hold 30–60 papers; others seminal and recent; `curiosities/` for fun | AGENTS | AGENTS |
| General before LLM-specific | AGENTS + guide | add-paper, reorganize |
| Explaining papers: intuition first, what is new, what is outdated, related papers, pages | AGENTS | AGENTS |
| Gemini access through Vertex AI | memory | memory (kept: credentials must not be committed) |

## Skills

| Rule | Before | After |
|---|---|---|
| Read `AGENTS.md` (and the guide) first | 5 skills | dropped: `CLAUDE.md` loads both into every session |
| Paths are defaults; the guide has this library's | 6 skills | 6 skills |
| Descriptions: every trigger phrase | frontmatter | frontmatter, shorter; "fill the gaps in llm/evaluation" and "a year has passed, what's new" generalised to "fill the gaps in X" and "what's new in X" |
| literature-review: reading cost, resumable, spread over sessions, never read with subagents | literature-review | literature-review (pointers to the experiments dropped) |
| overview format: failure modes of earlier drafts | overview/format.md (four bullets of history) | overview/format.md (one paragraph of the lessons) |

## The reading and filing prompts

| Rule | Before | After |
|---|---|---|
| Every rule of `guide/reading-prompt.md` | user message | system prompt, wording lightly tightened |
| The related list leaves out the paper itself | script | the list includes it, so the system prompt is the same for a whole scope; the prompt says to list only other papers |
| The filing rules and the topic tree | user message | system prompt |
| The user's own `CLAUDE.md` files | loaded into every `claude -p` request | not loaded (`CLAUDE_CODE_DISABLE_CLAUDE_MDS`) |
