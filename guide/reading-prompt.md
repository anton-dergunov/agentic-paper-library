You are reading one paper from a research-paper library and writing its note: what a later reader, or a literature review, needs in order to compare this paper with others without reading it again.

{{focus}}The paper's main text is in the message, converted to markdown, with the PDF page on each heading (`## 3 Method (p. 4)`). The references and what follows them were left out on purpose; the last line says what. Read all of it.

Write the note in exactly this format, and nothing else:

```
# <Title>

type: method | survey | benchmark | study | system | position | theory
read: full
family: <the kind of approach it belongs to, in a few words>
evidence: <what it was tested on, against what>; strength: <replicated / one benchmark / vendor-run / no ablations / …>
conversion: ok | <what is broken in the markdown, and where (p. N)> | key-content-broken: <what is broken, and where (p. N)>

## Digest

At most 20 bullet lines: the claim, the mechanism in plain words, the key definitions, what the paper leaves out or does not disclose, and the main numbers with their baselines. Say where the text claims more than its tables show.

## Related in library

- <stem>: how it relates, in one line
```

Rules:
- Every number carries its page and, if there is one, its table or figure: (p. N, Table M). Take the page from the nearest heading above the passage; for a section over several pages, give its range.
- Quote numbers exactly as the paper prints them. Never round, convert or compute a number, and never give one that is not in the text.
- Every number names its baseline, or what it is compared with.
- State only what the paper says. Do not add facts you know from elsewhere (a cited paper's authors, a predecessor's settings), and do not present an inference as the paper's statement.
- `conversion`: report garbled or missing equations, tables flattened into text or with rows out of order, a truncated body, and numbers that look wrong. The missing references, appendices and figure images are not conversion problems, and neither are cosmetic flaws that leave the content readable (footnote markers fused into the text, a scrambled author block, stray cross-reference text): write `ok` when those are all there is.
  Start the description with `key-content-broken:` when a part the paper's findings rest on is missing or wrong in the markdown: a results table that is absent, flattened past reading, or has values in the wrong rows or columns; marking lost that carries a claim (bold for the significant results, shading that separates conditions); the main method's equation unreadable; a missing section or a truncated body. Leave it out when the meaning can still be recovered (an equation garbled but explained in the prose, a table readable by order, reading order scrambled on one page) or the broken part is incidental to the findings.
  Do not quote a number from a broken table without saying it is unreliable.
- "Related in library" lists only other papers from the list below (it includes this one), by exact name, that this paper builds on, compares with or contradicts; leave it empty if none.

Papers in the same area of the library:

{{related}}

