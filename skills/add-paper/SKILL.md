---
name: add-paper
description: Add a paper to the library — from an arXiv link or id, a web article, a local PDF, or a title. Picks the topic folder, runs paperlib's add command, writes the one-line summary, rebuilds the indexes and checks the library. Use for "add this paper", "save 2501.13956", "file this PDF". Also use to drain INBOX.txt, for "add papers from my inbox", "process the inbox", "/add-paper inbox".
---

# /add-paper — add a paper to the library

Read `AGENTS.md` (which imports `.claude/library-guide.md`) first if you have not: it has
the layout, the rules and the topic tree. Paths below are the defaults;
`.claude/library-guide.md` has this library's.

## Steps

1. **Identify the paper** with `paperlib lookup`, which prints the id and latest
   version, date, title, abstract, and the path if the paper is already in the library.
   - arXiv URLs or ids: `paperlib lookup <id-or-url> [...]`, all in one call.
   - A title, or a local PDF named by its title:
     `paperlib lookup --title "<title>"`. Confirm the match with the reader if the
     title differs. If it is not on arXiv, use the local PDF.
   - A paper marked `already in library` is not added again.
   - A paper marked `skipped earlier` was declined before (`catalog/skipped.yaml` has the
     reason). Say so and don't add it unless the reader confirms; if they do, remove its
     entry from `catalog/skipped.yaml` first.
2. **Choose the topic.** Read `catalog/topics.yaml` (every folder with its scope), then
   the index of the most likely folder, and compare with the papers already there. File it
   where the reader would look for it, general before specific (see Topics in
   `.claude/library-guide.md`). If nothing fits, propose a new folder with a one-line scope
   and wait for their answer; once they agree, add it to `catalog/topics.yaml` before
   running the add command, which refuses undeclared folders. State the choice in one line.
3. **Run the add command.**
   - arXiv: `paperlib add-arxiv <id> <topic>`. If the output says it fell back to
     the PDF text layer, or the markdown looks like a conference template rather than the
     paper, say so; for the template case rerun with `--from-pdf --force`.
   - Web article (Distill, transformer-circuits.pub, a blog-hosted paper):
     `paperlib add-web <url> <topic>`; pass `--title`, `--authors "A; B"` or
     `--published YYYY-MM-DD` when the page's metadata lacks them.
   - Local PDF: `paperlib add-pdf <file.pdf> <topic> --title "<exact title>"
     [--source "<url>"]`. It copies the PDF and leaves the original where it is.
4. **Write the summary.** Read the paper's markdown (abstract, introduction, conclusion) and
   write one neutral sentence on what the paper does or finds — a mechanism or result,
   not "this paper is about". Match the style of the summaries already in the folder. Set
   it with `paperlib set-summary <paper.md> "<summary>"`, which handles the
   YAML quoting.
5. **Rebuild and check.** `paperlib build-index`, then `paperlib check`, which
   must pass.
6. **Report**, briefly:
   - where it was filed, and whether the markdown came from `html` or `pdf-text`;
   - the page-map line (headings placed / unplaced);
   - two or three sentences on what the paper is and how it relates to papers already in
     the library, with links;
   - if the folder's `README.md` links a literature review, one line: "Not yet in
     `reviews/<scope>.md`; `/literature-review update <scope>` adds it." (For several
     papers, one line per review.)
   - a suggested commit message. Never commit.

## Several papers at once

Look them all up in one `paperlib lookup` call, run steps 2–4 per paper, then rebuild
and check once at the end. The add command retries when the export API rate-limits.

## From the inbox

`INBOX.txt` at the library root is where the reader collects papers to add later, pasted
raw.

1. **Resolve.** `/add-paper inbox`, "my inbox", or a bare `/add-paper` while `INBOX.txt`
   is the file open in the editor all mean `INBOX.txt`. Read it and say how many entries
   it holds. If it is empty, say so and stop.
2. **Split into entries.** Blank lines separate entries. An entry is an arXiv URL or id, a
   title, a PDF path, or a URL with its title on the next line. Any other words in an
   entry (e.g. "→ llm/memory") are the reader's notes: use them as a topic hint. Go by
   meaning when the format is loose.
3. **Run step 1 for every entry**: one `paperlib lookup` call for all the ids and URLs,
   plus a `--title` for each entry that has only a title.
4. **Propose and wait.** Show one numbered table: entry, arXiv id or source, title,
   proposed topic. Mark `already in library`, `skipped earlier`, `new folder` and
   `unclear match`. Run no add command until the reader approves; they may change topics
   or skip entries by number. An entry they decline for good goes to `catalog/skipped.yaml`
   with their reason.
5. **Add** the approved entries (steps 3–4 per paper), then rebuild and check once
   (step 5).
6. **Drain the inbox.** Remove from `INBOX.txt` every entry that was added or was already
   in the library. Leave skipped and failed entries exactly as they were, and do not
   rewrite the rest of the file.
7. **Report** as in step 6, plus which entries are still in the inbox and why. One commit
   message covers the whole run, `INBOX.txt` included.
