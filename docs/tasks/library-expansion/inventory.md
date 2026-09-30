# Inventory of existing papers

Phase 1 of [the library expansion](../library-expansion.md). `inventory.tsv` has one row per unique
paper referenced anywhere in Anton's material, as of 2026-09-30.

## Where the papers came from

| Source | What was read | Papers |
|---|---|--:|
| `Papers_old/` | all 546 PDFs, by filename | 538 |
| Obsidian | `ML & AI/`, `Statistics/`, `Math/`, `Programming/`: links, paper notes, wiki-links to paper notes, and papers named in prose | 515 |
| Org | every `.org` file except `Body/`, `Play/`, `Admin/`: links and papers named in prose (mostly `ML/*.org`) | 168 |
| **Unique papers** | after merging duplicates across and within sources | **981** |

752 papers appear in only one source: 329 only in `Papers_old/`,
314 only in Obsidian, 109 only in org. All 546 PDFs map to a row; seven
are second copies of a paper (`…2`, a timestamped copy) and share the original's row.

Titles were matched against arXiv (title search), then Crossref, and ids and DOIs were looked up
in Semantic Scholar for year, venue and citation count. 74 papers matched nothing, mostly
pre-arXiv classics and industry papers (Bigtable, BLEU, DBSCAN, t-SNE, the Yahoo LTR challenge,
the Kohavi experimentation papers). They are filed by title and need a PDF from `Papers_old/` or
the publisher when added.

## Columns

`key | title | year | arxiv | url | sources | local_pdf | topic | action | reason | status | venue | citations | matched_from`

- `key`: `arxiv:<id>`, `s2:<Semantic Scholar id>`, or `title:<normalised title>` when nothing matched.
- `sources`: every place the paper is referenced: `papers_old`, `obsidian:<vault path>`, `org:<path>`.
- `local_pdf`: the file stem in `Papers_old/`.
- `topic`: the folder in the approved tree, [structure.md](structure.md).
- `action`: `add`, `in-library` or `skip`.
- `status`: `todo`, then `added`, `skipped` or `in-library`.
- `citations`: Semantic Scholar's count, a rough signal only, since preprint and proceedings
  records are sometimes split.
- `matched_from`: the original titles, when they differ from the matched one.

## Counts

| Action | Papers |
|---|--:|
| add | 862 |
| skip | 91 |
| already in the library | 28 |

Of the 862 to add, 703 have an arXiv id, 90 exist only as a local PDF, and 69 need a
PDF from the web.

| Area | To add |
|---|--:|
| `llm/` | 233 |
| `deep-learning/` | 96 |
| `vision-and-multimodal/` | 69 |
| `search-and-ranking/` | 61 |
| `nlp/` | 50 |
| `representation-learning/` | 46 |
| `interpretability/` | 41 |
| `recommender-systems/` | 37 |
| `ml-foundations/` | 36 |
| `ml-systems/` | 30 |
| `graphs/` | 29 |
| `reinforcement-learning/` | 25 |
| `generative-models/` | 23 |
| `data-centric-ml/` | 21 |
| `trustworthy-ml/` | 17 |
| `computer-systems/` | 13 |
| `research-practice/` | 12 |
| `experimentation-and-metrics/` | 10 |
| `robotics-and-embodied/` | 6 |
| `ai-and-society/` | 5 |
| `curiosities/` | 2 |

Anton's saved papers lean towards LLMs and deep learning. The literature pass (phase 6) is where
search, ranking, recsys and experimentation get their depth.

## Corrections made while matching

- Six automatic matches were a different paper with a similar title. They were corrected by hand
  and are marked in `reason`: Adaptive Mixtures of Local Experts (1991), Long Short-Term Memory
  (1997), Practical Secure Aggregation (2017), Stochastic Neighbor Embedding (2002), Hidden
  Technical Debt in ML Systems (2015), The Unreasonable Effectiveness of Data (2009).
