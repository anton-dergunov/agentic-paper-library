Your library has about ten papers on this, mostly in `llm/context`. Together they say that compression reliably saves tokens, but it improves answers only when it acts as question-aware selection, and it is close to lossless only up to roughly 4–10x unless the content is redundant.

The intuition: there are three ways to shrink a prompt.

| Family | How it works | Papers | Headline |
|---|---|---|---|
| Drop tokens | A small model scores each token and the low-value ones are deleted; works with API-only models | LLMLingua, LongLLMLingua, LLMLingua-2 | 2–20x |
| Rewrite as a summary | A trained compressor selects sentences or writes a short summary of the retrieved documents | RECOMP | about 5% of tokens kept |
| Replace text with vectors | The prompt becomes a few learned activations, so it needs access to the model's weights | Gist tokens, ICAE, Cartridges, DeepSeek-OCR (text as image) | 4–26x, more for a reused corpus |

**What the papers find**

- **Redundant prompts compress very well.** LLMLingua keeps GSM8K accuracy at 77.3 with a 20x shorter few-shot prompt, against 78.9 for the full prompt, but collapses at 25–30x ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.2&page=6)). My reading of that table: simply keeping one demonstration already scores 77.1 at 6x, so much of the gain is dropping examples.
- **Question-blind compression fails on retrieval prompts.** On NaturalQuestions with 20 documents, LLMLingua scores 39.7 at 2x, below the 56.1 with no documents at all. LongLLMLingua, which scores documents against the question, reaches 71.2 at 4x with the gold document in 10th position, against 54.1 uncompressed ([p. 6, Table 1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.1&page=6)).
- **That gain is mostly reranking.** LongLLMLingua's document ranker alone gets 69.3, and with the gold document first the original prompt is just as good (75.7 against 75.0). The cost is recompressing per question, so nothing can be cached (p. 9).
- **There is large headroom in selection.** In RECOMP, a 36-token summary gives 37.0 EM on NaturalQuestions against 39.4 for five full documents at 660 tokens, while the single best sentence would give 60.2 ([p. 7, Table 2](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.2&page=7)). Its compressor transfers poorly to another model (p. 8).
- **A trained classifier beats perplexity scoring.** LLMLingua-2 is 3–6x faster than LLMLingua and better on MeetingBank, but still below the task-aware LongLLMLingua on LongBench (39.1 against 48.0) and tied with LLMLingua on GSM8K ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.2&page=6)).
- **Vector compression loses exact detail.**
  - Gist tokens reach 26x only on instructions of about 20 tokens, lose verbatim wording, and save just 1% wall time over ordinary KV caching ([p. 8](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)).
  - ICAE at 4x loses to the same model with the full context more often than it wins: 45.4% against 19.6% ([p. 6, Table 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=table.4&page=6)).
  - DeepSeek-OCR recovers 97% of text below 10x and about 60% at 20x (p. 1).
- **Paying offline buys much more.** Cartridges match full-context quality at 38.6x less memory, but need about 30 minutes on 8 H100s per corpus (p. 12).
- **Latency gains trail token savings.** 5x fewer tokens gives a 3.3x speedup in LLMLingua (p. 8, Table 6), and 2–5x gives 1.6–2.9x in LLMLingua-2 (p. 8, Table 5).

**Where compression hurts**

- **Destroyed answer spans.** "Recall Is Not Enough" reports that LLMLingua-2 lowers accuracy when it deletes the answer span, and that a budgeted packer beats it at equal cost (p. 1; I read only the abstract and introduction).
- **Repeated summarisation.** ACE calls the erosion "context collapse" (p. 1), and Recursive Language Models beat compaction by a median 26% on GPT-5 (p. 1).
- **Memory systems.** LLMLingua-2 as a denoiser helps retrieval in SeCom (59.9 to 69.3 on LoCoMo, p. 7), but xMemory finds LightMem's compression weaker on multi-hop and temporal questions (p. 6).

**How far to trust this**

- The three LLMLingua papers come from one Microsoft group that also ran the baselines, target GPT-3.5-era models, and report no variance.
- No paper here compares token-dropping against vector methods head to head.
- Nothing here weighs compression against provider-side prompt caching.

Four of the core papers (LLMLingua, LongLLMLingua, Gist tokens, RECOMP) have no note in `notes/` yet; I read them directly for this answer and changed nothing in the library.
