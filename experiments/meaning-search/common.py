"""What the experiment's scripts share: the engine's paperlib, the papers and their texts, the
candidate encoders, the queries, and where the vectors are kept (the cache, not git)."""
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
import paperlib  # noqa: E402

RESULTS = HERE / "results"
CACHE = paperlib.CACHE_DIR / "experiments" / "meaning-search"

_E5 = "Represent this sentence for searching relevant passages: "
# name: the model, its prefixes for a query and for a paper, and what loading it needs.
ENCODERS = {
    "minilm": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
    "bge-small": {"model": "BAAI/bge-small-en-v1.5", "query": _E5},
    "bge-base": {"model": "BAAI/bge-base-en-v1.5", "query": _E5},
    "e5-small": {"model": "intfloat/multilingual-e5-small", "query": "query: ", "doc": "passage: "},
    "specter": {"model": "sentence-transformers/allenai-specter"},
    "qwen3": {"model": "Qwen/Qwen3-Embedding-0.6B",
              "query": "Instruct: Given a description of what a reader is looking for, "
                       "retrieve research papers about it\nQuery: "},
}
# What a paper is embedded from.
VARIANTS = ("tsa", "ts", "ta")
HEAD_BYTES = 16384  # the abstract is near the start; abstract_from_body looks at 8,000 characters


def papers():
    """[(paper file, its topic, its frontmatter)], sorted by path, for every paper in the library."""
    rows = []
    for path, meta in sorted(paperlib.paper_index().items()):
        rows.append((path, path.parent.relative_to(paperlib.LIBRARY_DIR).as_posix(), meta))
    return rows


def relative(paper):
    return Path(paper).relative_to(paperlib.LIBRARY_DIR).with_suffix("").as_posix()


def _clean(value):
    return " ".join(str(value or "").split())


def abstracts(rows):
    """{paper: abstract}, from the head of its own text (no arXiv request), kept in the cache by
    the file's size and time."""
    store = CACHE / "abstracts.json"
    known = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    found, changed = {}, False
    for path, _, _ in rows:
        stat = path.stat()
        stamp = [stat.st_mtime_ns, stat.st_size]
        entry = known.get(str(path))
        if not entry or entry[0] != stamp:
            with open(path, encoding="utf-8", errors="replace") as file:
                head = file.read(HEAD_BYTES)
            entry, changed = [stamp, paperlib.abstract_from_body(paperlib.split_frontmatter(head)[1])], True
            known[str(path)] = entry
        found[path] = entry[1]
    if changed:
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
    return found


def texts(rows, variant):
    """Each paper's text in a variant: tsa (title, summary, abstract), ts or ta."""
    found = abstracts(rows) if "a" in variant else {}
    out = []
    for path, _, meta in rows:
        parts = [_clean(meta.get("title"))]
        if "s" in variant:
            parts.append(_clean(meta.get("summary")))
        if "a" in variant:
            parts.append(found[path])
        out.append("\n".join(p for p in parts if p))
    return out


def topics():
    return paperlib.load_topics()


def judged_queries():
    return yaml.safe_load((HERE / "queries.yaml").read_text(encoding="utf-8"))


def scope_queries(rows, least=5):
    """[(topic, scope line)] for each leaf topic (no subtopics) holding `least` papers or more."""
    declared = topics()
    counts = {}
    for _, topic, _ in rows:
        counts[topic] = counts.get(topic, 0) + 1
    leaves = [t for t in declared if not any(o.startswith(t + "/") for o in declared)]
    return [(t, re.sub(r"\s+", " ", str(declared[t]))) for t in leaves if counts.get(t, 0) >= least]


def vectors(encoder, variant):
    """The papers' matrix for an encoder and variant, rows in papers()' order."""
    import numpy as np
    return np.load(CACHE / encoder / f"{variant}.npy")


def query_vectors(encoder):
    import numpy as np
    return np.load(CACHE / encoder / "queries.npy"), json.loads((CACHE / encoder / "queries.json").read_text())
