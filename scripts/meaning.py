#!/usr/bin/env python3
"""Meaning search: the library's papers ranked by what they are about, not by the words
they use (experiments/meaning-search has the measurements behind every choice here).

    paperlib embed [<scope or paper.txt> ...]
    paperlib meaning "<description>" [--in <topic>] [-n N] [--json]
    paperlib similar <paper.txt, arxiv id or title words> [-n N] [--json]

`embed` embeds the papers that have no vector yet (all of them the first time, a few
minutes; then only new or changed ones); `meaning` ranks the papers, in the whole library or
a topic and its subtopics, by how close they are to the description; `similar` lists a
paper's nearest papers. Both embed what is missing first.

Each paper is embedded from its title, summary and abstract (the abstract from the head of
its own text, so no request leaves the laptop). A vector is kept in the cache as one `.npy`
named by the digest of the model and the text it was made from: a changed summary is
embedded again, and nothing else is; trying another model is a constant and a recompute.
carrel imports this module and keeps a `Space` in memory.
"""

import hashlib
import io
import json
import logging
import os
import sys
import threading
from pathlib import Path

import paperlib

# The encoder, pinned to the exact revision measured (experiments/meaning-search): Qwen3-Embedding
# 0.6B (Apache-2.0), with the instruction it takes before a query; a document takes none. Its
# nDCG@10 on 32 judged queries was 0.752, against 0.628 for the best small encoder and 0.504 for
# BM25. It is 1.2 GB on disk and 1.6 GB in memory, and answers a query in 65-175 ms on the M1
# (GPU or CPU).
MODEL = "Qwen/Qwen3-Embedding-0.6B"
REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"
QUERY_PREFIX = ("Instruct: Given a description of what a reader is looking for, retrieve research "
                "papers about it\nQuery: ")
DOC_PREFIX = ""
MAX_TOKENS = 1024

HEAD_BYTES = 16384  # the abstract is near the start: abstract_from_body looks at 8,000 characters
BATCH = 32
CACHE = paperlib.CACHE_DIR / "embeddings"


def _clean(value):
    return " ".join(str(value or "").split())


def paper_text(meta, head):
    """What a paper is embedded from: its title, summary and abstract, a line each. `head` is
    the start of its file (HEAD_BYTES), frontmatter included."""
    abstract = paperlib.abstract_from_body(paperlib.split_frontmatter(head)[1])
    return "\n".join(part for part in (_clean(meta.get("title")), _clean(meta.get("summary")), abstract) if part)


def digest(model, text):
    return hashlib.sha256(f"{model}\n{text}".encode("utf-8")).hexdigest()


class SentenceEncoder:
    """The pinned model through sentence-transformers, loaded on first use (a few seconds) and
    kept until `unload()`. Anything with `model` and `encode(texts, query)` can stand in for it,
    as the tests' encoder does."""

    def __init__(self, model=MODEL, revision=REVISION):
        self.model, self.revision = model, revision
        self._loaded = None
        self._lock = threading.Lock()

    def _load(self):
        with self._lock:
            if self._loaded is None:
                os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
                # No progress bars or torch's macOS note in what an agent reads.
                os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
                os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
                logging.getLogger("torch.distributed.elastic.multiprocessing.redirects").setLevel(logging.ERROR)
                if _have_model(self.model, self.revision):
                    # Never reach the network once the model is here: a sandboxed agent may not.
                    os.environ.setdefault("HF_HUB_OFFLINE", "1")
                import torch
                import transformers
                from sentence_transformers import SentenceTransformer

                transformers.utils.logging.disable_progress_bar()
                # The GPU when there is one; a sandboxed agent has none. On the CPU, float32: the
                # model's own bfloat16 is far slower there, and says so in what the agent reads.
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                kwargs = {"model_kwargs": {"dtype": torch.float32}} if device == "cpu" else {}
                loaded = SentenceTransformer(self.model, revision=self.revision or None, device=device, **kwargs)
                loaded.max_seq_length = min(loaded.max_seq_length or MAX_TOKENS, MAX_TOKENS)
                self._loaded = loaded
            return self._loaded

    @property
    def loaded(self):
        return self._loaded is not None

    def unload(self):
        """Free the model (about 1.2 GB); the next `encode` loads it again, in about 4 s. Returns
        whether there was one to free."""
        with self._lock:
            if self._loaded is None:
                return False
            self._loaded = None
        import gc

        import torch
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        return True

    def encode(self, texts, query=False):
        """Unit vectors, one row per text, as float32."""
        import numpy as np
        prefix = QUERY_PREFIX if query else DOC_PREFIX
        vectors = self._load().encode([prefix + text for text in texts], batch_size=BATCH,
                                      normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)


