---
title: "The Probabilistic Relevance Framework: BM25 and Beyond"
aliases: [BM25, PRF]
authors: [Stephen Robertson, Hugo Zaragoza]
year: 2009
type: survey
topic: search-and-ranking/indexing-and-classical-ir
links:
  - https://doi.org/10.1561/1500000019
concepts: ["[[Probability ranking principle]]", "[[Binary independence model]]", "[[Term frequency saturation]]", "[[Relevance feedback]]", "[[Document length normalisation]]"]
papers: ["[[Okapi at TREC]]", "[[A Language Modeling Approach to Information Retrieval]]", "[[Divergence from randomness]]"]
tags: [bm25, bm25f, term-weighting, query-expansion, lexical-retrieval]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> A recipe for scoring a document against a search query by estimating how likely it is to be relevant, and the formula that search engines still use.

## Overview

### Scope

The monograph covers one family of ranking models, the Probabilistic Relevance Framework (PRF). It starts from a single question, "how likely is this document to be relevant to this person's need?", and derives scoring formulas from it. It is a conceptual exposition: the authors say it is "not primarily an experimental survey", so claims that a technique "works well" are not backed by data in the text.

### Taxonomy

- **Basic model**: rank documents by their probability of relevance.
- **Binary independence model**: the first concrete formula, which needs relevance judgements.
- **Feedback**: relevance feedback and blind feedback, which estimate those judgements from documents and expand the query.
- **Eliteness and BM25**: a model of how often a term appears, which yields the saturating formula.
- **Extensions**: BM25F for multi-field documents, non-text signals such as a PageRank score, and word position.
- **Comparisons**: other probabilistic and language-model approaches.
- **Tuning**: how to set the parameters.

### Findings

- **Rank by the odds of relevance.** Ranking by the probability of relevance can be rewritten, through Bayes' rule and some assumptions, as a sum over the query terms that appear in the document. Only those terms need scoring, which is what makes the inverted index work.
- **Term frequency saturates.** A word that appears twice counts for more than once, but the gain shrinks as the count grows. The score tends to a ceiling instead of growing without limit.
- **Long documents are normalised, softly.** Two explanations compete: long documents say more (the verbosity hypothesis) or cover more topics (the scope hypothesis). A length term divides the frequency by a length-dependent amount, and both explanations lead to the same formula in practice.
- **Fields share one saturation step.** When a title, anchor text or body field is present, the frequencies are weighted and summed first, then saturated once. Scoring each field separately and adding the scores is the weaker option.
- **The constants are not derived.** The model gives no value for its two tuning parameters. They are set from data, and the monograph shows only a few reported settings.
- **Position helps little.** No natural way to add word proximity to the framework emerges, and reported gains are small.

The classic formula, which the framework leads to, is

$$
\mathrm{score}(q,d)=\sum_{t\in q}\underbrace{\log\frac{N-n_t+0.5}{n_t+0.5}}_{\text{rarity of }t}\cdot\frac{(k_1+1)\,f_{t,d}}{\underbrace{k_1\big((1-b)+b\,\tfrac{dl_d}{\overline{dl}}\big)}_{\text{length correction}}+f_{t,d}}
$$

Here $f_{t,d}$ is how often term $t$ occurs in document $d$, $n_t$ is how many documents contain $t$, $N$ is the collection size, $dl_d$ is the document's length and $\overline{dl}$ the average length. The constants $k_1$ and $b$ are the two tuned parameters. The first factor is an idf weight; the second is the saturating term-frequency part.

### Open problems

- **IDF for fields.** Defining the rarity weight properly when fields are combined is left open.
- **Proximity.** The authors suggest word order might matter less than expected in language, and that combining fields already rewards proximity. They leave the question open.
- **Tuning at scale.** Retrieval metrics are not smooth, so standard gradient methods do not apply directly. Gradient-based learning to rank is mentioned but not worked out.

### Coverage

- The empirical support is cited only in passing, so the results rest on the earlier papers.
- The examples come from web and newswire test collections of the 2000s (not from the paper).
- Neural rankers and learned sparse methods are absent, as the text predates them (not from the paper).

### Concepts

- [[Probability ranking principle]]: show documents in order of their chance of being relevant. Rank by the odds, not the probability, because the odds cancel out the parts that do not depend on the document.
- [[Binary independence model]]: each word's presence is treated as independent given relevance, which makes the score a sum over query words.
- [[Term frequency saturation]]: the diminishing gain from repeated words, a curve of the form $f/(k+f)$ that rises fast and then levels off.
- [[Relevance feedback]]: use the documents a user marked as relevant to pick new query words.
- [[Document length normalisation]]: dividing a count by a length-dependent amount, so long documents do not win by size alone.

## Questions

- Why rank by the odds of relevance instead of the probability itself?
- Why does a repeated word stop adding score, and is that a fact about language or a modelling choice?
- Why can't the BM25 score be read as a calibrated probability?
- Which of the two length explanations would predict better behaviour on short queries?

## Follow-ups

**Read**:
- [[Okapi at TREC]]: where the formula first appeared, with the experiments this monograph leaves out (not in library).
- [[A Language Modeling Approach to Information Retrieval]]: the main rival, which scores documents by how likely they are to generate the query (not in library).
- [[Divergence from randomness]]: the other family of models the monograph compares to (not in library).

**Try**:
- Score three short documents by hand with the formula, doubling one document's term count, and watch the score level off.
