You are reading one paper from a research-paper library and writing its note: what a later reader, or a literature review, needs in order to compare this paper with others without reading it again.

{{focus}}The paper's main text follows, converted to markdown. Headings carry the PDF page they start on, as in `## 3 Method (p. 4)`. The references and whatever follows them were left out on purpose; the last line says what. Read all of it.

Write the note in exactly this format, and nothing else:

```
# <Title>

type: method | survey | benchmark | study | system | position | theory
read: full
family: <the kind of approach it belongs to, in a few words>
evidence: <what it was tested on, against what>; strength: <replicated / one benchmark / vendor-run / no ablations / …>
conversion: ok | <what is broken in the markdown, and where (p. N)>

## Digest

At most 20 bullet lines: the claim, the mechanism in plain words, the key definitions, what the paper leaves out or does not disclose, and the main numbers with their baselines. Say where the text claims more than its tables show.

## Related in library

- <stem>: how it relates, in one line
```

Rules:
- Every number carries its page and, where there is one, its table or figure: (p. N, Table M). Take the page from the nearest heading above the passage; if a section runs over several pages, give the section's range.
- Quote numbers exactly as the paper prints them. Never round, convert or compute a number, and never give one that is not in the text.
- Every number names its baseline, or what it is compared with.
- State only what the paper says. Do not add facts you know from elsewhere (a cited paper's authors, a predecessor's settings), and do not present an inference as the paper's statement.
- `conversion`: report garbled or missing equations, tables flattened into text or with rows out of order, a truncated body, and numbers that look wrong. The missing references, appendices and figure images are not conversion problems, and neither are cosmetic flaws that leave the content readable (footnote markers fused into the text, a scrambled author block, stray cross-reference text): write `ok` when those are all there is. Do not quote a number from a broken table without saying it is unreliable.
- "Related in library" lists only papers from the list below, by their exact name, and only those this paper builds on, compares with or contradicts. Leave the section empty if there are none.

Papers in the same area of the library:

{{related}}

The paper:

