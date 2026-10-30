"""Ask a candidate request for each sampled paper's type.

    PAPER_LIBRARY=<library> python3 run.py <filing | type-only> [--per-type N] [--model ID]

- `filing`: the request `paperlib add` sends (paperlib.filing_prompts: the topic tree, the
  title and the abstract), whose JSON now has a `type`. Sonnet, at FILING_EFFORT.
- `type-only`: guide/type-prompt.md (paperlib.type_prompts: the title, the stored summary
  and the abstract), as `paperlib fill-types` would send it. Sonnet, at FILING_EFFORT.

The abstract is arXiv's for a paper with an id, else the text layer's opening
(paperlib.paper_abstracts), as at filing and in the backfill. `--per-type N` asks only the
first N papers of each type (the pilot). Appends to results/<candidate>.jsonl, a line per
paper: the type given, the tokens and the dollars; a paper already answered is not asked again.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from common import RESULTS, abstracts, answers, paperlib, relative, sample


def main(argv):
    candidate = argv[0] if argv else None
    if candidate not in ("filing", "type-only"):
        sys.exit(__doc__)
    per_type = int(argv[argv.index("--per-type") + 1]) if "--per-type" in argv else None
    model = argv[argv.index("--model") + 1] if "--model" in argv else "sonnet"
    rows, seen = [], {}
    for paper, gold in sample():
        seen[gold] = seen.get(gold, 0) + 1
        if per_type is None or seen[gold] <= per_type:
            rows.append((paper, gold))
    done = answers(candidate)
    rows = [(p, g) for p, g in rows if relative(p) not in done]
    texts = abstracts([p for p, _ in rows])
    index = paperlib.paper_index()
    if candidate == "filing":
        topics = paperlib.load_topics()
        system, template = paperlib.filing_prompts(topics)
    else:
        system, template = paperlib.type_prompts()

    def one(row):
        paper, gold = row
        meta = index[paper]
        summary = " ".join(str(meta.get("summary") or "").split())
        prompt = template.format(title=meta["title"], summary=summary, abstract=texts[paper])
        start = time.time()
        try:
            reply, usage = paperlib.ask_model(model, system, prompt, effort=paperlib.FILING_EFFORT)
            kind = (paperlib.filing_choice(reply, topics)[2] if candidate == "filing"
                    else paperlib.type_choice(reply))
        except RuntimeError as error:  # one failed request should not stop the others
            print("FAILED", relative(paper), str(error)[:200], flush=True)
            return None
        return {"paper": relative(paper), "gold": gold, "type": kind, "model": model,
                **usage, "seconds": round(time.time() - start)}

    RESULTS.mkdir(exist_ok=True)
    spent = 0.0
    with ThreadPoolExecutor(4) as pool, open(RESULTS / f"{candidate}.jsonl", "a", encoding="utf-8") as log:
        for row in pool.map(one, rows):
            if row:
                log.write(json.dumps(row, ensure_ascii=False) + "\n")
                log.flush()
                spent += row.get("usd") or 0
                print(f"{row['gold']:>9} -> {row['type'] or '-':<9} ${row.get('usd') or 0:.4f}  {row['paper']}", flush=True)
    print(f"{candidate}: asked {len(rows)}, ${spent:.2f}")


if __name__ == "__main__":
    main(sys.argv[1:])
