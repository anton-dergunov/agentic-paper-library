#!/bin/zsh
# Builds a small copy of a library in $WORK/lib with the papers in papers.txt, their notes,
# the catalog, the reviews and the reader's AGENTS.md, with overview_dir inside it, so that
# the overview skill and `paperlib read` write nowhere else. The copy is a git repository,
# so reset.sh can put it back after each run.
#   LIBRARY=<library> WORK=<scratch dir> ./setup.sh
set -eu
HERE=${0:A:h}; L=$WORK/lib; mkdir -p $L
PDF_ROOT=$(cd $LIBRARY && python3 -c "import yaml,os;print(os.path.expanduser(yaml.safe_load(open('paper-library.yaml'))['pdf_root']))")
while IFS= read -r p; do
  mkdir -p "$L/library/${p:h}" "$L/pdf/${p:h}" $L/notes
  cp "$LIBRARY/library/$p.txt" "$L/library/$p.txt"
  ln -sf "$PDF_ROOT/$p.pdf" "$L/pdf/$p.pdf"
  [ -f "$LIBRARY/notes/${p:t}.md" ] && cp "$LIBRARY/notes/${p:t}.md" $L/notes/
done < $HERE/papers.txt
cp -R $LIBRARY/catalog $LIBRARY/reviews $LIBRARY/AGENTS.md $LIBRARY/CLAUDE.md $L/
touch $L/INBOX.txt
printf 'reader: %s\npdf_root: pdf\noverview_dir: overviews\n' "$(cd $LIBRARY && python3 -c "import yaml;print(yaml.safe_load(open('paper-library.yaml')).get('reader','the reader'))")" > $L/paper-library.yaml
mkdir -p $L/.claude/skills/overview
(cd $L && git init -q && paperlib build-index >/dev/null && git add -A && git -c user.name=x -c user.email=x@x commit -qm baseline)
