"""What the experiment's scripts share: the engine's paperlib, the sample and the abstracts."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
import paperlib  # noqa: E402

RESULTS = HERE / "results"
CANDIDATES = ("filing", "type-only")


def sample():
    """[(paper path, the note's type)] from papers.txt: `<type>\\t<path in the library, no suffix>`."""
    rows = []
    for line in open(HERE / "papers.txt", encoding="utf-8"):
        if line.strip():
            gold, relative = line.rstrip("\n").split("\t")
            rows.append((paperlib.paper_file_for(paperlib.LIBRARY_DIR / relative), gold))
    return rows


def abstracts(papers):
    """paperlib.paper_abstracts, kept in the cache dir (abstracts are not committed: not every
    paper is openly licensed)."""
    store = paperlib.CACHE_DIR / "paper-type-abstracts.json"
    known = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    missing = [p for p in papers if str(p) not in known]
    if missing:
        known.update({str(p): a for p, a in paperlib.paper_abstracts(missing).items()})
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
    return {p: known[str(p)] for p in papers}


def relative(paper):
    return paper.relative_to(paperlib.LIBRARY_DIR).with_suffix("").as_posix()


def answers(candidate):
    target = RESULTS / f"{candidate}.jsonl"
    if not target.exists():
        return {}
    return {row["paper"]: row for row in map(json.loads, open(target, encoding="utf-8"))}
