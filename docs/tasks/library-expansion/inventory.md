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
in Semantic Scholar for year, venue and citation count. 83 papers matched nothing, mostly
pre-arXiv classics and industry papers (Bigtable, BLEU, DBSCAN, t-SNE, the Yahoo LTR challenge,
the Kohavi experimentation papers). They are filed by title and need a PDF from `Papers_old/` or
the publisher when added.

## Columns

`key | title | year | arxiv | url | sources | local_pdf | topic | action | reason | status | venue | citations | matched_from`

- `key`: `arxiv:<id>`, `s2:<Semantic Scholar id>`, or `title:<normalised title>` when nothing matched.
- `sources`: every place the paper is referenced: `papers_old`, `obsidian:<vault path>`, `org:<path>`.
- `local_pdf`: the file stem in `Papers_old/`.
- `topic`: the folder from the proposed tree in [structure.md](structure.md).
- `action`: `add`, `in-library`, `skip` (settled), or `skip?` (waiting for Anton).
- `status`: `todo`, then `added`, `skipped` or `in-library`.
- `citations`: Semantic Scholar's count, a rough signal only, since preprint and proceedings
  records are sometimes split.
- `matched_from`: the original titles, when they differ from the matched one.

## Counts

| Action | Papers |
|---|--:|
| add | 859 |
| skip? (below) | 88 |
| skip | 6 |
| already in the library | 28 |

Of the 859 to add, 701 have an arXiv id, 89 exist only as a local PDF, and 69 need a
PDF from the web.

| Area | To add |
|---|--:|
| `llm/` | 232 |
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

## Skipped (settled)

- Alice's Adventures in a Differentiable Wonderland - Volume I, A Tour of the Land: a book (Alice's Adventures in a Differentiable Wonderland), not a paper
- Machine Learning with Neural Networks: lecture notes (Mehlig), not a paper
- Adversarial Examples Are Not Bugs, They Are Features: mislinked in the floating-point note (link text: bfloat16 whitepaper)
- Learning Deep Representations of Data Distributions: an online book (Ma et al.), not a paper
- Data-Efficient Control Barrier Function Refinement: mislinked in the floating-point note (link text: A Review of Quantization Methods)
- GPT-1, GPT-2 and GPT-3: an Obsidian note covering three papers, not a paper; the papers are separate rows

## Flagged `skip?`: for Anton to confirm

These are low-quality, outdated, superseded or off-interest papers. Confirmed skips go to
`catalog/skipped.yaml`, so they are not proposed again. Anything struck from this list is added.
Answer by number, e.g. "keep S5, S22, S81; skip the rest".

**data-centric-ml**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S1 | Self-supervised Semi-supervised Learning for Data Labeling and Quality Evaluation | 2021 | 14 | minor 2021 paper, 14 citations |
| S2 | Using GPT-2 to Create Synthetic Data to Improve the Prediction Performance of NLP Machine Learning Classification Models | 2021 | 16 | weak 2021 study, 16 citations |

**deep-learning**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S3 | DataMUX: Data Multiplexing for Neural Networks | 2022 | 27 | curiosity 2022 multiplexing paper, little uptake |
| S4 | Efficient shallow learning as an alternative to deep learning | 2022 | 36 | weak 2022 claim, little uptake |
| S5 | Hamiltonian Neural Networks | 2019 | 1360 | physics-inspired architecture; off the main interests |
| S6 | Posterior Differential Regularization with f-divergence for Improving Model Robustness | 2020 | 33 | minor robustness regularizer from a course note; little uptake |
| S7 | Single Cortical Neurons as Deep Artificial Neural Networks | 2020 | 13 | neuroscience; off the main interests |
| S8 | The Effect of Diversity in Meta-Learning | 2022 | 20 | minor 2022 meta-learning study, 20 citations |
| S9 | Understanding Convolutional Neural Networks | 2016 | 22 | student seminar report, 22 citations |

