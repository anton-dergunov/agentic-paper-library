# Experiment · page citations that stay plain text

**Question.** The guide asks an agent to make a citation a link that opens the PDF at the page. In the reader's chats, the lead citation of each point is a link, but passing ones stay plain: "the judge is described on p. 5", "Table 6 on p. 20", "Fig. 10 (p. 20)", "Design results, p. 8–10". Can the guide get more of them linked without pushing the agent to cite more, or spending more tokens and time on an answer? Can the reader's app link the rest at no cost?

**Status.** Measured 31 Oct 2026 on Haiku 5.5 and Sonnet 5.5, 7 questions a run.
- **Haiku linked 27% of its page citations with the guide as it was** (3 runs). Answers were all or nothing. "Which parts should I read" answers had no link in 4 of 6, while the KV-cache question, which asks for links, linked everything.
- **One line early in the guide raised this to 47%** (3 runs). Under "Cite pages … "p. 7, Table 2"" it adds "in an answer to the reader, as a link (below)". Reading-guide answers with a link went from 2 of 6 to 5 of 6. Output tokens and time did not rise. The line costs 16 tokens of the guide.
  - A fuller draft got 53%, within the runs' noise (25% to 70% for the same guide). It also widened the link section to passing mentions and ranges, and said a range needs no `locate`. Those sentences alone got 34% over 2 runs, and they cost 45 tokens more.
- **Sonnet links what it has run `locate` on and leaves pages to read plain**: 43% before, 51% with the fuller draft (1 run each, $1.17 a run).
- **carrel's fallback links the rest at no cost.** It makes a plain citation in an answer a link to the page of the paper asked about (`page-links.js`). Over all 91 answers, it linked 507 of 525 plain citations, none of them to the wrong paper.
  - It skips an answer that links two papers.
  - It also skips a citation whose sentence names another library paper just before it. That catches the 4 citations of another paper that it would otherwise have linked ("FASTopic paper, p. 6–7"). It also leaves 3 right ones plain, where "Orca", a library paper's name, is in the same row.
  - Over the reader's chats since 26 Oct it adds 20 links, all right, among them every citation the screenshot that prompted this left plain.

**The line shipped in the guide, and the fallback in carrel.** The experiment cost $3.25 (11 Haiku runs at $0.08, 2 Sonnet runs at $1.17, token counts).

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), the guide's "Paper files" and "Linking to a place in a paper", carrel's `src/carrel/static/page-links.js`.

## Method

- **The library.** [`setup.sh`](setup.sh) copies the 8 papers of [`papers.txt`](papers.txt) into a scratch library, with their notes, the catalog, the reviews and the reader's `AGENTS.md`. The PDFs are copied once outside it, and each copy links that folder as its `pdf_root`, so `paperlib locate` prints library-relative links. (In [`latex-math`](../latex-math/README.md) each PDF was a symlink, and one answer's links came out absolute.)
- **Runs.** [`run.sh`](run.sh) asks each of the 7 questions in a fresh session, in its own clone of the library, with an engine's guide rendered into it, through `claude -p --output-format stream-json`.
- **Questions.** All but one come with carrel's context line, `[Reading <paper>, page N]`:
  - the three LongMemEval questions of the chat that prompted this, as the reader asked them ("which parts I need to read", S against M, chain-of-note);
  - two more from the reader's chats where citations stayed plain (CompleteP's main idea, a default topic model from a survey);
  - JudgeBench, in the same shape as the first;
  - the KV-cache question of `latex-math`, which names no paper and asks for links.
- **Guides.**
  - `base`: the guide at commit `03c9d0e`;
  - `new`: the link section widened to passing mentions and ranges, a range linking its first page, and no `locate` for a page or range to read;
  - `new2`: `new` plus the line under "Paper files" (with a markdown link to the section, later written as "(below)", 16 tokens fewer);
  - `early`: that line alone, as shipped.
- **Counts.** [`count.py`](count.py) counts, in each answer's text, outside code:
  - page citations ("p. 7", "pp. 8–10", "page 7");
  - those in a `pdf.invalid` link's text, and those right beside one ("**p. 5–6** ([p. 5](…))", or a quoted phrase as the link and its page after it);
  - links with `rect`, `locate` calls, output tokens, cost and time.
  
  "page 6" in "I'll check what page 6 says" counts too, so no answer reaches 100%.
