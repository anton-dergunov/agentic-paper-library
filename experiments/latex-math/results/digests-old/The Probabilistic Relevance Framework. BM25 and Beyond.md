# The Probabilistic Relevance Framework: BM25 and Beyond

type: survey
family: probabilistic relevance framework (BM25 family of term-weighting and scoring models)
evidence: no experiments run by the authors; cites unreported TREC-style results; Table 3.1 gives BM25F parameter values from [62] on TREC 2003 topic-distillation and name-page tasks, with no effectiveness scores (p. 35, Table 3.1); strength: no own experiments, no effectiveness numbers in the text

## Digest

- Claim: the PRF is a family of retrieval models built on the Probability Ranking Principle (PRP), which ranks documents by probability of relevance. The monograph is conceptual, not experimental: "This is not primarily an experimental survey," and the empirical claims "will not in general be fully referenced" (p. 5).
- PRP as stated: "If retrieved documents are ordered by decreasing probability of relevance on the data available, then the system's effectiveness is the best that can be obtained for the data." It is applied to a single user and query, not to a population of users (p. 8).
- Relevance is assumed binary and judged per document, without reference to other documents (p. 7). The paper says both assumptions are "at the least arguable" (p. 7).
- Mechanism: odds-ratio, Bayes inversion and log transforms, all rank-preserving. Term independence is assumed conditionally on relevance and on non-relevance. Only query terms are kept. The score is a sum of weights w_i over query terms present in the document (Eq. 2.11, p. 10). The paper calls the independence step "clearly a much more arguable step" (p. 11).
- The non-relevance overbars are lost in the text file for Eqs. 2.12–2.15, 3.1, 3.6, and footnotes 4–5 (pp. 13–14, 17, 24). Relevance versus non-relevance is therefore read from the surrounding prose, not from the equations.
- Binary weight with RSJ estimate (Eq. 3.2, p. 18) uses a 0.5 pseudo-count. Setting R = r_i = 0 gives IDF (Eq. 3.3, p. 19), which the paper calls "a close approximation to classical idf" (p. 19).
- Offer weight: OW_i = (P(t_i|rel) − P(t_i|rel̄)) w_i (Eq. 3.4, p. 20), approximated by r_i·w_i^RSJ (Eq. 3.5, p. 21). The paper says to add "only the top x terms," with x "of the order of 10" (p. 21).
- Eliteness is a hidden term–document property (p. 22). The 2-Poisson model yields a saturating tf weight whose asymptote is the binary weight w^BIM (Eqs. 3.8–3.9, p. 26). The paper says this behaviour is "established only for the 2-Poisson case" (p. 26).
- BM25 (Eq. 3.15, p. 30) combines the saturation tf/(k1+tf) with w^RSJ, using length normalisation with 0 ≤ b ≤ 1. The paper says the saturation curve was fitted, not derived from a corpus model (p. 28, Eq. 3.10). The denominator of Eq. 3.15 is split across lines in the text file, so it is not quoted exactly.
- Parameter ranges: "values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many circumstances" (p. 30). A "common combination" is b = 0.5, k1 = 2, with "many experiments suggest a somewhat lower value of k1 and a somewhat higher value of b" (p. 31). No source experiments are cited for these ranges.
- BM25F (Eq. 3.21, p. 34) sums weighted stream term frequencies (v_s) and applies a stream-specific length normalisation (b_s). The text argues that eliteness should be term/document-level, so saturation is applied after pooling across streams (pp. 32–33).
- Table 3.1 (p. 35), TD'03 / NP'03: k1 = 27.5 / 4.9; b_title 0.95 / 0.6; b_body 0.7 / 0.5; b_anchor 0.6 / 0.6; v_title 38.4 / 13.5; v_body 1.0 / 1.0; v_anchor 35 / 11.5. The text gives no scores for these settings. The k1 values lie outside the 1.2–2 range stated on p. 30. The paper attributes this to k1 rescaling with stream weights (p. 51, Eq. 5.1).
- Non-textual features enter as λ_i·V_i(f_i) with a free λ_i (Eq. 3.22, p. 36). "BM25F(q,d)+log(PageRank(d)) may work well in practice" (p. 37). The sigmoid form of V_i (p. 37) is garbled in the text file, so it is not quoted as exact.
- Positional information is largely left out. The paper says the reported improvements are "small" and that the cited works "all claim statistically significant improvements," but gives no figures (p. 39). It proposes two untested hypotheses for why position matters little (p. 39).
- Comparisons with other models (pp. 41–46) are qualitative: the Maron–Kuhns model, the unified model with Models 0–3 (p. 43), the simple LM, the relevance LM with KL divergence (p. 45), and DFR, which gives "approximately the same as BM25" (p. 46).
- Optimisation (pp. 47–53) covers robust line search, greedy recursive search (called "impracticable for large n (e.g., n > 3)," p. 50), promising-directions search, and batched scheduling. Caching and a grid to "the second decimal" are used (pp. 48–49). The text reports no before/after gains; Figs. 5.1–5.2 are illustrative.
- Claims that outrun the text's evidence: that BM25 and BM25F are "quite robust with respect to their parameters" (p. 47); that the complement method "gives better estimates" (p. 19); and that the saturating function "has frequently been shown to work better than traditional tf*idf" (p. 26). None of these gives a number or citation.
- Extraction and garbling: the footnote 1 PF/Tijah IDF formula (p. 40), the BM25F k1 scaling Eq. 5.1 (p. 51), and the sigmoid V_i (p. 37) are garbled in the text file. Page numbers here are the [page N] markers; printed folios are N + 330 from N = 4 onward.

## Related in library

## Q&A
