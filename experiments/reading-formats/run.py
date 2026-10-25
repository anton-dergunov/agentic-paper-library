#!/usr/bin/env python3
"""Ask the test set's questions in each condition, one `claude -p` request per question.

    PAPER_LIBRARY=<library> uv run python run.py status
    PAPER_LIBRARY=<library> uv run python run.py <tier>... [--budget USD] [--stop-at 0.8]

Tiers, in priority order (see PROGRESS.md):
  A  E0 extras on DPO, and E1 on DPO in all five conditions (the pilot)
  B  E1 on SimPO, GPT-1, Lost in the Middle, InstructGPT in c0, pdf, txt, md; E4
  B2 E1 in c0, pdf, txt, md on four papers published after the model's training cutoff; E4 in txt
  C  E5 (E1 in html beyond DPO was dropped at checkpoint 1)
  C2 E5 on the unseen papers, with txt; E6, equation structure, in pdf, txt, md
  D  E3 across papers: Claude Code sessions in the library, PDF and text-layer copies
     (copies.py builds them), and the papers' PDFs attached to one request

A tier runs group by group (a paper, for E1). The conditions of a group run in parallel,
each asking its questions one after another so that the document is read from the cache
after the first. When a group is done its questions are judged (judge.py), and every
question whose answers differ between conditions (closed book aside) is asked twice more in
each condition while the cache is warm, and judged again.

Each request is results/runs/<exp>/<condition>/<qid>-r<n>.json, written when it succeeds;
one that exists is not asked again, so the command can be stopped and repeated. It stops
by itself, after the requests in flight, when the five-hour window's utilisation reaches
--stop-at, the subscription refuses a request, or --budget dollars have been spent by this
invocation. Raw event streams go to the cache, not to results/.
"""

import base64
import concurrent.futures
import json
import os
import re
import shutil
import tempfile
import subprocess
import sys
import threading
import time
from pathlib import Path

import inputs

HERE = Path(__file__).resolve().parent
RUNS = HERE / "results" / "runs"
STREAMS = inputs.OUT / "streams"
EMPTY = inputs.OUT / "empty"  # one working directory for every request, so the prompt prefix stays the same
MODEL = "claude-opus-5-5"
SYSTEM_DOC = ("Answer the question using only the document provided. Give the page number for every fact you use. "
              "If the document does not contain the answer, say so.")
SYSTEM_C0 = "Answer the question from what you know. If you do not know, say so."
Q = {q["id"]: q for q in inputs.QUESTIONS}
# Tier D's agent sessions: the copy each runs in, the tools it has, what the prompt adds.
AGENT_COPIES = {"x-lib": "lib", "x-pdf": "pdf", "x-txt": "txt"}
AGENT_TOOLS = "Read,Grep,Glob,Bash"
AGENT_SUFFIX = "\n\nAnswer from the papers in this folder. Give the page number for every fact you use."
AGENT_BUDGET = "5"
SHARED_TMP = "/private/tmp"  # /tmp on macOS
PDF_TOOLS = r"(?i)pdftotext|pdfinfo|pdfimages|pdftoppm|fitz|pymupdf|pypdf|pdfplumber|qpdf"  # dollars a session may spend before Claude Code stops it
CLI_VERSION = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()


class Stop(Exception):
    pass


class Guard:
    """Stops the run on a usage limit, a utilisation threshold or the budget."""

    def __init__(self, budget, stop_at):
        self.budget, self.stop_at, self.spent, self.reason = budget, stop_at, 0.0, None
        self.utilisation = None
        self.lock = threading.Lock()

    def check(self):
        if self.reason:
            raise Stop(self.reason)

    def record(self, usd, rate):
        with self.lock:
            self.spent += usd or 0
            five = ((rate or {}).get("unifiedWindows") or {}).get("five_hour") or {}
            if five.get("utilization") is not None:
                self.utilisation = five["utilization"]
            if rate and rate.get("status") not in (None, "allowed", "allowed_warning"):
                self.reason = "the subscription refused: %s" % rate.get("status")
            elif self.utilisation is not None and self.utilisation >= self.stop_at:
                self.reason = "five-hour utilisation %.0f%% reached --stop-at %.0f%%" % (
                    100 * self.utilisation, 100 * self.stop_at)
            elif self.budget is not None and self.spent >= self.budget:
                self.reason = "budget $%.2f spent" % self.spent


GUARD = Guard(None, 0.8)


