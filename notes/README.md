# Paper notes (agent memory)

One file per paper, `notes/<stem>.md`, where `<stem>` is the paper's file name in `library/`
without `.md`. The folder is flat, so moving a paper between topics does not touch it;
`scripts/check-library.py` fails on a note whose paper is not in the library.

These files are for the agent, not for Anton, whose notes live in Obsidian. They hold
what was learned about a paper, so that later sessions and comparisons across papers
don't re-read and re-derive it. The `overview` skill creates a paper's file; any session
may append to its Q&A.

```markdown
# <Title>

type: method

## Digest

At most 20 lines: the mechanism, key definitions, and the main numbers with their
baselines, each with its page (p. N). Enough to compare this paper with others without
re-reading it.

## Related in library

- <stem>: how it relates, in one line

## Q&A

- 2026-10-01: <question> → <short answer> (p. N)
```

Merge into an existing file; never drop its Q&A.
