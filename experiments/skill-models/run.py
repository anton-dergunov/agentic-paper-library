"""Ask each model to file each paper and summarise it: topic tree, title and abstract in,
folder and summary out, one request with no tools.

    python3 run.py <library> <out-dir> [model ...]

Writes <out-dir>/<model>.jsonl, a line per paper (folder, reason, summary, tokens, seconds).
A paper a model has already answered is not asked again.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import MODELS, ask, json_in, paper

HERE = Path(__file__).parent
SYSTEM = "You are a careful research librarian."
# The style sample: three summaries of papers that are not in papers.txt.
STYLE = ["llm/prompting-and-in-context/GEPA. Reflective Prompt Evolution Can Outperform Reinforcement Learning",
         "llm/post-training/preference-learning/Constitutional AI. Harmlessness from AI Feedback",
         "llm/memory/agent/Zep. A Temporal Knowledge Graph Architecture for Agent Memory"]


def main():
    library, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    stems = [line.strip() for line in open(HERE / "papers.txt") if line.strip()]
    assert not set(stems) & set(STYLE)
    template = (HERE / "prompt.md").read_text()
    topics = "\n".join(line for line in (Path(library) / "catalog/topics.yaml").read_text().splitlines()
                       if line and not line.startswith("#"))
    style = "\n".join("- " + paper(library, s)["summary"] for s in STYLE)

    def one(model, relative):
        p = paper(library, relative)
        prompt = template.format(topics=topics, style=style, title=p["title"], abstract=p["abstract"])
        start = time.time()
        try:
            text, usage = ask(model, SYSTEM, prompt)
            answer = json_in(text)
        except Exception as error:  # one failed call should not stop the others
            print(model, relative, "FAILED", str(error)[:200], flush=True)
            return None
        return {"paper": relative, "folder": answer.get("folder"), "reason": answer.get("reason"),
                "summary": answer.get("summary"), **usage, "seconds": round(time.time() - start)}

    for model in sys.argv[3:] or MODELS:
        target = out / (model + ".jsonl")
        done = {json.loads(line)["paper"] for line in open(target)} if target.exists() else set()
        todo = [s for s in stems if s not in done]
        with ThreadPoolExecutor(4) as pool, open(target, "a") as log:
            for row in pool.map(lambda s: one(model, s), todo):
                if row:
                    log.write(json.dumps(row, ensure_ascii=False) + "\n")
                    log.flush()
        print(model, "asked", len(todo), flush=True)


if __name__ == "__main__":
    main()
