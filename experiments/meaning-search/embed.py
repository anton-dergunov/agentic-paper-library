"""Embed every paper, and the queries, with one candidate encoder.

    PAPER_LIBRARY=<library> uv run --with sentence-transformers \
        python embed.py <encoder> [variant ...] [--cpu-sample N]

Writes <cache>/meaning-search/<encoder>/<variant>.npy (one unit vector a paper, in papers()'
order) and queries.npy/queries.json (the scope lines and the judged queries, with the query
prefix). Appends what it cost to results/cost.jsonl: the seconds to embed the library on the
M1's GPU (MPS), a query's median milliseconds, the peak memory, and, with --cpu-sample, the
seconds a paper on the CPU alone, as on the NAS.
"""
import json
import resource
import statistics
import sys
import time
from pathlib import Path

import numpy as np

from common import CACHE, ENCODERS, RESULTS, VARIANTS, judged_queries, papers, scope_queries, texts


def load(spec, device):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(spec["model"], device=device, trust_remote_code=False)
    model.max_seq_length = min(model.max_seq_length or 512, 1024)
    return model


def encode(model, items, prefix, batch=16):
    return np.asarray(model.encode([prefix + t for t in items], batch_size=batch,
                                   normalize_embeddings=True, show_progress_bar=False), dtype=np.float32)


def revision(spec):
    """The commit of the model's files, as the Hugging Face cache holds them."""
    from huggingface_hub import snapshot_download
    try:
        return Path(snapshot_download(spec["model"], local_files_only=True)).name
    except Exception:
        return None


def main(argv):
    if not argv or argv[0] not in ENCODERS:
        sys.exit(__doc__)
    name, spec = argv[0], ENCODERS[argv[0]]
    cpu_sample = int(argv[argv.index("--cpu-sample") + 1]) if "--cpu-sample" in argv else 0
    variants = [a for a in argv[1:] if a in VARIANTS] or ["tsa"]
    rows = papers()
    out = CACHE / name
    out.mkdir(parents=True, exist_ok=True)
    model = load(spec, "mps")
    cost = {"encoder": name, "model": spec["model"], "revision": revision(spec),
            "papers": len(rows), "dims": model.get_sentence_embedding_dimension(),
            "max_tokens": model.max_seq_length}

    queries = [s for _, s in scope_queries(rows)] + [q["query"] for q in judged_queries()]
    np.save(out / "queries.npy", encode(model, queries, spec.get("query", "")))
    (out / "queries.json").write_text(json.dumps(queries, ensure_ascii=False))
    single = []
    for q in queries[-32:]:
        start = time.perf_counter()
        encode(model, [q], spec.get("query", ""))
        single.append((time.perf_counter() - start) * 1000)
    cost["query_ms"] = round(statistics.median(single), 1)

    for variant in variants:
        items = texts(rows, variant)
        start = time.perf_counter()
        matrix = encode(model, items, spec.get("doc", ""))
        cost[f"seconds_{variant}"] = round(time.perf_counter() - start, 1)
        np.save(out / f"{variant}.npy", matrix)
        print(f"{name} {variant}: {len(items)} papers in {cost[f'seconds_{variant}']} s", flush=True)

    if cpu_sample:
        cpu = load(spec, "cpu")
        items = texts(rows, "tsa")[:cpu_sample]
        start = time.perf_counter()
        encode(cpu, items, spec.get("doc", ""))
        cost["cpu_seconds_a_paper"] = round((time.perf_counter() - start) / len(items), 3)
        single = []
        for q in queries[-10:]:
            start = time.perf_counter()
            encode(cpu, [q], spec.get("query", ""))
            single.append((time.perf_counter() - start) * 1000)
        cost["cpu_query_ms"] = round(statistics.median(single), 1)
    cost["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20)
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "cost.jsonl", "a", encoding="utf-8") as log:
        log.write(json.dumps(cost) + "\n")
    print(json.dumps(cost))


if __name__ == "__main__":
    main(sys.argv[1:])
