"""Summarise the question sessions: cost, time, and what each one opened.

    python3 summarize.py <out-dir> <library> [<answers-dir>]

Reads the event streams written by run.py. Prints one row per session:

- turns, seconds, input tokens processed (new, written to the cache and read from it),
  output tokens, tool calls;
- reviews whole / part: tool calls that print a file of reviews/ entire (Read without a
  range, or cat), and calls that search it or print a slice (grep, sed -n, head, Read
  with a range);
- note calls: tool calls that touch notes/ at all (a glob such as notes/Zep*.md names no
  paper, so it shows only here);
- notes and papers named: distinct papers whose note, or whose markdown, a tool call
  names (by the first 40 characters of the file name). "after review" counts only the
  calls that follow the first one touching reviews/: what the session checked once it had
  the review;
- write attempts: shell commands that open a file for writing in Python, redirect into
  notes/, reviews/, library/ or catalog/, or run sed -i or chmod. The copies are
  read-only, so these fail; the column shows that a session tried.

With <answers-dir>, also writes each final answer to <answers-dir>/<session>.md.
"""
import glob
import json
import os
import re
import sys

REVIEW = r"(?<![-\w])reviews/[^\s|;&]*"
WRITE = (r"open\([^)]*,\s*['\"][wa]|(>>?|\btee\s+(-a\s+)?)\s*[\"']?(\./)?(notes|reviews|library|catalog)/"
         r"|\bsed\s+-i|\bchmod\b")


def tool_calls(path):
    """The session's tool calls as text, and its final result event."""
    calls, result = [], None
    for line in open(path):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            result = event
        if event.get("type") != "assistant":
            continue
        for part in event["message"].get("content", []):
            if part.get("type") != "tool_use":
                continue
            given = part["input"]
            if given.get("file_path"):
                ranged = "offset" in given or "limit" in given
                calls.append(("read-part " if ranged else "read-whole ") + given["file_path"])
            else:
                calls.append(given.get("command") or "")
    return calls, result


def review_use(call):
    """How a tool call uses a review: "whole", "part" or None."""
    if not re.search(REVIEW, call):
        return None
    if call.startswith("read-"):
        return call.split("-")[1].split()[0]
    # cat of a review whose output is not piped on into head, grep and the like
    whole = re.search(r"\bcat\s+(?:[^|;&\n]*\s)?[\"']?" + REVIEW + r"[^|;&\n]*(?:$|[;&\n]|\|\|)", call, re.M)
    return "whole" if whole else "part"


def named(calls, stems):
    """The stems whose note, and whose paper, the calls name.

    A session names files in shell idioms, so this is a reading of the command, not of
    what it opened. A name is found whole (its first 40 characters) or as a quoted prefix
    before a glob ("Zep."*). It counts as the note when its path has notes/ in it, or
    when it has no library/ path and the command reads from notes (cd notes, or
    "notes/$f.md" in a loop over names); otherwise as the paper.
    """
    notes, papers = set(), set()
    for call in calls:
        moves = [(match.end(), match.group(1).strip("\"'").rstrip("/")) for match in re.finditer(r"\bcd\s+(\"[^\"]+\"|\S+)", call)]
        found = [(match.start(), stem) for stem in stems for match in re.finditer(re.escape(stem), call)]
        for match in re.finditer(r"\"([^\"*$]{8,})\"\*", call):
            found += [(match.start(), stem) for stem in stems if stem.startswith(match.group(1)[:40])]
        for start, stem in found:
            path = re.search(r"[^\s\"'=(;|&]*$", call[:start]).group(0)
            here = [folder for end, folder in moves if end <= start]
            in_notes = here[-1].endswith("notes") if here else bool(re.search(r"notes/\$", call))
            if "notes/" in path or ("library/" not in path and "/" not in path and in_notes):
                notes.add(stem)
            else:
                papers.add(stem)
    return notes, papers


def main():
    out, library = sys.argv[1], sys.argv[2]
    stems = {os.path.basename(p)[:-3][:40] for p in glob.glob(os.path.join(library, "library", "**", "*.md"), recursive=True)
             if not p.endswith("README.md")}
    print("session\tturns\tseconds\tinput\toutput\ttool calls\treviews whole\treviews part\tnote calls\tnotes named"
          "\tpapers named\tnotes after review\tpapers after review\twrite attempts")
    for path in sorted(glob.glob(os.path.join(out, "*.jsonl"))):
        name = os.path.basename(path)[:-6]
        calls, result = tool_calls(path)
        if not result or result.get("is_error"):
            print(name + "\tunfinished")
            continue
        usage = result["usage"]
        uses = [review_use(call) for call in calls]
        first = next((i for i, use in enumerate(uses) if use), None)
        notes, papers = named(calls, stems)
        after = named(calls[first + 1:], stems) if first is not None else None
        shell = [call for call in calls if not call.startswith("read-")]
        print("\t".join(str(x) for x in [
            name, result.get("num_turns"), round(result.get("duration_ms", 0) / 1000),
            usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0),
            usage.get("output_tokens"), len(calls), uses.count("whole"), uses.count("part"),
            sum(1 for call in calls if re.search(r"(?<![-\w])notes/", call)),
            len(notes), len(papers), len(after[0]) if after else "", len(after[1]) if after else "",
            sum(1 for call in shell if re.search(WRITE, call))]))
        if len(sys.argv) > 3:
            os.makedirs(sys.argv[3], exist_ok=True)
            open(os.path.join(sys.argv[3], name + ".md"), "w").write((result.get("result") or "") + "\n")


if __name__ == "__main__":
    main()