- A truncated link in the Obsidian IR course note (`arxiv.org/abs/2007.0080`) is ANCE, `2007.00808`.
- Two links in `Programming/Floating point number representation.md` point at unrelated papers:
  "bfloat16 whitepaper" links to 1905.02175, and "A Review of Quantization Methods" links to
  2303.05973. Worth fixing in the note.

## Review of weak papers (done 2026-09-30)

88 papers were flagged as low quality, outdated, superseded or off-interest. Anton kept three:
"A Categorical Archive of ChatGPT Failures" (`llm/behaviour`), and two fun reads in
`curiosities/`: the speed-dating study and "Real numbers, data science and chaos". He also noted
that "Pen and Paper Exercises in Machine Learning" is a book worth having, not a paper; it belongs
with Books. The rest are skipped, and go to `catalog/skipped.yaml` in phase 3.

## Skipped

- GPT-1, GPT-2 and GPT-3 (-): an Obsidian note covering three papers, not a paper; the papers are separate rows
- Using GPT-2 to Create Synthetic Data to Improve the Prediction Performance of NLP Machine Learning Classification Models (data-centric-ml/augmentation-and-synthetic-data): confirmed by Anton: weak 2021 study, 16 citations
- Self-supervised Semi-supervised Learning for Data Labeling and Quality Evaluation (data-centric-ml/labels-and-annotation): confirmed by Anton: minor 2021 paper, 14 citations
- Alice's Adventures in a Differentiable Wonderland - Volume I, A Tour of the Land (deep-learning): a book (Alice's Adventures in a Differentiable Wonderland), not a paper
- Machine Learning with Neural Networks (deep-learning): lecture notes (Mehlig), not a paper
- Single Cortical Neurons as Deep Artificial Neural Networks (deep-learning): confirmed by Anton: neuroscience; off the main interests
- DataMUX: Data Multiplexing for Neural Networks (deep-learning/architectures): confirmed by Anton: curiosity 2022 multiplexing paper, little uptake
- Efficient shallow learning as an alternative to deep learning (deep-learning/architectures): confirmed by Anton: weak 2022 claim, little uptake
- Hamiltonian Neural Networks (deep-learning/architectures): confirmed by Anton: physics-inspired architecture; off the main interests
- Understanding Convolutional Neural Networks (deep-learning/architectures): confirmed by Anton: student seminar report, 22 citations
- The Effect of Diversity in Meta-Learning (deep-learning/optimizers-and-schedules): confirmed by Anton: minor 2022 meta-learning study, 20 citations
- Adversarial Examples Are Not Bugs, They Are Features (deep-learning/uncertainty-and-robustness): mislinked in the floating-point note (link text: bfloat16 whitepaper)
- Posterior Differential Regularization with f-divergence for Improving Model Robustness (deep-learning/uncertainty-and-robustness): confirmed by Anton: minor robustness regularizer from a course note; little uptake
- A Comprehensive Survey of AI-Generated Content (AIGC): A History of Generative AI from GAN to ChatGPT (generative-models): confirmed by Anton: broad 2023 AIGC survey, outdated
- Generative Human Motion Stylization in Latent Space (generative-models): confirmed by Anton: niche 3D human-motion generation (from a course note); off the main interests
- GeoCode: Interpretable Shape Programs (generative-models): confirmed by Anton: niche 3D shape-program paper, 24 citations
- Go to Zero: Towards Zero-Shot Motion Generation with Million-Scale Data (generative-models): confirmed by Anton: niche 3D human-motion generation (from a course note); off the main interests
- InterMask: 3D Human Interaction Generation via Collaborative Masked Modelling (generative-models): confirmed by Anton: niche 3D human-interaction generation (from a course note); off the main interests
- MoMask: Generative Masked Modeling of 3D Human Motions (generative-models): confirmed by Anton: niche 3D human-motion generation (from a course note); off the main interests
- ReinDiffuse: Crafting Physically Plausible Motions with Reinforced Diffusion Model (generative-models): confirmed by Anton: niche 3D human-motion generation (from a course note); off the main interests
- Can AI Outperform Human Experts in Creating Social Media Creatives? (generative-models/diffusion): confirmed by Anton: weak 2024 study, 1 citation
- ClickDiffusion: Harnessing LLMs for Interactive Precise Image Editing (generative-models/diffusion): confirmed by Anton: minor 2024 image-editing demo, 2 citations
- CLIPascene: Scene Sketching with Different Types and Levels of Abstraction (generative-models/diffusion): confirmed by Anton: niche sketch-generation paper; off the main interests
- CogView2: Faster and Better Text-to-Image Generation via Hierarchical Transformers (generative-models/diffusion): confirmed by Anton: 2022 text-to-image transformer, superseded by diffusion models
- Diffusion Models as Artists: Are we Closing the Gap between Humans and Machines? (generative-models/diffusion): confirmed by Anton: minor 2023 study, 14 citations
- Extreme Generative Image Compression by Learning Text Embedding from Diffusion Models (generative-models/diffusion): confirmed by Anton: niche 2022 image-compression paper; off the main interests
- HIVE: Harnessing Human Feedback for Instructional Visual Editing (generative-models/diffusion): confirmed by Anton: 2023 instructional image editing; superseded
- Neural Image Compression with a Diffusion-Based Decoder (generative-models/diffusion): confirmed by Anton: niche image-compression paper; off the main interests
- Fast Distributed PageRank Computation (graphs): confirmed by Anton: 2012 distributed PageRank algorithm; theory niche outside the main interests
- HINT: Hierarchical Neuron Concept Explainer (interpretability/explainability): confirmed by Anton: minor 2022 neuron-concept explainer, 25 citations
- Approximating How Single Head Attention Learns (interpretability/mechanistic): confirmed by Anton: narrow 2021 theory of single-head attention; little uptake
- CAT-probing: A Metric-based Approach to Interpret How Pre-trained Models for Programming Language Attend Code Structure (interpretability/mechanistic): confirmed by Anton: niche probing metric for code models, little uptake
- Into the Unknown: Self-Learning Large Language Models (llm/agents): confirmed by Anton: weak 2024 self-learning claim, 6 citations
- Scaling Laws for Linear Complexity Language Models (llm/architecture/recurrent-and-state-space): confirmed by Anton: minor 2024 scaling study, 20 citations
- Evaluating Language Model Context Windows: A "Working Memory" Test and Inference-time Correction (llm/context): confirmed by Anton: minor 2024 context-window test, 8 citations
- PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLMs (llm/evaluation/benchmarks): confirmed by Anton: minor 2024 code benchmark, 22 citations
- Who's Thinking? A Push for Human-Centered Evaluation of LLMs using the XAI Playbook (llm/evaluation/methods): confirmed by Anton: minor 2023 position paper, 17 citations
- A Comprehensive Survey on Pretrained Foundation Models: A History from BERT to ChatGPT (llm/foundation-models): confirmed by Anton: 2023 survey BERT-to-ChatGPT, outdated
- ChatGPT is not all you need. A State of the Art Review of large Generative AI models (llm/foundation-models): confirmed by Anton: low-quality 2023 generative-AI review, outdated
- Summary of ChatGPT-Related Research and Perspective Towards the Future of Large Language Models (llm/foundation-models): confirmed by Anton: low-quality 2023 ChatGPT survey, outdated
- O1 Replication Journey - Part 2: Surpassing O1-preview through Simple Distillation, Big Progress or Bitter Lesson? (llm/post-training/rl-for-reasoning): confirmed by Anton: 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models
- O1 Replication Journey - Part 3: Inference-time Scaling for Medical Reasoning (llm/post-training/rl-for-reasoning): confirmed by Anton: 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models
- O1 Replication Journey: A Strategic Progress Report - Part 1 (llm/post-training/rl-for-reasoning): confirmed by Anton: 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models
- o1-Coder: an o1 Replication for Coding (llm/post-training/rl-for-reasoning): confirmed by Anton: 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models
- Boosted Prompt Ensembles for Large Language Models (llm/prompting-and-in-context): confirmed by Anton: minor 2023 prompt-ensembling method; superseded
- Can discrete information extraction prompts generalize across language models? (llm/prompting-and-in-context): confirmed by Anton: narrow 2023 prompt-transfer study, few citations
- Large Language Models Understand and Can be Enhanced by Emotional Stimuli (llm/prompting-and-in-context): confirmed by Anton: headline effect did not replicate (your Prompt engineering note)
- Multi-Meta-RAG: Improving RAG for Multi-Hop Queries using Database Filtering with LLM-Extracted Metadata (llm/retrieval-augmented): confirmed by Anton: minor 2024 RAG tweak
- Winning Solution For Meta KDD Cup' 24 (llm/retrieval-augmented): confirmed by Anton: competition write-up (KDD Cup 2024 RAG)
- Towards Healthy AI: Large Language Models Need Therapists Too (llm/safety-and-privacy): confirmed by Anton: weak 2023 position paper, 34 citations
- Why Does ChatGPT Fall Short in Providing Truthful Answers? (llm/uncertainty-and-hallucination): confirmed by Anton: weak 2023 ChatGPT truthfulness analysis; superseded
- Consequences of the Moosbauer-Poole Algorithms (ml-foundations): confirmed by Anton: matrix-multiplication algorithms; off-topic for the library
- From Statistical Relational to Neuro-Symbolic Artificial Intelligence (ml-foundations): confirmed by Anton: neuro-symbolic survey mentioned in a course note; off the main interests
- Pen and Paper Exercises in Machine Learning (ml-foundations): a book of exercises with solutions, not a paper
- Bias-Variance Analysis of Support Vector Machines for the Development of (ml-foundations/classical-ml): confirmed by Anton: 2004 SVM bias-variance study; outdated
- Efficient High-Order Interaction-Aware Feature Selection Based on Conditional (ml-foundations/classical-ml): confirmed by Anton: niche feature-selection paper
- Estimating Bias and Variance From Data (ml-foundations/classical-ml): confirmed by Anton: unpublished lecture note on bias-variance; covered by later work
- A survey of 25 years of evaluation (nlp/generation-metrics): confirmed by Anton: 2019 survey of NLG evaluation; few citations and superseded by LLM-era evaluation work
- Optimal Subarchitecture Extraction For BERT (nlp/pretrained-language-models): confirmed by Anton: minor 2020 architecture search for BERT, 18 citations
- A Nested Attention Neural Hybrid Model for Grammatical Error Correction (nlp/tasks-and-methods): confirmed by Anton: 2017 grammatical error correction model; niche and superseded
- Addressing Semantic Drift in Generative Question Answering with Auxiliary Extraction (nlp/tasks-and-methods): confirmed by Anton: minor 2021 generative-QA paper, 29 citations
- Explainable natural language processing with matrix product states (nlp/tasks-and-methods): confirmed by Anton: niche 2021 tensor-network NLP, 10 citations
- LLM-Based Robust Product Classification in Commerce and Compliance (nlp/tasks-and-methods): confirmed by Anton: minor 2024 applied paper, 13 citations
- Neural Databases (nlp/tasks-and-methods): confirmed by Anton: 2020 position paper, 9 citations
- Overview of BioASQ 2025: The Thirteenth BioASQ Challenge on Large-Scale Biomedical Semantic Indexing and Question Answering (nlp/tasks-and-methods): confirmed by Anton: annual challenge overview; dataset reference only
- ProBERT: Product Data Classification with Fine-tuning BERT Model (nlp/tasks-and-methods): confirmed by Anton: minor applied paper
- Smart Expert System: Large Language Models as Text Classifiers (nlp/tasks-and-methods): confirmed by Anton: weak 2024 paper
- FashionNet: Personalized Outfit Recommendation with Deep Neural Network (recommender-systems/deep-and-sequential): confirmed by Anton: niche 2018 outfit recommender, 25 citations
- SWAG: Item Recommendations using Convolutions on Weighted Graphs (recommender-systems/industrial-systems): confirmed by Anton: minor 2019 paper, 11 citations
- Optimizing debt collections using constrained reinforcement learning (reinforcement-learning/deep-rl): confirmed by Anton: 2010 applied constrained RL, niche
- Reinforcement Learning: A Comprehensive Overview (reinforcement-learning/deep-rl): confirmed by Anton: 2024 overview with few citations; Murphy's "Reinforcement Learning: An Overview" covers it
- Learning Deep Representations of Data Distributions (representation-learning): an online book (Ma et al.), not a paper
- SimpleTran: Transferring Pre-Trained Sentence Embeddings for Low Resource Text Classification (representation-learning/embeddings): confirmed by Anton: minor 2020 transfer method for sentence embeddings; superseded
- Vector-based similarity measurements for historical figures (representation-learning/embeddings): confirmed by Anton: curiosity paper, 1 citation
- Contrastive Representation Learning for Electroencephalogram Classification (representation-learning/self-supervised): confirmed by Anton: EEG application from a course note; off the main interests
- Internet Explorer: Targeted Representation Learning on the Open Web (representation-learning/self-supervised): confirmed by Anton: minor 2023 web-crawling representation learner, 30 citations
- Reproducing BowNet: Learning Representations by Predicting Bags of Visual Words (representation-learning/self-supervised): confirmed by Anton: reproduction report, 0 citations
- Data-Efficient Control Barrier Function Refinement (research-practice): mislinked in the floating-point note (link text: A Review of Quantization Methods)
- EARL: Speedup Transformer-based Rankers with Pre-computed Representation (search-and-ranking/neural-ranking): confirmed by Anton: minor 2020 reranker speed-up, 9 citations
- On the Effect of Low-Frequency Terms on Neural-IR Models (search-and-ranking/neural-ranking): confirmed by Anton: minor 2019 analysis, 41 citations
- Passage Ranking with Weak Supervsion (search-and-ranking/neural-ranking): confirmed by Anton: 2019 workshop note, 19 citations
- Fast and Memory Efficient Differentially Private-SGD via JL Projections (trustworthy-ml/privacy-and-federated): confirmed by Anton: minor 2021 DP-SGD speed-up
- Federated Residual Learning (trustworthy-ml/privacy-and-federated): confirmed by Anton: minor 2020 federated-learning variant, 39 citations
- A Dataset and Taxonomy for Urban Sound Research (vision-and-multimodal/speech-and-audio): confirmed by Anton: 2014 urban-sound dataset paper; off the main interests
- Semantic reconstruction of continuous language from non-invasive brain recordings (vision-and-multimodal/speech-and-audio): confirmed by Anton: brain decoding; off the main interests
- Finding the Right Moment: Human-Assisted Trailer Creation via Task Composition (vision-and-multimodal/vision): confirmed by Anton: niche trailer-creation system paper
- Recent Advances in Vision Transformer: A Survey and Outlook of Recent Work (vision-and-multimodal/vision): confirmed by Anton: 2022 ViT survey, superseded by the other vision-transformer surveys
- Single Image Super-Resolution Based on Capsule Neural Networks (vision-and-multimodal/vision): confirmed by Anton: weak paper, 0 citations
- CoBIT: A Contrastive Bi-directional Image-Text Generation Model (vision-and-multimodal/vision-language): confirmed by Anton: minor 2023 image-text model, 15 citations; superseded
- Towards Models that Can See and Read (vision-and-multimodal/vision-language): confirmed by Anton: minor 2023 model, 17 citations
- Virgo: A Preliminary Exploration on Reproducing o1-like MLLM (vision-and-multimodal/vision-language): confirmed by Anton: 2025 o1-replication report for MLLMs; superseded
