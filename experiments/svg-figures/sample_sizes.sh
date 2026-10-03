#!/bin/bash
# Sample papers with <object> figures and record the size of up to three SVGs each.
#
#   ./sample_sizes.sh <objects.tsv> <out dir>
#
# Takes a 5% random sample (awk srand(7), first 40) of the papers with objects,
# writes <out dir>/sample_ids.txt, <out dir>/sizes.txt ("<id> <svg path> <bytes>")
# and downloads each SVG to <out dir>/svgs/<n>.svg for threshold_sweep.py.
set -e
OBJ=$1; S=$2; mkdir -p "$S/svgs"
awk -F'\t' '$3>0' "$OBJ" | awk 'BEGIN{srand(7)} {if (rand()<0.05) print}' | head -40 | cut -f2 > "$S/sample_ids.txt"
: > "$S/sizes.txt"
while read id; do
  curl -s "https://arxiv.org/html/$id" | grep -o '<object[^>]*type="image/[^"]*"[^>]*data="[^"]*"' | grep -o 'data="[^"]*"' | head -3 | sed 's/data="//;s/"$//' | while read p; do
    sz=$(curl -s "https://arxiv.org/html/$p" | wc -c); echo "$id $p $sz" >> "$S/sizes.txt"; sleep 0.3
  done
done < "$S/sample_ids.txt"
awk '{print $3}' "$S/sizes.txt" | sort -n | awk '{a[NR]=$1; s+=$1} END{print NR" files; mean "int(s/NR/1024)"KB; median "int(a[int(NR/2)]/1024)"KB; p90 "int(a[int(NR*0.9)]/1024)"KB; max "int(a[NR]/1024)"KB"}'
i=0; while read id p sz; do i=$((i+1)); curl -s "https://arxiv.org/html/$p" -o "$S/svgs/$i.svg"; sleep 0.2; done < "$S/sizes.txt"
