#!/bin/zsh
cd "$(dirname "$0")"
V=~/.cache/papers/venvs
for s in larimar dpo hipporag kosinski; do
  t=$(date +%s)
  $V/marker/bin/marker_single pdf/$s.pdf --output_dir marker --output_format markdown > marker/$s.log 2>&1 && r=ok || r=FAILED
  echo "marker\t$s\t$(($(date +%s)-t))s $r" >> times.tsv
done
for s in memlayers larimar simpo metalearn zep textpred dpo hipporag kosinski; do
  t=$(date +%s)
  $V/mineru/bin/mineru parse pdf/$s.pdf -p all --tier advanced --wait 3600 -o mineru/$s.md > mineru/$s.log 2>&1 && r=ok || r=FAILED
  echo "mineru\t$s\t$(($(date +%s)-t))s $r" >> times.tsv
done
echo rest2-done >> times.tsv
