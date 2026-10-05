Your library covers prompt compression with six core papers in `llm/context/`, which split into three families. The shared finding is that compression pays off mainly when the prompt is redundant or noisy. There is no review for `llm/context` yet, so this comes from the notes for ICAE and LLMLingua-2 and a direct read of the other four.

**Example of the idea:** an 8-shot chain-of-thought prompt for GSM8K is 2,366 tokens. LLMLingua drops whole demonstrations, then the most predictable tokens, leaving 446 tokens of broken-looking text that GPT-3.5 answers from just as well (79.08 vs 78.85 EM).

## The three families

| Family | Papers | How it compresses | Works with API models |
|---|---|---|---|
| Token pruning | LLMLingua, LongLLMLingua, LLMLingua-2 | Delete tokens; the output is still text | Yes |
| Summarising retrieved documents | RECOMP | A small trained model picks sentences or writes a summary | Yes |
| Soft tokens | Gisting, ICAE | Train the model to pack the prompt into a few vectors | No, needs the weights |

## What each one finds

- **LLMLingua** scores tokens by a small LM's perplexity and keeps the surprising ones.
  - It holds 77.33 EM on GSM8K at 20x and collapses around 25–30x ([p. 5–6, Table 2](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?dest=table.2&page=6); [p. 9, Limitations](http://pdf.invalid/llm/context/LLMLingua.%20Compressing%20Prompts%20for%20Accelerated%20Inference%20of%20Large%20Language%20Models.pdf?page=9&search=Limitations)).
  - Simply keeping one demonstration gets 77.10 at 6x in the same table, so much of the result is that few-shot demonstrations are redundant.
- **LongLLMLingua** makes the pruning question-aware and reorders documents by relevance.
  - On NaturalQuestions with 20 documents at 4x it scores 71.2 against 54.1 for the full prompt when the gold document is 10th ([p. 5–6, Table 1](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?dest=table.1&page=6)).
  - Its document ranker alone gets 69.3 in that setting, so most of the gain is selection rather than token pruning.
  - Question-agnostic LLMLingua gets 23.5 there, below the zero-shot 56.1.
  - The compressed prompt cannot be cached across questions, and it costs twice LLMLingua's compute ([p. 9, Limitation](http://pdf.invalid/llm/context/LongLLMLingua.%20Accelerating%20and%20Enhancing%20LLMs%20in%20Long%20Context%20Scenarios%20via%20Prompt%20Compression.pdf?page=9&search=Limitation)).
- **LLMLingua-2** replaces perplexity with a small bidirectional classifier trained on GPT-4 keep/drop labels.
  - The compressor is 3–6x faster than LLMLingua's ([p. 8, Table 5](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.5&page=8)).
  - It still loses to task-aware LongLLMLingua on LongBench, 39.1 vs 48.0 at 2,000 tokens, and to the full prompt at 44.0 ([p. 6, Table 2](http://pdf.invalid/llm/context/LLMLingua-2.%20Data%20Distillation%20for%20Efficient%20and%20Faithful%20Task-Agnostic%20Prompt%20Compression.pdf?dest=table.2&page=6)).
- **RECOMP** compresses five retrieved documents (660 tokens) to about 36 tokens.
  - NQ exact match drops from 39.39 to 37.04 ([p. 6–7, Table 2](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.2&page=7)).
  - It can return an empty summary when retrieval would not help.
  - It cuts copying of wrong answers from the context from 81% to 39% ([p. 8, Table 3](http://pdf.invalid/llm/context/RECOMP.%20Improving%20Retrieval-Augmented%20LMs%20with%20Compression%20and%20Selective%20Augmentation.pdf?dest=table.3&page=8)).
  - On multi-hop HotpotQA the abstractive version (28.20) falls below a single uncompressed document (28.80).
- **Gisting** trains the model, through an attention mask, to squeeze an instruction into one gist token.
  - The "26x" means roughly 26-token instructions become one token ([p. 4, §4.1](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=subsection.4.1&page=4)).
  - Against ordinary KV caching of the prompt it saves 0.11% of FLOPs and 1% of wall time; the real saving is cache storage ([p. 8, §6](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=section.6&page=8)).
  - It loses details that must be copied verbatim ([p. 7, §5.1](http://pdf.invalid/llm/context/Learning%20to%20Compress%20Prompts%20with%20Gist%20Tokens.pdf?dest=subsection.5.1&page=7)).
- **ICAE** extends the idea to roughly 512-token contexts packed into 128 memory slots.
  - At 4x the same model with compressed context loses more often than it wins against itself with the full context: 19.6% wins, 45.4% losses ([p. 4–6, Table 4](http://pdf.invalid/llm/context/In-context%20Autoencoder%20for%20Context%20Compression%20in%20a%20Large%20Language%20Model.pdf?dest=table.4&page=5)).
  - The authors call going beyond 4x "rather challenging".

## Weak or dated

- **Old targets:** every paper uses 2023 models (GPT-3.5, Claude 1.3, Llama-2 7B/13B). None tests whether the gains survive on current long-context models or against provider prompt caching.
- **Vendor-run evidence:** the LLMLingua line comes from one Microsoft group that also wrote its main baselines, and LLMLingua-2 copies some baseline numbers rather than re-running them.
- **Headline numbers:** LongLLMLingua's "21.4%" is points and includes reordering (75.5 vs 54.1). LLMLingua-2's MeetingBank comparison is not at equal token budget.

## Later papers that push back

- [Recall Is Not Enough](http://pdf.invalid/llm/context/Recall%20Is%20Not%20Enough.%20A%20Reader-Context%20Diagnostic%20for%20Budget-Constrained%20Retrieval-Augmented.pdf?page=1) (2026) reports that a budgeted evidence packer beats LLMLingua-2 at equal or lower token cost. I read only its abstract and introduction.
- [ACE](http://pdf.invalid/llm/context/Agentic%20Context%20Engineering.%20Evolving%20Contexts%20for%20Self-Improving%20Language%20Models.pdf?page=3&search=context%20collapse) shows the risk of repeated LLM rewriting: a context fell from 18,282 to 122 tokens in one step, and accuracy dropped from 66.7 to 57.1, below the 63.7 no-adaptation baseline (p. 3).
- In the memory folder, SeCom and LightMem use LLMLingua-2 as a denoiser before retrieval. SeCom's note records LOCOMO falling from 69.33 to 59.87 without it (p. 7, Table 2). That figure is from the note, not re-checked in the paper.

Four of the six papers (LLMLingua, LongLLMLingua, Gisting, RECOMP) have no note yet; `paperlib read library/llm/context` would write them.
