# /// script
# requires-python = ">=3.12"
# dependencies = ["trafilatura==2.3.1", "pyyaml>=6"]
# ///
"""Which converter should make a web article's markdown, now that papers are read from
their PDF's text layer and web articles keep a markdown copy?

    PAPER_LIBRARY=<library> uv run run.py [pick | render | convert | score]   # all by default

- pick: three of the library's web articles at random (fixed seed), one from each kind of
  site: distill.pub, transformer-circuits.pub, and the others (company blogs).
- render: each page in headless Chrome after its scripts ran (`--dump-dom`), into the cache.
- convert: Defuddle and Readability + Turndown (convert.mjs, on jsdom), Trafilatura (here);
  images dropped by each. The library's markdown, its image links removed, is the baseline.
- score: size, coverage of the rendered article's sentences and of the baseline's, text from
  outside the article, equations kept as TeX, headings, tables, footnotes, captions.
  Writes results/summary.md and results/scores.json.

Converted text stays in the cache, ~/.cache/papers/experiments/web-articles/<slug>/: of the
three sites only distill.pub is CC BY.
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
LIBRARY = Path(os.environ["PAPER_LIBRARY"]).expanduser()
OUT = Path.home() / ".cache" / "papers" / "experiments" / "web-articles"
RESULTS = HERE / "results"
SEED = 20261026
FORMS = ("baseline", "defuddle", "readability", "trafilatura")
CHROME = (os.environ.get("CHROME") or shutil.which("google-chrome")
          or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
# As in add-web-article.py: Cloudflare-fronted blogs answer "HeadlessChrome" with a bot check.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def kind(url):
    return "distill" if "distill.pub" in url else "circuits" if "transformer-circuits.pub" in url else "blog"


def web_articles():
    found = []
    for path in sorted((LIBRARY / "library").rglob("*.md")):
        head = path.read_text(encoding="utf-8")[:4000]
        if path.name != "README.md" and "\nsource: web\n" in head:
            meta = yaml.safe_load(head.split("---")[1])
            found.append({"path": str(path), "url": meta["url"], "title": meta["title"]})
    return found


def slug(article):
    return re.sub(r"[^a-z0-9]+", "-", article["title"].lower())[:40].strip("-")


def pick():
    rng = random.Random(SEED)
    chosen = []
    articles = web_articles()
    for k in ("distill", "circuits", "blog"):
        pool = [a for a in articles if kind(a["url"]) == k]
        chosen.append(dict(rng.choice(pool), kind=k, slug=None, of=len(pool)))
        chosen[-1]["slug"] = slug(chosen[-1])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "chosen.json").write_text(json.dumps(chosen, indent=1))
    for a in chosen:
        print("%s (1 of %d): %s" % (a["kind"], a["of"], a["title"]))
    return chosen


def chosen():
    return json.loads((OUT / "chosen.json").read_text())


def render():
    """The rendered DOM, after a 20 s virtual-time budget; Chrome is stopped after 60 s."""
    for a in chosen():
        target = OUT / a["slug"] / "page.html"
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as profile:
            proc = subprocess.Popen(
                [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                 f"--user-data-dir={profile}", f"--user-agent={USER_AGENT}", "--virtual-time-budget=20000",
                 "--dump-dom", a["url"]], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            try:
                dom, _ = proc.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                dom, _ = proc.communicate()
        target.write_text(dom, encoding="utf-8")
        print("%s: %d KB rendered" % (a["slug"], len(dom) // 1024))


def baseline(path):
    """The library's markdown without frontmatter, image links or <img> tags."""
    text = Path(path).read_text(encoding="utf-8")
    text = text.split("---", 2)[2] if text.startswith("---") else text
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    return re.sub(r"<img[^>]*>", "", text)


def convert():
    import trafilatura
    for a in chosen():
        folder = OUT / a["slug"]
        html = (folder / "page.html").read_text(encoding="utf-8")
        subprocess.run(["node", str(HERE / "convert.mjs"), str(folder / "page.html"), a["url"], str(folder)],
                       check=True, cwd=HERE)
        md = trafilatura.extract(html, url=a["url"], output_format="markdown", include_formatting=True,
                                 include_tables=True, include_images=False, include_links=False,
                                 include_comments=False, favor_recall=True) or ""
        (folder / "trafilatura.md").write_text(md, encoding="utf-8")
        (folder / "baseline.md").write_text(baseline(a["path"]), encoding="utf-8")
        print(a["slug"], {f: len((folder / ("%s.md" % f)).read_text()) for f in FORMS})


