# Example library

A small library built with `paperlib`, to show what the converters produce. It holds three openly licensed papers, one through each converter:

| Paper | Converter | Licence |
|---|---|---|
| [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](library/llm/post-training/preference-learning/) (Rafailov et al., 2023) | arXiv's HTML rendering, through pandoc: equations as the authors' LaTeX, tables as tables | [CC BY 4.0](https://arxiv.org/abs/2305.18290) |
| [Larimar: Large Language Models with Episodic Memory Control](library/llm/memory/parametric/) (Das et al., 2024) | The PDF, by docling's layout analysis, with equations and inline maths read from the page image by marker's model. Larimar does have an HTML rendering; it was added with `--from-pdf` to show the PDF path on a paper you can check against arXiv's HTML. That is why its note says it has none. | [CC BY 4.0](https://arxiv.org/abs/2403.11901) |
| [Why Momentum Really Works](library/deep-learning/optimizers-and-schedules/) (Goh, Distill, 2017) | The web page rendered by headless Chrome, through pandoc. The interactive figures are missing. | [CC BY 4.0](https://distill.pub/2017/momentum/) |

The papers are © their authors. They are included here under their licences, converted to markdown, with figures extracted.

Start at [library/README.md](library/README.md), the generated index.

To rebuild it yourself:

```bash
cd examples/library
paperlib init .            # links the skills, recreates pdfs/
paperlib add-arxiv 2305.18290 llm/post-training/preference-learning --force
paperlib add-arxiv 2403.11901 llm/memory/parametric --from-pdf --force
paperlib add-web https://distill.pub/2017/momentum/ deep-learning/optimizers-and-schedules
paperlib build-index && paperlib check
```

The PDFs go to `pdfs/`, which is not committed. `paperlib check` skips the PDF checks while that folder has none.
