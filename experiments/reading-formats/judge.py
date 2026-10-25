#!/usr/bin/env python3
"""Grade every answer to a question against its gold answer, blind to the condition.

    PAPER_LIBRARY=<library> uv run python judge.py [qid ...]     # all questions with answers by default

One request per question, holding all its answers (every condition and rerun) in an
order shuffled with a fixed seed, numbered, without the condition. Writes
results/judge/<qid>.json, keyed by a hash of the answers it graded: a question is judged
again only when its set of answers has changed.
"""

import hashlib
import json
import random
import re
import sys
from pathlib import Path

import run

JUDGE = run.HERE / "results" / "judge"
SYSTEM = "You grade answers to questions about research papers against a gold answer. Reply with JSON only."
PROMPT = """Question: {question}

Gold answer: {gold}{tolerance}{page}

{unanswerable}Grade each numbered answer below independently:
- "score": "correct" (every value or element the question asks for agrees with the gold; notation may differ; a value read off a plot counts when it is inside the tolerance), "partial" (some of the asked values right and none contradicting the gold, or right but missing a part the question asks for), "wrong" (a stated value or claim contradicts the gold), or "declined" (says the document or the model does not give the answer).
- "page_ok": true if the answer cites the gold page (±1) for the gold fact, false if it cites another page for it, null if it cites no page or no page applies.
- "confident_wrong": true if the score is "wrong" and the answer states the wrong value without a hedge (no "about", "appears", "unclear", "cannot read").
- "note": at most 15 words: what is wrong or missing, or "".

Reply with JSON only: {{"1": {{"score": "...", "page_ok": null, "confident_wrong": false, "note": ""}}, "2": {{...}}}}

{answers}"""
UNANSWERABLE = ("The gold says the paper does not report this. An answer that declines, or says it is not reported "
                "and correctly points to what the paper does report, scores \"correct\"; one that gives a value as "
                "the paper's answer scores \"wrong\".\n\n")


def answers(qid):
    """{run id: answer text} for a question, over every experiment and condition."""
    out = {}
    for path in sorted(run.RUNS.glob("*/*/%s-r*.json" % qid)):
        record = json.loads(path.read_text())
        if record["status"] == "ok":
            out["%s/%s/%s-r%d" % (record["exp"], record["cond"], qid, record["rep"])] = record["answer"] or ""
    return out


def grades(qid):
    path = JUDGE / ("%s.json" % qid)
    return json.loads(path.read_text())["grades"] if path.exists() else {}


def judge_one(qid):
    found = answers(qid)
    if not found:
        return
    key = hashlib.sha256(json.dumps(sorted(found.items())).encode()).hexdigest()[:16]
    path = JUDGE / ("%s.json" % qid)
    if path.exists() and json.loads(path.read_text()).get("key") == key:
        return
    q = run.Q[qid]
    names = sorted(found)
    random.Random(qid).shuffle(names)
    # An aggregation question's gold names its list only by reference; the judge needs the names.
    gold = q["gold"] + ("\nThe items: %s." % "; ".join(q["items"]) if q.get("items") else "")
    prompt = PROMPT.format(
        question=q["question"], gold=gold,
        tolerance="\nTolerance: " + q["tolerance"] if q.get("tolerance") else "",
        page="\nGold page (of the PDF): %s" % q["page"] if q.get("page") else "",
        unanswerable=UNANSWERABLE if q.get("answerable") is False else "",
        answers="\n\n".join("===== ANSWER %d =====\n%s" % (n, found[name]) for n, name in enumerate(names, 1)))
    result, _ = run.request(SYSTEM, [{"type": "text", "text": prompt}])
    reply = result.get("result") or ""
    parsed = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
    graded = {name: parsed[str(n)] for n, name in enumerate(names, 1)}
    JUDGE.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"key": key, "usd": result.get("total_cost_usd"), "grades": graded},
                              ensure_ascii=False, indent=1))
    tmp.rename(path)
    print("  judged %s: %s  $%.3f" % (qid, " ".join("%s=%s" % (name.split("/")[1], g["score"][0])
                                                   for name, g in sorted(graded.items())),
                                      result.get("total_cost_usd") or 0), flush=True)


def judge(qids):
    for qid in qids:
        try:
            judge_one(qid)
        except (ValueError, KeyError, RuntimeError) as error:
            print("  judge FAILED on %s: %s" % (qid, str(error)[:200]), flush=True)


if __name__ == "__main__":
    wanted = sys.argv[1:] or sorted({re.sub(r"-r\d+$", "", p.stem) for p in run.RUNS.glob("*/*/*.json")} & set(run.Q))
    judge(wanted)
