# Experiment · how many tokens do the library's instructions cost, and can they be cut without losing what they say?

**Question.** Every session in a library loads the guide, the library's `AGENTS.md` and the skill list before it does anything, and re-reads them on every turn; every `paperlib read` request carries the reading instructions and a list of the area's papers. How much of that is needed? Can it be cut, and does anything get worse?

**Status.** Measured 7 Oct 2026, with Opus 5.5's token counts, on the author's library; core run and follow-up. The library's share of a session's starting context fell from 8.3K to 5.5K tokens (−33%; the guide −32%, the library's `AGENTS.md` −49%), and over ten paired sessions the after sessions processed 16% fewer tokens. A `paperlib read` request lost 830 fixed tokens and now reads its instructions and related list from the prompt cache after an area's first paper: six papers cost 24% less (21% on the input side). Quality held: the notes had 4 errors against 5 and 4 for the two before runs, with no point missed, and every rule check that measures the instructions passed in all 20 sessions. The experiment cost $18.92: $6.99 for the core, $11.93 for the follow-up.

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

### Follow-up: running it, and resuming after a usage limit

The follow-up adds:
- a second run of each session task, for a noise floor;
- the other three papers of reading-models (Phi-4, DeepSeek-V2, Command A);
- the synthesis question of review-usefulness;
- `/reorganize llm/text-analytics` (a proposal only);
- `/literature-review status`, and `read experimentation-and-metrics/variance-reduction 1`.

One command runs all of it, and is run again until it says `done`:

```bash
python3 follow_up.py            # work folder ~/.cache/papers/prompt-trim, library ~/papers
```

**State lives in the work folder,** not in a session: the old engine (`engine-before/`, a `git archive` of a67d5b4 plus the engine's untracked `AGENTS.md`), the library's old `AGENTS.md` (`papers-before/`), the library copies with a pristine twin each, a mini library and cache per reading condition, and a `paperlib` shim per condition.

**Each piece is idempotent:**
- a paper with a note is not read again;
- a judged paper is not judged again;
- a session that succeeded is not run again;
- before every session its copy is reset to the pristine twin, so a repeat or a retried run never sees an earlier run's work.

**At a usage limit** a step stops with exit code 3 and says so. Switch account (`/login`) or wait for the reset, and run the same command again.

Sessions run each condition's own engine through the shim and their own cache. In the core run, the session's `paperlib` was the current engine in both conditions; that only matters for `/literature-review read`, whose inner request is itself the reading prompt.

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

Six papers, the first three in the core run and the last three in the follow-up:

| Condition | Errors (6 notes) | Points missed, of 60 | Digest bullets (≤ 20 a note) | Note length | Output tokens | Cost, 6 papers |
|---|--:|--:|--:|--:|--:|--:|
| before | 5 | 1 | 122 (3 notes over 20) | 43.3K chars | 41.2K | $2.51 |
| before, again | 4 | 0 | 119 (3 notes over 20) | 41.2K chars | 41.6K | $2.52 |
| after | 4 | 0 | 109 (none over 20) | 41.9K chars | 29.9K | **$1.92** |

- **Related papers.** They overlap as much between before and after as between the two before runs. Summed over the six papers, after shares 19 related papers with the first before run and 18 with the second, and the two before runs share 19 ([`judge.txt`](results/judge.txt)).
- **Conversion lines.** All three conditions flag Command A's broken Tables 7 and 8 as `key-content-broken`, and none flags Phi-4 or DeepSeek-V2. The judge's remaining remarks are the same in all three: cosmetic flaws, such as fused footnote markers or a scrambled author block, that the reading prompt says to call `ok`.
- **Where the 24% comes from.**
  - **Input, about 21% of its cost:** each request lost the 760 tokens of the user's CLAUDE.md, and from an area's second paper on, its instructions and 39-paper list came from the cache.
  - **Output:** the after reads used fewer output tokens on every paper, for notes of the same length that keep to the 20-bullet limit, so the difference is thinking. Why the system-prompt layout thinks less is not known; it is observed on six of six papers, but not designed.

### Sessions

Seven tasks, before and after, in copies of the library. The question, `/overview` and `/add-paper` ran twice (core and follow-up); the other four ran once (follow-up):
- the synthesis question "What does current research say about managing obsolete facts in LLM memory?" (Opus);
- `/reorganize llm/text-analytics`, where the proposal is the whole task (Opus);
- `/literature-review status`;
- `/literature-review read experimentation-and-metrics/variance-reduction 1`.

[`sessions.tsv`](results/sessions.tsv) has every check, and [`answers/`](results/answers/) every final answer.

- **Every check passed in both conditions,** 124 in all, except one that failed in both.
  - **The question:** each run read Zep's note, cited pages with `pdf.invalid` links and `page=`, gave 71.2% against 60.2% for full context, and opened no PDF.
  - **`/overview`:** the format and the skill's steps held in all four runs.
  - **`/add-paper`:** the steps held in all four runs, and every run filed MemOS in `llm/memory/agent`.
  - **Synthesis:** both sessions grepped the review, read slices of it rather than the whole file, opened notes and papers before stating numbers, and said where a point rests on the review alone. The after answer also points out a slip in the review.
  - **`/reorganize`:** both proposed the same move (a paper on LLMs as annotators to `data-centric-ml/labels-and-annotation`) and the same rescope, moved nothing, and weighed BERTopic against the "general before LLM-specific" rule, which now lives in the skill rather than the guide. Before declined to move it; after proposed it as optional, with the downside.
  - **`/literature-review status`:** ran `review-status` and changed nothing.
  - **`/literature-review read`:** both sessions ran `review-status`, wrote the focus file and started `paperlib read … --focus … --limit 1` in the background, as the skill says. Neither wrote a note: a headless `claude -p` session ends when its turn does, which stops the background read. In an interactive session the agent is woken when the read finishes. The inner read is the reading prompt, measured above.

| Task | Runs | Input processed, before → after | Price, before → after |
|---|--:|--:|--:|
| question | 2 | 441K → 468K | $0.64 → $0.64 |
| `/overview` | 2 | 843K → 818K | $1.07 → $1.01 |
| `/add-paper` | 2 | 672K → 566K | $0.46 → $0.44 |
| synthesis | 1 | 575K → 434K | $0.64 → $0.59 |
| `/reorganize` | 1 | 415K → 230K | $0.56 → $0.42 |
| `/literature-review status` | 1 | 283K → 171K | $0.30 → $0.23 |
| `/literature-review read` | 1 | 231K → 217K | $0.25 → $0.23 |
| **all ten pairs** | | **3.46M → 2.90M (−16%)** | **$3.92 → $3.56 (−9%)** |

A single pair differs mostly by the path a session takes: one or two turns more, or a file read twice. Over ten pairs, the after sessions took 74 turns against 79, and processed 39K tokens a turn against 44K. The price falls less than the tokens, because most of them are cache reads at a tenth of the price.

## Conclusions

1. The guide, the library's `AGENTS.md` and the memory index now cost 3K fewer tokens per session start, re-read on every turn and in every subagent. No rule is lost ([`rules.md`](rules.md)), and over twenty sessions of seven tasks no change was found in what sessions do.
2. `paperlib read` and `paperlib add` no longer send the user's CLAUDE.md files, and they send what an area shares as a cached system prompt. On six papers a read cost 24% less, with notes as good. In a large scope the input saving per paper is larger: about $0.09 of a $0.45 read in `search-and-ranking`.
3. Skill files load only when they run, and splitting them further would cost more turns than it saves, so they were tightened in place.
4. **Limits.**
   - Six papers, and one or two sessions per task and condition. The checks cover the rules these tasks exercise; the others rest on the inventory.
   - The related-list cache saving was measured in a probe and on six papers of one folder, not on a full scope.
   - The lower thinking in after reads is observed, not explained.
   - `/literature-review read` cannot be tested headless as the skill runs it.
