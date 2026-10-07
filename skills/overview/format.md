# Paper overview note: format

## Who reads it

The reader reads this note **before** the paper, in 3–5 minutes, to get the intuition and
decide whether to read further. They know the basics of their field (`AGENTS.md` says who
they are). They read papers to extend their knowledge, so the note must teach the idea, not
summarise the paper's details.

- **Length:** about 600–900 words of body. If it would take longer than 5 minutes to read,
  it is too long.
- **Test every sentence:** would the reader understand it without having read the paper? If
  not, explain it in plain words or cut it. A note that needs the paper to be understood
  has failed.
- **Intuition first, always.** Plain language, an analogy or a small picture before any
  term. Details are for the paper and for `notes/<stem>.md`, not this note.

The note is about one paper. The general approach or field goes in concept notes, which
this note links to. It must render well in the reader's notes app (e.g. Obsidian) and VS
Code.

## What makes a good overview

Earlier drafts failed by being clear but repetitive and shallow, or deep but dense. One was
4× too long, full of hyperparameters, provider names, costs, numbers and page references;
its second try listed technical preconditions as the Setting, wrote Why it works as a wall
of text, and used claims ("the model learns from its rare successes") as bold lead-ins
instead of naming the design choice. The examples below come from a note that got these
right. Aim for a clear structure and real insight, in few words:

- **Punchy.** One idea per bullet and one line per bullet where possible. If a bullet runs
  past two lines, cut it. Bold lead-ins name *the thing* (the design choice, the step, the
  kind of evidence), and the text after them says what it does.
- **One angle per section, each fact once.** The abstract callout is the only summary.
- **Concrete means plain mechanism, not implementation detail.** "The model writes code, a
  checker scores it, and the model is nudged toward its best attempts", not "sample 512
  rollouts from gpt-oss-120b with a rank-32 LoRA adapter on Tinker".
- **Numbers: default to none.** Keep a number only if the note would be worse without it,
  and then give its baseline ("about 2× faster than the best human kernel"). Never include
  hyperparameters, batch sizes, ranks, step counts, costs, API or provider names, or exact
  scores. A model name only when the model itself is the point (e.g. "works with an open
  model, where prior results needed closed ones").
- **No page, table, figure or equation references.** They pull the note toward detail; the
  paper is there for that.
- **No unexplained names.** Every method or benchmark gets a link or a few plain words at
  first use.
- **Answer questions; don't raise them.** A reader shouldn't finish a sentence with a new
  question. If a term would puzzle someone new to the area, unpack it in place or leave it
  out.
- **Say why, not only what.** Tie each design choice to the problem it solves, in words.
- **Background only where needed**, and no overview of the field.
- **Claims come from the paper.** Anything from general knowledge is marked "(not from the
  paper)".
- **Plain, readable prose.** Short paragraphs, bold lead-ins, bullets where items are
  parallel. No `---` separators.

### Math

Assume the reader likes maths but remembers intuition, not formulas. At most one small
formula, only when it makes the idea click, in reduced notation and followed by one
sentence on what it means. No numeric worked examples. Usually words are enough: "the loss
exponentially up-weights the best attempts, so the model learns mostly from its rare
successes".

### Diagrams

A mermaid `flowchart LR` when the method is a loop or a pipeline: at most 5 nodes, one loop
and one exit to the result, two-line labels (`<br/>`) so it renders wide. Describe steps,
not applications. Don't verify the rendering; the reader will say if it needs redrawing:

```mermaid
flowchart LR
    P[Single target problem] --> S[Sample candidates<br/>from LLM + LoRA]
    S --> E[External verifier<br/>scores each one]
    E --> U[Update LoRA<br/>toward the best]
    U --> S
    E --> B[Best-so-far solution]
```

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

- `title`: the exact title from the library frontmatter, without the method name (that
  goes in `aliases`).
- `aliases`: the method's or paper's short name; leave the field out if it has none.
- `authors`: all if 6 or fewer, otherwise the first 5 and `et al.`.
- `affiliations`: only if the paper states them; short names, deduplicated.
- `year`: from `published`.
- `type`: the same value as in the library frontmatter (see the table below).
- `topic`: the paper's library folder path.
- `links`: plain URLs: the arXiv page, and the code or project URLs printed in the paper.
- `concepts`: 3–6 links to the ideas the paper is *about*, not tools it merely uses.
- `papers`: links to the 2–5 closest papers: a library paper by its stem, otherwise its
  short common name or the name of its existing note in the notes folder.
- `tags`: lowercase, hyphenated: the specific tools, models, datasets and domains the paper
  touches, so an agent can search for them (these details go here, not in the body). Never
  `paper`, anything every note would carry, vague umbrellas (`ai-for-science`), or anything
  in `concepts`.
- The checkboxes all start `false`; the reader sets them.

## Body

No H1 (notes apps show the file name). It starts with the callout:

```markdown
> [!abstract]
> <one punchy sentence, at most about 20 words: the idea and what it is for>
```

