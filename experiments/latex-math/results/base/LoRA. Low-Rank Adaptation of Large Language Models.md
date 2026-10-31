---
title: "Low-Rank Adaptation of Large Language Models"
aliases: [LoRA]
authors: [Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, et al.]
affiliations: [Microsoft]
year: 2021
type: method
topic: llm/post-training/fine-tuning
links:
  - https://arxiv.org/abs/2106.09685
  - https://github.com/microsoft/LoRA
concepts: ["[[Full fine-tuning]]", "[[Low-rank matrix factorisation]]", "[[Intrinsic dimension]]", "[[Parameter-efficient fine-tuning]]"]
papers: ["[[Adapter layers]]", "[[QLoRA]]", "[[DoRA]]", "[[LoRA Learns Less and Forgets Less]]"]
tags: [roberta, deberta, gpt-2, gpt-3, glue, e2e-nlg, wikisql, mnli, samsum, attention-matrices]
read: false
analyzed: false
queued: false
revisit: false
reproduce: false
---

> [!abstract]
> Fine-tune a huge language model by training a tiny add-on instead of its whole body, with no slowdown when it runs.

## Overview

### Setting

Adapting one large pretrained language model to many tasks, where each task would normally get its own full-size copy of the model. The copy has to stay as good as retraining everything, but be cheap to store and swap.

### Motivation

Full fine-tuning updates every weight, so each task costs a whole model's worth of storage and memory. At the scale of a 175-billion-parameter model, that is impractical. The earlier fixes each cost something: [[Adapter layers]] add small modules that run one after another and slow inference, and [[Prefix tuning]] spends part of the input length on learned tokens and is hard to optimise.

**Freeze the model and learn only the change.** The paper bets that the change a task needs is simple: it is a low-rank matrix, which can be written with very few numbers. A matrix has low rank when its rows are mostly combinations of a few patterns, so it can be stored as two thin matrices instead of one full grid.

### Method

Each weight matrix that gets adapted gains a side path:

1. **Freeze** the pretrained weight W. It never changes.
2. **Add** a thin side path made of two small matrices, B and A, whose product BA is the update.
3. **Start** B at zero, so the model begins exactly as the pretrained one.
4. **Train** only A and B on the new task.
5. **Merge** BA into W after training, so the deployed model has the original shape again.

```
          x
    ┌─────┴──────────────┐
    │                    │
 W (frozen)        A, then B
    │             (small, trained;
    │              B starts at zero)
    └──────────(+)───────┘
               │
          h = Wx + BAx
```

Notice that the side path starts at zero, so the first output is the pretrained model's. Once training ends, BA is folded into W and the side path disappears.

### Why it works

- **Low-rank update** ([[Low-rank matrix factorisation]]): BA has far fewer numbers than W, and the paper's experiments suggest the needed change fits in a few directions.
- **Zero start for B**: training begins at the pretrained model, so nothing is disturbed before learning starts.
- **Merge after training**: the side path folds into W, so the deployed model costs what the original does. Adapters cannot do this, because they add layers.
- **Attention matrices only**: the paper adapts the query and value projections of attention. A small budget spread over two matrices beats the same budget on one.

### Applications and results

| Domain | Task, in plain words | Outcome |
|---|---|---|
| Language understanding | GLUE: sentence pairs, entailment, sentiment, on RoBERTa and DeBERTa | Matches or slightly beats full fine-tuning, with a fraction of the trainable parameters |
| Data to text | E2E: turning restaurant attributes into descriptions, on GPT-2 | Beats full fine-tuning and the prefix method |
| Text to SQL | WikiSQL: questions into database queries, on GPT-3 175B | Roughly matches full fine-tuning |
| Dialogue summaries | SAMSum: summarising chats, on GPT-3 175B | Beats full fine-tuning |

### Evidence

- **Broad benchmarks:** four model families and five task sets, from GLUE to SAMSum.
- **Matched baselines:** full fine-tuning, adapters and prefix methods, in the same setups.
- **Thin ablations:** the study of which matrices and which rank runs on one model and two tasks.
- **Rank claim is empirical:** the low-rank argument rests on a subspace-overlap check between two runs, not on theory.
- **Limits:** the main results adapt attention only. The paper warns that a rank of one may not suffice for a task far from pretraining, such as a new language. Merged weights also cannot serve several tasks in one batch.

### Novelty

- vs [[Adapter layers]]: the same bottleneck idea, but the update merges into the weights, so inference gets no slower.
- vs [[Prefix tuning]]: adds no tokens to the input, so the usable context stays the same, and it is easier to optimise.
- vs [[Intrinsic dimension]] (Aghajanyan et al.): the paper takes the low-dimension hypothesis behind that work and turns it into a method on weight updates.
- Later work: [[QLoRA]] and [[DoRA]] build on it. A later study finds it falls short of full fine-tuning on code and math with modern models (not from the paper).

### Concepts

- [[Full fine-tuning]]: updating every weight of the model; the baseline here.
- [[Low-rank matrix factorisation]]: writing a grid of numbers as a product of two thin grids.
- [[Intrinsic dimension]]: the idea that learning a task needs movement in only a few directions.
- [[Parameter-efficient fine-tuning]]: methods that train a small share of the parameters.

## Questions

- Why can a low-rank change capture what a full fine-tune learns?
- Why does B start at zero, and A does not?
- Why is it safe to fold BA into the weights after training?
- Would a rank-one update work for a task far from pretraining?
- Why adapt attention matrices rather than the feed-forward layers?

## Follow-ups

**Read**:
- [[Parameter-Efficient Transfer Learning for NLP]]: the adapter baseline; the idea LoRA keeps, minus the added latency.
- [[QLoRA]]: the same low-rank update on a compressed base model, to save memory.
- [[LoRA Learns Less and Forgets Less]]: a later check of LoRA against full fine-tuning on code and math.
- [[Intrinsic dimension]]: Aghajanyan et al., the hypothesis this paper builds on.

**Try**:
- Wrap one linear layer in PyTorch with a frozen weight, a random A and a zero-initialised B. Train it on a toy regression, merge BA into the weight, and check the outputs match.
