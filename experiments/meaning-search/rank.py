"""Rankings: each candidate's papers for a query, nearest first, and each paper's neighbours.

A run is (encoder, variant), or ("bm25", variant) for the keyword baseline (bm25s, its English
stop words, Okapi BM25 at its defaults).
"""
import numpy as np

from common import CACHE, ENCODERS, VARIANTS, papers, query_vectors, texts, vectors

_BM25 = {}


def runs():
    """Every run whose vectors exist, and BM25's. `body` is the best of a paper's chunks and its
    title, summary and abstract (body.py)."""
    found = [(e, v) for e in ENCODERS for v in VARIANTS + ("body",) if (CACHE / e / f"{v}.npy").exists()]
    return found + [("bm25", v) for v in VARIANTS]


def _bm25(variant):
    if variant not in _BM25:
        import bm25s
        corpus = texts(papers(), variant)
        retriever = bm25s.BM25()
        retriever.index(bm25s.tokenize(corpus, stopwords="en", show_progress=False), show_progress=False)
        _BM25[variant] = (retriever, corpus)
    return _BM25[variant]


def scores(run, queries):
    """A (queries × papers) matrix of scores for the query texts."""
    encoder, variant = run
    if encoder == "bm25":
        import bm25s
        retriever, corpus = _bm25(variant)
        out = np.zeros((len(queries), len(corpus)), dtype=np.float32)
        tokens = bm25s.tokenize(queries, stopwords="en", show_progress=False, return_ids=False)
        for i, words in enumerate(tokens):
            out[i] = retriever.get_scores(words)
        return out
    qvecs, qtexts = query_vectors(encoder)
    index = {q: i for i, q in enumerate(qtexts)}
    qs = qvecs[[index[q] for q in queries]]
    if variant == "body":
        best = qs @ vectors(encoder, "tsa").T
        owner = np.load(CACHE / encoder / "body-owner.npy")
        sims = qs @ vectors(encoder, "body").T
        for i in range(len(queries)):
            np.maximum.at(best[i], owner, sims[i])
        return best
    return qs @ vectors(encoder, variant).T


def neighbours(run, k=10):
    """For each paper, its k nearest other papers (indices), by the run's own similarity."""
    encoder, variant = run
    if encoder == "bm25":
        corpus = texts(papers(), variant)
        sims = np.vstack([scores(run, corpus[i:i + 200]) for i in range(0, len(corpus), 200)])
    else:
        matrix = vectors(encoder, "tsa" if variant == "body" else variant)  # neighbours: by the paper's own text
        sims = matrix @ matrix.T
    np.fill_diagonal(sims, -np.inf)
    return np.argsort(-sims, axis=1)[:, :k]


def top(run, queries, k=10):
    s = scores(run, queries)
    return np.argsort(-s, axis=1)[:, :k]
