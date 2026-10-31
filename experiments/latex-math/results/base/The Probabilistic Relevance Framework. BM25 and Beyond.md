---
title: "The Probabilistic Relevance Framework: BM25 and Beyond"
aliases: [PRF, BM25]
authors: [Stephen Robertson, Hugo Zaragoza]
affiliations: [Microsoft Research, Yahoo! Research]
year: 2009
type: survey
topic: search-and-ranking/indexing-and-classical-ir
links:
  - https://doi.org/10.1561/1500000019
concepts: ["[[Probability ranking principle]]", "[[Binary independence model]]", "[[Eliteness]]", "[[BM25]]", "[[BM25F]]"]
papers: ["[[Term Frequency Normalisation Tuning for BM25 and DFR Models]]", "[[Divergence from randomness]]", "[[Dense Passage Retrieval]]"]
tags: [bm25, bm25f, relevance-feedback, query-expansion, inverted-index]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> The theory behind BM25, the keyword scorer still used everywhere: rank documents by their odds of being relevant.

## Overview

### Scope

Picture a librarian who must put a shelf of books in order for one question. For each book, the question is: how likely is this one to be what the reader wanted? Robertson and Zaragoza follow that question from its assumptions down to the formulas that search engines run. They call the family of models built on it the Probabilistic Relevance Framework (PRF). It is a conceptual tour, not an experimental survey: the authors say so outright. The work runs from ideas of the 1970s and 1980s to BM25F, which they date to the 2000s.

### Taxonomy

- **Basic model:** rank by the probability of relevance, where relevance is binary and judged per document.
  - **Binary independence model:** each query word is either in a document or not.
    - **Relevance feedback:** learn word weights from documents the user marked. **Blind feedback** assumes the top results are relevant instead.
  - **Eliteness and BM25:** a word is "elite" in a document when the document is about it. Repeated counts saturate.
    - **BM25F:** the same idea over several fields, such as title, body and anchor text.
    - **Non-textual features:** a link score such as PageRank is added to the sum.
  - **Positional information:** word proximity, with small reported gains.
- **Other probabilistic models, compared:** the language model approach, divergence from randomness, and topic models.
- **Parameter tuning:** greedy, multidimensional and gradient search, since IR metrics are not smooth.

### Findings

- **Each part of BM25 has a reason.** The rare-word weight follows from the odds. A word's repeats count for less and less, and long documents are discounted.
- **The saturation curve is fitted, not derived.** Eliteness predicts its shape, but the authors fit a simple curve to that shape.
- **BM25F sums field evidence before saturating.** Scoring each field separately and adding the scores is the weaker option.
- **The theory gives no default settings.** The two main parameters, k1 and b, have to be tuned, and experiments suggest only ranges.
- **Scores are not probabilities.** Dropping the terms that do not depend on the document makes the output a ranking, not a calibrated probability. This hurts filtering.
- **Proximity helps little.** Gains from word distance are small, even on the web.
- **No new experiments.** Claims that a technique "works well" rest on experiments the text does not cite.

### Open problems

- A proper definition of IDF for BM25F, which can break down when computed over the whole collection.
- The authors' closing claim: the framework has not reached the end of its useful life, and it can analyse new problems.

### Coverage

- (not from the paper) It predates neural rankers, dense retrieval and LLM rerankers, so none of the results from those years appear here.
- Its comparisons stop at language models and divergence from randomness.
- Learning to rank comes up only in passing.

### Concepts

- [[Probability ranking principle]]: rank documents by their probability of being relevant. The starting point.
- [[Inverse document frequency]]: rare words count more. In the paper's form it is a log of odds.

## Questions

- Why does a word's tenth occurrence add less than its first?
- Which parts of BM25 come from the theory, and which are fitted to data?
- What does a score lose by not being a calibrated probability?
- Why sum field counts before saturating in BM25F?

## Follow-ups

**Read:**

- [[Term Frequency Normalisation Tuning for BM25 and DFR Models]]: sets BM25's length parameter on new collections without labels, the open tuning question here. Not in the library yet.
- [[Divergence from randomness]]: the rival probabilistic family this monograph compares against.
- [[Dense Passage Retrieval]]: what took over from keyword scoring for question answering. Not in the library yet.

**Try:**

- Score three short toy documents for one query, first by counting matched words and then with a count that saturates. See where the order changes. (Ours, not from the paper.)
