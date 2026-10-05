Your library has a compact prompt-compression cluster in `llm/context`: six papers from 2023–24, plus a 2025 paper that tests one of them as a baseline. Together they say compression works well on redundant prompts, but dropping tokens can delete the one span that mattered.

**The intuition.** There are two families:

- **Hard compression** deletes text and sends the shorter prompt to any model, including API-only ones. A GSM8K few-shot prompt with its filler words stripped is unreadable to a person but still usable by GPT-4.
- **Soft compression** replaces the prompt with a few learned vectors. This needs access to the model's weights, and the vectors do not transfer between models.

## Hard compression (works with black-box models)

| Paper | Mechanism | Headline result | Weak spot |
|---|---|---|---|
| LLMLingua (2023) | A small LM scores tokens by perplexity and predictable ones are dropped, iteratively, with separate budgets for instruction, demonstrations and question. | 20x on GSM8K for a 1.5-point EM loss ([p. 6](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=subsection.5.2&page=6)). | BBH loses 8.5–13.2 points at 5–7x, and everything collapses around 25–30x ([p. 9](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?page=9&search=Limitations)). |
| LongLLMLingua (2023) | Makes scoring question-aware (how much the question changes a token's perplexity), then reorders documents to counter lost-in-the-middle. | +21.4% on NaturalQuestions with about 4x fewer tokens ([p. 6](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=section.5&page=6)). | Must recompress per question, so nothing can be cached, and it costs twice LLMLingua's compute ([p. 9](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?page=9&search=Limitation)). |
| LLMLingua-2 (2024) | Replaces the perplexity heuristic with a BERT-size keep/discard token classifier trained on GPT-4-compressed meeting transcripts. | 3–6x faster than earlier compressors; 1.6–2.9x end-to-end speedup at 2–5x compression ([p. 8](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=section.5&page=8)). | Being question-agnostic, it trails LongLLMLingua on LongBench (p. 8). |
| RECOMP (2023) | Trains extractive and abstractive summarisers of retrieved documents on the reader's end-task performance; can return an empty string. | Keeps 5% of tokens for a 2 EM loss on NQ ([p. 7](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.5&page=7)). | Compressors transfer poorly to a different reader on QA ([p. 8](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.6&page=8)). |

Two findings recur across these papers:

- **Compression can beat the full prompt.** LongLLMLingua and RECOMP both improve accuracy by removing distractors. RECOMP cuts wrong copying from the evidence from 81% (top-5 documents) to 39% (p. 8).
- **Question-blind compression fails on noisy retrieval.** On NaturalQuestions, LLMLingua and Selective-Context score below zero-shot (LongLLMLingua, p. 6).

## Soft compression (needs the weights)

- **Gist tokens (2023):** an attention mask during instruction fine-tuning forces the prompt through a single gist token, giving up to 26x compression.
  - The compute gain mostly vanishes against ordinary KV caching of the instruction: 0.11% fewer FLOPs and about 1% wall time. What remains is storage and context-window space ([p. 8](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)).
  - It loses details that must be copied verbatim ([p. 7](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=subsection.5.1&page=7)).
- **ICAE (2023):** a LoRA-adapted encoder writes 512 tokens into 128 memory slots that the frozen LLM reads, a 4x compression.
  - Reconstruction is near-perfect up to about 300 tokens and degrades past 400 ([p. 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=subsubsection.3.2.1&page=4)).
  - Answers still lag the uncompressed context ([p. 6](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=subsubsection.3.2.2&page=6)).

## The dissent

*Recall Is Not Enough* (2025) runs LLMLingua-2 against plain chunk selection at the same tight RAG budget of about 130 tokens. Compression loses by 0.125 F1, and even naive packing beats it by 0.075, because token dropping destroys the answer span ([p. 6](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?dest=section.5&page=6)). Its conclusion is that which evidence you keep matters more than how tightly you compress it.

LLMLingua-2's own appendix points the same way: adding LongLLMLingua's document-level budgeting gives +25.3% on NQ ([p. 14](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=appendix.K&page=14)).

## What is dated or thin

- **Old targets:** the results are on GPT-3.5-Turbo, Claude-v1.3 and LLaMA-7B, with latency measured on a V100. None of the papers tests a current long-context model, so I would not assume the "compression improves accuracy" gains carry over.
- **Caching:** only the Gist paper compares against KV caching, and that comparison removes most of its speed argument.
- **Weak evidence of losslessness:** it is shown by GPT-4 reconstructing example prompts, not measured.
- **The survey:** *A Survey of Context Engineering* covers compression in a single subsection (§4.3.3, p. 25).

## Adjacent papers

- **DeepSeek-OCR:** renders text as an image, with 97% decoding precision below 10x compression and about 60% at 20x ([p. 1](http://pdf.invalid/vision-and-multimodal/vision-language/DeepSeek-OCR.%20Contexts%20Optical%20Compression.pdf?page=1)).
- **Cartridges** (`llm/memory/parametric`): trains a small KV cache per corpus; I only read its summary line (38x less memory).
- **LightMem** (`llm/memory/agent`): uses LLMLingua-2 as its pre-compressor, so that is the place to see it used inside a memory system.

I read the method, results and limitations sections of the six core papers, not every appendix. I found no standalone copies of Selective-Context or AutoCompressor, which these papers use as baselines.
