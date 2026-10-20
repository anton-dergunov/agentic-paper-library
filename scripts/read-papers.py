#!/usr/bin/env python3
"""Read papers and write their notes, one model request per paper.

    ./scripts/read-papers.py <scope or paper.md> ... [--limit N] [--jobs N] [--model ID]
                             [--focus FILE] [--redo | --flagged] [--appendix] [--clean]
    ./scripts/read-papers.py --all [--clean] [--limit N] ...

For every paper named, or under a scope (a folder of the library), that has no digest in
notes/<stem>.md yet, sends the paper's reading view (paperlib read-view) to a model through
`claude -p`, with no tools, and writes the reply as the note. The prompt in
guide/reading-prompt.md, with the focus and the scope's papers, is the system prompt: the
same for every paper of a scope, so the requests after the first read it from the prompt
cache. Each paper is its own request, so nothing read earlier is paid for again, and a run
that is stopped loses only the papers in progress: run it again and it continues. An
existing note's Q&A is kept.

    --limit N     read at most N papers in this run (to spend a known budget)
    --jobs N      requests at a time (default 4)
    --model ID    the reading model (default: `reader_model` in paper-library.yaml, else
                  opus; experiments/reading-models compares the candidates)
    --focus FILE  a few lines on what the area's review will ask, put before the paper
    --redo        read again every paper named, whatever its note says
    --flagged     read again the papers named whose note is marked `reread:` (paperlib
                  reading lists them)
    --appendix    give the reader the appendices too (for papers whose note says the
                  main results are in them); use with --redo on those papers
    --all         every review scope (`review_scopes` in paper-library.yaml), in its order,
                  so the areas to review first are read first
    --clean       read only the papers whose conversion is likely sound: converted from
                  arXiv's HTML, with no open record of broken key content, and lacking no
                  pages of the PDF. Papers converted from a PDF have about ten times the
                  problems; read them after their tickets are fixed

The reader ends the note with the conversion problems it found, one a line, each under
the id of a ticket in the engine's tickets/ (or `new:<slug>`). They are taken out of the
note and written to issues/<stem>.yaml: they replace the records an earlier reading left
there, while the records a session or `paperlib symptoms` added, and those marked
wont-fix, stay (a problem already marked wont-fix is not added again).

Prints a line per paper with its tokens and the problems it recorded (how many break key
content), and appends the same to <cache>/read-papers.jsonl.

A request refused for a moment (rate limit, service busy) is retried after a pause. When
the account's usage window is used up, no further requests are sent, the message with its
reset time is printed, and the exit code is 3: the notes written are kept, and the same
command continues, after the reset or on another account.
"""

import datetime
import json
import re
import sys
import threading
import time
from concurrent.futures import CancelledError, ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

from paperlib import (
    CACHE_DIR, CONFIG, ENGINE_ROOT, LIBRARY_DIR, NOTES_DIR, ask_model, is_open, load_issues,
    load_tickets, note_path, paper_files, pdf_path_for, read_paper, read_view, reread_reason, save_issues,
)

SYSTEM = "You read research papers carefully and write precise notes on them."
RELATED_MAX = 150
_PAGE_MAP = None


def note_state(stem):
    """(has a digest, Q&A text) of a paper's note."""
    note = NOTES_DIR / f"{stem}.md"
    if not note.exists():
        return False, ""
    text = note.read_text(encoding="utf-8")
    qa = re.search(r"^## Q&A[ \t]*\n(.*)\Z", text, re.M | re.S)
    return "## Digest" in text, (qa.group(1).strip() if qa else "")


def related_list(paper, scope_dir):
    """The papers of the area, one line each, for the note's "Related in library".

    The paper itself is listed too, so that the list, and with it the system prompt, is the
    same for every paper of the area and is read from the prompt cache.
    """
    def lines(folder):
        return [f"- {o.stem}: " + " ".join(str(read_paper(o)[0].get("summary") or "").split())
                for o in paper_files(folder)]
    found = lines(scope_dir)
    if len(found) > RELATED_MAX:
        # A large area: keep the paper's own folder, which holds its nearest neighbours.
        found = lines(paper.parent)[:RELATED_MAX]
    return "\n".join(found)


