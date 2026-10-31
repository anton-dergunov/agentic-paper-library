"""Do agents use meaning search when the guide names it, and does it find more of the papers?

    PAPER_LIBRARY=<library> python3 agents.py setup <copy>     # the library without .git
    python3 agents.py run <copy> [--model haiku]              # both arms, every question
    python3 agents.py score                                   # results/agents.md

Five of the judged queries asked as a reader asks in a chat, each once with the library's
guide as it is (`without`) and once with the line on `paperlib meaning` (`with`), in a copy of
the library (`claude -p`, no Edit or Write, so the copy stays as it was). Records each run's
tool calls, answer, tokens and dollars in results/agents.jsonl, and scores which of the papers
the judge graded 2 for that query the answer names.
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

QUESTIONS = {
    "q01": "Which papers in my library study LLM judges that prefer answers written by their own model? List them, a line each.",
    "q10": "Which papers in the library are about models telling users what they want to hear rather than the truth? List them, a line each.",
    "q19": "What do I have on shrinking a prompt to save tokens without losing what matters? List the papers, a line each.",
    "q24": "Which papers in my library are about machine learning results that don't hold up when someone reruns them? List them, a line each.",
    "q31": "Do I have papers on whether people trust and follow advice from an algorithm? List them, a line each.",
}

LINE = ('- **Find papers by what they are about**: `paperlib meaning "<description>" [--in <topic>]` '
        "ranks the library's papers by meaning, across folders and wording, and `paperlib similar "
        "<paper>` lists a paper's nearest. Use them where grep would miss a paper that words it "
        "otherwise.\n")
ANCHOR = "- **Move papers only with `paperlib move"


def guide(copy):
    return Path(copy) / ".claude" / "library-guide.md"


def setup(copy):
    sys.path.insert(0, str(HERE.parent.parent / "scripts"))
    import paperlib
    copy = Path(copy)
    if copy.exists():
        sys.exit(f"{copy} exists")
    shutil.copytree(paperlib.LIBRARY_ROOT, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    text = guide(copy).read_text(encoding="utf-8")
    if ANCHOR not in text:
        sys.exit("the guide has changed: put the line where it belongs by hand")
    (copy / ".claude" / "guide-without.md").write_text(text, encoding="utf-8")
    (copy / ".claude" / "guide-with.md").write_text(text.replace(ANCHOR, LINE + ANCHOR, 1), encoding="utf-8")
    print(f"copied to {copy}")


def one(copy, arm, qid, model):
    shutil.copyfile(Path(copy) / ".claude" / f"guide-{arm}.md", guide(copy))
    start = time.time()
    done = subprocess.run(
        ["claude", "-p", "--model", model, "--output-format", "stream-json", "--verbose",
         "--allowedTools", "Bash,Read,Grep,Glob", "--disallowedTools", "Edit,Write,NotebookEdit,WebSearch,WebFetch",
         "--no-session-persistence", QUESTIONS[qid]],
        cwd=copy, capture_output=True, text=True, timeout=900)
    calls, answer, usd, tokens = [], "", None, {}
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append({"tool": block["name"], "input": block["input"]})
        if event.get("type") == "result":
            answer, usd, tokens = event.get("result", ""), event.get("total_cost_usd"), event.get("usage", {})
    row = {"arm": arm, "id": qid, "model": model, "seconds": round(time.time() - start),
           "usd": usd, "output_tokens": tokens.get("output_tokens"), "calls": calls, "answer": answer}
    # No private paths in the committed results: the copy's folder and the home folder.
    text = json.dumps(row, ensure_ascii=False)
    for path, name in ((str(Path(copy).resolve()), "<library>"), (str(Path(copy)), "<library>"), (str(Path.home()), "~")):
        text = text.replace(path, name)
    return json.loads(text)


def run(copy, model):
    RESULTS.mkdir(exist_ok=True)
    target = RESULTS / "agents.jsonl"
    done = set()
    if target.exists():
        done = {(r["arm"], r["id"]) for r in map(json.loads, open(target, encoding="utf-8"))}
    try:
        for qid in QUESTIONS:
            for arm in ("without", "with"):
                if (arm, qid) in done:
                    continue
                row = one(copy, arm, qid, model)
                with open(target, "a", encoding="utf-8") as log:
                    log.write(json.dumps(row, ensure_ascii=False) + "\n")
                used = sum("paperlib meaning" in str(c["input"]) or "paperlib similar" in str(c["input"]) for c in row["calls"])
                print(f"{qid} {arm:<7} {len(row['calls'])} calls, {used} meaning, ${row['usd'] or 0:.3f}, {row['seconds']} s", flush=True)
    finally:
        shutil.copyfile(Path(copy) / ".claude" / "guide-without.md", guide(copy))


def _norm(text):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def named(answer, title):
    """Whether the answer names the paper: its title, or its title before the colon (the
    library's file names turn a colon into ". ") when that is three words or more."""
    text = _norm(answer)
    head = re.split(r"\. |: ", title, maxsplit=1)[0]
    return _norm(title) in text or (len(head.split()) >= 3 and _norm(head) in text) or (
        len(head.split()) < 3 and re.search(rf"\b{re.escape(_norm(head))}\b", text) is not None and len(head) >= 4)


def score():
    grades = {}
    for row in map(json.loads, open(RESULTS / "judgements.jsonl", encoding="utf-8")):
        grades.setdefault(row["id"], {})[row["paper"].rsplit("/", 1)[-1]] = row["grade"]
    runs = [json.loads(line) for line in open(RESULTS / "agents.jsonl", encoding="utf-8")]
    out = ["# Agents with and without the guide's line on meaning search", "",
           "| Query | Arm | Tool calls | Meaning calls | Grade-2 papers named | Grade-1 named | $ | s |", "|---|---|--:|--:|--:|--:|--:|--:|"]
    totals = {}
    for row in sorted(runs, key=lambda r: (r["id"], r["arm"] != "without")):
        table = grades.get(row["id"], {})
        two = [t for t, g in table.items() if g == 2]
        got2 = sum(named(row["answer"], t) for t in two)
        got1 = sum(named(row["answer"], t) for t, g in table.items() if g == 1)
        used = sum("paperlib meaning" in str(c["input"]) or "paperlib similar" in str(c["input"]) for c in row["calls"])
        out.append(f"| {row['id']} | {row['arm']} | {len(row['calls'])} | {used} | {got2} of {len(two)} | {got1} | {row['usd'] or 0:.3f} | {row['seconds']} |")
        t = totals.setdefault(row["arm"], [0, 0, 0, 0.0, 0])
        t[0] += got2
        t[1] += len(two)
        t[2] += used > 0
        t[3] += row["usd"] or 0
        t[4] += 1
    out += ["", "| Arm | Grade-2 papers named | Runs that used meaning search | $ |", "|---|--:|--:|--:|"]
    for arm, (got, of, used, usd, n) in totals.items():
        out.append(f"| {arm} | {got} of {of} | {used} of {n} | {usd:.2f} |")
    (RESULTS / "agents.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["setup"] and len(args) == 2:
        setup(args[1])
    elif args[:1] == ["run"] and len(args) >= 2:
        run(args[1], args[args.index("--model") + 1] if "--model" in args else "haiku")
    elif args[:1] == ["score"]:
        score()
    else:
        sys.exit(__doc__)
