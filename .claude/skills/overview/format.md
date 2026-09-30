# Paper overview note: format

The note is about one paper. It is not about the general approach or the field: those go in
concept notes, which the paper note links to. Anton reads it in Obsidian and in VS Code, so
it must render well in both.

## What makes a good overview

Anton's verdict on earlier drafts:
- ChatGPT's were clear and well structured, but repetitive and shallow.
- Claude's had the depth and nuance, but were dense and harder to read.

Aim for Claude's depth with clean structure:

- **One angle per section, each fact once.** Don't restate the summary in "Why it matters",
  or the method in "Novelty". The abstract callout is the only summary. If a fact belongs in
  two sections, put it in one and link to the other.
- **Concrete over abstract.** "Sample N candidate programs from gpt-oss-120b with a LoRA
  adapter" rather than "generate candidates". Name the model, the data, the reward, the
  signal.
- **No unexplained names.** Every method, algorithm or benchmark the note mentions gets a
  link or a short gloss at first use. "A [[PUCT]]-style rule (the UCB exploration bonus from
  AlphaZero)", not a bare "PUCT-style strategy".
- **Say why, not only what.** Papers publish what worked, rarely why. "Why it works" (or
  its equivalent for the type) is the most valuable part of the note. Tie each design choice
  to the problem it solves.
- **Answer questions; don't raise them.** A reader shouldn't finish a sentence with a new
  question. For example, "RL on a single problem" needs one clause saying why a single
  problem. If a term would puzzle someone new to the area, unpack it in place.
- **Background only where it's needed.** Give enough context to follow the paper (Anton
  learns from these notes), and no overview of the field.
- **Numbers need a baseline.** "About 2× faster than the best human kernel" is useful. "An
  error of 0.38 → 0.36" is not, unless the note says what the scale means and what the
  previous best was.
- **Claims come from the paper.** Related work and trends are taken from the paper itself.
  Anything added from general knowledge is marked "(not from the paper)", because training
  knowledge may be stale.
- **Plain, readable prose.** Short paragraphs, bold lead-ins, bullets where items are
  parallel, and nested bullets rather than long compound sentences. Don't use `---`
  separators between sections.
- **Pages.** Put "(p. 6)" after anything worth checking in the PDF: the main equation, a
  key table, the ablation. Library headings carry the page each section starts on.

### Math

Anton likes maths but remembers intuition, not formulas. Papers often write a simple idea as
a huge formula. Include an equation only when it carries the idea, and then:

1. rewrite it in clean, reduced notation, dropping indices and terms that don't matter for
   the idea;
2. label each part in plain words, as a bullet per term or with `\underbrace`;
3. give the intuition in one sentence;
4. when it helps, add a tiny numeric example: "with rewards 1, 2 and 10, the weights become
   …, so the 10 dominates";
5. cite the paper's equation number and page, so the full form can be found.

Never paste a large formula as-is.

### Diagrams

Use a mermaid `flowchart` when the method is a loop or a pipeline. Keep node labels short,
describe the step rather than an application ("External verifier → reward", not the list of
verifiers), and make each arrow a real data flow.

## Frontmatter

Every field name is one word. Use this order:

```yaml
---
title: "Learning to Discover at Test Time"
aliases: [TTT-Discover]
authors: [Mert Yuksekgonul, <author 2>, <author 3>, <author 4>, <author 5>, et al.]
affiliations: [Stanford, NVIDIA, Together AI]
year: 2026
type: method
topic: llm/agents
links:
  - https://arxiv.org/abs/2601.16175
  - https://github.com/test-time-training/discover
concepts: ["[[Test-time training]]", "[[Risk-sensitive RL]]", "[[Test-time compute scaling]]"]
papers: ["[[AlphaEvolve A coding agent for scientific and algorithmic discovery]]"]
tags: [lora, gpt-oss, gpu-kernels, combinatorics]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---
```

- `title`: the exact paper title, copied from the library frontmatter. Don't add the method
  name in brackets; that goes in `aliases`.
- `aliases`: the method's or paper's short name, if it has one. Otherwise leave the field
  out.
