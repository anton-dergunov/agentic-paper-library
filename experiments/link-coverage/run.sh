#!/bin/zsh
# Asks the seven questions in fresh sessions, each in its own clone of $WORK/lib with the guide
# of <engine> rendered into it, and keeps each session's stream in $WORK/runs/<label>/<q>.jsonl.
#   WORK=<dir> ./run.sh <label> <engine> <model>
set -eu
LABEL=$1; E=$2; MODEL=$3; O=$WORK/runs/$LABEL; mkdir -p $O
LME="library/llm/memory/benchmarks/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory.txt"
TOOLS=("Bash(paperlib *)" "Bash(find *)" "Bash(grep *)" "Bash(sed *)" "Bash(head *)" "Bash(cat *)" "Bash(ls *)" "Bash(wc *)" "Bash(awk *)" Read Write Edit Glob Grep)
run() {
  local L=$O/lib-$1
  rm -rf $L; git clone -q $WORK/lib $L; ln -s $WORK/pdf $L/pdf
  (cd $L && PAPER_LIBRARY=$L $E/bin/paperlib build-index >/dev/null)
  (cd $L && claude -p --model $MODEL --output-format stream-json --verbose --allowedTools "${TOOLS[@]}" <<< "$2" > "$O/$1.jsonl" 2> "$O/$1.err")
}
run lme-parts "[Reading $LME, page 2]
I want to understand what tasks are there in this dataset quickly. Tell me which parts I need to read. And which parts are the most useful overall." &
run lme-sizes "[Reading $LME, page 5]
What is the difference between longmemeval s and m and other versions?" &
run lme-con "[Reading $LME, page 6]
Describe in short chain of note and how it is used here" &
run completep "[Reading library/deep-learning/optimizers-and-schedules/Don't be lazy. CompleteP enables compute-efficient deep transformers.txt, page 1]
What is the main idea of this paper?" &
run topics "[Reading library/nlp/topic-models/A Survey on Neural Topic Models. Methods, Applications, and Challenges.txt, page 3]
Based on this paper, which model for topic modeling should be the default go to one nowadays?" &
run judgebench "[Reading library/llm/evaluation/methods/JudgeBench. A Benchmark for Evaluating LLM-based Judges.txt, page 1]
I want to understand how this benchmark is built quickly. Tell me which parts I need to read. And which parts are the most useful overall." &
run kv "How does  KV cache work? Please find a paper that describes it, and tell me concisely and practically: how does it work. Also, what are the measurements? Ideally add links to some text passages, numbers, equations, tables, etc in your reply." &
wait
