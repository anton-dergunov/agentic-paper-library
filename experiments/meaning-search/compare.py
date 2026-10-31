"""Two runs compared on the judged queries, query by query.

    PAPER_LIBRARY=<library> uv run --with bm25s python compare.py <encoder>:<variant> <encoder>:<variant>

e.g. `compare.py qwen3:tsa qwen3:body`. Prints each run's nDCG@10, P@10, R@10, R@10 (grade 2)
and MAP@10, then the second's nDCG@10 minus the first's: the mean, its 95% interval from a
paired bootstrap over the queries (10,000 resamples, fixed seed), and how many queries it is
better and worse on. Ungraded papers count as not relevant: run judge.py first.
"""
import sys

import numpy as np

from common import judged_queries, papers
from judge import judged
from score import judged_scores


def main(argv):
    if len(argv) != 2 or not all(":" in a for a in argv):
        sys.exit(__doc__)
    rows, queries, grades = papers(), judged_queries(), judged()
    scored = [judged_scores(rows, tuple(a.split(":", 1)), queries, grades) for a in argv]
    for name, (s, _) in zip(argv, scored):
        print(f"{name:<14} nDCG@10 {s['ndcg']:.3f}  P@10 {s['p10']:.3f}  R@10 {s['r10']:.3f}  "
              f"R@10(2) {s['r10_2']:.3f}  MAP@10 {s['map10']:.3f}  ungraded {s['missing']:.0%}")
    ids = [q["id"] for q in queries]
    diff = np.array([scored[1][1][i] - scored[0][1][i] for i in ids])
    means = diff[np.random.default_rng(0).integers(0, len(ids), (10_000, len(ids)))].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    print(f"{argv[1]} minus {argv[0]}: {diff.mean():+.3f} nDCG@10, 95% interval {low:+.3f} to {high:+.3f}, "
          f"better on {(diff > 0.001).sum()} queries, worse on {(diff < -0.001).sum()}")


if __name__ == "__main__":
    main(sys.argv[1:])