- `authors`: all of them if there are 6 or fewer, otherwise the first 5 followed by
  `et al.`.
- `affiliations`: only if the paper states them. Short names, deduplicated.
- `year`: from `published`.
- `type`: the same value as in the library frontmatter (see the table below).
- `topic`: the paper's library folder path. Bases group notes by it, so the notes need no
  topic folders.
- `links`: a plain list of URLs, without types, since the domain says what each one is.
  Include the arXiv page and the code or project URLs printed in the paper. Anton adds more
  by hand.
- `concepts`: 3–6 links to the ideas the paper is *about*: the edges it adds to the graph.
  Not tools it merely uses.
- `papers`: links to the 2–5 closest papers. For a paper in the library, link its stem, so
  the link resolves once that paper has a note. Otherwise use its short common name. If the
  vault already has a note for the paper under another name, use that name.
- `tags`: lowercase and hyphenated. List the specific tools, models, datasets and domains
  the paper touches (`lora`, `gpt-oss`, `gpu-kernels`), so that an agent can search for
  them. Never `paper`, never something every note would carry (`ml`, `llm`), and never
  vague umbrellas (`ai-for-science`). Don't repeat anything already in `concepts`.
- The checkboxes all start `false`. Anton sets them:
  - `read`: he has read the paper itself.
  - `analyzed`: he has worked through it in depth, beyond this overview.
  - `queued`: he wants to read it properly.
  - `revisit`: he wants to come back to it.
  - `reproduce`: he wants to try it hands-on.

## Body

The body has no H1, because Obsidian shows the file name. It starts with the callout:

```markdown
> [!abstract]
> <the library `summary`, copied verbatim>
```

Then come three `##` sections. Anton adds his own `##` sections later, beside these.

