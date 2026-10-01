# Literature review: format

## Who reads it

Two readers, one file.

- **Anton** reads the narrative to learn the state of an area: what problem it works on,
  what kinds of approaches exist and how they work, how it got here, what is settled, what
  is open and where to start reading. He is an ML engineer who knows the basics, but not
  necessarily this area. The narrative must teach, in plain language, and not read as a
  list of papers. He reads it section by section, so detail is welcome; what matters is
  that every section stays easy to read and not too technical.
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

**Length: no cap.** Cover every paper in the scope and explain each family of approaches
properly; don't cut to hit a word count. The pilot review of 70 papers came to about
11,000 words, and Anton said twice that would also be fine. Readability is the limit, not
length: short paragraphs, bold lead-ins, a table where items compare along the same axes.

## What Anton liked, and what was missing

From his reading of the pilot review (`llm/memory`, 2026-10-01). Keep what worked; the
missing part is now the "Kinds of …" section below.

Worked well, keep it:
- **The introduction** with a mermaid diagram of the area's loop or pipeline, and the
  short vocabulary list.
- **The map**, placing every paper in a family with a few words each.
- **The history by year**: what each period added and what replaced what.
- **Findings headed by claims**, each with its evidence and how strong that evidence is.
- **Comparison tables**, of systems by mechanism and of benchmarks.
- **Where to start reading**, in order, with why each paper comes at that point. Anton
  called this section very important.
- **Connections** to neighbouring areas.
- **The paper map**, whose lines were written from reading the papers. They read much
  better than technical one-line summaries.
- **Flagged conversion problems**, which he fixes separately.

Missing, now required:
- **A taxonomy of the kinds of approaches**, explained at the level of how each one works,
  as an architecture overview would: the questions that separate the designs, and one
  subsection per family with how it works, what it buys, what it costs and where it fits.
  The map alone listed papers by family but did not explain the families.
- **More introduction to the field**: what types of systems or methods exist, before the
  findings about them.

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
3. `## Kinds of <systems | methods | …>`: the taxonomy, explained. Name it for the area
   ("Kinds of memory systems", "Kinds of ranking models", "Kinds of variance reduction").
   - `### <N> questions that separate the designs`: the few choices on which the
     approaches differ, each with its possible answers. Reading papers as answers to these
     questions is what turns dozens of named methods into a handful of families.
   - Optionally a `###` for the one split that decides most (for memory: text, cache or
     weights), with a table of what each side can and cannot do.
   - One `###` per family, named by the family and its best-known members. Each has bold
     lead-ins **How it works** (plain mechanism, a concrete example, a small mermaid
     diagram when it is a pipeline), **What it buys**, **What it costs** (with the evidence
     against it, if any) and **Fits** (the kind of problem it suits). Name the variants with
     a few words each.
   - `### The families side by side`: one table, a row per family, columns for the
     questions above plus what it buys and what it costs.
4. `## The map`: every paper in the scope, grouped by the same families (plus benchmarks
   and surveys), as bold-led entries: the family in a line, then its papers, each with a
   few words on what it adds.
5. `## How the field got here`: the history by period, each a bold lead-in with its years
   ("**2023: text memory around a frozen model.**") and a short list of what that period
   added. Start with the seminal papers, say what replaced what and why, and end with what
   is new in the last year or two. An update adds a period rather than rewriting the old
   ones.
6. `## Findings`: 4–8 `###` subsections (more if the area needs them). Each heading is a
   claim the papers support, written as a sentence ("Compact memories beat full history
   only when retrieval is good"). Under it: the evidence with citations, then a bold
   **How strong the evidence is** line, and the papers that disagree.
7. `## Comparison` (when the area has one): a table of the main methods or systems along
   the axes that matter for the area. For memory systems these are: what is stored, how it
   is written, how it is retrieved, how it is forgotten, and how it was evaluated. One row
   per paper, linked.
8. `## Open questions`: what is contested, unmeasured, or rests on thin evidence. Each item
   is a bold-led line plus one or two sentences, with the papers that raise it.
9. `## Where to start reading`: 5–8 papers in reading order. Each one is a link and a line on
   why it comes at that point ("the clearest statement of the problem", "the system later
   papers compare against").
10. `## Connections`: neighbouring areas, as links to their reviews (`../<scope>.md`) or their
   folders, each with one line on what they share with this one.
11. `## Updates`: a dated log, one line per version: what it took in and what it changed
    ("2027-10-03: 14 new papers; the long-context finding now holds only up to 200K tokens;
    new family: …"). The first line records the first version. Anton reads it to see what
    moved since he last looked.
12. `## Q&A`: cross-paper points settled in later sessions, appended one per line:
    `- 2026-10-05: <question> → <short answer, with links>`. An update folds the lasting
    ones into the findings and removes them from here.
13. `## Paper map`: every paper in the scope, grouped under `### <folder>` headings, one line
    each:

    ```markdown
    - [Zep](../../library/llm/memory/agent/Zep.%20A%20Temporal….md): temporal knowledge-graph memory; beats full context on LongMemEval, vendor-run. → Findings: compact vs full history
    ```

    The link text is the paper's short name. After it come its role and main result in one
    line, in plain words, written from the reading digest rather than copied from the
    index summary. Then `→` and the sections that discuss it (or `→ map only` if none
    does). Every
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

A long review is fine as one file. Split only when one file becomes unwieldy to edit
(roughly 1,500 lines): move it to `reviews/<scope>/index.md`, which keeps the frontmatter,
the abstract, the introduction, the kinds section, the map, the history, open questions,
where to start, connections, updates and Q&A. Each finding, or each group of findings, becomes its own file
in the same folder, and the paper map moves to `paper-map.md` (with its `## Paper map`
heading). Links in the moved files go one level deeper (`../../../library/…`).
