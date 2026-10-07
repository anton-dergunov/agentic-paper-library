# Experiment · how many tokens do the library's instructions cost, and can they be cut without losing what they say?

**Question.** Every session in a library loads the guide, the library's `AGENTS.md` and the skill list before it does anything, and re-reads them on every turn; every `paperlib read` request carries the reading instructions and a list of the area's papers. How much of that is needed? Can it be cut, and does anything get worse?

**Status.** Measured 7 Oct 2026, with Opus 5.5's token counts, on the author's library. The library's share of a session's starting context fell from 8.3K to 5.5K tokens (−33%; the guide −32%, the library's `AGENTS.md` −49%). A `paperlib read` request lost 830 fixed tokens and now reads its instructions and related list from the prompt cache after the first paper of an area: three papers cost 19% less. Reading notes, a question about a paper, `/overview` and `/add-paper` were as good after as before: the same errors and points in the notes, and every rule check passed in both conditions. The core run cost $6.99.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `guide/library-guide.md`, `guide/reading-prompt.md`, `scripts/paperlib.py` (`ask_model`), `scripts/read-papers.py`, `scripts/add-paper.py`, the skills, and `paperlib init`'s default `AGENTS.md`.

## Method

- **Conditions.** *Before* is the engine at commit a67d5b4 with the library's `AGENTS.md` and memory as they were. *After* is the trimmed engine and `AGENTS.md`.
- **What was trimmed, and how.** Four rules, applied to every file:
  - **Load where needed.** A rule only one workflow uses moved from the always-loaded guide into that skill: the add commands' syntax went to `add-paper`, reconversion details to `fix-conversions`, and "how to file" to `add-paper` and `reorganize`.
  - **Say it once.** Duplicates across the guide, the library's `AGENTS.md`, the skills and the library's memory were removed.
  - **Keep the rule, drop the history.** The exception is wording tuned by an experiment, which stayed verbatim: the "Start from the review" rule and the reading prompt's conversion grading.
  - **No silent loss.** [`rules.md`](rules.md) lists every rule with where it was and where it is now; the few dropped ones say why.
- **Token accounting** ([`count.py`](count.py)). Each file's tokens are the input of a `claude -p --model opus` request holding the file, minus an empty request's. A session's starting context is the input of `claude -p "Reply OK."` with Claude Code's own system prompt and tools, started in a folder holding only the instructions (`CLAUDE.md`, `AGENTS.md`, the guide, the skills), in each condition and in an empty folder. The same script measures the fixed input of a `paperlib read` request under candidate flags.
- **Reading quality** ([`reads.py`](reads.py), [`judge.py`](judge.py)).
  - Three papers of `llm/foundation-models` ([`papers.txt`](papers.txt)): GPT-1 (converted from the PDF), Gemma 3 and OLMo, the three shortest of [`../reading-models`](../reading-models/README.md).
  - Each was read three times, by each engine's own `read-papers.py` in a copy of the folder: before, before again (the noise floor) and after.
  - A blind Opus judge, adapted from reading-models', saw the paper and the three notes in shuffled order. It listed 10 points a note needs, then each note's errors, missed points and whether its `conversion` line is right.
  - The "Related in library" sections are compared by script.
- **Session quality** ([`sessions.py`](sessions.py), [`check.py`](check.py)).
  - Two copies of the library (paper markdown without figures or PDFs, catalog, notes and reviews; built with [`../review-usefulness/copies.py`](../review-usefulness/copies.py)), each with its condition's `AGENTS.md`, its engine's rendered guide and its engine's skills. Their config points the PDF folder and the overview folder into scratch.
  - One `claude -p` session per task and condition:
    - the question about Zep from review-usefulness (Opus);
    - `/overview` of GPT-1 (Opus);
    - `/add-paper 2505.22101` (MemOS; Sonnet, as the skill names).
  - `check.py` grades each session against the rules its task exercises, from the event stream and the files it wrote. The two answers and two overview notes were also compared by hand.
- **Results.** [`results/`](results/):
  - [`tokens-before.tsv`](results/tokens-before.tsv) and [`tokens-after.tsv`](results/tokens-after.tsv);
  - the nine notes in `notes/`, the request logs `reads-*.jsonl`, the judge's findings in `judge/` and [`judge.txt`](results/judge.txt);
  - [`sessions.tsv`](results/sessions.tsv) (checks and tokens), the final answers in `answers/`, and the two overview notes in `overview/`.

  The event streams are not committed: they hold paper text.

```bash
python3 count.py flags results/tokens-after.tsv
python3 count.py files results/tokens-after.tsv guide=<library>/.claude/library-guide.md ...
python3 count.py session results/tokens-after.tsv library=<folder with the instructions>
python3 reads.py <library> <engine> <scratch> <condition> --python <engine>/.venv/bin/python
PAPER_LIBRARY=<library> python3 judge.py
python3 sessions.py build <library> <scratch> before=<old engine>:<old library files> after=<engine>:<library>
python3 sessions.py run <scratch>
python3 check.py <scratch>
```

## Results

### Where the tokens were, and where they are now

Opus 5.5 tokens (about 2.7 characters a token):

| What | Loaded | Before | After |
|---|---|--:|--:|
| Claude Code's own system prompt and tools | every session | 32,494 | 32,494 |
| The library's share of a session's start: guide, `AGENTS.md`, skill list | every session and subagent, every turn | 8,294 | **5,540** |
| of which the guide | | 5,261 | 3,579 |
| of which the library's `AGENTS.md` | | 1,888 | 955 |
| of which the skill list | | 932 | 799 |
| The library's memory index (not in the measured folders) | every session | 262 | 48 |
| `add-paper` skill | when it runs | 1,998 | 1,858 |
| `overview` skill + `format.md` | when it runs | 6,694 | 6,382 |
| `literature-review` skill + `format.md` | when it runs | 10,221 | 10,112 |
| `fix-conversions` skill | when it runs | 2,167 | 2,240 |
| `expand-library` skill + reading-list guide | when it runs | 2,607 | 2,543 |
| `reorganize` skill | when it runs | 968 | 985 |
| Engine `AGENTS.md` (engine sessions only) | engine sessions | 1,693 | 1,827 |
| Fixed input of a `paperlib read`/`add` request, before its prompt | every request | 1,442 | **614** |
| Reading prompt | every read | 1,002 | 988 |

- **The session start.** A main session writes its context to the cache once, at twice the input price, and reads it back on every turn at a tenth. A 10-turn session saves about 2.75K × 2 + 2.75K × 0.1 × 10 ≈ 8K cost-eq; every subagent saves the same again.
- **The skills barely moved, on purpose.** Skill text loads only when the skill runs, and two planned splits were not made:
  - `overview` would have loaded only its paper type's section, about 1K tokens;
  - `literature-review` would have loaded only its mode, 1.5–2.5K tokens.

  Reading the extra file costs a turn, which re-reads the whole context (about 4K cost-eq at 41K tokens), more than either split saves. `literature-review/format.md` was left as it is: it specifies a rare, expensive deliverable, and its 6K tokens are well under 1% of a review run. `fix-conversions` and `reorganize` grew a little, with the rules they took over from the guide.
- **What `claude -p` adds.** Even with `--system-prompt` and no tools, it sends the user's `CLAUDE.md` files, an environment note and the date. Two variables take that from 1,442 to 614 tokens and leave user settings (auth helpers, proxies) alone:
  - `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` drops the CLAUDE.md files;
  - `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` drops the background requests.

  `--setting-sources ''` would reach 432, but it ignores user settings. `--disable-slash-commands` and `--strict-mcp-config` change nothing. `--bare` needs an API key, so it cannot run on a subscription.
- **The related list was paid in full on every read.** `docs/tasks/reading-cost.md` found about 16K fixed tokens per read in a 127-paper scope, most of it the list of the scope's papers with their summaries. That list left out the paper being read, so no two requests shared it. It now includes the paper, and the instructions, the focus and the list form the system prompt, which Claude Code caches. Two requests with `search-and-ranking`'s 12.6K-token system prompt cost $0.101 for the first (cache write) and $0.008 for the second (12,023 tokens read from the cache). `paperlib add` sends its rules and topic tree the same way.

### Reading quality

| Condition | Errors (3 notes) | Points missed, of 30 | Related papers listed | Cost, 3 papers |
|---|--:|--:|--:|--:|
| before | 1 | 1 | 9 | $0.79 |
| before, again | 1 | 0 | 8 | $0.81 |
| after | 1 | 0 | 8 | **$0.64** |

- The related papers overlap as much between before and after as between the two before runs: Gemma 3 lists the same three in all three notes; OLMo's after note lists 5, all 5 among the first before note's 6 and 4 among the repeat's 5; GPT-1 lists none in any.
- The judge's remarks on the `conversion` lines are the same in all three conditions: each misses cosmetic flaws (fused footnote markers, a scrambled author block), which the reading prompt says to call `ok`.
- After cost 19% less: each request lost the 760 tokens of the user's CLAUDE.md, and from the second paper on, its 5K-token instructions and 39-paper list came from the cache.

### Sessions

All 48 checks passed, 24 in each condition ([`sessions.tsv`](results/sessions.tsv)):
- **Question about Zep:** it read Zep's note, cited pages with `pdf.invalid` links carrying `page=`, gave 71.2% against 60.2% for full context with gpt-4o, and did not open a PDF.
- **`/overview`:** the note was in the overview folder, with the frontmatter in order, the callout, the method's eight subsections in order and no page references; `set-type` was run, the note's Q&A was kept, and the report was the link and a commit message, without rebuilds or `git status`.
- **`/add-paper`:** lookup, topics read, `add-arxiv`, `set-summary`, `build-index` then `check`, a commit message and no commit. Both filed MemOS in `llm/memory/agent`, and both saw that `check` fails in a copy without figures and PDFs and said why.

By hand, the two answers give the same numbers, pages and links; the after answer adds the knowledge-update breakdown and a note that the evidence is thin. The two overview notes have the same frontmatter, sections and length.

| Task | Condition | Input processed | Output | Turns | Price |
|---|---|--:|--:|--:|--:|
| question | before / after | 223K / 215K | 4.0K / 4.3K | 8 / 8 | $0.33 / $0.33 |
| `/overview` | before / after | 402K / 450K | 6.3K / 5.5K | 10 / 10 | $0.56 / $0.53 |
| `/add-paper` | before / after | 355K / 225K | 2.3K / 1.7K | 8 / 6 | $0.22 / $0.24 |

Single sessions differ by more than the start-context saving: the path a session takes (6 or 8 turns, a paper read once or twice) decides its tokens. The saving per session is the accounting's 2.75K per turn, not these totals.

## Conclusions

1. The guide, the library's `AGENTS.md` and the memory index now cost 3K fewer tokens per session, re-read on every turn and in every subagent, with no rule lost ([`rules.md`](rules.md)) and no change found in what sessions do.
2. `paperlib read` and `paperlib add` no longer send the user's CLAUDE.md files, and send what is shared by an area as a cached system prompt. On three papers the reading cost 19% less with notes as good; in a large scope the saving per paper is larger (about $0.09 of a $0.45 read in `search-and-ranking`).
3. Skill files load only when they run, and splitting them further costs more turns than it saves; they were tightened in place.
4. Limits: three papers and one session per task and condition. The checks cover the rules those tasks exercise; the others rest on the inventory. The related-list cache saving was measured in a probe and on three papers, not on a full scope.
