# Reading list: NLP and graphs

The NLP folders hold a thin BERT-era core (BERT, T5, ModernBERT, fine-tuning stability papers), a mixed set of task papers (CRF, fastText, SQuAD, relation extraction, extreme multi-label, TextRank/LexRank), only four generation metrics (BLEU, BERTScore, MoverScore, Word Rotator's Distance), and the graph folders hold GCN/GAT/GraphSAGE, surveys, RelBench and DeepWalk/node2vec/metapath2vec/FastRP. The list fills the obvious holes: the rest of the encoder family (RoBERTa, ALBERT, ELECTRA, DeBERTa, BART, XLM-R, mT5, ELMo, GLUE) plus the 2025 modern-encoder wave; pre-Transformer foundations (seq2seq, attention, BPE/SentencePiece, BiLSTM-CRF) and a few task benchmarks; the learned and factuality metrics that replaced BLEU (COMET, BLEURT, MetricX, SummEval, TRUE, MQM) with SacreBLEU and ROUGE; and for graphs GNN theory (GIN, over-smoothing, over-squashing), self-supervision, benchmarks and evaluation critiques, graph transformers and relational deep learning (RDL, RelGT, KumoRFM-2), and LINE, struc2vec, NetMF, PBG and knowledge-graph embeddings. LLM-specific work (LLM judges, GraphRAG, LLMs on graphs) is left to llm/ lists.

## Proposed

Duplicates removed (2026-10-01), each kept on the list that files it best: 15 Sequence to Sequence Learning with Neural Networks (on deep-and-representation-learning); 16 Neural Machine Translation by Jointly Learning to Align and Translate (on deep-and-representation-learning); 19 Enriching Word Vectors with Subword Information (on deep-and-representation-learning).

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | RoBERTa: A Robustly Optimized BERT Pretraining Approach | 2019 | 1907.11692 | nlp/pretrained-language-models | The recipe (more data, no NSP, dynamic masking) that made BERT a strong baseline; the default encoder checkpoint for years. |
| 2 | ALBERT: A Lite BERT for Self-supervised Learning of Language Representations | 2019 | 1909.11942 | nlp/pretrained-language-models | Parameter sharing and sentence-order prediction; the reference for parameter-efficient encoders. |
| 3 | ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators | 2020 | 2003.10555 | nlp/pretrained-language-models | Replaced-token detection gives far better sample efficiency; the library already has XLM-E built on it. |
| 4 | DeBERTa: Decoding-enhanced BERT with Disentangled Attention | 2020 | 2006.03654 | nlp/pretrained-language-models | Disentangled position/content attention; the strongest BERT-family encoder on GLUE/SuperGLUE and still a common cross-encoder backbone. |
| 5 | BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension | 2019 | 1910.13461 | nlp/pretrained-language-models | Denoising encoder-decoder; with T5 (in library) defines the pre-LLM seq2seq pretraining family. |
| 6 | Unsupervised Cross-lingual Representation Learning at Scale | 2019 | 1911.02116 | nlp/pretrained-language-models | XLM-R: the standard multilingual encoder and baseline for cross-lingual transfer. |
| 7 | mT5: A massively multilingual pre-trained text-to-text transformer | 2020 | 2010.11934 | nlp/pretrained-language-models | Multilingual T5; extends the library's T5 paper and is the backbone of learned metrics such as MetricX. |
| 8 | Deep contextualized word representations | 2018 | 1802.05365 | nlp/pretrained-language-models | ELMo: introduced contextual embeddings and the pretrain-then-fine-tune paradigm that BERT generalised. |
| 9 | GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding | 2018 | 1804.07461 | nlp/pretrained-language-models | The benchmark that framed encoder evaluation; needed to read any BERT-era paper. |
| 10 | Don't Stop Pretraining: Adapt Language Models to Domains and Tasks | 2020 | 2004.10964 | nlp/pretrained-language-models | Domain- and task-adaptive continued pretraining; the basis of domain-specific encoders (relevant to search and e-commerce). |
| 11 | NeoBERT: A Next-Generation BERT | 2025 | 2502.19587 | nlp/pretrained-language-models | Modern architecture and data for a BERT-size encoder; companion to ModernBERT (in library). |
| 12 | EuroBERT: Scaling Multilingual Encoders for European Languages | 2025 | 2503.05500 | nlp/pretrained-language-models | Multilingual encoder with 8K context built from modern decoder-style recipes. |
| 13 | mmBERT: A Modern Multilingual Encoder with Annealed Language Learning | 2025 | 2509.06888 | nlp/pretrained-language-models | Massively multilingual ModernBERT-style encoder with annealed language schedule; current multilingual baseline. |
| 14 | Should We Still Pretrain Encoders with Masked Language Modeling? | 2025 | 2507.00994 | nlp/pretrained-language-models | Controlled comparison of MLM vs causal pretraining for encoders; informs when to use each. |
| 17 | Neural Machine Translation of Rare Words with Subword Units | 2015 | 1508.07909 | nlp/tasks-and-methods | BPE for NLP; the tokenization scheme underlying nearly all later models. |
| 18 | SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing | 2018 | 1808.06226 | nlp/tasks-and-methods | Language-independent subword tokenizer used by T5, XLM-R and Llama-family models. |
| 20 | Neural Architectures for Named Entity Recognition | 2016 | 1603.01360 | nlp/tasks-and-methods | BiLSTM-CRF tagger; the standard pre-BERT sequence-labelling architecture, complements the CRF introduction in library. |
| 21 | Matching the Blanks: Distributional Similarity for Relation Learning | 2019 | 1906.03158 | nlp/tasks-and-methods | Entity-marker relation representations learned from text; the standard BERT relation-extraction recipe. |
| 22 | Know What You Don't Know: Unanswerable Questions for SQuAD | 2018 | 1806.03822 | nlp/tasks-and-methods | SQuAD 2.0: adds unanswerable questions; a core extractive-QA benchmark next to SQuAD (in library). |
| 23 | A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference | 2017 | 1704.05426 | nlp/tasks-and-methods | MultiNLI: the main NLI dataset, widely used for entailment training and zero-shot classification. |
| 24 | Get To The Point: Summarization with Pointer-Generator Networks | 2017 | 1704.04368 | nlp/tasks-and-methods | Copy mechanism and coverage for abstractive summarization; the pre-transformer baseline. |
| 25 | PEGASUS: Pre-training with Extracted Gap-sentences for Abstractive Summarization | 2019 | 1912.08777 | nlp/tasks-and-methods | Summarization-specific pretraining objective; strong pre-LLM summarization reference. |
| 26 | A Call for Clarity in Reporting BLEU Scores | 2018 | 1804.08771 | nlp/generation-metrics | SacreBLEU: shows BLEU numbers are not comparable without fixed tokenization; the practical companion to the library's BLEU paper. |
| 27 | ROUGE: A Package for Automatic Evaluation of Summaries | 2004 | https://aclanthology.org/W04-1013/ | nlp/generation-metrics | The standard summarization metric; absent from the library next to BLEU. |
| 28 | Tangled up in BLEU: Reevaluating the Evaluation of Automatic Machine Translation Evaluation Metrics | 2020 | 2006.06264 | nlp/generation-metrics | Shows BLEU-style metrics' correlations rest on outliers; the case for moving to learned metrics. |
| 29 | BLEURT: Learning Robust Metrics for Text Generation | 2020 | 2004.04696 | nlp/generation-metrics | Fine-tuned BERT regression metric with synthetic pretraining; first widely adopted learned metric. |
| 30 | COMET: A Neural Framework for MT Evaluation | 2020 | 2009.09025 | nlp/generation-metrics | Cross-lingual learned metric using source, hypothesis and reference; the de facto MT metric. |
| 31 | xCOMET: Transparent Machine Translation Evaluation through Fine-grained Error Detection | 2023 | 2310.10482 | nlp/generation-metrics | COMET extended with error-span detection; shows how a metric can explain its score. |
| 32 | MetricX-24: The Google Submission to the WMT 2024 Metrics Shared Task | 2024 | 2410.03983 | nlp/generation-metrics | mT5-based hybrid reference/QE metric that topped WMT24; current state of the art for learned MT metrics. |
| 33 | Experts, Errors, and Context: A Large-Scale Study of Human Evaluation for Machine Translation | 2021 | 2104.14478 | nlp/generation-metrics | Shows crowd ratings are unreliable and MQM expert annotation is the gold standard against which metrics are now judged. |
| 34 | BARTScore: Evaluating Generated Text as Text Generation | 2021 | 2106.11520 | nlp/generation-metrics | Scores text by generation likelihood under BART; the idea that LLM-based judges later generalised. |
| 35 | Towards a Unified Multi-Dimensional Evaluator for Text Generation | 2022 | 2210.07197 | nlp/generation-metrics | UniEval: casts multi-aspect NLG evaluation as boolean QA; bridge from BERTScore-era metrics to LLM judges. |
| 36 | SummEval: Re-evaluating Summarization Evaluation | 2020 | 2007.12626 | nlp/generation-metrics | Re-scores 14 metrics against expert judgements and releases annotations; the standard meta-evaluation for summarization. |
| 37 | Asking and Answering Questions to Evaluate the Factual Consistency of Summaries | 2020 | 2004.04228 | nlp/generation-metrics | QAGS: QA-based faithfulness metric; the origin of QA-style factuality evaluation. |
| 38 | TRUE: Re-evaluating Factual Consistency Evaluation | 2022 | 2204.04991 | nlp/generation-metrics | Meta-evaluation of factual-consistency metrics across tasks; the standard comparison for hallucination metrics. |
| 39 | MAUVE: Measuring the Gap Between Neural Text and Human Text using Divergence Frontiers | 2021 | 2102.01454 | nlp/generation-metrics | Distribution-level metric for open-ended generation quality and diversity. |
| 40 | How Powerful are Graph Neural Networks? | 2018 | 1810.00826 | graphs/graph-neural-networks | GIN and the Weisfeiler-Leman bound on message-passing expressiveness; the core theory paper of GNNs. |
| 41 | Modeling Relational Data with Graph Convolutional Networks | 2017 | 1703.06103 | graphs/graph-neural-networks | R-GCN: GCNs for multi-relational and heterogeneous graphs; the basis of heterogeneous GNNs and RelBench baselines. |
| 42 | Deeper Insights into Graph Convolutional Networks for Semi-Supervised Learning | 2018 | 1801.07606 | graphs/graph-neural-networks | Analyses GCN as Laplacian smoothing and names over-smoothing; the reason GNNs stay shallow. |
| 43 | On the Bottleneck of Graph Neural Networks and its Practical Implications | 2020 | 2006.05205 | graphs/graph-neural-networks | Names over-squashing: long-range information is compressed through narrow paths; motivates graph transformers. |
| 44 | Deep Graph Infomax | 2018 | 1809.10341 | graphs/graph-neural-networks | Self-supervised node embeddings by maximising mutual information; start of graph contrastive learning. |
| 45 | Graph Contrastive Learning with Augmentations | 2020 | 2010.13902 | graphs/graph-neural-networks | GraphCL: augmentations for graph contrastive pretraining; the standard reference for graph self-supervision. |
| 46 | Open Graph Benchmark: Datasets for Machine Learning on Graphs | 2020 | 2005.00687 | graphs/graph-neural-networks | The standard large-scale graph benchmark suite with fixed splits; needed to read most GNN results. |
| 47 | Pitfalls of Graph Neural Network Evaluation | 2018 | 1811.05868 | graphs/graph-neural-networks | Shows rankings of GCN/GAT/GraphSAGE flip under fair tuning and splits; a lesson in evaluation rigour. |
| 48 | A critical look at the evaluation of GNNs under heterophily: Are we really making progress? | 2023 | 2302.11640 | graphs/graph-neural-networks | Shows heterophily benchmarks were flawed and simple baselines compete; corrected datasets are now standard. |
| 49 | Do Transformers Really Perform Bad for Graph Representation? | 2021 | 2106.05234 | graphs/graph-neural-networks | Graphormer: structural encodings make full attention work on graphs. |
| 50 | Recipe for a General, Powerful, Scalable Graph Transformer | 2022 | 2205.12454 | graphs/graph-neural-networks | GPS: combines local message passing with global attention and positional encodings; the standard graph-transformer framework. |
| 51 | Graph Transformers: A Survey | 2024 | 2407.09777 | graphs/graph-neural-networks | Maps graph-transformer designs, encodings and scaling; the orienting survey. |
| 52 | Relational Deep Learning: Graph Representation Learning on Relational Databases | 2023 | 2312.04615 | graphs/graph-neural-networks | Frames multi-table databases as temporal graphs for GNNs; the paper behind RelBench (in library) and relational foundation models. |
| 53 | Relational Graph Transformer | 2025 | 2505.10960 | graphs/graph-neural-networks | RelGT: tokenisation of nodes by features, type, hop, time and structure; beats GNNs on RelBench. |
| 54 | KumoRFM-2: Scaling Foundation Models for Relational Learning | 2026 | 2604.12596 | graphs/graph-neural-networks | Relational foundation model with in-context learning and fine-tuning; the current frontier of GNN-style learning on enterprise data. |
| 55 | Position: Graph Learning Will Lose Relevance Due To Poor Benchmarks | 2025 | 2502.14546 | graphs/graph-neural-networks | Argues benchmarks are too small and unrealistic to guide the field; frames what a useful graph benchmark needs. |
| 56 | LINE: Large-scale Information Network Embedding | 2015 | 1503.03578 | graphs/graph-embeddings | First- and second-order proximity embeddings that scale to millions of nodes; the third pillar with DeepWalk and node2vec. |
| 57 | struc2vec: Learning Node Representations from Structural Identity | 2017 | 1704.03165 | graphs/graph-embeddings | Embeds structural roles rather than neighbourhood proximity; the standard contrast to node2vec. |
| 58 | Network Embedding as Matrix Factorization: Unifying DeepWalk, LINE, PTE, and node2vec | 2017 | 1710.02971 | graphs/graph-embeddings | Proves random-walk embeddings factorise a PMI-like matrix; explains why they work. |
| 59 | graph2vec: Learning Distributed Representations of Graphs | 2017 | 1707.05005 | graphs/graph-embeddings | Whole-graph embeddings by analogy with doc2vec; the standard graph-level embedding baseline. |
| 60 | PyTorch-BigGraph: A Large-scale Graph Embedding System | 2019 | 1903.12287 | graphs/graph-embeddings | Partitioned training of billion-edge embeddings; the reference for embeddings at scale. |
| 61 | Translating Embeddings for Modeling Multi-relational Data | 2013 | https://papers.nips.cc/paper_files/paper/2013/hash/1cecc7a77928ca8133fa24680a88d2f9-Abstract.html | graphs/graph-embeddings | TransE: the origin of knowledge-graph embedding; needed for any KG link-prediction work. |
| 62 | Embedding Entities and Relations for Learning and Inference in Knowledge Bases | 2014 | 1412.6575 | graphs/graph-embeddings | DistMult: bilinear KG embedding that remains a strong baseline. |
| 63 | Complex Embeddings for Simple Link Prediction | 2016 | 1606.06357 | graphs/graph-embeddings | ComplEx: complex-valued embeddings handling asymmetric relations. |
| 64 | RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space | 2019 | 1902.10197 | graphs/graph-embeddings | Relations as rotations; models symmetry, inversion and composition and is a widely used baseline. |
| 65 | A Review of Relational Machine Learning for Knowledge Graphs | 2015 | 1503.00759 | graphs/graph-embeddings | Survey of latent-feature and graph-feature models for KGs; the orienting overview. |

## Added from "Considered" at Anton's request (2026-10-01)

GraphToken (Let Your Graph Do the Talking) stands for the "Talk like a Graph follow-ups" row.

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 66 | GFM-RAG: Graph Foundation Model for Retrieval Augmented Generation | 2025 | 2502.01113 | llm/retrieval-augmented | Moved in from Considered by Anton. |
| 67 | GraphGPT: Graph Instruction Tuning for Large Language Models | 2023 | 2310.13023 | graphs/graph-neural-networks | Moved in from Considered by Anton. |
| 68 | Let Your Graph Do the Talking: Encoding Structured Data for LLMs | 2024 | 2402.05862 | graphs/graph-neural-networks | Moved in from Considered by Anton. |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| RoBERTa-like variants: SpanBERT, XLNet | 2019 | 1907.10529, 1906.08237 | nlp/pretrained-language-models | Superseded by RoBERTa/ELECTRA/DeBERTa; little current use |
| SuperGLUE | 2019 | 1905.00537 | nlp/pretrained-language-models | Saturated; GLUE covers the framing |
| Language-specific ModernBERTs (ModernGBERT, Finnish ModernBERT, Polish ModernBERT) | 2025 | 2505.13136, 2511.09213, 2609.01379 | nlp/pretrained-language-models | Language-specific variants with narrow uptake |
| Longformer, DistilBERT, TinyBERT, Adapters, BERT Rediscovers the Classical NLP Pipeline, Sentence-BERT | 2019-2020 | various | nlp/pretrained-language-models | Already in library under other folders |
| GloVe | 2014 | aclanthology D14-1162 | representation-learning/embeddings | Belongs with word2vec in representation-learning, not NLP tasks |
| Stanza; TriviaQA | 2020; 2017 | 2003.07082, 1705.03551 | nlp/tasks-and-methods | Toolkit and dataset with little relevance to Anton's areas |
| Transformer (Attention Is All You Need) | 2017 | 1706.03762 | deep-learning | Belongs to deep-learning architecture folders |
| CIDEr, SPICE | 2014-2016 | 1411.5726, 1607.08822 | vision-and-multimodal | Image-captioning metrics |
| GEMBA, G-Eval style LLM-based evaluators | 2023 | 2302.14520 | llm/evaluation | LLM-specific; belongs under llm/ |
| METEOR, chrF, TER | 2005-2015 | n/a | nlp/generation-metrics | Superseded by BLEURT/COMET; marginal use |
| SGC, APPNP, Cluster-GCN, DropEdge, GraphMAE | 2018-2022 | 1902.07153, 1810.05997, 1905.07953, 1907.10903, 2205.10803 | graphs/graph-neural-networks | Incremental scaling/depth variants; GraphSAINT already in library |
| PyTorch Geometric | 2019 | 1903.02428 | graphs/graph-neural-networks | Software library paper; useful but not conceptual |
| GraphBench; GraphFM | 2024-2025 | 2512.04475, 2406.08310 | graphs/graph-neural-networks | Overlap OGB and the position paper; little uptake yet |
| GraphGPT; Talk like a Graph follow-ups; GraphAny | 2023-2024 | 2310.13023, 2405.20445 | graphs/graph-neural-networks | LLM-on-graph work belongs under llm/; GraphAny niche |
| GFM-RAG | 2025 | 2502.01113 | llm/retrieval-augmented | GraphRAG belongs under LLM retrieval |
| Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges; Transformers are Graph Neural Networks | 2021; 2025 | 2104.13478, 2506.22084 | graphs/graph-neural-networks | Book-length/essay; geometric deep learning survey already in library |
| GraphVite | 2019 | 1903.00757 | graphs/graph-embeddings | Overlaps PyTorch-BigGraph |
| GraRep, SDNE, ProNE, HOPE | 2015-2019 | n/a | graphs/graph-embeddings | Superseded by NetMF and LINE; no arXiv versions |
