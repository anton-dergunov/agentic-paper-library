---
name: overview
description: Write a short pre-read overview note for a paper already in the library into the reader's own notes folder (overview_dir, e.g. an Obsidian vault), giving the intuition in 3–5 minutes; also sets the paper type and writes its notes/ memory file. Use for "overview <paper>", "/overview", "start working on <paper>", "make me a note for <paper>". Not for adding papers (that is add-paper).
model: opus
---

# /overview — a quick pre-read note for a paper

The reader runs this before reading a paper. The note gives them the intuition in 3–5
minutes (what problem, what idea, why it works, what it was tried on, how it relates to
other work); then they decide whether to read the paper, and grow the note themselves.
`format.md` in this folder defines the note; read it before writing.

**Be fast and lightweight.** The reader runs this on many papers: a couple of minutes and
a handful of tool calls. Do only the steps below, nothing around them.

**Where notes go:** `<overview_dir>/<stem>.md`, where `overview_dir` is set in
`paper-library.yaml` (the guide's layout table shows it) and `<stem>` is the paper's file
name in `library/`; no other notes-folder path. If `overview_dir` is not configured, ask
the reader where notes should live and suggest setting it; don't write the note until it
is settled. Other paths below are the defaults; `.claude/library-guide.md` has this
library's.

## Steps

1. **Resolve the paper** with one `find library -iname "*<words>*.md" -not -name README.md`
   (or `paperlib lookup <id>` for an arXiv id). Several matches: ask. None: stop and
   offer `/add-paper`.
2. **Check two files, nothing else.**
   - `<overview_dir>/<stem>.md`: if it exists, don't overwrite it; say so in one
     line and ask whether to write `<stem> - overview.md` instead or stop. Don't search
     for other versions or variants of the note.
   - `notes/<stem>.md`: if it exists, read it and reuse it.
3. **Read the paper once**: the main text, up to the `References` heading. Skip the
   appendix and the reference list.
4. **Set the type** (table in `format.md`) with
   `paperlib set-type <paper.md> <type>`. Don't touch any other frontmatter field,
   in particular `summary`.
5. **Find links cheaply**: if the folder's `README.md` links a literature review, read the
   paper's line in its paper map and the lines around it. Otherwise, at most two greps over
   the indexes (`grep -il "<name1>\|<name2>" library --include=README.md`) for the closest
   works the paper names. Then one note-name search over the notes folder
   (`find <overview_dir> -name '*.md' -not -path '*/.*' | grep -iE 'puct|lora|alphaevolve'`).
   An existing note there: link its exact name. None: link the natural name anyway. Don't
   open other papers.
6. **Write the note** as `format.md` describes.
7. **Write `notes/<stem>.md`**, the agent's memory, in the notes format in
   `.claude/library-guide.md`: a digest of the mechanism and key numbers, and the related
   library papers. Detail belongs here, not in the reader's note. If the file exists, merge
   and keep its Q&A.
8. **Report.** The whole reply is exactly these two parts, with nothing before or after:
   - `I've written the overview note: [<stem>](<path>)`
   - A short commit message for the library side (`type` field and `notes/<stem>.md`): a
     one-line summary and one short line of detail. Never commit.

   Never mention what already existed or was skipped (the type was already set, the memory
   file already had a digest), the type you chose, or what you did. Add one line only if
   something is really wrong (for example `source: pdf-text`, so the numbers may be
   unreliable).

**Out of scope:** rebuilding indexes, `paperlib check`, `git status`, the library's other
documents, the web, subagents, and the reader's files outside the library and the notes
folder. Untracked papers and empty summaries come from other sessions running in parallel;
ignore them.

## Iterating on this skill

The reader refines the format as they use it. When they correct a note, apply the
correction to the note and, if it is a general rule, to `format.md` or this file as well.