- **The fallback.** [`fallback.mjs`](fallback.mjs) runs carrel's matcher on each answer's markdown, its code and links taken out, with the library's paper names for the guard. It reports what it links ([`fallback.tsv`](results/fallback.tsv)) and lists each link with the words before it ([`fallback-links.tsv`](results/fallback-links.tsv)). The list was read through, and searched for the names of the other papers in the copy and of the other works the answers name. It was also run on the reader's chats since 26 Oct; that list is not committed.
- **Tokens.** The guide before and after, counted with [`../prompt-trim/count.py`](../prompt-trim/count.py) on Haiku 5.5 ([`tokens.tsv`](results/tokens.tsv)).
- **Results.** [`counts.tsv`](results/counts.tsv), and every answer's text in [`results/answers/`](results/answers/). The sessions' streams are not committed: their tool results hold the papers' text.

```bash
LIBRARY=~/papers WORK=<scratch> ./setup.sh
WORK=<scratch> ./run.sh base-haiku-1 <engine at 03c9d0e> haiku     # and so on for each label
python3 count.py <scratch>/runs [--plain] [--export results/answers]
node fallback.mjs <carrel> <library> runs <scratch>/runs [--list]
```

## Results

### The guide

| Guide | Model | Runs | Citations | Linked | Answers with a link | Reading-guide answers with a link | Output tokens | Seconds |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| base | Haiku | 3 | 216 | **27%** (31, 31, 19) | 12 of 21 | 2 of 6 | 98,003 | 714 |
| new | Haiku | 2 | 128 | 34% (44, 24) | 6 of 14 | 0 of 4 | 67,688 | 449 |
| new2 | Haiku | 3 | 212 | 53% (46, 70, 43) | 18 of 21 | 4 of 6 | 101,305 | 624 |
| **early** | Haiku | 3 | 195 | **47%** (60, 59, 25) | 14 of 21 | 5 of 6 | 93,522 | 609 |
| base | Sonnet | 1 | 68 | 43% | 7 of 7 | 2 of 2 | 22,863 | 324 |
| new2 | Sonnet | 1 | 53 | 51% | 6 of 7 | 2 of 2 | 18,755 | 296 |

- **Why the line works.** The guide said how to cite ("p. 7, Table 2", plain) 40 lines before it said to link. The notes an agent reads first cite plain "(p. N)" too, and an answer copies their style. Saying "as a link" where the citation style is set reaches the answers that never got to the link section. Widening the link section itself did nothing measurable.
- **What stays plain:**
  - pages to read ("pp. 4–6", "p. 11 onward");
  - a page mentioned in passing in a sentence about something else;
  - pages taken from the note without opening the paper.
  
  Sonnet links what it located (60 of its 61 links carry a rectangle) and writes pages to read as plain text.
- **No extra cost seen.** Output tokens and seconds vary more between runs than between guides. `locate` calls stayed at 1–4 a run for Haiku. Links are long (a percent-encoded path), so more links do cost output tokens. The fallback adds links without that cost.

### The fallback

| Guide | Model | Plain citations | Linked by carrel |
|---|---|--:|--:|
| base | Haiku (3 runs) | 158 | 157 |
| early | Haiku (3 runs) | 106 | 97 |
| new2 | Haiku (3 runs) | 108 | 105 |
| new | Haiku (2 runs) | 85 | 84 |
| base, new2 | Sonnet | 68 | 64 |

- **How it finds the paper.** It uses the paper the question was asked about, and only when every link in the answer goes to it. When the question names no paper, it uses the one paper the answer links. Those left unlinked are in answers that link two papers (the KV-cache question), or are named for another paper.
- **What it adds.** A page, a range's first page, and a named destination from the label: "Table 6 on p. 20" → `dest=table.6&page=20`, "§5.2–5.4, p. 8" → `subsection.5.2`. A LaTeX paper's destination finds the table even where the cited page is wrong. In the screenshot's chat, Table 6 is on p. 21, not p. 20.
- **The guard.** It looks back 40 characters in the citation's sentence for another library paper's short name: the title before its colon, if three words or fewer. In the 91 answers that skipped all 4 wrong-paper citations and 3 right ones.
- **The reader's chats** since 26 Oct: 20 links added, all to the right paper, and 1 kept plain ("the LongMemEval result on p. 7" in a chat about Zep). Most of those answers already linked everything, or linked two papers.
- **In carrel.** The added links look like the agent's own and open the PDF the same way. Checked on the screenshot's chat drawn in WebKit, in both themes: 16 links added.

## What is not measured

- **Opus**, the reader's usual model. In the reader's chats since 26 Oct it linked about 9 in 10 citations already.
- **Sonnet with the line alone.** Sonnet ran only `base` and `new2`, one run each.
- **Claude Code's panel in VS Code**, where nothing can add links after the answer. There, only the guide's line helps.
- **Answers about several papers.** carrel leaves them as the agent wrote them. Linking each plain citation to the paper of the nearest link before it might work, but it was not tried.
