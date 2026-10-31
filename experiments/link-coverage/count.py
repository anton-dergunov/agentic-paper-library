"""Counts, for each answer a run kept, the page citations it makes and how many are links.

A page citation is "p. 7", "pp. 8–10" or "page 7" outside code. It is linked when it is in a
link's text to a `pdf.invalid` URL, and beside a link when one is right before or after it. Also counted: links, links with `rect`, `paperlib locate`
calls, output tokens, cost and seconds, from the session's stream.

    python count.py <runs dir> [--plain] [--export <dir>]   # one row per answer, then totals per run
    --plain also prints each plain citation with the words around it; --export writes each
    answer's text to <dir>/<run>/<question>.md, with the scratch library's path cut off.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

LINK = re.compile(r"\[((?:[^\[\]\n]|\[[^\]\n]*\])*)\]\((http://pdf\.invalid[^)\s]*)\)")
CITE = re.compile(r"\b(?:pp?\.|pages?)\s?\d+(?:\s?[–-]\s?\d+)?", re.IGNORECASE)
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)


def session(path):
    """The answer's text (every assistant text block, in order), the locate calls and the
    result message of a stream-json file."""
    texts, locates, result = [], 0, {}
    for line in path.read_text().splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "assistant":
            for block in msg["message"].get("content", []):
                if block.get("type") == "text":
                    texts.append(block["text"])
                elif block.get("type") == "tool_use":
                    locates += "paperlib locate" in json.dumps(block.get("input", {}))
        elif msg.get("type") == "result":
            result = msg
    return "\n\n".join(texts), locates, result


def citations(text):
    """Linked and plain page citations, the links, and those with rect."""
    text = CODE.sub("", text)
    links = LINK.findall(text)
    linked = sum(len(CITE.findall(label)) for label, _ in links)
    # A citation in plain text right beside a link is covered: "p. 5–6** ([p. 5](…)", or a
    # quote as the link and its page after it, "[quoted words](…) (p. 14)".
    rest = LINK.sub("\x00", text)
    plain, beside = [], 0
    for m in CITE.finditer(rest):
        if re.match(r"[\s*:,(]{0,6}\x00", rest[m.end() :]) or re.search(r"\x00[\s*(]{0,3}$", rest[: m.start()]):
            beside += 1
        else:
            plain.append(rest[max(0, m.start() - 70) : m.end() + 15].replace("\n", " ").replace("\x00", "[L]"))
    return linked, beside, plain, links


def main():
    runs, show = Path(sys.argv[1]), "--plain" in sys.argv
    export = Path(sys.argv[sys.argv.index("--export") + 1]) if "--export" in sys.argv else None
    totals = defaultdict(lambda: defaultdict(float))
    print("run\tquestion\tcited\tlinked\tbeside\tplain\tlinks\trect\tlocate\tout_tok\tcost\tsec")
    for path in sorted(runs.glob("*/*.jsonl")):
        text, locates, result = session(path)
        linked, beside, plain, links = citations(text)
        if export:
            (export / path.parent.name).mkdir(parents=True, exist_ok=True)
            cut = re.sub(r"/(?:private/)?(?:tmp|var|Users)/[^\s)`'\"]*?/lib-[\w-]+/", "", text)
            (export / path.parent.name / f"{path.stem}.md").write_text(cut + "\n")
        rect = sum("rect=" in url for _, url in links)
        out = result.get("usage", {}).get("output_tokens", 0)
        row = dict(cited=linked + beside + len(plain), linked=linked, beside=beside, plain=len(plain), links=len(links),
                   rect=rect, locate=locates, out_tok=out, cost=result.get("total_cost_usd", 0),
                   sec=result.get("duration_ms", 0) / 1000, answers=1)
        print(path.parent.name, path.stem, *(f"{row[k]:g}" if isinstance(row[k], int) else f"{row[k]:.3f}"
              for k in ("cited", "linked", "beside", "plain", "links", "rect", "locate", "out_tok", "cost", "sec")), sep="\t")
        if show:
            for p in plain:
                print("\t  plain:", p)
        for k, v in row.items():
            totals[path.parent.name][k] += v
    print("\nrun\tanswers\tcited\tlinked\tbeside\tplain\tcoverage\tlinks\trect\tlocate\tout_tok\tcost\tsec")
    for name, t in sorted(totals.items()):
        cov = (t["linked"] + t["beside"]) / t["cited"] if t["cited"] else 0
        print(name, int(t["answers"]), int(t["cited"]), int(t["linked"]), int(t["beside"]), int(t["plain"]), f"{cov:.0%}",
              int(t["links"]), int(t["rect"]), int(t["locate"]), int(t["out_tok"]), f"{t['cost']:.2f}",
              f"{t['sec']:.0f}", sep="\t")


if __name__ == "__main__":
    main()
