# Reading list: search and ranking

The library's 62 search-and-ranking papers lean on classical IR, early neural rankers (DRMM, KNRM, DSSM), BERT/T5 rerankers, DPR/ColBERT/ANCE, a handful of click-model and unbiased LTR papers, and industry systems from Yahoo, Facebook, LinkedIn and Etsy. This list adds the missing sources (BM25, WAND, RankNet, ERR/NDCG, DBN and position-bias click models, the PageRank-era web search paper), the modern retrieval stack (SPLADE-v3, ColBERTv2/PLAID, hard-negative mining, E5/BGE/GTE and LLM-based embedders, MTEB/BEIR/BRIGHT), LLM rerankers and query expansion, the LLM-relevance-judgement debate, and a block of approximate nearest-neighbour papers. There is no ANN folder in the catalog: the ANN papers (HNSW, DiskANN, FreshDiskANN, SPANN, ScaNN, Faiss, ANN-Benchmarks) are filed under dense-retrieval as the nearest fit, and a dedicated `search-and-ranking/vector-search` folder would be the natural home if Anton wants one. The two Airbnb/LinkedIn/Baidu style systems papers fill the industry gap; video, people and enterprise-search specifics are thin in the public literature and have no strong candidates not already present.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | The Probabilistic Relevance Framework: BM25 and Beyond | 2009 | https://doi.org/10.1561/1500000019 | search-and-ranking/indexing-and-classical-ir | The reference derivation of BM25 and BM25F, the lexical baseline every retriever is measured against. |
| 2 | Efficient Query Evaluation using a Two-Level Retrieval Process (WAND) | 2003 | https://doi.org/10.1145/956863.956944 | search-and-ranking/indexing-and-classical-ir | Dynamic pruning that makes top-k retrieval over inverted indexes fast; the basis of production first-stage scoring. |
| 3 | Learning to Rank using Gradient Descent (RankNet) | 2005 | https://www.microsoft.com/en-us/research/publication/learning-to-rank-using-gradient-descent/ | search-and-ranking/learning-to-rank | The pairwise neural loss that started the RankNet-LambdaRank-LambdaMART line; the library has the overview but not the source paper. |
| 4 | The LambdaLoss Framework for Ranking Metric Optimization | 2018 | https://doi.org/10.1145/3269206.3271784 | search-and-ranking/learning-to-rank | Gives LambdaRank/LambdaMART a probabilistic loss and explains why lambdas optimise NDCG. |
| 5 | An Alternative Cross Entropy Loss for Learning-to-Rank | 2019 | 1911.09798 | search-and-ranking/learning-to-rank | Shows a softmax-style listwise loss bounds NDCG; the default listwise loss in neural LTR. |
| 6 | CatBoost: unbiased boosting with categorical features | 2017 | 1706.09516 | search-and-ranking/learning-to-rank | Yandex's GBDT library, ordered boosting and a widely used LTR ranker (YetiRank); ties to the Yandex LTR background. |
| 7 | Passage Re-ranking with BERT | 2019 | 1901.04085 | search-and-ranking/neural-ranking | monoBERT, the first BERT cross-encoder reranker and the baseline for everything after. |
| 8 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents | 2023 | 2304.09542 | search-and-ranking/neural-ranking | RankGPT: listwise prompting with sliding windows, and distillation into small rankers. |
| 9 | Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting | 2023 | 2306.17563 | search-and-ranking/neural-ranking | Pairwise prompting lets open LLMs rerank competitively; the efficiency-vs-quality contrast to listwise. |
| 10 | RankZephyr: Effective and Robust Zero-Shot Listwise Reranking is a Breeze! | 2023 | 2312.02724 | search-and-ranking/neural-ranking | Open listwise reranker that matches GPT-4 reranking; the usual open baseline. |
| 11 | Rank1: Test-Time Compute for Reranking in Information Retrieval | 2025 | 2502.18418 | search-and-ranking/neural-ranking | Reasoning-trace reranker; first serious test-time-compute approach to reranking. |
| 12 | Query2doc: Query Expansion with Large Language Models | 2023 | 2303.07678 | search-and-ranking/neural-ranking | Pseudo-documents from an LLM appended to the query; simple and effective expansion. |
| 13 | Large Language Models for Information Retrieval: A Survey | 2023 | 2308.07107 | search-and-ranking/neural-ranking | Covers LLMs as query rewriters, retrievers, rerankers and readers. |
| 14 | Transformer Memory as a Differentiable Search Index | 2022 | 2202.06991 | search-and-ranking/neural-ranking | Generative retrieval: a model maps queries straight to document ids; the alternative to index-based retrieval. |
| 15 | SPLADE-v3: New baselines for SPLADE | 2024 | 2403.06789 | search-and-ranking/dense-retrieval | Current SPLADE recipe for learned sparse retrieval; the original SPLADE is the line it extends. |
| 16 | Sparse, Dense, and Attentional Representations for Text Retrieval | 2020 | 2005.00181 | search-and-ranking/dense-retrieval | Theory and experiments on when dense dual encoders fail and why hybrid with sparse helps. |
| 17 | ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction | 2021 | 2112.01488 | search-and-ranking/dense-retrieval | Residual compression and denoised supervision for late interaction; the usual multi-vector baseline. |
| 18 | PLAID: An Efficient Engine for Late Interaction Retrieval | 2022 | 2205.09707 | search-and-ranking/dense-retrieval | Makes ColBERTv2 search several times faster; the serving side of late interaction. |
| 19 | RocketQA: An Optimized Training Approach to Dense Passage Retrieval for Open-Domain Question Answering | 2020 | 2010.08191 | search-and-ranking/dense-retrieval | Cross-batch negatives, denoised hard negatives and distillation, the core of hard-negative mining practice. |
| 20 | Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling | 2021 | 2104.06967 | search-and-ranking/dense-retrieval | Topic-aware batches plus margin distillation from a cross-encoder; cheap and strong training recipe. |
| 21 | NV-Retriever: Improving text embedding models with effective hard-negative mining | 2024 | 2407.15831 | search-and-ranking/dense-retrieval | Positive-aware false-negative filtering in hard-negative mining; the recent systematic treatment. |
| 22 | Unsupervised Dense Information Retrieval with Contrastive Learning (Contriever) | 2021 | 2112.09118 | search-and-ranking/dense-retrieval | Label-free contrastive pre-training for dense retrieval, strong zero-shot. |
| 23 | Text Embeddings by Weakly-Supervised Contrastive Pre-training (E5) | 2022 | 2212.03533 | search-and-ranking/dense-retrieval | The recipe behind the E5 family: large weakly supervised pairs, then fine-tuning; a baseline for enterprise embedders. |
| 24 | M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation | 2024 | 2402.03216 | search-and-ranking/dense-retrieval | BGE-M3: one model for dense, sparse and multi-vector retrieval across 100+ languages. |
| 25 | Improving Text Embeddings with Large Language Models | 2023 | 2401.00368 | search-and-ranking/dense-retrieval | E5-Mistral: decoder LLM as embedder trained on synthetic data; start of the LLM-embedder era. |
| 26 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | 2023 | 2310.08319 | search-and-ranking/dense-retrieval | RepLLaMA and RankLLaMA: LLM bi-encoder and cross-encoder trained on MS MARCO. |
| 27 | NV-Embed: Improved Techniques for Training LLMs as Generalist Embedding Models | 2024 | 2405.17428 | search-and-ranking/dense-retrieval | Latent-attention pooling and two-stage training; top of MTEB and the template for later LLM embedders. |
| 28 | Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models | 2025 | 2506.05176 | search-and-ranking/dense-retrieval | Open embedding and reranker series built on an LLM with synthetic training data; widely used current baseline. |
| 29 | Gemini Embedding: Generalizable Embeddings from Gemini | 2025 | 2503.07891 | search-and-ranking/dense-retrieval | Distillation from a frontier LLM into an embedder; set the MTEB state of the art in 2025. |
| 30 | Promptagator: Few-shot Dense Retrieval From 8 Examples | 2022 | 2209.11755 | search-and-ranking/dense-retrieval | LLM-generated synthetic queries to train task-specific retrievers; foundation of synthetic-data retrieval training. |
| 31 | BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models | 2021 | 2104.08663 | search-and-ranking/dense-retrieval | The standard zero-shot benchmark; shows BM25 is hard to beat out of domain. |
| 32 | MTEB: Massive Text Embedding Benchmark | 2022 | 2210.07316 | search-and-ranking/dense-retrieval | The embedder leaderboard every model above reports on. |
| 33 | BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval | 2024 | 2407.12883 | search-and-ranking/dense-retrieval | Queries that need reasoning; where current retrievers fail and the reasoning-reranker work is tested. |
| 34 | Dense Text Retrieval based on Pretrained Language Models: A Survey | 2022 | 2211.14876 | search-and-ranking/dense-retrieval | The best single survey of dense retrieval architecture, training and negatives. |
| 35 | Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs (HNSW) | 2016 | 1603.09320 | search-and-ranking/dense-retrieval | The default graph ANN index in nearly every vector database (ANN folder gap; see notes). |
| 36 | DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node | 2019 | https://papers.nips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html | search-and-ranking/dense-retrieval | SSD-resident graph index from Microsoft; the basis of billion-scale serving at Bing (ANN folder gap). |
| 37 | Accelerating Large-Scale Inference with Anisotropic Vector Quantization (ScaNN) | 2019 | 1908.10396 | search-and-ranking/dense-retrieval | Score-aware quantization for inner-product search; Google's production ANN (ANN folder gap). |
| 38 | Billion-scale similarity search with GPUs | 2017 | 1702.08734 | search-and-ranking/dense-retrieval | The Faiss paper: product quantization and IVF on GPUs (ANN folder gap). |
| 39 | ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms | 2018 | 1807.05614 | search-and-ranking/dense-retrieval | The standard recall-vs-QPS comparison of ANN libraries (ANN folder gap). |
| 40 | An Experimental Comparison of Click Position-Bias Models | 2008 | https://doi.org/10.1145/1341531.1341545 | search-and-ranking/click-models-and-unbiased-ltr | Cascade and position-bias click models compared on real logs; the starting point of click modelling. |
| 41 | A Dynamic Bayesian Network Click Model for Web Search Ranking | 2009 | https://doi.org/10.1145/1526709.1526711 | search-and-ranking/click-models-and-unbiased-ltr | DBN separates attractiveness from satisfaction; the standard click model used to derive relevance labels. |
| 42 | Optimizing Search Engines using Clickthrough Data | 2002 | https://doi.org/10.1145/775047.775067 | search-and-ranking/click-models-and-unbiased-ltr | The founding paper on learning rankers from click logs (Ranking SVM, preference pairs). |
| 43 | Unbiased LambdaMART: An Unbiased Pairwise Learning-to-Rank Algorithm | 2018 | 1809.05818 | search-and-ranking/click-models-and-unbiased-ltr | Joint propensity and ranker estimation inside LambdaMART; the closest recipe to a GBDT production setting. |
| 44 | Policy-Aware Unbiased Learning to Rank for Top-k Rankings | 2020 | 2005.09035 | search-and-ranking/click-models-and-unbiased-ltr | Corrects for items cut off by the logging policy, which plain IPS ignores. |
| 45 | Doubly-Robust Estimation for Correcting Position-Bias in Click Feedback for Unbiased Learning to Rank | 2022 | 2203.17118 | search-and-ranking/click-models-and-unbiased-ltr | Doubly-robust estimator with lower variance and robust to propensity error; current standard in counterfactual LTR. |
| 46 | A Large Scale Search Dataset for Unbiased Learning to Rank | 2022 | 2207.03051 | search-and-ranking/click-models-and-unbiased-ltr | Baidu-ULTR, the first real-click benchmark for ULTR; the library already has the follow-up reality check. |
| 47 | Towards Disentangling Relevance and Bias in Unbiased Learning to Rank | 2022 | 2212.13937 | search-and-ranking/click-models-and-unbiased-ltr | Two-tower additive relevance/bias model deployed in practice; baseline on Baidu-ULTR. |
| 48 | Cumulated Gain-Based Evaluation of IR Techniques | 2002 | https://doi.org/10.1145/582415.582418 | search-and-ranking/evaluation | Defines DCG/NDCG, the metric that most ranking work optimises and reports. |
| 49 | Expected Reciprocal Rank for Graded Relevance | 2009 | https://doi.org/10.1145/1645953.1646033 | search-and-ranking/evaluation | Cascade-based metric with diminishing returns, from Yahoo/Yandex-era web ranking; a counterpart to NDCG. |
| 50 | MS MARCO: A Human Generated MAchine Reading COmprehension Dataset | 2016 | 1611.09268 | search-and-ranking/evaluation | The Bing-derived passage ranking data behind most neural ranking and dense retrieval work. |
| 51 | Overview of the TREC 2019 Deep Learning Track | 2020 | 2003.07820 | search-and-ranking/evaluation | Established the deep-judged MS MARCO evaluation that exposed the BERT-era gains. |
| 52 | Shallow pooling for sparse labels | 2021 | 2109.00062 | search-and-ranking/evaluation | Shows MS MARCO's sparse labels mis-rank systems, motivating deeper judgements and LLM judging. |
| 53 | Large language models can accurately predict searcher preferences | 2023 | 2309.10621 | search-and-ranking/evaluation | Bing's study of LLM relevance labels against human raters; the paper that started LLM judging in industry. |
| 54 | UMBRELA: UMbrela is the (Open-Source Reproduction of the) Bing RELevance Assessor | 2024 | 2406.06519 | search-and-ranking/evaluation | Open reproduction of the Bing LLM assessor, used in TREC RAG; the practical reference implementation. |
| 55 | Don't Use LLMs to Make Relevance Judgments | 2024 | 2409.15133 | search-and-ranking/evaluation | The main argument against LLM judges (circularity, bias); the counterweight to the Bing study. |
| 56 | The Anatomy of a Large-Scale Hypertextual Web Search Engine | 1998 | http://infolab.stanford.edu/~backrub/google.html | search-and-ranking/search-systems | The original Google architecture paper: crawl, index, PageRank and ranking. |
| 57 | Large Search Model: Redefining Search Stack in the Era of LLMs | 2023 | 2310.14587 | search-and-ranking/search-systems | Microsoft's proposal to replace the stack of rankers with one LLM; relevant to Copilot-style search. |
| 58 | Pre-trained Language Model based Ranking in Baidu Search | 2021 | 2105.11108 | search-and-ranking/search-systems | Shipping a BERT ranker in web search: pruning, distillation and calibration with click data. |
| 59 | Deep Natural Language Processing for LinkedIn Search Systems | 2021 | 2108.08252 | search-and-ranking/search-systems | Query intent, ranking and retrieval with transformers in a people/jobs search product. |
| 60 | Practical Lessons from Predicting Clicks on Ads at Facebook | 2014 | https://doi.org/10.1145/2648584.2648589 | search-and-ranking/ads | GBDT-feature plus logistic regression for CTR; a reference industrial ads ranking design. |

