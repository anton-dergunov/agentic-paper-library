# Experiment · where do the tokens of a literature review go?

**Question.** Writing a review with the `literature-review` skill used up a 5-hour usage window every time, whatever the size of the area. Which step spends the tokens, what is lost when a run is cut off, and what can be saved without reading the papers less carefully?

**Status.** Measured 5 Oct 2026 on the transcripts of the first five reviews (39 to 110 papers each). The reading agents take 70–80% of a run, and about two thirds of an agent's cost is re-reading its own context: papers it has already finished, sent again with every later request. Interruptions lost little reading, but one run paid 15% extra to re-cache, and the first two runs left half their papers without a note.

**Serves.** [`docs/design.md`](../../docs/design.md), and the `literature-review` skill.

## Method

- **Runs.** The first five reviews of the author's library, written 1–5 Oct 2026 with Opus 5.5 in the main session and in every reading agent: `llm/memory` (70 papers, 7 agents), `llm/personalization` (70, 6), `llm/evaluation` (109, 10), `llm/post-training` (110, 11) and `llm/foundation-models` (39, 4). Each agent read a batch of 10 to 15 papers, about a third in full and the rest as skims, and wrote a section per paper to a batch file and a note per paper.
- **Source.** Claude Code's session transcripts: one JSON-lines file per session, and one per subagent. Each model request records its input tokens, the tokens written to the prompt cache, the tokens read from it, and its output tokens. Usage is repeated on every line of a message, so it is counted once per message id.
- **Cost-eq.** Tokens weighted by the API's price ratios: uncached input 1, cache read 0.1, cache write 1.25 (subagents, 5-minute cache) or 2 (main session, 1-hour cache), output 5. How a subscription's usage limit weights the same tokens is not published, so cost-eq approximates what the limit counts.
- **Output is estimated.** The logged output tokens of subagents are unreliable (some agents that wrote four notes show 600), so output is estimated from the length of the text and tool input at 3.6 characters a token. Thinking is not in the transcripts and is not counted, for agents or the main session.
- **Re-caching.** Tokens written to the cache by the first request after a pause longer than the cache's life (5 minutes for a subagent, an hour for the main session): context that was cached before the pause and had to be written again.
- **Apparatus.** [`measure.py`](measure.py) sums a run and each of its agents; [`trace.py`](trace.py) lists one agent's requests with the context size of each.

  ```bash
  python3 measure.py ~/.claude/projects/<project> memory=<session-id> ... > runs.tsv
  python3 trace.py ~/.claude/projects/<project>/<session-id>/subagents/agent-<id>.jsonl
  ```
- **Results.** [`runs.tsv`](runs.tsv) (per run, then per agent) and [`trace-foundation-models-batch-01.tsv`](trace-foundation-models-batch-01.tsv) (one agent, 45 requests). The transcripts are not committed.

## Results

### Where the tokens go

| Run | Papers | Agents | Agents, cost-eq | Main session, cost-eq | Cost-eq per paper |
|---|---|---|---|---|---|
| memory | 70 | 7 | 11.1M | 3.3M | 206K |
| personalization | 70 | 6 | 9.8M | 2.0M | 169K |
| evaluation | 109 | 10 | 7.7M | 2.7M | 95K |
| post-training | 110 | 11 | 11.1M | 2.4M | 123K |
| foundation-models | 39 | 4 | 6.0M | 1.7M | 197K |

The main-session column covers the whole session, including the conversation about the review after it was written.

Inside the agents, summed per run:

| Run | Written to cache | Read from cache | Output (est.) | Largest context, mean | Requests per agent |
|---|---|---|---|---|---|
| memory | 3.80M | 57.7M | 0.12M | 288K | 50 |
| personalization | 2.22M | 64.0M | 0.12M | 310K | 57 |
| evaluation | 2.43M | 38.0M | 0.17M | 242K | 27 |
| post-training | 3.08M | 58.9M | 0.27M | 295K | 31 |
| foundation-models | 1.53M | 33.8M | 0.14M | 382K | 38 |

- **An agent's context only grows.** It starts at 35K tokens (system prompt, tool definitions, the library's instructions) and ends at 200–480K, with every paper it has read still in it. Each request sends all of it again. The agent in the trace read 10 papers in 45 requests: 483K tokens were written to the cache once and 12.8M were read from it. In cost-eq that is 0.60M for writing, 1.28M for re-reading and 0.18M for output.
- **A paper takes 4 to 5 requests.** Agents read with `Read` in slices of 100 to 400 lines, with `sed` ranges, and with their own `perl` one-liners that strip link targets and `<sup>` tags first. Each request costs a tenth of the whole context.
- **The papers themselves are the smaller part.** Main text up to the references is 46–62% of a paper file by area (the rest is references and appendices, which agents mostly skipped by offset); link targets and inline tags are about a tenth of the main text.
- **The evaluation run was the cheapest per paper** because three quarters of its papers were skims and its agents made about half as many requests.
- **Writing is 20–30% of a run.** The main session reads the batch files (about 100K tokens for 39 papers) and writes 9,000 to 21,000 words. It never reads the papers, so the writing does not depend on being in the same session as the reading.

### What an interruption cost

| Run | The limit hit | On "continue" | Lost |
|---|---|---|---|
| memory | all 7 agents, 5 minutes after they started | all 7 were resumed with their context, 8 minutes later | 1.82M tokens written to the cache a second time: the agents' cache had expired. About 15% of the run |
| personalization | 1 agent of 6, with 12 of its 15 papers done | resumed for the last 3 | nothing |
| evaluation | 5 agents of 8 | the papers left were given to 2 new agents | the reading of the papers in progress |
| post-training | all 11 agents; later the main session, while writing | agents resumed 2 minutes later, cache still alive; the main session resumed 6 hours later | 0.38M tokens re-cached by the main session, about 6% of the run |
| foundation-models | 1 agent of 4, after its last paper | nothing left to read | 0.14M tokens re-cached by the main session |

- Runs finish quickly after "continue" because agents append a section per paper, so only the paper in progress is lost.
- No paper marked for a full read was found downgraded to a skim. In foundation-models the notes match the assignments (18 full); evaluation ended with 39 full reads against 28 assigned. The post-training assignments could not be parsed from its prompts and were not checked.
- **Half the reading of the first two runs is not reusable.** They ran before the skill wrote a note for every paper: 41 of 70 memory papers and 35 of 70 personalization papers have no note, and the batch files are deleted when the review is written.

### What a paper would cost read alone

Estimated from the trace, not measured: 448K tokens of paper text and notes entered the agent's context over 10 papers, about 45K a paper. Read one paper to a context, the same 4.5 requests would re-read about 260K tokens a paper instead of 1.28M, and the 35K start-up would be paid ten times instead of once. Reading cost falls by about a third if each agent writes its own start-up to the cache, and by about half if agents started within five minutes of each other share it. [`../reading-models/`](../reading-models/README.md) measures the limit of this: one request per paper, with no agent.

## Conclusions

1. Read one paper per context. The saving is a third to a half of the reading, and an interrupted run loses one paper per agent and re-caches nothing.
2. Give agents the paper as one cleaned text (main text, no link targets) instead of letting them slice it: fewer requests per paper.
3. Keep what was read in the notes, not in batch files that are deleted. Then reading can be done in advance, in any session, and the review written in a fresh one.
4. Talk about a finished review in a new session. A main session with 400K tokens of context costs about 0.8M cost-eq to re-cache after an hour's pause.
