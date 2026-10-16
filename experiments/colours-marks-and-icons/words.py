"""Words a reconverted paper lost or gained against git HEAD, link targets and titles aside: words.py <paper.md>."""
import re, sys, subprocess, collections
f = sys.argv[1]
old = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
new = open(f).read()
def w(t):
    t = re.sub(r"\]\([^)\s]*(?:\s+\"[^\"]*\")?\)", "]", t)
    t = re.sub(r'href="[^"]*"|title="[^"]*"', "", t)
    return collections.Counter(re.findall(r"\w+", t))
a, b = w(old), w(new)
print("lost:", sum((a - b).values()), list((a - b).items())[:15])
print("gained:", sum((b - a).values()), list((b - a).items())[:15])
