# Experiment · which model can file a paper and write its index line?

**Question.** The `add-paper` skill runs a script, chooses the paper's folder and writes a one-line summary. Does that need an agent session, or Opus? Given only the topic tree, the title and the abstract, which model picks the folder and writes the summary well enough in one request?

**Status.** Measured 5 Oct 2026 on 60 papers from 60 folders of the author's library. A blind judge graded the folder "best" for 57 papers with Opus 5.5, 53 with Sonnet 5.5 and 49 with Haiku 4.5, against 47 for the folders the papers are in now. Sonnet's summaries were graded level with Opus's (4.8 of 5) and above Haiku's (3.5), which contradicted the abstract in 8 of 60. One request takes about 9K tokens and 4 seconds, against 228K tokens and 55 seconds for the skill in a Sonnet session. **`paperlib add` shipped with Sonnet as the filing model**, and the `add-paper` skill is set to Sonnet.

**Serves.** [`docs/design.md`](../../docs/design.md), `paperlib add`, and the "Which model" table in the [README](../../README.md).

## Method

- **Papers.** One paper from each of 60 folders of the author's library (2,204 papers, 115 declared folders), drawn with a fixed seed from the papers that have an abstract heading and a stored summary. One per folder, so that small folders count as much as large ones: the sample is harder than the papers that arrive day to day. [`sample.py`](sample.py), [`papers.txt`](papers.txt).
- **Input.** The same for every model, in [`prompt.md`](prompt.md): the topic tree (every folder with its scope), three summaries from the library as a style sample, the paper's title and its abstract as converted, cut at 3,000 characters. Not the folder indexes, which the skill reads.
- **Models.** Haiku 4.5, Sonnet 5.5 and Opus 5.5 through `claude -p` with no tools and the system prompt replaced by one line, default thinking. [`run.py`](run.py).
- **Scoring by script.** Whether the folder is the one the paper is in, or near it (parent, child or sibling). [`score.py`](score.py).
- **Scoring by a judge.** The folder a paper is in was itself chosen by a model, so it is a candidate, not the answer. [`judge.py`](judge.py) gives Opus the tree, the title and abstract, the distinct folders proposed (the three models' and the current one) and the four summaries (the three models' and the stored one), each list shuffled per paper and labelled by letter. It grades each folder best, acceptable or wrong, and for each summary lists the statements that contradict the abstract and those that go beyond it, and gives a quality mark from 1 to 5 as an index line.
- **Results.** [`results/`](results/): each model's answers (`<model>.jsonl`, with tokens and seconds), [`folders.tsv`](results/folders.tsv), [`summaries.tsv`](results/summaries.tsv) and the judge's findings per paper in `judge/`. The abstracts and the stored summaries are not committed.

```bash
python3 sample.py <library> 60 > papers.txt
python3 run.py <library> results
python3 judge.py <library> results
python3 score.py <library> results
```

## Results

Sixty papers per column:

| | Haiku 4.5 | Sonnet 5.5 | Opus 5.5 | As filed now |
|---|---|---|---|---|
| Folder is the one the paper is in | 45 | 46 | 49 | |
| Folder is next to it | 4 | 5 | 5 | |
| Folder judged best | 49 | 53 | 57 | 47 |
| Folder judged acceptable | 8 | 3 | 1 | 9 |
| Folder judged wrong | 3 | 4 | 2 | 4 |
| Folder not in the tree, or "none" | 0 | 0 | 0 | |
| Summary quality, mean of 5 | 3.5 | 4.8 | 4.8 | 3.7 |
| Summaries contradicting the abstract | 8 | 3 | 0 | 3 |
| Statements beyond the abstract | 15 | 10 | 10 | 23 |
| Words per summary | 23 | 33 | 33 | 24 |
| Input tokens per paper | 6.9K | 9.3K | 9.6K | |
| Output tokens per paper | 2.1K | 0.2K | 0.2K | |
| Seconds per paper | 21 | 3.7 | 4.3 | |
| API price per paper, as `claude -p` reports it | $0.029 | $0.037 | $0.069 | |

- **Every model files at least as well as the library is filed now.** Where a model left the current folder, the judge more often preferred the model's choice: Adaptive-RAG is in `llm/routing` and all three chose `llm/retrieval-augmented`.
- **The "wrong" folders are mostly close calls.** Sonnet's four: a survey put in a subfolder where the parent was better, a benchmark-or-method call inside `llm/evaluation` (where it agreed with the current folder), `llm/evaluation/methods` for a study of LLM feedback on research papers (filed under `research-practice`), and a paper for which the judge rejected the one folder that all three models and the library agree on.
- **Sonnet's three contradictions are loose wording**, in the judge's own description: "field experiment" for a controlled one, "matches" for "comparable", "lower cost" for "faster". Haiku's eight include wrong attributions.
- **Haiku is not cheaper here.** It spent ten times the output tokens of the others, on thinking, and took five times as long.
- **Stored summaries.** One of the three the judge flagged is a real error: the summary of "Measuring AI Ability to Complete Long Software Tasks" gives a time horizon of about 50 minutes where the stored abstract says about 110. Their 23 statements beyond the abstract are expected: many were written from the paper's body.
- **Against the skill.** The `add-paper` skill run with Sonnet on one arXiv paper the same day took 5 requests, 228K input tokens and 55 seconds, nearly all of it the session's own context sent five times. One filing request is 9.3K tokens and 4 seconds, before the conversion, which costs the same either way.

## Caveats

- **The judge is Opus**, one of the three models, and it may favour its own answers. Its quality mark also rises with length: the two models it marked highest wrote 33 words against 24.
- **Summaries were checked against the abstract only**, so "beyond" is not "wrong", and an error that needs the paper's body to see is not counted.
- **One request per cell.** A difference of two or three papers between models is within what a second run could change; Haiku's gap in summaries is not.
- **Not measured:** papers that need a new folder (none of the 180 answers was "none", and every sampled paper has a folder that fits), papers without an arXiv abstract, and the two or three sentences on related papers that the skill reports.

## Decision

- **`paperlib add <arxiv-id> ...`** files a paper with one request to the filing model (`filing_model` in `paper-library.yaml`, default Sonnet), using this prompt with a length limit on the summary ([`guide/filing-prompt.md`](../../guide/filing-prompt.md)). It never creates a folder.
- **The `add-paper` skill stays**, on Sonnet, for what the command does not do: a new folder, a paper named by title, a web page or a PDF, the inbox, and how the paper relates to the library.
- **Opus is not needed for filing**; it is two papers in sixty better than Sonnet on a judge that may favour it, at twice the price.
