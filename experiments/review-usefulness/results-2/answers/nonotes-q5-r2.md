Six papers in `llm/context/` are about prompt compression directly, and five more elsewhere test or reuse it. Together they say compression is cheap and works well on redundant text, but the claim that it beats simply selecting the right evidence is weakly supported.

## The idea

A prompt is mostly words the model could have guessed. The papers differ in what they replace the prompt with:

- **Fewer of the same tokens** (LLMLingua family): delete words, keep the rest verbatim. Works with any API model.
- **A shorter text** (RECOMP): a summary or a few selected sentences. Also works with any model.
- **A few vectors** (gist tokens, ICAE): the prompt becomes activations the model attends to. This needs access to the model's weights.

## Deleting tokens

- **LLMLingua** scores each token with a small LM and drops the predictable ones, re-scoring as it goes so each token is judged given what was already kept.
  - On GSM8K it reaches 20x compression for about 1.5 points of exact match, but BBH loses 8.5 to 13 points at only 5–7x ([p. 6, §5.2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=subsection.5.2&page=6)).
  - Every method falls off a cliff around 25–30x ([p. 9, Figure 3](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=figure.3&page=9)).
  - The iterative scoring and the per-component budget each carry 5–6 points; aligning the small LM to the target model adds about half a point ([p. 7, Table 3](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.3&page=7)).
  - Asking GPT-4 to write a shorter prompt did worse, because it dropped reasoning steps.
- **LongLLMLingua** makes this question-aware for RAG-style prompts.
  - It ranks documents by how well each one predicts the question, and scores tokens by how much the question changes their perplexity ([p. 3, §4.1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=subsection.4.1&page=3)).
  - It also reorders documents to counter lost-in-the-middle, and restores names mangled by deletion.
  - It reports +21.4% on NaturalQuestions with about 4x fewer tokens, while question-blind LLMLingua scores below zero-shot there ([p. 6, main results](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?page=6)).
  - The cost is that every new question needs a fresh compression, so nothing can be cached ([p. 9, Limitation](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?page=9)).
- **LLMLingua-2** argues perplexity is the wrong signal, since it sees only left context and was never trained to compress.
  - It trains a 355M bidirectional encoder to label each word keep or drop, on GPT-4 compressions of meeting transcripts restricted to deleting words ([p. 5, §4](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=section.4&page=5)).
  - It is 3–6x faster than the earlier methods and uses 2.1 GB of GPU memory instead of 16.6 GB.
  - It still loses to LongLLMLingua on LongBench, because it ignores the question ([p. 8](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?page=8)).

## Rewriting as shorter text

**RECOMP** trains the compressor on whether its output helps the reader model answer, not on summary quality. It has a sentence selector and a summariser distilled from a large LM, and either can return nothing when retrieval would not help.

- It gets down to 6% of the tokens with minimal loss ([p. 1, abstract](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?page=1)).
- With five full documents the reader copies a wrong span 81% of the time; with RECOMP's compressor, 39% ([p. 8, §6](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.6&page=8)).
- Its own summaries are less faithful than GPT-3.5's, and worst on multi-hop HotpotQA (p. 9).

## Compressing into vectors

- **Gist tokens** change only the attention mask during instruction fine-tuning, so later tokens see the instruction only through one or a few gist tokens.
  - It reaches up to 26x compression and 40% fewer FLOPs.
  - Against ordinary KV caching of the full prompt the speedup is about 1%, so the real gain is cache storage ([p. 8, §6](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)).
  - It fails when the instruction holds details to be copied verbatim ([p. 7, §5.1](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=subsection.5.1&page=7)).
- **ICAE** scales this from short instructions to contexts: a LoRA-adapted encoder turns 512 tokens into 128 memory slots that the unmodified LLM reads.
  - Pretraining the encoder to reconstruct and continue text is what makes it work.
  - Its slots beat a GPT-4 summary of the same length about 2 to 1, but still lag the full context ([p. 6, §3.2.2](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=subsubsection.3.2.2&page=6)).

## What later papers found

- **As a denoiser:** SeCom runs LLMLingua-2 over memory units before retrieval and gets higher recall ([§1, Figure 3](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=figure.3&page=1)). LightMem finds that keeping 50–80% of tokens matches uncompressed accuracy on LongMemEval ([p. 8, §5.3](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?dest=subsection.5.3&page=8)).
- **Against selection:** "Recall Is Not Enough" finds LLMLingua-2 loses even to naive top-k packing at the same budget, because dropping tokens destroys the answer span ([p. 6](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?page=6)). That is one setting: HotpotQA, a 160-token budget and a 3B reader.
- **On hard long-context tasks:** Cartridges finds summarisation and truncation degrade beyond 2x on LongHealth and QASPER, where a trained KV cache holds quality at 10–100x less memory ([p. 9, §5.1](http://pdf.invalid/llm/memory/parametric/Cartridges.%20Lightweight%20and%20general-purpose%20long%20context%20representations%20via%20self-study.pdf?dest=subsection.5.1&page=9)).
- **Through pixels:** DeepSeek-OCR renders text as an image and recovers it at about 97% precision under 10x, falling to about 60% at 20x ([p. 10, §4.1](http://pdf.invalid/llm/vision-and-multimodal/vision-language/DeepSeek-OCR.%20Contexts%20Optical%20Compression.pdf?dest=subsection.4.1&page=10)). That measures reconstruction, not task accuracy.

## What is weak or dated

- **Headline ratios are task-specific.** The 20x figure is few-shot GSM8K, where the demonstrations are highly redundant; the papers' own numbers on BBH, and Cartridges' on long documents, are far lower.
- **"Compression improves accuracy" is mostly reranking.** LongLLMLingua's gain comes with the gold document buried at position 10 for GPT-3.5-Turbo. None of these papers tests whether it survives with current long-context models.
- **Small, old models.** Gist and ICAE are shown on LLaMA-7B to 13B, and LLMLingua-2 is trained on one domain (meeting transcripts).
- **Prompt caching undercuts the cost argument.** Gist's own 1% number shows this, and question-aware compression cannot be cached at all.

The library lacks Selective-Context and AutoCompressors, the baselines nearly all of these papers compare against, and the prompt-compression survey that the context-engineering survey cites.
