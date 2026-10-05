"""Have one model read each paper once: the reading view in, the note out, no tools.

    python3 run.py <library>/library/<topic> <out-dir> <reader> ...

Readers: a Claude model id (run with `claude -p`, no tools, the system prompt replaced by
one line) or a Gemini model id (Vertex AI; needs google-genai, GOOGLE_APPLICATION_CREDENTIALS
and GOOGLE_CLOUD_PROJECT). Writes <out-dir>/<reader>/<stem>.md and appends a line per call
to <out-dir>/runs.jsonl. A note that already exists is not read again.
"""
import json
import os
import subprocess
import sys
import time

from read_view import read_view

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM = "You read research papers carefully and write precise notes on them."


def claude(model, prompt):
    done = subprocess.run(
        ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", SYSTEM,
         "--output-format", "json", "--no-session-persistence"],
        input=prompt, capture_output=True, text=True, cwd="/tmp")
    reply = json.loads(done.stdout)
    usage = reply.get("usage", {})
    return reply["result"], {
        "input": usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0),
        "output": usage.get("output_tokens", 0), "usd": reply.get("total_cost_usd")}


def gemini(model, prompt):
    from google import genai
    from google.genai import types
    client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"],
                          location="global")
    reply = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM))
    usage = reply.usage_metadata
    return reply.text, {
        "input": usage.prompt_token_count,
        "output": (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)}


def main():
    topic, out = sys.argv[1], sys.argv[2]
    instructions = open(os.path.join(HERE, "prompt.md")).read()
    stems = [line.strip() for line in open(os.path.join(HERE, "papers.txt")) if line.strip()]
    for reader in sys.argv[3:]:
        os.makedirs(os.path.join(out, reader), exist_ok=True)
        for stem in stems:
            target = os.path.join(out, reader, stem + ".md")
            if os.path.exists(target):
                continue
            prompt = instructions + read_view(open(os.path.join(topic, stem + ".md")).read())
            start = time.time()
            try:
                note, usage = (gemini if reader.startswith("gemini") else claude)(reader, prompt)
            except Exception as error:  # one failed call should not stop the others
                print(reader, stem, "FAILED", str(error)[:300], flush=True)
                continue
            note = note.strip()
            if note.startswith("```"):
                note = note.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            open(target, "w").write(note + "\n")
            usage.update(reader=reader, paper=stem, seconds=round(time.time() - start),
                         prompt_chars=len(prompt), note_chars=len(note))
            with open(os.path.join(out, "runs.jsonl"), "a") as log:
                log.write(json.dumps(usage) + "\n")
            print(reader, stem[:40], usage, flush=True)


if __name__ == "__main__":
    main()
