# Improving Language Understanding by Generative Pre-Training

type: method
read: full
family: autoregressive language model pre-training and fine-tuning (GPT-1)
evidence: evaluated on 12 natural language understanding datasets (NLI, QA, Semantic Similarity, Classification) against prior state-of-the-art models; strength: strong (multiple public benchmarks, systematic ablations of architecture and training objectives)
conversion: broken missing equation (Equation 5 is completely missing on p. 3, reading only "(5)"); table headers in Table 4 are flattened but readable

## Digest

- **Mechanism**: Introduces a two-stage semi-supervised framework: unsupervised generative pre-training using a standard language modeling objective on a large corpus, followed by supervised discriminative fine-tuning on specific target tasks (p. 1, p. 3).
- **Model Architecture**: Uses a 12-layer decoder-only Transformer with masked self-attention (768 dimensional states, 12 attention heads) and 3072 dimensional inner states for feed-forward networks (p. 4).
- **Pre-training Data**: Trained on the BooksCorpus dataset (over 7,000 unique unpublished books) because its long stretches of contiguous text allow the model to learn long-range conditioning (p. 4).
- **Fine-tuning**: Adapts the pre-trained model to structured tasks via traversal-style input transformations (adding start, end, and delimiter tokens) to avoid making task-specific architectural changes (p. 4).
- **Auxiliary Objective**: Includes language modeling as an auxiliary objective during fine-tuning (with weight 0.5) to improve generalization and accelerate convergence (p. 3, p. 5).
- **Disclosed**: Hyperparameters (learning rates, dropout, epochs, 40,000 BPE merges), pre-training data source, and architectural dimensions are disclosed. Parameter counts and the exact Equation 5 are missing (p. 3, p. 4).
- **Overall Performance**: Outperforms discriminatively trained models, improving upon the state of the art in 9 out of the 12 tasks studied (p. 1, p. 7).
- **NLI Results**: Achieves 82.1 on MNLI-m (vs 80.6 baseline Stochastic Answer Network), 88.3 on SciTail (vs 83.3 baseline CAFE), and 88.1 on QNLI (vs 82.3 baseline GenSen) (p. 6, Table 2).
- **QA / Commonsense**: Achieves 86.5 on Story Cloze (vs 77.6 baseline Hidden Coherence Model) and 59.0 on RACE (vs 53.3 baseline BiAttention MRU) (p. 6, Table 3).
- **Semantic Similarity**: Achieves 82.0 on STSB (vs 81.0 baseline ECNU) and 70.3 on QQP (vs 66.1 baseline Single-task BiLSTM + ELMo + Attn) (p. 7, Table 4).
- **Classification**: Achieves 45.4 on CoLA (vs 35.0 baseline Single-task BiLSTM + ELMo + Attn) and an overall GLUE score of 72.8 (vs 68.9 baseline Multi-task BiLSTM + ELMo + Attn) (p. 7, Table 4).
- **Ablation (Pre-training)**: Direct supervised training without pre-training results in a 14.8% decrease compared to the full model, dropping the average score to 59.9 from 74.7 (p. 8, Table 5).
- **Ablation (Architecture)**: Replacing the Transformer with a 2048 unit LSTM results in a 5.6 average score drop (p. 8).
- **Ablation (Auxiliary LM)**: Removing the auxiliary LM objective slightly increases the average score to 75.0 (from 74.7), though the text notes the objective still benefits larger datasets (p. 8, Table 5).
- **Layer Transfer**: Transferring each transformer layer provides further benefits, up to 9% for full transfer on MultiNLI (p. 7).
- **Zero-shot Behavior**: Heuristic zero-shot performance steadily increases over LM pre-training updates, suggesting generative pre-training supports the learning of task-relevant functionality (p. 7, Figure 2).

## Related

- Transformer [62]: Provides the underlying decoder-only architecture used for the generative model.
- ELMo [44]: Prior state-of-the-art that uses pre-trained LSTMs for auxiliary features, which this work replaces with a single fine-tuned model.
- ULMFiT [21]: Closest prior method using language model pre-training and supervised fine-tuning, but uses LSTMs instead of Transformers.
