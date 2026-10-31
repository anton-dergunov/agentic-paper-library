# Scores

2275 papers; 88 scope queries (leaf topics with 5 papers or more); 32 judged queries, 2036 grades. A judged query's pool holds 66 papers (median), of which 18 are graded 1 or 2 and 9 graded 2; 30 queries have more than 10 relevant papers, where R@10 cannot reach 1.

## Judged queries

Relevant for P, R and MAP: graded 1 or 2. R@10 (2): of the papers graded 2. MAP@10: AP normalised by min(relevant, 10).

| Run | nDCG@10 | P@10 | R@10 | R@10 (2) | MAP@10 | Ungraded in top 10 |
|---|--:|--:|--:|--:|--:|--:|
| qwen3 · tsa | 0.752 | 0.716 | 0.388 | 0.642 | 0.666 | 0% |
| qwen3 · ta | 0.739 | 0.706 | 0.382 | 0.631 | 0.652 | 0% |
| qwen3 · ts | 0.675 | 0.653 | 0.361 | 0.578 | 0.572 | 0% |
| bge-base · body | 0.646 | 0.688 | 0.370 | 0.547 | 0.602 | 0% |
| bge-base · ta | 0.628 | 0.619 | 0.342 | 0.514 | 0.551 | 0% |
| bge-small · ta | 0.622 | 0.603 | 0.322 | 0.510 | 0.529 | 0% |
| bge-base · tsa | 0.619 | 0.597 | 0.319 | 0.501 | 0.544 | 0% |
| bge-small · tsa | 0.611 | 0.594 | 0.319 | 0.486 | 0.514 | 0% |
| minilm · tsa | 0.574 | 0.591 | 0.326 | 0.444 | 0.496 | 0% |
| minilm · ta | 0.568 | 0.575 | 0.315 | 0.449 | 0.483 | 0% |
| e5-small · tsa | 0.542 | 0.550 | 0.295 | 0.464 | 0.457 | 0% |
| e5-small · ta | 0.526 | 0.537 | 0.283 | 0.415 | 0.437 | 0% |
| bge-base · ts | 0.510 | 0.531 | 0.288 | 0.424 | 0.438 | 0% |
| bm25 · tsa | 0.504 | 0.512 | 0.281 | 0.446 | 0.430 | 0% |
| bge-small · ts | 0.503 | 0.531 | 0.287 | 0.398 | 0.432 | 0% |
| bm25 · ta | 0.492 | 0.494 | 0.265 | 0.424 | 0.409 | 0% |
| minilm · ts | 0.486 | 0.522 | 0.291 | 0.370 | 0.426 | 0% |
| e5-small · ts | 0.442 | 0.481 | 0.246 | 0.300 | 0.394 | 0% |
| specter · tsa | 0.373 | 0.387 | 0.211 | 0.275 | 0.303 | 0% |
| specter · ts | 0.370 | 0.391 | 0.227 | 0.296 | 0.280 | 0% |
| specter · ta | 0.366 | 0.394 | 0.229 | 0.276 | 0.303 | 0% |
| bm25 · ts | 0.337 | 0.347 | 0.181 | 0.272 | 0.252 | 0% |

## Topics

| Run | Topic@10 (folder) | Topic@10 (area) | Scope R-prec | Scope nDCG@20 |
|---|--:|--:|--:|--:|
| qwen3 · tsa | 0.499 | 0.744 | 0.584 | 0.720 |
| qwen3 · ta | 0.489 | 0.737 | 0.573 | 0.716 |
| qwen3 · ts | 0.418 | 0.682 | 0.547 | 0.684 |
| bge-base · body | 0.447 | 0.701 | 0.528 | 0.643 |
| bge-base · ta | 0.442 | 0.701 | 0.521 | 0.657 |
| bge-small · ta | 0.432 | 0.699 | 0.473 | 0.604 |
| bge-base · tsa | 0.447 | 0.701 | 0.530 | 0.660 |
| bge-small · tsa | 0.439 | 0.701 | 0.475 | 0.615 |
| minilm · tsa | 0.422 | 0.694 | 0.495 | 0.624 |
| minilm · ta | 0.412 | 0.686 | 0.493 | 0.614 |
| e5-small · tsa | 0.350 | 0.611 | 0.400 | 0.528 |
| e5-small · ta | 0.348 | 0.614 | 0.399 | 0.527 |
| bge-base · ts | 0.356 | 0.609 | 0.457 | 0.611 |
| bm25 · tsa | 0.406 | 0.665 | 0.479 | 0.625 |
| bge-small · ts | 0.360 | 0.620 | 0.418 | 0.550 |
| bm25 · ta | 0.388 | 0.650 | 0.467 | 0.607 |
| minilm · ts | 0.389 | 0.661 | 0.472 | 0.606 |
| e5-small · ts | 0.294 | 0.537 | 0.374 | 0.525 |
| specter · tsa | 0.381 | 0.685 | 0.277 | 0.375 |
| specter · ts | 0.299 | 0.581 | 0.303 | 0.432 |
| specter · ta | 0.375 | 0.683 | 0.276 | 0.354 |
| bm25 · ts | 0.302 | 0.543 | 0.428 | 0.567 |
| random neighbours | 0.013 | 0.159 | | |

