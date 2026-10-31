---
title: "The Probabilistic Relevance Framework: BM25 and Beyond"
aliases: [BM25 and Beyond]
authors: [S. Robertson, H. Zaragoza]
year: 2009
type: survey
topic: search-and-ranking/indexing-and-classical-ir
links:
  - https://doi.org/10.1561/1500000019
concepts: ["[[Probability ranking principle]]", "[[Binary independence model]]", "[[Two-Poisson model]]", "[[Relevance feedback]]"]
papers: ["[[Term Frequency Normalisation Tuning for BM25 and DFR Models]]", "[[BEIR. A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models|BEIR]]"]
tags: [bm25, bm25f, term-weighting, query-expansion, trec]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> The theory behind BM25, the keyword scoring formula that most search engines still use, and how it was extended to documents with fields.

## Overview

### Scope

A monograph from 2009 by S. Robertson and H. Zaragoza. It explains one family of ranking functions, the Probabilistic Relevance Framework (PRF), from its assumptions down to the formulas a search engine runs. It is a conceptual text: the authors say it is "not primarily an experimental survey". It starts with the simplest model, then adds feedback from users, then the two practical formulas BM25 and BM25F, and ends with how to tune them.

### Taxonomy

- **Basic model**: the binary independence model, which scores a document by how each query word shows up in it.
- **Learning from judgements**: relevance feedback (use documents the user marked) and blind feedback (assume the top results are relevant), both used to pick extra query words.
- **Term frequency**: the two-Poisson or "eliteness" model, which explains why repeated words count, but with diminishing returns.
- **Practical functions**: BM25 for plain text, BM25F for documents with fields such as title and body, and a way to add non-text signals.
- **Neighbours**: how the same ideas compare with language models and with divergence-from-randomness models.

### Findings

- **Rank by odds of relevance.** Starting from the probability ranking principle, a few simplifying assumptions turn the score into a sum over query words. Only words present in the document add to it, which is what lets a search engine score through an inverted index.
- **A rare word is worth more.** Each word's weight grows when it appears in few documents: the idf part.
- **Repeats saturate.** The first occurrence of a word counts most; each later one adds less, and the total levels off. The authors fitted this curve to the shape the theory predicts rather than deriving it exactly.
- **Long documents are discounted, but not punished fully.** A document is penalised for length, by a soft rule that depends on how long it is compared with the average.
- **Fields share one count.** In BM25F, a word in the title and in the body is added up, with per-field weights, before the saturation step. Scoring each field separately and adding the results is the weaker option.
- **The parameters are empirical.** The framework says nothing about the two main constants, so they are set by experiment.

### Open problems

- **Document frequency for fields.** The idf term in BM25F is computed over the whole collection, and this can break down. The authors leave the right definition open.
- **Word order.** No approach to position or proximity counts as a natural extension, and the gains reported are small.
- **Calibrated scores.** The scores are not probabilities, which makes them awkward for filtering, where a real probability of relevance is needed.
- **Tuning.** Ranking metrics are not smooth, so gradient methods do not apply directly. The authors mention learning to rank but do not go into it.

### Coverage

- **No new experiments.** The text reports no tests of its own. Its claims about what "works well" rest on experiments it does not cite.
- **Strong words, thin support.** The abstract calls BM25 and BM25F among the most successful retrieval algorithms, and the text repeats it without tables.
- **Stale in places.** Nothing here covers neural rankers or dense retrieval, which later work found to behave differently on other collections (not from the paper).

### Concepts

- **[[Probability ranking principle]]**: the idea that ranking documents by their probability of being relevant gives the best order for the user.
- **[[Binary independence model]]**: the simplest version of the framework, where each query word is treated as an independent yes-or-no signal of relevance.
- **[[Two-Poisson model]]**: a model of word counts in which a hidden "eliteness" variable decides whether a word appears often; it explains why repeats saturate.
- **[[Relevance feedback]]**: using documents the user has judged to pick better query words or to reweight terms.

## Questions

- Why does the score only sum over words that are in the document, and what is lost by dropping the rest?
- What does the saturation curve assume about why a word repeats in a document?
- Why can't the score be read as a probability, and when does that matter?
- How much of BM25's behaviour comes from theory, and how much from the fitted curve and its constants?

## Follow-ups

**Read**:
- [[Term Frequency Normalisation Tuning for BM25 and DFR Models]]: in the library; sets BM25's length parameter from collection statistics alone, which this monograph leaves open.
- [[BEIR. A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models|BEIR]]: in the library; shows how BM25 holds up against neural retrievers on collections they were not trained on.
- [[Efficient Query Evaluation using a Two-Level Retrieval Process (WAND)|WAND]]: in the library; how a large index is scored with BM25 quickly by skipping documents that cannot reach the top.

**Try**:
- Score three toy documents by hand with the saturation curve, one query word at a time, to see why the second occurrence counts less than the first (ours, not from the paper).
