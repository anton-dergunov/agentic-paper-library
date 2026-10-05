"""Grade the answers to each question against the papers, blind to the condition.

    python3 judge.py <out-dir> <library> [--judge MODEL] [--only q1,q3] <answers-dir>[@<label>] ...

Answers are the files <session>.md that summarize.py writes; those of a directory given
with @<label> are named <session>@<label>, which is how the first run's answers join the
pool. The library should be a copy without reviews/ and notes/ (lib-nonotes): the judge
verifies against the paper markdown only, and the copy is read-only.

Two stages, so that every answer to a question is scored against the same list:

1. Pool (Opus, one session per question, able to read files and run shell commands):
   gets all the answers, pools the distinct points they make, and verifies each in the
   paper. Writes <out-dir>/pool-<question>.json.
2. Grade (one session per batch of up to five answers, in an order shuffled with a fixed
   seed and saved in <out-dir>/batches-<question>.json): which pooled points each answer
   makes, every wrong statement in it, and whether it tells the reader which points rest
   on a review or a note alone. Writes <out-dir>/grade-<question>-b<n>.json.

The grades of a question are merged into <out-dir>/judge-<question>.json. Every file that
exists is kept, so the command can be repeated until all are there; answers added later
go into new batches.

--judge names another model for stage 2 only, on the same pooled points; its files end
in -<model>.json. A Gemini model (Vertex AI; needs google-genai,
GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT) has no tools: its request carries
the markdown of every paper the pool or the batch's answers name, in place of the library.
"""
import concurrent.futures
import glob
import json
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = 5
RULES = """Do not use reviews/ or notes/ as evidence: verify against the paper markdown under library/ (grep for the number or phrase; headings carry the page as "(p. N)")."""

POOL = """%d assistants answered the same question from this paper library. Build the list of points their answers will be graded against. """ + RULES + """

Question: %s

Steps:
1. Pool the distinct substantive points the answers make (a finding, a mechanism, a number with its baseline). Merge duplicates. Keep at most 30, the ones that matter most for the question; prefer points that several answers make, and keep the important ones that only one makes.
2. Verify every pooled point in the paper it is attributed to. Mark it "holds", "wrong" (say what the paper says and where) or "unverifiable" (no paper named, or the paper is not in the library).

Reply with JSON only:
{"points": [{"id": 1, "point": "...", "paper": "<path of the paper's markdown under library/>", "verdict": "holds|wrong|unverifiable", "evidence": "..."}]}
"""

GRADE = """%d assistants answered the same question from this paper library. Grade the answers against the papers. %s

Question: %s

The points the answers are graded against, already checked in the papers:

%s

Per answer:
1. "makes": the ids of the points above that the answer states. A point counts when the answer says the same thing, in any words; it does not count when the answer only names the paper or the topic.
2. "errors": every statement in the answer that is wrong, whether or not it is one of the points: wrong numbers, wrong attributions, wrong pages (a page off by one section is wrong; a section's range is fine), a wrong reading of what a result means, a claim about what the library has or lacks that is false. Verify each in the paper before listing it; quote the answer and say what the paper says and where. Do not list omissions, or statements you could not check.
3. "papers_cited": how many distinct library papers it cites.
4. "review_only": "no", or a quote where the answer tells the reader that a point rests on a review or a note and was not checked in the paper.
5. "misleading": "no", or how it would mislead a reader on the main question.

Reply with JSON only:
{"answers": {"A": {"makes": [1, 2], "errors": [{"quote": "...", "paper_says": "..."}], "papers_cited": 0, "review_only": "no|<quote>", "misleading": "no|<how>", "comment": "..."}, "B": {}}}
"""


class Failed(Exception):
    pass


def claude(model, prompt, library):
    done = subprocess.run(
        ["claude", "-p", "--model", model, "--output-format", "json",
         "--allowedTools", "Read", "Bash", "--disallowedTools", "Write", "Edit", "Agent",
         "WebSearch", "WebFetch", "NotebookEdit", "Skill", "--strict-mcp-config",
         "--no-session-persistence"],
        input=prompt, capture_output=True, text=True, cwd=library)
    try:
        reply = json.loads(done.stdout)
    except ValueError:
        raise Failed(done.stdout[:300] or done.stderr[:300])
    if reply.get("is_error") or reply.get("subtype") != "success":
        raise Failed(str(reply.get("result"))[:300])
    return reply["result"], {"usd": reply.get("total_cost_usd"), "seconds": round(reply.get("duration_ms", 0) / 1000)}


def gemini(model, prompt):
    from google import genai
    client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"], location="global")
    reply = client.models.generate_content(model=model, contents=prompt)
    usage = reply.usage_metadata
    return reply.text, {"input": usage.prompt_token_count,
                        "output": (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)}


def parse(text):
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def collect(specs, key):
    """{answer name: text} for one question, over the answers directories."""
    answers = {}
    for spec in specs:
        folder, _, label = spec.partition("@")
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            name = os.path.basename(path)[:-3]
            if re.search(r"-%s(-r\d+)?$" % key, name):
                answers[name + ("@" + label if label else "")] = open(path).read()
    return answers


