# Literature review: format

## Who reads it

Two readers, one file.

- **Anton** reads the narrative to learn the state of an area: what problem it works on,
  how it got here, what is settled, what is open and where to start reading. He is an ML
  engineer who knows the basics, but not necessarily this area. The narrative must teach,
  in plain language, and not read as a list of papers.
- **Agents** start any question about the area here, before opening papers. They need the
  claims with their evidence and pages, and the paper map, which places every paper in
  the scope.

Write for Anton first. The agent's needs are met by precise citations and the paper map,
not by denser prose.

## Style

The `overview` skill's `format.md` sets the voice. These rules carry over:

- **Intuition first.** An everyday framing or a small example before any term or formula.
  Restate heavy notation in plain words.
- **No unexplained names.** Every method, benchmark or term gets a link or a few plain
  words at first use.
- **Say why, not only what.** Tie each approach to the problem it solves.
- **Bold lead-ins name the thing** (the family, the design choice, the kind of evidence),
  and the text after them says what it does. Short paragraphs; bullets where items are
  parallel. No `---` separators.
- **Math:** at most a few small formulas in the whole review, each followed by one
  sentence saying what it means.
- **Diagrams:** a mermaid `flowchart LR` in the introduction when the area has a pipeline
  or a loop, at most 6 nodes.

These are different from an overview note:

- **Numbers are allowed when a finding rests on them.** Each one comes with its baseline
  and a page link: "Zep answers 71% of LongMemEval questions against 60% for the full
  history in context ([p. 7, Table 2](…))". Never give hyperparameters, costs or provider
  names, except when they are the finding.
- **Cite pages for claims** with `pdf.invalid` links (below), so Anton can check them in
  the PDF and an agent can find them.
- **Weigh the evidence.** Each finding says how well it is supported: replicated across
  papers; one paper; vendor-reported (the authors sell the system); one benchmark; a
  benchmark that later papers call saturated or flawed; contradicted by another paper.
- **Mark what changed.** When a recent paper overturns or narrows an older finding, say so
  in place ("this held until 2025, when …").

Framing:

- **Claims come from the papers in the library.** Anything from general knowledge is
  marked "(not from the library)". The library is a selection, so say "the papers here"
  rather than "the field" when coverage matters.
- **Neutral and generic.** It is written for someone who wants to understand the area,
  not to build a particular product: no "our system", no design recommendations, no
  product vocabulary.

Length: the narrative (everything before the paper map) is about 3,000 words for an area
of 20–40 papers, up to about 6,000 for 150 or more. If the whole file passes about 800
lines, split it (see "Split reviews").

## The file

`reviews/<scope>.md`, where `<scope>` is a folder in `catalog/topics.yaml`. The review covers
that folder and all its subfolders.

```yaml
---
scope: llm/memory
title: Memory for LLMs and agents
updated: 2026-10-02
---
```

`title` is a plain name for the area, not the folder path. `updated` is the date the review
last took in new papers or changed a finding.

The body has these sections, in this order:

1. `# <title>`, then an abstract callout:

   ```markdown
   > [!abstract]
   > <2–3 sentences: what the area is about, where it stands, and the one thing most
   > worth knowing>
   ```

2. `## Introduction`: the problem in everyday terms, why it is hard, the core vocabulary
   (3–6 terms, each glossed), and the diagram if there is one. Someone new to the area
   should finish it knowing what the rest of the review is talking about.
3. `## The map`: the main families of approaches, as bold-led entries of 2–3 lines each:
   what the family does, the idea behind it, and its key papers linked. Optionally a small
   nested list for the taxonomy.
4. `## How the field got here`: a short history. The seminal papers, then what replaced
   what and why, ending with what is new in the last year or two. Prose, roughly in time
   order, with years.
5. `## Findings`: 4–8 `###` subsections. Each heading is a claim the papers support,
   written as a sentence ("Compact memories beat full history only when retrieval is
   good"). Under it: the evidence with citations, the strength of that evidence, and the
   papers that disagree.
6. `## Comparison` (when the area has one): a table of the main methods or systems along
   the axes that matter for the area. For memory systems these are: what is stored, how it
   is written, how it is retrieved, how it is forgotten, and how it was evaluated. One row
   per paper, linked.
7. `## Open questions`: what is contested, unmeasured, or rests on thin evidence. Each item
   is a bold-led line plus one or two sentences, with the papers that raise it.
8. `## Where to start reading`: 5–8 papers in reading order. Each one is a link and a line on
   why it comes at that point ("the clearest statement of the problem", "the system later
   papers compare against").
9. `## Connections`: neighbouring areas, as links to their reviews (`../<scope>.md`) or their
   folders, each with one line on what they share with this one.
10. `## Q&A`: cross-paper points settled in later sessions, appended one per line:
    `- 2026-10-05: <question> → <short answer, with links>`. An update folds the lasting
    ones into the findings and removes them from here.
11. `## Paper map`: every paper in the scope, grouped under `### <folder>` headings, one line
    each:

    ```markdown
    - [Zep](../../library/llm/memory/agent/Zep.%20A%20Temporal….md): temporal knowledge-graph memory; beats full context on LongMemEval, vendor-run. → Findings: compact vs full history
    ```

    The link text is the paper's short name. After it come its role and main result in one
    line, then `→` and the sections that discuss it (or `→ map only` if none does). Every
    paper in the scope must be here: `scripts/review-status.py` counts this section.

## Links

- **A paper:** a relative link to its markdown, as `scripts/review-status.py --links <scope>`
  prints it. The link text is the paper's short name (method or system name, or a few words
  of the title).
- **A place in a paper:** a `pdf.invalid` link as AGENTS.md describes ("Linking to a place in
  a paper"), using the pdf base that `--links` prints, plus `?page=N` and `dest` where it
  helps: `[p. 7, Table 2](http://pdf.invalid/…/Zep.%20….pdf?dest=table.2&page=7)`.
- **Another review:** relative, `../search-and-ranking.md`.

`scripts/check-library.py` fails on any of these that doesn't resolve, and
`scripts/review-status.py --fix-links` repairs links to papers that moved.

## Split reviews

When a review passes about 800 lines, move it to `reviews/<scope>/index.md`, which keeps the
frontmatter, the abstract, the introduction, the map, the history, open questions, where to
start, connections and Q&A. Each finding, or each group of findings, becomes its own file
in the same folder, and the paper map moves to `paper-map.md` (with its `## Paper map`
heading). Links in the moved files go one level deeper (`../../../library/…`).