A `body` run's topic agreement is its `tsa` text's: its neighbours are found from that text.

## Cost (title, summary and abstract)

| Encoder | Model | Revision | Dims | Max tokens | Library on MPS (s) | Query on MPS (ms) | CPU a paper (s) | Query on CPU (ms) | Peak memory (MB) |
|---|---|---|--:|--:|--:|--:|--:|--:|--:|
| minilm | `sentence-transformers/all-MiniLM-L6-v2` | `1110a243fd` | 384 | 256 | 18.6 | 6.9 | 0.014 | 6.3 | 817 |
| bge-small | `BAAI/bge-small-en-v1.5` | `5c38ec7c40` | 384 | 512 | 72.5 | 14.8 | 0.055 | 9.7 | 605 |
| bge-base | `BAAI/bge-base-en-v1.5` | `a5beb1e3e6` | 768 | 512 | 191.9 | 19.8 | 0.174 | 32.9 | 967 |
| e5-small | `intfloat/multilingual-e5-small` | `614241f622` | 384 | 512 | 73.3 | 12.1 | 0.076 | 11.2 | 1405 |
| specter | `sentence-transformers/allenai-specter` | `2c68eeca61` | 768 | 512 | 238.3 | 17.5 | 0.133 | 27.9 | 921 |
| qwen3 | `Qwen/Qwen3-Embedding-0.6B` | `97b0c614be` | 1024 | 1024 | 1534.6 | 79.0 | 16.918 | 466.5 | 1433 |

## Paired against the best run, qwen3 · tsa (judged nDCG@10)

| Run | Mean difference | 95% interval | Queries better / worse |
|---|--:|--:|--:|
| qwen3 · ta | -0.013 | -0.030 to +0.005 | 11 / 19 |
| qwen3 · ts | -0.076 | -0.113 to -0.039 | 6 / 24 |
| bge-base · body | -0.106 | -0.170 to -0.042 | 10 / 22 |
| bge-base · ta | -0.124 | -0.183 to -0.065 | 7 / 24 |
| bge-small · ta | -0.130 | -0.188 to -0.074 | 7 / 25 |
| bge-base · tsa | -0.133 | -0.192 to -0.072 | 7 / 23 |
| bge-small · tsa | -0.141 | -0.196 to -0.086 | 8 / 24 |
| minilm · tsa | -0.178 | -0.238 to -0.115 | 4 / 26 |
| minilm · ta | -0.184 | -0.243 to -0.125 | 4 / 25 |
| e5-small · tsa | -0.210 | -0.286 to -0.135 | 5 / 27 |
| e5-small · ta | -0.226 | -0.291 to -0.161 | 4 / 28 |
| bge-base · ts | -0.242 | -0.310 to -0.177 | 2 / 30 |
| bm25 · tsa | -0.247 | -0.340 to -0.154 | 7 / 25 |
| bge-small · ts | -0.249 | -0.317 to -0.182 | 2 / 30 |
| bm25 · ta | -0.260 | -0.354 to -0.166 | 7 / 25 |
| minilm · ts | -0.266 | -0.334 to -0.198 | 2 / 30 |
| e5-small · ts | -0.310 | -0.386 to -0.233 | 3 / 28 |
| specter · tsa | -0.379 | -0.460 to -0.295 | 1 / 31 |
| specter · ts | -0.382 | -0.455 to -0.310 | 1 / 31 |
| specter · ta | -0.385 | -0.466 to -0.305 | 1 / 31 |
| bm25 · ts | -0.415 | -0.502 to -0.329 | 2 / 30 |

## Judged nDCG@10 by query (title, summary and abstract)

