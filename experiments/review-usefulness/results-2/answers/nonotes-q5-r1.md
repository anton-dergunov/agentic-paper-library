Your library covers prompt compression with seven core papers, and together they say this: compression of 2–5x is usually cheap and sometimes even helps, but the headline ratios (20x, 26x) hold only on redundant prompts. Later papers in the library show that compression loses to simply selecting better evidence when the answer hinges on a specific span.

## The intuition

A long prompt can be shortened at three levels. Take a GSM8K prompt with eight worked examples:

- **Delete text.** Drop whole examples, then drop predictable tokens from the rest; the result is ungrammatical but still readable by the model.
- **Rewrite text.** Replace retrieved documents with a short query-focused summary.
- **Replace text with vectors.** Encode the prompt into a few learned activations the model attends to instead of the tokens.

The first two work with API-only models; the third needs access to the weights.

## What each paper finds

| Paper | Mechanism | Headline result | Main catch |
|---|---|---|---|
| LLMLingua (2023) | A small LM scores tokens by perplexity; a budget controller protects the instruction and question and prunes demonstrations hardest | GSM8K matches the full prompt at 5x and loses about 1.5 EM at 20x | BBH loses 8.5 and 13.2 EM at 5x and 7x; everything collapses around 25–30x |
| LongLLMLingua (2023) | Makes the scoring question-aware and reorders documents by relevance | +21.4% on NaturalQuestions with about 4x fewer tokens | Must recompress per question, so nothing can be cached, at twice LLMLingua's compute |
| LLMLingua-2 (2024) | A BERT-size encoder classifies each token keep or discard, trained on GPT-4 extractive compressions of meeting transcripts | 3–6x faster than earlier compressors; 1.6–2.9x end-to-end speedup at 2–5x | Trails LongLLMLingua on LongBench because it ignores the question |
| RECOMP (2023) | Trained extractive and abstractive compressors between retriever and model; may return an empty string | Keeps 5% of tokens for a 2 EM loss on NQ | The abstractive compressor is weaker on multi-hop HotpotQA |
| Gist tokens (2023) | An attention mask forces everything after the gist tokens to see the instruction only through them | 26x compression, up to 40% fewer FLOPs | Only short instructions; against ordinary KV caching the saving is 0.11% FLOPs |
| ICAE (2023) | A LoRA-adapted encoder writes 512 tokens into 128 memory slots, pretrained by autoencoding | 4x compression, over 2x faster inference | Lossy: still behind the same model with the full context |
| Cartridges (2025) | Trains a small KV cache per corpus offline, by distilling the model's own behaviour with the corpus in context | Matches full-context quality with 38.6x less memory | Per-corpus training cost, worthwhile only when a corpus is queried repeatedly |

