# Topic tree

Phase 2 of [the library expansion](../library-expansion.md). This is the complete folder tree for
`library/` (and the mirrored PDF tree), with the moves of papers already in the library. Folders
are created now even when they are empty. The literature pass (phase 6) fills the thin ones.
Approved by Anton on 2026-09-30, with the decisions at the end.

## How it is organised

- **Twenty areas at the top**, each a field Anton works in or reads about. The areas follow his
  org study plans closely, so a plan section and a library folder point at the same thing:

  | Org plan | Library areas |
  |---|---|
  | `Generative_AI.org` | `llm/`, `generative-models/`, `vision-and-multimodal/` |
  | `Ranking.org` | `search-and-ranking/`, `recommender-systems/` |
  | `Experiments.org`, `Statistics.org` | `experimentation-and-metrics/` |
  | `Deep_Learning.org` | `deep-learning/`, `representation-learning/`, `nlp/`, `graphs/`, `interpretability/` |
  | `Foundations.org` | `ml-foundations/`, `data-centric-ml/`, `trustworthy-ml/` |
  | `Systems.org` | `ml-systems/`, `computer-systems/` |
  | `RL.org` | `reinforcement-learning/`, `robotics-and-embodied/` |

- **Two levels, three where an area has a natural grouping** (`llm/post-training/`,
  `llm/memory/`, `llm/personalization/`, `llm/evaluation/`).
- **General before LLM-specific.** A method that predates LLMs or applies to all of ML lives in
  its general area: knowledge distillation is in `deep-learning/`, SHAP in `interpretability/`,
  and DP-SGD and federated learning in `trustworthy-ml/`. `llm/` holds what is about language
  models.
- **Interpretability is one area**, with `mechanistic/` (circuits, features, attention analysis)
  and `explainability/` (attribution, SHAP, LIME), rather than splitting it between `llm/` and
  elsewhere.
- **Systems work sits in two areas.** `ml-systems/` covers training, serving and production ML.
  `computer-systems/` holds the classic systems papers from `Papers_old/`: GFS, Bigtable, Spanner,
  Chubby, Memcache, and the sketches and data structures.
- **Bandits go under `reinforcement-learning/`**, as in `RL.org`. Contextual-bandit recommenders
  are cross-referenced from `recommender-systems/` by the literature pass rather than
  duplicated.

"In library" counts the current 240 papers after the moves below. "From inventory" counts the
papers marked `add` in [inventory.tsv](inventory.tsv); the `skip?` ones are not counted.
Totals: 108 folders, 240 papers in the library and 862 to add.

## The tree

