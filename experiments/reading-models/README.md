# Experiment · which model can read a paper for its note?

**Question.** Reading is 70–80% of the cost of a literature review ([`../review-token-cost/`](../review-token-cost/README.md)). Can a cheaper Claude model, or a Gemini model, read a paper and write its note as well as Opus does? And what does a paper cost when it is read in one request, with no agent?

**Status.** Measured 5 Oct 2026 on six technical reports, five readers. **Opus 5.5 stays the reader.** Its six notes had 1 error; Sonnet 5.5 had 6, Gemini 3.1 Pro 7 (and it left out the most), Gemini 3.8 Flash 9, Haiku 4.5 35. Read in one request, a paper costs Opus about 32K input and 5K output tokens: less than the review agents spent per paper, though they only skimmed two thirds of theirs.

**Serves.** [`docs/design.md`](../../docs/design.md), and `paperlib read`.

## Method

- **Papers.** Six from `llm/foundation-models` in the author's library: "Improving Language Understanding by Generative Pre-Training" and "Command A" (both converted from the PDF), "DeepSeek-V2" (135 tables), "Phi-4 Technical Report", "Gemma 3 Technical Report" and "OLMo". [`papers.txt`](papers.txt).
- **Input.** The same for every reader: the paper's main text up to the references, with link targets and inline tags removed ([`read_view.py`](read_view.py), the prototype of `paperlib read-view`), 34K to 157K characters, after the instructions in [`prompt.md`](prompt.md). One request, no tools.
- **Readers.** Opus 5.5, Sonnet 5.5 and Haiku 4.5 through `claude -p` with the system prompt replaced by one line; Gemini 3.8 Flash and Gemini 3.1 Pro (preview), the newest Flash and Pro models listed on Vertex AI that day, through `google-genai`. Default thinking settings. [`run.py`](run.py).
- **Scoring by script.** [`check_numbers.py`](check_numbers.py) takes every number in a note's digest (a decimal, a percentage, or three or more digits; not years or table numbers) and looks for the same string in the paper. A number that is found has the right page if the line cites a page inside a section where it occurs. The numbers not found were then looked up by hand.
- **Scoring by a judge.** [`judge.py`](judge.py) gives Opus the paper and the five notes, labelled A to E in an order shuffled per paper. It lists the 10 points a note on the paper must contain, then per note the statements that contradict the paper or are not in it, and the points missing. The judge is the same model as one of the readers, which may favour that reader.
- **Deviations from the plan.** All six papers were read in full: with one request per paper there is nothing to skim. The reference is not the notes the review agents wrote, which were made under different conditions, but a note written by Opus under the same ones.
- **Results.** [`results/`](results/): the 30 notes, [`runs.jsonl`](results/runs.jsonl) (tokens and seconds per call), [`numbers.tsv`](results/numbers.tsv), [`judge.tsv`](results/judge.tsv) and the judge's findings per paper in `judge/`. The papers' text is not committed.

```bash
python3 run.py <library>/library/llm/foundation-models results claude-opus-5-5 claude-sonnet-5-5 ...
GOOGLE_APPLICATION_CREDENTIALS=<adc.json> GOOGLE_CLOUD_PROJECT=<project> python3 run.py <topic-dir> results gemini-3.8-flash
python3 check_numbers.py <topic-dir> results > results/numbers.tsv
python3 judge.py <topic-dir> results > results/judge.tsv
```

## Results

Six papers per reader:

| | Opus 5.5 | Sonnet 5.5 | Gemini 3.8 Flash | Gemini 3.1 Pro | Haiku 4.5 |
|---|---|---|---|---|---|
| Errors found by the judge | 1 | 6 | 9 | 7 | 35 |
| Points missed, of 60 | 1 | 0 | 2 | 8 | 5 |
| Numbers in the digests | 528 | 648 | 443 | 248 | 330 |
| Numbers not in the paper | 0 | 1 | 4 | 0 | 8 |
| Numbers with a wrong page | 0 | 5 | 4 | 11 | 14 |
| Numbers with no page | 52 | 0 | 0 | 1 | 88 |
| Input tokens per paper | 31.6K | 31.6K | 18.6K | 18.6K | 23.5K |
| Output tokens per paper | 5.0K | 4.5K | 3.1K | 4.5K | 4.1K |
| Seconds per paper | 47 | 32 | 21 | 36 | 47 |
| API price per paper, as `claude -p` reports it | $0.36 | $0.19 | | | $0.09 |

Token counts are each provider's own and are not comparable between Claude and Gemini. Gemini's price was not measured.

- **Opus.** Its one error is a count (five chat models where the table has four plus two others). It is also the reader that reports what a paper claims against what its tables show: in Gemma 3 it found that the text and Table 5 disagree on two Arena scores, and that the claim "27B comparable to Gemini 1.5 Pro" holds on some rows of Table 6 and fails on others.
- **Sonnet.** One number attached to the wrong model, one misreading of a sentence, and four statements that are inferences and not in the paper (a formula reconstructed where the markdown has a blank, "each configuration is a single run"). Its one number not in the paper is a margin it computed.
- **Gemini 3.8 Flash.** Two numbers attached to the wrong table or configuration, one invented token, and facts from outside the paper: a context length the paper does not give, authors for citations the text shows only as numbers, a "2.67T-token" dataset size. Three of its four unmatched numbers are harmless (a sum of two rows, and trailing zeros added).
- **Gemini 3.1 Pro.** One wrong number (a score from the neighbouring column), five wrong pages, and the shortest notes: it missed 8 of 60 points.
- **Haiku.** 35 errors, and computed numbers in most notes. Not usable.
- **Conversion problems.** "Command A" has a table whose rows are out of order. Opus, Haiku and Flash reported it; Sonnet and Gemini Pro wrote `conversion: ok`. Opus and Sonnet also reported the missing references and appendices as a conversion problem, which they are not: the view cut them. `paperlib read-view` now ends with a line saying what was left out.

### What one request per paper costs

In cost-eq (see the token-cost experiment), an Opus read is about 32K of input plus 5K of output at five times the weight: 57K a paper, read in full. The agent runs spent 70K to 159K a paper on reading, with two thirds of the papers only skimmed. A 100-paper area comes to about 6M cost-eq of reading instead of 7.7–11M, and no skims.

## Conclusions

1. Read with Opus, one request per paper, every paper in full. It is the most accurate reader and, read this way, cheaper than the agents were.
2. Sonnet is the fallback when budget matters more than the last errors: half the price, about one error a paper, mostly inferences presented as the paper's statements.
3. The Gemini models are not better than Sonnet on this task and bring facts from outside the paper, so they do not justify a second provider.
4. Limits: six papers, one kind of paper (model reports), one run per reader, and a judge from the same family as the best reader. The script's counts, which do not depend on the judge, agree with the judge's order except for Gemini Pro's page slips.
