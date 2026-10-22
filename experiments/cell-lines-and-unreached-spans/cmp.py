"""cmp.py <old outdir> <new outdir>: characters, HTML tables and line breaks of the papers two
converters wrote (runeng.sh), in all and for the papers that changed most."""
import sys, re
from pathlib import Path
tok = len
old, new = Path(sys.argv[1]), Path(sys.argv[2])
T = [0, 0]; H = [0, 0]; B = [0, 0]; changed = []; missing = []
for d in sorted(old.iterdir()):
    a, b = d / "body.md", new / d.name / "body.md"
    if not a.exists() or not b.exists():
        missing.append(d.name); continue
    x, y = a.read_text(), b.read_text()
    T[0] += tok(x); T[1] += tok(y)
    H[0] += x.count("<table>"); H[1] += y.count("<table>")
    B[0] += len(re.findall(r"<br ?/?>", x)); B[1] += len(re.findall(r"<br ?/?>", y))
    if x != y: changed.append((d.name, tok(y) - tok(x), y.count("<table>") - x.count("<table>")))
print("papers", len(list(old.iterdir())), "missing", missing)
print("characters", T, f"{(T[1]-T[0])/T[0]*100:+.2f}%", "html tables", H, "br", B, "changed papers", len(changed))
for c in sorted(changed, key=lambda c: c[1])[:8] + sorted(changed, key=lambda c: c[1])[-8:]: print(c)
