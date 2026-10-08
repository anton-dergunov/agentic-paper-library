#!/usr/bin/env python3
"""The papers of the measurement: those the task file names, and sixty at random.

    PAPER_LIBRARY=<library> uv run python sample.py > papers.tsv

Two columns: "named" or "random", and the paper's path under the library.
Only arXiv-HTML papers that are not hand-edited (reconvert skips those).
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from paperlib import LIBRARY_DIR, paper_files, read_paper  # noqa: E402

NAMED = """Which Tricks Are Important for Learning to Rank
Continual Learning via Sparse Memory Finetuning
BEIR
BRIGHT
Approximate Nearest Neighbor Negative Contrastive Learning
Unsupervised Dense Information Retrieval with Contrastive Learning
Doubly-Robust Estimation for Correcting Position-Bias
A Large Scale Search Dataset for Unbiased Learning to Rank
Overview of the TREC 2019 deep learning track
ANN-Benchmarks
PLAID
Large language models can accurately predict searcher preferences
Qwen3 Technical Report
OpenThoughts
In-context Autoencoder
QLoRA
Nemotron-4 340B
Phi-4
Transformer models: an introduction and catalog
ColBERTv2
Decoding billions of integers per second through vectorization
Dense Text Retrieval based on Pretrained Language Models
Gemini 2.5
Gemma 3
UltraFeedback
The Llama 3 Herd of Models
2 OLMo 2 Furious
DeepSeek-V3.2
The Entropy Mechanism of Reinforcement Learning
Understanding R1-Zero-Like Training
Nemotron-Cascade 2""".splitlines()


def main():
    papers = []
    for md in paper_files():
        meta, body = read_paper(md)
        if meta.get("source") == "html" and "<!-- hand-edited" not in body:
            papers.append((str(meta.get("title") or ""), md))
    named = {md for title, md in papers if any(title.startswith(n) for n in NAMED)}
    rest = sorted(md for _, md in papers if md not in named)
    for md in sorted(named):
        print(f"named\t{md.relative_to(LIBRARY_DIR)}")
    for md in sorted(random.Random(20261008).sample(rest, 60)):
        print(f"random\t{md.relative_to(LIBRARY_DIR)}")


if __name__ == "__main__":
    main()