- `## Overview`, with the `###` subsections for the paper's type (next table). Keep every
  subsection of the type. If the paper gives nothing for one, say so in one line ("No
  ablations; all results are self-reported."), because that is information too.
- `## Questions`: 3–6 open questions for exploring this paper with the agent. Make them
  specific to its mechanism and claims: what exactly is updated, what it costs, which
  component the gain comes from, where it would break. Leave out generic ones such as "does
  it generalise?" unless the question names the case.
- `## Follow-ups`, with two bold-led lists. No checkboxes.
  - **Read**: papers and concepts to read next, each with why, and in order. Start with the
    closest prior and concurrent work, then prerequisites. Mark papers already in the
    library.
  - **Try**: concrete hands-on steps, such as an entry point in the paper's repo, a toy
    version to build in a notebook, and what to observe. Leave this list out when nothing
    practical applies.

### Sections by type

These names mean the same thing in every type:
- **Setting**: which problems the paper targets and what it assumes, for example a verifier
  with a continuous reward. Say where it does not apply.
- **Evidence**: how solid the claims are. External validation, ablations, baselines, cost,
  vendor-reported or single-benchmark results, and what is missing.
- **Novelty**: nested bullets of the form "vs [[X]]: the difference", taken from the
  paper's own related work, with concurrent work marked. End with one line on the broader
  trend if the paper names one.
- **Concepts**: always last. The prerequisites to learn, each as a link plus a one-line
  gloss. Skip what Anton clearly knows, such as LoRA or transformers, and anything with a
  concept note in the vault. This list may overlap the frontmatter `concepts` only where a
  gloss is needed.

| Type | The paper… | `###` subsections of Overview, in order |
|---|---|---|
| `method` | proposes a technique, model or algorithm | Setting · Motivation · Method · Why it works · Applications and results · Evidence · Novelty · Concepts |
| `survey` | reviews a field | Scope · Taxonomy · Findings · Open problems · Coverage · Concepts |
| `benchmark` | introduces a dataset or evaluation | Setting · Construction · Findings · Validity · Novelty · Concepts |
| `study` | analyses existing methods empirically, with no new method | Question · Design · Findings · Caveats · Novelty · Concepts |
| `system` | is a technical report or system paper: a whole model or product | Setting · Architecture · Recipe · Results · Novelty · Evidence · Concepts |
| `position` | argues a view | Claim · Arguments · Counterarguments · Implications · Novelty · Concepts |
| `theory` | proves results | Setting · Result · Proof idea · Implications · Novelty · Concepts |

For a mixed paper, such as a method that also introduces a benchmark, use the main type and
add one subsection for the other part.

#### method

- **Motivation**: what existing approaches do and where they fall short, with just enough
  background to follow. Link each approach named (Best-of-N, evolutionary search, MCTS).
  End with the key insight in one line. Example of the level wanted: "Best-of-N treats
  every attempt as independent: if attempt #37 was a near-miracle, attempt #38 learns
  nothing from it."
- **Method**: numbered, concrete steps, a diagram if the method is a loop or pipeline, and
  pages. Keep it to the mechanism; the reasons go in the next subsection.
- **Why it works**: one bold-led item per key design choice, each saying the problem it
  solves. The central equation goes here, following the maths rules.
- **Applications and results**: one entry per application or benchmark.
  - **What the task is**, in one or two sentences: "AtCoder Heuristic Contests: open-ended
    optimisation problems, such as scheduling, scored by a numeric objective rather than
    pass/fail".
  - **How the method was applied**: what was generated and what the reward or verifier was.
  - **The result against a baseline.**
  Use a table only if each cell stays short.

#### survey

- **Scope**: what is covered and what is excluded, the date range and the literature
  cutoff.
- **Taxonomy**: the survey's organising axes, as a nested list or a table. List the
  reviewed methods under each branch, as links, with one line on each important one. Mark
  those already in the library.
- **Findings**: what the field agrees on, the main trade-offs, and the trends the survey
  identifies.
- **Open problems**: as the authors state them.
- **Coverage**: what is missing or stale given the cutoff. If you add later developments
  from general knowledge, mark them "(not from the paper)".
- In Follow-ups, **Read** lists the primary papers worth reading from the survey.

#### benchmark

- **Setting**: the capability it measures, and why existing benchmarks fall short.
- **Construction**: the data source, the task format, how labels were made, and the
  metric.
- **Findings**: how current models score and where they fail, with examples of failures.
- **Validity**: contamination, label quality, whether the metric measures the capability,
  and headroom or saturation.

#### study

- **Question**: what the study asks and why it is open.
- **Design**: which models and data, what is varied, and what is held fixed.
- **Findings**: one bold-led claim per item, each with its evidence and page.
- **Caveats**: confounds, scale, and how far the findings generalise.
- **Novelty**: what it confirms and what it overturns.

#### system

- **Architecture**: the components and how they connect, with a diagram.
- **Recipe**: data, training stages, compute, and the choices the report says mattered.
- **Results**: as in `method`, each benchmark explained.
- **Novelty**: usually engineering decisions. Say which ones, and why they were made.

#### position

- **Claim**: the thesis in one or two sentences.
- **Arguments**: the paper's main arguments, each with the evidence it gives.
- **Counterarguments**: those the paper addresses, plus obvious ones it doesn't, marked
  "(not from the paper)".
- **Implications**: what would change if the claim is right.

#### theory

- **Setting**: the problem and the assumptions, flagging the restrictive ones.
- **Result**: the main theorem in plain words first, then stated cleanly.
- **Proof idea**: the key trick in a few sentences, not the proof.
- **Implications**: what it explains or predicts in practice, and what it does not.

## Links

- Use Obsidian links (`[[Name]]`) for concepts and papers, in the frontmatter and in the
  body. For a long paper stem in the body, add a display name:
  `[[AlphaEvolve A coding agent for scientific and algorithmic discovery|AlphaEvolve]]`.
- Linking to notes that don't exist yet is encouraged: those links show Anton which notes to
  write. Pick a natural, singular name ("Risk-sensitive RL", "PUCT"). Don't normalise names
  across the vault beyond reusing an existing note's name.
- Don't add a "My thoughts" section, placeholders, or to-do checkboxes. Anton adds his own
  sections when he has something to say.
