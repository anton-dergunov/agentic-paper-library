---
name: add-paper
description: Add a paper to the library — from an arXiv link or id, a local PDF, or a paper in the unconverted Papers_old/ folder named by title. Picks the topic folder, runs the add script, writes the one-line summary, rebuilds the indexes and checks the library. Use for "add this paper", "save 2501.13956", "file this PDF", "convert <title> from my old papers".
---

# /add-paper — add a paper to the library

Read `AGENTS.md` first if you have not: it has the layout, the rules and the topic tree.

## Steps

1. **Identify the paper.**
   - arXiv URL or id: use it directly.
   - A title, or a file in `~/Yandex.Disk.localized/Papers_old/`: find its arXiv id (search
     the arXiv export API by title, e.g.
     `http://export.arxiv.org/api/query?search_query=ti:%22<words>%22`). Confirm the match
     with Anton if the title differs. If it is not on arXiv, use the local PDF.
   - Check it is not already in the library: `grep -rl "^arxiv: '<id>'" library/`.
2. **Choose the topic.** Read `library/README.md`, then the index of the most likely
   folder, and compare with the papers already there. File it where Anton would look for
   it. If nothing fits, propose a new folder (following the intended top level in
   `AGENTS.md`) and wait for his answer before creating it. State the choice in one line.
3. **Run the script.**
   - arXiv: `scripts/add-arxiv-paper.sh <id> <topic>`. If the output says it fell back to
     the PDF text layer, or the markdown looks like a conference template rather than the
     paper, say so; for the template case rerun with `--from-pdf --force`.
   - Local PDF: `scripts/add-pdf-paper.sh <file.pdf> <topic> --title "<exact title>"
     [--source "<url>"]`. It copies the PDF; files in `Papers_old/` stay where they are.
4. **Write the summary.** Read the paper's markdown (abstract, introduction, conclusion) and
   set `summary:` in its frontmatter to one neutral sentence on what the paper does or
   finds — a mechanism or result, not "this paper is about". Match the style of the
   summaries already in the folder.
5. **Rebuild and check.** `scripts/build-index.py`, then `scripts/check-library.py`, which
   must pass.
6. **Report**, briefly:
   - where it was filed, and whether the markdown came from `html` or `pdf-text`;
   - the page-map line (headings placed / unplaced);
   - two or three sentences on what the paper is and how it relates to papers already in
     the library, with links;
   - a suggested commit message. Never commit.

## Several papers at once

Run steps 1–4 per paper, then rebuild and check once at the end. Leave a few seconds
between arXiv calls; the export API rate-limits.
