# OLMo: Accelerating the Science of Language Models

type: system
read: full
family: open-source foundation model technical report
evidence: downstream zero-shot classification, intrinsic perplexity (Paloma), and adapted chat evaluation (Tülu 2 suite) against comparably sized models like Llama 2, MPT, and Falcon; strength: vendor-run open benchmarks
conversion: ok | Table 3 contains empty brackets `[]` where icons or checkmarks likely were, but all text and numbers are perfectly intact.

## Digest

- **Framework:** The OLMo project aims to provide a "truly Open Language Model" by releasing all artifacts—model weights, 500+ intermediate checkpoints, pretraining data, and training/evaluation code—to enable scientific study of LLMs (p. 1).
- **Disclosed:** The entire pipeline is open: the full pretraining corpus (Dolma), exact data ordering, W&B training logs, adaptation training code/data, and checkpoints every 1000 steps (p. 8). 
- **Undisclosed:** No significant artifacts are withheld; the release explicitly counters the trend of gated, proprietary models.
- **Architecture:** Uses a decoder-only transformer modified to exclude all bias terms, use non-parametric layer norm (no adaptive gain or bias), replace absolute positions with Rotary positional embeddings (RoPE), and use SwiGLU activations (p. 2).
- **Scale:** The 7B model variant features 32 layers, a hidden dimension of 4086, 32 attention heads, and is trained on 2.46T tokens with a peak LR of 3.0E-4 (p. 1, Table 1).
- **Pretraining Data:** The Dolma dataset comprises 2,668 billion tokens across 4,367 million documents, with 2,180 billion of those tokens sourced from Common Crawl (p. 3, Table 2).
- **Training Recipe:** Employs the AdamW optimizer with a 5000-step learning rate warmup, followed by a linear decay down to a tenth of the peak learning rate (p. 5).
- **Late Training Boost:** Linearly reducing the learning rate to 0 over the final 1000 training steps (a brief second tune on Dolma) produces a sharp upward tick in accuracy on most core end-tasks (p. 5, Figure 1).
- **Downstream Evaluation (Aggregate):** Across an 8-task zero-shot core suite, OLMo-7B achieves an avg. score of 69.3, compared to Llama 2 7B at 70.5, Falcon-7B at 70.3, MPT-7B at 69.8, LLaMA 7B at 69.6, and Pythia 6.9B at 63.0 (p. 5, Table 3).
- **Downstream Evaluation (Specific):** On boolq, OLMo-7B scores 73.4 against Llama 2 7B at 80.2; on hellaswag, OLMo-7B scores 76.4 against Llama 2 7B at 76.8 (p. 5, Table 3).
- **Intrinsic Evaluation:** Measured using the Paloma perplexity benchmark, tracking bits per byte across data sources that were explicitly decontaminated from OLMo's pretraining data (p. 4).
- **Adaptation (Capabilities):** After Supervised Fine-Tuning and Direct Preference Optimization (OLMo+SFT+DPO), the model achieves a 0-shot MMLU score of 46.2, compared to Llama-2-Chat at 46.8 and Tülu 2+DPO at 50.7 (p. 7, Table 4).
- **Adaptation (Safety/Alignment):** OLMo+SFT+DPO achieves 1.7 % Toxic on ToxiGen and 52.0 %Info+True on TruthfulQA, compared to Llama-2-Chat which scores 0.0 % Toxic and 26.3 %Info+True respectively (p. 7, Table 4).

## Related

- LLaMA, PaLM, Falcon: Model families whose architectural modifications (e.g., RoPE, SwiGLU, removing biases) OLMo adopts.
- Pythia / BLOOM: Acknowledged as the most open prior language models, which also released checkpoints and data.
- Llama 2: Treated as the state-of-the-art capability baseline that OLMo attempts to narrow the gap toward.
- Tülu (Ivison et al., 2023; Wang et al., 2023): The instruction fine-tuning and evaluation framework directly applied to adapt and evaluate OLMo for chat.
