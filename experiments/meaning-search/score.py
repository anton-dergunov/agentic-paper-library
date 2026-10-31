"""Score every run and write results/scores.md.

    PAPER_LIBRARY=<library> uv run --with bm25s python score.py

- Topic agreement@10: the share of a paper's 10 nearest papers in its folder, and in its
  top-level area; random neighbours as the baseline.
- Scope as query: each leaf topic's scope line (topics.yaml) as a query, its folder's papers
  as gold: R-precision and nDCG@20.
- Judged queries: nDCG@10 (gains 2^grade - 1, the ideal from every grade the query has);
  P@10, R@10 and MAP@10 with grade 1 or 2 as relevant, and R@10 of the grade-2 papers; the
  share of a run's top 10 left ungraded (counted as not relevant). Each run
  is compared with the best one query by query: the mean difference in nDCG@10 and its 95%
  interval from a paired bootstrap over the queries (10,000 resamples, fixed seed).
"""
import json
import math
import sys

import numpy as np

from common import RESULTS, judged_queries, papers, relative, scope_queries
from judge import judged
from rank import neighbours, runs, top


def ndcg(gains, ideal, k):
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains[:k]))
    best = sum(g / math.log2(i + 2) for i, g in enumerate(sorted(ideal, reverse=True)[:k]))
    return dcg / best if best else 0.0


def topic_agreement(rows, nearest):
    leaf = np.array([t for _, t, _ in rows])
    area = np.array([t.split("/")[0] for t in leaf])
    return float((leaf[nearest] == leaf[:, None]).mean()), float((area[nearest] == area[:, None]).mean())


def random_agreement(rows):
    n = len(rows)
    leaf = [t for _, t, _ in rows]
    out = []
    for labels in (leaf, [t.split("/")[0] for t in leaf]):
        counts = {}
        for t in labels:
            counts[t] = counts.get(t, 0) + 1
        out.append(sum((counts[t] - 1) / (n - 1) for t in labels) / n)
    return out


def scope_scores(rows, run, scopes):
    leaf = [t for _, t, _ in rows]
    found = top(run, [s for _, s in scopes], k=max(leaf.count(t) for t, _ in scopes))
    rprec, nd = [], []
    for (topic, _), ranked in zip(scopes, found):
        gold = leaf.count(topic)
        hits = [1.0 if leaf[i] == topic else 0.0 for i in ranked]
        rprec.append(sum(hits[:gold]) / gold)
        nd.append(ndcg(hits, [1.0] * gold, 20))
    return float(np.mean(rprec)), float(np.mean(nd))


def average_precision(hits, relevant, k):
    """AP@k over binary hits, normalised by min(relevant, k): the most a top k can hold."""
    if not relevant:
        return 0.0
    found, total = 0, 0.0
    for i, hit in enumerate(hits[:k]):
        if hit:
            found += 1
            total += found / (i + 1)
    return total / min(relevant, k)


def judged_scores(rows, run, queries, grades):
    """Per run, the mean over queries of nDCG@10 (graded) and, counting grade 1 or 2 as
    relevant: P@10, R@10 and MAP@10; R@10 also for grade 2 alone. Relevant papers are the
    ones the judge graded so in the pool; an ungraded paper counts as not relevant."""
    found = top(run, [q["query"] for q in queries])
    m = {key: [] for key in ("ndcg", "p10", "r10", "r10_2", "map10")}
    missing, per = 0, {}
    for q, ranked in zip(queries, found):
        known = [g for (qid, _), g in grades.items() if qid == q["id"]]
        got = [grades.get((q["id"], relative(rows[i][0]))) for i in ranked]
        missing += sum(g is None for g in got)
        got = [g or 0 for g in got]
        relevant, strict = sum(g >= 1 for g in known), sum(g == 2 for g in known)
        m["ndcg"].append(ndcg([2 ** g - 1 for g in got], [2 ** g - 1 for g in known], 10))
        m["p10"].append(sum(g >= 1 for g in got) / 10)
        m["r10"].append(sum(g >= 1 for g in got) / relevant if relevant else 0.0)
        m["r10_2"].append(sum(g == 2 for g in got) / strict if strict else 0.0)
        m["map10"].append(average_precision([g >= 1 for g in got], relevant, 10))
        per[q["id"]] = m["ndcg"][-1]
    out = {key: float(np.mean(values)) for key, values in m.items()}
    out["missing"] = missing / (10 * len(queries))
    return out, per


def pool_sizes(queries, grades):
    """For each query: the papers judged, those graded 1 or 2, and those graded 2."""
    sizes = {}
    for (qid, _), g in grades.items():
        judged, relevant, strict = sizes.get(qid, (0, 0, 0))
        sizes[qid] = (judged + 1, relevant + (g >= 1), strict + (g == 2))
    return [sizes.get(q["id"], (0, 0, 0)) for q in queries]