# The note's last section, where the reader lists the conversion problems: one per line,
# `- <kind> | <where> | <what>[ | key-content]`, or `- none`.
CONVERSION_SECTION = re.compile(r"^## Conversion[ \t]*\n(.*?)(?=^## |\Z)", re.M | re.S)


def lacks_pages(paper):
    """Whether the paper's markdown lacks pages of its PDF (arXiv's HTML stopped partway)."""
    global _PAGE_MAP
    import importlib.util
    import pymupdf
    if _PAGE_MAP is None:
        spec = importlib.util.spec_from_file_location("page_map", Path(__file__).with_name("page-map.py"))
        _PAGE_MAP = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_PAGE_MAP)
    pdf = pdf_path_for(paper)
    if not pdf.exists():
        return False
    pymupdf.TOOLS.mupdf_display_errors(False)
    with pymupdf.open(pdf) as doc:
        missing, _ = _PAGE_MAP.missing_pages(doc, paper.read_text(encoding="utf-8"))
    return len(missing) >= _PAGE_MAP.MIN_MISSING


def unclean_reason(paper):
    """Why a paper's conversion is likely to read badly, or "" when it is likely sound."""
    source = (read_paper(paper)[0] or {}).get("source")
    if source != "html":
        return f"converted from {source or '?'}"
    if any(r.get("key-content") and is_open(r) for r in load_issues(paper)):
        return "key content broken"
    return "lacks pages of its PDF" if lacks_pages(paper) else ""


def kinds_list(tickets, status=None):
    """The causes for the reading prompt, one line per ticket: those still to fix, or with
    `status`, those of that status (the wont-fix ones, which the reader leaves unrecorded)."""
    chosen = [(tid, t) for tid, t in tickets.items()
              if (t.get("status") == status if status else t.get("status") not in ("done", "wont-fix"))]
    return "\n".join(f"- {tid}: {t.get('title', '')}" for tid, t in chosen) or "- (none yet)"


def take_conversion(note, tickets):
    """(the note without its Conversion section, the records the section lists)."""
    m = CONVERSION_SECTION.search(note)
    if not m:
        return note, []
    today = datetime.date.today().isoformat()
    records = []
    for line in m.group(1).splitlines():
        # The description may hold a "|" of its own (p(w|z), |V|): split off the kind and the
        # place from the left, and a closing "| key-content" from the right.
        parts = [p.strip() for p in line.strip().lstrip("-*").split("|", 2)]
        if len(parts) < 3 or not parts[0] or parts[0].lower() == "none":
            continue
        kind, where, what = parts[0].strip("`"), parts[1], parts[2]
        head, _, tail = what.rpartition("|")
        key = bool(head) and tail.strip().lower().replace(" ", "-") == "key-content"
        if key:
            what = head.strip()
        record = {"kind": kind, "where": where, "what": what, "key-content": key,
                  "by": "reader", "found": today}
        if kind.startswith("new:") or kind not in tickets:
            record.update(kind="new", suggested=kind.removeprefix("new:"))
        records.append(record)
    return (note[:m.start()] + note[m.end():]).rstrip() + "\n", records


def merge_reader_records(old, new):
    """A paper's records after a reading: the reader's replace those of the previous reading;
    the rest stay, and a problem already marked wont-fix is not added again."""
    kept = [r for r in old if r.get("by") != "reader" or not is_open(r)]
    known = {(r.get("kind"), " ".join(str(r.get("where", "")).lower().split())) for r in old if not is_open(r)}
    return kept + [r for r in new if (r["kind"], " ".join(r["where"].lower().split())) not in known]


class UsageLimit(RuntimeError):
    """The account's usage window is used up: nothing more can be read until it resets."""


# What `claude -p` says when the usage window is used up ("You've hit your session limit ·
# resets 1:10am"), and when a request was refused for a moment (too many at once, the
# service busy). The first stops the run; the second is retried after a pause.
WINDOW_LIMIT = re.compile(r"(session|usage|weekly|daily|monthly) limit|resets? (at )?\d|quota|credit balance", re.I)
TRANSIENT = re.compile(r"rate.?limit|too many requests|\b429\b|overloaded|\b529\b|\b50[234]\b|timed? ?out", re.I)
RETRY_PAUSES = [30, 60, 120]  # seconds before each retry of a transient refusal
stop = threading.Event()  # set at a usage limit: requests not yet sent are not sent