def _have_model(model, revision):
    """Whether the Hugging Face cache already holds the model at this revision. The first use
    downloads it (1.2 GB), which a sandboxed agent cannot: `paperlib embed` outside it does."""
    from huggingface_hub.constants import HF_HUB_CACHE
    folder = Path(HF_HUB_CACHE) / f"models--{model.replace('/', '--')}" / "snapshots"
    return (folder / revision).is_dir() if revision else folder.is_dir() and any(folder.iterdir())


class Store:
    """The vectors of one model, content-addressed: `<digest[:2]>/<digest>.npy`. And an index of
    each paper file's size and time with the digest of its text, so only a new or changed paper
    is read again."""

    def __init__(self, model, root=None):
        self.model = model
        self.root = Path(root or CACHE) / model.replace("/", "--")

    def _path(self, key):
        return self.root / key[:2] / f"{key}.npy"

    def find(self, key):
        import numpy as np
        try:
            return np.load(self._path(key), allow_pickle=False)
        except (OSError, ValueError):
            return None

    def store(self, key, vector):
        """Atomically: two processes embedding the same text is not a conflict."""
        import numpy as np
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        buffer = io.BytesIO()
        np.save(buffer, np.asarray(vector, dtype=np.float32), allow_pickle=False)
        partial = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.part")
        partial.write_bytes(buffer.getvalue())
        os.replace(partial, path)

    def texts(self, papers):
        """{paper: (digest, text or None)} for `papers` ({path: frontmatter}). The text is read
        only for a paper whose file changed since the index saw it; otherwise it is None. The
        vectors stay: another paper, or the same text again, may use them."""
        index_path = self.root / "index.json"
        try:
            saved = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saved = {}
        found, changed = {}, False
        for path, meta in papers.items():
            stat = path.stat()
            stamp = [stat.st_mtime_ns, stat.st_size]
            entry = saved.get(str(path))
            if entry and entry[0] == stamp:
                found[path] = (entry[1], None)
                continue
            with open(path, encoding="utf-8", errors="replace") as file:
                text = paper_text(meta, file.read(HEAD_BYTES))
            key = digest(self.model, text)
            saved[str(path)], changed = [stamp, key], True
            found[path] = (key, text)
        # A paper removed, or a copy of the library deleted, leaves an entry behind: drop it.
        for gone in [p for p in saved if Path(p) not in papers and not Path(p).exists()]:
            del saved[gone]
            changed = True
        if changed:
            index_path.parent.mkdir(parents=True, exist_ok=True)
            partial = index_path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
            partial.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
            os.replace(partial, index_path)
        return found


def _topic(path):
    return path.parent.relative_to(paperlib.LIBRARY_DIR).as_posix()


class Space:
    """The papers' unit vectors, one row each, ranked by cosine (a dot product)."""

    def __init__(self, papers, matrix, encoder):
        self.papers = list(papers)  # paper files, in the matrix's row order
        self.matrix = matrix
        self.encoder = encoder
        self.row = {path: i for i, path in enumerate(self.papers)}
        self.topics = [_topic(path) for path in self.papers]

    def _ranked(self, scores, k, within=None, leave_out=None):
        import numpy as np
        order = np.argsort(-scores)
        prefix = (within or "").strip("/")
        found = []
        for i in order:
            path = self.papers[i]
            if path == leave_out:
                continue
            if prefix and not (self.topics[i] == prefix or self.topics[i].startswith(prefix + "/")):
                continue
            found.append((path, float(scores[i])))
            if len(found) == k:
                break
        return found

    def search(self, description, k=10, within=None):
        """[(paper, score)] nearest the description, in the topic `within` and below it."""
        if not self.papers:
            return []
        query = self.encoder.encode([description], query=True)[0]
        return self._ranked(self.matrix @ query, k, within)

    def similar(self, paper, k=10):
        """[(paper, score)] nearest the paper, without it."""
        i = self.row.get(Path(paper))
        if i is None:
            return []
        return self._ranked(self.matrix @ self.matrix[i], k, leave_out=self.papers[i])