def request(system, content, model=MODEL, stream_path=None):
    """One request with `content` (a list of message blocks) and no tools.

    Returns (result event, rate-limit info). Raises Stop on a usage limit.
    """
    GUARD.check()
    env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
    message = {"type": "user", "message": {"role": "user", "content": content}}
    EMPTY.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(
        ["claude", "-p", "--model", model, "--input-format", "stream-json", "--output-format", "stream-json",
         "--verbose", "--tools", "", "--max-turns", "1", "--system-prompt", system, "--no-session-persistence"],
        input=json.dumps(message) + "\n", capture_output=True, text=True, cwd=EMPTY, env=env, timeout=1800)
    if stream_path:
        stream_path.parent.mkdir(parents=True, exist_ok=True)
        stream_path.write_text(done.stdout)
    result, rate = None, None
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            result = event
        elif event.get("type") == "rate_limit_event":
            rate = event.get("rate_limit_info")
    GUARD.record((result or {}).get("total_cost_usd"), rate)
    text = str((result or {}).get("result") or done.stderr or done.stdout)[-500:]
    if result is None or result.get("is_error"):
        lowered = text.lower()
        if "too long" in lowered or "context" in lowered and "exceed" in lowered:
            return {"too_long": True, "result": text, "usage": (result or {}).get("usage", {}),
                    "total_cost_usd": (result or {}).get("total_cost_usd")}, rate
        if any(word in lowered for word in ("limit", "429", "overloaded", "credit")):
            GUARD.reason = GUARD.reason or "usage limit: " + text[:200]
            raise Stop(GUARD.reason)
        raise RuntimeError(text[:300])
    return result, rate


# ---- conditions -------------------------------------------------------------------------

def _b64(path):
    return base64.standard_b64encode(Path(path).read_bytes()).decode()


def document(path):
    return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": _b64(path)}}


def image(path):
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _b64(path)}}


def text(path):
    return {"type": "text", "text": Path(path).read_text(encoding="utf-8")}


def blocks(form, paper, page=None):
    """The message blocks that carry the paper in a form, or None when it has none."""
    if form in ("c0", "empty"):
        return []
    if form == "pdf":
        return [document(inputs.pdf(paper))]
    if form == "pdfs":  # several papers, one request (E3's X-ATT)
        return [document(inputs.pdf(p)) for p in paper]
    if form == "page":
        return [document(inputs.page_pdf(paper, page))]
    if form.startswith("img"):
        return [image(inputs.page_png(paper, page, int(form[3:])))]
    path = {"txt": inputs.txt, "html": inputs.html, "md": inputs.md, "md-old": inputs.md_old,
            "md-noanchors": inputs.md_noanchors}[form](paper)
    return [text(path)] if path else None


def job(exp, cond, qid, rep=1, form=None, question=None, paper=None, page=None):
    q = Q.get(qid, {})
    return {"exp": exp, "cond": cond, "qid": qid, "rep": rep, "form": form or cond,
            "question": question or q["question"], "paper": paper or q.get("paper") or q.get("papers"),
            "page": page or q.get("page"), "system": SYSTEM_C0 if cond == "c0" else SYSTEM_DOC}


def path_of(j):
    return RUNS / j["exp"] / j["cond"] / ("%s-r%d.json" % (j["qid"], j["rep"]))


def ask(j):
    """Run one job unless its result exists. Returns the record, or None if skipped."""
    target = path_of(j)
    if target.exists():
        return None
    if j["form"] in AGENT_COPIES:
        return ask_agent(j, target)
    content = blocks(j["form"], j["paper"], j["page"])
    if content is None:
        return None
    if content:
        # Claude Code caches up to the end of the message, question included; a breakpoint
        # after the document lets the next question on the paper read it from the cache.
        content[-1]["cache_control"] = {"type": "ephemeral", "ttl": "1h"}
    started = time.time()
    stream = STREAMS / j["exp"] / j["cond"] / ("%s-r%d.jsonl" % (j["qid"], j["rep"]))
    result, rate = request(j["system"], content + [{"type": "text", "text": j["question"]}], stream_path=stream)
    usage = result.get("usage") or {}
    record = {
        "exp": j["exp"], "cond": j["cond"], "qid": j["qid"], "rep": j["rep"], "paper": j["paper"],
        "form": j["form"], "page": j["page"], "status": "too_long" if result.get("too_long") else "ok",
        "answer": result.get("result"),
        "input": sum(usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "cache_write": usage.get("cache_creation_input_tokens"), "cache_read": usage.get("cache_read_input_tokens"),
        "output": usage.get("output_tokens"), "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
        "usd": result.get("total_cost_usd"), "seconds": round(time.time() - started, 1),
        "model": MODEL, "cli": CLI_VERSION,
        "five_hour": (((rate or {}).get("unifiedWindows") or {}).get("five_hour") or {}).get("utilization"),
        "date": time.strftime("%Y-%m-%d %H:%M"),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=1))
    tmp.rename(target)
    print("  %-3s %-12s %-5s r%d  %6d in  %5d out  $%.3f  %s  [window %s]" % (
        j["exp"], j["cond"], j["qid"], j["rep"], record["input"], record["output"] or 0, record["usd"] or 0,
        record["status"], "%.0f%%" % (100 * record["five_hour"]) if record["five_hour"] is not None else "?"),
        flush=True)
    return record


