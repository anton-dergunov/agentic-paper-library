You are reading one paper from a research-paper library and writing its note: what a later reader, or a literature review, needs in order to compare this paper with others without reading it again.

{{focus}}The paper's main text is in the message, as its PDF's text layer (`pdftotext -layout`, two-column pages side by side), with a line `[page N]` where each page starts. The references and what follows them were left out on purpose; the last line says what. Read all of it.

Write the note in exactly this format, and nothing else:

```
# <Title>

type: method | survey | benchmark | study | system | position | theory
family: <the kind of approach it belongs to, in a few words>
evidence: <what it was tested on, against what>; strength: <replicated / one benchmark / vendor-run / no ablations / …>

## Digest

At most 20 bullet lines: the claim, the mechanism in plain words, the key definitions, what the paper leaves out or does not disclose, and the main numbers with their baselines. Say where the text claims more than its tables show. If the paper prints things that disagree with each other (two values for one number, a count that does not add up), end with one bullet: `- The paper's own inconsistencies: <what> (p. N); <what> (p. N).`

## Related in library

- <stem>: how it relates, in one line
```

Rules:
- `type` is one of the seven: the closest one when the paper is mixed or unclear.
- Every number carries its page and, if there is one, its table or figure: (p. N, Table M). Take the page from the nearest `[page N]` line above the passage.
- Quote numbers exactly as the paper prints them. Never round, convert or compute a number, and never give one that is not in the text.
- Every number names its baseline, or what it is compared with.
- State only what the paper says. Do not add facts you know from elsewhere (a cited paper's authors, a predecessor's settings), and do not present an inference as the paper's statement.
- A number or an equation whose text looks garbled (a digit or a sign missing, a fraction spread over lines): say so in the digest, and do not quote it as exact. Write a formula in LaTeX (`$…$`), rewritten from the text rather than copied, with its symbols defined. A result given only in a plot is not in the text: say which figure shows it (p. N, Figure M) rather than that it is not disclosed.
- "Related in library" lists only other papers from the list below (it includes this one), by exact name, that this paper builds on, compares with or contradicts; leave it empty if none.

Papers in the same area of the library:

{{related}}

