#!/bin/zsh
cd "$(dirname "$0")"
V=~/.cache/papers/venvs
python3 run_docling.py plain 2>/dev/null >> times.tsv
python3 run_docling.py formula 2>docling-formula.err >> times.tsv
mkdir -p marker mineru
for pdf in pdf/*.pdf; do
  s=$(basename $pdf .pdf); t=$(date +%s)
  $V/marker/bin/marker_single $pdf --output_dir marker --output_format markdown > marker/$s.log 2>&1 && r=ok || r=FAILED
  echo "marker\t$s\t$(($(date +%s)-t))s $r" >> times.tsv
done
for pdf in pdf/*.pdf; do
  s=$(basename $pdf .pdf); t=$(date +%s)
  $V/mineru/bin/mineru -p $pdf -o mineru -b pipeline > mineru/$s.log 2>&1 && r=ok || r=FAILED
  echo "mineru\t$s\t$(($(date +%s)-t))s $r" >> times.tsv
done
echo done >> times.tsv
