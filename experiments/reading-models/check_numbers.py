"""Check every number in a note against the paper, and every page against its section.

    python3 check_numbers.py <library>/library/<topic> <results-dir>

A number is a figure with a decimal point, a percent sign or at least three digits, as
printed in a Digest line (years and page, table, figure and section numbers are left
out). It is "found" if the same string occurs in the paper's reading view. Its page is
"right" if the line cites a page or range that overlaps a section in which the number
occurs: a section runs from the page on its heading to the page on the next heading.
A line with no page at all counts as "no page". Prints one row per reader and paper,
then the numbers not found, so they can be looked up by hand.
"""
import glob
import os
import re
import sys

from read_view import read_view

NUMBER = re.compile(r"(?<![\w.,])\d[\d,]*\.\d+%?|(?<![\w.,])\d[\d,]*%|(?<![\w.,])\d{1,3}(?:,\d{3})+|(?<![\w.,])\d{3,}(?![\w,]*\d)")
REFERENCE = re.compile(r"\(?pp?\.\s*[\d–\-, ]+|(?:Tables?|Figures?|Fig\.|Section|Sec\.|§|App\.|Appendix|Eq\.|Equation)\s*[\dA-Z.]+(?:\s*[–\-,&]\s*[\dA-Z.]+)*", re.I)
PAGES = re.compile(r"pp?\.\s*(\d+)(?:\s*[–\-]\s*(\d+))?")
HEADING = re.compile(r"^#{1,6} .*\(p\. (\d+)\)\s*$", re.M)


def sections(view):
    """[(first page, last page, text)] for the text under each heading that has a page."""
    marks = [(m.start(), int(m.group(1))) for m in HEADING.finditer(view)]
    out = []
    if marks:
        out.append((1, marks[0][1], view[:marks[0][0]]))
    for i, (pos, page) in enumerate(marks):
        end, last = (marks[i + 1][0], marks[i + 1][1]) if i + 1 < len(marks) else (len(view), 10 ** 6)
        out.append((page, last, view[pos:end]))
    return out


def plain(s):
    return s.replace(",", "").replace("\\%", "%")


def main():
    topic, results = sys.argv[1], sys.argv[2]
    misses = []
    print("reader\tpaper\tnumbers\tnot found\tno page\twrong page")
    for note_path in sorted(glob.glob(os.path.join(results, "*", "*.md"))):
        reader = os.path.basename(os.path.dirname(note_path))
        stem = os.path.basename(note_path)[:-3]
        view = plain(read_view(open(os.path.join(topic, stem + ".md")).read()))
        parts = sections(view)
        note = open(note_path).read()
        digest = note.split("## Digest", 1)[-1].split("## Related", 1)[0]
        total = missing = unpaged = wrong = 0
        for line in digest.splitlines():
            cited = [(int(a), int(b or a)) for a, b in PAGES.findall(line)]
            for number in NUMBER.findall(REFERENCE.sub(" ", line)):
                number = plain(number)
                if re.fullmatch(r"(19|20)\d\d", number):
                    continue
                total += 1
                variants = {number, number.rstrip("%")}
                if not any(v in view for v in variants):
                    missing += 1
                    misses.append("%s\t%s\t%s\t%s" % (reader, stem[:30], number, line.strip()[:160]))
                elif not cited:
                    unpaged += 1
                elif parts and not any(first <= hi and lo <= last and any(v in text for v in variants)
                                       for first, last, text in parts for lo, hi in cited):
                    wrong += 1
        print("%s\t%s\t%d\t%d\t%d\t%d" % (reader, stem[:30], total, missing, unpaged, wrong))
    print("\nNumbers not found in the paper's text:\nreader\tpaper\tnumber\tline")
    print("\n".join(misses))


if __name__ == "__main__":
    main()
