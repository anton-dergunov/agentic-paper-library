# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: generative LM pre-training of a decoder-only Transformer, then per-task discriminative fine-tuning (GPT-1)
evidence: 12 NLU datasets (NLI, QA/commonsense, similarity, classification; several via GLUE) against previously published task-specific models and ensembles, plus three ablations and an LSTM variant; strength: author-run, single model, baseline numbers taken from cited papers, no seeds or variance reported, ablations on GLUE tasks only, zero-shot analysis shown only as a figure
conversion: Eq. 5 (the combined fine-tuning objective) is missing, only "(5)" survives (p. 3); Table 1 is flattened, with all four task rows merged into one cell (p. 4); Table 2's CAFE single-model row has blank QNLI and RTE cells (pp. 5–7); table captions are duplicated; an author name and footnote 1 are displaced into the Introduction text (p. 1); Tables 2–5 otherwise look aligned

## Digest

- Two stages: unsupervised pre-training with a standard left-to-right LM objective L1 over a context window k (Eq. 1), then supervised fine-tuning with a linear output layer W_y on the final block's activation at the last token (Eqs. 3–4) (p. 3).
- Fine-tuning adds the LM loss as an auxiliary objective with weight λ; the equation itself is lost in conversion, and λ was set to 0.5 (p. 3; pp. 4–5).
- The only new fine-tuning parameters are W_y and the delimiter-token embeddings (p. 3).
- Task-specific input transformations replace task-specific architectures: entailment is premise + delimiter + hypothesis; similarity runs both orderings and adds the two representations element-wise; QA/commonsense builds [z; q; $; a_k] per answer, softmax-normalised across answers (p. 4).
- Architecture: 12-layer decoder-only Transformer with masked self-attention, 768 dimensional states, 12 attention heads, 3072 dimensional feed-forward inner states, GELU, learned position embeddings, BPE with 40,000 merges (pp. 4–5).
- Pre-training data: BooksCorpus, "over 7,000 unique unpublished books", chosen for long contiguous text, in contrast to the sentence-shuffled 1B Word Benchmark used by ELMo; token-level perplexity is 18.4 on this corpus, with no baseline given (pp. 4–5).
- Pre-training recipe: Adam, max learning rate 2.5e-4, linear warmup over the first 2000 updates then cosine annealing to 0, 100 epochs, minibatches of 64 sequences of 512 tokens, dropout 0.1, modified L2 with w = 0.01, init N(0, 0.02) (pp. 4–5).
- Fine-tuning recipe: learning rate 6.25e-5, batchsize 32, 3 epochs "for most cases", linear decay with warmup over 0.2% of training, classifier dropout 0.1 (pp. 4–5).
- Not disclosed: parameter count, compute or training time, corpus token count, how per-task hyperparameters were chosen where they differ from "most tasks", and the number of runs or their variance.
- Headline claim: new state of the art on 9 out of the 12 datasets, against task-specific architectures and in many cases ensembles (p. 1; pp. 5–7).
- NLI: MNLI-m 82.1 against 80.6 for Stochastic Answer Network (3x); MNLI-mm 81.4 against 80.1 for the same; SNLI 89.9 against 89.3 for ESIM+ELMo (5x) and CAFE (5x); SciTail 88.3 against 83.3 for CAFE; QNLI 88.1 against 82.3 for GenSen (pp. 5–7, Table 2).
- RTE is a loss: 56.0 against 61.7 for the multi-task BiLSTM + Attn; the authors attribute this to the small dataset (2490 examples) and suggest multi-task training, which was not tried (pp. 5–7, Table 2).
- QA/commonsense: Story Cloze 86.5 against 77.6 for Hidden Coherence Model; RACE 59.0 against 53.3 for BiAttention MRU (9x), with RACE-m 62.9 against 60.2 and RACE-h 57.4 against 50.3 (pp. 5–7, Table 3).
- GLUE: CoLA 45.4 against 35.0 for single-task BiLSTM+ELMo+Attn; STS-B 82.0 against 81.0 for the ECNU mixed ensemble; QQP 70.3 against 66.1 for single-task BiLSTM+ELMo+Attn; overall 72.8 against the previous best 68.9 (pp. 5–7, Table 4).
- Not state of the art: SST-2 91.3 against 93.2 for Sparse byte mLSTM, and MRPC 82.3 against 86.0 for TF-KLD (pp. 5–7, Table 4).
- Internal inconsistencies: the Introduction claims a 5.5% GLUE improvement (pp. 1–2) while the printed scores are 72.8 against 68.9 (pp. 5–7); MNLI is 82.1 for MNLI-m in Table 2 but 81.8 for the full model in Table 5 (pp. 7–8).
- Ablation, no pre-training: average score 59.9 against 74.7 for the full model, described as a "14.8% decrease", and worse on every task, e.g. STS-B 30.9 against 82.0 (pp. 7–8, Table 5).
- Ablation, no auxiliary LM: average 75.0 against 74.7 for the full model, so the auxiliary objective does not help on average; the authors say it helps on the NLI tasks and QQP, i.e. the larger datasets (pp. 7–8, Table 5).
- Ablation, single-layer 2048-unit LSTM in the same framework: average 69.1 against 74.7 for the Transformer, a "5.6 average score drop"; the LSTM wins only on MRPC, 83.2 against 82.3 (pp. 7–8, Table 5).
- Layer transfer and zero-shot: each transferred layer helps, "up to 9%" on MultiNLI for full transfer against transferring none; zero-shot heuristics on CoLA, SST-2, RACE and DPRD improve steadily over pre-training and the LSTM shows higher variance, but both results appear only in Figure 2 with no numbers in the text (pp. 7–8, Figure 2).

## Related

- Vaswani et al., Transformer [62]: the base architecture, changed here to decoder-only with learned rather than sinusoidal position embeddings.
- Liu et al., Transformer decoder [34]: the decoder-only variant used as the language model.
- ELMo, Peters et al. [44]: the closest contemporary; it feeds pre-trained LM representations as features into task-specific architectures, whereas this paper fine-tunes one model, and it is beaten on SNLI.
- Howard and Ruder (ULMFiT) [21] and Dai et al. [13]: earlier LM pre-training plus fine-tuning with LSTMs, for text classification only; this paper argues LSTMs limit range and covers more task types.
- Rei [50]: the source of the auxiliary LM objective during supervised training.
- Rocktäschel et al. [52]: the traversal-style approach behind the single-sequence input transformations.
- GLUE, Wang et al. [64]: the benchmark and the source of the BiLSTM+ELMo+Attn baselines; the previous best overall score of 68.9 is the one compared against.
- CAFE [58], Stochastic Answer Network [35], BiAttention MRU [59], Dynamic Fusion Net [67]: the task-specific and ensemble models used as prior state of the art on NLI and RACE.
- BooksCorpus, Zhu et al. [71]: the pre-training corpus.