MATH = re.compile(r"\$\$.+?\$\$|\$[^$\n]+?\$|\\\(.+?\\\)|\\\[.+?\\\]", re.S)


def words(text):
    return re.sub(r"[^0-9a-z]+", " ", text.lower()).split()


def grams(ws, n=5):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def sentences(text):
    """Sentences of eight words or more, with markdown syntax and maths taken out."""
    text = MATH.sub(" ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return [s for s in re.split(r"(?<=[.!?])\s+|\n\s*\n", text) if len(words(s)) >= 8]


def coverage(reference, candidate):
    """The share of the reference's sentences with at least 80% of their 5-grams in the candidate."""
    have = grams(words(MATH.sub(" ", candidate)))
    sents = sentences(reference)
    hit = sum(1 for s in sents if (g := grams(words(s))) and len(g & have) >= 0.8 * len(g))
    return hit / len(sents) if sents else 0.0, len(sents)


def outside(candidate, *references):
    """The share of the candidate's words in 5-grams found in no reference: page chrome, or
    text the converter made up (a table flattened into a new order also counts)."""
    ws = words(MATH.sub(" ", candidate))
    known = set().union(*(grams(words(MATH.sub(" ", r))) for r in references))
    flags = [False] * len(ws)
    for i in range(len(ws) - 4):
        if tuple(ws[i:i + 5]) not in known:
            for j in range(i, i + 5):
                flags[j] = True
    return sum(flags) / len(ws) if ws else 0.0


def counts(text):
    return {
        "chars": len(text),
        "words": len(words(text)),
        # Only dollar signs: in markdown, \[ and \( are escaped brackets (citations), not maths.
        "display_math": len(re.findall(r"\$\$.+?\$\$", text, re.S)),
        "inline_math": len(re.findall(r"(?<!\$)\$[^$\n]+?\$(?!\$)", text)),
        "headings": len(re.findall(r"^#{1,6} ", text, re.M)),
        "table_rows": len(re.findall(r"^\|.*\|\s*$", text, re.M)),
        "footnotes": len(re.findall(r"^\[\^[^\]]+\]:", text, re.M)),
        "captions": len(re.findall(r"^\**(?:Figure|Fig\.|Table) \d+", text, re.M)),
        "links": len(re.findall(r"\]\((?:https?:|#)", text)),
    }


def score():
    rows = []
    for a in chosen():
        folder = OUT / a["slug"]
        article = (folder / "article.txt").read_text(encoding="utf-8")
        base = (folder / "baseline.md").read_text(encoding="utf-8")
        for form in FORMS:
            text = (folder / ("%s.md" % form)).read_text(encoding="utf-8")
            cov_article, n_article = coverage(article, text)
            cov_base, n_base = coverage(base, text)
            rows.append(dict(article=a["slug"], kind=a["kind"], form=form, **counts(text),
                             covers_article=round(cov_article, 3), article_sentences=n_article,
                             covers_baseline=round(cov_base, 3), baseline_sentences=n_base,
                             outside=round(outside(text, article, base), 3)))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "scores.json").write_text(json.dumps(rows, indent=1) + "\n")
    cols = ["form", "words", "covers_article", "covers_baseline", "outside", "display_math", "inline_math",
            "headings", "table_rows", "footnotes", "captions", "links"]
    lines = ["# Web articles: scores", "", "Generated by `run.py score`.", ""]
    for a in chosen():
        lines += ["## %s (%s)" % (a["title"], a["kind"]), "", "| " + " | ".join(cols) + " |",
                  "|" + "---|" * len(cols)]
        lines += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows if r["article"] == a["slug"]]
        lines.append("")
    (RESULTS / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    steps = sys.argv[1:] or ["pick", "render", "convert", "score"]
    for step in steps:
        globals()[step]()
