---
name: overview
description: Write a short first overview note for a paper that is already in the library, into Anton's Obsidian vault — a 3–5 minute pre-read that gives the intuition behind the paper before he reads it. Classifies the paper type and keeps a per-paper memory file in notes/. Use for "overview <paper>", "/overview", "start working on <paper>", "make me a note for <paper>". Not for adding papers (that is add-paper).
---

# /overview — a quick pre-read note for a paper

Anton runs this when he is about to read a paper. The note gives him the intuition in 3–5
minutes: what problem, what idea, why it works, what it was tried on, and how it relates to
other work. Then he decides whether to read the paper, and grows the note himself.
`format.md` in this folder defines the note; read it before writing.

**Be fast and lightweight.** Anton runs this on many papers. Aim for a couple of minutes and
a handful of tool calls. Do only the steps below, nothing around them.

**Where notes go.** New paper notes are written to `~/obsidian/ML & AI/Papers/<stem>.md`,
where `<stem>` is the paper's file name in `library/`. This is the only vault path the skill
uses. Reorganising the vault means changing only this line.

## Steps

1. **Resolve the paper** with one `find library -iname "*<words>*.md" -not -name README.md`
   (or `scripts/arxiv-lookup.py <id>` for an arXiv id). Several matches: ask. None: stop and
   offer `/add-paper`.
2. **Check two files, nothing else.**
   - `~/obsidian/ML & AI/Papers/<stem>.md`: if it exists, don't overwrite it; say so in one
     line and ask whether to write `<stem> - overview.md` instead or stop. Don't search
     for other versions or variants of the note.
   - `notes/<stem>.md`: if it exists, read it and reuse it.
3. **Read the paper once**: the main text, up to the `References` heading. Skip the
   appendix and the reference list.
4. **Set the type** (table in `format.md`) with
   `scripts/paperlib.py set-type <paper.md> <type>`. Don't touch any other frontmatter field,
   in particular `summary`.
5. **Find links cheaply**: at most two greps over the indexes
   (`grep -il "<name1>\|<name2>" library --include=README.md`) for the closest works the
   paper names, and one vault-name search
   (`find ~/obsidian -name '*.md' -not -path '*/.*' | grep -iE 'puct|lora|alphaevolve'`).
   An existing vault note: link its exact name. None: link the natural name anyway. Don't
   open other papers.
6. **Write the note** as `format.md` describes.
7. **Write `notes/<stem>.md`**, the agent's memory, in the format in `notes/README.md`: a
   digest of the mechanism and key numbers, and the related library papers. Detail belongs
   here, not in the vault note. If the file exists, merge and keep its Q&A.
8. **Report in two parts only:**
   - `I've written the overview note: [<stem>](<path>)`
   - A short commit message for the repo side (`type` field and `notes/<stem>.md`): a
     one-line summary and one short line of detail. Never commit.

   Don't restate the type, the memory file or what you did. Add one line only if something
   is really wrong (for example `source: pdf-text`, so the numbers may be unreliable).

**Out of scope:** rebuilding indexes, `check-library.py`, `git status`, `docs/` and the
inventory, the web, subagents, and career or org files. Untracked papers and empty summaries
come from other sessions running in parallel; ignore them.

## Iterating on this skill

Anton refines the format as he uses it. When he corrects a note, apply the correction to
the note and, if it is a general rule, to `format.md` or this file as well.
