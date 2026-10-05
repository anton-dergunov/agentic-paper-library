"""Grade the three answers to each question against the papers, blind to the condition.

    python3 judge.py <answers-dir> <library> <out-dir>

For each question the judge (Opus, in a headless session inside the full library, able
to read files and run shell commands but not to edit) gets the answers labelled A, B, C
in an order shuffled per question. It pools the distinct points the answers make, checks
each one against the paper's markdown, and reports per answer: the points it makes that
hold, the statements that are wrong, and the pooled points it lacks. Writes
<out-dir>/judge-<question>.json with the key from letters to conditions.
"""
import glob
import json
import os
import random
import subprocess
import sys

PROMPT = """Three assistants answered the same question from this paper library. Grade the answers against the papers. Do not use reviews/ or notes/ as evidence: verify against the paper markdown under library/ (grep for the number or phrase; headings carry the page as "(p. N)").

Question: %s

Steps:
1. Pool the distinct substantive points the three answers make (a finding, a mechanism, a number with its baseline). Merge duplicates. Keep at most 20, the ones that matter most for the question.
2. Verify every pooled point in the paper it is attributed to. Mark it "holds", "wrong" (say what the paper says and where) or "unverifiable" (no paper named, or the paper is not in the library).
3. Per answer: which pooled points it makes; every statement in it that is wrong, including wrong numbers, wrong attributions and wrong pages (a page off by one section is wrong; a section's range is fine); how many distinct library papers it cites; and whether it would mislead a reader on the main question.

Reply with JSON only:
{"points": [{"id": 1, "point": "...", "paper": "...", "verdict": "holds|wrong|unverifiable", "evidence": "..."}],
 "answers": {"A": {"makes": [1, 2], "errors": [{"quote": "...", "paper_says": "..."}], "papers_cited": 0, "misleading": "no|<how>", "comment": "..."}, "B": {}, "C": {}},
 "ranking": ["best letter", "...", "worst letter"], "why": "..."}

"""


def main():
    answers, library, out = sys.argv[1:4]
    here = os.path.dirname(os.path.abspath(__file__))
    for line in open(os.path.join(here, "questions.txt")):
        key, question = line.rstrip("\n").split("\t")
        target = os.path.join(out, "judge-%s.json" % key)
        if os.path.exists(target):
            continue
        files = sorted(glob.glob(os.path.join(answers, "*-%s.md" % key)))
        random.Random(key).shuffle(files)
        letters = {chr(65 + i): os.path.basename(f)[:-3].rsplit("-", 1)[0] for i, f in enumerate(files)}
        prompt = PROMPT % question
        for i, f in enumerate(files):
            prompt += "\n\n===== ANSWER %s =====\n\n%s" % (chr(65 + i), open(f).read())
        done = subprocess.run(
            ["claude", "-p", "--model", "claude-opus-5-5", "--output-format", "json",
             "--allowedTools", "Read", "Bash", "--disallowedTools", "Write", "Edit", "Agent",
             "WebSearch", "WebFetch", "NotebookEdit", "Skill", "--strict-mcp-config",
             "--no-session-persistence"],
            input=prompt, capture_output=True, text=True, cwd=library)
        reply = json.loads(done.stdout)
        text = reply["result"]
        grade = json.loads(text[text.index("{"):text.rindex("}") + 1])
        grade["key"] = letters
        grade["judge_usd"] = reply.get("total_cost_usd")
        json.dump(grade, open(target, "w"), indent=1, ensure_ascii=False)
        print(key, letters, grade.get("ranking"), flush=True)


if __name__ == "__main__":
    main()
