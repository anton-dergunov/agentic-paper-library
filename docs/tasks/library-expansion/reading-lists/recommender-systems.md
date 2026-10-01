# Reading list: recommender systems

The library has 37 recommender papers: NCF, EASE, the BellKor Netflix solution, SASRec, BERT4Rec, the YouTube DNN paper, TIGER, HSTU, PinSage and Pixie, Google Drive and Outlook-style email recommendation, and the evaluation classics (sampled metrics, 'Are we really making much progress'). Missing are the canonical CF and CTR foundations (BPR, iALS, FM, Wide & Deep, DLRM, DCN, two-tower with bias correction, MMoE/PLE), the LLM-for-recommendation line, the 2024-2026 generative and scaling wave (OneRec, PLUM, MTGR, RankMixer, UniPinRec, Netflix GenRec) and the industry ranking papers from LinkedIn, ByteDance, Pinterest and Kuaishou, plus the offline-evaluation literature on leakage, splits and baselines. Factorization Machines, the two-tower bias-correction paper, MMoE, PLE and the YouTube multitask paper are not on arXiv, so they get DOIs. Bandit papers are not proposed here; none is recommendation-specific enough to be missing from reinforcement-learning/bandits. No candidate fit outside the five existing folders.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | BPR: Bayesian Personalized Ranking from Implicit Feedback | 2012 | 1205.2618 | recommender-systems/collaborative-filtering | The pairwise ranking loss behind most implicit-feedback training; the standard baseline. |
| 2 | Collaborative Filtering for Implicit Feedback Datasets | 2008 | https://doi.org/10.1109/ICDM.2008.22 | recommender-systems/collaborative-filtering | The original iALS: confidence-weighted ALS for implicit data, still a production workhorse. |
| 3 | Revisiting the Performance of iALS on Item Recommendation Benchmarks | 2021 | 2110.14037 | recommender-systems/collaborative-filtering | Shows a tuned iALS matches or beats newer models; essential companion to the iALS paper. |
| 4 | Factorization Machines | 2010 | https://doi.org/10.1109/ICDM.2010.127 | recommender-systems/collaborative-filtering | Rendle's FM: pairwise feature interactions in linear time; ancestor of DeepFM, DLRM and most CTR models. |
| 5 | Variational Autoencoders for Collaborative Filtering | 2018 | 1802.05814 | recommender-systems/collaborative-filtering | Mult-VAE: a strong non-linear CF baseline that complements EASE. |
| 6 | LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation | 2020 | 2002.02126 | recommender-systems/collaborative-filtering | The standard graph-CF baseline; shows what GCN parts actually matter. |
| 7 | Wide & Deep Learning for Recommender Systems | 2016 | 1606.07792 | recommender-systems/deep-and-sequential | Google Play's memorization plus generalization ranker; the template for deep ranking. |
| 8 | Deep Learning Recommendation Model for Personalization and Recommendation Systems | 2019 | 1906.00091 | recommender-systems/deep-and-sequential | Meta's DLRM: the reference architecture and benchmark for embedding-heavy recommenders. |
| 9 | Deep & Cross Network for Ad Click Predictions | 2017 | 1708.05123 | recommender-systems/deep-and-sequential | Explicit bounded-degree feature crossing; origin of the DCN family. |
| 10 | DCN V2: Improved Deep & Cross Network and Practical Lessons for Web-scale Learning to Rank Systems | 2020 | 2008.13535 | recommender-systems/deep-and-sequential | The production-hardened DCN, with low-rank and mixture-of-experts crossing and practical lessons. |
| 11 | DeepFM: A Factorization-Machine based Neural Network for CTR Prediction | 2017 | 1703.04247 | recommender-systems/deep-and-sequential | Shares embeddings between an FM and a deep part; a widely used CTR baseline. |
| 12 | Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations | 2019 | https://doi.org/10.1145/3298689.3346996 | recommender-systems/deep-and-sequential | The two-tower retrieval recipe with in-batch logQ correction used across industry. |
| 13 | Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts | 2018 | https://doi.org/10.1145/3219819.3220007 | recommender-systems/deep-and-sequential | MMoE: the standard multi-task ranking architecture (YouTube, many others). |
| 14 | Progressive Layered Extraction (PLE): A Novel Multi-Task Learning Model for Personalized Recommendations | 2020 | https://doi.org/10.1145/3383313.3412236 | recommender-systems/deep-and-sequential | Fixes MMoE's seesaw effect with task-specific and shared experts; RecSys 2020 best paper. |
| 15 | Recommending What Video to Watch Next: A Multitask Ranking System | 2019 | https://doi.org/10.1145/3298689.3346997 | recommender-systems/deep-and-sequential | YouTube's multitask ranker with MMoE and a shallow tower for selection bias. |
| 16 | Deep Interest Network for Click-Through Rate Prediction | 2017 | 1706.06978 | recommender-systems/deep-and-sequential | Target-aware attention over user behaviour; the start of behaviour-sequence CTR modelling. |
| 17 | Search-based User Interest Modeling with Lifelong Sequential Behavior Data for Click-Through Rate Prediction | 2020 | 2006.05639 | recommender-systems/deep-and-sequential | SIM: long-history modelling by retrieving relevant behaviours first; widely deployed. |
| 18 | Session-based Recommendations with Recurrent Neural Networks | 2015 | 1511.06939 | recommender-systems/deep-and-sequential | GRU4Rec: the paper that started neural sequential recommendation. |
| 19 | Turning Dross Into Gold Loss: is BERT4Rec really better than SASRec? | 2023 | 2309.07602 | recommender-systems/deep-and-sequential | Shows SASRec with cross-entropy beats BERT4Rec; resolves the SASRec versus BERT4Rec question. |
| 20 | Revisiting Neural Retrieval on Accelerators | 2023 | 2306.04039 | recommender-systems/deep-and-sequential | Mixture-of-logits retrieval beyond dot products, making learned similarity servable on GPUs/TPUs. |
| 21 | Self-supervised Learning for Large-scale Item Recommendations | 2020 | 2007.12865 | recommender-systems/deep-and-sequential | Contrastive augmentations for two-tower retrieval to help the long tail; Google. |
| 22 | Recommendation as Language Processing (RLP): A Unified Pretrain, Personalized Prompt & Predict Paradigm (P5) | 2022 | 2203.13366 | recommender-systems/llm-and-generative | The first unified text-to-text LLM recommender; origin of the LLM-for-recsys wave. |
| 23 | TALLRec: An Effective and Efficient Tuning Framework to Align Large Language Model with Recommendation | 2023 | 2305.00447 | recommender-systems/llm-and-generative | Lightweight instruction tuning of an LLM for rec; common LLM baseline. |
| 24 | Is ChatGPT a Good Recommender? A Preliminary Study | 2023 | 2304.10149 | recommender-systems/llm-and-generative | Early zero-shot evidence of what prompting LLMs does and does not do for recommendation. |
| 25 | Large Language Models are Zero-Shot Rankers for Recommender Systems | 2023 | 2305.08845 | recommender-systems/llm-and-generative | Analyses LLM ranking biases (position, popularity) and how to prompt around them. |
| 26 | A Survey on Large Language Models for Recommendation | 2023 | 2305.19860 | recommender-systems/llm-and-generative | The most-cited survey mapping discriminative and generative LLM-based recommenders. |
| 27 | Better Generalization with Semantic IDs: A Case Study in Ranking for Recommendations | 2023 | 2306.08121 | recommender-systems/llm-and-generative | YouTube: content-derived semantic IDs replace random item IDs in ranking; the bridge to TIGER. |
| 28 | Unifying Generative and Dense Retrieval for Sequential Recommendation | 2024 | 2411.18814 | recommender-systems/llm-and-generative | LIGER: combines semantic-ID generative retrieval with dense retrieval, fixing cold start. |
| 29 | Scaling Law of Large Sequential Recommendation Models | 2023 | 2311.11351 | recommender-systems/llm-and-generative | Empirical scaling laws for sequential recommenders; motivates the HSTU-style scaling line. |
| 30 | OneRec Technical Report | 2025 | 2506.13695 | recommender-systems/llm-and-generative | Kuaishou's end-to-end generative recommender replacing the retrieve-rank cascade in production. |
| 31 | OneRec-V2 Technical Report | 2025 | 2508.20900 | recommender-systems/llm-and-generative | Decoder-only successor with reward-model preference alignment at scale. |
| 32 | PLUM: Adapting Pre-trained Language Models for Industrial-scale Generative Recommendations | 2025 | 2510.07784 | recommender-systems/llm-and-generative | YouTube: fine-tuning an LLM on semantic IDs for production generative retrieval. |
| 33 | Semantic IDs for Joint Generative Search and Recommendation | 2025 | 2508.10478 | recommender-systems/llm-and-generative | Spotify: one set of semantic IDs serving both search and recommendation. |
| 34 | Monolith: Real Time Recommendation System With Collisionless Embedding Table | 2022 | 2209.07663 | recommender-systems/industrial-systems | ByteDance/TikTok: collisionless embeddings and online training for real-time recsys. |
| 35 | Top-K Off-Policy Correction for a REINFORCE Recommender System | 2018 | 1812.02353 | recommender-systems/industrial-systems | YouTube: policy-gradient recommender with off-policy correction; recommendation-specific RL. |
| 36 | Deep Retrieval: Learning A Retrievable Structure for Large-Scale Recommendations | 2020 | 2007.07203 | recommender-systems/industrial-systems | ByteDance: learned retrieval structure (an early semantic-ID-like index) end to end. |
| 37 | Wukong: Towards a Scaling Law for Large-Scale Recommendation | 2024 | 2403.02545 | recommender-systems/industrial-systems | Meta: stacked factorization machines that show scaling laws in ranking. |
| 38 | LiRank: Industrial Large Scale Ranking Models at LinkedIn | 2024 | 2402.06859 | recommender-systems/industrial-systems | LinkedIn's lessons combining DCN V2, attention and calibration in production ranking. |
| 39 | 360Brew: A Decoder-only Foundation Model for Personalized Ranking and Recommendation | 2025 | 2501.16450 | recommender-systems/industrial-systems | LinkedIn: one LLM-based ranker replacing many task-specific models. |
| 40 | TransAct: Transformer-based Realtime User Action Model for Recommendation at Pinterest | 2023 | 2306.00248 | recommender-systems/industrial-systems | Pinterest: realtime sequence model for the Homefeed ranker. |
| 41 | PinRec: Unified Generative Retrieval for Pinterest Recommender Systems | 2025 | 2504.10507 | recommender-systems/industrial-systems | Pinterest's outcome-conditioned generative retrieval in production. |
| 42 | UniPinRec: Unifying Generative Retrieval and Ranking at Pinterest Scale | 2026 | 2606.00422 | recommender-systems/industrial-systems | 2026 follow-up merging retrieval and ranking in one generative model on an existing stack. |
| 43 | TWIN: TWo-stage Interest Network for Lifelong User Behavior Modeling in CTR Prediction at Kuaishou | 2023 | 2302.02352 | recommender-systems/industrial-systems | Kuaishou's lifelong behaviour modelling, consistent between search and ranking stages. |
| 44 | LONGER: Scaling Up Long Sequence Modeling in Industrial Recommenders | 2025 | 2505.04421 | recommender-systems/industrial-systems | ByteDance: serving very long user sequences with a transformer efficiently. |
| 45 | RankMixer: Scaling Up Ranking Models in Industrial Recommenders | 2025 | 2507.15551 | recommender-systems/industrial-systems | ByteDance: hardware-friendly ranking architecture scaled to 1B parameters. |
| 46 | MTGR: Industrial-Scale Generative Recommendation Framework in Meituan | 2025 | 2505.18654 | recommender-systems/industrial-systems | Meituan: HSTU-style generative ranking that keeps cross features at production scale. |
| 47 | GenRec: An LLM-Backed Recommendation Ranker at Netflix | 2026 | 2608.10257 | recommender-systems/industrial-systems | Netflix's LLM-backed ranker, a rare detailed Netflix account from 2026. |
| 48 | A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research | 2019 | 1911.07698 | recommender-systems/evaluation | Extends 'Are we really making much progress' to more models and venues; reproducibility reference. |
| 49 | On the Difficulty of Evaluating Baselines: A Study on Recommender Systems | 2019 | 1905.01395 | recommender-systems/evaluation | Properly tuned old baselines beat published gains on MovieLens; why baselines must be tuned. |
| 50 | A Case Study on Sampling Strategies for Evaluating Neural Sequential Item Recommendation Models | 2021 | 2107.13045 | recommender-systems/evaluation | How sampled evaluation distorts sequential model rankings. |
| 51 | Exploring Data Splitting Strategies for the Evaluation of Recommendation Models | 2020 | 2007.13237 | recommender-systems/evaluation | Random versus temporal splits change model rankings; leakage in standard protocols. |
| 52 | A Critical Study on Data Leakage in Recommender System Offline Evaluation | 2020 | 2010.11060 | recommender-systems/evaluation | Quantifies how future-data leakage inflates offline results. |
| 53 | Off-policy evaluation for slate recommendation | 2016 | 1605.04812 | recommender-systems/evaluation | Pseudoinverse estimator for counterfactual evaluation of slates; foundation of offline-to-online work. |
| 54 | The Unfairness of Popularity Bias in Recommendation | 2019 | 1907.13286 | recommender-systems/evaluation | Beyond-accuracy: how popularity bias affects user groups differently. |
| 55 | Bias and Debias in Recommender System: A Survey and Future Directions | 2020 | 2010.03240 | recommender-systems/evaluation | One survey of the biases (position, exposure, popularity) that break offline evaluation. |
| 56 | Understanding the Role of Cross-Entropy Loss in Fairly Evaluating Large Language Model-based Recommendation | 2024 | 2402.06216 | recommender-systems/evaluation | Shows many LLM-rec gains come from unfair baseline loss choices. |

