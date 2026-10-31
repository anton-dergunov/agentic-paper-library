#!/bin/zsh
# Puts $WORK/lib back to its first commit and installs an engine's overview skill, set to
# Haiku (the skill pins Opus), and its guide.   WORK=<dir> ./reset.sh [<engine>]
set -eu
E=${1:-${0:A:h:h:h}}; L=$WORK/lib
git -C $L checkout -q -- . && git -C $L clean -fdq
mkdir -p $L/.claude/skills/overview $L/overviews
cp $E/skills/overview/*.md $L/.claude/skills/overview/
sed -i '' 's/^model: opus$/model: haiku/' $L/.claude/skills/overview/SKILL.md
(cd $L && $E/bin/paperlib build-index >/dev/null)
