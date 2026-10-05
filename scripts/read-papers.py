#!/usr/bin/env python3
"""Read papers and write their notes, one model request per paper.

    ./scripts/read-papers.py <scope or paper.md> ... [--limit N] [--jobs N]
                             [--model ID] [--focus FILE] [--skims] [--redo] [--appendix]

For every paper named, or under a scope (a folder of the library), that has no digest in
notes/<stem>.md yet, sends the paper's reading view (paperlib read-view) with the prompt
in guide/reading-prompt.md to a model through `claude -p`, with no tools, and writes the
reply as the note. Each paper is its own request, so nothing read earlier is paid for
again, and a run that is stopped loses only the papers in progress: run it again and it
continues. An existing note's Q&A is kept.

    --limit N     read at most N papers in this run (to spend a known budget)
    --jobs N      requests at a time (default 3)
    --model ID    the reading model (default: `reader_model` in paper-library.yaml, else
                  opus; experiments/reading-models compares the candidates)
    --focus FILE  a few lines on what the area's review will ask, put before the paper
    --skims       also read again the papers whose note says `read: skim`
    --redo        read again every paper named, whatever its note says
    --appendix    give the reader the appendices too (for papers whose note says the
                  main results are in them); use with --redo on those papers

Prints a line per paper with its tokens and any conversion problem the reader reported,
and appends the same to <cache>/read-papers.jsonl. Exit code 3 means the usage limit was
reached; the papers already written are kept.
"""

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from paperlib import (
    CACHE_DIR, CONFIG, ENGINE_ROOT, LIBRARY_DIR, NOTES_DIR, ask_model, paper_files, read_paper,
    read_view,
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


def read_one(paper, scope_dir, model, focus, template, appendix):
    meta, body = read_paper(paper)
    prompt = (template.replace("{{focus}}", focus)
              .replace("{{related}}", related_list(paper, scope_dir))
              + read_view(meta, body, appendix=appendix))
    start = time.time()
    note, usage = ask_model(model, SYSTEM, prompt)
    note = note.strip()
    if note.startswith("```"):
        note = note.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if "## Digest" not in note or not note.startswith("# "):
        raise RuntimeError("the reply is not a note: " + note[:120].replace("\n", " "))
    if "## Related in library" not in note:
        note += "\n\n## Related in library\n"
    _, qa = note_state(paper.stem)
    note = note.rstrip() + "\n\n## Q&A\n" + (f"\n{qa}\n" if qa else "")
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    (NOTES_DIR / f"{paper.stem}.md").write_text(note, encoding="utf-8")
    conversion = re.search(r"^conversion:\s*(.*)$", note, re.M)
    usage.update(paper=paper.stem, model=model, seconds=round(time.time() - start),
                 conversion=conversion.group(1).strip() if conversion else "?")
    return usage


def main(argv):
    options = {"--limit": None, "--jobs": "3", "--model": None, "--focus": None}
    flags, targets = set(), []
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg in options:
            if not args:
                sys.exit(__doc__)
            options[arg] = args.pop(0)
        elif arg in ("--skims", "--redo", "--appendix"):
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
    template = (ENGINE_ROOT / "guide" / "reading-prompt.md").read_text(encoding="utf-8")

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
    todo, done_before = [], 0
    for paper, scope_dir in papers:
        depth, _ = note_state(paper.stem)
        if "--redo" in flags or depth is None or (depth == "skim" and "--skims" in flags):
            todo.append((paper, scope_dir))
        else:
            done_before += 1
    if options["--limit"]:
        todo = todo[:int(options["--limit"])]
    print(f"read: {len(papers)} papers, {done_before} already have a digest, reading {len(todo)} with {model}")

    log = CACHE_DIR / "read-papers.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    read = failed = 0
    totals = {"input": 0, "output": 0}
    limit_hit = False
    with ThreadPoolExecutor(max_workers=int(options["--jobs"])) as pool:
        waiting = {pool.submit(read_one, paper, scope_dir, model, focus, template,
                               "--appendix" in flags): paper
                   for paper, scope_dir in todo}
        for future in as_completed(waiting):
            paper = waiting[future]
            try:
                usage = future.result()
            except Exception as error:  # one failed paper should not stop the others
                failed += 1
                print(f"  FAILED {paper.stem}: {error}", flush=True)
                if re.search(r"limit|quota|rate", str(error), re.I):
                    limit_hit = True
                    for other in waiting:
                        other.cancel()
                continue
            read += 1
            totals["input"] += usage["input"]
            totals["output"] += usage["output"]
            with log.open("a", encoding="utf-8") as out:
                out.write(json.dumps(usage, ensure_ascii=False) + "\n")
            problem = "" if usage["conversion"].lower().startswith("ok") else f" | conversion: {usage['conversion']}"
            print(f"  read {paper.stem} ({usage['input']} in, {usage['output']} out, "
                  f"{usage['seconds']} s){problem}", flush=True)
    print(f"read: {read} notes written, {failed} failed, {len(todo) - read - failed} not started; "
          f"{totals['input']} input and {totals['output']} output tokens")
    if limit_hit:
        print("read: stopped at a usage limit; run the same command again to continue")
        sys.exit(3)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
