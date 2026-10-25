# Task: a ledger of how agents read the library's papers

If the library drops the markdown and keeps each paper's text layer beside its PDF (the reading-formats experiment, tiers F–H, decide this), it relies on Claude Code to read the text first and to look at a page image only when a value is drawn (a point on a plot, a bar, a raster figure). That is Claude Code's behaviour, guided by a line of the guide, not the library's code: it can improve with a release (a text-only or page-selective `Read` of PDFs would change the costs) or regress (whole PDFs read through `Read`, about twice the markdown's tokens, every page sent as text plus image). The experiment's canary checks it on fixed questions; this ledger checks it in real use.

Do this only if the library switches to text layers; until then, the same command would show how often agents open PDFs beside the markdown, which is also worth knowing.

## What it records

Claude Code already keeps each session in a library as a transcript (`~/.claude/projects/<the library's path, encoded>/<session>.jsonl`): every tool call with its arguments, and each turn's token usage. Nothing has to be added to the sessions; a command reads the transcripts afterwards, as `experiments/reading-formats/report.py` reads tier D's event streams.

`paperlib reads [--since DATE]` reads the transcripts not yet seen and appends one line per session to a ledger in the library (`usage/reads.jsonl`, committed), so the record outlives the transcripts (Claude Code deletes old ones after its retention period, to check: 30 days by default):

- date, session id, `claude --version` (the transcript records it), model;
- counts by kind: text layer read or grepped, a PDF page read (`Read` with `pages`, how many pages), a whole PDF read (`Read` without `pages`, or more than a few pages), a page rendered or read as an image, `pdftotext` or another PDF tool in the shell, notes and reviews read;
- input tokens of the session, and an estimate of what the page images cost (pages × the measured cost: about 1,550 tokens for a page image inside a PDF read, 2,250 for a 1,255 px rendering);
- the first line of the user's question, to sample by hand.

## What it reports

Per Claude Code version and per month: the share of sessions that opened any page image, pages opened per session, the share of input tokens spent on images, and the sessions to look at: a whole-PDF `Read`, more than a few pages in one session, or images opened in a session whose question names no figure. A jump in any of these after a new version is the signal to rerun the experiment's canary and, if needed, change the guide's line.

## Keep it light

No hook and no live logging: the transcripts already have everything, and a hook would add a step to every tool call. Run it by hand or from `paperlib check`; library-agnostic (the transcript folder comes from the library's path); no model requests.

## Done when

It reproduces tier F's counts (pages opened per question, whole-PDF reads) from that tier's saved event streams (the experiment's sessions keep no transcripts, `--no-session-persistence`, but their stream-json carries the same tool calls and usage), and a month of real use gives a report the author can read in a minute.
