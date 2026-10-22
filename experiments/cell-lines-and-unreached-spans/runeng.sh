#!/bin/bash
# runeng.sh <engine root> <cached html dir> <outdir>
eng=$1; d=$2; out=$3; id=$(basename $d)
mkdir -p $out/$id
gunzip -c $d/index.html.gz > $out/$id/paper.html
PAPERLIB_ICONS=off timeout 300 python3 $eng/eng/html-to-markdown.py $out/$id/paper.html $out/$id/body.md $out/$id/images paper 2> $out/$id/stderr.txt
rm -f $out/$id/paper.html; rm -rf $out/$id/images
