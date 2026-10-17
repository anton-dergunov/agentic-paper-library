"""Words each reconverted paper lost or gained against git HEAD, marks, link targets and
titles aside, and its change in characters: run in the library, words.py <paper.md> ...

    git diff --name-only -- library | grep '\\.md$' | tr '\\n' '\\0' | xargs -0 python3 words.py > words.tsv
"""
import re, sys, subprocess, collections
def words(t):
    t = re.sub(r"</?mark\b[^>]*>", "", t)
    t = re.sub(r"\]\([^)\s]*(?:\s+\"[^\"]*\")?\)", "]", t)
    t = re.sub(r'href="[^"]*"|title="[^"]*"', "", t)
    return collections.Counter(re.findall(r"\w+", t))
print("paper\tchars_old\tchars_new\tlost\tgained\tlost_words\tgained_words")
for f in sys.argv[1:]:
    old = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
    new = open(f, encoding="utf-8").read()
    a, b = words(old), words(new)
    lost, gained = a - b, b - a
    print("\t".join(map(str, [f.rsplit("/", 1)[-1][:-3], len(old), len(new), sum(lost.values()), sum(gained.values()),
                              " ".join(list(lost)[:12]), " ".join(list(gained)[:12])])))
