"""The text a reader is given: a paper's main text, without what a reader skips.

    python3 read_view.py <paper.md>

Keeps the frontmatter's title and everything up to the references heading, with the
(p. N) markers on headings. Drops link targets, image links (a figure becomes "[figure]"
next to its caption), and inline span/sup/anchor tags. Tables stay as they are. This is
the prototype of a `paperlib read-view` command.
"""
import re
import sys

REFERENCES = re.compile(r"^#{1,3} +(References|Bibliography|REFERENCES)\b.*$", re.M)


def read_view(text):
    title = re.search(r"^title:\s*(.*)$", text, re.M).group(1).strip("'\"")
    body = text.split("\n---\n", 1)[1] if text.startswith("---") else text
    cut = REFERENCES.search(body)
    if cut:
        body = body[:cut.start()]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "[figure]", body)
    body = re.sub(r"\]\((#|https?://)[^)]*\)", "]", body)
    body = re.sub(r"</?(span|sup|sub|a|div)\b[^>]*>", "", body)
    body = re.sub(r' (class|style|id)="[^"]*"', "", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return "# %s\n\n%s" % (title, body.strip()) + "\n"


if __name__ == "__main__":
    sys.stdout.write(read_view(open(sys.argv[1]).read()))