Sources, in table order:
- [LLMLingua, p. 4, §4.2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=subsection.4.2&page=4), [p. 6, §5.2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=subsection.5.2&page=6) and [p. 9, Limitations](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?page=9&search=Limitations)
- [LongLLMLingua, p. 3, §4.1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=subsection.4.1&page=3) and [p. 9, Limitation](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?page=9&search=Limitation)
- [LLMLingua-2, p. 5, §4](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=section.4&page=5) and [p. 8, out-of-domain results](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?page=8&search=falls%20short)
- [RECOMP, p. 7, open-domain QA](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.5&page=7)
- [Gist tokens, p. 3, §3](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.3&page=3) and [p. 8, §6](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)
- [ICAE, p. 4, §3.2.1](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=subsubsection.3.2.1&page=4) and [p. 6, §3.2.2](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=subsubsection.3.2.2&page=6)
- [Cartridges, p. 1, §1](http://pdf.invalid/llm/memory/parametric/Cartridges.%20Lightweight%20and%20general-purpose%20long%20context%20representations%20via%20self-study.pdf?dest=section.1&page=1) and [p. 9, §5.1](http://pdf.invalid/llm/memory/parametric/Cartridges.%20Lightweight%20and%20general-purpose%20long%20context%20representations%20via%20self-study.pdf?dest=subsection.5.1&page=9)

## Where the papers agree and disagree

- **Compression can improve accuracy, as a denoiser.** LongLLMLingua and RECOMP both beat the uncompressed prompt in places, because removing distractors helps the reader. SeCom finds the same for memory retrieval: compressing memory units with LLMLingua-2 raises retrieval recall ([SeCom, p. 1](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?page=1&search=denoising)).
- **Question-aware beats task-agnostic, but cannot be cached.** This trade-off is stated from both sides, by LongLLMLingua and by LLMLingua-2.
- **Asking a large model to summarise the prompt is a weak baseline.** LLMLingua finds GPT-4 drops reasoning steps, and RECOMP finds GPT-3.5 summaries make the reader copy a wrong answer 85% of the time, against 39% for its trained compressor ([RECOMP, p. 8, §6](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.6&page=8)).
- **Verbatim detail is the first casualty.** Gist tokens lose phrases that must be copied exactly ([p. 7, §5.1](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=subsection.5.1&page=7)), and LongLLMLingua needs a post-hoc step to restore mangled entity names in the response.
- **The strongest negative result is from 2026.** At equal token budget on HotpotQA, LLMLingua-2 loses to a submodular evidence packer by 0.125 F1, and even to naive packing by 0.075, because it destroys the answer span ([Recall Is Not Enough, p. 6, §5](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?dest=section.5&page=6)).
- **Cartridges reports the same limit on long documents.** Its prompt and KV-cache compression baselines degrade beyond about 2x on long-context tasks (p. 9, §5.1).

## What is dated or weakly supported

- **Old targets.** The 2023 results use GPT-3.5-Turbo, Claude-v1.3 and LLaMA-7B; nothing in the library tests token pruning against a current model with prompt caching.
- **Soft metrics.** LLMLingua's 9x on ShareGPT is judged by BERTScore, and the gist and ICAE results by ChatGPT or GPT-4 pairwise preference.
- **Narrow training data.** LLMLingua-2 is trained only on meeting transcripts; the authors' own test of adding 50k TriviaQA examples gave little gain.
- **The 26x figure.** It means a roughly 26-token instruction squeezed into one token, not long-context compression; ICAE makes this criticism directly ([ICAE, p. 8, §4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=section.4&page=8)).

## Adjacent papers

- **Agent-side compression.** Recursive Language Models reports a 26% median gain over summarise-when-full compaction on GPT-5 ([p. 1](http://pdf.invalid/llm/context/Recursive%20Language%20Models.pdf?page=1&search=compaction)), and Agentic Context Engineering names the failure "context collapse" ([p. 1](http://pdf.invalid/llm/context/Agentic%20Context%20Engineering.%20Evolving%20Contexts%20for%20Self-Improving%20Language%20Models.pdf?page=1&search=context%20collapse)).
- **Memory systems.** LightMem uses LLMLingua-2 as its pre-compressor ([p. 3](http://pdf.invalid/llm/memory/agent/LightMem.%20Lightweight%20and%20Efficient%20Memory-Augmented%20Generation.pdf?page=3&search=LLMLingua-2)). LongMemEval finds that compressing history into individual facts hurts overall but helps multi-session reasoning ([p. 1](http://pdf.invalid/llm/memory/benchmarks/LongMemEval.%20Benchmarking%20Chat%20Assistants%20on%20Long-Term%20Interactive%20Memory.pdf?page=1&search=information%20loss)).
- **Optical compression.** DeepSeek-OCR renders text as an image: 97% decoding precision below 10x, about 60% at 20x ([p. 1](http://pdf.invalid/vision-and-multimodal/vision-language/DeepSeek-OCR.%20Contexts%20Optical%20Compression.pdf?page=1&search=compression%20ratio)).

## Coverage and caveats

- **Missing baselines.** Selective-Context and AutoCompressors are cited as baselines by nearly every paper above, but neither is in the library or the skip list.
- **How I read.** I read the method, results and limitations prose of the seven core papers and only the matching passages of the adjacent ones; I did not check the numbers against the result tables.
- **Cartridges conversion.** It has an open conversion issue (an equation layout on p. 6 and a misplaced Figure 8); nothing quoted here comes from those parts.
