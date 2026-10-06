#!/usr/bin/env python3
"""Read papers and write their notes, one model request per paper.

    ./scripts/read-papers.py <scope or paper.md> ... [--limit N] [--jobs N] [--model ID]
                             [--focus FILE] [--stale] [--skims] [--redo] [--appendix]
    ./scripts/read-papers.py <scope or paper.md> ... --stamp

For every paper named, or under a scope (a folder of the library), that has no digest in
notes/<stem>.md yet, sends the paper's reading view (paperlib read-view) with the prompt
in guide/reading-prompt.md to a model through `claude -p`, with no tools, and writes the
reply as the note. Each paper is its own request, so nothing read earlier is paid for
again, and a run that is stopped loses only the papers in progress: run it again and it
continues. An existing note's Q&A is kept.

A note records the text it was written from (`paper-hash:`, a fingerprint of the paper's
body). When the paper is reconverted or fixed by hand, the note is stale.

    --limit N     read at most N papers in this run (to spend a known budget)
    --jobs N      requests at a time (default 4)
    --model ID    the reading model (default: `reader_model` in paper-library.yaml, else
                  opus; experiments/reading-models compares the candidates)
    --focus FILE  a few lines on what the area's review will ask, put before the paper
    --stale       also read again the papers changed since their note was written
    --skims       also read again the papers whose note says `read: skim`
    --redo        read again every paper named, whatever its note says
    --appendix    give the reader the appendices too (for papers whose note says the
                  main results are in them); use with --redo on those papers
    --stamp       read nothing: record each paper's current text in its note, for notes
                  written before notes recorded it (they are never reported stale)

Prints a line per paper with its tokens and any conversion problem the reader reported
(`minor: …` or `damaged: …`), and appends the same to <cache>/read-papers.jsonl.

A request refused for a moment (rate limit, service busy) is retried after a pause. When
the account's usage window is used up, no further requests are sent, the message with its
reset time is printed, and the exit code is 3: the notes written are kept, and the same
command continues, after the reset or on another account.
"""

import json
import re
import sys
import threading
import time
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from pathlib import Path

from paperlib import (
    CACHE_DIR, CONFIG, ENGINE_ROOT, LIBRARY_DIR, NOTE_HASH, NOTES_DIR, ask_model, note_conversion,
    note_is_stale, note_path, paper_files, paper_hash, read_paper, read_view, stamp_note,
)

SYSTEM = "You read research papers carefully and write precise notes on them."
RELATED_MAX = 150


def note_state(stem):
    """(depth, Q&A text) of a paper's note: depth is "full", "skim" or None for no digest."""
    note = NOTES_DIR / f"{stem}.md"
    if not note.exists():
        return None, ""
    text = note.read_text(encoding="utf-8")
    qa = re.search(r"^## Q&A[ \t]*\n(.*)\Z", text, re.M | re.S)
    depth = re.search(r"^read:\s*(\w+)", text, re.M)
    has_digest = "## Digest" in text
    return (depth.group(1) if depth else "full") if has_digest else None, (qa.group(1).strip() if qa else "")


def related_list(paper, scope_dir):
    """The other papers of the area, one line each, for the note's "Related in library"."""
    lines = []
    for other in paper_files(scope_dir):
        if other == paper:
            continue
        summary = " ".join(str(read_paper(other)[0].get("summary") or "").split())
        lines.append(f"- {other.stem}: {summary}")
    if len(lines) > RELATED_MAX:
        # A large area: keep the paper's own folder, which holds its nearest neighbours.
        own = [f"- {o.stem}: " + " ".join(str(read_paper(o)[0].get('summary') or '').split())
               for o in paper_files(paper.parent) if o != paper]
        lines = own[:RELATED_MAX]
    return "\n".join(lines) or "(none)"


class UsageLimit(RuntimeError):
    """The account's usage window is used up: nothing more can be read until it resets."""


# What `claude -p` says when the usage window is used up ("You've hit your session limit ·
# resets 1:10am"), and when a request was refused for a moment (too many at once, the
# service busy). The first stops the run; the second is retried after a pause.
WINDOW_LIMIT = re.compile(r"(session|usage|weekly|daily|monthly) limit|resets? (at )?\d|quota|credit balance", re.I)
TRANSIENT = re.compile(r"rate.?limit|too many requests|\b429\b|overloaded|\b529\b|\b50[234]\b|timed? ?out", re.I)
RETRY_PAUSES = [30, 60, 120]  # seconds before each retry of a transient refusal
stop = threading.Event()  # set at a usage limit: requests not yet sent are not sent


def ask(model, prompt):
    """ask_model, with transient refusals retried and a usage limit raised as UsageLimit."""
    for pause in RETRY_PAUSES + [None]:
        if stop.is_set():
            raise UsageLimit("stopped: the usage limit was reached")
        try:
            return ask_model(model, SYSTEM, prompt)
        except RuntimeError as error:
            if WINDOW_LIMIT.search(str(error)):
                stop.set()
                raise UsageLimit(str(error)) from None
            if pause is None or not TRANSIENT.search(str(error)):
                raise
            time.sleep(pause)


