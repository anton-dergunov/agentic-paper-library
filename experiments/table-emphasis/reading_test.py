#!/usr/bin/env python3
"""Does marking a table's shading help a model answer questions about the table?

    uv run python reading_test.py pick shading.tsv > tables.tsv
    uv run python reading_test.py excerpts tables.tsv <out-dir>
    uv run python reading_test.py ask questions.tsv <out-dir> > answers.jsonl

pick      sixteen shaded tables, four for each of: rows or cells shaded, the
          caption referring to the shading or not (seeded).
excerpts  each table with its caption and the two paragraphs that cite it,
          converted twice: <n>-plain.md (shading dropped) and <n>-marked.md
          (shading as <mark>). The excerpts are paper text and stay out of
          the repository.
ask       questions.tsv has a table's number, the kind of question
          ("shading" or "control"), the question and the expected answer.
          Each is put to the model over both excerpts, as `paperlib read`
          puts a paper: one request, no tools.
"""

import collections
import gzip
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from paperlib import CACHE_DIR, ask_model, read_view  # noqa: E402

spec = importlib.util.spec_from_file_location("html_to_markdown", SCRIPTS / "html-to-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

MODEL = "opus"
SYSTEM = ("You answer a question about an excerpt of a research paper: a table, its caption and the "
          "paragraphs that cite it. Answer from the excerpt only, in one or two sentences. If the excerpt "
          "does not say, answer \"The excerpt does not say.\"")


def pick(shading):
    rows = [line.split("\t") for line in Path(shading).read_text(encoding="utf-8").splitlines()[1:]]
    groups = collections.defaultdict(list)
    for paper, float_id, pattern, shaded, cells, colours, named, *_ in rows:
        # A table of a readable size, one table per paper.
        if pattern in ("some rows", "some cells") and 12 <= int(cells) <= 150:
            groups[pattern, named].append((paper, float_id))
    rng = random.Random(20261008)
    print("n\tpaper\tfloat\tpattern\tcaption names it")
    n, used = 0, set()
    for (pattern, named), tables in sorted(groups.items()):
        rng.shuffle(tables)
        chosen = 0
        for paper, float_id in tables:
            if paper in used or chosen == 4:
                continue
            used.add(paper)
            chosen += 1
            n += 1
            print(f"{n}\t{paper}\t{float_id}\t{pattern}\t{named}")


def excerpt(paper, float_id, rule):
    page = gzip.open(CACHE_DIR / "arxiv" / "html" / paper / "index.html.gz", "rt", encoding="utf-8").read()
    article = converter.extract_article(page)
    start = re.search(rf'<figure\b[^>]*\bid="{re.escape(float_id)}"', article)
    figure = article[start.start():converter.balanced_end(article, start.start(), "figure")]
    citing = [p for p in re.findall(r'<p\b[^>]*class="ltx_p"[^>]*>.*?</p>', article, re.S)
              if f'href="#{float_id}"' in p and "<figure" not in p][:2]
    html = f'<html><body><div class="ltx_page_content">{"".join(citing)}{figure}</div></body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "paper.html").write_text(html, encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "html-to-markdown.py", tmp / "paper.html", tmp / "body.md",
                        tmp / "images", "paper"], check=True, capture_output=True,
                       env={**os.environ, "PAPERLIB_SHADING": rule})
        body = (tmp / "body.md").read_text(encoding="utf-8")
    # As a model reads it: the read view's body, without its title and closing note.
    return read_view({"title": "", "source": "html"}, body).split("\n\n", 2)[2].rsplit("\n\n", 1)[0]


def excerpts(tables, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for line in Path(tables).read_text(encoding="utf-8").splitlines()[1:]:
        n, paper, float_id, *_ = line.split("\t")
        for name, rule in (("plain", "none"), ("marked", "all")):
            (out / f"{n}-{name}.md").write_text(excerpt(paper, float_id, rule), encoding="utf-8")
        marked = (out / f"{n}-marked.md").read_text(encoding="utf-8")
        print(f"{n}\t{paper}\t{len(marked)} chars\t{marked.count('<mark>')} marks", file=sys.stderr)


def ask(questions, out):
    out = Path(out)
    for line in Path(questions).read_text(encoding="utf-8").splitlines()[1:]:
        n, kind, question, expected = line.split("\t")
        for variant in ("plain", "marked"):
            text = (out / f"{n}-{variant}.md").read_text(encoding="utf-8")
            reply, usage = ask_model(MODEL, SYSTEM, f"{text}\n\nQuestion: {question}")
            print(json.dumps({"table": n, "kind": kind, "variant": variant, "question": question,
                              "expected": expected, "answer": " ".join(reply.split()), **usage},
                             ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("pick", "excerpts", "ask"):
        sys.exit(__doc__)
    {"pick": pick, "excerpts": excerpts, "ask": ask}[sys.argv[1]](*sys.argv[2:])
