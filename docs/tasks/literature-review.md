# Task: literature review of LLM memory and personalisation

Write a synthesis of what the papers in `library/llm/` say about memory and personalisation
for LLMs and agents. It should be what I read to know what is settled, what is open, and how
the systems compare, without re-reading 150 papers.

## Scope

Mainly these folders, with the rest of `llm/` pulled in where relevant:

- `memory/` (`agent/`, `parametric/`, `benchmarks/`)
- `personalization/` (`methods/`, `user-modelling/`, `benchmarks/`), `text-analytics/`
- `evaluation/methods/`, `uncertainty-and-hallucination/`
- `post-training/preference-learning/`, `context/`, `safety-and-privacy/`

## Framing

General and neutral. It is written for someone who wants to understand the field, not to
design a particular product, so:

- no "our system", no design recommendations, no product vocabulary;
- claims come from the papers here, each cited as a relative link into `library/`, with a page
  number where it helps;
- say where the evidence is thin, contradictory, vendor-reported, or rests on one benchmark;
- say what changed recently. Many of these papers are from 2025–2026, so mark findings that
  overturn older ones.

## Suggested shape

Findings-first sections, each a claim the papers support, then the evidence. For example:

- how far long-horizon personalisation benchmarks put current models;
- compact profiles versus full history;
- the memory lifecycle (extract, consolidate, retrieve, forget) and where systems diverge;
- memory in text, in the KV cache or in weights;
- belief updating and staleness;
- over-personalisation and restraint;
- evaluation: simulated versus real users, LLM judges, rubrics;
- personalised rewards and preference learning;
- privacy and memory as an attack surface.

Plus one comparison table of memory systems by mechanism: what is stored, how it is written,
how it is retrieved, how it is forgotten, and how it was evaluated.

## Output

`reviews/llm-memory-and-personalization.md` at the repo root. If it grows past about 600
lines, make it a folder of one file per section with an `index.md`. Read the markdown copies,
not the PDFs. Suggest a commit message when done.
