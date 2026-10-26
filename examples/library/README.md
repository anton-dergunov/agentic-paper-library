# Example library

A small library built with `paperlib`, to show what a library holds. It has three openly licensed papers: two arXiv papers, each kept as its PDF's text layer, and a web article kept as markdown.

| Paper | Kept as | Licence |
|---|---|---|
| [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](library/llm/post-training/preference-learning/) (Rafailov et al., 2023) | The PDF's text layer, a line `[page N]` where each page starts | [CC BY 4.0](https://arxiv.org/abs/2305.18290) |
| [Larimar: Large Language Models with Episodic Memory Control](library/llm/memory/parametric/) (Das et al., 2024) | The same | [CC BY 4.0](https://arxiv.org/abs/2403.11901) |
| [Why Momentum Really Works](library/deep-learning/optimizers-and-schedules/) (Goh, Distill, 2017) | The web page as markdown, by Defuddle, with its equations as TeX; no figures | [CC BY 4.0](https://distill.pub/2017/momentum/) |

The papers are © their authors. They are included here under their licences, as text.

Start at [library/README.md](library/README.md), the generated index.

To rebuild it yourself:

```bash
cd examples/library
paperlib init .            # links the skills, recreates pdfs/
paperlib add-arxiv 2305.18290 llm/post-training/preference-learning --force
paperlib add-arxiv 2403.11901 llm/memory/parametric --force
paperlib add-web https://distill.pub/2017/momentum/ deep-learning/optimizers-and-schedules --force
paperlib build-index && paperlib check
```

The PDFs go to `pdfs/`, which is not committed. `paperlib check` skips the PDF checks while that folder has none.
