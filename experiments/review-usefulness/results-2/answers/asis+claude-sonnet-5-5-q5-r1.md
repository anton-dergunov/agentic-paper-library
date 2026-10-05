The library has about ten papers on prompt compression. Most are in `llm/context/`, and the rest are in memory, parametric memory and vision. There is no review for `llm/context`, so this comes from the paper files and two existing notes. Only LLMLingua-2 and ICAE have notes, so the other numbers come straight from the papers' abstracts and limitations sections.

## Three ways to compress

| Family | Papers | Idea |
|---|---|---|
| **Hard prompts** (drop tokens or sentences, output is still text) | LLMLingua, LongLLMLingua, LLMLingua-2 | A small model decides which tokens to keep. This works with black-box APIs. |
| **Compression for retrieval** | RECOMP | Compress retrieved documents into an extractive or abstractive summary, trained so the end task improves. It can return an empty string when the documents don't help. |
| **Soft prompts** (learned vectors) | Gist tokens, ICAE | Train a model to turn a prompt or context into a few vectors that the LLM reads. This needs access to the weights. |

A fourth group is related but has a different goal. Cartridges and DeepSeek-OCR (compressing text into vision tokens) are in the memory and vision folders.

## How the main papers differ

- **LLMLingua** uses a small LM's perplexity to drop low-information tokens. It adds a budget controller and iterative token-level pruning. The abstract claims up to 20x compression with little loss. Its [limitations section (p. 9, Fig. 3)](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?page=9) says that all methods drop sharply at about 25–30x on GSM8K.
- **LongLLMLingua** makes this question-aware for long contexts and reorders documents to reduce lost-in-the-middle effects. Its claim is that compression can improve accuracy, because it raises the density of key information. LLMLingua-2 still falls short of it on LongBench. It scores 39.1 against 48.0 at a 2,000-token budget, so a task-aware method beats a task-agnostic one when the question is known.
- **LLMLingua-2** replaces perplexity with a small bidirectional encoder that classifies each token as keep or drop. It is trained on labels distilled from GPT-4. It is 3–6x faster than LLMLingua and generalises across target models.
  - [MeetingBank QA, p. 5, Table 1](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?page=5): EM 86.92 against 67.52 for LLMLingua and 87.75 for the full prompt.
  - [LongBench, p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?page=6): average 39.1 against 44.0 for the full prompt, so it stays below the original. The Synthetic subset is much worse (21.3 against 37.8).
  - On GSM8K and BBH it only ties LLMLingua (p. 6, Table 3).
  - My note flags the evidence as vendor-run. The authors also wrote the baselines, and the out-of-domain baseline numbers are copied from earlier papers.
- **RECOMP** compresses for RAG down to 6% of the retrieved text with minimal loss, on language modeling and open-domain QA ([abstract, p. 1](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?page=1)). Its selective augmentation, where an empty summary is allowed, is the part the token-dropping methods lack.
- **Gist tokens** compress instruction prompts into cacheable tokens by changing the attention mask during finetuning. The paper reports up to 26x compression on LLaMA-7B and FLAN-T5-XXL, but only 40% fewer FLOPs and 4.2% lower latency. It needs the weights and is trained for prompts, not for arbitrary context.
- **ICAE** writes 128 memory slots for a 512-token context (4x), using a LoRA-adapted copy of the LLM as the encoder.
  - Autoencoding is near-lossless (BLEU about 99).
  - On the same Llama-2-7b-chat, the compressed version loses more often than it wins against the original context: 45.4% lose to 19.6% win ([Table 4, p. 4–6](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?page=6)).
  - The evidence is one self-built benchmark with GPT-4 as judge, and it has no comparison against Gisting.

## Cross-paper observations

- **Practical limits:** the papers put the usable range at about 2–5x for most tasks and up to about 10x for extractive RAG compression. Beyond that, quality degrades fast. Cartridges makes the same point about other compression methods. In its experiments, prompt and KV-cache compression degrade quickly beyond 2x on hard long-context tasks.
- **Weak comparisons:** the results are not directly comparable across papers. Budgets differ, so LLMLingua-2's Table 1 uses 970 tokens against 1,176–1,222 for its baselines. Judges and benchmarks also differ.
- **Compression in memory systems:** LightMem uses LLMLingua-2 as a "pre-compression" step before building memory, so the method is now reused as a component.
- **Newer approaches** compress by training on the corpus itself (Cartridges, 38.6x less memory at ICL quality) or render text as an image (DeepSeek-OCR, 97% OCR accuracy below 10x and about 60% at 20x).

## Caveats

- The `llm/context` folder has no review, and four of the six core papers have no note. If you want a proper comparison, `paperlib read llm/context` would create the notes and a review could follow.
- I haven't checked whether the library covers newer work from 2025–26 on soft compression for agents or KV-cache methods. `llm/efficiency` and `llm/memory/parametric` are the next places to look.

I made no changes to the library.
