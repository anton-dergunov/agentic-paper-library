"""Score the candidates against the notes' types.

    PAPER_LIBRARY=<library> python3 score.py

Writes results/scores.md (accuracy as sampled and reweighted to the library's mix of types,
precision and recall by type, the confusion matrices, tokens and dollars a paper) and
results/disagreements.tsv (every paper where a candidate differs from the note).
"""
from collections import Counter

from common import CANDIDATES, RESULTS, answers, paperlib, sample

TYPES = ["method", "study", "benchmark", "system", "survey", "theory", "position"]


def main():
    rows = sample()
    gold = {paperlib.paper_file_for(p).relative_to(paperlib.LIBRARY_DIR).with_suffix("").as_posix(): g
            for p, g in rows}
    library = Counter(t for t in (paperlib.note_fields(p).get("type") for p in paperlib.paper_index()) if t)
    sampled = Counter(gold.values())
    out = [f"# Scores\n\n{len(gold)} papers, {sampled.most_common(1)[0][1]} a type; the gold is the note's type. "
           f"Reweighted: each paper counts as its type's share of the {sum(library.values())} typed papers "
           f"({', '.join(f'{t} {library[t]}' for t in TYPES)}).\n"]
    by_candidate = {c: answers(c) for c in CANDIDATES}
    summary = ["| | " + " | ".join(CANDIDATES) + " |", "|---" * (len(CANDIDATES) + 1) + "|"]
    lines = {k: [] for k in ("right", "acc", "wacc", "in", "out", "usd", "sec")}
    for c in CANDIDATES:
        got = by_candidate[c]
        hits = [p for p in gold if got.get(p, {}).get("type") == gold[p]]
        weight = {t: library[t] / sum(library.values()) / sampled[t] for t in sampled}
        n = len([p for p in gold if p in got])
        lines["right"].append(f"{len(hits)} of {n}")
        lines["acc"].append(f"{len(hits) / n:.0%}")
        lines["wacc"].append(f"{sum(weight[gold[p]] for p in hits) / sum(weight[gold[p]] for p in gold if p in got):.1%}")
        mean = lambda key: sum(r.get(key) or 0 for r in got.values()) / max(1, len(got))
        lines["in"].append(f"{mean('input') / 1000:.1f}K")
        lines["out"].append(f"{mean('output'):.0f}")
        lines["usd"].append(f"${mean('usd'):.4f}")
        lines["sec"].append(f"{mean('seconds'):.1f}")
    names = {"right": "Agrees with the note", "acc": "Accuracy as sampled", "wacc": "Accuracy, library's mix",
             "in": "Input tokens a paper", "out": "Output tokens a paper", "usd": "Dollars a paper",
             "sec": "Seconds a paper"}
    summary += [f"| {names[k]} | " + " | ".join(v) + " |" for k, v in lines.items()]
    out.append("\n".join(summary) + "\n")
    for c in CANDIDATES:
        got = by_candidate[c]
        out.append(f"## {c}\n\n| note \\ answer | " + " | ".join(TYPES) + " | none | recall |\n"
                   + "|---" * (len(TYPES) + 3) + "|")
        for t in TYPES:
            answered = Counter(got[p]["type"] or "none" for p in gold if gold[p] == t and p in got)
            out.append(f"| **{t}** | " + " | ".join(str(answered[u] or "·") for u in TYPES + ["none"])
                       + f" | {answered[t] / max(1, sum(answered.values())):.0%} |")
        precision = []
        for t in TYPES:
            said = [p for p in gold if got.get(p, {}).get("type") == t]
            precision.append(f"{sum(gold[p] == t for p in said) / len(said):.0%}" if said else "–")
        out.append("| precision | " + " | ".join(precision) + " | | |\n")
    (RESULTS / "scores.md").write_text("\n".join(out), encoding="utf-8")
    with open(RESULTS / "disagreements.tsv", "w", encoding="utf-8") as tsv:
        tsv.write("paper\tnote\t" + "\t".join(CANDIDATES) + "\n")
        for p in gold:
            said = [by_candidate[c].get(p, {}).get("type") or "" for c in CANDIDATES]
            if any(s != gold[p] for s in said):
                tsv.write(f"{p}\t{gold[p]}\t" + "\t".join(said) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
