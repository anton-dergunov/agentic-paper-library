"""How one reading agent's context grows, request by request.

    python3 trace.py <agent-transcript.jsonl>

Prints, for every model request: the time, the size of the context it was sent (cache
write + cache read + uncached input), the tokens newly written to the cache, and the
tools it called, with the name of the file each one touched (not its path).
"""
import json
import os
import sys


def main():
    by_id, order = {}, []
    for line in open(sys.argv[1]):
        row = json.loads(line)
        message = row.get("message") or {}
        if row.get("type") != "assistant" or message.get("model") == "<synthetic>":
            continue
        key = message.get("id")
        if key not in by_id:
            by_id[key] = {"at": row["timestamp"], "usage": {}, "tools": []}
            order.append(key)
        by_id[key]["usage"] = message.get("usage") or by_id[key]["usage"]
        for part in message.get("content") or []:
            if part.get("type") != "tool_use":
                continue
            target = part["input"].get("file_path")
            label = part["name"]
            if target:
                label += " " + os.path.basename(target)
                if part["input"].get("limit"):
                    label += " (%s lines from %s)" % (part["input"]["limit"],
                                                      part["input"].get("offset") or 1)
            by_id[key]["tools"].append(label)
    print("request\ttime\tcontext\tnewly cached\ttools")
    for number, key in enumerate(order):
        request = by_id[key]
        usage = request["usage"]
        write = usage.get("cache_creation_input_tokens", 0) or 0
        context = write + (usage.get("cache_read_input_tokens", 0) or 0) + (usage.get("input_tokens", 0) or 0)
        print("%d\t%s\t%d\t%d\t%s" % (number, request["at"][11:19], context, write,
                                      "; ".join(request["tools"])))


if __name__ == "__main__":
    main()