**generative-models**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S10 | A Comprehensive Survey of AI-Generated Content (AIGC): A History of Generative AI from GAN to ChatGPT | 2023 | 859 | broad 2023 AIGC survey, outdated |
| S11 | Can AI Outperform Human Experts in Creating Social Media Creatives? | 2024 | 1 | weak 2024 study, 1 citation |
| S12 | ClickDiffusion: Harnessing LLMs for Interactive Precise Image Editing | 2024 | 2 | minor 2024 image-editing demo, 2 citations |
| S13 | CLIPascene: Scene Sketching with Different Types and Levels of Abstraction | 2022 | 104 | niche sketch-generation paper; off the main interests |
| S14 | CogView2: Faster and Better Text-to-Image Generation via Hierarchical Transformers | 2022 | 430 | 2022 text-to-image transformer, superseded by diffusion models |
| S15 | Diffusion Models as Artists: Are we Closing the Gap between Humans and Machines? | 2023 | 14 | minor 2023 study, 14 citations |
| S16 | Extreme Generative Image Compression by Learning Text Embedding from Diffusion Models | 2022 | 36 | niche 2022 image-compression paper; off the main interests |
| S17 | Generative Human Motion Stylization in Latent Space | 2024 | 40 | niche 3D human-motion generation (from a course note); off the main interests |
| S18 | GeoCode: Interpretable Shape Programs | 2022 | 24 | niche 3D shape-program paper, 24 citations |
| S19 | Go to Zero: Towards Zero-Shot Motion Generation with Million-Scale Data | 2025 | 86 | niche 3D human-motion generation (from a course note); off the main interests |
| S20 | HIVE: Harnessing Human Feedback for Instructional Visual Editing | 2023 | 199 | 2023 instructional image editing; superseded |
| S21 | InterMask: 3D Human Interaction Generation via Collaborative Masked Modelling | 2024 | 52 | niche 3D human-interaction generation (from a course note); off the main interests |
| S22 | MoMask: Generative Masked Modeling of 3D Human Motions | 2023 | 498 | niche 3D human-motion generation (from a course note); off the main interests |
| S23 | Neural Image Compression with a Diffusion-Based Decoder |  |  | niche image-compression paper; off the main interests |
| S24 | ReinDiffuse: Crafting Physically Plausible Motions with Reinforced Diffusion Model | 2024 | 27 | niche 3D human-motion generation (from a course note); off the main interests |

**graphs**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S25 | Fast Distributed PageRank Computation | 2012 | 158 | 2012 distributed PageRank algorithm; theory niche outside the main interests |

**interpretability**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S26 | Approximating How Single Head Attention Learns | 2021 | 36 | narrow 2021 theory of single-head attention; little uptake |
| S27 | CAT-probing: A Metric-based Approach to Interpret How Pre-trained Models for Programming Language Attend Code Structure | 2022 | 11 | niche probing metric for code models, little uptake |
| S28 | HINT: Hierarchical Neuron Concept Explainer | 2022 | 25 | minor 2022 neuron-concept explainer, 25 citations |

