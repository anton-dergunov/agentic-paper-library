#!/usr/bin/env python3
"""Meaning search on a copy of the example library, with a stand-in encoder (no model, no torch).

    paperlib test   (or: python3 tests/test_meaning.py)

Checks that every paper is embedded once and kept, that a changed summary re-embeds only its
paper, that a search and a topic narrow as they should, and that a paper is not its own
nearest. The stand-in hashes words into a small vector, so a paper's own words find it. The
encoder in a child process is checked with the same stand-in in the child.
"""

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
TEMP = Path(tempfile.mkdtemp())
ROOT = TEMP / "library"
shutil.copytree(ENGINE / "examples" / "library", ROOT)
os.environ.update(PAPER_LIBRARY=str(ROOT), PDF_ROOT=str(ROOT / "no-pdfs"), PAPERS_CACHE=str(TEMP / "cache"))
sys.path.insert(0, str(ENGINE / "scripts"))

import numpy as np  # noqa: E402

import meaning  # noqa: E402
import paperlib  # noqa: E402


class Words:
    """Each word hashed into one of 256 places; a unit vector a text."""

    model = "test/words"

    def __init__(self):
        self.texts = []

    def encode(self, texts, query=False):
        self.texts += texts
        out = np.zeros((len(texts), 256), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z]{4,}", text.lower()):
                out[row, sum(map(ord, word)) % 256] += 1
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)


class Chatty(Words):
    """The stand-in as the child runs it: it fails on "boom", and prints on stdout as libraries do,
    which the child must keep out of its answers."""

    def encode(self, texts, query=False):
        if "boom" in texts:
            raise ValueError("boom")
        print("(the stand-in child printing on stdout, which it sends to stderr)")
        return super().encode(texts, query)


def check(problems, ok, message):
    if not ok:
        problems.append(message)


def check_child(problems):
    """ChildEncoder against the stand-in run in a child (this file with --words-child)."""
    child = meaning.ChildEncoder("test/words", "", command=[sys.executable, __file__, "--words-child"])
    texts = ["direct preference optimization", "memory for agents"]
    check(problems, not child.loaded, "a child encoder started before its first encode")
    vectors = child.encode(texts)
    check(problems, np.allclose(vectors, Words().encode(texts)) and vectors.dtype == np.float32,
          "the child's vectors differ from the encoder's own")
    first = child._child.pid
    try:
        child.encode(["boom"])
        problems.append("an encoder's error in the child was not raised")
    except RuntimeError as error:
        check(problems, "boom" in str(error), f"the child's error lost its message: {error}")
    check(problems, child.loaded and child._child.pid == first, "an encoder's error ended the child")
    check(problems, child.unload() and not child.loaded and not child.unload(), "unload() did not end the child")
    child.encode(texts)
    check(problems, child._child.pid != first, "encode() after unload() did not start a new child")
    child._child.kill()
    child._child.wait()
    child.encode(texts)  # a child that died is started again
    check(problems, child.loaded, "a dead child was not started again")
    child.unload()


def main():
    problems = []
    check_child(problems)
    papers = paperlib.paper_index()
    encoder = Words()
    space = meaning.build(encoder)
    check(problems, len(space.papers) == len(papers) >= 3, f"{len(space.papers)} papers embedded of {len(papers)}")
    check(problems, len(encoder.texts) == len(papers), "a paper was embedded more than once")
    check(problems, all("\n" in text for text in encoder.texts), "a text is not title, summary and abstract")

    encoder.texts.clear()
    again = meaning.build(encoder)
    check(problems, not encoder.texts, f"{len(encoder.texts)} papers embedded again with nothing changed")
    check(problems, np.allclose(again.matrix, space.matrix), "the kept vectors differ from the first")

    dpo = next(p for p in papers if p.name.startswith("Direct Preference"))
    found = space.search("direct preference optimization reward model", k=3)
    check(problems, found and found[0][0] == dpo, f"DPO's own words did not find it first: {found}")
    within = space.search("direct preference optimization reward model", k=3, within="llm/memory")
    check(problems, within and all("llm/memory" in str(p) for p, _ in within), f"--in llm/memory found {within}")
    check(problems, all(p != dpo for p, _ in space.similar(dpo)), "a paper is its own nearest")
    check(problems, len(space.similar(dpo, k=10)) == len(papers) - 1, "similar() did not rank every other paper")

    text = dpo.read_text(encoding="utf-8")
    dpo.write_text(re.sub(r"^summary: .*$", "summary: A changed summary.", text, count=1, flags=re.M), encoding="utf-8")
    encoder.texts.clear()
    meaning.build(encoder, papers=paperlib.paper_index())
    check(problems, len(encoder.texts) == 1 and "A changed summary." in encoder.texts[0],
          f"a changed summary re-embedded {len(encoder.texts)} papers")

    check(problems, paperlib.papers_named("Direct Preference Optimization") == [dpo], "papers_named by title words")

    index_file = meaning.Store(encoder.model).root / "index.json"
    dpo.unlink()
    meaning.build(encoder, papers=paperlib.paper_index())
    check(problems, str(dpo) not in index_file.read_text(), "a removed paper's entry stayed in the index")

    shutil.rmtree(TEMP, ignore_errors=True)
    if problems:
        print("meaning: FAILED\n  " + "\n  ".join(problems))
        return 1
    print(f"meaning: ok ({len(papers)} papers)")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--words-child"]:
        meaning._serve_encoder("test/words", "", encoder=Chatty())
        sys.exit(0)
    sys.exit(main())
