"""Grade the pooled top 10s of the judged queries, TREC-style.

    PAPER_LIBRARY=<library> uv run --with bm25s python judge.py [--model sonnet] [--only q01,q02] [--dry-run]

Each run's top 10 for each query in queries.yaml is pooled; the papers not graded yet are put
to the judge in one request per query, in an order shuffled with a fixed seed (a list read in
file order is read with a position bias), each with its title, summary and abstract. Grades:
2 the paper is about what the query describes, 1 partly or a closely related aspect, 0 not.
Appends to results/judgements.jsonl; run it again after new runs to grade what they add.
"""
import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from common import RESULTS, abstracts, judged_queries, paperlib, papers, relative
from rank import runs, top

SYSTEM = """You judge search results in a researcher's library of papers.

The reader typed a description of what they are looking for. For each paper below, from its
title, summary and abstract, grade how well it matches:

2: the paper is about what the description asks for (a reader would want it in the results).
1: partly: it treats a closely related aspect, or the topic is a substantial part of it.
0: it is not about it, even if it shares words with the description.

Judge what the paper is about, not its quality. Answer with JSON only:
{"grades": {"<number>": <grade>, ...}} with a grade for every number."""


def judged():
    target = RESULTS / "judgements.jsonl"
    if not target.exists():
        return {}
    return {(r["id"], r["paper"]): r["grade"] for r in map(json.loads, open(target, encoding="utf-8"))}


def main(argv):
    model = argv[argv.index("--model") + 1] if "--model" in argv else "sonnet"
    rows = papers()
    queries = judged_queries()
    if "--only" in argv:
        wanted = set(argv[argv.index("--only") + 1].split(","))
        queries = [q for q in queries if q["id"] in wanted]
    pools = {q["id"]: set() for q in queries}
    for run in runs():
        for q, found in zip(queries, top(run, [q["query"] for q in queries])):
            pools[q["id"]].update(int(i) for i in found)
    done = judged()
    todo = {q["id"]: sorted(i for i in pools[q["id"]] if (q["id"], relative(rows[i][0])) not in done)
            for q in queries}
    print(f"{sum(map(len, pools.values()))} pooled, {sum(map(len, todo.values()))} to grade", flush=True)
    if "--dry-run" in argv:
        return
    found = abstracts(rows)

    def one(q):
        items = todo[q["id"]]
        if not items:
            return []
        random.Random(q["id"]).shuffle(items)
        lines = [f"Description: {q['query']}", ""]
        for n, i in enumerate(items, 1):
            path, _, meta = rows[i]
            lines += [f"[{n}] {' '.join(str(meta.get('title')).split())}",
                      f"Summary: {' '.join(str(meta.get('summary') or '').split())}",
                      f"Abstract: {found[path][:900]}", ""]
        try:
            reply, usage = paperlib.ask_model(model, SYSTEM, "\n".join(lines), effort="medium")
            grades = json.loads(re.search(r"\{.*\}", reply, re.S)[0])["grades"]
        except (RuntimeError, ValueError, TypeError, KeyError) as error:
            print("FAILED", q["id"], str(error)[:200], flush=True)
            return []
        out = []
        for n, i in enumerate(items, 1):
            grade = grades.get(str(n))
            if grade in (0, 1, 2):
                out.append({"id": q["id"], "paper": relative(rows[i][0]), "grade": grade, "model": model})
        print(f"{q['id']}: {len(out)} of {len(items)} graded, ${usage.get('usd') or 0:.3f}", flush=True)
        if out:
            out[0]["usd"] = usage.get("usd")
        return out

    RESULTS.mkdir(exist_ok=True)
    with ThreadPoolExecutor(4) as pool, open(RESULTS / "judgements.jsonl", "a", encoding="utf-8") as log:
        for out in pool.map(one, queries):
            for row in out:
                log.write(json.dumps(row, ensure_ascii=False) + "\n")
            log.flush()


if __name__ == "__main__":
    main(sys.argv[1:])
