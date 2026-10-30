#!/usr/bin/env python3
"""Give papers without a type their type: the note's, else one model request each.

    ./scripts/fill-types.py [<scope or paper.txt> ...] [--dry-run] [--model ID] [--jobs N]

For every paper named, or under a scope (a folder of the library), or in the whole library
when none is named, whose frontmatter has no `type`: the type its note gives, where a reading
wrote one (no request); otherwise one request through `claude -p`, no tools, with the title,
the summary and the abstract (arXiv's, else the paper's own opening): guide/type-prompt.md.
A type already in the frontmatter is left alone (`paperlib read` and `paperlib set-type`
change it), so running it again only fills what is still empty. experiments/paper-type
measured the request against whole-paper readings: 100 of 105 agreed, at $0.0034 a paper.

    --dry-run    say how many papers would take their note's type and how many need a
                 request, and change nothing
    --model ID   the model (default: `filing_model` in paper-library.yaml, else sonnet)
    --jobs N     requests at a time (default 4)

Prints a line per paper typed, and appends each request's usage to <cache>/fill-types.jsonl.
Exit code 1 when a request failed: run it again for the rest.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from paperlib import (
    CACHE_DIR, CONFIG, FILING_EFFORT, LIBRARY_DIR, ask_model, note_fields, paper_abstracts, paper_files,
    paper_stem, read_paper, type_choice, type_prompts, write_paper,
)


def targets(names):
    """The papers named, or under the scopes named, or all of them."""
    if not names:
        return paper_files()
    papers = []
    for name in names:
        path = Path(name)
        if path.is_file():
            papers.append(path.resolve())
        elif (LIBRARY_DIR / name.strip("/")).is_dir():
            papers += paper_files(LIBRARY_DIR / name.strip("/"))
        else:
            sys.exit(f"fill-types: `{name}` is neither a paper nor a folder of the library")
    return list(dict.fromkeys(papers))


def set_type(paper, kind):
    meta, body = read_paper(paper)
    meta["type"] = kind
    write_paper(paper, meta, body)


def main(argv):
    options = {"--model": None, "--jobs": "4"}
    dry_run = "--dry-run" in argv
    args, names = [a for a in argv if a != "--dry-run"], []
    while args:
        arg = args.pop(0)
        if arg in options and args:
            options[arg] = args.pop(0)
        elif arg.startswith("-"):
            sys.exit(__doc__)
        else:
            names.append(arg)
    model = options["--model"] or CONFIG.get("filing_model") or "sonnet"

    untyped = [(p, read_paper(p)[0]) for p in targets(names)]
    untyped = [(p, meta) for p, meta in untyped if not meta.get("type")]
    from_note = [(p, note_fields(p).get("type")) for p, _ in untyped]
    from_note = [(p, kind) for p, kind in from_note if kind]
    noted = {p for p, _ in from_note}
    to_ask = [(p, meta) for p, meta in untyped if p not in noted]
    print(f"fill-types: {len(untyped)} papers without a type: {len(from_note)} from their note, "
          f"{len(to_ask)} to ask {model}" + (" (dry run)" if dry_run else ""))
    if dry_run:
        return

    for paper, kind in from_note:
        set_type(paper, kind)
        print(f"  {kind:<9} (note)  {paper_stem(paper)}")

    abstracts = paper_abstracts(p for p, _ in to_ask) if to_ask else {}
    system, template = type_prompts()

    def ask(paper, meta):
        prompt = template.format(title=meta.get("title") or paper_stem(paper),
                                 summary=" ".join(str(meta.get("summary") or "").split()) or "(none)",
                                 abstract=abstracts[paper] or "(none)")
        reply, usage = ask_model(model, system, prompt, effort=FILING_EFFORT)
        kind = type_choice(reply)
        if not kind:
            raise RuntimeError("no known type in the reply: " + reply.strip()[:120])
        set_type(paper, kind)
        return kind, usage

    asked, failed, usd = 0, 0, 0.0
    log = CACHE_DIR / "fill-types.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=int(options["--jobs"])) as pool, log.open("a", encoding="utf-8") as out:
        waiting = {pool.submit(ask, paper, meta): paper for paper, meta in to_ask}
        for future in as_completed(waiting):
            paper = waiting[future]
            try:
                kind, usage = future.result()
            except RuntimeError as error:  # one failed paper should not stop the others
                failed += 1
                print(f"  FAILED {paper_stem(paper)}: {error}", flush=True)
                continue
            asked += 1
            usd += usage.get("usd") or 0
            out.write(json.dumps({"paper": paper_stem(paper), "type": kind, "model": model, **usage},
                                 ensure_ascii=False) + "\n")
            print(f"  {kind:<9} (asked) {paper_stem(paper)}", flush=True)
    print(f"fill-types: {len(from_note)} from notes, {asked} asked (${usd:.2f}), {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
