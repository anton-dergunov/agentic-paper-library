# DBSCAN Revisited, Revisited: Why and How You Should (Still) Use DBSCAN

type: position
family: density-based clustering; DBSCAN complexity, indexing and parameter heuristics
evidence: runtime against ε on three datasets supplied by Gan and Tao (Household, Farm, PAMAP2). Compared: Gan and Tao's C++ binary (their new method, plus their GriDBSCAN, R-tree and KDD'96 reimplementations), ELKI 0.7.0 Java DBSCAN with R*-tree, k-d-tree and cover tree, and the authors' own C++ DBSCAN on an ANN k-d-tree and on a cover tree; strength: a reproduction on one machine by the critics; runtime results are shown only in figures; no evaluation of cluster quality or utility; repeats and variance not reported

## Digest

- This is a technical correspondence rebutting Gan and Tao (SIGMOD 2015, "DBSCAN Revisited: Mis-Claim, Un-Fixability, and Approximation"). The authors accept Gan and Tao's lower bound but dispute three things:
  - that DBSCAN is "intractable in practice";
  - that DBSCAN is restricted to Euclidean distance;
  - the experimental support for the claim that ρ-approximate DBSCAN "should replace DBSCAN on big data" (pp. 2, 5, 7).
- Model (p. 2): a point is a core point if enough neighbours, counting itself, lie within radius ε.
  - Neighbours of core points are direct density reachable; chaining these links gives density reachable.
  - Non-core members of a cluster are border points; points not reachable from any core point are noise.
  - DBSCAN is described as a uniform kernel with bandwidth h = ε and density threshold minPts/n (p. 3).
- Algorithm (pp. 3–4, Algorithm 1): exactly one RangeQuery is run per point. Runtime is O(C + n·Q + Σ r_i), where Q is the range-query cost, r_i the result sizes and C the index construction cost.
  - The sum is garbled in the text layer, so the formula above is not an exact quote.
  - A linear scan gives Θ(n²·D), or Θ(n²·d) in Euclidean space; an expensive shared-nearest-neighbour distance can give O(n³) (pp. 3–4).
- Border points reachable from several clusters go to the first cluster found. The result is deterministic but depends on the order of the data. In rare cases a cluster can end up with fewer than minPts points (p. 4, footnote 1).
- The authors concede that the O(n log n) average runtime in the original paper rested on a wrong assumption: that "small" R*-tree range queries take O(log n). They argue it was an informal average-case statement, not a worst-case claim. They also argue that the O(n²) worst case was already known, for example from GDBSCAN, and was not a new finding of Gunawan's thesis (pp. 5–6).
- Theory (p. 8, Theorems 3.1 and 3.2), for d ≥ 3: if USEC or BCP is Ω(n^{4/3}), then an ε-range or nearest-neighbour query costs at least Ω(n^{1/3}), or preprocessing costs at least Ω(n^{4/3}).
  - Consequence (p. 9): no universal index guarantees O(log n) queries with O(n log n) construction.
  - Ω(n^{4/3}) still leaves room for speedups over the Θ(n²) linear scan (p. 9).
- Critique of grids (p. 10): Gan and Tao's method touches O(1 + (1/ρ)^{d−1}) boundary cells, which is O(1 + 1000^{d−1}) at the suggested ρ = 1/1000. Their analysis treats dimensionality as a constant.
  - Grid methods need point data and Minkowski distances. DBSCAN with an R*-tree, M-tree or cover tree works with other distances.
- Parameter heuristics (p. 11):
  - minPts = 4 for 2-D data, or minPts = 2·dim.
  - Choose ε as small as possible, using the "elbow" of the sorted k-distance plot.
  - On Household the plots use k = 4, 13 and 99; k = 99 corresponds to Gan and Tao's minPts = 100.
