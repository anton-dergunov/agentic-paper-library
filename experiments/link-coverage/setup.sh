#!/bin/zsh
# Builds a small copy of a library in $WORK/lib with the papers in papers.txt, their notes, the
# catalog, the reviews and the reader's AGENTS.md, as a git repository that run.sh clones for
# each answer. The PDFs are copied once into $WORK/pdf, outside the repository; each clone links
# that folder as its pdf_root, so `paperlib locate` prints library-relative links.
#   LIBRARY=<library> WORK=<scratch dir> ./setup.sh
set -eu
HERE=${0:A:h}; L=$WORK/lib; mkdir -p $L $WORK/pdf
PDF_ROOT=$(cd $LIBRARY && python3 -c "import yaml,os;print(os.path.expanduser(yaml.safe_load(open('paper-library.yaml'))['pdf_root']))")
while IFS= read -r p; do
  mkdir -p "$L/library/${p:h}" "$WORK/pdf/${p:h}" $L/notes
  cp "$LIBRARY/library/$p.txt" "$L/library/$p.txt"
  cp "$PDF_ROOT/$p.pdf" "$WORK/pdf/$p.pdf"
  [ -f "$LIBRARY/notes/${p:t}.md" ] && cp "$LIBRARY/notes/${p:t}.md" $L/notes/
done < $HERE/papers.txt
cp -R $LIBRARY/catalog $LIBRARY/reviews $LIBRARY/AGENTS.md $LIBRARY/CLAUDE.md $L/
touch $L/INBOX.txt
printf 'reader: %s\npdf_root: pdf\n' "$(cd $LIBRARY && python3 -c "import yaml;print(yaml.safe_load(open('paper-library.yaml')).get('reader','the reader'))")" > $L/paper-library.yaml
printf 'pdf\n' > $L/.gitignore
(cd $L && git init -q && git add -A && git -c user.name=x -c user.email=x@x commit -qm baseline)