def agent_request(cwd, prompt, stream_path):
    """One Claude Code session in `cwd` that may read files and run shell commands but not
    edit, search the web or start subagents. It loads the copy's CLAUDE.md (`--restricted`
    would not) and no user settings (hooks, plugins); the copies are read-only, and a call
    that reaches outside the copy is recorded, not prevented. Returns (result event, rate-limit info, the
    session's tool calls as short strings). Raises Stop on a usage limit."""
    GUARD.check()
    # Its own temporary folder, and afterwards whatever it made in /tmp under a name its calls
    # use, removed: a later session must not find another's converted papers.
    scratch = tempfile.mkdtemp(prefix="reading-formats-agent-")
    before = set(os.listdir(SHARED_TMP))
    env = {**os.environ, "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "TMPDIR": scratch}
    done = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL, "--output-format", "stream-json", "--verbose",
         "--tools", AGENT_TOOLS, "--allowedTools", AGENT_TOOLS, "--setting-sources", "project,local",
         "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", AGENT_BUDGET],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=cwd, env=env, timeout=3600)
    stream_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path.write_text(done.stdout)
    result, rate, calls = None, None, []
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            result = event
        elif event.get("type") == "rate_limit_event":
            rate = event.get("rate_limit_info")
        elif event.get("type") == "assistant":
            for part in event["message"].get("content", []):
                if part.get("type") == "tool_use":
                    given = part.get("input") or {}
                    detail = given.get("file_path") or given.get("command") or given.get("pattern") or ""
                    ranged = " [%s+%s]" % (given.get("offset"), given.get("limit")) if "offset" in given or "limit" in given else ""
                    calls.append("%s %s%s" % (part.get("name"), str(detail)[:300], ranged))
    shutil.rmtree(scratch, ignore_errors=True)
    for name in set(os.listdir(SHARED_TMP)) - before:
        if any("/tmp/" + name in call for call in calls):
            target = os.path.join(SHARED_TMP, name)
            shutil.rmtree(target, ignore_errors=True) if os.path.isdir(target) else os.remove(target)
            print("  removed %s, which the session wrote" % target, flush=True)
    GUARD.record((result or {}).get("total_cost_usd"), rate)
    text = str((result or {}).get("result") or done.stderr or done.stdout)[-500:]
    if result is None or (result.get("is_error") and result.get("subtype") != "error_max_budget_usd"):
        if any(word in text.lower() for word in ("limit", "429", "overloaded", "credit")):
            GUARD.reason = GUARD.reason or "usage limit: " + text[:200]
            raise Stop(GUARD.reason)
        raise RuntimeError(text[:300])
    return result, rate, calls


