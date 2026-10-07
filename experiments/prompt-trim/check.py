"""Grade each session against the rules its task exercises, from its event stream.

    python3 check.py [<work>]

Reads results/sessions/<condition>-<task>-r<n>.jsonl and what the run left in
results/artifacts/<condition>-<task>-r<n>/ (see sessions.py), and prints one row per check:
task, condition and run, check, pass/FAIL or a value. Then the tokens per session: input
processed (uncached, written to and read from the cache), output, turns, seconds and the API
price `claude -p` reports. Writes the same to results/sessions.tsv and the final answers to
results/answers/<condition>-<task>-r<n>.md, with <work> replaced by "<work>".
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
REVIEW_SCOPE = "experimentation-and-metrics/variance-reduction"


def events(path):
    for line in path.read_text().splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            continue


def session(path):
    """(tool calls as (name, input), final result event)."""
    calls, final = [], {}
    for event in events(path):
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append((block["name"], block["input"]))
        elif event.get("type") == "result":
            final = event
    return calls, final


def ran(calls, pattern):
    return any(re.search(pattern, json.dumps(given, ensure_ascii=False)) for _, given in calls)


def read_text(path):
    return path.read_text() if path.exists() else ""


def changes(art):
    return [line for line in read_text(art / "changes.txt").splitlines() if line.strip()]


def links_with_pages(answer):
    return bool(re.search(r"\]\(http://pdf\.invalid/[^)\s]+\.pdf\?[^)\s]*page=\d", answer))


def checks_qa(calls, answer, art):
    return {
        "read Zep's note": ran(calls, r"notes/Zep"),
        "did not open a PDF": not any(name == "Read" and ".pdf" in json.dumps(given) for name, given in calls),
        "cites a page (p. N)": bool(re.search(r"p\. ?\d", answer)),
        "pdf.invalid link with page=": links_with_pages(answer),
        "gives 71.2% against 60.2% full context (gpt-4o)": "71.2" in answer and "60.2" in answer,
    }


def checks_overview(calls, answer, art):
    note = read_text(art / "overview.md")
    head, _, body = note.partition("\n---\n")
    keys = re.findall(r"^(\w+):", head, re.M)
    memory = read_text(art / "memory.md")
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


def checks_add(calls, answer, art):
    added = json.loads(read_text(art / "added.json") or "[]")
    return {
        "lookup run": ran(calls, r"paperlib lookup"),
        "topics.yaml read": ran(calls, r"topics\.yaml"),
        "add-arxiv run": ran(calls, r"paperlib add-arxiv"),
        "paper added": bool(added),
        "summary set with set-summary": ran(calls, r"paperlib set-summary")
        and any(re.search(r"^summary: \S", a["frontmatter"], re.M) for a in added),
        "build-index then check": ran(calls, r"paperlib build-index") and ran(calls, r"paperlib check"),
        "no git commit": not ran(calls, r"git commit"),
        "suggests a commit message": "commit" in answer.lower(),
        "filed in": str(Path(added[0]["path"]).parent) if added else "-",
    }


def checks_synthesis(calls, answer, art):
    whole = any((name == "Read" and "reviews/" in given.get("file_path", "") and not given.get("limit"))
                or (name == "Bash" and re.search(r"\bcat\b[^|;]*reviews/", given.get("command", "")))
                for name, given in calls)
    return {
        "searched a review (grep)": any("reviews/" in json.dumps(given) and
                                        (name == "Grep" or re.search(r"\bgrep\b", given.get("command", "")))
                                        for name, given in calls),
        "did not read a review whole": not whole,
        "checked notes or papers": ran(calls, r"\bnotes\b|library/llm/"),
        "pdf.invalid links with page=": links_with_pages(answer),
        "files changed": ", ".join(changes(art)) or "none",
    }


def checks_reorganize(calls, answer, art):
    return {
        "topics.yaml read": ran(calls, r"topics\.yaml"),
        "folder index or papers read": ran(calls, r"text-analytics"),
        "numbered proposal": bool(re.search(r"^\s*(\*\*)?1[.)]", answer, re.M)),
        "nothing moved before approval": not ran(calls, r"paperlib move|\bmv\b") and not changes(art),
    }


def checks_reviewstatus(calls, answer, art):
    return {
        "review-status run": ran(calls, r"paperlib review-status"),
        "no reading or writing": not ran(calls, r"paperlib read\b") and not changes(art),
    }


def checks_reviewread(calls, answer, art):
    notes = list(art.glob("note-*.md"))
    reads = [json.loads(line) for line in read_text(art / "reads.jsonl").splitlines() if line.strip()]
    return {
        "review-status run": ran(calls, r"paperlib review-status"),
        "focus written": (art / "focus.md").exists(),
        "paperlib read with --focus and --limit 1": ran(calls, r"paperlib read [^\"]*--focus") and ran(calls, r"--limit 1\b"),
        "exactly one new note": len(notes) == 1,
        "stopped before writing a review": not any(c.startswith(f"reviews/{REVIEW_SCOPE}") for c in changes(art)),
        "inner read: input tokens, USD": ", ".join(f"{r['input']}, ${r['usd']:.3f}" for r in reads) or "-",
    }


CHECKS = {"qa": checks_qa, "overview": checks_overview, "add": checks_add, "synthesis": checks_synthesis,
          "reorganize": checks_reorganize, "reviewstatus": checks_reviewstatus, "reviewread": checks_reviewread}


def main(argv):
    work = Path(argv[0]).expanduser() if argv else None
    rows, usage = [], []
    answers = HERE / "results" / "answers"
    answers.mkdir(exist_ok=True)
    for path in sorted((HERE / "results" / "sessions").glob("*.jsonl")):
        condition, task, run = path.stem.split("-")
        calls, final = session(path)
        if final.get("subtype") != "success":
            continue
        answer = final.get("result") or ""
        shown = answer.replace(str(work), "<work>") if work else answer
        shown = re.sub(r"/private/tmp/claude-[^\s)]*?/scratchpad", "<scratch>", shown).replace(str(Path.home()), "~")
        (answers / f"{path.stem}.md").write_text(shown + "\n")
        art = HERE / "results" / "artifacts" / path.stem
        for name, value in CHECKS[task](calls, answer, art).items():
            value = value if isinstance(value, str) else ("pass" if value else "FAIL")
            rows.append(f"{task}\t{condition} {run}\t{name}\t{value}")
        u = final.get("usage", {})
        processed = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        usage.append(f"{task}\t{condition} {run}\t{processed}\t{u.get('cache_creation_input_tokens', 0)}\t"
                     f"{u.get('cache_read_input_tokens', 0)}\t{u.get('output_tokens', 0)}\t{final.get('num_turns')}\t"
                     f"{round((final.get('duration_ms') or 0) / 1000)}\t{final.get('total_cost_usd', 0):.2f}\t{len(calls)}")
    text = ("task\trun\tcheck\tresult\n" + "\n".join(sorted(rows)) +
            "\n\ntask\trun\tinput processed\tcache write\tcache read\toutput\tturns\tseconds\tusd\ttool calls\n"
            + "\n".join(sorted(usage)) + "\n")
    (HERE / "results" / "sessions.tsv").write_text(text)
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
