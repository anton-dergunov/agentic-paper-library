"""Build the copies of a library that the question sessions run in.

    python3 copies.py <library> <out-dir> [asis] [noreviews] [nonotes] [<name>=<condition>]

Each copy <out-dir>/lib-<name> holds the library's instructions (AGENTS.md, CLAUDE.md,
.claude/library-guide.md), catalog/, paper-library.yaml and the paper markdown without
figures. "asis" also has notes/ and reviews/; "noreviews" has notes/ only; "nonotes" has
neither. Where a folder is left out, the guide's rule and layout row for it, the mentions
in AGENTS.md and the review links in the folder indexes are removed too, and the script
prints what is still mentioned so that a leak shows. <name>=<condition> builds a second
copy of a condition under another name, for a variant of the rule: see --rule.

    python3 copies.py --rule <rule.md> <out-dir>/lib-<name>

replaces the "Start from the review" rule of a built copy's guide with the text of
<rule.md> (one list item, with its sub-items).

A copy is a real copy (about 260 MB) and is made read-only, so that a session cannot
write to it through the shell. An existing copy is rebuilt. Delete with `chmod -R u+w`
first.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

RULE = r"^- \*\*Start from the review.*\n(  - .*\n)*"


def lock(copy, locked):
    subprocess.run(["chmod", "-R", "a-w" if locked else "u+w", copy], check=True)


def build(library, out, name, condition):
    copy = os.path.join(out, "lib-" + name)
    if os.path.exists(copy):
        lock(copy, False)
        shutil.rmtree(copy)
    os.makedirs(os.path.join(copy, ".claude"))
    subprocess.run(["rsync", "-a", "--exclude", "images", "--exclude", "*.pdf",
                    os.path.join(library, "library") + "/", os.path.join(copy, "library") + "/"], check=True)
    shutil.copytree(os.path.join(library, "catalog"), os.path.join(copy, "catalog"))
    for file in ("AGENTS.md", "CLAUDE.md", "paper-library.yaml", ".claude/library-guide.md"):
        if os.path.exists(os.path.join(library, file)):
            shutil.copy(os.path.join(library, file), os.path.join(copy, file))
    keep = {"asis": ("notes", "reviews"), "noreviews": ("notes",), "nonotes": ()}[condition]
    for folder in keep:
        shutil.copytree(os.path.join(library, folder), os.path.join(copy, folder),
                        ignore=shutil.ignore_patterns(".work"))
    guide_path = os.path.join(copy, ".claude", "library-guide.md")
    agents_path = os.path.join(copy, "AGENTS.md")
    guide, agents = open(guide_path).read(), open(agents_path).read()
    if "reviews" not in keep:
        for index in glob.glob(os.path.join(copy, "library", "**", "README.md"), recursive=True):
            text = open(index).read()
            cut = re.sub(r"^Literature review: .*\n\n?", "", text, flags=re.M)
            if cut != text:
                open(index, "w").write(cut)
        guide = re.sub(r"^\| Literature review per area.*\n", "", guide, flags=re.M)
        guide = re.sub(RULE, "", guide, flags=re.M)
        agents = agents.replace(", `reviews/`", "")
        agents = re.sub(r"; the area's review\s+and its paper map are the quickest way to find those", "", agents)
    if "notes" not in keep:
        guide = re.sub(r"^\| Agent memory per paper.*\n", "", guide, flags=re.M)
        guide = re.sub(r"^- \*\*Check what is already known about a paper\.\*\*.*\n", "", guide, flags=re.M)
        guide = re.sub(r"^## Notes: agent memory per paper\n.*?(?=^## Topics)", "", guide, flags=re.M | re.S)
        agents = agents.replace(", `notes/`", "")
    open(guide_path, "w").write(guide)
    open(agents_path, "w").write(agents)
    lock(copy, True)
    left = {word: len(re.findall(word, guide + agents)) for word in ("reviews?/|[Rr]eview", "`?notes/")}
    print("%s (%s): %s; still mentioned in the instructions: %s" % (name, condition, copy, left))


def set_rule(rule_path, copy):
    guide_path = os.path.join(copy, ".claude", "library-guide.md")
    guide, rule = open(guide_path).read(), open(rule_path).read().strip() + "\n"
    changed, count = re.subn(RULE, lambda match: rule, guide, flags=re.M)
    if count != 1:
        sys.exit("the guide of %s has %d 'Start from the review' rules, expected 1" % (copy, count))
    lock(copy, False)
    open(guide_path, "w").write(changed)
    lock(copy, True)
    print("%s: rule replaced with %s" % (copy, rule_path))


def main():
    if sys.argv[1] == "--rule":
        return set_rule(sys.argv[2], os.path.abspath(sys.argv[3]))
    library, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    for spec in sys.argv[3:] or ["asis", "noreviews", "nonotes"]:
        name, _, condition = spec.partition("=")
        build(library, out, name, condition or name)


if __name__ == "__main__":
    main()
