"""Summarise the question sessions: cost, time, and what each one opened.

    python3 summarize.py <out-dir> <library> [<answers-dir>]

Reads the event streams written by run.py. Prints one row per session: turns, seconds,
tokens written to and read from the cache, output tokens, the API price, whether its
tool calls read a file in reviews/ or in notes/, and how many distinct papers they name (a paper
counts when the first 40 characters of its file name appear in a tool call, whether the
call opened the paper or its note). With <answers-dir>, also writes each final answer to
<answers-dir>/<condition>-<question>.md.
"""
import glob
import json
import os
import re
import sys


def main():
    out, library = sys.argv[1], sys.argv[2]
    stems = {os.path.basename(p)[:-3][:40] for p in glob.glob(os.path.join(library, "library", "**", "*.md"), recursive=True)
             if not p.endswith("README.md")}
    print("session\tturns\tseconds\tcache write\tcache read\toutput\tusd\ttool calls\treviews\tnotes\tpapers named")
    for path in sorted(glob.glob(os.path.join(out, "*.jsonl"))):
        name = os.path.basename(path)[:-6]
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
                if part.get("type") == "tool_use":
                    calls.append(part["input"].get("file_path") or part["input"].get("command") or "")
        if not result:
            print(name + "\tunfinished")
            continue
        text = "\n".join(calls)
        usage = result["usage"]
        print("\t".join(str(x) for x in [
            name, result.get("num_turns"), round(result.get("duration_ms", 0) / 1000),
            usage.get("cache_creation_input_tokens"), usage.get("cache_read_input_tokens"),
            usage.get("output_tokens"), "%.2f" % result.get("total_cost_usd", 0), len(calls),
            "yes" if re.search(r"reviews/\S+\.md", text) else "no",
            "yes" if re.search(r"(?<![-\w])notes/|/notes &&", text) else "no",
            sum(1 for stem in stems if stem in text)]))
        if len(sys.argv) > 3:
            os.makedirs(sys.argv[3], exist_ok=True)
            open(os.path.join(sys.argv[3], name + ".md"), "w").write((result.get("result") or "") + "\n")


if __name__ == "__main__":
    main()
