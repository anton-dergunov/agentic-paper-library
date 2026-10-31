# Next: the body with Qwen3

Whether to embed the opening of each paper's body as well as its title, summary and abstract. With bge-base it put more relevant papers in the top 10 (P@10 0.597 → 0.688, MAP@10 0.544 → 0.602), but nDCG@10 gained only +0.027, within noise (95% interval −0.025 to +0.072). This run asks the same question of Qwen3, the encoder that ships. Delete this file once the answer is in the README.

## Where things stand (31 Oct 2026)

- **Shipped:** Qwen3-Embedding-0.6B on title, summary and abstract (`scripts/meaning.py`), `paperlib meaning / similar / embed`, the guide's line, and carrel's Meaning depth and similar papers. The README's Results and Decision have the numbers.
- **The grades:** 2,036, in `results/judgements.jsonl`, covering every run's top 10 so far, bge-base's body included.
- **The body runner, `body.py`:** embeds 8 chunks of 250 words a paper (18,184 chunks) and saves them in slices of 1,000. A stopped run resumes after the last whole slice.

## 1. Embed the body with Qwen3 (overnight, about 3 hours)

On power, with the lid open:

```bash
cd ~/projects/products/agentic-paper-library/experiments/meaning-search
PAPER_LIBRARY=~/papers caffeinate -is uv run --project ../.. --with sentence-transformers \
  python body.py qwen3 2>&1 | tee -a ~/.cache/papers/experiments/meaning-search/qwen3-body.log
```

- **Watch:** `tail -f ~/.cache/papers/experiments/meaning-search/qwen3-body.log`. A line after each of the 19 slices gives the minutes spent and an estimate of those left.
- **Stopped or crashed:** run the same command again. Finished slices are kept in `~/.cache/papers/experiments/meaning-search/qwen3/body-parts/`.
- **Done when** the log's last line reads `qwen3 body: 18184 chunks, … slices embedded in … s`, and `body.npy` and `body-owner.npy` are in `~/.cache/papers/experiments/meaning-search/qwen3/`.
- **Memory:** about 1.6 GB. carrel's server can keep running beside it.

## 2. Evaluate it (a new Claude Code session)

Ask the session to read this file, then:

```bash
cd ~/projects/products/agentic-paper-library/experiments/meaning-search
export PAPER_LIBRARY=~/papers
uv run --project ../.. --with bm25s python judge.py --dry-run             # how many new papers the body brought
uv run --project ../.. --with bm25s python judge.py                       # grades them: Sonnet, about $0.10-0.30
uv run --project ../.. --with bm25s python score.py                       # results/scores.md
uv run --project ../.. --with bm25s python compare.py qwen3:tsa qwen3:body
```

- **Grade first.** `compare.py` counts ungraded papers as not relevant, and its "ungraded" column must read 0%.
- **Read nDCG@10's interval and the binary measures** (P@10, MAP@10) together, as the README's body section does for bge-base. The question is whether the body finds more papers squarely on the topic (grade 2, nDCG) or only more that touch it (grade 1, P@10).
- **Write the result** into the README (Status, "The body", Decision 4), the experiments index row in `../README.md`, and the design log entry in `docs/design.md`.

## 3. If the body is worth it

- **The engine:** `scripts/meaning.py` would embed each paper's chunks too, cached by digest like the rest. `Space` would hold the chunk matrix with each chunk's owner, and a paper's score would be the best of its chunks and its abstract text, as `rank.py` computes it. `similar()` could stay on the abstract text, as the experiment's neighbours did.
- **The cost:**
  - **First embed:** about 3 hours on the laptop, and the NAS's CPU about the same, unless it copies the cache.
  - **Each new paper:** about 4–5 s more.
  - **Memory:** 18,184 × 1,024 floats, about 75 MB of vectors in carrel's server.
- **carrel:** its API wouldn't change. Update `docs/architecture.md`'s meaning search section.
- **Tests:** `tests/test_meaning.py` with the word-hashing encoder, and carrel's tests.

If it isn't worth it, record why in the README and leave the code as it is.
