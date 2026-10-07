"""Read the test papers with one version of the engine, into results/notes/<condition>/.

    python3 reads.py <library> <engine> <scratch> <condition> [--python PATH]

Builds <scratch>/mini, a copy of the library's `llm/foundation-models` (paper markdown only)
with its own config, cache and an empty notes folder, then runs <engine>'s own
scripts/read-papers.py on the papers of papers.txt, one at a time (--jobs 1), so that a
version's whole request (prompt, related list, flags) is what it sends. The notes go to
results/notes/<condition>/ and the request log to results/reads-<condition>.jsonl.
"""
import os
import shutil
import subprocess
import sys
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
    library, engine, scratch = (Path(a).expanduser() for a in argv[:3])
    condition = argv[3]
    mini = scratch / "mini"
    if mini.exists():
        shutil.rmtree(mini)
    (mini / "library" / TOPIC).mkdir(parents=True)
    for paper in (library / "library" / TOPIC).glob("*.md"):
        if paper.name != "README.md":
            shutil.copy(paper, mini / "library" / TOPIC / paper.name)
    (mini / "notes").mkdir()
    (mini / "paper-library.yaml").write_text(f"reader: the reader\npdf_root: {scratch / 'pdfs'}\n")
    cache = scratch / f"cache-{condition}"
    if cache.exists():
        shutil.rmtree(cache)
    stems = [s.strip() for s in open(HERE / "papers.txt") if s.strip()]
    papers = [str(mini / "library" / TOPIC / f"{s}.md") for s in stems]
    env = {**os.environ, "PAPER_LIBRARY": str(mini), "PAPERS_CACHE": str(cache)}
    subprocess.run([python, str(engine / "scripts" / "read-papers.py"), *papers, "--jobs", "1",
                    "--model", "opus"], env=env, check=True)
    out = HERE / "results" / "notes" / condition
    out.mkdir(parents=True, exist_ok=True)
    for stem in stems:
        shutil.copy(mini / "notes" / f"{stem}.md", out / f"{stem}.md")
    shutil.copy(cache / "read-papers.jsonl", HERE / "results" / f"reads-{condition}.jsonl")


if __name__ == "__main__":
    main(sys.argv[1:])
