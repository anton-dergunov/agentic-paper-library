#!/usr/bin/env python3
"""Does a model answer questions about a paper as well from its LaTeX as from the library's markdown?

    PAPER_LIBRARY=<library> uv run python qa.py questions <papers.tsv> > results/questions.jsonl
    PAPER_LIBRARY=<library> uv run python qa.py answer results/questions.jsonl > results/answers.jsonl
    uv run python qa.py grade results/questions.jsonl results/answers.jsonl > results/grades.jsonl
    uv run python qa.py table results/grades.jsonl results/answers.jsonl

questions  Six questions a paper, each with the answer and where the paper
           gives it: three written by a model reading the library's markdown
           and three by a model reading the stripped LaTeX (tex.tex of
           convert.py), so that neither form is favoured by who set the
           questions. Each set asks for an equation, a number in a table, and
           a statement that depends on a cross-reference or a citation.
answer     Each paper's six questions are put to the model in one request
           over each form of the paper: `library`, `pandoc`, `tex`. One
           request, no tools, as `paperlib read` reads a paper.
grade      A judge that does not see which form an answer came from marks
           each answer right, partly right or wrong against the expected one.
table      Scores by form and by who set the question, and the tokens of a request.
"""

import collections
import json
import random
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import CACHE_DIR, ask_model, paper_files, read_paper  # noqa: E402

OUT = CACHE_DIR / "experiments" / "latex-source"
FORMS = {"pandoc": "pandoc.md", "tex": "tex.tex"}
SETTER, READER, JUDGE = "opus", "sonnet", "opus"

SET_SYSTEM = """You write exam questions about a research paper to test whether a reader has the paper's exact content. \
Write three questions, each answerable from one place in the paper and from nowhere else:
1. about a display equation: what a term of it is, or what it states (name the equation by what it defines, not by its number);
2. about one number in a results table (name the row and the column in words);
3. about a statement that refers to another part of the paper or to another work: which table, figure, section or cited work it points to, and what is said about it.
Do not ask about the abstract. Do not use labels, macro names or file names in a question. \
Reply with a JSON list of three objects with the keys "kind" ("equation", "table" or "reference"), "question", \
"answer" (one or two sentences, with the exact value or expression) and "where" (the section, table or equation). Reply with the JSON only."""

READ_SYSTEM = """You answer questions about a research paper from the paper's text, which may be Markdown or LaTeX source. \
Answer each question in one or two sentences, with the exact value or expression. Write mathematics in plain words or simple notation. \
If the text does not say, answer "The paper does not say." \
Reply with a JSON list of strings, one answer per question, in the order of the questions. Reply with the JSON only."""

JUDGE_SYSTEM = """You grade answers to questions about a research paper against the expected answer. \
An answer is "right" when it states the same value, expression or reference as the expected answer (notation may differ), \
"partly" when it is right in part or right but imprecise where the expected answer is exact, and "wrong" otherwise, \
including "The paper does not say." \
Reply with a JSON list of strings ("right", "partly" or "wrong"), one per answer, in order. Reply with the JSON only."""


def parse(reply):
    return json.loads(re.search(r"\[.*\]", reply, re.S).group(0))


def forms(arxiv_id, md):
    texts = {"library": read_paper(md)[1]}
    for name, file in FORMS.items():
        if (OUT / arxiv_id / file).exists():  # pandoc fails on some sources
            texts[name] = (OUT / arxiv_id / file).read_text(encoding="utf-8", errors="replace")
    return texts


def library():
    return {str(read_paper(md)[0].get("arxiv") or ""): md for md in paper_files()}


def questions(papers):
    by_id = library()
    for line in Path(papers).read_text().splitlines()[1:]:
        arxiv_id = line.split("\t")[0]
        texts = forms(arxiv_id, by_id[arxiv_id])
        for setter in ("library", "tex"):
            reply, usage = ask_model(SETTER, SET_SYSTEM, texts[setter])
            for q in parse(reply):
                print(json.dumps({"arxiv": arxiv_id, "set_from": setter, **q, "usd": usage["usd"]}), flush=True)


def load(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def answer(question_file):
    by_id = library()
    by_paper = collections.defaultdict(list)
    for q in load(question_file):
        by_paper[q["arxiv"]].append(q)
    for arxiv_id, qs in by_paper.items():
        asked = "\n".join(f"{n}. {q['question']}" for n, q in enumerate(qs, 1))
        for form, text in forms(arxiv_id, by_id[arxiv_id]).items():
            reply, usage = ask_model(READER, READ_SYSTEM, f"{text}\n\n---\n\nQuestions:\n{asked}")
            print(json.dumps({"arxiv": arxiv_id, "form": form, "answers": parse(reply), "chars": len(text), **usage}),
                  flush=True)


def grade(question_file, answer_file):
    by_paper = collections.defaultdict(list)
    for q in load(question_file):
        by_paper[q["arxiv"]].append(q)
    rng = random.Random(20261013)
    for arxiv_id, qs in by_paper.items():
        items = [(a["form"], n, text) for a in load(answer_file) if a["arxiv"] == arxiv_id
                 for n, text in enumerate(a["answers"])]
        rng.shuffle(items)  # the judge sees the answers in no order of form
        prompt = "\n\n".join(f"Question: {qs[n]['question']}\nExpected: {qs[n]['answer']}\nAnswer: {text}"
                             for _, n, text in items)
        marks = parse(ask_model(JUDGE, JUDGE_SYSTEM, prompt)[0])
        for (form, n, text), mark in zip(items, marks, strict=True):
            print(json.dumps({"arxiv": arxiv_id, "form": form, "n": n, "set_from": qs[n]["set_from"],
                              "kind": qs[n]["kind"], "mark": mark, "answer": text}), flush=True)


def table(grade_file, answer_file):
    score = {"right": 1, "partly": 0.5, "wrong": 0}
    cells = collections.defaultdict(list)
    for g in load(grade_file):
        for key in (("all", g["form"]), ("set from " + g["set_from"], g["form"]), (g["kind"], g["form"])):
            cells[key].append(g["mark"])
    print("questions\tform\tn\tright\tpartly\twrong\tscore")
    for (group, form), marks in sorted(cells.items()):
        c = collections.Counter(marks)
        print(f"{group}\t{form}\t{len(marks)}\t{c['right']}\t{c['partly']}\t{c['wrong']}\t"
              f"{sum(score[m] for m in marks) / len(marks):.2f}")
    tokens = collections.defaultdict(list)
    for a in load(answer_file):
        tokens[a["form"]].append(a)
    print("\nform\tpapers\tinput tokens\tcharacters\tusd")
    for form, rows in sorted(tokens.items()):
        print(f"{form}\t{len(rows)}\t{sum(r['input'] for r in rows)}\t{sum(r['chars'] for r in rows)}\t"
              f"{sum(r['usd'] or 0 for r in rows):.2f}")


if __name__ == "__main__":
    {"questions": questions, "answer": answer, "grade": grade, "table": table}[sys.argv[1]](*sys.argv[2:])