## Added from "Considered" at Anton's request (2026-10-01)

| # | Paper | Year | arXiv / URL | Folder |
|--:|---|--:|---|---|
| 57 | PinnerFormer: Sequence Modeling for User Representation at Pinterest | 2022 | 2205.04507 | recommender-systems/industrial-systems |
| 58 | ItemSage: Learning Product Embeddings for Shopping Recommendations at Pinterest | 2022 | 2205.11728 | recommender-systems/industrial-systems |
| 59 | How Can Recommender Systems Benefit from Large Language Models: A Survey | 2023 | 2306.05817 | recommender-systems/llm-and-generative |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| iALS++: Speeding up Matrix Factorization with Subspace Optimization | 2021 | 2110.14044 | recommender-systems/collaborative-filtering | Speed-up of iALS; implementation detail, covered by the iALS pair. |
| Item2Vec: Neural Item Embedding for Collaborative Filtering | 2016 | 1603.04259 | recommender-systems/collaborative-filtering | Historically useful but superseded by two-tower retrieval. |
| gSASRec: Reducing Overconfidence in Sequential Recommendation Trained with Negative Sampling | 2023 | 2308.07192 | recommender-systems/deep-and-sequential | Incremental SASRec variant; the BERT4Rec vs SASRec paper covers the lesson. |
| Deep Interest Evolution Network for Click-Through Rate Prediction | 2018 | 1809.03672 | recommender-systems/deep-and-sequential | Incremental over DIN, little uptake against later sequence models. |
| Towards Universal Sequence Representation Learning for Recommender Systems (UniSRec) | 2022 | 2206.05941 | recommender-systems/deep-and-sequential | Text-based transfer; superseded by LLM and semantic-ID approaches. |
| LLaRA: Large Language-Recommendation Assistant | 2023 | 2312.02445 | recommender-systems/llm-and-generative | One of many LLM-rec fine-tuning variants; TALLRec and the survey suffice. |
| Adapting Large Language Models by Integrating Collaborative Semantics for Recommendation (LC-Rec) | 2023 | 2311.09049 | recommender-systems/llm-and-generative | Overlaps TIGER and the semantic-ID papers already proposed. |
| How Can Recommender Systems Benefit from Large Language Models: A Survey | 2023 | 2306.05817 | recommender-systems/llm-and-generative | Second LLM survey; one survey is enough. |
| Large Language Models for Generative Recommendation: A Survey and Visionary Discussions | 2023 | 2309.01157 | recommender-systems/llm-and-generative | Same reason; one LLM survey is enough. |
| Generative Recommender with End-to-End Learnable Item Tokenization (ETEGRec) | 2024 | 2409.05546 | recommender-systems/llm-and-generative | Incremental tokenizer variant. |
| Scaling Transformers for Discriminative Recommendation via Generative Pretraining | 2025 | 2506.03699 | recommender-systems/llm-and-generative | Interesting but little uptake so far. |
| Differentiable Semantic ID for Generative Recommendation | 2026 | 2601.19711 | recommender-systems/llm-and-generative | Too recent to show uptake. |
| OneRec-Think: In-Text Reasoning for Generative Recommendation | 2025 | 2510.11639 | recommender-systems/llm-and-generative | Incremental on the OneRec reports. |
| Sparse Meets Dense: Unified Generative Recommendations with Cascaded Sparse-Dense Representations (COBRA) | 2025 | 2503.02453 | recommender-systems/llm-and-generative | Similar to LIGER, which is proposed. |
| GPR: Towards a Generative Pre-trained One-Model Paradigm for Large-Scale Advertising Recommendation | 2025 | 2511.10138 | recommender-systems/llm-and-generative | Advertising-specific; the OneRec and PLUM papers cover the paradigm. |
| Multi-Decoder OneRec: Controllable Generative Retrieval for Multi-Objective Industrial Recommendation | 2026 | 2607.26500 | recommender-systems/llm-and-generative | Incremental variant, unverified uptake. |
| Large Foundation Model for Ads Recommendation | 2025 | 2508.14948 | recommender-systems/industrial-systems | Ads-focused; Wukong and LiRank cover the ranking-scaling story. |
| PinnerFormer: Sequence Modeling for User Representation at Pinterest | 2022 | 2205.04507 | recommender-systems/industrial-systems | Pinterest is already covered by PinnerSage, TransAct and PinRec. |
| ItemSage: Learning Product Embeddings for Shopping Recommendations at Pinterest | 2022 | 2205.11728 | recommender-systems/industrial-systems | Shopping-specific. |
| PEPNet: Parameter and Embedding Personalized Network for Infusing with Personalized Prior Information | 2023 | 2302.01115 | recommender-systems/industrial-systems | Incremental multi-domain gating. |
| Understanding Scaling Laws for Recommendation Models | 2022 | 2208.08489 | recommender-systems/industrial-systems | Wukong and the sequential scaling-law paper supersede it. |
| Software-Hardware Co-design for Fast and Scalable Training of Deep Learning Recommendation Models | 2021 | 2104.05158 | recommender-systems/industrial-systems | Systems-heavy; Monolith and DLRM cover the ground. |
| RecBole: Towards a Unified, Comprehensive and Efficient Framework for Recommendation Algorithms | 2020 | 2011.01731 | recommender-systems/evaluation | A toolkit, not an evaluation result. |
| Offline A/B testing for Recommender Systems | 2018 | 1801.07030 | recommender-systems/evaluation | Covered by the off-policy slate paper and the library's existing evaluation papers. |
| LEARN: Knowledge Adaptation from Large Language Model to Recommendation for Practical Industrial Application | 2024 | 2405.03988 | recommender-systems/llm-and-generative | Industry-specific; limited uptake. |
| Netflix Foundation Model; Meta GEM (engineering blog posts) | 2025 |  | recommender-systems/industrial-systems | Engineering blog posts, not papers. |
