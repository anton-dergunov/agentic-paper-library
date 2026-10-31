# Experiment · which encoder for meaning search?

**Question.** The library is searched by words: grep, the indexes, carrel's text search. A paper that says "LLM-as-a-judge" is missed by "automatic evaluation with models". Meaning search embeds each paper and ranks the papers by how close they are to a description. Which local encoder, embedding which text, finds what a reader means on this library, at what cost on the laptop (and later the NAS)? And is it worth embedding the body, not only the abstract?

**Status.** Measured 31 Oct 2026 on the author's 2,275 papers. On 32 judged queries **Qwen3-Embedding-0.6B** reached nDCG@10 **0.752**. The best small encoder, bge-base, reached 0.628, and BM25 over the same text 0.504. Qwen3 was better on 24 of the 32 queries, with a paired 95% interval for the difference of +0.065 to +0.183. Embedding the abstract is what counts: title and abstract scored about the same as title, summary and abstract, and title and summary alone scored 0.08–0.11 lower. SPECTER, trained on citations, came last. On the M1, Qwen3 takes 65–80 ms a query on the GPU and 174 ms on the CPU, 0.5–0.7 s a paper to embed on either, and 1.6 GB of memory while loaded. Told about it by one line of the guide, 5 of 5 Haiku sessions used it unprompted, found as many of the right papers with half the tool calls, and cost 30% less. Embedding the opening 2,000 words of the body as well, measured with bge-base, raised P@10 from 0.597 to 0.688, but nDCG@10 only from 0.619 to 0.646, within noise, at ten times the embedding; it waits for its run with Qwen3 ([`NEXT.md`](NEXT.md)). **`paperlib meaning` and `similar` ship with Qwen3, title, summary and abstract, and the guide's line.** Grading cost $2.51 of Sonnet, the agent check $0.13 of Haiku.

