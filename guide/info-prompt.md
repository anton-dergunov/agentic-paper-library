You describe a research paper for a reader who has just come across it, from its abstract alone. You report; you do not advise. Never say whether the paper is worth reading, adding or skipping, and never guess what the reader is interested in.

Fill these fields:

- "proposes": two or three plain sentences. What exactly the paper proposes or finds, what is new in it, and what one could use it for. Leave out the background the abstract opens with, and its praise of itself. Attribute results to the authors ("the authors report").
- "type": one of method, survey, benchmark, study, system, position, theory.
- "character": one of mathematical (the contribution is a derivation, proof or formal analysis), empirical (experiments and measurements), practical (a system, tool, model or dataset to use), conceptual (a survey, framework or argument). Add "unclear from the abstract" when it is.
- "evidence": what the abstract says it was tested on and against what, in one line; "not stated" when it does not say.
- "releases": code, weights, data or a benchmark the abstract or the authors' comment says is released; "none stated" otherwise.
- "nearest": the two or three papers of the folder list closest to this one, nearest first. For each: "n" (its number in the list), "relation" (one of same-idea, builds-on, alternative, predecessor, successor, same-problem) and "how" (one line: what this paper does that the listed one does not, or the reverse). An empty list when none is close.

Use only the abstract, the comment and the folder list. Keep numbers exact.

Reply with JSON only: {{"proposes": "...", "type": "...", "character": "...", "evidence": "...", "releases": "...", "nearest": [{{"n": 1, "relation": "...", "how": "..."}}]}}

THE PAPER

Title: {title}
Authors' comment: {comment}

Abstract: {abstract}

Papers of the folder it would be filed in, {folder} ({scope}):
{neighbours}
