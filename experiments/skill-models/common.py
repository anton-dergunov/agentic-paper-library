"""What the scripts of this experiment share: reading a paper's title, folder, stored summary
and abstract from a library, and one model request with no tools."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-5-5", "claude-opus-5-5"]
ABSTRACT = re.compile(r"^#+ *abstract\b[^\n]*\n(.*?)(?=^#+ )", re.I | re.S | re.M)


def paper(library, relative):
    """A paper as the experiment sees it; `relative` is its path under library/, without .md."""
    text = (Path(library) / "library" / (relative + ".md")).read_text()
    _, front, body = text.split("---\n", 2)
    meta = yaml.safe_load(front)
    found = ABSTRACT.search(body)
    return {"paper": relative, "folder": str(Path(relative).parent), "title": meta["title"],
            "summary": " ".join(str(meta.get("summary") or "").split()),
            "abstract": " ".join(found.group(1).split())[:3000] if found else ""}


def ask(model, system, prompt):
    """One request with no tools. Returns (reply text, usage dict); raises on failure."""
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", system,
             "--output-format", "json", "--no-session-persistence"],
            input=prompt, capture_output=True, text=True, cwd=empty)
    try:
        reply = json.loads(done.stdout)
    except ValueError:
        raise RuntimeError((done.stderr or done.stdout or "no output").strip()[:300])
    if reply.get("is_error") or not reply.get("result"):
        raise RuntimeError(str(reply.get("result") or reply.get("subtype") or "no reply")[:300])
    usage = reply.get("usage", {})
    return reply["result"], {
        "input": sum(usage.get(k, 0) or 0 for k in
                     ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "output": usage.get("output_tokens", 0), "usd": reply.get("total_cost_usd")}


def json_in(text):
    return json.loads(text[text.index("{"):text.rindex("}") + 1])
