Your library has six papers squarely on this (all in `llm/context/`), plus a handful that use or stress-test compression. The short version: **dropping text is cheap and works with any API model, but only reliably helps when it knows the question. Compressing into vectors reaches higher ratios but needs model access and has only been tested on small models.**

There is no review for `llm/context/` yet, and four of the six core papers have no note, so I read those four from the paper text.

## The three ways to compress

A toy example (mine, not from a paper): a 3,000-token prompt of 20 retrieved passages plus a question.

- **Delete tokens.** A small model scores each token and the low scorers are dropped; the result is broken text that the LLM can still read.
- **Rewrite or select.** A small model picks the useful sentences or writes a short query-focused summary.
- **Replace with vectors.** The prompt becomes a few learned embeddings or a trained KV cache; nothing readable remains.

| Paper | Family | Sees the question? | Headline, with its baseline |
|---|---|---|---|
| LLMLingua | delete, by small-LM perplexity | no | GSM8K EM 79.08 at 5x and 77.33 at 20x, against 78.85 for the full prompt ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.2&page=6)) |
| LongLLMLingua | delete, question-conditioned, with reordering | yes | NaturalQuestions at 4x, gold document in 10th position: 71.2 against 54.1 for the original prompt ([p. 6, Table 1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.1&page=6)) |
| LLMLingua-2 | delete, by a trained encoder classifier | no | MeetingBank QA 86.92 at 3.1x against 87.75 original; compressor takes 0.4–0.5 s against 1.5–2.9 s for LLMLingua ([p. 5, Table 1](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.1&page=5); p. 8, Table 5) |
| RECOMP | select or summarise, trained on reader accuracy | yes | NQ EM 37.04 with 36 tokens against 39.39 with 660 tokens of top-5 documents ([p. 7, Table 2](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.2&page=7)) |
| Gisting | vectors: one "gist" token via attention masking | no | 26x on short instructions; humans prefer the gist model 52.3% of the time on 100 examples ([p. 5, Table 2](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=table.2&page=5)) |
| ICAE | vectors: 128 memory slots from a LoRA encoder | no | 4x; against the same model with the full context it wins 19.6% and loses 45.4% ([p. 4–6, Table 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=table.4&page=5)) |

## What the evidence supports

- **Question-blind deletion fails on retrieval prompts.** In LongLLMLingua's own table, LLMLingua scores 39.7–42.3 on NaturalQuestions at 2x, below the 56.1 of asking with no documents at all (p. 6, Table 1).
- **LongLLMLingua's gain is mostly reranking.** Its document ranker alone reaches 46.3 on LongBench against 48.3 for the full method and 44.0 uncompressed (p. 6, Table 2). The "compression beats the original" result is largely a lost-in-the-middle fix; that reading is mine.
- **Compression can remove distractors.** RECOMP's reader copies a wrong answer from context 81% of the time with five documents and 39% with its summary (p. 8, Table 3). An oracle single sentence gets 60.22 EM on NQ, so the headroom is in selection.
- **Vector methods are weaker than their abstracts suggest.** Gisting saves 40% of FLOPs only against no caching; against ordinary KV caching it saves 0.11% (p. 8). It also loses details that must be copied verbatim (p. 7).
- **Per-corpus training goes furthest.** Cartridges match in-context quality at 38.6x less memory, but cost about 30 minutes on 8 H100s per corpus (p. 1, 12, from the note).

## Where independent papers push back

- **Selection beats compression at a tight budget.** At 160 tokens on HotpotQA, LLMLingua-2 gets 0.326 F1, plain top-k packing 0.400 and a redundancy-aware packer 0.451 ([Recall Is Not Enough, p. 6, Table 3](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?dest=table.3&page=6)). This is a 2026 preprint with a 3B reader.
- **Agent-memory results are mixed.** One paper finds LLMLingua-2 pruning lowers LoCoMo F1 from 36.48 to 34.58 ([Beyond RAG for Agent Memory, §5.3, Table 3](http://pdf.invalid/llm/memory/agent/Beyond%20RAG%20for%20Agent%20Memory.%20Retrieval%20by%20Decoupling%20and%20Aggregation.pdf?dest=table.3&page=8)). SeCom, from the LLMLingua group, finds removing it costs about 9 points (69.33 to 59.87; p. 7, Table 2, from the note).
- **Repeated summarising degrades.** ACE reports a context collapsing from 18,282 tokens to 122 in one rewrite, with accuracy falling from 66.7 to 57.1 ([p. 3](http://pdf.invalid/llm/context/Agentic%20Context%20Engineering.%20Evolving%20Contexts%20for%20Self-Improving%20Language%20Models.pdf?page=3&search=context%20collapse)).

## What is dated or thin

- The LLMLingua line is all from one Microsoft group, tested on GPT-3.5-era readers, and LLMLingua-2's out-of-domain baselines were copied rather than re-run.
- ICAE and Gisting stop at 7–13B models and are never compared with each other.
- DeepSeek-OCR (rendering text as an image, about 97% decoding precision under 10x) is in the library, but I read only its abstract.
- Recursive Language Models uses a compaction agent as a baseline; I did not check those numbers.

Nothing was changed in the library. The four un-noted papers (LLMLingua, LongLLMLingua, Gisting, RECOMP) are worth a `paperlib read`, and this comparison would be the core of a review for `llm/context/`.