**llm**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S29 | A Categorical Archive of ChatGPT Failures | 2023 | 503 | 2023 anecdotal catalogue of ChatGPT failures; superseded by systematic evaluations |
| S30 | A Comprehensive Survey on Pretrained Foundation Models: A History from BERT to ChatGPT | 2023 | 767 | 2023 survey BERT-to-ChatGPT, outdated |
| S31 | Boosted Prompt Ensembles for Large Language Models | 2023 | 64 | minor 2023 prompt-ensembling method; superseded |
| S32 | Can discrete information extraction prompts generalize across language models? | 2023 | 9 | narrow 2023 prompt-transfer study, few citations |
| S33 | ChatGPT is not all you need. A State of the Art Review of large Generative AI models | 2023 | 362 | low-quality 2023 generative-AI review, outdated |
| S34 | Evaluating Language Model Context Windows: A "Working Memory" Test and Inference-time Correction | 2024 | 8 | minor 2024 context-window test, 8 citations |
| S35 | Into the Unknown: Self-Learning Large Language Models | 2024 | 6 | weak 2024 self-learning claim, 6 citations |
| S36 | Large Language Models Understand and Can be Enhanced by Emotional Stimuli | 2023 | 256 | headline effect did not replicate (your Prompt engineering note) |
| S37 | Multi-Meta-RAG: Improving RAG for Multi-Hop Queries using Database Filtering with LLM-Extracted Metadata | 2024 | 36 | minor 2024 RAG tweak |
| S38 | O1 Replication Journey - Part 2: Surpassing O1-preview through Simple Distillation, Big Progress or Bitter Lesson? | 2024 | 99 | 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models |
| S39 | O1 Replication Journey - Part 3: Inference-time Scaling for Medical Reasoning | 2025 | 40 | 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models |
| S40 | O1 Replication Journey: A Strategic Progress Report - Part 1 | 2024 | 155 | 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models |
| S41 | o1-Coder: an o1 Replication for Coding | 2024 | 85 | 2024 o1-replication report, superseded by DeepSeek-R1 and later open reasoning models |
| S42 | PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLMs | 2024 | 22 | minor 2024 code benchmark, 22 citations |
| S43 | Scaling Laws for Linear Complexity Language Models | 2024 | 20 | minor 2024 scaling study, 20 citations |
| S44 | Summary of ChatGPT-Related Research and Perspective Towards the Future of Large Language Models | 2023 | 775 | low-quality 2023 ChatGPT survey, outdated |
| S45 | Towards Healthy AI: Large Language Models Need Therapists Too | 2023 | 34 | weak 2023 position paper, 34 citations |
| S46 | Who's Thinking? A Push for Human-Centered Evaluation of LLMs using the XAI Playbook | 2023 | 17 | minor 2023 position paper, 17 citations |
| S47 | Why Does ChatGPT Fall Short in Providing Truthful Answers? | 2023 | 84 | weak 2023 ChatGPT truthfulness analysis; superseded |
| S48 | Winning Solution For Meta KDD Cup' 24 | 2024 | 4 | competition write-up (KDD Cup 2024 RAG) |

**ml-foundations**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S49 | Bias-Variance Analysis of Support Vector Machines for the Development of |  |  | 2004 SVM bias-variance study; outdated |
| S50 | Consequences of the Moosbauer-Poole Algorithms | 2025 | 6 | matrix-multiplication algorithms; off-topic for the library |
| S51 | Efficient High-Order Interaction-Aware Feature Selection Based on Conditional |  |  | niche feature-selection paper |
| S52 | Estimating Bias and Variance From Data |  |  | unpublished lecture note on bias-variance; covered by later work |
| S53 | From Statistical Relational to Neuro-Symbolic Artificial Intelligence | 2020 | 152 | neuro-symbolic survey mentioned in a course note; off the main interests |
| S54 | Gender Differences in Mate Selection: Evidence From a Speed Dating Experiment | 2006 | 550 | economics study of speed dating; off-topic |
| S55 | Pen and Paper Exercises in Machine Learning | 2022 | 0 | an exercise collection, not a research paper |
| S56 | Real numbers, data science and chaos: How to fit any dataset with a single parameter | 2019 | 2 | curiosity paper (single-parameter fitting) |

**nlp**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S57 | A Nested Attention Neural Hybrid Model for Grammatical Error Correction | 2017 | 116 | 2017 grammatical error correction model; niche and superseded |
| S58 | A survey of 25 years of evaluation | 2019 | 19 | 2019 survey of NLG evaluation; few citations and superseded by LLM-era evaluation work |
| S59 | Addressing Semantic Drift in Generative Question Answering with Auxiliary Extraction | 2021 | 29 | minor 2021 generative-QA paper, 29 citations |
| S60 | Explainable natural language processing with matrix product states | 2021 | 10 | niche 2021 tensor-network NLP, 10 citations |
| S61 | LLM-Based Robust Product Classification in Commerce and Compliance | 2024 | 13 | minor 2024 applied paper, 13 citations |
| S62 | Neural Databases | 2020 | 9 | 2020 position paper, 9 citations |
| S63 | Optimal Subarchitecture Extraction For BERT | 2020 | 18 | minor 2020 architecture search for BERT, 18 citations |
| S64 | Overview of BioASQ 2025: The Thirteenth BioASQ Challenge on Large-Scale Biomedical Semantic Indexing and Question Answering | 2025 | 47 | annual challenge overview; dataset reference only |
| S65 | ProBERT: Product Data Classification with Fine-tuning BERT Model |  |  | minor applied paper |
| S66 | Smart Expert System: Large Language Models as Text Classifiers |  |  | weak 2024 paper |

