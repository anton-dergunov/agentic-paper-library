"""Read the test papers at one effort level, into results/notes/<effort>/.

    PAPER_LIBRARY=<library> python3 run.py <effort> [<effort> ...]
    PAPER_LIBRARY=<library> python3 run.py library

The request is the one `paperlib read` sends (read-papers.py's read_one: the reading prompt
with the paper's folder as the related list, as system prompt; the paper's reading view as
the prompt), with `--effort <effort>`. Notes go to results/notes/<effort>/ and the request's
usage to results/reads.jsonl; nothing in the library changes, and a paper with a note is not
read again. `library` copies the library's current notes into results/notes/high instead
of reading: they were read at the author's Claude Code setting, `effortLevel: high`.
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent
sys.path.insert(0, str(ENGINE / "scripts"))
from paperlib import LIBRARY_DIR, NOTES_DIR, ask_model, read_paper, text_view  # noqa: E402

spec = importlib.util.spec_from_file_location("read_papers", ENGINE / "scripts" / "read-papers.py")
read_papers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(read_papers)


def papers():
    return [LIBRARY_DIR / f"{line.strip()}.txt" for line in open(HERE / "papers.txt") if line.strip()]


def main(efforts):
    template = (ENGINE / "guide" / "reading-prompt.md").read_text(encoding="utf-8")
    for effort in efforts:
        out = HERE / "results" / "notes" / ("high" if effort == "library" else effort)
        out.mkdir(parents=True, exist_ok=True)
        for paper in papers():
            target = out / f"{paper.stem}.md"
            if target.exists():
                continue
            if effort == "library":
                shutil.copy(NOTES_DIR / f"{paper.stem}.md", target)
                continue
            meta, body = read_paper(paper)
            system = (read_papers.SYSTEM + "\n\n" + template.replace("{{focus}}", "")
                      .replace("{{related}}", read_papers.related_list(paper, paper.parent)))
            note, usage = ask_model("opus", system, "The paper:\n\n" + text_view(meta, body), effort=effort)
            target.write_text(note.strip() + "\n", encoding="utf-8")
            usage.update(paper=paper.stem, effort=effort)
            with (HERE / "results" / "reads.jsonl").open("a") as log:
                log.write(json.dumps(usage) + "\n")
            print(f"{effort} {paper.stem[:40]}: {usage}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or sys.exit(__doc__))
