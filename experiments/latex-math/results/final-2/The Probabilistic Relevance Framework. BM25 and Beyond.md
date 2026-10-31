---
title: "The Probabilistic Relevance Framework: BM25 and Beyond"
aliases: [BM25]
authors: [Stephen Robertson, Hugo Zaragoza]
affiliations: [Microsoft Research, Yahoo! Research]
year: 2009
type: survey
topic: search-and-ranking/indexing-and-classical-ir
links:
  - https://doi.org/10.1561/1500000019
concepts: ["Probability ranking principle", "Inverse document frequency", "Term-frequency saturation", "Relevance feedback"]
papers: ["Dense Passage Retrieval"]
tags: [bm25, bm25f, okapi, term-weighting, query-expansion, inverted-index]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> A principled way to score a document against a query by how likely it is to be relevant. It yields BM25, one of the most successful text-search scoring functions.

## Overview

### Scope

The monograph covers the framework from its assumptions down to the BM25 and BM25F scoring functions. It is conceptual: it explains why the formulas take their shape, and says little about how well they work. Its literature stops around 2008 (not from the paper).

### Taxonomy

- **Basic model:** rank documents by their probability of being relevant to one user's need.
- **Derived models:**
  - the binary independence model, the simplest scoring rule;
  - relevance and blind feedback, which add words to the query;
  - the eliteness model, which gives BM25;
  - BM25F, for documents with fields such as title and anchor text;
  - non-textual signals such as link popularity;
  - word positions.
- **Neighbours:** language models, divergence from randomness and topic models, compared on the same footing.
- **Tuning:** how to set the free parameters.

### Findings

- **The score:** each query word found in a document adds one weight. The sum is the score:

$$
\mathrm{score}(q,d)=\sum_{t\in q\cap d}\mathrm{idf}(t)\cdot\frac{(k_1+1)\,\mathrm{tf}_{t,d}}{k_1\,B_d+\mathrm{tf}_{t,d}},
\qquad
B_d=(1-b)+b\,\frac{\mathrm{dl}_d}{\mathrm{avdl}}
$$

  Here $\mathrm{tf}_{t,d}$ is how often word $t$ occurs in document $d$, $\mathrm{dl}_d$ is the document's length, and $\mathrm{avdl}$ is the average length. Only matched words contribute, which is why an inverted index can score documents quickly.
- **Saturation:** a repeated word counts more, but each extra occurrence adds less. Long documents are discounted, but only partly, since a long document may simply cover more ground.
- **Fields:** BM25F adds the weighted counts from all fields first, then saturates once. Scoring each field separately and combining the scores is the weaker option.
- **Parameters:** the theory gives no values for $k_1$ and $b$. Experiments suggest $b$ between 0.5 and 0.8 and $k_1$ between 1.2 and 2, but the paper says so without citing them.
- **Tuning:** the metrics are step functions with no gradient, so the authors tune with grid and line searches.

### Open problems

- The score cannot easily be turned back into a calibrated probability, which limits filtering and blind feedback.
- Inverse document frequency for BM25F is ill-defined when fields are pooled; the authors leave the proper definition open.
- No natural way to add word-proximity information has emerged, and the gains reported so far are small.

### Coverage

- Almost no experiments of its own. Claims that techniques "work well" rest on experiments the authors do not cite, and the paper says so itself.
- It predates the neural and dense methods that now compete with BM25 (not from the paper).

## Concepts

- **Probability ranking principle:** if documents are sorted by their chance of relevance, that ordering is the best the system can do for one user.
- **Inverse document frequency (idf):** a word found in few documents is more informative. A common form is $\mathrm{idf}(t)=\log\frac{N-n_t+0.5}{n_t+0.5}$, where $N$ is the number of documents and $n_t$ the number containing $t$.
- **Term-frequency saturation:** the curve $\frac{\mathrm{tf}}{k_1+\mathrm{tf}}$ rises fast at first and flattens, so the first occurrences count most.
- **Relevance feedback:** using documents the user has judged relevant to pick better query words.

## Follow-ups

**Read**

- [Search and ranking review](../reviews/search-and-ranking.md): where BM25 sits among the newer methods that compete with it.
- Dense Passage Retrieval (not in the library): the neural retriever that most later work compares against BM25, and the closest contrast to this lexical scoring.

**Try**

- Score two short documents by hand against a two-word query with BM25, then set $b$ to 0 and to 1 and watch the length penalty change the ranking (ours, not from the paper).