**recommender-systems**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S67 | FashionNet: Personalized Outfit Recommendation with Deep Neural Network | 2018 | 25 | niche 2018 outfit recommender, 25 citations |
| S68 | SWAG: Item Recommendations using Convolutions on Weighted Graphs | 2019 | 11 | minor 2019 paper, 11 citations |

**reinforcement-learning**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S69 | Optimizing debt collections using constrained reinforcement learning | 2010 | 95 | 2010 applied constrained RL, niche |
| S70 | Reinforcement Learning: A Comprehensive Overview | 2024 | 9 | 2024 overview with few citations; Murphy's "Reinforcement Learning: An Overview" covers it |

**representation-learning**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S71 | Contrastive Representation Learning for Electroencephalogram Classification |  |  | EEG application from a course note; off the main interests |
| S72 | Internet Explorer: Targeted Representation Learning on the Open Web | 2023 | 30 | minor 2023 web-crawling representation learner, 30 citations |
| S73 | Reproducing BowNet: Learning Representations by Predicting Bags of Visual Words | 2022 | 0 | reproduction report, 0 citations |
| S74 | SimpleTran: Transferring Pre-Trained Sentence Embeddings for Low Resource Text Classification | 2020 | 4 | minor 2020 transfer method for sentence embeddings; superseded |
| S75 | Vector-based similarity measurements for historical figures | 2017 | 1 | curiosity paper, 1 citation |

**search-and-ranking**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S76 | EARL: Speedup Transformer-based Rankers with Pre-computed Representation | 2020 | 9 | minor 2020 reranker speed-up, 9 citations |
| S77 | On the Effect of Low-Frequency Terms on Neural-IR Models | 2019 | 41 | minor 2019 analysis, 41 citations |
| S78 | Passage Ranking with Weak Supervsion | 2019 | 19 | 2019 workshop note, 19 citations |

**trustworthy-ml**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S79 | Fast and Memory Efficient Differentially Private-SGD via JL Projections | 2021 | 49 | minor 2021 DP-SGD speed-up |
| S80 | Federated Residual Learning | 2020 | 39 | minor 2020 federated-learning variant, 39 citations |

**vision-and-multimodal**

| # | Paper | Year | Cited | Why flagged |
|--:|---|--:|--:|---|
| S81 | A Dataset and Taxonomy for Urban Sound Research | 2014 | 1610 | 2014 urban-sound dataset paper; off the main interests |
| S82 | CoBIT: A Contrastive Bi-directional Image-Text Generation Model | 2023 | 15 | minor 2023 image-text model, 15 citations; superseded |
| S83 | Finding the Right Moment: Human-Assisted Trailer Creation via Task Composition | 2021 | 20 | niche trailer-creation system paper |
| S84 | Recent Advances in Vision Transformer: A Survey and Outlook of Recent Work | 2022 | 80 | 2022 ViT survey, superseded by the other vision-transformer surveys |
| S85 | Semantic reconstruction of continuous language from non-invasive brain recordings | 2022 | 25 | brain decoding; off the main interests |
| S86 | Single Image Super-Resolution Based on Capsule Neural Networks | 2022 | 0 | weak paper, 0 citations |
| S87 | Towards Models that Can See and Read | 2023 | 17 | minor 2023 model, 17 citations |
| S88 | Virgo: A Preliminary Exploration on Reproducing o1-like MLLM | 2025 | 72 | 2025 o1-replication report for MLLMs; superseded |
