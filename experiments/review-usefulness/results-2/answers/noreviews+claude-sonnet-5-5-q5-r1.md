Short status: I searched the library and read the notes for the papers that turned up. Four of the core papers have no notes yet, so for those I only have the one-line summaries.

## Where it lives

The main folder is `llm/context/`, whose scope covers "selecting, compressing and ordering what goes into the context window". Related work sits in `llm/memory/`, `llm/efficiency/` and a few other places.

## Three families of approach

**1. Hard prompt compression: drop tokens and keep readable text**
- **LLMLingua** uses a budget controller and iterative token-level pruning. I only have its summary.
- **LongLLMLingua** adapts that to long contexts and is task-aware. I only have its summary.
- **RECOMP** puts a learned extractive or abstractive compressor between retrieval and the model. I only have its summary.
- [**LLMLingua-2**](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?page=3) trains a small bidirectional encoder to keep or drop each token. The labels come from GPT-4 compressing text by deletion only (p. 3–4).
  - Against LLMLingua it is faster: 0.4–0.5 s for the compressor vs 1.5–2.9 s, and 1.6–2.9x end-to-end speedup (p. 8, Table 5).
  - Quality is mixed. It clearly beats LLMLingua on MeetingBank and LongBench (AVG 39.1 vs 34.6 at a 2,000-token budget). It only ties LLMLingua on GSM8K and BBH (p. 6, Table 3).
  - It stays below the original prompt on LongBench AVG, and below task-aware LongLLMLingua (48.0 at 2,000 tokens, p. 6, Table 2).
  - My notes rate the evidence as vendor-run, with no variance reported and baseline numbers copied from an earlier paper.

**2. Soft prompt compression: learn dense vectors**
- **Gisting** trains the model to compress prompts into cacheable gist tokens, with up to 26x compression and up to 40% fewer FLOPs. That is from the summary only.
- [**ICAE**](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?page=3) has a LoRA-adapted encoder write 128 memory slots for a frozen LLM, which gives 4x compression (p. 1, p. 3).
  - Autoencoding is near-perfect for contexts up to about 300 tokens, and beyond 4x compression is "rather challenging" (p. 4–6).
  - Against the same model given the full context, ICAE wins 19.6% and loses 45.4% (Llama-2-7b-chat, k=128, p. 4–6, Table 4).
  - The evidence is one self-built, GPT-4-judged benchmark, and it never compares against other compression methods.
- **Cartridges** train a small KV cache offline per corpus with "self-study" (synthetic conversations plus context distillation).
  - It matches in-context learning at 38.6x less memory and 26.4x higher throughput (p. 1, 12).
  - It costs about 30 minutes on 8×H100 per corpus, so it only pays off when many queries reuse the corpus (p. 12).
  - It beats cache-compression baselines, which degrade beyond 2x (p. 9–10).

**3. Compress the cache or change the representation**
- **H2O** evicts KV-cache entries, keeping recent tokens plus "heavy hitters". Its throughput gains are up to 29x (summary only). **KIVI** does 2-bit KV quantization.
- **DeepSeek-OCR** ("Contexts Optical Compression") and **StreamingVLM** compress text or video through the visual modality. I haven't read either.

## Compression inside agent memory
- **LightMem** uses LLMLingua-2 as a "sensory" denoising stage before topic segmentation and summarisation.
  - It reports accuracy holding for retain ratios of 50–80% (p. 8–9).
  - On LongMemEval it reaches 68.64 vs 56.80 for full text, with far fewer tokens and LLM calls (p. 6, Table 2).
  - It has no variance reported, and it equals NaiveRAG with GLM-4.6 (73.2 each).
- **MemAgent** and **Mem-α** learn memory construction with RL, and several memory surveys cover compression. I haven't opened these.

## Patterns across them
- **Task-aware beats task-agnostic.** LLMLingua-2 concedes this on LongBench, where it is below LongLLMLingua (p. 8).
- **Gains shrink on fine-grained tasks.** LLMLingua-2 scores 21.3 on LongBench Synthetic at 2,000 tokens vs 37.8 for the original (p. 6, Table 2). ICAE is weak on random or patterned text (p. 4–6, Table 3).
- **Compression ratios and budgets are often not matched across baselines.** This shows up in the LLMLingua-2 MeetingBank table (p. 5, Table 1) and in its distillation ablation (p. 8, Table 7).

## Gaps
- No notes exist yet for LLMLingua, LongLLMLingua, Gisting, RECOMP and H2O. I can run `paperlib read` on them for proper digests.
- I haven't checked whether the survey papers (the context engineering survey, the efficient-inference survey) compare these approaches head-to-head.

Do you want me to read those five and write their notes?