def ask_agent(j, target):
    copy = inputs.OUT / "copies" / ("lib-asis" if AGENT_COPIES[j["form"]] == "lib" else AGENT_COPIES[j["form"]])
    if not copy.exists():
        raise RuntimeError("no copy at %s: run copies.py first" % copy)
    started = time.time()
    stream = STREAMS / j["exp"] / j["cond"] / ("%s-r%d.jsonl" % (j["qid"], j["rep"]))
    result, rate, calls = agent_request(copy, j["question"] + AGENT_SUFFIX, stream)
    usage = result.get("usage") or {}
    record = {
        "exp": j["exp"], "cond": j["cond"], "qid": j["qid"], "rep": j["rep"], "paper": j["paper"],
        "form": j["form"], "page": None,
        "status": "over_budget" if result.get("subtype") == "error_max_budget_usd" else "ok",
        "answer": result.get("result"),
        "input": sum(usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "cache_write": usage.get("cache_creation_input_tokens"), "cache_read": usage.get("cache_read_input_tokens"),
        "output": usage.get("output_tokens"), "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
        "usd": result.get("total_cost_usd"), "seconds": round(time.time() - started, 1),
        "turns": result.get("num_turns"), "calls": calls,
        "opened_pdf": any(c.startswith("Read ") and ".pdf" in c or c.startswith("Bash ") and re.search(PDF_TOOLS, c)
                          for c in calls),
        "outside": [c for c in calls if any(mark in c for mark in ("~/", "/Users/", "../", "/private/", "/tmp"))
                    and str(copy) not in c],
        "model": MODEL, "cli": CLI_VERSION,
        "five_hour": (((rate or {}).get("unifiedWindows") or {}).get("five_hour") or {}).get("utilization"),
        "date": time.strftime("%Y-%m-%d %H:%M"),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=1))
    tmp.rename(target)
    print("  %-3s %-12s %-5s r%d  %3s turns %3d calls  %7d in  $%.3f  %s%s  [window %s]" % (
        j["exp"], j["cond"], j["qid"], j["rep"], record["turns"], len(calls), record["input"], record["usd"] or 0,
        record["status"], "  OUTSIDE" if record["outside"] else "",
        "%.0f%%" % (100 * record["five_hour"]) if record["five_hour"] is not None else "?"), flush=True)
    return record


# ---- tiers --------------------------------------------------------------------------------

E1_ALL = ("c0", "pdf", "txt", "html", "md")
E1_CORE = ("c0", "pdf", "txt", "md")
UNSEEN = ("pair", "sftrl", "kvxfer", "genrec")  # tier B2: published after June 2026
E4_PAPERS = ("musique", "toolformer", "gpt1", "qwen3vl")


def qids(exp, paper):
    return [q["id"] for q in inputs.QUESTIONS if q["exp"] == exp and q.get("paper") == paper]


def e0_jobs():
    title = "What is the title of this paper? Reply with the title only."
    return [job("E0", "empty", "ok", form="empty", paper="dpo", question="Reply with the single word: ok"),
            job("E0", "md-noanchors", "D1"),
            job("E0", "page1", "title", form="page", paper="dpo", page=1, question=title),
            job("E0", "page1", "title", rep=2, form="page", paper="dpo", page=1, question=title),
            job("E0", "page2", "title", form="page", paper="dpo", page=2, question=title),
            job("E0", "page9", "D2", form="page"),
            job("E0", "img1255", "D2", form="img1255"),
            job("E0", "img2576", "D2", form="img2576")]


def groups(tier):
    """[(name, {condition: [jobs]}, rerun conditions)] of a tier, in order."""
    out = []
    e1 = lambda paper: ("E1 " + paper, {c: [job("E1", c, i) for i in qids("E1", paper)] for c in E1_CORE},
                        E1_CORE[1:])
    if tier == "A":
        out.append(("E0 dpo", {"e0": e0_jobs()}, ()))
        out.append(("E1 dpo", {c: [job("E1", c, i) for i in qids("E1", "dpo")] for c in E1_ALL}, E1_ALL[1:]))
    elif tier == "B":
        # The pilot found DPO answered from memory; the less famous SimPO and the E4 fixes
        # tell the most per dollar, InstructGPT (200K-token PDF) the least.
        out.append(e1("simpo"))
        for paper in E4_PAPERS:
            conds = ("md-old", "md", "pdf")
            out.append(("E4 " + paper, {c: [job("E4", c, i) for i in qids("E4", paper)] for c in conds}, conds))
        out += [e1(paper) for paper in ("gpt1", "litm", "instructgpt")]
    elif tier == "B2":
        out += [e1(paper) for paper in UNSEEN]
        # Does the naive text layer carry the errors the converter had? The other conditions
        # were asked in tier B; they count in the disagreements, and are not asked again.
        for paper in E4_PAPERS:
            out.append(("E4 txt " + paper, {"txt": [job("E4", "txt", i) for i in qids("E4", paper)]},
                        ("md-old", "md", "pdf", "txt")))
    elif tier == "C":
        conds = ("page", "img1255", "img2576", "md")
        for paper in ("qwen3vl", "litm"):
            out.append(("E5 " + paper, {c: [job("E5", c, i, form=c) for i in qids("E5", paper)] for c in conds}, conds))
    elif tier == "C2":
        # A paper's E5 and E6 groups run one after the other, so that E6 reads the whole
        # paper's txt and md from the cache E5 wrote.
        small = ("page", "img1255", "img2576", "md", "txt")
        for paper in UNSEEN:
            if qids("E5", paper):
                out.append(("E5 " + paper, {c: [job("E5", c, i, form=c) for i in qids("E5", paper)] for c in small},
                            small))
            if qids("E6", paper):
                out.append(("E6 " + paper, {c: [job("E6", c, i) for i in qids("E6", paper)] for c in ("pdf", "txt", "md")},
                            ("pdf", "txt", "md")))
    elif tier == "D":
        # One group: every condition's six questions run in parallel across conditions, in
        # turn within one, so that a condition's later sessions find its copy's files in the
        # operating system's cache. X-ATT asks only the questions with named papers.
        across = [q["id"] for q in inputs.QUESTIONS if q["exp"] == "E3"]
        conditions = {c: [job("E3", c, i) for i in across] for c in AGENT_COPIES}
        conditions["x-att"] = [job("E3", "x-att", i, form="pdfs") for i in across if Q[i]["papers"]]
        out.append(("E3 across papers", conditions, tuple(conditions)))
    return out