def lettered(names, answers):
    return "".join("\n\n===== ANSWER %s =====\n\n%s" % (chr(65 + i), answers[name]) for i, name in enumerate(names))


def pool(key, question, answers, library, out):
    target = os.path.join(out, "pool-%s.json" % key)
    if os.path.exists(target):
        return json.load(open(target))
    names = sorted(answers)
    random.Random(key).shuffle(names)
    text, cost = claude("claude-opus-5-5", POOL % (len(names), question) + lettered(names, answers), library)
    pooled = parse(text)
    pooled.update(answers=names, cost=cost)
    json.dump(pooled, open(target, "w"), indent=1, ensure_ascii=False)
    print(key, "pooled", len(pooled["points"]), "points from", len(names), "answers", flush=True)
    return pooled


def batches(key, answers, out):
    """The saved batches, with new ones for answers not yet in any."""
    target = os.path.join(out, "batches-%s.json" % key)
    saved = json.load(open(target)) if os.path.exists(target) else []
    new = sorted(set(answers) - {name for batch in saved for name in batch})
    if new:
        random.Random("%s %d" % (key, len(saved))).shuffle(new)
        count = -(-len(new) // BATCH)
        saved += [new[i::count] for i in range(count)]
        json.dump(saved, open(target, "w"), indent=1)
    return saved


def papers_for(points, texts, library):
    """The markdown of the papers a Gemini judge needs: the pool's, and those the answers name."""
    wanted = {point.get("paper") for point in points}
    joined = "\n".join(texts)
    chosen = []
    for path in sorted(glob.glob(os.path.join(library, "library", "**", "*.md"), recursive=True)):
        relative, stem = os.path.relpath(path, library), os.path.basename(path)[:-3]
        if stem != "README" and (relative in wanted or stem[:40] in joined):
            chosen.append("\n\n===== PAPER %s =====\n\n%s" % (relative, open(path).read()))
    return "".join(chosen), len(chosen)


def grade(key, question, number, names, answers, pooled, library, out, judge):
    suffix = "" if judge == "claude-opus-5-5" else "-" + judge
    target = os.path.join(out, "grade-%s-b%d%s.json" % (key, number, suffix))
    if os.path.exists(target):
        return json.load(open(target))
    points = "\n".join("%d. %s [%s; %s]" % (p["id"], p["point"], p.get("paper"), p["verdict"]) for p in pooled["points"])
    if judge.startswith("gemini"):
        papers, count = papers_for(pooled["points"], [answers[name] for name in names], library)
        rules = "Verify against the %d papers given in full after the answers, and nothing else." % count
        text, cost = gemini(judge, GRADE % (len(names), rules, question, points) + lettered(names, answers) + papers)
    else:
        text, cost = claude(judge, GRADE % (len(names), RULES, question, points) + lettered(names, answers), library)
    graded = parse(text)
    graded = {"answers": {name: graded["answers"][chr(65 + i)] for i, name in enumerate(names)}, "cost": cost}
    json.dump(graded, open(target, "w"), indent=1, ensure_ascii=False)
    print(key, "batch", number, judge, {name: (len(a["makes"]), len(a["errors"])) for name, a in graded["answers"].items()}, flush=True)
    return graded


def option(args, name, default=None):
    if name not in args:
        return default
    value = args.pop(args.index(name) + 1)
    args.remove(name)
    return value


def main():
    args = sys.argv[1:]
    judge = option(args, "--judge", "claude-opus-5-5")
    only = option(args, "--only")
    out, library, specs = args[0], os.path.abspath(args[1]), args[2:]
    os.makedirs(out, exist_ok=True)
    questions = [line.rstrip("\n").split("\t") for line in open(os.path.join(HERE, "questions.txt"))]
    questions = [(key, q) for key, q in questions if not only or key in only.split(",")]
    answers = {key: collect(specs, key) for key, _ in questions}
    failed = 0
    with concurrent.futures.ThreadPoolExecutor(6) as workers:
        pools = {key: workers.submit(pool, key, q, answers[key], library, out) for key, q in questions}
        jobs = {}
        for key, question in questions:
            try:
                pooled = pools[key].result()
            except Exception as error:
                failed += 1
                print(key, "pool FAILED", str(error)[:300], flush=True)
                continue
            for number, names in enumerate(batches(key, answers[key], out), 1):
                jobs[key, number] = workers.submit(grade, key, question, number, names, answers[key], pooled, library, out, judge)
        merged = {key: {} for key, _ in questions}
        for (key, number), job in jobs.items():
            try:
                graded = job.result()["answers"]
                if merged[key] is not None:
                    merged[key].update(graded)
            except Exception as error:
                failed += 1
                merged[key] = None
                print(key, "batch", number, "FAILED", str(error)[:300], flush=True)
    suffix = "" if judge == "claude-opus-5-5" else "-" + judge
    for key, graded in merged.items():
        if graded and key in pools and not pools[key].exception():
            json.dump({"judge": judge, "points": pools[key].result()["points"], "answers": graded},
                      open(os.path.join(out, "judge-%s%s.json" % (key, suffix)), "w"), indent=1, ensure_ascii=False)
    if failed:
        sys.exit("%d unit(s) failed; run the same command again to resume" % failed)


if __name__ == "__main__":
    main()
