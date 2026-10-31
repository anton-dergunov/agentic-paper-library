#!/bin/zsh
# Runs the five overviews and the KV-cache question on Haiku in $WORK/lib, in parallel, and
# keeps the replies, the overviews and the notes in $WORK/runs/<label>.
#   WORK=<dir> PDF_ROOT=<the library's pdf_root> ./run.sh <label>
L=$WORK/lib; O=$WORK/runs/$1; mkdir -p $O; cd $L
TOOLS=("Bash(paperlib *)" "Bash(find *)" "Bash(grep *)" "Bash(sed *)" "Bash(head *)" Read Write Edit Glob Grep)
run() { claude -p --model haiku --output-format json --add-dir "$PDF_ROOT" --allowedTools "${TOOLS[@]}" <<< "$2" > "$O/$1.json" 2> "$O/$1.err"; }
run dpo "/overview Direct Preference Optimization" &
run lora "/overview LoRA. Low-Rank Adaptation" &
run bm25 "/overview The Probabilistic Relevance Framework" &
run zep "/overview Zep. A Temporal Knowledge Graph" &
run judgebench "/overview JudgeBench" &
run kv "How does  KV cache work? Please find a paper that describes it, and tell me concisely and practically: how does it work. Also, what are the measurements? Ideally add links to some text passages, numbers, equations, tables, etc in your reply." &
wait
cp -R $L/overviews $O/overviews; cp -R $L/notes $O/notes
