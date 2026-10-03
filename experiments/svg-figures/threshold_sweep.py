"""Size of keeping SVG figures as SVG versus rasterizing those over a threshold.

    python3 threshold_sweep.py <scripts dir> <svgs dir> [<figures to project to>]

<scripts dir> holds paperlib.py (to_webp: WebP at quality 85, at most 1600 px).
Each SVG is rasterized with rsvg-convert at 1600 px wide on white and encoded as
WebP. "git" approximates the repository cost by zlib level 9 for an SVG (git
compresses text) and the WebP's own size. Projects to 10,016 figures by default,
the count found by scan_objects.py. Needs librsvg (`brew install librsvg`).
"""
import glob, subprocess, sys, time, zlib
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from paperlib import to_webp
TOTAL = int(sys.argv[3]) if len(sys.argv) > 3 else 10016
t = time.time()
rows = []
for f in sorted(glob.glob(str(Path(sys.argv[2]) / "*.svg"))):
    d = open(f, "rb").read()
    png = subprocess.run(["rsvg-convert", "-w", "1600", "--keep-aspect-ratio", "-b", "white", f],
                         capture_output=True).stdout
    rows.append((len(d), len(zlib.compress(d, 9)), len(to_webp(png))))
n = len(rows)
print(f"{n} files: svg {sum(r[0] for r in rows)/n/1024:.0f}KB, zlib {sum(r[1] for r in rows)/n/1024:.0f}KB, "
      f"webp {sum(r[2] for r in rows)/n/1024:.0f}KB, {time.time()-t:.0f}s")
for th in (10**9, 500e3, 300e3, 200e3, 100e3):
    disk = sum(r[0] if r[0] <= th else r[2] for r in rows) / n
    git = sum(r[1] if r[0] <= th else r[2] for r in rows) / n
    k = sum(r[0] > th for r in rows)
    print(f"threshold {th/1e3:>7.0f}KB: rasterized {k:2d}/{n}; per figure disk {disk/1024:4.0f}KB git {git/1024:3.0f}KB"
          f" -> {TOTAL} figs disk {disk*TOTAL/2**30:.2f}GB git {git*TOTAL/2**20:.0f}MB")
