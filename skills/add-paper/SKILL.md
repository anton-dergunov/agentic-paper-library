---
name: add-paper
description: Add a paper to the library from an arXiv link or id, a web article, a local PDF or a title, filing it and writing its summary; also drains INBOX.txt. Use for "add this paper", "save 2501.13956", "file this PDF", "process the inbox", "/add-paper inbox".
model: sonnet
---

# /add-paper — add a paper to the library

Paths below are the defaults; `.claude/library-guide.md` has this library's.

## Steps

1. **Identify the paper** with `paperlib lookup`, which prints the id and latest
   version, date, title, abstract, and the path if the paper is already in the library.
   - arXiv URLs or ids: `paperlib lookup <id-or-url> [...]`, all in one call.
   - A title, or a local PDF named by its title: `paperlib lookup --title "<title>"`.
     Confirm the match with the reader if the title differs. If it is not on arXiv, use
     the local PDF.
   - `already in library`: not added again.
   - `skipped earlier`: declined before (`catalog/skipped.yaml` has the reason). Say so and
     don't add it unless the reader confirms; if they do, remove its entry first.
2. **Choose the topic.** Read `catalog/topics.yaml` (every folder with its scope), then the
   index of the most likely folder, and compare with the papers there. File it where the
   reader would look for it, in the folder whose scope fits. General before specific: a
   method that predates LLMs, or applies to all of ML, goes in its general area, not in an
   LLM folder. A clear, natural structure comes first; about 20 papers a folder is a
   heuristic, not a limit. If nothing fits, propose a new folder with a one-line scope
   rather than forcing a near miss, and wait; once the reader agrees, add it to
   `catalog/topics.yaml` (the add command refuses undeclared folders). State the choice in
   one line.
3. **Run the add command.**
   - arXiv: `paperlib add-arxiv <id> <topic>`. If the output says it fell back to the PDF
     text layer, or the markdown looks like a conference template rather than the paper,
     say so; for the template case rerun with `--from-pdf --force`.
   - Web article (Distill, transformer-circuits.pub, a blog-hosted paper):
     `paperlib add-web <url> <topic>`; pass `--title`, `--authors "A; B"` or
     `--published YYYY-MM-DD` when the page's metadata lacks them.
   - Local PDF: `paperlib add-pdf <file.pdf> <topic> --title "<exact title>"
     [--source "<url>"]`. It copies the PDF and leaves the original.
4. **Write the summary.** From the paper's abstract, introduction and conclusion, one
   neutral sentence on what the paper does or finds (a mechanism or result, not "this
   paper is about"), in the style of the folder's summaries. Set it with
   `paperlib set-summary <paper.md> "<summary>"`, which handles the YAML quoting.
5. **Rebuild and check.** `paperlib build-index`, then `paperlib check`, which must pass.
6. **Report**, briefly:
   - where it was filed, and whether the markdown came from `html` or `pdf-text`;
   - the page-map line (headings placed / unplaced, and any pages it says the markdown lacks);
   - two or three sentences on what the paper is and how it relates to papers already in
     the library, with links;
   - if the folder's `README.md` links a literature review, one line: "Not yet in
     `reviews/<scope>.md`; `/literature-review update <scope>` adds it." (one per review);
   - a suggested commit message. Never commit.

## Several papers at once

Look them all up in one `paperlib lookup` call, run steps 2–4 per paper, then rebuild and
check once. The add command retries when the export API rate-limits.

## From the inbox

`INBOX.txt` at the library root holds papers the reader pasted in raw, to add later.

1. **Resolve.** `/add-paper inbox`, "my inbox", or a bare `/add-paper` while `INBOX.txt`
   is open in the editor all mean it. Say how many entries it holds; if none, stop.
2. **Split into entries.** Blank lines separate entries: an arXiv URL or id, a title, a
   PDF path, or a URL with its title on the next line. Other words in an entry (e.g.
   "→ llm/memory") are the reader's notes: a topic hint. Go by meaning when the format is
   loose.
3. **Look up every entry** as in step 1: one `paperlib lookup` call for the ids and URLs,
   plus a `--title` for each title-only entry.
4. **Propose and wait.** One numbered table: entry, arXiv id or source, title, proposed
   topic; mark `already in library`, `skipped earlier`, `new folder` and `unclear match`.
   Run no add command until the reader approves; they may change topics or skip entries by
   number. An entry they decline for good goes to `catalog/skipped.yaml` with their reason.
5. **Add** the approved entries (steps 3–4 per paper), then rebuild and check once.
6. **Drain the inbox.** Remove every entry that was added or was already in the library.
   Leave skipped and failed entries exactly as they were, and don't rewrite the rest.
7. **Report** as in step 6, plus which entries are still in the inbox and why. One commit
   message covers the run, `INBOX.txt` included.
