"""Token use of literature-review runs, from Claude Code session transcripts.

    python3 measure.py <transcripts-dir> <name>=<session-id-prefix> ...

<transcripts-dir> is the project's folder under ~/.claude/projects/. A session is
<id>.jsonl, and its subagents are <id>/subagents/agent-*.jsonl. Usage is repeated on
every line of a message, so it is counted once per message id. Requests answered by the
harness itself (model "<synthetic>", e.g. the session-limit notice) are left out.

"Cost-eq" weights tokens by API price ratios: input 1, cache read 0.1, 5-minute cache
write 1.25, 1-hour cache write 2, output 5. Logged output tokens are unreliable for
subagents, so output is estimated from the length of the text and tool input (3.6
characters a token); thinking is not in the transcript and is not counted.
"""
import datetime
import glob
import json
import os
import sys

CHARS_PER_TOKEN = 3.6


def when(stamp):
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def requests(path):
    """One record per model request, in order."""
    by_id, order = {}, []
    for line in open(path):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        message = row.get("message") or {}
        if row.get("type") != "assistant" or message.get("model") == "<synthetic>":
            continue
        key = message.get("id") or row.get("uuid")
        if key not in by_id:
            by_id[key] = {"at": row["timestamp"], "chars": 0, "usage": {}, "tools": []}
            order.append(key)
        request = by_id[key]
        request["usage"] = message.get("usage") or request["usage"]
        for part in message.get("content") or []:
            if part.get("type") == "tool_use":
                request["chars"] += len(json.dumps(part["input"], ensure_ascii=False))
                request["tools"].append(part["name"])
            elif part.get("type") == "text":
                request["chars"] += len(part.get("text", ""))
    return [by_id[key] for key in order]


def totals(reqs, cache_life, write_weight):
    """Sum a transcript. Writes after a pause longer than the cache's life are re-caching."""
    out = {"requests": len(reqs), "write": 0, "read": 0, "recache": 0, "output": 0,
           "max_context": 0, "tools": 0}
    previous = None
    for request in reqs:
        usage = request["usage"]
        write = usage.get("cache_creation_input_tokens", 0) or 0
        read = usage.get("cache_read_input_tokens", 0) or 0
        context = write + read + (usage.get("input_tokens", 0) or 0)
        out["write"] += write
        out["read"] += read
        out["output"] += request["chars"] / CHARS_PER_TOKEN
        out["max_context"] = max(out["max_context"], context)
        out["tools"] += len(request["tools"])
        if previous and (when(request["at"]) - when(previous)).total_seconds() > cache_life:
            out["recache"] += write
        previous = request["at"]
    out["cost"] = out["write"] * write_weight + out["read"] * 0.1 + out["output"] * 5
    return out


def millions(n):
    return "%.2fM" % (n / 1e6)


def main():
    folder = sys.argv[1]
    print("run\tagents\tagent write\tagent read\tagent output (est.)\tagent re-cache after a pause"
          "\tagent cost-eq\tmean largest agent context\trequests per agent"
          "\tmain write\tmain read\tmain re-cache after a pause\tmain cost-eq")
    detail = []
    for pair in sys.argv[2:]:
        name, prefix = pair.split("=")
        session = glob.glob(os.path.join(folder, prefix + "*.jsonl"))[0]
        agents = []
        for path in sorted(glob.glob(session[:-6] + "/subagents/agent-*.jsonl")):
            # Subagents cache for 5 minutes at 1.25x.
            agents.append(totals(requests(path), 300, 1.25))
        # The main session caches for an hour at 2x.
        main_session = totals(requests(session), 3600, 2)
        total = {key: sum(agent[key] for agent in agents) for key in agents[0]}
        print("\t".join([
            name, str(len(agents)), millions(total["write"]), millions(total["read"]),
            millions(total["output"]), millions(total["recache"]), millions(total["cost"]),
            "%dK" % (total["max_context"] / len(agents) / 1e3),
            "%d" % (total["requests"] / len(agents)),
            millions(main_session["write"]), millions(main_session["read"]),
            millions(main_session["recache"]), millions(main_session["cost"])]))
        for number, agent in enumerate(agents, 1):
            detail.append("\t".join([
                name, str(number), str(agent["requests"]), str(agent["tools"]),
                "%dK" % (agent["write"] / 1e3), millions(agent["read"]),
                "%dK" % (agent["max_context"] / 1e3), "%dK" % (agent["recache"] / 1e3),
                millions(agent["cost"])]))
    print("\nrun\tagent\trequests\ttool calls\twrite\tread\tlargest context\tre-cache\tcost-eq")
    print("\n".join(detail))


if __name__ == "__main__":
    main()
