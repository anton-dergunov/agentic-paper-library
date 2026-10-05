Your library has six papers that are squarely about prompt compression, all in `llm/context/`, plus a few that use it or argue against it. They show that 2–5x compression is usually close to free, that higher ratios hold only on redundant prompts, and that the gains are largest when compression is query-aware and removes noise.

**Example.** LLMLingua takes an 8-shot chain-of-thought prompt for GSM8K, drops whole demonstrations, then deletes the tokens a small LM finds most predictable. The result is unreadable to a person, but GPT-3.5 scores 79.08 EM at 5x, and loses about 1.5 points at 20x ([p. 6](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=subsection.5.2&page=6)).

## Three families

| Family | Papers | How it compresses | Works with API-only models |
|---|---|---|---|
| Token pruning (text out) | LLMLingua, LongLLMLingua, LLMLingua-2 | Delete tokens, keep the rest verbatim | Yes |
| Summarising retrieved documents | RECOMP | Select sentences or write a short summary for the query | Yes |
| Soft tokens (vectors out) | Gist tokens, ICAE | Train the model to pack the prompt into a few activations | No |

## What each one finds

- **LLMLingua** scores tokens by perplexity under a small LM.
  - Ablations show the budget controller and iterative pruning carry the result: removing either costs about 6 EM, while removing alignment to the target LLM costs 0.5 ([p. 7, Table 3](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.3&page=7)).
  - It degrades faster on BBH (−8.5 EM at 5x) and collapses at 25–30x (p. 6, p. 9).
  - Asking GPT-4 to rewrite the prompt shorter does worse, because it drops reasoning steps (p. 6).
- **LongLLMLingua** makes the pruning question-aware.
  - It ranks each document by how predictable the question becomes given it, reorders documents by that score, and gives relevant ones more budget ([p. 3–4](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=subsection.4.1&page=3)).
  - Compressed prompts beat the original: +21.4 on NaturalQuestions with the gold document in 10th position, at about 4x fewer tokens (p. 6).
  - The cost is recompressing for every question, at twice LLMLingua's compute (p. 9).
- **LLMLingua-2** replaces perplexity with a small encoder trained on GPT-4 keep/drop labels.
  - The compressor is 3–6x faster than LLMLingua (0.4–0.5 s against 1.5–2.9 s) ([p. 8, Table 5](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.5&page=8)).
  - It is much better on meeting QA (86.9 against 67.5 EM) but only ties on GSM8K and BBH (p. 5–6).
  - It still loses to question-aware LongLLMLingua on LongBench, 39.1 against 48.0, with the uncompressed prompt at 44.0 ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.2&page=6)).
- **RECOMP** compresses the top-5 retrieved documents to about 5% of their tokens.
  - That costs 2 EM on NQ and 3.7 on TriviaQA; on multi-hop HotpotQA the extractive version does better, at 11% for −2.4 EM ([p. 7](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=section.5&page=7)).
  - It can return nothing when retrieval would not help.
  - The oracle sentence reaches 60.2 EM against 39.3 for full documents, so the ceiling is in choosing what to keep (p. 8, Table 3).
- **Gist tokens** compress an instruction into one token (up to 26x) by changing the attention mask during fine-tuning.
  - Quality is near parity with the uncompressed model: 45.8–49.7% win rate on unseen prompts for LLaMA-7B ([p. 5](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.5&page=5)).
  - It fails when details must be copied verbatim (p. 7).
  - Against ordinary KV caching of the instruction, the saving is 0.11% of FLOPs and 1% of wall time; the real gain is cache storage (p. 8).
- **ICAE** extends this to 512-token contexts at 4x, with a LoRA encoder writing 128 memory slots for a frozen LLM.
  - Reconstruction is near perfect (BLEU 99.3), but against the same model with the full context it loses 45.4% and wins 19.6% ([p. 4–6, Table 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=table.4&page=5)).
  - Below 128 slots quality drops sharply.

## Around the core

- **As a denoiser in agent memory:** SeCom and LightMem both run LLMLingua-2 over dialogue before retrieval. Removing it from SeCom drops LOCOMO from 69.33 to 59.87 ([p. 7, Table 2](http://pdf.invalid/llm/memory/agent/On%20Memory%20Construction%20and%20Retrieval%20for%20Personalized%20Conversational%20Agents.pdf?dest=table.2&page=7)).
- **Against compression:** ACE argues contexts should be long playbooks. Its evidence is one case, where an LLM rewrite shrank a context from 18,282 to 122 tokens and accuracy fell from 66.7 to 57.1 ([p. 3, Figure 2](http://pdf.invalid/llm/context/Agentic%20Context%20Engineering.%20Evolving%20Contexts%20for%20Self-Improving%20Language%20Models.pdf?dest=figure.2&page=3)).
- **Per-corpus alternative:** Cartridges trains a KV prefix per corpus and matches full-context quality at 38.6x less memory, for about 30 minutes on 8×H100 per corpus (p. 1, p. 12).

## What is weak or dated

- **Vendor-run evidence:** the three LLMLingua papers come from one Microsoft group, who also wrote each other's baselines.
- **Unequal budgets:** LLMLingua-2's headline table compares 3.1x against 2.5x.
- **No cross-family comparison:** ICAE never runs against Gist tokens, and neither runs against token pruning.
- **Old targets:** the models are GPT-3.5, Claude-v1.3 and 7B Llamas; nothing here tests a current long-context model.
- **Prompt caching (my inference, not from a paper):** it undercuts the cost argument. ACE reports 91.8% of its input tokens served from cache (p. 10), and question-aware compression defeats caching.

## Coverage

`llm/context` has no literature review, and LLMLingua, LongLLMLingua, Gist tokens and RECOMP have no notes. For those four I read the method and main results sections, not the appendices. A review of `llm/context` would make this reusable; say if you want one.