### `llm/`: Large language models — how they are built, adapted, used and evaluated.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `foundation-models/` | Model families and technical reports (GPT, LLaMA, PaLM, DeepSeek), and surveys of LLMs as a whole. |  | 18 |
| `architecture/` (group) | Transformer variants for language models — mixture of experts, positional encoding, tokenization and byte-level models, other architectural changes. |  | 41 |
| `architecture/efficient-attention-and-long-context/` | Sparse, linear and blockwise attention, and extending context length (Longformer, Reformer, ALiBi, Ring Attention). |  | 10 |
| `architecture/recurrent-and-state-space/` | Recurrent and state-space alternatives to attention (Mamba, RWKV, RetNet, xLSTM, linear RNNs, hybrids). |  | 14 |
| `pretraining/` | Pretraining data, data curation and mixtures, synthetic data and model collapse, scaling laws, how knowledge is acquired during pretraining. | 3 | 19 |
| `prompting-and-in-context/` | Prompting, in-context learning, chain-of-thought prompting, and automatic prompt optimization. | 9 | 7 |
| `context/` | Context engineering — selecting, compressing and ordering what goes into the context window, and how models use long contexts. | 11 |  |
| `post-training/` (group) | Adapting pretrained models after pretraining. | 31 | 23 |
| `post-training/fine-tuning/` | Supervised fine-tuning, instruction tuning, parameter-efficient methods (LoRA, adapters), and forgetting. | 2 | 10 |
| `post-training/preference-learning/` | RLHF, reward models, DPO and other preference-optimization methods. | 21 | 2 |
| `post-training/rl-for-reasoning/` | Reinforcement learning with verifiable rewards and the reasoning models trained with it (R1, GRPO, RLVR analyses). | 1 | 10 |
| `post-training/data/` | Data for alignment and post-training — instruction and preference datasets, real conversation logs, synthetic alignment data. | 7 | 1 |
| `reasoning/` | Reasoning behaviour and test-time compute — chain-of-thought analyses, overthinking, latent and recursive reasoning, limits of reasoning. | 2 | 18 |
| `agents/` | LLM agents — tool use, planning, multi-agent systems, agentic RL, research and coding agents. | 2 | 31 |
| `retrieval-augmented/` | Retrieval-augmented generation — architectures, graph RAG, retrieval-aware generation and RAG evaluation. |  | 9 |
| `memory/` (group) | Memory for LLMs and agents. | 49 | 4 |
| `memory/agent/` | External memory systems for agents — extraction, consolidation, retrieval, forgetting. | 34 |  |
| `memory/parametric/` | Memory held in weights or activations — knowledge editing, memorizing transformers, test-time training. | 8 | 4 |
| `memory/benchmarks/` | Benchmarks for long-term and agent memory. | 7 |  |
| `personalization/` (group) | Personalizing LLMs to individual users. | 51 | 4 |
| `personalization/methods/` | Personalization methods — user profiles and representations, personalized alignment, surveys. | 20 | 4 |
| `personalization/user-modelling/` | Inferring user state, traits and intent — theory of mind, personality, clarification seeking. | 11 |  |
| `personalization/benchmarks/` | Benchmarks and datasets for personalization and user understanding. | 20 |  |
| `behaviour/` | Model behaviour and character — instruction following, sycophancy, model specs and constitutions, steering. | 10 | 4 |
| `uncertainty-and-hallucination/` | Hallucination, calibration, verbalized uncertainty, knowing what the model knows. | 4 | 9 |
| `evaluation/` (group) | Evaluating LLMs. | 24 | 23 |
| `evaluation/benchmarks/` | Benchmarks and datasets for LLM capabilities. |  | 14 |
| `evaluation/methods/` | Evaluation methodology — LLM-as-judge, human evaluation, simulated users, statistical rigour. | 24 | 9 |
| `safety-and-privacy/` | Jailbreaks, prompt injection, memorization and data extraction, watermarking and detection, privacy. | 19 | 15 |
| `routing/` | Routing queries across models for cost and quality. | 11 |  |
| `efficiency/` | Making LLMs cheaper — quantization, pruning, distillation, speculative and efficient decoding. |  | 8 |
| `text-analytics/` | Using LLMs to analyse text collections — topic modelling, concept induction, usage insights. | 6 |  |

### `search-and-ranking/`: Information retrieval — indexing, ranking, retrieval models, evaluation.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `indexing-and-classical-ir/` | Inverted indexes, compression, BM25 and probabilistic models, classical diversification (MMR) and rank fusion. |  | 7 |
| `learning-to-rank/` | Learning-to-rank with features — RankNet/LambdaMART, GBDT rankers, listwise losses, LTR challenges. |  | 6 |
| `neural-ranking/` | Neural rerankers — interaction models (DRMM, KNRM), BERT and seq2seq rerankers, LLM rankers. |  | 12 |
| `dense-retrieval/` | Dense, sparse-learned and late-interaction retrieval (DPR, ColBERT, ANCE), embedding-based retrieval, document expansion. |  | 9 |
| `click-models-and-unbiased-ltr/` | Learning from user behaviour — position bias, click models, counterfactual and unbiased learning to rank. | 1 | 5 |
| `evaluation/` | IR evaluation — metrics, test collections, significance testing, interleaving, user satisfaction. |  | 6 |
| `search-systems/` | Production search systems and product surfaces — web, enterprise, email and personal search, query understanding, whole-page presentation. |  | 12 |
| `ads/` | Computational advertising — CTR prediction, feature hashing, auctions and reserve prices. |  | 4 |

### `recommender-systems/`: Recommender systems.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `collaborative-filtering/` | Matrix factorization, neighbourhood and linear models (iALS, EASE), and their neural counterparts. |  | 5 |
| `deep-and-sequential/` | Deep recommenders (two-tower, YouTube DNN) and sequential models (SASRec, BERT4Rec). |  | 9 |
| `llm-and-generative/` | LLMs in recommendation and generative retrieval with semantic IDs. |  | 3 |
| `industrial-systems/` | Recommenders deployed at scale — Pinterest, LinkedIn, Google Drive, video platforms. |  | 11 |
| `evaluation/` | Offline and online evaluation of recommenders, metrics, reproducibility. |  | 9 |

