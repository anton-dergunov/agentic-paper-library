"""Have Opus grade the three notes on each test paper against the paper, blind to the condition.

    PAPER_LIBRARY=<library> python3 judge.py

Adapted from ../reading-models/judge.py. For each paper of papers.txt the judge gets the
reading view and the notes in results/notes/<condition>/, labelled A, B, C in an order
shuffled per paper (seeded by its name). It lists the points a note must contain, then per
note the statements that contradict the paper or are not in it, the points it lacks, and
whether its `conversion` line is right. Writes results/judge/<stem>.json with the key from
letters to conditions, then prints a table; also compares the "Related in library" sections.
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from paperlib import LIBRARY_DIR, read_paper, read_view  # noqa: E402

TOPIC = "llm/foundation-models"
# What `claude -p` says when the account's usage window is used up.
LIMIT = re.compile(r"(session|usage|weekly|daily|monthly) limit|resets? (at )?\d|quota|credit balance", re.I)
PROMPT = """You are grading notes that three readers wrote on the same paper, for a literature review of model technical reports. The paper's main text comes first (as the readers saw it, without references), then the notes, labelled by letter.

Step 1. From the paper alone, list the 10 points a note must contain to be useful for comparing this paper with others: its mechanism or recipe, what it discloses and withholds, and its main results with their baselines.

Step 2. For each note:
- "errors": every statement that contradicts the paper or is not in it: a wrong number, a number attached to the wrong model, baseline, benchmark or table, a wrong page (pages are on the headings; a section's range is acceptable), a mechanism described wrongly. Quote the note, then say what the paper says and where. Do not count omissions, rounding the paper itself does, or matters of emphasis. Check each suspected error against the text before listing it.
- "missed": the numbers of the Step 1 points the note lacks.
- "conversion": is the note's `conversion` line right about the markdown you see? "right", or what it misses or gets wrong, in a few words. Missing references and appendices are not conversion problems.

Reply with JSON only:
{"points": ["1 ...", ...], "notes": {"A": {"errors": [{"quote": "...", "paper": "..."}], "missed": [3, 7], "conversion": "..."}, ...}}

"""


def related(note):
    section = note.split("## Related in library", 1)[-1].split("## Q&A", 1)[0]
    return {m.strip() for m in re.findall(r"^- ([^:]+):", section, re.M)}


def main():
    conditions = sorted(p.name for p in (HERE / "results" / "notes").iterdir() if p.is_dir())
    out = HERE / "results" / "judge"
    out.mkdir(exist_ok=True)
    rows, usd = [], 0.0
    for stem in [s.strip() for s in open(HERE / "papers.txt") if s.strip()]:
        target = out / f"{stem}.json"
        notes = {c: (HERE / "results" / "notes" / c / f"{stem}.md").read_text() for c in conditions}
        if not target.exists():
            order = list(conditions)
            random.Random(stem).shuffle(order)
            key = {chr(65 + i): c for i, c in enumerate(order)}
            prompt = PROMPT + "THE PAPER\n\n" + read_view(*read_paper(LIBRARY_DIR / TOPIC / f"{stem}.md"))
            for letter, condition in key.items():
                prompt += f"\n\nNOTE {letter}\n\n{notes[condition]}"
            env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
                   "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
            with tempfile.TemporaryDirectory() as empty:
                done = subprocess.run(
                    ["claude", "-p", "--model", "claude-opus-5-5", "--tools", "", "--system-prompt",
                     "You are a careful grader. You verify every claim against the source text.",
                     "--output-format", "json", "--no-session-persistence"],
                    input=prompt, capture_output=True, text=True, cwd=empty, env=env)
            try:
                reply = json.loads(done.stdout)
                text = reply["result"]
                if reply.get("is_error"):
                    raise ValueError(text)
                grade = json.loads(text[text.index("{"):text.rindex("}") + 1])
            except (ValueError, KeyError) as error:
                message = str(error)[:300] or done.stderr[:300]
                if LIMIT.search(message + done.stdout[-2000:] + done.stderr[-2000:]):
                    print(f"judge: usage limit at {stem}: {message}\nSwitch account and run the "
                          "same command again; papers already judged are kept.", file=sys.stderr)
                    sys.exit(3)
                sys.exit(f"judge: failed at {stem}: {message}\nRun the same command again to retry.")
            grade["key"], grade["usd"] = key, reply.get("total_cost_usd")
            target.write_text(json.dumps(grade, indent=1, ensure_ascii=False))
        grade = json.loads(target.read_text())
        usd += grade.get("usd") or 0
        for letter, condition in grade["key"].items():
            note = grade["notes"][letter]
            rows.append((condition, stem[:30], len(note["errors"]), len(note["missed"]),
                         len(related(notes[condition])), note["conversion"]))
        base = related(notes[conditions[0]])
        for c in conditions[1:]:
            other = related(notes[c])
            both = len(base & other)
            print(f"related, {stem[:30]}: {conditions[0]} {len(base)}, {c} {len(other)}, in both {both}")
    print("\ncondition\tpaper\terrors\tpoints missed of 10\trelated listed\tconversion line")
    for row in sorted(rows):
        print("%s\t%s\t%d\t%d\t%d\t%s" % row)
    print(f"\njudge: ${usd:.2f}")


if __name__ == "__main__":
    main()