**Serves.** [`docs/design.md`](../../docs/design.md#decisions-log), `scripts/meaning.py` (`paperlib meaning`, `paperlib similar`, `paperlib embed`), carrel's Meaning search and similar papers.

## Method

- **Papers.** All 2,275 papers of the author's library on 31 Oct 2026.
- **Text.** Three variants: `tsa` (title, the one-line summary, the abstract), `ts` and `ta`. The abstract is `paperlib.abstract_from_body` on the head of the paper's own text (the Abstract section, or the opening of the first page), so nothing is fetched at run time. Median `tsa` text: 1,750 characters.
- **Candidates**, all run locally with sentence-transformers 6.2 on the M1's GPU (MPS), each with the query and document prefixes it was trained with ([`common.py`](common.py)):
  - `all-MiniLM-L6-v2` (22M parameters, 256 tokens), the usual baseline;
  - `bge-small-en-v1.5` (33M) and `bge-base-en-v1.5` (109M);
  - `multilingual-e5-small` (118M), Acervo's encoder;
  - `allenai-specter` (110M), trained on scientific papers' citations;
  - `Qwen3-Embedding-0.6B` (600M), high on MTEB, with an instruction for the query;
  - **BM25** over the same texts (bm25s, English stop words), the keyword baseline meaning search has to beat.
  - Not run: `nomic-embed-text-v1.5`, which needs `trust_remote_code` (its own Python from the model's repository); the other candidates load with the libraries' code.
- **Measures** ([`score.py`](score.py)):
  1. **Topic agreement@10**: the share of a paper's ten nearest papers in its folder, and in its top-level area, against random neighbours. Acervo's measure, which there did not separate encoders.
  2. **Scope as query**: each of the 88 leaf folders with five papers or more, its one-line scope from `topics.yaml` as the query and its papers as the answer: R-precision and nDCG@20. The scopes were in the filing prompt that chose most folders, so this favours whatever reads like a scope.
  3. **Judged queries**, the measure for search. 32 queries a reader might type, spread over the areas and worded as descriptions rather than in a paper's own terms ([`queries.yaml`](queries.yaml), written before any encoder ran). Every run's top 10 for each query is pooled, TREC-style, and Sonnet 5.5 grades each pooled paper from its title, summary and abstract: 2 about what the query describes, 1 partly or a closely related aspect, 0 not ([`judge.py`](judge.py); one request a query, the papers in an order shuffled with a fixed seed). nDCG@10 with gains 2^grade − 1, and P@10. Each run is compared with the best by a paired bootstrap over the queries.
  4. **Cost**: seconds to embed the library on MPS, a query's median milliseconds, seconds a paper and a query on the CPU alone (as on the NAS), and peak memory ([`embed.py`](embed.py)).
- **The body** ([`body.py`](body.py)): the first 2,000 words of each paper's main text (no references) in eight chunks of 250 words, a paper's score the best of its chunks and its `tsa` text. Run with bge-base, as Qwen3 needs about three hours for it; Qwen3's run is next ([`NEXT.md`](NEXT.md)).
- **The judge** was read before it was trusted: its 26 grades for the first query by hand (below).

```bash
export PAPER_LIBRARY=~/papers
./run-all.sh                                                              # every encoder, three variants
uv run --project ../.. --with sentence-transformers python body.py <encoder>   # resumable, in slices
uv run --project ../.. --with bm25s python judge.py                       # grades what the pools add
uv run --project ../.. --with bm25s python score.py                       # results/scores.md
uv run --project ../.. --with bm25s python compare.py qwen3:tsa qwen3:body  # two runs, query by query
```

## Results

### Judged queries

2,036 grades in all: 299 papers graded 2, 338 graded 1, 1,399 graded 0. A query's pool holds 66 papers (median), of which 18 are graded 1 or 2 and 9 graded 2. P, R and MAP count grade 1 or 2 as relevant; MAP@10 is normalised by min(R, 10). 30 queries have more than 10 relevant papers, so R@10 cannot reach 1 on them. The full table, with every run, is in [`results/scores.md`](results/scores.md).

| Run (title, summary, abstract) | nDCG@10 | P@10 | R@10 | R@10 (grade 2) | MAP@10 |
|---|--:|--:|--:|--:|--:|
| **Qwen3-Embedding-0.6B** | **0.752** | **0.716** | **0.388** | **0.642** | **0.666** |
| bge-base-en-v1.5 | 0.619 | 0.597 | 0.319 | 0.501 | 0.544 |
| bge-small-en-v1.5 | 0.611 | 0.594 | 0.319 | 0.486 | 0.514 |
| all-MiniLM-L6-v2 | 0.574 | 0.591 | 0.326 | 0.444 | 0.496 |
| multilingual-e5-small | 0.542 | 0.550 | 0.295 | 0.464 | 0.457 |
| BM25 | 0.504 | 0.512 | 0.281 | 0.446 | 0.430 |
| allenai-specter | 0.373 | 0.387 | 0.211 | 0.275 | 0.303 |

- **Qwen3 leads on every measure**, and its lead over the next run (bge-base with title and abstract, 0.628: +0.124, 95% interval +0.065 to +0.183) is outside the noise of 32 queries. The small encoders sit within 0.06 of each other.
- **Every encoder but SPECTER beats BM25.** The queries were worded as a reader describes a topic, not in a paper's terms, which is where keywords fail: "models telling users what they want to hear" (sycophancy), "whether people trust and follow advice from an algorithm" (algorithm aversion). BM25 wins where the query names the paper's own terms ("getting a model to reveal text it memorized").
- **SPECTER** was trained to place a paper near the papers it cites, from its title and abstract. It was not trained to match a description to a paper, and it has no query form.
- **Which text.** For each encoder, title and abstract scored within 0.015 of title, summary and abstract. Title and summary alone scored 0.08–0.11 lower (SPECTER's three were level): the one-line summary is too thin on its own.

### Topics

| Run (title, summary, abstract) | Topic@10, folder | Topic@10, area | Scope R-precision | Scope nDCG@20 |
|---|--:|--:|--:|--:|
| Qwen3-Embedding-0.6B | 0.499 | 0.744 | 0.584 | 0.720 |
| bge-base-en-v1.5 | 0.447 | 0.701 | 0.530 | 0.660 |
| BM25 | 0.406 | 0.665 | 0.479 | 0.625 |
| random neighbours | 0.013 | 0.159 | | |

The topic measures order the encoders as the judged queries do, but the gaps are narrower. As in Acervo, they would not have separated the small encoders.

### Cost

| Encoder | Dims | Library on MPS | Query on MPS | A paper on CPU | Query on CPU | Peak memory |
|---|--:|--:|--:|--:|--:|--:|
| all-MiniLM-L6-v2 | 384 | 19 s | 7 ms | 0.014 s | 6 ms | 0.8 GB |
| bge-small-en-v1.5 | 384 | 73 s | 15 ms | 0.055 s | 10 ms | 0.6 GB |
| bge-base-en-v1.5 | 768 | 192 s | 20 ms | 0.17 s | 33 ms | 1.0 GB |
| Qwen3-Embedding-0.6B | 1024 | 1,535 s | 79 ms | 0.60 s | 174 ms | 1.6 GB |

- **Qwen3 on a CPU must be loaded in float32.** Loaded as its weights come, in bfloat16, it took 16.9 s a paper and 467 ms a query on the CPU, and transformers warns about it. `meaning.py` loads it in float32 on a CPU. The figures above are float32 from a second measurement; the others are from [`embed.py`](embed.py)'s run.
- **For Qwen3 the M1's GPU barely helps.** Embedding takes 0.5–0.7 s a paper on either, and a query 65–80 ms on the GPU against 174 ms on the CPU. So the NAS, with no GPU, can embed the whole library in about 25 minutes. The cache is content-addressed, so it can also take the laptop's vectors instead.
- **A `paperlib meaning` call takes 8–9 s** on either: about 4 s to import torch, 3.5 s to load the model, then the query.
- **Memory**, as macOS's `footprint` counts it: 1.6 GB with the model loaded. Freeing the model leaves 430 MB, mostly torch's libraries.

### The body

Run with bge-base as a proxy: Qwen3 needs about three hours for the 18,184 chunks, where bge-base took 32 minutes (1,947 s, ten times its 192 s for one text a paper). A paper's score is the best of its eight chunks of 250 words and its title, summary and abstract. The body brought 76 papers into the top 10s that no other run had ranked there; they were graded in a round of their own.

| bge-base | nDCG@10 | P@10 | R@10 | R@10 (grade 2) | MAP@10 | Scope nDCG@20 |
|---|--:|--:|--:|--:|--:|--:|
| Title, summary, abstract | 0.619 | 0.597 | 0.319 | 0.501 | 0.544 | 0.660 |
| With the opening 2,000 words | **0.646** | **0.688** | **0.370** | **0.547** | **0.602** | 0.643 |

- **More relevant papers in the top 10:** P@10 rose by 0.09 and MAP@10 by 0.06, and 21 of the 32 queries improved.
- **But the graded measure gained within noise:** nDCG@10 +0.027, 95% interval −0.025 to +0.072. The body finds more papers that touch the topic (grade 1) more than papers squarely on it (grade 2), and scope queries did not improve (nDCG@20 0.643 against 0.660).
- **Qwen3 with the body** is still Qwen3 at its best: bge-base with the body stays 0.106 below Qwen3 without it (95% interval −0.170 to −0.042). Whether the body adds as much to Qwen3 is the next run.

### Agents with the guide's line

Five of the judged queries asked as chat questions on Haiku (`claude -p --model haiku`) in a copy of the library, each once with the guide as it was and once with the line on `paperlib meaning` ([`agents.py`](agents.py), [`results/agents.md`](results/agents.md)). Edit and Write were off, so the copy stayed as it was.

| | Used meaning search | Grade-2 papers named | Tool calls | $ |
|---|--:|--:|--:|--:|
| Without the line | 0 of 5 | 17 of 23 | 54 | 0.075 |
| With the line | 5 of 5 | 18 of 23 | 25 | 0.051 |

- **Both arms answered well.** The difference is the route. Without the line, the agent grepped for one wording after another: 25 calls for the reproducibility question, 14 for sycophancy. With it, one `paperlib meaning` call and a grep or two found the same papers. The answer to the reproducibility question added the papers on leakage and untuned baselines.
- **The line costs about 70 tokens** of the guide in every session.
- **In carrel's sandbox** the command works with no question to the reader. The sandbox hides the GPU, so the model runs on the CPU, in float32. A call takes 8–9 s there, as it does with the GPU, because importing torch and loading the model take most of it.

### The judge, read by hand

The 26 grades of the first query (LLM judges favouring their own model) were read before the rest were asked for. The two papers squarely on self-preference were graded 2, general studies of judge bias 1, and papers on position bias or on judges in general 0. That is strict, and consistent.

## Caveats

- **One assessor, an LLM.** The grades are Sonnet's, read by hand only for one query. Published LLM assessors agree with TREC's people about as well as people agree with each other, and rank systems as people's labels do (Thomas et al. 2024, UMBRELA 2024). Those assessors judged one paper per prompt.
- **The judging was batched.** Each query's ungraded papers went to the judge in one prompt: 22–58 papers in the first round, then, in three more rounds, only what the later runs added (e5-small; SPECTER and Qwen3; bge-base's body), about 1–15 a query. Long lists may be judged worse, and a grade may be relative to the others in its batch. All runs were graded from the same pool, so the comparison between them is fair, but the absolute numbers carry this.
- **The queries were written by the experimenter**, before any encoder ran, as a reader might type. 32 queries put the small encoders within noise of each other, but not Qwen3.
- **Pool depth 10.** Nothing below rank 10 is graded, so recall is relative to what the pools found, and R@20 or full MAP cannot be computed without more grading.
- **The library is one reader's**: machine learning, mostly in English, summaries written by Sonnet.

## Decision

1. **`scripts/meaning.py` embeds with Qwen3-Embedding-0.6B** at revision `97b0c614be`, from each paper's title, summary and abstract, with the instruction Qwen3 takes before a query. Vectors are cached by the digest of model and text in the engine's cache folder.
2. **`paperlib meaning`, `similar` and `embed`** use it, and carrel serves the same search on the tablet (its Meaning depth, and a paper's similar papers).
3. **The guide gains one line** pointing agents at `paperlib meaning` where grep would miss a paper that words a topic differently.
4. **The body is not embedded, for now.** With bge-base it put more relevant papers in the top 10, but the graded measure moved within noise, and it costs ten times the embedding. Qwen3's run decides it ([`NEXT.md`](NEXT.md)).
5. **Not done:** a stronger encoder (Qwen3-Embedding-4B, or a hosted one), or reranking the top results with a cross-encoder. Both are worth measuring once the reader's sittings show where meaning search falls short.