| Query | qwen3 | bge-base | bge-small | minilm | e5-small | bm25 | specter |
|---|--:|--:|--:|--:|--:|--:|--:|
| q01 LLM judges preferring answers written by their own model | 0.61 | 0.42 | 0.62 | 0.38 | 0.19 | 0.21 | 0.18 |
| q02 an assistant that remembers a user across many conversations | 1.00 | 1.00 | 0.96 | 1.00 | 0.87 | 0.35 | 0.25 |
| q03 does a language model's stated confidence match how often it is right | 0.91 | 0.93 | 0.78 | 0.87 | 0.56 | 0.45 | 0.21 |
| q04 correcting for users clicking the top results more when training a ranker | 1.00 | 0.73 | 0.86 | 1.00 | 0.53 | 0.57 | 0.68 |
| q05 using data from before an experiment to make A/B tests more sensitive | 0.81 | 0.61 | 0.37 | 0.29 | 0.56 | 0.08 | 0.00 |
| q06 making attention cheap enough for very long documents | 0.72 | 0.26 | 0.45 | 0.34 | 0.18 | 0.44 | 0.07 |
| q07 training models to reason with rewards from answers that can be checked | 0.63 | 0.39 | 0.43 | 0.23 | 0.79 | 0.29 | 0.50 |
| q08 language models that call external tools and APIs | 0.66 | 0.60 | 0.63 | 0.50 | 0.62 | 0.74 | 0.27 |
| q09 benchmark questions leaking into training data and inflating scores | 0.76 | 0.61 | 0.77 | 0.55 | 0.24 | 0.40 | 0.41 |
| q10 models telling users what they want to hear instead of the truth | 0.37 | 0.00 | 0.00 | 0.10 | 0.19 | 0.22 | 0.35 |
| q11 large language models as recommender systems | 0.89 | 0.84 | 0.96 | 0.94 | 0.75 | 0.56 | 0.70 |
| q12 serving many LLM requests at once on GPUs with high throughput | 0.70 | 0.78 | 0.75 | 0.57 | 0.81 | 0.96 | 0.49 |
| q13 simulating users to evaluate a conversational system | 0.96 | 0.69 | 0.86 | 0.77 | 0.84 | 0.64 | 0.76 |
| q14 finding mislabelled examples in a training set | 0.67 | 0.57 | 0.57 | 0.62 | 0.55 | 0.22 | 0.74 |
| q15 merging the result lists of several search systems into one ranking | 0.77 | 0.77 | 0.36 | 0.31 | 0.32 | 0.30 | 0.66 |
| q16 long-term effects of a product change that a short experiment misses | 0.80 | 0.87 | 0.69 | 0.63 | 0.68 | 0.90 | 0.55 |
| q17 getting a model to reveal text it memorized during training | 0.62 | 0.29 | 0.29 | 0.44 | 0.88 | 0.96 | 0.36 |
| q18 sentence embeddings for semantic similarity | 0.80 | 0.75 | 0.96 | 0.81 | 0.88 | 0.95 | 0.62 |
| q19 shrinking a prompt to save tokens without losing what matters | 0.75 | 0.69 | 0.52 | 0.44 | 0.30 | 0.40 | 0.00 |
| q20 sending each query to a cheap or an expensive model depending on difficulty | 0.68 | 0.73 | 0.58 | 0.75 | 0.33 | 0.16 | 0.00 |
| q21 explaining why a model made one particular prediction | 0.64 | 0.87 | 0.72 | 0.93 | 0.39 | 0.55 | 0.16 |
| q22 finding interpretable features inside a network with sparse autoencoders | 0.92 | 0.76 | 0.83 | 0.85 | 0.79 | 0.90 | 0.45 |
| q23 discovering the themes of a large collection of documents | 0.70 | 0.43 | 0.37 | 0.37 | 0.50 | 0.38 | 0.29 |
| q24 published machine learning results that do not hold up when rerun | 0.57 | 0.66 | 0.59 | 0.44 | 0.23 | 0.18 | 0.11 |
| q25 how AI assistants change the productivity of workers | 0.86 | 0.97 | 0.90 | 0.85 | 0.89 | 0.90 | 0.79 |
| q26 when gradient boosted trees beat neural networks on tables of data | 0.88 | 0.79 | 0.51 | 0.78 | 0.74 | 0.57 | 0.13 |
| q27 retrieving passages with learned dense vectors for open-domain question answering | 0.85 | 0.72 | 0.69 | 0.62 | 0.81 | 0.79 | 0.77 |
| q28 inferring a person's personality or preferences from what they write | 0.74 | 0.60 | 0.58 | 0.55 | 0.71 | 0.49 | 0.22 |
| q29 knowledge graphs combined with retrieval-augmented generation | 0.86 | 0.53 | 0.74 | 0.56 | 0.74 | 0.73 | 0.57 |
| q30 how much data and how many parameters to use for a fixed compute budget | 0.71 | 0.15 | 0.33 | 0.18 | 0.22 | 0.75 | 0.05 |
| q31 whether people trust and follow advice from an algorithm | 0.46 | 0.29 | 0.24 | 0.15 | 0.06 | 0.04 | 0.04 |
| q32 telling whether searchers were satisfied without asking them | 0.76 | 0.52 | 0.68 | 0.54 | 0.16 | 0.06 | 0.56 |
