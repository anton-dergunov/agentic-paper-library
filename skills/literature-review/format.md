# Literature review: format

## Who reads it

Two readers, one file.

- **The reader** reads the narrative to learn the state of an area: what problem it works
  on, what kinds of approaches exist and how they work, how it got here, what is settled,
  what is open and where to start reading. They know the basics of their field
  (`AGENTS.md` says who they are), but not necessarily this area. The narrative must
  teach, in plain language, and not read as a list of papers. They read it section by
  section, so detail is welcome; what matters is that every section stays easy to read and
  not too technical.
- **Agents** start any question about the area here, before opening papers. They need the
  claims with their evidence and pages, and the paper map, which places every paper in
  the scope.

Write for the reader first. The agent's needs are met by precise citations and the paper map,
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
- **Diagrams:** see "Diagrams and figures" below. Draw one where a picture shows something
  the text cannot, and pick the type that fits; don't default to a left-to-right chain of
  boxes.

These are different from an overview note:

- **Numbers are allowed when a finding rests on them.** Each one comes with its baseline
  and a page link: "Zep answers 71% of LongMemEval questions against 60% for the full
  history in context ([p. 7, Table 2](…))". Never give hyperparameters, costs or provider
  names, except when they are the finding.
- **Cite pages for claims** with `pdf.invalid` links (below), so the reader can check them
  in the PDF and an agent can find them.
- **Weigh the evidence.** Each finding says how well it is supported, starting with a
  label from the fixed list under "Evidence labels" below, so that findings can be
  compared within a review and across reviews.
- **Mark what changed.** When a recent paper overturns or narrows an older finding, say so
  in place ("this held until 2025, when …").

Framing:

- **Claims come from the papers in the library.** Anything from general knowledge is
  marked "(not from the library)". The library is a selection, so say "the papers here"
  rather than "the field" when coverage matters.
- **Neutral and generic.** It is written for someone who wants to understand the area,
  not to build a particular product: no "our system", no product vocabulary. Advice on
  what to do belongs in the "In practice" section and nowhere else; the other sections
  report what the papers show.