- Household data (p. 11): 5% duplicate records, 32 to 4,186 distinct values per attribute, normalised to integers. The range prints as "[0; 105]", where 10^5 is evidently meant; the exponent is garbled.
- k-distance reading on Household (p. 12, Figure 2): the cut falls between ε ≈ 500 and ε ≈ 2,000, and lower values (ε ≤ 1,000) typically work better. By contrast, Gan and Tao use ε ≥ 5,000. The phrase "below ε 2,000" has a symbol missing.
- "Red flags" for degenerate results (p. 12):
  - noise should usually be between 1% and 30%;
  - if the largest cluster holds more than 20% to 50% of the clustered points, use a smaller ε, OPTICS or HDBSCAN*.
- Household under these flags (pp. 12–13, Figure 3):
  - at ε = 5,000, more than 99% of points are in one cluster;
  - at ε ≈ 500 and ε ≈ 3,500 the cluster count drops while the largest component grows from 5% to 30% and from 40% to 95%; the authors attribute both jumps to low-resolution artefacts;
  - the heuristics suggest ε < 500 (noise) and ε ≤ 400 (largest component), giving an interesting range of ε = 100 to 500;
  - in the OPTICS plot (p. 13, Figure 4), valleys vanish at ε ≈ 2,500 and some structure needs ε < 1,500.
- Grid-cell argument (p. 14): reducing ε from 5,000 to 1,000 on 7-dimensional data multiplies the theoretical number of grid cells by 5^7 = 78,125. The authors suggest this is why Gan and Tao's runtime falls as ε grows.
- Runtime on Household (p. 14, Figure 5):
  - at ε < 1,000 the largest cluster holds about 29% of the data, and 84% of the data falls into 47 clusters;
  - for ε < 500, all indexes give a 10- to 1000-fold speedup over linear scan;
  - up to ε = 2,000, Gan and Tao's new method is slower than their own GriDBSCAN and R-tree implementations;
  - GriDBSCAN degrades to a linear scan for ε ≥ 3,000;
  - the ANN k-d-tree was usually fastest.
  - The authors note that comparing ELKI (Java, double precision) with C++ code is unfair.
- Farm data (pp. 14–16, Figures 6–7): the interesting range is ε ∈ [400; 1,000], probably around ε = 900. The authors say the data may not contain meaningful density-based clusters.
- PAMAP2 data (pp. 15–16, Figures 8–10):
  - the interesting range is ε ∈ [500; 2,000];
  - at ε = 5,000, two clusters account for 99.6% of the data;
  - the authors suspect Gan and Tao did not remove the timestamp before PCA, and say the data should have been treated as time series.
- Scope of the comparison: the "outperformed in the interesting range" verdicts for Farm and PAMAP2 rest only on the figures (p. 16).
  - The conclusion generalises the 10- to 1,000-fold speedup to "reasonably small ε" (p. 18), but the explicit statement on p. 14 is for ε < 500 on Household.
  - The authors admit the benchmark datasets may be the "wrong" ones (p. 19).
  - They give no comparison against approximate neighbour search, OPTICS, HDBSCAN*, STING or DenClue; they say these comparisons would have been desirable (pp. 16–17).
- The paper's own inconsistencies:
  - The text defines a core point as having "more than minPts neighbors" (p. 2), but Algorithm 1 treats |N| < minPts as non-core, so exactly minPts already counts as core (p. 4).
  - Footnote 4 maps k nearest neighbours to minPts = k + 1. That conflicts with pairing the fourth-nearest-neighbour heuristic with the default minPts = 4 (p. 11).

## Related in library

- A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise: the original DBSCAN, whose model, algorithm and O(n log n) statement this paper defends and corrects.
- Density-Based Clustering Based on Hierarchical Density Estimates: HDBSCAN* is recommended as the alternative when ε is hard to choose or the largest cluster is too big.
- Scikit-learn. Machine Learning in Python: cited for its vectorised DBSCAN variant and for recommending DBSCAN for very large numbers of samples.

## Q&A