def build(encoder=None, papers=None, store=None, progress=None):
    """The Space of `papers` ({path: frontmatter}; default: the whole library), embedding the
    papers that have no vector yet. `progress(done, total)` is called as batches finish."""
    import numpy as np
    encoder = encoder or SentenceEncoder()
    papers = paperlib.paper_index() if papers is None else papers
    store = store or Store(encoder.model)
    texts = store.texts(papers)
    vectors, missing = {}, []
    for path, (key, text) in texts.items():
        vector = store.find(key)
        if vector is not None:
            vectors[path] = vector
            continue
        if text is None:  # the index knew the paper but its vector is gone: read it again
            with open(path, encoding="utf-8", errors="replace") as file:
                text = paper_text(papers[path], file.read(HEAD_BYTES))
        missing.append((path, key, text))
    for start in range(0, len(missing), BATCH):
        chunk = missing[start:start + BATCH]
        for (path, key, _), vector in zip(chunk, encoder.encode([text for _, _, text in chunk])):
            store.store(key, vector)
            vectors[path] = vector
        if progress:
            progress(start + len(chunk), len(missing))
    ordered = sorted(vectors)
    matrix = np.vstack([vectors[p] for p in ordered]) if ordered else np.zeros((0, 0), dtype=np.float32)
    return Space(ordered, matrix, encoder)


# The command line.

def _scope(args):
    """The papers that `paperlib embed` arguments name: topics or paper files; all with none."""
    index = paperlib.paper_index()
    if not args:
        return index
    chosen = {}
    for arg in args:
        folder = (paperlib.LIBRARY_DIR / arg.strip("/")).resolve()
        if folder.is_dir():
            chosen.update({p: m for p, m in index.items() if p.resolve().is_relative_to(folder)})
            continue
        try:
            named = paperlib.papers_named(arg, index)
        except ValueError as error:
            sys.exit(f"error: {error}")
        if not named:
            sys.exit(f"error: no topic or paper `{arg}` in the library")
        chosen.update({p: index[p] for p in named})
    return chosen


def _option(args, name, default=None):
    if name in args:
        at = args.index(name)
        if at + 1 >= len(args):
            sys.exit(f"error: {name} needs a value")
        value = args[at + 1]
        del args[at:at + 2]
        return value
    return default


def _show(found, as_json):
    index = paperlib.paper_index()
    rows = [{"paper": str(path.relative_to(paperlib.LIBRARY_ROOT)), "score": round(score, 3),
             "title": _clean(index.get(path, {}).get("title")),
             "summary": _clean(index.get(path, {}).get("summary"))} for path, score in found]
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    for row in rows:
        print(f"{row['score']:.3f}  {paperlib.styled(row['title'], 1)}\n       {row['paper']}\n       {row['summary']}")


def _progress(done, total):
    if total > BATCH:
        print(f"\rembedding {done}/{total} papers", end="" if done < total else "\n", file=sys.stderr, flush=True)


def main(argv):
    if not argv or argv[0] not in {"embed", "meaning", "similar"}:
        sys.exit(__doc__)
    command, args = argv[0], list(argv[1:])
    if command == "embed":
        papers = _scope(args)
        space = build(papers=papers, progress=_progress)
        print(f"{len(space.papers)} papers embedded with {MODEL}")
        return 0
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    k = int(_option(args, "-n", "10"))
    if command == "meaning":
        within = _option(args, "--in")
        if within and not (paperlib.LIBRARY_DIR / within.strip("/")).is_dir():
            sys.exit(f"error: no topic `{within}` in the library")
        description = " ".join(args).strip()
        if not description:
            sys.exit('usage: paperlib meaning "<description>" [--in <topic>] [-n N] [--json]')
        _show(build(progress=_progress).search(description, k, within), as_json)
        return 0
    words = " ".join(args).strip()
    try:
        named = paperlib.papers_named(words) if words else []
    except ValueError as error:
        sys.exit(f"error: {error}")
    if len(named) != 1:
        found = "no paper" if not named else f"{len(named)} papers"
        sys.exit(f"error: `{words}` names {found}; give its file, its arXiv id or more title words")
    _show(build(progress=_progress).similar(named[0], k), as_json)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