def read_one(paper, scope_dir, model, focus, template, appendix):
    if stop.is_set():
        raise UsageLimit("not started: the usage limit was reached")
    meta, body = read_paper(paper)
    prompt = (template.replace("{{focus}}", focus)
              .replace("{{related}}", related_list(paper, scope_dir))
              + read_view(meta, body, appendix=appendix))
    start = time.time()
    try:
        note, usage = ask(model, prompt)
    except RuntimeError:
        # A request in flight when the limit was reached fails with an empty or odd message.
        if stop.is_set():
            raise UsageLimit("stopped: the usage limit was reached") from None
        raise
    note = note.strip()
    if note.startswith("```"):
        note = note.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if "## Digest" not in note or not note.startswith("# "):
        raise RuntimeError("the reply is not a note: " + note[:120].replace("\n", " "))
    if "## Related in library" not in note:
        note += "\n\n## Related in library\n"
    _, qa = note_state(paper.stem)
    note = stamp_note(note.rstrip(), paper_hash(paper)) + "\n\n## Q&A\n" + (f"\n{qa}\n" if qa else "")
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    note_path(paper).write_text(note, encoding="utf-8")
    grade, problem = note_conversion(note)
    usage.update(paper=paper.stem, model=model, seconds=round(time.time() - start),
                 conversion=f"{grade}: {problem}" if problem else (grade or "?"))
    return usage


def stamp(papers):
    """Record the current text of each paper in its note, without reading it again."""
    stamped = 0
    for paper, _ in papers:
        note = note_path(paper)
        if not note.exists() or "## Digest" not in note.read_text(encoding="utf-8"):
            continue
        text = note.read_text(encoding="utf-8")
        if NOTE_HASH.search(text):
            continue
        note.write_text(stamp_note(text, paper_hash(paper)), encoding="utf-8")
        stamped += 1
    print(f"read: {stamped} notes stamped with their paper's current text")


def main(argv):
    options = {"--limit": None, "--jobs": "4", "--model": None, "--focus": None}
    flags, targets = set(), []
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg in options:
            if not args:
                sys.exit(__doc__)
            options[arg] = args.pop(0)
        elif arg in ("--skims", "--redo", "--appendix", "--stale", "--stamp"):
            flags.add(arg)
        elif arg.startswith("-"):
            sys.exit(__doc__)
        else:
            targets.append(arg)
    if not targets:
        sys.exit(__doc__)
    model = options["--model"] or CONFIG.get("reader_model") or "opus"
    focus = ""
    if options["--focus"]:
        focus = ("What the area's review will ask, so that the note captures it:\n\n"
                 + Path(options["--focus"]).read_text(encoding="utf-8").strip() + "\n\n")
    grades = (ENGINE_ROOT / "guide" / "conversion-grades.md").read_text(encoding="utf-8").strip()
    template = (ENGINE_ROOT / "guide" / "reading-prompt.md").read_text(encoding="utf-8").replace(
        "{{grades}}", "\n".join("  " + line for line in grades.split("\n")))

    papers = []  # (paper, the folder whose papers are offered as related)
    for target in targets:
        path = Path(target)
        if path.is_file():
            papers.append((path.resolve(), path.resolve().parent))
        elif (LIBRARY_DIR / target.strip("/")).is_dir():
            scope_dir = LIBRARY_DIR / target.strip("/")
            papers += [(p.resolve(), scope_dir) for p in paper_files(scope_dir)]
        else:
            sys.exit(f"read: `{target}` is neither a paper nor a folder of the library")
    if "--stamp" in flags:
        stamp(papers)
        return
    todo, done_before, stale = [], 0, 0
    for paper, scope_dir in papers:
        depth, _ = note_state(paper.stem)
        is_stale = "--stale" in flags and depth is not None and note_is_stale(paper)
        stale += is_stale
        if ("--redo" in flags or depth is None or is_stale
                or (depth == "skim" and "--skims" in flags)):
            todo.append((paper, scope_dir))
        else:
            done_before += 1
    if options["--limit"]:
        todo = todo[:int(options["--limit"])]
    print(f"read: {len(papers)} papers, {done_before} already have a current digest"
          + (f", {stale} notes stale" if "--stale" in flags else "")
          + f", reading {len(todo)} with {model}")

    log = CACHE_DIR / "read-papers.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    read = failed = stopped = 0
    totals = {"input": 0, "output": 0}
    limit_message = None
    with ThreadPoolExecutor(max_workers=int(options["--jobs"])) as pool:
        waiting = {pool.submit(read_one, paper, scope_dir, model, focus, template,
                               "--appendix" in flags): paper
                   for paper, scope_dir in todo}
        for future in as_completed(waiting):
            paper = waiting[future]
            try:
                usage = future.result()
            except UsageLimit as error:
                stopped += 1
                if not str(error).startswith(("stopped:", "not started:")):
                    limit_message = str(error)
                    print(f"  LIMIT {paper.stem}: {error}", flush=True)
                    for other in waiting:
                        other.cancel()
                continue
            except CancelledError:
                stopped += 1
                continue
            except Exception as error:  # one failed paper should not stop the others
                failed += 1
                print(f"  FAILED {paper.stem}: {error}", flush=True)
                continue
            read += 1
            totals["input"] += usage["input"]
            totals["output"] += usage["output"]
            with log.open("a", encoding="utf-8") as out:
                out.write(json.dumps(usage, ensure_ascii=False) + "\n")
            problem = "" if usage["conversion"] == "ok" else f" | conversion: {usage['conversion']}"
            print(f"  read {paper.stem} ({usage['input']} in, {usage['output']} out, "
                  f"{usage['seconds']} s){problem}", flush=True)
    print(f"read: {read} notes written, {failed} failed, {stopped} not read because of the limit; "
          f"{totals['input']} input and {totals['output']} output tokens")
    if stop.is_set():
        print(f"read: stopped at the usage limit ({limit_message or 'no message'}). The notes written "
              "are kept; the same command continues, after the reset or on another account.")
        sys.exit(3)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
