#!/usr/bin/env python3
"""Vet papers whose fate in a library is known, and save the verdicts.

    PAPER_LIBRARY=<library> uv run python experiments/paper-vetting/run.py sample
    PAPER_LIBRARY=<library> uv run python experiments/paper-vetting/run.py vet <model> [--jobs N]

`sample` writes results/sample.jsonl: papers in three classes of label (see the README),
drawn with a fixed seed. `vet` runs vet.py's `vet` on each and appends to
results/<model>.jsonl; a rerun skips the papers already there. A paper in the library is
hidden from its own verdict: its file is left out of the folder's list and of the search for
its title, and notes and reviews are not searched at all, since they name a paper because it
is in the library.
"""
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import paperlib  # noqa: E402

RESULTS = HERE / "results"
SEED, SKIPPED, WEAK = 20261009, 30, 15


def ever_skipped():
    """arXiv ids that were in catalog/skipped.yaml at any commit of the library."""
    import yaml
    git = ["git", "-C", str(paperlib.LIBRARY_ROOT)]
    file = str(paperlib.SKIPPED_FILE.relative_to(paperlib.LIBRARY_ROOT))
    ids = set()
    for rev in subprocess.run(git + ["log", "--format=%H", "--", file], capture_output=True, text=True).stdout.split():
        text = subprocess.run(git + ["show", f"{rev}:{file}"], capture_output=True, text=True).stdout
        ids |= {str(e["arxiv"]) for e in yaml.safe_load(text) or [] if e.get("arxiv")}
    return ids


def sample():
    rng = random.Random(SEED)
    in_library = paperlib.library_arxiv_ids()
    relative = lambda p: str(p.relative_to(paperlib.LIBRARY_DIR))
    skipped = [e for e in paperlib.load_skipped() if e.get("arxiv") and str(e["arxiv"]) not in in_library]
    rows = [{"class": "skipped", "arxiv": str(e["arxiv"]), "title": e["title"], "label": e.get("reason", "")}
            for e in rng.sample(skipped, SKIPPED)]
    reviewed = {}
    for arxiv_id in sorted(ever_skipped() & set(in_library)):
        reviewed[arxiv_id] = "unskipped by the reader"
    overviews = {p.stem for p in paperlib.OVERVIEW_DIR.glob("*.md")} if paperlib.OVERVIEW_DIR else set()
    for arxiv_id, path in in_library.items():
        if path.stem in overviews:
            reviewed.setdefault(arxiv_id, "the reader wrote an overview of it")
    rows += [{"class": "kept-reviewed", "arxiv": i, "title": in_library[i].stem, "label": why,
              "paper": relative(in_library[i])} for i, why in sorted(reviewed.items())]
    rest = sorted(set(in_library) - set(reviewed))
    rows += [{"class": "kept-unreviewed", "arxiv": i, "title": in_library[i].stem, "label": "proposed by an agent",
              "paper": relative(in_library[i])} for i in rng.sample(rest, WEAK)]
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "sample.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    for name in ("skipped", "kept-reviewed", "kept-unreviewed"):
        print(name, sum(r["class"] == name for r in rows))


def vet_all(model, jobs):
    spec = importlib.util.spec_from_file_location("vet_paper", HERE / "vet.py")
    vp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vp)
    vp.NOTES_DIR = vp.REVIEWS_DIR = Path("/nonexistent")
    rows = [json.loads(line) for line in (RESULTS / "sample.jsonl").read_text().splitlines()]
    out = RESULTS / f"{re.sub(r'[^a-z0-9.-]+', '-', model)}.jsonl"
    done = {json.loads(line)["arxiv"] for line in out.read_text().splitlines()} if out.exists() else set()
    rows = [r for r in rows if r["arxiv"] not in done]
    if not rows:
        return print("nothing left")
    ids = [r["arxiv"] for r in rows]
    data = paperlib.fetch(f"{vp.API}?id_list={quote(','.join(ids))}&max_results={len(ids)}", attempts=5)
    entries = paperlib.parse_arxiv_entries(data.decode("utf-8"))
    records = vp.semantic_scholar(ids)
    topics = paperlib.load_topics()
    prompts = paperlib.filing_prompts(topics), vp.vetting_prompts()

    def one(row):
        entry = entries.get(row["arxiv"])
        if not entry:
            return {**row, "error": "not found on arXiv"}
        exclude = paperlib.LIBRARY_DIR / row["paper"] if row.get("paper") else None
        try:
            result = vp.vet(row["arxiv"], entry, records.get(row["arxiv"]), topics, model,
                            exclude=exclude, prompts=prompts)
        except RuntimeError as error:
            return {**row, "error": str(error)}
        return {**row, **{k: result[k] for k in ("folder", "signals", "verdict", "recommendation", "usage")}}

    with ThreadPoolExecutor(jobs) as pool, out.open("a") as file:
        for result in pool.map(one, rows):
            if "error" not in result:
                file.write(json.dumps(result, ensure_ascii=False) + "\n")
                file.flush()
            print(result["class"], result["arxiv"], result.get("recommendation") or result.get("error"), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["sample"]:
        sample()
    elif sys.argv[1:2] == ["vet"] and len(sys.argv) > 2:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 4
        vet_all(sys.argv[2], jobs)
    else:
        sys.exit(__doc__)
