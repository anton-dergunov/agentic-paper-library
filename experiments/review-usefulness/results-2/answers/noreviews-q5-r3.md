Your library has six papers squarely on prompt compression, all in `llm/context/`, plus a handful that use or test it. Together they say: compression works well on redundant prompts, token pruning that ignores the question fails on retrieval QA, and the later independent tests are less favourable than the method papers.

## Two families

Take a 2,400-token prompt of eight worked maths examples plus a question.

- **Hard (text) compression** deletes or rewrites text, so the result is still a prompt any API model can read. LLMLingua keeps the highest-perplexity demonstrations, then drops the tokens a small LM finds most predictable.
- **Soft compression** replaces the text with a few learned vectors that only the trained model can read. Gisting squeezes an instruction into one "gist" token's activations; ICAE writes 512 tokens into 128 memory slots.

## The six core papers

| Paper | Mechanism | Headline | Caveat |
|---|---|---|---|
| Gisting (2023) | Attention mask forces everything after the gist tokens to see the prompt only through them | 26x; humans prefer the gist model 52.3% of the time against the uncompressed control ([p. 5, Table 2](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=table.2&page=5)) | Prompts average about 20–26 tokens; against ordinary KV caching it saves 0.11% FLOPs and 1% wall time ([p. 8](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)) |
| ICAE (2023) | LoRA-adapted encoder writes memory slots for the frozen LLM | "4x compression" | Against the same model with the full context it loses 45.4% and wins 19.6% ([p. 4–6, Table 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=table.4&page=5)) |
| LLMLingua (2023) | Budget per prompt part, then iterative perplexity-based token pruning | GSM8K 79.08 at 5x and 77.33 at 20x, against 78.85 for the full prompt ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.2&page=6)) | BBH falls from 70.07 to 56.85 at 7x; quality collapses at 25–30x (p. 9) |
| LongLLMLingua (2023) | Ranks documents by how well each predicts the question, reorders them, prunes tokens by how much the question changes their perplexity | NaturalQuestions at 4x: 71.2 against 54.1 for the full prompt with the answer in the 10th document ([p. 5, Table 1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.1&page=5)) | Must recompress per question, so no caching, at twice LLMLingua's compute (p. 9) |
| RECOMP (2023) | Trained sentence selector, or a T5 summariser distilled from GPT-3.5, that may return nothing | NQ: 37.04 EM from 36 tokens against 39.39 from 660 ([p. 7, Table 2](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.2&page=7)) | On HotpotQA only 67% of summaries are faithful, from 30 samples judged by the authors ([p. 9, Table 4](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.4&page=9)) |
| LLMLingua-2 (2024) | Small bidirectional encoder classifies each word keep/drop, trained on GPT-4 deletions | MeetingBank QA 86.92 against 87.75 uncompressed at 3.1x; 3–6x faster than LLMLingua | Ties LLMLingua on GSM8K and BBH; trails the full prompt on LongBench, 39.1 against 44.0 ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.2&page=6)) |

## What holds across papers

- **Redundancy is what gets compressed.** The best results are on few-shot demonstrations and meeting transcripts. LLMLingua's ablation shows the demonstration-level budget and iterative pruning carry the gain; aligning the small LM to the target adds 0.5 EM ([p. 7, Table 3](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.3&page=7)).
- **Question-blind pruning fails on retrieval QA.** On NaturalQuestions, LLMLingua and Selective-Context score 25–44, below the 56.1 of no documents at all (LongLLMLingua, p. 5, Table 1).
- **LongLLMLingua's win is mostly selection.** Without question-aware document ranking it falls from 77.2 to 42.1; without question-aware token pruning, only to 75.8 ([p. 7, Table 3](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.3&page=7)).
- **Less context can beat more.** RECOMP's oracle single sentence reaches 60.22 EM on NQ against 39.39 for five full documents, so the ceiling is high and the trained compressors are far below it.
- **Soft compression tops out near 4x for content.** ICAE's reconstruction degrades below 128 slots, and the authors call more than 4x "rather challenging". Gisting's 26x applies to short instructions and loses verbatim details such as a list of allowed categories (p. 7).

## Later tests are less kind

- *Recall Is Not Enough* (2026) runs LLMLingua-2 against plain packing at the same budget on HotpotQA: 0.326 F1 against 0.400 for naive top-k and 0.451 for its own packer. Token dropping destroys the answer span ([p. 6, Table 3](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?dest=table.3&page=6)). This is a 160-token budget with a 3B reader, so an extreme setting.
- *Beyond RAG for Agent Memory* finds LLMLingua-2 pruning on LoCoMo saves tokens (1,588 against 1,979) but lowers F1 from 36.48 to 34.58 ([p. 8, Table 3](http://pdf.invalid/llm/memory/agent/Beyond%20RAG%20for%20Agent%20Memory.%20Retrieval%20by%20Decoupling%20and%20Aggregation.pdf?dest=table.3&page=8)).
- *Rethinking Memory in LLM based Agents* reports a benchmark where context compression has the worst compression/accuracy trade-off, behind KV-cache quantisation and eviction (p. 15, Fig. 6).
- *Recursive Language Models* beats summarise-when-full compaction by a median 26% on GPT-5 (p. 1).

The one favourable outside use is as a denoiser for memory. In *On Memory Construction and Retrieval*, removing LLMLingua-2 before retrieval drops LoCoMo from 69.33 to 59.87 ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=table.2&page=7)), and LightMem builds on the same step. Both share authors or lineage with LLMLingua-2.

## Outdated or weakly supported

- **Old targets.** Everything is measured on GPT-3.5, Claude-v1.3, LLaMA-7B or Flan-UL2 with 4k–16k windows. None of the six tests a current long-context model or compares against provider prompt caching.
- **Vendor-run comparisons.** The three LLMLingua papers come from one Microsoft group that also wrote the baselines; LLMLingua-2 copies baseline numbers instead of re-running them.
- **Headline wording.** LongLLMLingua's "21.4%" boost is 21.4 points (75.5 with reordering against 54.1). ICAE's wins are against other models, not the same model uncompressed.

## Gaps

The library has no Selective-Context, AutoCompressors, xRAG or a compression benchmark, and the context-engineering survey names no token-pruning compressors at all (p. 25). Adjacent directions it does hold are Cartridges (a trained KV prefix per corpus, 38.6x less memory at in-context quality), Generative Adapter, and DeepSeek-OCR (text rendered as vision tokens, 97% decoding precision below 10x).

LLMLingua, LongLLMLingua, Gisting and RECOMP have no file in `notes/`; I read their main text for this answer but did not write notes. `paperlib read llm/context` would create them.
