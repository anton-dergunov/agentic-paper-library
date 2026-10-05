"""Have Opus grade, per paper, the folders and the summaries, blind to where each came from.

    python3 judge.py <library> <results-dir>

The judge gets the topic tree, the paper's title and abstract, the distinct folders proposed
(the models' and the one the paper is in), and the summaries (the models' and the stored
one), each labelled by letter in an order shuffled per paper. Writes
<results-dir>/judge/<n>.json with the keys from letters to sources. A paper already judged
is skipped.
"""
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import MODELS, ask, json_in, paper

HERE = Path(__file__).parent
PROMPT = """You are grading how a research paper was filed in a library and summarised for the folder index.

The library's topic tree, one folder per line with its scope:

{topics}

THE PAPER

Title: {title}

Abstract: {abstract}

PART 1. FOLDERS. These folders were proposed for the paper:
{folders}

Grade each: "best" (where a reader would look first; several may be best), "acceptable" (a reader would also look here and the scope covers the paper) or "wrong" (the scope does not cover it, or a clearly better folder exists and this one would hide the paper).

PART 2. SUMMARIES. These one-line summaries were written for the index:
{summaries}

For each, list:
- "contradicts": statements that contradict the abstract (a wrong number, a result attached to the wrong thing, a claim the abstract denies). Quote the summary and say what the abstract says.
- "beyond": statements that are not in the abstract and do not contradict it. They may come from the paper's body, which you cannot see.
- "quality": 1 to 5 as an index line: 5 states the mechanism or the main result specifically and briefly; 1 is vague, or only restates the title.

Reply with JSON only:
{{"folders": {{"A": "best", ...}}, "summaries": {{"A": {{"contradicts": ["..."], "beyond": ["..."], "quality": 4}}, ...}}}}
"""


def main():
    library, results = sys.argv[1], Path(sys.argv[2])
    (results / "judge").mkdir(exist_ok=True)
    stems = [line.strip() for line in open(HERE / "papers.txt") if line.strip()]
    answers = {m: {r["paper"]: r for r in map(json.loads, open(results / (m + ".jsonl")))} for m in MODELS}
    topics = "\n".join(line for line in (Path(library) / "catalog/topics.yaml").read_text().splitlines()
                       if line and not line.startswith("#"))

    def one(item):
        number, relative = item
        target = results / "judge" / f"{number:02d}.json"
        if target.exists():
            return
        p = paper(library, relative)
        draw = random.Random(relative)
        folders = sorted({p["folder"]} | {str(answers[m][relative]["folder"]) for m in MODELS})
        draw.shuffle(folders)
        writers = ["stored"] + MODELS
        draw.shuffle(writers)
        letter = lambda i: chr(65 + i)
        summary = lambda w: p["summary"] if w == "stored" else answers[w][relative]["summary"]
        prompt = PROMPT.format(
            topics=topics, title=p["title"], abstract=p["abstract"],
            folders="\n".join(f"{letter(i)}. {f}" for i, f in enumerate(folders)),
            summaries="\n".join(f"{letter(i)}. {summary(w)}" for i, w in enumerate(writers)))
        try:
            text, _ = ask("claude-opus-5-5", "You are a careful grader. You verify every claim against the source text.", prompt)
            grade = json_in(text)
        except Exception as error:
            print(relative, "FAILED", str(error)[:200], flush=True)
            return
        grade.update(paper=relative, folder_key={letter(i): f for i, f in enumerate(folders)},
                     summary_key={letter(i): w for i, w in enumerate(writers)})
        json.dump(grade, open(target, "w"), indent=1, ensure_ascii=False)

    with ThreadPoolExecutor(4) as pool:
        list(pool.map(one, enumerate(stems, 1)))


if __name__ == "__main__":
    main()
