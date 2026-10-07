---
name: reorganize
description: Review how papers are organised in a folder or the whole library and propose moves, splits, merges or renames of topic folders; carry them out only after the reader approves. Use for "reorganise llm/memory", "this folder is too big", "is this paper in the right place", "restructure the library around X".
model: opus
---

# /reorganize — restructure topic folders

`AGENTS.md` may describe the intended top level. Paths below are the defaults;
`.claude/library-guide.md` has this library's.

**Propose first, move after approval.** Never move a paper before the reader picks the
changes.

## Steps

1. **Scope.** Restate it in one line: a folder, several folders, or the whole library.
2. **Read.** The folders' scopes in `catalog/topics.yaml`, the scope's indexes
   (`README.md`: titles and summaries), and each paper's abstract where the summary is not
   enough to place it.
3. **Propose** numbered changes, each with a one-line reason:
   - move a paper to another folder;
   - split a folder into subfolders, listing which papers go where;
   - merge or rename folders;
   - add, remove or rescope a folder in `catalog/topics.yaml`. Empty folders are fine when
     they are part of the intended tree.

   Structure comes first; the ~20-per-folder figure is only a hint. Only split where a
   natural division exists that the reader would recognise, and leave a large folder alone
   when it does not. File general before specific: a method that predates LLMs, or applies
   to all of ML, belongs in its general area, not in an LLM folder. Show the resulting tree
   for the scope.
4. **Wait** for the reader to pick changes by number.
5. **Apply** the changes to the tree first, then the moves:
   - Add each new folder to `catalog/topics.yaml` with a one-line scope, next to its
     siblings; `paperlib move` refuses undeclared folders.
   - Move each paper with `paperlib move <paper.md> <new-topic>`. A rename or merge
     is a move of every paper in the folder. The command moves the markdown, figures and
     PDF together.
   - Remove folders that no longer exist from `catalog/topics.yaml`, and update the `topic`
     of any `catalog/skipped.yaml` entry that pointed at them (`paperlib check` fails on
     both). Adjust the scopes of folders whose content changed.
6. **Rebuild and check.** `paperlib review-status --fix-links` (repairs the review links to
   moved papers), then `paperlib build-index`, then `paperlib check`, which
   must pass. A review whose scope folder was renamed or removed gets its `scope` updated
   and its file moved to match.
7. **Report** what moved, and suggest a commit message. Never commit. If other files in
   the library (such as `AGENTS.md` or the reader's own documents) link to moved papers,
   list them so the links can be updated.