def main(argv):
    rows = papers()
    scopes = scope_queries(rows)
    queries = judged_queries()
    grades = judged()
    cost = {}
    if (RESULTS / "cost.jsonl").exists():
        for line in open(RESULTS / "cost.jsonl", encoding="utf-8"):
            row = json.loads(line)
            cost.setdefault(row["encoder"], {}).update(row)  # body.py adds its own line
    table, per_query = [], {}
    for run in runs():
        leaf, area = topic_agreement(rows, neighbours(run))
        rprec, snd = scope_scores(rows, run, scopes)
        scored, per = judged_scores(rows, run, queries, grades)
        name = f"{run[0]} · {run[1]}"
        per_query[name] = per
        table.append((name, leaf, area, rprec, snd, scored))
        print(f"{name:<18} topic {leaf:.3f}/{area:.3f}  scope {rprec:.3f}/{snd:.3f}  judged nDCG {scored['ndcg']:.3f} "
              f"P {scored['p10']:.3f} R {scored['r10']:.3f} R2 {scored['r10_2']:.3f} MAP {scored['map10']:.3f} "
              f"({scored['missing']:.0%} ungraded)", flush=True)
    rleaf, rarea = random_agreement(rows)

    sizes = pool_sizes(queries, grades)
    ranked_rows = sorted(table, key=lambda r: -r[5]["ndcg"])
    out = ["# Scores", "",
           f"{len(rows)} papers; {len(scopes)} scope queries (leaf topics with 5 papers or more); "
           f"{len(queries)} judged queries, {len(grades)} grades. A judged query's pool holds "
           f"{np.median([s[0] for s in sizes]):.0f} papers (median), of which "
           f"{np.median([s[1] for s in sizes]):.0f} are graded 1 or 2 and {np.median([s[2] for s in sizes]):.0f} graded 2; "
           f"{sum(s[1] > 10 for s in sizes)} queries have more than 10 relevant papers, where R@10 cannot reach 1.", "",
           "## Judged queries", "",
           "Relevant for P, R and MAP: graded 1 or 2. R@10 (2): of the papers graded 2. MAP@10: AP normalised by min(relevant, 10).", "",
           "| Run | nDCG@10 | P@10 | R@10 | R@10 (2) | MAP@10 | Ungraded in top 10 |",
           "|---|--:|--:|--:|--:|--:|--:|"]
    for name, *_, j in ranked_rows:
        out.append(f"| {name} | {j['ndcg']:.3f} | {j['p10']:.3f} | {j['r10']:.3f} | {j['r10_2']:.3f} | {j['map10']:.3f} | {j['missing']:.0%} |")
    out += ["", "## Topics", "",
            "| Run | Topic@10 (folder) | Topic@10 (area) | Scope R-prec | Scope nDCG@20 |", "|---|--:|--:|--:|--:|"]
    for name, leaf, area, rprec, snd, _ in ranked_rows:
        out.append(f"| {name} | {leaf:.3f} | {area:.3f} | {rprec:.3f} | {snd:.3f} |")
    out.append(f"| random neighbours | {rleaf:.3f} | {rarea:.3f} | | |")
    out.append("")
    out.append("A `body` run's topic agreement is its `tsa` text's: its neighbours are found from that text.")
    out += ["", "## Cost (title, summary and abstract)", "",
            "| Encoder | Model | Revision | Dims | Max tokens | Library on MPS (s) | Query on MPS (ms) | CPU a paper (s) | Query on CPU (ms) | Peak memory (MB) |",
            "|---|---|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, c in cost.items():
        out.append(f"| {name} | `{c['model']}` | `{(c.get('revision') or '')[:10]}` | {c['dims']} | {c['max_tokens']} | "
                   f"{c.get('seconds_tsa')} | {c.get('query_ms')} | {c.get('cpu_seconds_a_paper')} | {c.get('cpu_query_ms')} | {c.get('peak_rss_mb')} |")
    ranked = [r[0] for r in ranked_rows]
    best = ranked[0]
    rng = np.random.default_rng(0)
    ids = [q["id"] for q in queries]
    picks = rng.integers(0, len(ids), size=(10_000, len(ids)))
    out += ["", f"## Paired against the best run, {best} (judged nDCG@10)", "",
            "| Run | Mean difference | 95% interval | Queries better / worse |", "|---|--:|--:|--:|"]
    for name in ranked[1:]:
        diff = np.array([per_query[name][i] - per_query[best][i] for i in ids])
        means = diff[picks].mean(axis=1)
        low, high = np.percentile(means, [2.5, 97.5])
        out.append(f"| {name} | {diff.mean():+.3f} | {low:+.3f} to {high:+.3f} | {(diff > 0.001).sum()} / {(diff < -0.001).sum()} |")
    names = [r for r in ranked if r.endswith("· tsa")]
    out += ["", "## Judged nDCG@10 by query (title, summary and abstract)", "",
            "| Query | " + " | ".join(n.split(" ·")[0] for n in names) + " |",
            "|---|" + "--:|" * len(names)]
    for q in queries:
        out.append(f"| {q['id']} {q['query']} | " + " | ".join(f"{per_query[n].get(q['id'], 0):.2f}" for n in names) + " |")
    (RESULTS / "scores.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
