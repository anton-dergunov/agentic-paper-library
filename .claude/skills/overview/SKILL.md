---
name: overview
description: Write the first overview note for a paper that is already in the library, into Anton's Obsidian vault — the mechanism, why it works, what each application was, how it relates to other work, and what to learn and try next. Classifies the paper type and keeps a per-paper memory file in notes/. Use for "overview <paper>", "/overview", "start working on <paper>", "make me a note for <paper>". Not for adding papers (that is add-paper).
---

# /overview — first working note for a paper

Anton runs this when he decides to work through a paper. The note is where he starts, and he
grows it himself afterwards. It must take him past the abstract: the internal mechanism, why
it works, what the experiments actually were, and where the paper sits among other work.
`format.md` in this folder defines the note; read it before writing.

Read `AGENTS.md` first if you have not.

**Where notes go.** New paper notes are written to `~/obsidian/ML & AI/Papers/<stem>.md`,
where `<stem>` is the paper's file name in `library/`. This is the only vault path the skill
uses. Everything else finds notes by name across the whole vault, so reorganising the vault
means changing only this line.

**Budget.** Read the paper once. Beyond that, use only the cheap layers: the library
`summary` fields, the per-folder `README.md` indexes, and vault note names. Don't read other
papers' bodies, run subagents, search the web, or read career or org files.

## Steps

1. **Resolve the paper.** The argument may be a title fragment, a stem, a path or an arXiv
   id. Use `find library -iname "*<words>*.md" -not -name README.md`, or
   `scripts/arxiv-lookup.py <id>`, which prints the library path. If there are several
   matches, ask. If the paper is not in the library, stop and offer `/add-paper`.
2. **Check what exists.**
   - Look for a vault note with the same name:
     `find ~/obsidian -name "<stem>.md" -not -path '*/.*'`. If there is one, don't
     overwrite it. Say what it holds and ask whether to start from it, write alongside as
     `<stem> - overview.md`, or stop.
   - If `notes/<stem>.md` exists, read it first. Its digest and Q&A are earlier findings, so
     reuse them.
3. **Read the paper.** Start with `grep -n '^#' <paper.md>` for the outline and the page
   numbers. Then read the frontmatter, abstract, introduction, the method or main sections,
   experiments, related work and conclusion. Read an appendix only where the main text sends
   you to it, for example for a loss definition or a benchmark description. Skip the
   reference list unless you need it to identify a cited work. If `source: pdf-text`, say
   in the report that equations and numbers may be unreliable.
4. **Classify the type** using the table in `format.md`: `method`, `survey`, `benchmark`,
   `study`, `system`, `position` or `theory`. Record it with
   `scripts/paperlib.py set-type <paper.md> <type>`. The note's frontmatter gets the same
   value.
5. **Find the links**, cheaply:
   - **Library.** For each method, baseline, concurrent work or surveyed system the paper
     names, grep the indexes: `grep -ril "<name>" library --include=README.md`. Also read
     this paper's own folder index. A hit gives you the paper's stem and summary, and that is
     enough to say how it relates. Don't open the paper.
   - **Vault.** Run one name search over the whole vault, built from the concepts and papers
     you plan to link:
     `find ~/obsidian -name '*.md' -not -path '*/.*' | grep -iE 'puct|entropic|lora|alphaevolve'`.
     Don't list folders. If a matching note exists, link its exact name. If none does, link
     the name anyway: Anton wants links to notes that don't exist yet. Don't try to
     normalise names across the vault.
   - **Familiarity.** An existing concept note means Anton has studied the topic. Link it,
     and give no gloss or a short one.
   - **URLs.** The arXiv abstract page (the frontmatter `url`), plus any code or project
     URLs printed in the paper.
6. **Write the note** as `format.md` describes, at the path from "Where notes go" (or the
   alternative name chosen in step 2).
7. **Write `notes/<stem>.md`**, the agent's memory of the paper, in the format in
   `notes/README.md`:
   - a digest of the mechanism and key numbers, with pages;
   - the library papers found in step 5 and how each relates.
   If the file exists, merge into it and keep its Q&A. This file is what later sessions
   read instead of the whole paper, so put in it what you learned that the Obsidian note
   leaves out: exact definitions, hyperparameters, numbers with their baselines.
8. **Report**, briefly. Don't summarise the note in chat; Anton reads the note itself.
   - The note's path and the type you chose, with one line of reasoning if the type was
     unclear.
   - Anything uncertain: a `pdf-text` source, a type that was hard to call, a benchmark the
     paper doesn't explain.
   - A suggested commit message for the repo side (the `type` field and `notes/<stem>.md`).
     The vault commits itself through obsidian-git. Never commit.

## Iterating on this skill

Anton refines the format as he uses it. When he corrects a note, apply the correction to
the note and, if it is a general rule, to `format.md` as well. Say which ones you changed.