### `experimentation-and-metrics/`: Online experimentation and the metrics behind product decisions.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `ab-testing/` | Controlled experiments at scale — platforms, pitfalls, trustworthy analysis. |  | 2 |
| `variance-reduction/` | CUPED, the delta method and other sensitivity improvements. |  | 3 |
| `metric-design/` | Choosing and validating metrics — long-term effects, user satisfaction, OEC. |  | 3 |
| `causal-inference/` | Causal inference, uplift and counterfactual estimation from observational and logged data. |  | 2 |

### `data-centric-ml/`: Data as the lever — labels, weak supervision, augmentation, data quality.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `data-centric-ml/` (top level) | papers spanning the area |  | 1 |
| `weak-supervision/` | Programmatic labelling and weak supervision (Snorkel and successors). | 1 | 3 |
| `labels-and-annotation/` | Annotation, label noise and label errors, active learning, LLMs as annotators. | 1 | 8 |
| `augmentation-and-synthetic-data/` | Data augmentation and synthetic training data outside LLM pretraining. |  | 5 |
| `data-quality-and-shift/` | Dataset shift, drift detection, data cascades and dataset bias. |  | 4 |

### `ml-systems/`: Systems for training and serving models.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `distributed-training/` | Data, tensor and pipeline parallelism, ZeRO/FSDP, training at cluster scale. | 1 | 16 |
| `inference-and-serving/` | Serving models — batching, KV cache, LLM inference engines, serving many adapters. | 1 | 5 |
| `production-ml/` | ML in production — technical debt, testing, MLOps, operational practice. |  | 9 |

### `computer-systems/`: Classic systems papers — distributed storage and coordination, data structures, probabilistic sketches.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `computer-systems/` | (no subfolders) |  | 13 |

### `deep-learning/`: Deep learning as a field — architectures, training, theory.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `deep-learning/` (top level) | papers spanning the area |  | 1 |
| `architectures/` | Core architectures and their building blocks — CNNs, RNNs and LSTMs, the original transformer, capsules, MLP alternatives, activation functions. |  | 19 |
| `optimizers-and-schedules/` | Optimizers, learning-rate and batch-size schedules, hyperparameter transfer, curricula, training diagnostics. |  | 21 |
| `normalization-and-regularization/` | Normalization layers, initialization, dropout, weight decay, label smoothing. |  | 19 |
| `theory/` | Generalization, double descent, lottery tickets, grokking, loss landscapes, implicit regularization. |  | 19 |
| `efficiency-and-compression/` | Knowledge distillation, pruning and quantization of neural networks in general. |  | 9 |
| `uncertainty-and-robustness/` | Bayesian deep learning, ensembles, out-of-distribution detection, adversarial examples. |  | 8 |

### `representation-learning/`: Learning representations.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `self-supervised/` | Contrastive and non-contrastive self-supervised learning (SimCLR, MoCo, BYOL, DINO). |  | 22 |
| `embeddings/` | Word, sentence, document and entity embeddings; metric learning. |  | 24 |

### `nlp/`: Natural language processing before and beside LLMs.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `pretrained-language-models/` | BERT-era pretrained encoders and encoder-decoders, fine-tuning them, BERTology. |  | 12 |
| `tasks-and-methods/` | Classification, extraction, summarization, QA and other tasks with pre-LLM methods. |  | 34 |
| `generation-metrics/` | Automatic metrics for generated text (BLEU, BERTScore, MoverScore). |  | 4 |

### `graphs/`: Graph learning.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `graph-neural-networks/` | GNN architectures and surveys (GCN, GAT, GraphSAGE, message passing). |  | 22 |
| `graph-embeddings/` | Random-walk and projection embeddings (DeepWalk, node2vec, metapath2vec, FastRP). |  | 7 |

### `vision-and-multimodal/`: Vision, vision-language and speech.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `vision/` | Vision architectures and tasks — ViT, detection, segmentation, tracking. |  | 28 |
| `vision-language/` | Vision-language models and multimodal LLMs (CLIP, Flamingo, SigLIP, VQA, document retrieval). |  | 23 |
| `speech-and-audio/` | Speech recognition, TTS, music and audio. |  | 18 |

### `generative-models/`: Generative models of images, video and other data.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `diffusion/` | Diffusion and flow models — image, video, text-to-image, theory. |  | 16 |
| `gans-and-vaes/` | GANs, VAEs and other pre-diffusion generative models. |  | 7 |

### `interpretability/`: Understanding what models compute.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `explainability/` | Feature attribution and explanations — SHAP, LIME, saliency, concept-based explanations. |  | 21 |
| `mechanistic/` | Mechanistic interpretability — circuits, features, superposition, attention analysis. |  | 20 |

