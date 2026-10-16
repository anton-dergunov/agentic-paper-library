---
id: pdf-table-image-ocr
title: "Tables that are images are read by OCR without saying so"
converter: pdf
takes: [engine, reconvert]
status: open
cost: "engine: small; reconvert the papers with such tables"
---

# Tables that are images are read by OCR without saying so

`engine` `reconvert` · pdf · open

**Broken.** A table set as an image is read by OCR, whose numbers differ a little from run to run, while the note at the top of the paper says the numbers are the PDF's own.

**Fix.** Say so in the note at the top when a table had no text layer under it.

**What it gives.** An agent knows which numbers to check against the PDF before quoting them.

**Cost.** Engine: small; reconvert the papers with such tables.

**Examples.** TabPFN's Extended Data tables (pp. 18–23).