Write the callout fresh, not from the library `summary` (written for agents). No method
name (it's in the title and aliases), no model names, no jargon. Example: "An LLM
keeps learning while it solves one hard problem, training on its own best attempts instead
of staying frozen."

Then come three `##` sections. The reader adds their own `##` sections later.

- `## Overview`, with the `###` subsections for the paper's type (next table). Keep every
  subsection of the type; if the paper gives nothing for one, say so in one line.
- `## Questions`: 3–5 conceptual questions, each at most about 15 words: what exactly is
  updated, why this works, where it would break, how it compares to X. No numbers, no audit
  of the experiments.
- `## Follow-ups`, with two bold-led lists, no checkboxes, one line per item.
  - **Read**: 2–4 papers or concepts, each a link plus a few words on why ("closest
    concurrent work"). Closest work first. Mark papers already in the library.
  - **Try**: 1–2 simple hands-on ideas for building intuition, such as running the repo's
    simplest example or a small toy notebook. No parameter choices. Leave the list out if
    nothing practical applies.

### Sections by type

Every type follows the same length and plainness rules; each subsection is a few sentences
or a short list.

These names mean the same in every type:
- **Setting**: one punchy sentence in the paper's own framing: the kind of problem and what
  success means there, with a few everyday examples in passing. Optionally one more short
  sentence for a key requirement, in everyday words ("needs an automatic checker that
  scores each attempt"). Don't state technical preconditions ("continuous rewards",
  "pass/fail rewards"), since they read as jargon without the paper. Example: "Hard
  discovery problems (a new math bound, a record GPU kernel, a winning contest program)
  where you want **one breakthrough**, not good average behaviour."
- **Evidence**: 2–4 one-line bullets with a bold label naming the kind of evidence, then
  the fact: "**Externally checked:** organisers and domain experts reviewed the
  solutions", "**Thin ablations:** one task, one run each". Limits of the method go here
  too, in everyday words. No tables.
- **Novelty**: 3–5 one-line bullets of the form "vs [[X]]: the difference", from the paper's
  own related work, concurrent work marked. Optionally one line on the broader trend the
  paper names.
- **Concepts**: always last. Prerequisites as a link plus a one-line plain gloss, no
  formulas. Skip what the reader clearly knows (for an ML reader: LoRA, transformers;
  anything with a concept note in the notes folder).

| Type | The paper… | `###` subsections of Overview, in order |
|---|---|---|
| `method` | proposes a technique, model or algorithm | Setting · Motivation · Method · Why it works · Applications and results · Evidence · Novelty · Concepts |
| `survey` | reviews a field | Scope · Taxonomy · Findings · Open problems · Coverage · Concepts |
| `benchmark` | introduces a dataset or evaluation | Setting · Construction · Findings · Validity · Novelty · Concepts |
| `study` | analyses existing methods empirically, with no new method | Question · Design · Findings · Caveats · Novelty · Concepts |
| `system` | is a technical report or system paper: a whole model or product | Setting · Architecture · Recipe · Results · Novelty · Evidence · Concepts |
| `position` | argues a view | Claim · Arguments · Counterarguments · Implications · Novelty · Concepts |
| `theory` | proves results | Setting · Result · Proof idea · Implications · Novelty · Concepts |

For a mixed paper, use the main type and add one subsection for the other part.

#### method

- **Motivation**: 2–3 sentences on what existing approaches do and the gap, with links,
  then the key insight in one bold-led line. Level wanted: "Search around a frozen model
  wastes its best attempts: if attempt #37 was a near-miracle, attempt #38 learns nothing
  from it."
- **Method**: one lead-in line, then 4–6 numbered steps, each a bold verb and one line:
  "**Sample** candidates from the current model (base + LoRA adapter)", "**Score** each
  with the checker", "**Update** the adapter toward the best ones". Then the diagram. The
  mechanism only; the reasons go in the next subsection.
- **Why it works**: 3–4 bullets, one per key design choice. The bold lead-in *names* the
  choice as the paper does (linked if it is a concept). Then one or two sentences say what
  it does and which problem it fixes. No paragraphs. Example: "**Entropic utility
  loss** ([[Risk-sensitive RL]]): exponentially up-weights the best attempts, so learning
  concentrates on rare breakthroughs instead of the average."
- **Applications and results**: a table with the domain, the task in everyday words (what
  was being built or optimised, in half a sentence), and a qualitative outcome ("beat the best human
  submission", "matched the known best, no gain"). At most one number per row, with its
  baseline.

#### survey

- **Scope**: what is covered, and roughly when the literature stops.
- **Taxonomy**: the organising axes as a short nested list, with the key methods linked.
- **Findings**: what the field agrees on and the main trade-offs.
- **Open problems**: as the authors state them.
- **Coverage**: what is missing or stale; general knowledge is marked "(not from the
  paper)".

#### benchmark

- **Setting**: the capability it measures and why existing benchmarks fall short.
- **Construction**: where the data comes from, the task format, and the metric, in words.
- **Findings**: how current models do and where they fail.
- **Validity**: contamination, label quality, saturation.

#### study

- **Question**: what it asks and why that is open.
- **Design**: what is compared and what is held fixed.
- **Findings**: one bold-led claim per item.
- **Caveats**: confounds and how far the findings generalise.

#### system

- **Architecture**: the components and how they connect, with a diagram.
- **Recipe**: the choices the report says mattered, not the full training setup.
- **Results**: as in `method`.

#### position

- **Claim**: the thesis in one or two sentences.
- **Arguments** and **Counterarguments**: the main ones, the latter marked "(not from the
  paper)" when added.
- **Implications**: what would change if the claim is right.

#### theory

- **Setting**: the problem and any restrictive assumption.
- **Result**: the main theorem in plain words.
- **Proof idea**: the key trick in a sentence or two.
- **Implications**: what it explains in practice.

## Links

- Use Obsidian links (`[[Name]]`) for concepts and papers, in the frontmatter and the body.
  For a long paper stem in the body, add a display name:
  `[[AlphaEvolve A coding agent for scientific and algorithmic discovery|AlphaEvolve]]`.
  These suit an Obsidian vault; if the notes folder is not one, use plain markdown links
  (`[AlphaEvolve](<stem>.md)`) instead, here and in the examples above.
- Linking to notes that don't exist yet is encouraged. Pick a natural, singular name
  ("Risk-sensitive RL", "PUCT"). Don't normalise names across the notes folder.
- No "My thoughts" section, placeholders, or to-do checkboxes.