def ask(model, system, prompt):
    """ask_model, with transient refusals retried and a usage limit raised as UsageLimit."""
    for pause in RETRY_PAUSES + [None]:
        if stop.is_set():
            raise UsageLimit("stopped: the usage limit was reached")
        try:
            return ask_model(model, system, prompt)
        except RuntimeError as error:
            if WINDOW_LIMIT.search(str(error)):
                stop.set()
                raise UsageLimit(str(error)) from None
            if pause is None or not TRANSIENT.search(str(error)):
                raise
            time.sleep(pause)


def read_one(paper, scope_dir, model, focus, template, appendix, tickets):
    if stop.is_set():
        raise UsageLimit("not started: the usage limit was reached")
    meta, body = read_paper(paper)
    system = (SYSTEM + "\n\n" + template.replace("{{focus}}", focus)
              .replace("{{related}}", related_list(paper, scope_dir)))
    start = time.time()
    try:
        note, usage = ask(model, system, "The paper:\n\n" + read_view(meta, body, appendix=appendix))
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
    note, records = take_conversion(note, tickets)
    if "## Related in library" not in note:
        note += "\n\n## Related in library\n"
    _, qa = note_state(paper.stem)
    note = note.rstrip() + "\n\n## Q&A\n" + (f"\n{qa}\n" if qa else "")
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    note_path(paper).write_text(note, encoding="utf-8")
    save_issues(paper, merge_reader_records(load_issues(paper), records))
    usage.update(paper=paper.stem, model=model, seconds=round(time.time() - start),
                 issues=len(records), key_content=sum(r["key-content"] for r in records))
    return usage


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
        elif arg in ("--redo", "--flagged", "--appendix", "--all", "--clean"):
            flags.add(arg)
        elif arg.startswith("-"):
            sys.exit(__doc__)
        else:
            targets.append(arg)
    if "--all" in flags:
        from reading import review_scopes
        targets += [s for _, scopes in review_scopes() for s in scopes]
    if not targets:
        sys.exit(__doc__)
    model = options["--model"] or CONFIG.get("reader_model") or "opus"
    focus = ""
    if options["--focus"]:
        focus = ("What the area's review will ask, so that the note captures it:\n\n"
                 + Path(options["--focus"]).read_text(encoding="utf-8").strip() + "\n\n")
    tickets = load_tickets()
    template = ((ENGINE_ROOT / "guide" / "reading-prompt.md").read_text(encoding="utf-8")
                .replace("{{kinds}}", kinds_list(tickets))
                .replace("{{wont_fix}}", kinds_list(tickets, "wont-fix")))

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
    seen = set()
    papers = [(p, s) for p, s in papers if not (p in seen or seen.add(p))]
    todo, done_before = [], 0
    for paper, scope_dir in papers:
        has_digest, _ = note_state(paper.stem)
        if "--flagged" in flags:
            if has_digest and reread_reason(paper):
                todo.append((paper, scope_dir))
            else:
                done_before += 1
        elif "--redo" in flags or not has_digest:
            todo.append((paper, scope_dir))
        else:
            done_before += 1
    skipped = {}
    if "--clean" in flags and todo:
        with ProcessPoolExecutor() as pool:  # the page check is CPU-bound
            reasons = list(pool.map(unclean_reason, [paper for paper, _ in todo], chunksize=20))
        for reason in filter(None, reasons):
            skipped[reason] = skipped.get(reason, 0) + 1
        todo = [item for item, reason in zip(todo, reasons) if not reason]
    if options["--limit"]:
        todo = todo[:int(options["--limit"])]
    print(f"read: {len(papers)} papers, {done_before} already have a digest, reading {len(todo)} with {model}"
          + ("; left for later, as likely to read badly: "
             + ", ".join(f"{n} {reason}" for reason, n in sorted(skipped.items())) if skipped else ""))

    log = CACHE_DIR / "read-papers.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    read = failed = stopped = 0
    totals = {"input": 0, "output": 0}
    limit_message = None
    with ThreadPoolExecutor(max_workers=int(options["--jobs"])) as pool:
        waiting = {pool.submit(read_one, paper, scope_dir, model, focus, template,
                               "--appendix" in flags, tickets): paper
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
            problem = (f" | conversion: {usage['issues']} problems" + (f", {usage['key_content']} key content"
                       if usage["key_content"] else "")) if usage["issues"] else ""
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
