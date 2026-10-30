"""Have Opus grade the notes of each condition on each test paper, blind, and pick the best.

    PAPER_LIBRARY=<library> python3 judge.py

Adapted from ../prompt-trim/judge.py. For each paper of papers.txt the judge gets the reading
view and the notes in results/notes/<condition>/, labelled A, B, C in an order shuffled per
paper (seeded by its name). It lists the points a note must contain, then per note the
statements that contradict the paper or are not in it and the points it lacks, and names the
note it would keep. Writes results/judge/<stem>.json with the key from letters to conditions,
then prints a table.
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from paperlib import LIBRARY_DIR, ask_model, read_paper, text_view  # noqa: E402

PROMPT = """You are grading notes that several readers wrote on the same paper, for a research-paper library where an agent answers questions from the notes and the paper. The paper's main text comes first (as the readers saw it, without references), then the notes, labelled by letter. Ignore the "Related in library" sections.

Step 1. From the paper alone, list the 10 points a note must contain to be useful: the problem and the method or recipe, the setup behind the results, and the main results with their baselines.

Step 2. For each note:
- "errors": every statement that contradicts the paper or is not in it: a wrong number, a number attached to the wrong method, baseline, dataset or table, a wrong page, a mechanism described wrongly. Quote the note, then say what the paper says and where. Do not count omissions, rounding the paper itself does, or matters of emphasis. Check each suspected error against the text before listing it.
- "missed": the numbers of the Step 1 points the note lacks.

Step 3. "best": the letter of the note you would keep in the library, and in one sentence why.

Reply with JSON only:
{"points": ["1 ...", ...], "notes": {"A": {"errors": [{"quote": "...", "paper": "..."}], "missed": [3, 7]}, ...}, "best": {"letter": "A", "why": "..."}}

"""


def main():
    conditions = sorted(p.name for p in (HERE / "results" / "notes").iterdir() if p.is_dir())
    out = HERE / "results" / "judge"
    out.mkdir(exist_ok=True)
    rows, best, usd = [], {}, 0.0
    for line in [s.strip() for s in open(HERE / "papers.txt") if s.strip()]:
        paper = LIBRARY_DIR / f"{line}.txt"
        target = out / f"{paper.stem}.json"
        if not target.exists():
            order = list(conditions)
            random.Random(paper.stem).shuffle(order)
            key = {chr(65 + i): c for i, c in enumerate(order)}
            prompt = PROMPT + "THE PAPER\n\n" + text_view(*read_paper(paper))
            for letter, condition in key.items():
                prompt += f"\n\nNOTE {letter}\n\n" + (HERE / "results" / "notes" / condition / f"{paper.stem}.md").read_text()
            text, usage = ask_model("opus", "You are a careful grader. You verify every claim against the source text.", prompt)
            grade = json.loads(text[text.index("{"):text.rindex("}") + 1])
            grade["key"], grade["usage"] = key, usage
            target.write_text(json.dumps(grade, indent=1, ensure_ascii=False))
        grade = json.loads(target.read_text())
        usd += grade["usage"].get("usd") or 0
        best[paper.stem] = grade["key"][grade["best"]["letter"]]
        for letter, condition in grade["key"].items():
            note = grade["notes"][letter]
            rows.append((condition, paper.stem[:30], len(note["errors"]), len(note["missed"]),
                         "best" if best[paper.stem] == condition else ""))
    print("condition\tpaper\terrors\tpoints missed of 10\tbest")
    for row in sorted(rows):
        print("%s\t%s\t%d\t%d\t%s" % row)
    for c in conditions:
        mine = [r for r in rows if r[0] == c]
        print(f"{c}: errors {sum(r[2] for r in mine)}, missed {sum(r[3] for r in mine)}, best {sum(r[4] == 'best' for r in mine)}")
    print(f"judge: ${usd:.2f}")
    (HERE / "results" / "best.json").write_text(json.dumps(best, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
