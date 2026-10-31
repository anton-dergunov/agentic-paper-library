# The Probabilistic Relevance Framework: BM25 and Beyond

type: survey
family: probabilistic relevance models (binary independence, BM25 and BM25F term weighting)
evidence: no experiments of its own; quotes TREC 2003 BM25F parameter values from [62] (Table 3.1, p. 35) and states parameter ranges and robustness from unreferenced experiments; strength: no new experiments, no baselines given for the quoted numbers

## Digest

- Scope: a conceptual monograph. It says it is "not primarily an experimental survey" and that its claims about what "works well" derive from experiments "which will not in general be fully referenced" (p. 5). Page numbers follow the [page N] markers, not the printed journal pagination.
- Claim: applying the Probability Ranking Principle to a single user's query justifies ranking documents by $P(rel \mid d,q)$, and the derivation yields a sum of per-term weights over query terms present in the document (p. 8, p. 10, Eq. 2.11). Relevance is assumed binary and judged per document; the authors call both assumptions "at least arguable" (p. 7).
- Derivation steps: odds ratio, Bayes inversion, conditional term independence for relevant and non-relevant cases, restriction to query terms, log, and removal of zero-frequency terms (p. 10–15). The independence step is justified by Naive Bayes experience and Cooper's linked-dependence argument, with no numbers (p. 11–12).
- Basic term weight (Eq. 2.14, p. 14), with $\overline{rel}$ denoting non-relevance (overbars were lost in extraction):
  $w_i = \log \frac{P(TF_i=tf_i \mid rel)\,P(TF_i=0 \mid \overline{rel})}{P(TF_i=tf_i \mid \overline{rel})\,P(TF_i=0 \mid rel)}$
- Binary independence model (Eq. 3.1, p. 17). The RSJ weight (Eq. 3.2, p. 18) adds a pseudo-count of 0.5 to avoid infinities. Setting $R = r_i = 0$ gives $\log\frac{N-n_i+0.5}{n_i+0.5}$, an idf-like weight (Eq. 3.3, p. 19).
- Feedback: the complement method treats unjudged documents as non-relevant and is said to beat judged-only estimates, with no figures (p. 19). Query expansion ranks candidate terms by offer weight $OW_i \propto r_i w_i^{RSJ}$ (Eq. 3.5, p. 21) and adds "the top x terms" (x "of the order of 10", p. 21).
- Blind feedback assumes the top y documents are relevant (y "say 5 or 10", p. 21). The text says it "tends to fail on some queries" but gives no figures (p. 21–22).
- Eliteness and 2-Poisson model: each term-document pair has a hidden eliteness variable; term frequency is Poisson given eliteness (Eq. 3.7, p. 24). The weight rises toward $w^{BIM}$ as tf grows, the "saturation" property (Eqs. 3.8–3.9, p. 26). The BM25 saturation $tf/(k+tf)$ (Eq. 3.10, p. 27) is a curve chosen to fit the 2-Poisson shape, not derived from a corpus model.
- Length normalisation: $B=(1-b)+b\,dl/avdl$ (Eq. 3.12, p. 29), where $dl$ is document length and $avdl$ the collection average. It is motivated by a verbosity-versus-scope argument (p. 28–29). The final BM25 weight, with $b$ and $k_1$ as free parameters, is $w^{BM25}=\frac{tf}{k_1\left((1-b)+b\,dl/avdl\right)+tf}\,w^{RSJ}$ (Eqs. 3.13–3.15, p. 30). This is reconstructed from the garbled layout of Eq. 3.15 and its algebra.
- Parameter ranges are asserted, not shown: "values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many circumstances" (p. 30). A "common combination" is b = 0.5, k1 = 2 (p. 31). These rest on "a significant number of such experiments", which are not cited or reported.
- BM25F: stream frequencies are combined as $tf_i=\sum_s v_s\,tf_{si}/B_s$ with per-stream $B_s=(1-b_s)+b_s\,sl_s/avsl_s$ (Eqs. 3.19–3.20, p. 34). The authors argue saturation should follow stream aggregation, since eliteness is a term-document property (p. 32–33). The simple version is equivalent to BM25 on a document with streams replicated (p. 35).
- Only numbers in the paper (Table 3.1, p. 35): BM25F parameters from [62] for TREC 2003 topic distillation (TD'03) and name page (NP'03), printed as TD'03 / NP'03. $k_1$: 27.5 / 4.9. $b_{title}$: 0.95 / 0.6. $b_{body}$: 0.7 / 0.5. $b_{anchor}$: 0.6 / 0.6. $v_{title}$: 38.4 / 13.5. $v_{body}$: 1.0 / 1.0. $v_{anchor}$: 35 / 11.5. No effectiveness results or baselines appear in the text. The $k_1$ values lie outside the 1.2–2 range given on p. 30, and the text does not discuss this.
- Non-textual features (p. 35–37): the score adds $\lambda_i V_i(f_i)$ terms to the textual sum (Eq. 3.22, p. 36), with $V_i(f_i)=\log\frac{P(F_i=f_i\mid rel)}{P(F_i=f_i\mid\overline{rel})}$ (Eq. 3.23, p. 36). The text says "BM25F(q,d)+log(PageRank(d)) may work well in practice" and that a sigmoid gives "only slightly" more (p. 37). No numbers are given.
- Positional information (p. 37–39) is outside the PRF. The authors say proximity gains in cited works are "small" yet "statistically significant" over non-positional baselines, and offer two untested hypotheses. They state they know of no studies on why (p. 38–39).
- Optimisation (Section 5, p. 47–53): Robust Line Search splits the interval into "m equal parts" with m unspecified (p. 49). Parameters are gridded to the second decimal (p. 49). Greedy multidimensional search is "not practicable for large n (e.g., n > 3)" (p. 50). The text says tuning gives "significant gains" (p. 47) but gives no numbers. Gradient methods are out of scope (p. 52–53).
- Comparisons (Section 4, p. 41–46) are conceptual: Maron and Kuhns, the Unified Model's Models 0–3 (p. 42–43), the simple and relevance language models (p. 43–45), and divergence from randomness, "approximately the same as BM25" (p. 46). No experiments compare them.
- Implementations (p. 39–40): the authors say MG4J fully implements BM25F. They inspected code visually, did not run tests, and report that two implementations were incorrect and were corrected.
- Undisclosed: the test collections and metrics behind the quoted parameter ranges and robustness claims; the scale of the "many experiments" cited on p. 30 and p. 47. PRP-based rank equivalence means the scores are not probabilities, and explicit probability estimation is "not discussed further" (p. 15–16).
- Extraction problems: overbars (complement probabilities) are lost throughout, including in Eqs. 2.1–2.14, 3.1, 3.4, 3.6 and 3.8. Eqs. 3.15, 3.18 and the sigmoid $V_i$ on p. 37 have broken layout or lost subscripts. Formulas in this note are rewritten from the text.

## Related in library

## Q&A
