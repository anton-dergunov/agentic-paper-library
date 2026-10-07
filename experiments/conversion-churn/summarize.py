"""Summaries of changes.tsv: per commit, and for the papers that had been read.

    python3 summarize.py changes.tsv notes-born.tsv

Writes passes.tsv (one row per commit that changed paper bodies), after-reading.txt (the
changes to papers that already had a note, before and after the converter settled) and
passes.png (the share of the body changed, per commit). Needs matplotlib.
"""

import csv
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SETTLED = "2026-10-03"  # the day after the library-wide reconversion was merged
OUT = Path(__file__).parent

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
for r in rows:
    for k in ("commit_index", "body_chars", "changed_lines", "changed_chars", "note_before"):
        r[k] = int(r[k])
    r["share"] = r["changed_chars"] / max(r["body_chars"], 1)
read_ever = sum(1 for _ in open(sys.argv[2]))


def pct(values, q):
    """The nearest-rank percentile."""
    values = sorted(values)
    return values[max(0, math.ceil(q * len(values)) - 1)]


# Per commit.
by_commit = defaultdict(list)
for r in rows:
    by_commit[(r["commit_index"], r["date"], r["sha"], r["subject"])].append(r)
passes = []
with open(OUT / "passes.tsv", "w") as f:
    f.write("date\tsha\tsubject\tpapers_changed\tof_them_read\tshare_median\tshare_p90\tshare_max\n")
    for (i, date, sha, subject), rs in sorted(by_commit.items()):
        shares = [r["share"] for r in rs]
        row = (date, sha, subject, len(rs), sum(r["note_before"] for r in rs),
               st.median(shares), pct(shares, 0.9), max(shares))
        passes.append(row)
        f.write("\t".join(str(x) if not isinstance(x, float) else f"{x:.5f}" for x in row) + "\n")

# Papers that had been read.
lines = []
after = [r for r in rows if r["note_before"]]
per_paper = defaultdict(int)
for r in after:
    per_paper[r["paper"]] += 1
counts = list(per_paper.values())
lines.append(f"Papers ever read (a note was added): {read_ever}")
lines.append(f"Papers whose body changed after their note was added: {len(per_paper)} "
             f"({100 * len(per_paper) / read_ever:.0f}%)")
lines.append(f"Times changed after reading: mean {st.mean(counts):.2f}, max {max(counts)}; "
             + ", ".join(f"{k}x: {counts.count(k)}" for k in sorted(set(counts))))
for label, keep in [(f"before {SETTLED}", lambda d: d < SETTLED), (f"from {SETTLED}", lambda d: d >= SETTLED)]:
    part = [r for r in after if keep(r["date"])]
    if not part:
        continue
    cl, cc, sh = [r["changed_lines"] for r in part], [r["changed_chars"] for r in part], [r["share"] for r in part]
    lines.append(
        f"Changes {label}: {len(part)} to {len({r['paper'] for r in part})} papers; "
        f"lines median {st.median(cl):g}, max {max(cl)}; characters median {st.median(cc):g}, "
        f"mean {st.mean(cc):.0f}, max {max(cc)}; share of the body median {100 * st.median(sh):.2f}%, "
        f"90th percentile {100 * pct(sh, 0.9):.2f}%, max {100 * max(sh):.1f}%; over 1%: {sum(s > 0.01 for s in sh)}")
lines.append("Largest changes after reading (share of the body):")
for r in sorted(after, key=lambda r: -r["share"])[:10]:
    lines.append(f"  {100 * r['share']:6.1f}%  {r['changed_chars']:7} chars  {r['changed_lines']:4} lines  "
                 f"{r['date']}  {r['paper'][:60]}")
(OUT / "after-reading.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# The chart: per commit, median and 90th percentile of the share changed, log scale.
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"
MEDIAN, P90 = "#2a78d6", "#eb6834"
FLOOR = 1e-4  # 0.01%: a smaller share is drawn at the floor
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "text.color": INK,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK})
fig, ax = plt.subplots(figsize=(9, 0.38 * len(passes) + 1.4), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
for y, (date, sha, subject, n, n_read, med, p90, mx) in enumerate(reversed(passes)):
    lo, hi = max(med, FLOOR), max(p90, FLOOR)
    ax.plot([lo, hi], [y, y], color=GRID, linewidth=2, zorder=1, solid_capstyle="round")
    ax.scatter([lo], [y], s=42, color=MEDIAN, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    ax.scatter([hi], [y], s=42, color=P90, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    if n_read:
        ax.text(1.02, y, f"{n_read}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=8, color=INK2)
ax.set_yticks(range(len(passes)))
def short(text, width=48):
    return text if len(text) <= width else text[:width].rsplit(" ", 1)[0] + "…"


ax.set_yticklabels([f"{p[0]}  {short(p[2])}  ({p[3]})" for p in reversed(passes)], fontsize=8)
ax.text(1.02, len(passes) - 0.3, "read", transform=ax.get_yaxis_transform(), va="bottom",
        fontsize=8, color=INK2, fontweight="bold")
ax.set_xscale("log")
ax.set_xlim(FLOOR * 0.7, 4)
ax.set_xticks([1e-4, 1e-3, 1e-2, 1e-1, 1])
ax.set_xticklabels(["≤0.01%", "0.1%", "1%", "10%", "100%"])
ax.set_xlabel("Share of a paper's body changed (characters, edit distance)")
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="y", length=0)
ax.scatter([], [], s=42, color=MEDIAN, label="median paper")
ax.scatter([], [], s=42, color=P90, label="90th percentile")
fig.legend(loc="upper left", bbox_to_anchor=(0.01, 0.94), ncol=2, frameon=False, fontsize=8)
fig.suptitle("How much of a paper each commit changed (papers changed in brackets;\n"
             "at right, how many of them had a note, i.e. had been read)",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(rect=(0, 0, 0.97, 0.92))
fig.savefig(OUT / "passes.png", dpi=150, facecolor=SURFACE)
