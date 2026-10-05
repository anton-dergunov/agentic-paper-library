"""Have Opus grade the notes on each paper against the paper, blind to who wrote them.

    python3 judge.py <library>/library/<topic> <results-dir>

For each paper the judge gets the reading view and every reader's note, labelled A, B, …
in an order shuffled per paper (seeded by the paper's name). It first lists the points a
note on this paper must contain, then, per note, the statements that contradict the paper
and the listed points it lacks. Writes <results-dir>/judge/<stem>.json, with the key from
letters to readers, and prints a table.
"""
import glob
import json
import os
import random
import subprocess
import sys

from read_view import read_view

PROMPT = """You are grading notes that five readers wrote on the same paper, for a literature review of model technical reports. The paper's main text comes first, then the notes, labelled by letter.

Step 1. From the paper alone, list the 10 points a note must contain to be useful for comparing this paper with others: its mechanism or recipe, what it discloses and withholds, and its main results with their baselines.

Step 2. For each note:
- "errors": every statement that contradicts the paper or is not in it: a wrong number, a number attached to the wrong model, baseline, benchmark or table, a wrong page (pages are on the headings; a section's range is acceptable), a mechanism described wrongly. Quote the note, then say what the paper says and where. Do not count omissions, rounding the paper itself does, or matters of emphasis. Check each suspected error against the text before listing it.
- "missed": the numbers of the Step 1 points the note lacks.
- "conversion_flagged": what the note says under `conversion`, in a few words.

Reply with JSON only:
{"points": ["1 ...", ...], "notes": {"A": {"errors": [{"quote": "...", "paper": "..."}], "missed": [3, 7], "conversion_flagged": "..."}, ...}}

"""


def main():
    topic, results = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(results, "judge"), exist_ok=True)
    readers = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(results, "*", ""))
                     if not p.rstrip("/").endswith("judge"))
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for stem in [line.strip() for line in open(os.path.join(here, "papers.txt")) if line.strip()]:
        target = os.path.join(results, "judge", stem + ".json")
        if not os.path.exists(target):
            order = [r for r in readers if os.path.exists(os.path.join(results, r, stem + ".md"))]
            random.Random(stem).shuffle(order)
            key = {chr(65 + i): reader for i, reader in enumerate(order)}
            prompt = PROMPT + "THE PAPER\n\n" + read_view(open(os.path.join(topic, stem + ".md")).read())
            for letter, reader in key.items():
                prompt += "\n\nNOTE %s\n\n%s" % (letter, open(os.path.join(results, reader, stem + ".md")).read())
            done = subprocess.run(
                ["claude", "-p", "--model", "claude-opus-5-5", "--tools", "", "--system-prompt",
                 "You are a careful grader. You verify every claim against the source text.",
                 "--output-format", "json", "--no-session-persistence"],
                input=prompt, capture_output=True, text=True, cwd="/tmp")
            text = json.loads(done.stdout)["result"]
            grade = json.loads(text[text.index("{"):text.rindex("}") + 1])
            grade["key"] = key
            json.dump(grade, open(target, "w"), indent=1, ensure_ascii=False)
        grade = json.load(open(target))
        for letter, reader in grade["key"].items():
            note = grade["notes"][letter]
            rows.append((reader, stem[:30], len(note["errors"]), len(note["missed"])))
    print("reader\tpaper\terrors\tpoints missed of 10")
    for row in sorted(rows):
        print("%s\t%s\t%d\t%d" % row)


if __name__ == "__main__":
    main()
