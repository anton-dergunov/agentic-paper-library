"""Score the folders against where each paper is, and tabulate the judge's grades.

    python3 score.py <library> <results-dir>

Writes <results-dir>/folders.tsv (per paper: the folder it is in, each model's folder and
the judge's grade of each) and <results-dir>/summaries.tsv (per paper and writer: quality,
contradictions, statements beyond the abstract), and prints the totals. The judge's columns
are empty until judge.py has run.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from common import MODELS, paper

HERE = Path(__file__).parent


def near(a, b):
    """The same folder, parent and child, or siblings under one parent."""
    a, b = a.split("/"), b.split("/")
    return a[:len(b)] == b or b[:len(a)] == a or (len(a) > 1 and a[:-1] == b[:-1])


def main():
    library, results = sys.argv[1], Path(sys.argv[2])
    stems = [line.strip() for line in open(HERE / "papers.txt") if line.strip()]
    declared = {line.split(":")[0] for line in (Path(library) / "catalog/topics.yaml").read_text().splitlines()
                if line and not line.startswith("#")}
    answers = {m: {r["paper"]: r for r in map(json.loads, open(results / (m + ".jsonl")))} for m in MODELS}
    totals = {m: Counter() for m in MODELS + ["stored"]}
    folder_rows, summary_rows = [], []
    for number, relative in enumerate(stems, 1):
        label = str(Path(relative).parent)
        judged = results / "judge" / f"{number:02d}.json"
        grade = json.load(open(judged)) if judged.exists() else None
        folder_grade = {grade["folder_key"][k]: v for k, v in grade["folders"].items()} if grade else {}
        row = [number, Path(relative).name, label, folder_grade.get(label, "")]
        totals["stored"]["papers"] += 1
        totals["stored"]["judge " + folder_grade.get(label, "?")] += 1
        for m in MODELS:
            a = answers[m][relative]
            folder = str(a["folder"])
            t = totals[m]
            t["papers"] += 1
            t["exact"] += folder == label
            t["near"] += folder != label and near(folder, label)
            t["undeclared"] += folder not in declared
            t["judge " + folder_grade.get(folder, "?")] += 1
            t["input"] += a["input"]
            t["output"] += a["output"]
            t["usd"] += a["usd"] or 0
            t["seconds"] += a["seconds"]
            row += [folder, folder_grade.get(folder, "")]
        folder_rows.append(row)
        if grade:
            for letter, writer in grade["summary_key"].items():
                g = grade["summaries"][letter]
                t = totals[writer]
                t["quality"] += g["quality"]
                t["contradictions"] += len(g["contradicts"])
                t["summaries contradicting"] += bool(g["contradicts"])
                t["beyond"] += len(g["beyond"])
                text = paper(library, relative)["summary"] if writer == "stored" else answers[writer][relative]["summary"]
                t["words"] += len(text.split())
                summary_rows.append([number, writer, g["quality"], len(g["contradicts"]), len(g["beyond"]),
                                     " | ".join(g["contradicts"])])
    short = [m.replace("claude-", "") for m in MODELS]
    with open(results / "folders.tsv", "w") as out:
        out.write("\t".join(["n", "paper", "filed in", "judge"] + [c for s in short for c in (s, "judge")]) + "\n")
        out.writelines("\t".join(map(str, r)) + "\n" for r in folder_rows)
    with open(results / "summaries.tsv", "w") as out:
        out.write("n\twriter\tquality\tcontradictions\tbeyond\twhat contradicts\n")
        out.writelines("\t".join(map(str, r)) + "\n" for r in summary_rows)
    keys = ["papers", "exact", "near", "undeclared", "judge best", "judge acceptable", "judge wrong",
            "quality", "summaries contradicting", "contradictions", "beyond", "words", "input", "output", "usd", "seconds"]
    print("\t".join(["measure"] + short + ["stored"]))
    for key in keys:
        print("\t".join([key] + [str(round(totals[m][key], 2)) for m in MODELS + ["stored"]]))


if __name__ == "__main__":
    main()
