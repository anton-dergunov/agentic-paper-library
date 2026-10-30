# DBSCAN Revisited, Revisited: Why and How You Should (Still) Use DBSCAN

type: study
family: density-based clustering; index-accelerated range queries (rebuttal of Gan & Tao, SIGMOD 2015)
evidence: runtime re-runs on the three Gan & Tao datasets (Household, Farm, PAMAP2), on one PC, sweeping ε. The runs compare Gan & Tao's binary (their new ρ-approximate method, GriDBSCAN, R-tree, KDD'96 reimplementation) with ELKI 0.7.0 Java (R*-tree, k-d-tree, cover tree) and the authors' own C++ DBSCAN (ANN k-d-tree, cover tree); strength: one machine, runtimes shown only in plots, no cluster-quality evaluation, written by the authors of the original DBSCAN

## Digest

- Technical correspondence answering Gan & Tao's SIGMOD 2015 paper. The authors accept its Ω(n^4/3) lower bound for Euclidean DBSCAN in d ≥ 3 (p. 5). They dispute four things:
  - the "17-year mis-claim" framing;
  - calling DBSCAN "intractable";
  - restricting DBSCAN to Euclidean distance;
  - an experimental setup with ε chosen far too large (pp. 5–7).
- The original KDD'96 O(n·log n) figure is conceded to be wrong. It was an informal average-case claim resting on an unproven O(log n) cost for R*-tree range queries. The O(n²) worst case was already stated in earlier sources, e.g. GDBSCAN (pp. 5–6).
- Algorithm 1 runs exactly one range query per point. Its runtime is O(C + n·Q + Σ r_i), with C the index build cost, Q the query cost and r_i the result sizes. With a linear scan it is Θ(n²·D), with D the cost of one distance computation (pp. 3–4).
- Border points reachable from several clusters go to the first cluster found. Footnote 1 says this can rarely leave a cluster with fewer than minPts points (p. 4).
- Theorems 3.1 and 3.2 reduce USEC to ε-range queries and BCP to nearest-neighbour queries. If those problems are Ω(n^4/3), then either a range or nearest-neighbour query costs Ω(n^1/3), or preprocessing costs Ω(n^4/3) (p. 8).
  - The authors conclude that no universal index gives O(log n) queries with O(n log n) construction (p. 9).
  - Cover-tree and navigating-net O(log n) claims rest on growth-restriction assumptions (p. 9).
- Critique of the grid-based approach:
  - The cells intersecting a boundary number O(1 + (1/ρ)^(d−1)), and Gan & Tao suggest ρ = 1/1000 (p. 10). The exponent is garbled in the text layer.
  - The method is limited to point data with Minkowski/Euclidean distance. DBSCAN can use R*-trees with cosine, divergence or geodetic distances, cover-trees and M-trees for metrics, and inverted indexes for text (p. 10).
- Parameter heuristics:
  - minPts = 4 for 2-D data, from the original DBSCAN paper, or minPts = 2·dim from GDBSCAN (p. 11).
  - ε is chosen from a sorted k-distance plot with k = 2·dim − 1; footnote 4 gives minPts = k + 1 (p. 11).
- Red flags for a degenerate result (p. 12):
  - Noise outside 1%–30%.
  - Largest cluster holding more than 20% to 50% of the clustered points. In that case use OPTICS or HDBSCAN*, or rerun DBSCAN with a smaller ε.
- Household dataset: 7 attributes, normalised to integers. The text layer prints the range as "[0; 105]", which is garbled. The data has 5% duplicate records and 32 to 4,186 distinct values per attribute (p. 11).
  - The k-dist plot for k = 4, 13, 99 suggests a cut between ε ≈ 500 and ε ≈ 2,000, with ε ≤ 1,000 usually better (p. 12, Figure 2).
  - At Gan & Tao's minimum ε = 5,000, more than 99% of the data sits in one cluster (p. 12, Figure 3).
  - The noise heuristic gives ε < 500 and the largest-component heuristic gives ε ≤ 400. The "interesting" range is ε = 100 to 500 (pp. 12–13).
- At ε < 1,000 on Household, the largest cluster holds about 29% of the data, and 84% of the data falls into 47 clusters (p. 14).
- Reducing ε from 5,000 to 1,000 in 7 dimensions multiplies the theoretical number of grid cells by 78,125 (printed as "57 = 78,125", i.e. a garbled exponent) (p. 14).
- Runtime results are given only in figures (p. 14, Figure 5; pp. 14–16, Figures 6 and 8):
  - For ε < 500, all indexes give a "10- to 1000-fold speedup" over the linear scan (p. 14, Figure 5).
  - Up to ε = 2,000, Gan & Tao's new method is slower than their own GriDBSCAN and their own R-tree. GriDBSCAN degrades to a linear scan only at ε ≥ 3,000 (p. 14, Figure 5).
  - The ANN k-d-tree was usually the fastest (p. 14).
- Farm dataset: the interesting range is ε ∈ [400; 1,000], probably around 900 (pp. 14–15, Figure 6). The authors suggest the data may hold no meaningful density-based clusters (p. 15).
- PAMAP2 dataset: the interesting range is ε ∈ [500; 2,000]. At ε = 5,000 two clusters cover 99.6% of the data (p. 15, Figure 8).
  - The authors guess that Gan & Tao left the timestamp in before PCA. This is their inference from scatter plots (p. 15, Figure 10), not something verified.
- What the paper leaves out:
  - No numeric runtime table.
  - No evaluation of cluster quality or utility, which the conclusion admits is needed (p. 19).
  - No comparison against STING, DenClue, OPTICS, HDBSCAN*, or approximate-neighbour DBSCAN; the authors say these would have been desirable (pp. 16–17).
  - Gan & Tao's method was run only as their supplied binary; reimplementing it is called hard because the BCP subroutine is not specified (p. 17).
- The general claim that DBSCAN with indexes "performs competitively" (p. 19) rests on three datasets and on plots alone.
- The paper's own inconsistencies:
  - A core point is defined as having "more than minPts neighbors" (p. 2), but Algorithm 1 marks a point as noise only if |N| < minPts, so ≥ minPts makes it core (p. 4).
  - For Household, the "interesting" ε range is 100 to 500 (pp. 12–13), yet ε < 1,000 is said to still give interesting clusters, and the k-dist plot suggests 500–2,000 (p. 12; p. 14).

## Related in library

- A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise: the original DBSCAN, whose model, algorithm and O(n·log n) claim this paper defends and corrects.
- Density-Based Clustering Based on Hierarchical Density Estimates: HDBSCAN* is cited as removing border points, and it is recommended when ε is hard to choose or the largest cluster is too big.
- Scikit-learn. Machine Learning in Python: cited for its vectorised DBSCAN variant, which uses quadratic memory, and for recommending DBSCAN for very large n.
