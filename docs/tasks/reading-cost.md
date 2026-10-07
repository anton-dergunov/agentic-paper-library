# Task: make reading a paper cheaper without reading it less

`paperlib read` costs about 35K input and 4K output tokens a paper with Opus (91 papers of
the author's `search-and-ranking`, 2026-10-06). A regression of input tokens on the length of
each paper's reading view puts about 16K of that in the part of the request that is not the
paper, and about 19K in the paper (2.7 characters a token). So the fixed part is nearly half
the input, and it is the same for every paper of an area.

## 1. Trim the fixed part of the request

It holds the reading prompt, the focus, and the "related" list: every other paper of the
scope as `- <stem>: <summary>`, for the note's "Related in library" (up to `RELATED_MAX` =
150 lines; past that, the paper's own folder). For a scope of 127 papers the list is most of
the 16K.

- Measure the parts: the prompt, the focus, the list, and what `claude -p` adds itself.
- Check how much is already served from the prompt cache. `ask_model` sums uncached input,
  cache writes and cache reads into one number, so the log cannot tell. Log them apart, and
  the `usd` per request.
- Then shrink what is paid for:
  - offer the paper's own folder and its sibling folders rather than the whole scope;
  - drop the summaries and keep the stems, or the reverse, and compare the "Related in
    library" sections on 10–20 papers against the current ones;
  - order the request so that what is shared by a folder's papers comes first and is cached.
- Done when a read costs measurably less and the related lists are as good.

Done in part on 2026-10-07 ([`experiments/prompt-trim`](../../experiments/prompt-trim/README.md)):
what `claude -p` adds is measured and cut from 1,442 to 614 tokens, and the prompt, the focus
and the list (now including the paper itself) are the system prompt, read from the cache by
every request of a scope after the first (a 12.6K-token prompt: $0.101 written, $0.008 read).
Still open: whether a shorter list (the paper's folder and its siblings, or stems without
summaries) keeps the related sections as good; with the cache it matters less.

## 2. Is a cheaper reading worth it for the thinly covered areas?

The first reviews skimmed most papers because each agent read 10–15 papers in one context
and paid for all of them again on every request. With one request per paper that reason is
gone, and every paper is read in full ([`experiments/reading-models`](../../experiments/reading-models/README.md)).
A skim is still cheaper per paper, but less than it looks:

| Per paper (estimate) | Full read | Skim: abstract, introduction, conclusion, all tables |
|---|--:|--:|
| Paper text | ~19K | ~5K (27% of the full view, over 238 papers) |
| Fixed part | ~16K | ~16K |
| Output | ~4K | ~2.5–3K |
| Cost-eq (output × 5) | ~56K | ~34K |

So about 35–40% saved, and less once item 1 is done. Compare at equal cost, not skim against
full: the alternative to an Opus skim is a full read by Sonnet, which costs about half and
made about one error a paper against one in six papers for Opus.

- **Free check first.** In the existing reviews, count the page citations that fall outside
  what a skim view holds. If most findings cite method or results sections beyond the
  headline tables, skims would starve the reviews; stop there.
- **Then 20 papers** that already have full Opus notes as the reference: an Opus skim note and
  a Sonnet full note of each, scored with `experiments/reading-models`' `check_numbers.py`
  and its judge, which also checks that the setup behind each number is stated correctly.
  About 1M cost-eq.
- **The decision is a rule, not a model's choice per paper**: a model choosing per paper
  would need to know which papers the review's findings will rest on, which it learns only
  after reading them. If the experiment favours a cheaper reading, make it a per-area setting
  in `paper-library.yaml` (full Opus for the reader's primary areas, the cheaper reading for
  the rest), perhaps with a length rule for books and long surveys.
