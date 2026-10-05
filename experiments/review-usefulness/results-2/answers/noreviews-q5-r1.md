Your library has about ten papers that bear on this. Together they say prompt compression works well when the prompt is redundant or noisy, and poorly when it is dense and the budget is tight. Most of the headline ratios come from the first case.

## The idea, by example

A GSM8K prompt with eight worked examples is 2,366 tokens. Keeping just one example (422 tokens) already scores 77.10 against 78.85 for the full prompt. So "20x compression with a 1.5-point loss" mostly says the other seven examples were redundant ([LLMLingua, p. 5–6, Table 2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.2&page=6)). A 160-token budget of retrieved evidence for a multi-hop question is the opposite case: dropping tokens there removes the answer itself.

## The four families

| Family | Papers | What the prompt becomes | Needs model weights | Where quality holds |
|---|---|---|---|---|
| Token dropping | LLMLingua, LongLLMLingua, LLMLingua-2 | Shorter text | No | 5x–20x on few-shot prompts; 2x–5x on documents |
| Query-focused summary for RAG | RECOMP | One or two sentences, or nothing | No, but trained per task and reader | 5–11% of the tokens for 2–4 EM lost |
| Soft tokens | Gisting, ICAE, Cartridges | Activations the model conditions on | Yes | Gisting 26x on ~26-token instructions; ICAE about 4x; Cartridges 38.6x less memory |
| Text rendered as an image | DeepSeek-OCR | Vision tokens | Yes | ~97% OCR precision under 10x, ~60% at 20x |

- **LLMLingua** uses a small language model to drop tokens it finds predictable (low perplexity). It first drops whole demonstrations, then tokens segment by segment, so each decision sees what was already removed (p. 3–4).
- **LongLLMLingua** makes this question-aware. It ranks documents by how well each one predicts the question, scores tokens by how much the question changes their perplexity, and moves the best documents to the front (p. 3–4).
- **LLMLingua-2** replaces perplexity with a small bidirectional encoder trained to label each word keep or drop, using GPT-4 compressions as training data (p. 3–5). The compressor is 3–6x faster.
- **RECOMP** trains a sentence selector and a T5 summariser on what actually helps the reader answer. The summariser can return an empty string when retrieval would hurt (p. 2–4).
- **Gisting** inserts gist tokens after the instruction and masks attention so later tokens see only those (p. 3). **ICAE** uses a LoRA-adapted encoder to write 128 memory slots for the frozen model.
- **Cartridges** trains a key-value prefix per corpus by gradient descent, using self-generated questions and distillation.
- **DeepSeek-OCR** measures how many vision tokens are needed to read back N text tokens (p. 10).

## What the evidence supports

- **Task-agnostic dropping fails on retrieval-heavy prompts.** On NaturalQuestions with 20 documents at 4x, LLMLingua scores 25.5–30.0, below the 56.1 the model gets with no documents ([LongLLMLingua, p. 5–6, Table 1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.1&page=6)).
- **"Compression improves accuracy" is mostly a lost-in-the-middle fix.** LongLLMLingua's +21.4 is 75.5 against 54.1 with the gold document at position 10. With it at position 1, the result is 75.0 against 75.7 (same table).
- **Selection beats compression under a tight budget.** In the one independent test you have, LLMLingua-2 scores F1 0.326, plain top-k truncation 0.400 and submodular chunk selection 0.451 ([Recall Is Not Enough, p. 6, Table 3](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?dest=table.3&page=6)). The paper's explanation is that dropping tokens destroys the answer span. This is one small reader (Qwen2.5-3B) on HotpotQA.
- **Abstractive summaries save the most tokens but mislead.** RECOMP's summariser reaches 37.04 EM on NQ with 36 tokens against 39.39 with 660 ([p. 6–7, Table 2](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.2&page=7)). GPT-3.5 summaries make the reader copy a wrong answer 85% of the time when the gold answer is absent, against 39% for RECOMP's (p. 8, Table 3). On multi-hop HotpotQA, extraction beats abstraction.
- **Compression helps as denoising in agent memory.** SeCom loses about 9.5 points on LOCOMO without LLMLingua-2 ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=table.2&page=7)). LightMem holds QA accuracy when keeping 50–80% of tokens (p. 8–9).
- **Summarising to fit the window loses to keeping the text outside it.** A compaction agent scores 0.1 on OOLONG-Pairs against 58.0 for a recursive language model at depth 1, and 70.5 against 91.3 on BrowseComp+ ([Recursive Language Models, p. 6, Table 1](http://pdf.invalid/llm/context/Recursive%20Language%20Models.pdf?dest=table.1&page=6)).

## What is weak or dated

- **Soft-prompt ratios are narrower than they sound.** Gisting's 26x is one token for a ~26-token instruction. Against ordinary KV caching it saves 0.11% of FLOPs, and it loses verbatim details such as category names (p. 7–8). ICAE at 4x loses to the same model with the full context 45.4% to 19.6% (p. 4–6, Table 4).
- **Cartridges is the strongest soft result but costly.** It takes about 30 minutes on 8×H100 per corpus, so it pays off only when many queries reuse that corpus (p. 12).
- **DeepSeek-OCR tests reconstruction, not use.** The authors say OCR alone does not validate the idea and that QA over compressed context is future work (p. 19).
- **The token-dropping line is one group's work.** All three LLMLingua papers are from Microsoft, tested on GPT-3.5-era models. LLMLingua-2's out-of-domain baselines are copied from the earlier paper, and it only ties LLMLingua on GSM8K and BBH (p. 6, Table 3).
- **None of the method papers accounts for provider prompt caching.** LongLLMLingua notes that its question-aware output cannot be cached across questions (p. 9).

## Housekeeping

Four of the core papers have no agent note yet (LLMLingua, LongLLMLingua, RECOMP, Gisting), so I read them directly; `paperlib read llm/context` would fill those in. I tried to append this comparison to the Q&A in the LLMLingua-2 note, but the write was denied, so nothing in the library changed and there is nothing to commit.
