"""Grade each session against the rules its task exercises, from its event stream.

    python3 check.py <scratch>

Reads results/sessions/<condition>-<task>.jsonl and the files the session wrote in its copy
(<scratch>/copies/lib-<condition>) and overview folder, and prints one row per check:
condition, task, check, pass/FAIL. Then the tokens per session: input processed (uncached,
written to and read from the cache), output, turns, seconds and the API price `claude -p`
reports. Writes the same to results/sessions.tsv and the final answers to
results/answers/<condition>-<task>.md.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GPT1 = "Improving Language Understanding by Generative Pre-Training"
METHOD_SECTIONS = ["Setting", "Motivation", "Method", "Why it works", "Applications and results",
                   "Evidence", "Novelty", "Concepts"]
FRONTMATTER = ["title", "aliases", "authors", "affiliations", "year", "type", "topic", "links",
               "concepts", "papers", "tags", "read", "analyzed", "queued", "revisit", "reproduce"]


def events(path):
    for line in path.read_text().splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            continue


def session(path):
    """(tool calls as (name, input text), tool results text, final result event)."""
    calls, results, final = [], [], {}
    for event in events(path):
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append((block["name"], json.dumps(block["input"], ensure_ascii=False)))
        elif event.get("type") == "user":
            for block in event["message"].get("content", []) if isinstance(event["message"].get("content"), list) else []:
                if block.get("type") == "tool_result":
                    content = block.get("content")
                    results.append(json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content)
        elif event.get("type") == "result":
            final = event
    return calls, results, final


def ran(calls, pattern):
    return any(re.search(pattern, text) for _, text in calls)


def checks_qa(calls, results, answer, copy, scratch, condition):
    return {
        "read Zep's note": ran(calls, r"notes/Zep"),
        "did not open a PDF": not any(name == "Read" and ".pdf" in text for name, text in calls),
        "cites a page (p. N)": bool(re.search(r"p\. ?\d", answer)),
        "pdf.invalid link with page=": bool(re.search(r"\]\(http://pdf\.invalid/[^)\s]+\.pdf\?[^)\s]*page=\d", answer)),
        "gives 71.2% against 60.2% full context (gpt-4o)": "71.2" in answer and "60.2" in answer,
    }


def checks_overview(calls, results, answer, copy, scratch, condition):
    path = scratch / f"overview-{condition}" / f"{GPT1}.md"
    note = path.read_text() if path.exists() else ""
    head, _, body = note.partition("\n---\n")
    keys = re.findall(r"^(\w+):", head, re.M)
    memory = (copy / "notes" / f"{GPT1}.md").read_text()
    return {
        "note written to overview_dir": bool(note),
        "frontmatter keys in order": [k for k in keys if k in FRONTMATTER] == [k for k in FRONTMATTER if k in keys],
        "checkboxes all false": all(f"{k}: false" in head for k in ("read", "analyzed", "queued", "revisit", "reproduce")),
        "abstract callout": "> [!abstract]" in body,
        "Overview, Questions, Follow-ups": all(f"## {s}" in body for s in ("Overview", "Questions", "Follow-ups")),
        "method subsections in order": [s for s in METHOD_SECTIONS if f"### {s}" in body] == METHOD_SECTIONS,
        "no page references in the note": not re.search(r"\(p\. ?\d|\bp\. ?\d", body),
        "set-type run": ran(calls, r"paperlib set-type"),
        "notes/ file keeps Digest and Q&A": "## Digest" in memory and "## Q&A" in memory,
        "report starts with the link": answer.strip().startswith("I've written the overview note"),
        "no build-index, check or git status": not ran(calls, r"paperlib (build-index|check)|git status"),
    }


def checks_add(calls, results, answer, copy, scratch, condition):
    added = list((copy / "library").rglob("MemOS*.md"))
    meta = added[0].read_text().split("---")[1] if added else ""
    return {
        "lookup run": ran(calls, r"paperlib lookup"),
        "topics.yaml read": ran(calls, r"topics\.yaml"),
        "add-arxiv run": ran(calls, r"paperlib add-arxiv"),
        "paper added": bool(added),
        "summary set with set-summary": ran(calls, r"paperlib set-summary") and bool(re.search(r"^summary: \S", meta, re.M)),
        "build-index then check": ran(calls, r"paperlib build-index") and ran(calls, r"paperlib check"),
        "no git commit": not ran(calls, r"git commit"),
        "suggests a commit message": "commit" in answer.lower(),
        "filed in": str(added[0].parent.relative_to(copy / "library")) if added else "-",
    }


CHECKS = {"qa": checks_qa, "overview": checks_overview, "add": checks_add}


def main(argv):
    if len(argv) != 1:
        sys.exit(__doc__)
    scratch = Path(argv[0])
    rows, usage = [], []
    answers = HERE / "results" / "answers"
    answers.mkdir(exist_ok=True)
    for path in sorted((HERE / "results" / "sessions").glob("*.jsonl")):
        condition, task = path.stem.split("-", 1)
        calls, results, final = session(path)
        answer = final.get("result") or ""
        (answers / f"{path.stem}.md").write_text(answer.replace(str(scratch), "<scratch>") + "\n")
        copy = scratch / "copies" / f"lib-{condition}"
        for name, value in CHECKS[task](calls, results, answer, copy, scratch, condition).items():
            shown = value if isinstance(value, str) else ("pass" if value else "FAIL")
            rows.append(f"{task}\t{condition}\t{name}\t{shown}")
        u = final.get("usage", {})
        processed = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        usage.append(f"{task}\t{condition}\t{processed}\t{u.get('cache_creation_input_tokens', 0)}\t"
                     f"{u.get('cache_read_input_tokens', 0)}\t{u.get('output_tokens', 0)}\t{final.get('num_turns')}\t"
                     f"{round((final.get('duration_ms') or 0) / 1000)}\t{final.get('total_cost_usd', 0):.2f}\t{len(calls)}")
    text = ("task\tcondition\tcheck\tresult\n" + "\n".join(sorted(rows)) +
            "\n\ntask\tcondition\tinput processed\tcache write\tcache read\toutput\tturns\tseconds\tusd\ttool calls\n"
            + "\n".join(sorted(usage)) + "\n")
    (HERE / "results" / "sessions.tsv").write_text(text)
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