### `ml-foundations/`: Classical machine learning and statistics.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `classical-ml/` | Trees and boosting, SVMs, naive Bayes, clustering, dimensionality reduction. |  | 14 |
| `tabular/` | Tabular learning — GBDT versus deep models, tabular transformers, tabular foundation models and generators. |  | 9 |
| `evaluation-and-model-selection/` | Evaluating classifiers and selecting models — PR/ROC, thresholds, validation pitfalls. |  | 6 |
| `probabilistic-and-statistics/` | Bayesian methods, MCMC, statistical inference and its misuse. |  | 7 |

### `trustworthy-ml/`: Fairness, privacy and safety of ML systems in general.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `fairness-and-bias/` | Fairness definitions, social bias in models. |  | 2 |
| `privacy-and-federated/` | Differential privacy, federated learning, secure aggregation. | 2 | 12 |
| `ai-safety/` | AI safety problems in general (not LLM-specific attacks). |  | 3 |

### `reinforcement-learning/`: Reinforcement learning.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `deep-rl/` | Value-based and policy-gradient deep RL (DQN, PPO), RLHF's origins. | 1 | 10 |
| `bandits/` | Multi-armed and contextual bandits, exploration. |  | 3 |
| `world-models/` | Model-based RL and world models. |  | 6 |
| `methodology/` | How RL is evaluated and reported. |  | 6 |

### `robotics-and-embodied/`: Robot learning, vision-language-action models, embodied agents.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `robotics-and-embodied/` | (no subfolders) |  | 6 |

### `ai-and-society/`: Economic and social effects of AI; human–AI interaction.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `ai-and-society/` | (no subfolders) |  | 5 |

### `research-practice/`: Reading, writing and doing research; reproducibility and the reliability of findings.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `research-practice/` | (no subfolders) |  | 12 |

### `curiosities/`: Papers kept for fun or personal interest, outside the professional areas.

| Folder | Scope | In library | From inventory |
|---|---|--:|--:|
| `curiosities/` | (no subfolders) |  | 2 |

## Moves of papers already in the library

### Folder changes

| # | Change | Why |
|--:|---|---|
| F1 | `llm/alignment/preference-learning/` → `llm/post-training/preference-learning/` | `post-training/` groups everything done to a model after pretraining: fine-tuning, preference learning, RL for reasoning, and the data for them. |
| F2 | `llm/alignment/data/` → `llm/post-training/data/`, after the moves below | The papers left are alignment datasets (LIMA, Magpie, UltraFeedback, LMSYS-Chat-1M, WildChat). |
| F3 | `llm/personalization/` → `llm/personalization/methods/`; `llm/user-modelling/` → `llm/personalization/user-modelling/` | Personalization, the user models behind it, and its benchmarks form one area. Nesting keeps it in one place as it grows. |
| F4 | Split `llm/evaluation/benchmarks/`: memory benchmarks → `llm/memory/benchmarks/`, personalization benchmarks → `llm/personalization/benchmarks/` | All 29 papers are memory or personalization benchmarks. You would look for LongMemEval under memory. `evaluation/benchmarks/` then holds general capability benchmarks. |
| F5 | `llm/user-intelligence/` → `llm/text-analytics/` | The papers are about analysing text collections with LLMs: topic modelling, concept induction, usage insights. The new name says so. |
| F6 | Empty `llm/infrastructure/` by moving its four papers (below), then remove the folder | The four papers are unrelated: scaling laws, distributed training, serving and fine-tuning. |

### Individual papers

