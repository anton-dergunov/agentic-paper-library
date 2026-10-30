# DBSCAN Revisited, Revisited: Why and How You Should (Still) Use DBSCAN

type: position
family: density-based clustering; a rebuttal on DBSCAN's complexity and how to choose its parameters
evidence: re-runs Gan and Tao's (SIGMOD 2015) binary and datasets (Household, Farm, PAMAP2) against linear scan, R*-tree, k-d tree and cover tree DBSCAN (ELKI Java plus the authors' own C++), and against Gan and Tao's own GriDBSCAN, R-tree and KDD'96 implementations; strength: one machine, three datasets, results shown only in plots, written by the original DBSCAN authors (an interested party)

## Digest

- **Purpose.** This is a technical correspondence answering Gan and Tao's SIGMOD 2015 "DBSCAN Revisited". It accepts their Ω(n^4/3) lower bound for Euclidean DBSCAN when d ≥ 3. It disputes their claims that DBSCAN is "intractable in practice" and that their approximate method "should replace DBSCAN on big data" (p. 1, p. 7).
- **Concession on the runtime claim.** The KDD'96 O(n·log n) runtime was an informal average-case claim. It rested on a wrong assumption that "small" range queries in an R*-tree cost O(log n). It was not a worst-case claim. The worst-case O(n²) was already known, for example from Sander et al. (pp. 5–6).
- **Algorithm and cost.** The original algorithm runs exactly one RangeQuery per point. Its runtime is O(n·Q + Σ r_i), plus index construction time C. With a linear scan it is Θ(n²·D), where D is the cost of one distance computation. With expensive distances such as shared-nearest-neighbour distance it can reach O(n³) (pp. 3–4). The summation term is garbled in the extracted text.
- **New theorems (Theorems 3.1 and 3.2).**
  - USEC can be solved by ε-range queries, and BCP by nearest-neighbour queries.
  - So if these problems are Ω(n^4/3), a single range query or nearest-neighbour query costs at least Ω(n^1/3), or preprocessing costs at least Ω(n^4/3) (p. 8).
  - Consequence: no universal index gives O(log n) queries with O(n log n) construction (p. 9).
  - The authors cite Erickson to argue that bounds of this kind were already known for problems that need n range queries (pp. 7–9).
- **Generality argument.** DBSCAN is not limited to Euclidean distance or to points. It can use R*-trees with cosine, divergence or geodetic distances, M-trees and cover trees, or inverted indexes. Gan and Tao's grid method supports only point data with Minkowski-type distances (p. 10).
- **Dimensionality cost of the grid method.** Gan and Tao's method has O(1 + (1/ρ)^{d−1}) boundary cells; with ρ = 1/1000 this is O(1 + 1000^{d−1}) (p. 10).
- **Parameter heuristics.**
  - minPts = 4 for 2-D data, or minPts = 2·dim (Sander et al.).
  - Choose ε from the sorted k-distance plot, using k = minPts − 1 (p. 11).
- **Household k-distance plots.** They suggest a cut between ε ≈ 500 and ε ≈ 2,000, with lower values, e.g. ε ≤ 1,000, typically working better (p. 12, Figure 2). Gan and Tao's minimum ε = 5,000 lies where the curve is still dropping steeply (p. 12).
- **"Red flags" for degenerate results.**
  - Noise should usually lie between 1% and 30%.
  - If the largest cluster holds more than 20% to 50% of the clustered points, reduce ε or switch to OPTICS or HDBSCAN* (p. 12).
- **Household results under the red flags.**
  - At ε = 5,000, more than 99% of the data is in one cluster.
  - The noise heuristic suggests ε < 500; the largest-component heuristic suggests ε ≤ 400.
  - The resulting interesting range is ε = 100 to 500 (pp. 12–13, Figure 3).
  - Sudden jumps near ε ≈ 500 and ε ≈ 3,500 are artifacts of low numerical resolution: attributes have as few as 32 distinct values, and 5% of records are duplicates (pp. 11–12).
- **Interesting ε ranges on the other datasets.** Farm: ε ∈ [400; 1,000] (p. 14, Figure 6(c)). PAMAP2: ε ∈ [500; 2,000]; at ε = 5,000 two clusters cover 99.6% of the data (p. 15, Figure 8(b)).
- **PAMAP2 preprocessing.** The authors suspect Gan and Tao did not remove the timestamp before PCA. They say the data should have been analysed as time series (pp. 15–16). This is stated as an inference ("likely") from scatter plots (Figure 10).
- **Grid-cell growth.** Lowering ε from 5,000 to 1,000 on 7-D data multiplies the theoretical number of grid cells by 5^7 = 78,125 (p. 14).
- **Runtime results (p. 14, Figure 5; Figures 6 and 8).**
  - For ε < 500, all indexes give a 10- to 1000-fold speedup over linear scan.
  - Up to ε = 2,000, Gan and Tao's new method is slower than their own GriDBSCAN and their own R-tree implementation.
  - The ANN k-d tree was usually the fastest.
  - At ε < 1,000, the largest cluster holds about 29% of the data, and 84% of the data falls into 47 clusters.
  - All of these appear only in plots; there are no tables.
- **Fairness caveats.** Comparing ELKI's Java runtimes with C++ is acknowledged as unfair. The authors could not reimplement Gan and Tao's method because efficient BCP details are missing, and they evaluated it only through Gan and Tao's binary (pp. 14, 17).
- **Omissions.** Cluster utility is not evaluated, and the authors concede the datasets may not hold meaningful clusters (p. 19). There is no comparison with approximate-neighbour DBSCAN, STING, DenClue, OPTICS or HDBSCAN* (pp. 16–17).
- **Where the conclusion claims more than the evidence.** The conclusion says the original DBSCAN "performs competitively" with Gan and Tao's method. That rests on plot-only comparisons on three datasets in the ε range the authors chose.
- **Garbled text.** The "not equal" symbols in Algorithm 1, lines 2 and 12, are missing from the extracted text (p. 4). So is the comparison sign in "below ε 2,000" (p. 12).
- The paper's own inconsistencies: a core point is defined as having "more than minPts neighbors" (p. 2), but Algorithm 1 treats |N| < minPts as non-core, so exactly minPts neighbours makes a core point (p. 4).

## Related in library

- A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise: the original DBSCAN paper, whose model, heuristics and informal O(n log n) claim this paper defends and corrects.
- Density-Based Clustering Based on Hierarchical Density Estimates: HDBSCAN* is cited as the variant without border points and as the recommended alternative when ε is hard to choose.
- Scikit-learn. Machine Learning in Python: cited for its vectorised DBSCAN variant and for recommending DBSCAN for very large n.