**Length: no cap.** Cover every paper in the scope and explain each family of approaches
properly; don't cut to hit a word count. The pilot review of 70 papers came to about
11,000 words, and its reader said twice that would also be fine. Readability is the limit, not
length: short paragraphs, bold lead-ins, a table where items compare along the same axes.

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
     lead-ins **How it works** (plain mechanism, a concrete example, and a diagram or a
     figure from one of the papers when it shows the mechanism better than words),
     **What it buys**, **What it costs** (with the evidence
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
   **How strong the evidence is** line that opens with one or two evidence labels in
   italics ("**How strong the evidence is:** *replicated; vendor-run.* …") and then says
   why, and the papers that disagree. Findings headed by claims are what makes the
   review usable; never head one with a topic.
7. `## Where the papers disagree`: every disagreement between papers in one list, so it
   is easy to find and to revisit on update. One bold-led item each: the question, who
   says what (with links and the deciding numbers), and what would explain or settle it
   (different settings, different models, a small sample). The findings mention each
   disagreement where it arises; this section collects them. Leave it out only if the
   papers do not disagree.
8. `## In practice: <topic>` (when the area has a practical use; one section, or two if
   there are two distinct topics). **Written last**, after every other section is done.
   See "The In practice section" below.
9. `## Comparison` (when the area has one): a table of the main methods or systems along
   the axes that matter for the area. For memory systems these are: what is stored, how it
   is written, how it is retrieved, how it is forgotten, and how it was evaluated. One row
   per paper, linked. A row that reports numbers ends with one page link to where they
   come from (a last column headed "Source": "[p. 6, Table 2](…)"); a single link per row
   is enough, and a row without numbers needs none. Say above the table that the numbers
   are each paper's own, so rows are not comparable when the setups differ.
10. `## Open questions`: what is contested, unmeasured, or rests on thin evidence. Each item
   is a bold-led line plus one or two sentences, with the papers that raise it.
11. `## Where to start reading`: 5–8 papers in reading order. Each one is a link and a line on
   why it comes at that point ("the clearest statement of the problem", "the system later
   papers compare against"). The reader of the first review called this section very
   important: choose the order with care, and say when a paper's copy has a conversion
   problem the reader should know about.
12. `## Connections`: neighbouring areas, as links to their reviews (`../<scope>.md`) or their
   folders, each with one line on what they share with this one.
13. `## Updates`: a dated log, one line per version: what it took in and what it changed
    ("2027-10-03: 14 new papers; the long-context finding now holds only up to 200K tokens;
    new family: …"). The first line records the first version. The reader reads it to see
    what moved since they last looked.
14. `## Q&A`: cross-paper points settled in later sessions, appended one per line:
    `- 2026-10-05: <question> → <short answer, with links>`. An update folds the lasting
    ones into the findings and removes them from here.
15. `## Paper map`: every paper in the scope, grouped under `### <folder>` headings, one line
    each:

    ```markdown
    - [Zep][zep]: temporal knowledge-graph memory; beats full context on LongMemEval, vendor-run. → Findings: compact vs full history
    - [MemoryOS][memoryos] (skimmed): three-tier store with heat-based promotion. → Kinds
    ```

    The link text is the paper's short name. A paper that was skimmed, not read in full,
    is marked "(skimmed)" after the link, so the reader can see when a claim rests on a
    skim. After that come its role and main result in one line, in plain words, written
    from the reading digest rather than copied from the index summary: these lines read
    much better than technical one-line summaries. Then `→` and the sections that discuss
    it (or `→ map only` if none does). Every paper in the scope must be here:
    `paperlib review-status` counts this section.

## Evidence labels

Every **How strong the evidence is** line opens with one or two of these, in italics, and
then explains. Use the same words elsewhere when weighing a claim.

| Label | Means |
|---|---|
| *replicated* | several independent papers, on different data, find the same thing |
| *single study* | one paper, however careful |
| *single benchmark* | several papers, but all on the same benchmark or dataset |
| *vendor-run* | the authors built or sell the system or model being measured |
| *constructed* | shown in a simulation, a worst case or a synthetic setup, not observed in normal use |
| *small sample* | the result rests on few items, models or raters; say how few |
| *contested* | another paper here finds otherwise; it is also listed under "Where the papers disagree" |
| *flawed benchmark* | measured on a benchmark that later papers call saturated, leaky or mislabelled |
| *superseded* | held until a later paper narrowed or overturned it; say which |

## The In practice section

The rest of the review says what the papers show. This section answers the question a
practitioner asks next: "given all this, what should I do?" It is the one place where the
review gives advice.

- **Write it last.** Once every other section is finished, ask which one or two topics
  someone who relies on these papers in their work would most want recommendations on (for
  LLM evaluation: how to build an LLM-judge evaluation for an application). Name the
  section for the topic. Skip the section when the area has no practical use that the
  papers support (a purely theoretical area, say), and never pad one.
- **Aim it at practical use**, not at the setting most papers study, when the two differ.
  Start by saying what is different for the practitioner.
- **Derive every recommendation from the findings.** Each one carries its evidence, with a
  paper link and a page link for a number. Where the papers are silent, say "no paper here
  tests this"; where they disagree, say so and don't pick a side without a reason. Mark
  anything from general knowledge "(not from the library)".
- **Open with a provenance note**, as a callout, so the reader never mistakes it for a
  tested procedure:

  ```markdown
  > [!warning] Written by an agent from these papers
  > These recommendations were derived by an LLM agent from the <N> papers in this review
  > (<M> read in full, the rest skimmed), as the library stood on <date>. They are a
  > synthesis, not a tested procedure, and nobody has verified them in practice. Recheck
  > them when the review is updated: new papers may overturn them.
  ```

- **Shapes that worked:** what is different in practice; a recommended design as numbered
  steps, each with its evidence; a table of common failures (what happens, the evidence,
  what helps); "common advice, checked against the papers" (supported, contested, or not
  supported); and a short version of five to eight lines at the end.
- **On update**, re-derive it. Change the date in the note, and say in `## Updates` which
  recommendations changed and why.

## Diagrams and figures

A diagram earns its place when it shows a structure the prose cannot: who talks to whom, a
loop, a trade-off between two axes, a hierarchy, an order in time. A numbered list drawn as
a row of boxes adds nothing; write the list.

- **Pick the type that fits.** Mermaid renders all of these:
  - `flowchart` for a pipeline or loop that branches or feeds back (not for a straight
    line of steps);
  - `sequenceDiagram` for interactions between parties (an agent, a user, a tool, a
    judge);
  - `quadrantChart` for placing approaches on two axes;
  - `timeline` for the history;
  - `mindmap` or a top-down `flowchart TD` for a taxonomy;
  - `xychart-beta` for a trend that a finding rests on, with the numbers cited in the
    text.
- **Vary them.** A review whose diagrams are all the same type is a sign that the type
  was chosen by habit. Don't copy the diagram types of an earlier review.
- **Keep them small**: at most 6–8 nodes or participants, labels of a few words.
- **Figures from the papers** are welcome when a paper's own figure explains a mechanism
  or shows a result better than a redrawn one. Link the extracted image by a relative path
  (`../../library/<topic path>/images/<Title>-figNN.<ext>`), and put a caption under it
  naming the paper and the figure, with a page link: "Figure 3 of [HELMET](…),
  [p. 7](…)". Open the image to check that it is the figure you mean and is readable
  on its own. At most a handful per review. `paperlib check` verifies that the file exists.
- **How many:** one in the introduction when the area has an overall structure, then only
  where a family or a finding needs one.

## Links

- **Reference-style.** A review links each paper and each page many times and the encoded
  paths are long, so the prose uses reference-style links, `[MMLU][mmlu]` and
  `[p. 5, Table 1][mmlu@5:table.1]`, with the definitions in one generated block at the
  end of the file. Write links inline or reference-style, whichever is easier, and run
  `paperlib review-refs <scope>` when done: it converts every link to a paper or a PDF
  page, names the labels and rebuilds the block. Never edit the block by hand.
  `paperlib review-refs --inline <scope>` turns a review back into inline links.
- **A paper:** a relative link to its markdown, as `paperlib review-status --links <scope>`
  prints it. The link text is the paper's short name (method or system name, or a few words
  of the title).
- **A place in a paper:** a `pdf.invalid` link as `.claude/library-guide.md` describes
  ("Linking to a place in a paper"), using the pdf base that `--links` prints, plus `?page=N` and `dest` where it
  helps: `[p. 7, Table 2](http://pdf.invalid/…/Zep.%20….pdf?dest=table.2&page=7)`.
- **Another review:** relative, `../search-and-ranking.md`.

`paperlib check` fails on any of these that doesn't resolve, and
`paperlib review-status --fix-links` repairs links to papers that moved.

## Split reviews

A long review is fine as one file. Split only when one file becomes unwieldy to edit
(roughly 1,500 lines): move it to `reviews/<scope>/index.md`, which keeps the frontmatter,
the abstract, the introduction, the kinds section, the map, the history, the disagreements,
the In practice section, open questions, where to start, connections, updates and Q&A. Each finding, or each group of findings, becomes its own file
in the same folder, and the paper map moves to `paper-map.md` (with its `## Paper map`
heading). Links in the moved files go one level deeper (`../../../library/…`).