| # | Paper | From | To | Why |
|--:|---|---|---|---|
| P1 | Snorkel: Rapid Training Data Creation with Weak Supervision | `llm/alignment/data` | `data-centric-ml/weak-supervision` | A 2017 weak-supervision system, not specific to LLMs. |
| P2 | Is GPT-3 a Good Data Annotator? | `llm/alignment/data` | `data-centric-ml/labels-and-annotation` | Labelling data for other models, not alignment data. |
| P3 | Selective Annotation Makes Language Models Better Few-Shot Learners | `llm/alignment/data` | `llm/prompting-and-in-context` | Chooses which examples to annotate for in-context learning. |
| P4 | Chatbot Arena | `llm/alignment/data` | `llm/evaluation/methods` | An evaluation platform. |
| P5 | The Curse of Recursion; Is Model Collapse Inevitable? | `llm/alignment/data` | `llm/pretraining` | Model collapse from synthetic pretraining data. |
| P6 | Whose Opinions Do Language Models Reflect? | `llm/alignment/data` | `llm/behaviour` | Measures model opinions, not a dataset for training. |
| P7 | Active Preference Learning for Large Language Models | `llm/alignment/data` | `llm/post-training/preference-learning` | A preference-learning method. |
| P8 | LoRA: Low-Rank Adaptation of Large Language Models | `llm/alignment/preference-learning` | `llm/post-training/fine-tuning` | Parameter-efficient fine-tuning, not preference learning. |
| P9 | Proximal Policy Optimization Algorithms | `llm/alignment/preference-learning` | `reinforcement-learning/deep-rl` | General deep RL (2017). RLHF uses it, but it is not an LLM paper. |
| P10 | DeepSeekMath | `llm/alignment/preference-learning` | `llm/post-training/rl-for-reasoning` | Introduced GRPO for reasoning. |
| P11 | ArCHer: Training Language Model Agents via Hierarchical Multi-Turn RL | `llm/alignment/preference-learning` | `llm/agents` | Agentic multi-turn RL. |
| P12 | LoRA Learns Less and Forgets Less | `llm/infrastructure` | `llm/post-training/fine-tuning` | Compares fine-tuning methods. |
| P13 | S-LoRA: Serving Thousands of Concurrent LoRA Adapters | `llm/infrastructure` | `ml-systems/inference-and-serving` | A serving system. |
| P14 | Training Compute-Optimal Large Language Models (Chinchilla) | `llm/infrastructure` | `llm/pretraining` | Scaling laws. |
| P15 | ZeRO: Memory Optimizations Toward Training Trillion Parameter Models | `llm/infrastructure` | `ml-systems/distributed-training` | Distributed training. |
| P16 | Anthropomimetic Uncertainty; Uncertainty Distillation | `llm/reasoning` | `llm/uncertainty-and-hallucination` | About expressing confidence, not reasoning. |
| P17 | Uncertainty Quantification and Confidence Calibration in LLMs: A Survey; Are LLM Decisions Faithful to Verbal Confidence? | `llm/evaluation/methods` | `llm/uncertainty-and-hallucination` | Same reason. |
| P18 | Off-Policy Evaluation for Ranking Policies under Deterministic Logging Policies | `llm/evaluation/methods` | `search-and-ranking/click-models-and-unbiased-ltr` | Counterfactual evaluation of rankers, not LLM evaluation. |
| P19 | Automatic Prompt Optimization with "Gradient Descent" and Beam Search; DSPy; GEPA; Large Language Models as Optimizers; TextGrad; On Transferability of Prompt Tuning | `llm/behaviour` | `llm/prompting-and-in-context` | Prompt optimization, not model behaviour. |
| P20 | Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design; Let Me Speak Freely? | `llm/behaviour` | `llm/prompting-and-in-context` | How prompt form changes results. |
| P21 | State of What Art? A Call for Multi-Prompt LLM Evaluation | `llm/behaviour` | `llm/evaluation/methods` | Evaluation methodology. |
| P22 | Reflexion: Language Agents with Verbal Reinforcement Learning | `llm/behaviour` | `llm/agents` | An agent method. |
| P23 | Agentic Context Engineering | `llm/behaviour` | `llm/context` | Context engineering. |
| P24 | Constitutional AI: Harmlessness from AI Feedback | `llm/behaviour` | `llm/post-training/preference-learning` | A training method (RLAIF). |
| P25 | Deep Learning with Differential Privacy; Membership Inference Attacks against Machine Learning Models | `llm/safety-and-privacy` | `trustworthy-ml/privacy-and-federated` | General ML privacy (2016), not LLM-specific. |
| P26 | Scaling Synthetic Data Creation with 1,000,000,000 Personas; WildFeedback | `llm/evaluation/benchmarks` | `llm/post-training/data` | Training data, not benchmarks. |

After these moves, `llm/behaviour/` keeps instruction following, sycophancy, model specs and constitutions, the instruction hierarchy, deliberative alignment and activation steering.

## Decisions (2026-09-30)

1. **The two biggest folders are split now.**
   - `deep-learning/training-and-optimization/` becomes `optimizers-and-schedules/` and
     `normalization-and-regularization/`. The activation-function papers go to
     `architectures/`.
   - `llm/architecture/` gets `efficient-attention-and-long-context/` and
     `recurrent-and-state-space/`. MoE, positional encoding, tokenization and other variants stay
     at its top level.
2. **"Attention Is All You Need"** stays in `deep-learning/architectures/`.
3. **`curiosities/`** is a new area for papers kept for fun or personal interest outside the
   professional areas. It starts with the two fun reads kept from the review in
   [inventory.md](inventory.md).
