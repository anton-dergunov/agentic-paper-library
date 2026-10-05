"""Build the copies of a library that the question sessions run in.

    python3 copies.py <library> <out-dir> [asis] [noreviews] [nonotes]

Each copy <out-dir>/lib-<condition> holds the library's instructions (AGENTS.md,
CLAUDE.md, .claude/library-guide.md), catalog/, paper-library.yaml and the paper markdown
without figures. "asis" also has notes/ and reviews/; "noreviews" has notes/ only;
"nonotes" has neither. Where a folder is left out, the guide's rule and layout row for it,
the mentions in AGENTS.md and the review links in the folder indexes are removed too, and
the script prints what is still mentioned so that a leak shows.

The paper files are hard links to the library's own (rsync --link-dest): a session that
edits a paper in a copy edits the library. The edited instruction and index files are
written as new files. Delete the copies when the run is done.
"""
import glob
import os
import re
import shutil
import subprocess
import sys


def build(library, out, condition):
    copy = os.path.join(out, "lib-" + condition)
    os.makedirs(os.path.join(copy, ".claude"), exist_ok=True)
    subprocess.run(["rsync", "-a", "--link-dest=" + os.path.join(library, "library"),
                    "--exclude", "images", "--exclude", "*.pdf",
                    os.path.join(library, "library") + "/", os.path.join(copy, "library") + "/"], check=True)
    shutil.copytree(os.path.join(library, "catalog"), os.path.join(copy, "catalog"), dirs_exist_ok=True)
    for name in ("AGENTS.md", "CLAUDE.md", "paper-library.yaml", ".claude/library-guide.md"):
        if os.path.exists(os.path.join(library, name)):
            shutil.copy(os.path.join(library, name), os.path.join(copy, name))
    keep = {"asis": ("notes", "reviews"), "noreviews": ("notes",), "nonotes": ()}[condition]
    for folder in keep:
        shutil.copytree(os.path.join(library, folder), os.path.join(copy, folder), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".work"))
    guide_path = os.path.join(copy, ".claude", "library-guide.md")
    agents_path = os.path.join(copy, "AGENTS.md")
    guide, agents = open(guide_path).read(), open(agents_path).read()
    if "reviews" not in keep:
        for index in glob.glob(os.path.join(copy, "library", "**", "README.md"), recursive=True):
            text = open(index).read()
            cut = re.sub(r"^Literature review: .*\n\n?", "", text, flags=re.M)
            if cut != text:
                os.remove(index)  # a hard link: replace the file, do not write through it
                open(index, "w").write(cut)
        guide = re.sub(r"^\| Literature review per area.*\n", "", guide, flags=re.M)
        guide = re.sub(r"^- \*\*Start from the review.*\n(  - .*\n)*", "", guide, flags=re.M)
        agents = agents.replace(", `reviews/`", "")
        agents = re.sub(r"; the area's review\s+and its paper map are the quickest way to find those", "", agents)
    if "notes" not in keep:
        guide = re.sub(r"^\| Agent memory per paper.*\n", "", guide, flags=re.M)
        guide = re.sub(r"^- \*\*Check what is already known about a paper\.\*\*.*\n", "", guide, flags=re.M)
        guide = re.sub(r"^## Notes: agent memory per paper\n.*?(?=^## Topics)", "", guide, flags=re.M | re.S)
        agents = agents.replace(", `notes/`", "")
    open(guide_path, "w").write(guide)
    open(agents_path, "w").write(agents)
    left = {word: len(re.findall(word, guide + agents)) for word in ("reviews?/|[Rr]eview", "`?notes/")}
    print("%s: %s; still mentioned in the instructions: %s" % (condition, copy, left))


def main():
    library, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    for condition in sys.argv[3:] or ["asis", "noreviews", "nonotes"]:
        build(library, out, condition)


if __name__ == "__main__":
    main()
