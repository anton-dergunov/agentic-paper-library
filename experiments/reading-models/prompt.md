You are reading one paper from a research-paper library for a literature review of `llm/foundation-models` (model families and their technical reports). The review asks what each generation of model report changed (architecture, data, training recipe, post-training, evaluation), what is claimed versus actually disclosed, and how strong the evidence is, given that the authors usually built the model they measure.

The paper's main text follows, converted to markdown. Headings carry the PDF page they start on, as in `## 3 Method (p. 4)`. Read all of it.

Write the paper's note in exactly this format, and nothing else:

```
# <Title>

type: method | survey | benchmark | study | system | position | theory
read: full
family: <the kind of approach or report it is, in a few words>
evidence: <what it was tested on, against what>; strength: <replicated / one benchmark / vendor-run / no ablations / …>
conversion: ok | <what is broken in the markdown, and where (p. N)>

## Digest

At most 20 bullet lines: the mechanism, the key definitions, what is disclosed and what is not, and the main numbers with their baselines. Every number carries its page and, where there is one, its table or figure: (p. N, Table M). Take pages from the nearest heading above the passage; if a section runs over several pages, give the range of that section.

## Related

- <other paper or model it builds on, compares with or contradicts>: how, in one line
```

Rules:
- Quote numbers exactly as the paper prints them. Never round, convert or compute a number, and never give one you did not see in the text.
- Every number names its baseline or what it is compared with.
- Check the conversion as you read: garbled or missing equations, tables flattened into text, a truncated body, numbers that look wrong. Say so under `conversion`, and do not quote a number from a broken table without saying it is unreliable.

The paper:

