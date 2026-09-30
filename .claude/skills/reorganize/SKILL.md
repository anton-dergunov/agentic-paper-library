---
name: reorganize
description: Review how papers are organised in a folder or the whole library and propose moves, splits, merges or renames of topic folders; carry them out only after Anton approves. Use for "reorganise llm/memory", "this folder is too big", "is this paper in the right place", "restructure the library around X".
---

# /reorganize — restructure topic folders

Read `AGENTS.md` first if you have not: it has the topic rules and the intended top level.

**Propose first, move after approval.** Never move a paper before Anton picks the changes.

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
   natural division exists that Anton would recognise, and leave a large folder alone when
   it does not. Show the resulting tree for the scope.
4. **Wait** for Anton to pick changes by number.
5. **Apply** the changes to the tree first, then the moves:
   - Add each new folder to `catalog/topics.yaml` with a one-line scope, next to its
     siblings; `scripts/move-paper.sh` refuses undeclared folders.
   - Move each paper with `scripts/move-paper.sh <paper.md> <new-topic>`. A rename or merge
     is a move of every paper in the folder. The script moves the markdown, figures and PDF
     together.
   - Remove folders that no longer exist from `catalog/topics.yaml`, and update the `topic`
     of any `catalog/skipped.yaml` entry that pointed at them (`check-library.py` fails on
     both). Adjust the scopes of folders whose content changed.
6. **Rebuild and check.** `scripts/build-index.py`, then `scripts/check-library.py`, which
   must pass.
7. **Report** what moved, and suggest a commit message. Never commit. If other files link
   to moved papers (`docs/`, `reviews/`), list them so the links can be updated.
