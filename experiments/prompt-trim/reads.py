"""Read the test papers with one version of the engine, into results/notes/<condition>/.

    python3 reads.py <library> <engine> <work> <condition> [--python PATH]

Keeps <work>/mini-<condition>, a copy of the library's `llm/foundation-models` (paper markdown
only) with its own config, cache and notes folder, seeded with the notes already in
results/notes/<condition>/. Then runs <engine>'s own scripts/read-papers.py on the papers of
papers.txt, one at a time (--jobs 1), so that a version's whole request (prompt, related list,
flags) is what it sends; papers that already have a note are skipped. New notes go to
results/notes/<condition>/ and new request-log lines to results/reads-<condition>.jsonl.

Exit code 3: the account's usage limit was reached. The notes written are kept; run the same
command again, on another account or after the reset, and it continues.
"""
import json
import shutil
import subprocess
import sys
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPIC = "llm/foundation-models"


def main(argv):
    python = sys.executable
    if "--python" in argv:
        i = argv.index("--python")
        python = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 4:
        sys.exit(__doc__)
    library, engine, work = (Path(a).expanduser() for a in argv[:3])
    condition = argv[3]
    mini = work / f"mini-{condition}"
    if not mini.exists():
        (mini / "library" / TOPIC).mkdir(parents=True)
        for paper in (library / "library" / TOPIC).glob("*.md"):
            if paper.name != "README.md":
                shutil.copy(paper, mini / "library" / TOPIC / paper.name)
        (mini / "notes").mkdir()
        (mini / "paper-library.yaml").write_text(f"reader: the reader\npdf_root: {work / 'pdfs'}\n")
    out = HERE / "results" / "notes" / condition
    out.mkdir(parents=True, exist_ok=True)
    for note in out.glob("*.md"):
        if not (mini / "notes" / note.name).exists():
            shutil.copy(note, mini / "notes" / note.name)
    cache = work / f"cache-reads-{condition}"
    stems = [s.strip() for s in open(HERE / "papers.txt") if s.strip()]
    papers = [str(mini / "library" / TOPIC / f"{s}.md") for s in stems]
    env = {**os.environ, "PAPER_LIBRARY": str(mini), "PAPERS_CACHE": str(cache)}
    code = subprocess.run([python, str(engine / "scripts" / "read-papers.py"), *papers, "--jobs", "1",
                           "--model", "opus"], env=env).returncode
    for stem in stems:
        if (mini / "notes" / f"{stem}.md").exists():
            shutil.copy(mini / "notes" / f"{stem}.md", out / f"{stem}.md")
    log, logged = HERE / "results" / f"reads-{condition}.jsonl", set()
    if log.exists():
        logged = {json.loads(line)["paper"] for line in log.read_text().splitlines() if line.strip()}
    if (cache / "read-papers.jsonl").exists():
        with log.open("a") as f:
            for line in (cache / "read-papers.jsonl").read_text().splitlines():
                if line.strip() and json.loads(line)["paper"] not in logged:
                    f.write(line + "\n")
                    logged.add(json.loads(line)["paper"])
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main(sys.argv[1:])