def run_group(conditions):
    """Each condition's jobs in order, the conditions in parallel. Stop propagates."""
    def worker(jobs):
        for j in jobs:
            try:
                ask(j)
            except RuntimeError as error:
                print("  FAILED %s %s %s: %s" % (j["exp"], j["cond"], j["qid"], error), flush=True)
    with concurrent.futures.ThreadPoolExecutor(len(conditions)) as pool:
        for future in [pool.submit(worker, jobs) for jobs in conditions.values()]:
            try:
                future.result()
            except Stop:
                pass
    GUARD.check()


def disagreements(qid_list, rerun_conds, exp):
    """Questions whose first answers score differently across the rerun conditions."""
    import judge
    out = []
    for qid in qid_list:
        grades = judge.grades(qid)
        scores = {grades.get("%s/%s/%s-r1" % (exp, c, qid), {}).get("score") for c in rerun_conds}
        scores.discard(None)
        if len(scores) > 1:
            out.append(qid)
    return out


def run_tier(tier):
    import judge
    for name, conditions, rerun_conds in groups(tier):
        print("%s" % name, flush=True)
        run_group(conditions)
        exp = name.split()[0]
        asked = sorted({j["qid"] for jobs in conditions.values() for j in jobs if j["qid"] in Q})
        judge.judge(asked)
        if not rerun_conds:
            continue
        differ = disagreements(asked, rerun_conds, exp)
        if differ:
            print("  rerunning where conditions disagree: %s" % ", ".join(differ), flush=True)
            reruns = {c: [dict(j, rep=r) for j in conditions[c] if j["qid"] in differ for r in (2, 3)]
                      for c in rerun_conds if c in conditions}
            run_group(reruns)
            judge.judge(differ)


def status():
    for tier in ("A", "B", "B2", "C", "C2", "D"):
        done = total = 0
        for name, conditions, _ in groups(tier):
            for jobs in conditions.values():
                for j in jobs:
                    if not (j["form"] == "html" and inputs.html(j["paper"]) is None):
                        total += 1
                        done += path_of(j).exists()
        print("tier %s: %d of %d first answers" % (tier, done, total))
    reruns = len(list(RUNS.glob("*/*/*-r[23].json")))
    spent = sum(json.loads(p.read_text()).get("usd") or 0 for p in RUNS.glob("*/*/*.json"))
    print("reruns: %d; requests so far $%.2f" % (reruns, spent))


def main():
    args = sys.argv[1:]
    if not args or args[0] == "status":
        return status()
    budget = float(args.pop(args.index("--budget") + 1)) if "--budget" in args else None
    if "--budget" in args:
        args.remove("--budget")
    stop_at = 0.8
    if "--stop-at" in args:
        stop_at = float(args.pop(args.index("--stop-at") + 1))
        args.remove("--stop-at")
    GUARD.budget, GUARD.stop_at = budget, stop_at
    try:
        for tier in args:
            run_tier(tier)
    except Stop as stop:
        sys.exit("stopped: %s (spent $%.2f this run). Run the same command again to resume." % (stop, GUARD.spent))
    print("done: spent $%.2f this run; window %s" % (
        GUARD.spent, "%.0f%%" % (100 * GUARD.utilisation) if GUARD.utilisation is not None else "?"))


if __name__ == "__main__":
    main()