## Added from "Considered" at Anton's request (2026-10-01)

| # | Paper | Year | arXiv / URL | Folder |
|--:|---|--:|---|---|
| 61 | Improving Deep Learning For Airbnb Search | 2020 | 2002.05515 | search-and-ranking/search-systems |
| 62 | Pre-trained Language Model for Web-scale Retrieval in Baidu Search | 2021 | 2106.03373 | search-and-ranking/dense-retrieval |
| 63 | Perspectives on Large Language Models for Relevance Judgment | 2023 | 2304.09161 | search-and-ranking/evaluation |
| 64 | Synthetic Test Collections for Retrieval Evaluation | 2024 | 2405.07767 | search-and-ranking/evaluation |
| 65 | Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference | 2024 | 2412.13663 | nlp/pretrained-language-models |
| 66 | LLM2Vec: Large Language Models Are Secretly Powerful Text Encoders | 2024 | 2404.05961 | search-and-ranking/dense-retrieval |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| SPLADE / SPLADE v2 | 2021 | 2107.05720, 2109.10086 | search-and-ranking/dense-retrieval | Superseded by SPLADE-v3, which is proposed. |
| Nomic Embed | 2024 | 2402.01613 | search-and-ranking/dense-retrieval | Reproducible but a variant of the E5/GTE recipe; little uptake beyond open-source circles. |
| LLM2Vec | 2024 | 2404.05961 | search-and-ranking/dense-retrieval | Adapts decoders to embedders; covered in effect by E5-Mistral and NV-Embed. |
| ModernBERT | 2024 | 2412.13663 | search-and-ranking/dense-retrieval | General encoder, not retrieval-specific; belongs in an NLP/architecture area. |
| Jina-ColBERT-v2 | 2024 | 2408.16672 | search-and-ranking/dense-retrieval | Incremental multilingual ColBERT variant. |
| A Few Brief Notes on DeepImpact, COIL, and uniCOIL | 2021 | 2106.14807 | search-and-ranking/dense-retrieval | Short note; superseded by SPLADE for learned sparse retrieval. |
| Gemini/Qwen3-VL embedding, ColPali successors | 2026 | 2601.04720 | search-and-ranking/dense-retrieval | Multimodal document retrieval is outside this folder; ColPali is already in vision-and-multimodal. |
| RaBitQ | 2024 | 2405.12497 | search-and-ranking/dense-retrieval | Promising quantization but little deployment evidence yet; revisit if a vector-search folder is created. |
| The Faiss library | 2024 | 2401.08281 | search-and-ranking/dense-retrieval | Library description; the 2017 GPU paper is proposed instead. |
| Results of the NeurIPS'21 Billion-Scale ANN Challenge | 2022 | 2205.03763 | search-and-ranking/dense-retrieval | Competition report; less canonical than ANN-Benchmarks. |
| Query Expansion by Prompting LLMs | 2023 | 2305.03653 | search-and-ranking/neural-ranking | Overlaps Query2doc and HyDE (already in library). |
| Generative Relevance Feedback with LLMs | 2023 | 2304.13157 | search-and-ranking/neural-ranking | Incremental expansion variant. |
| RankVicuna | 2023 | 2309.15088 | search-and-ranking/neural-ranking | Superseded by RankZephyr. |
| A Setwise Approach for Zero-shot Ranking with LLMs | 2023 | 2310.09497 | search-and-ranking/neural-ranking | Efficiency variant of PRP/listwise; limited uptake. |
| Rank-R1 | 2025 | 2503.06034 | search-and-ranking/neural-ranking | Overlaps Rank1; RL-trained reasoning rerankers are still moving fast. |
| Rank-DistiLLM | 2024 | 2405.07920 | search-and-ranking/neural-ranking | Incremental distillation study. |
| JudgeRank, E2Rank, jina-reranker-v3 | 2024-2025 | 2411.00142, 2510.22733, 2509.25085 | search-and-ranking/neural-ranking | Recent rerankers with little uptake as baselines yet. |
| ReasonIR | 2025 | 2504.20595 | search-and-ranking/dense-retrieval | Useful but BRIGHT is the benchmark of record; add if reasoning retrieval becomes a focus. |
| A Survey of Reasoning-Intensive Retrieval | 2026 | 2605.00063 | search-and-ranking/dense-retrieval | Very new survey with no track record; dense-retrieval survey is proposed instead. |
| C-Pack (BGE) | 2023 | 2309.07597 | search-and-ranking/dense-retrieval | Chinese-focused; BGE-M3 is proposed instead. |
| Rethinking Search: Making Domain Experts out of Dilettantes | 2021 | 2105.02274 | search-and-ranking/search-systems | Position paper, not a method. |
| LLMJudge: LLMs for Relevance Judgments | 2024 | 2408.08896 | search-and-ranking/evaluation | Challenge overview; the individual judging papers are proposed. |
| A Large-Scale Study of Relevance Assessments with LLMs | 2024 | 2411.08275 | search-and-ranking/evaluation | Overlaps UMBRELA and the Bing study. |
| SetRank | 2019 | 1912.05891 | search-and-ranking/learning-to-rank | Covered by the groupwise scoring paper; minor uptake. |
| Learning-to-Rank with BERT in TF-Ranking | 2020 | 2004.08476 | search-and-ranking/learning-to-rank | Incremental over TF-Ranking and monoBERT. |
| Whole Page Unbiased Learning to Rank | 2022 | 2210.10718 | search-and-ranking/click-models-and-unbiased-ltr | Niche setting; Baidu-ULTR papers cover the topic. |
| Towards Deep and Representation Learning for Talent Search at LinkedIn | 2018 | 1809.06473 | search-and-ranking/search-systems | Covered by the LinkedIn NLP search paper. |
| Applying Deep Learning To Airbnb Search | 2018 | 1810.09591 | search-and-ranking/search-systems | Superseded by the 2020 lessons paper. |
| Web-Scale Responsive Visual Search at Bing | 2018 | 1802.04914 | search-and-ranking/search-systems | Visual search is better filed with vision-and-multimodal; Pinterest's is already here. |
| FreshDiskANN; SPANN | 2021 | 2105.09613, 2111.08566 | search-and-ranking/dense-retrieval | Variants of DiskANN-style serving; add if a vector-search folder is created. |
| TF-Ranking; Groupwise scoring functions | 2018 | 1812.00073, 1811.04415 | search-and-ranking/learning-to-rank | Useful libraries/architectures but the library's neural-vs-GBDT papers cover the ground. |
| Unbiased propensity estimation; Estimating position bias; Online or Offline | 2018-2020 | 1804.05938, 1812.05161, 2004.13574 | search-and-ranking/click-models-and-unbiased-ltr | Overlap Unbiased LambdaMART and the doubly-robust paper already proposed. |
| GTE; Gecko; GTR; coCondenser; Pre-training Tasks for EBR | 2020-2024 | 2308.03281, 2403.20327, 2112.07899, 2108.05540, 2002.03932 | search-and-ranking/dense-retrieval | Strong but largely covered by E5, BGE-M3, NV-Embed and RocketQA. |
| Doc2Query--; FIRST; Semantic Product Search; Airbnb 2020; Baidu web-scale retrieval | 2019-2023 | 2301.03266, 2406.15657, 1907.00937, 2002.05515, 2106.03373 | search-and-ranking/various | Cut for length; good second-tier additions. |
| Perspectives on LLMs for Relevance Judgment; Synthetic Test Collections | 2023-2024 | 2304.09161, 2405.07767 | search-and-ranking/evaluation | Second-tier LLM-judging papers. |
