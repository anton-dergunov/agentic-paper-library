# Reading list: LLM post-training

The library covers the classic foundations (FLAN, LoRA, QLoRA, InstructGPT, DPO, IPO, KTO, SimPO, RLOO, HH-RLHF, overoptimisation scaling laws), the R1/GRPO/RLVR line (DeepSeek-R1, DeepSeekMath, ProRL, 1-shot RLVR, Does RL Really Incentivize) and a small set of synthetic-data papers (Magpie, UltraFeedback, LIMA, WildChat). The list adds what a practitioner also needs: the canonical open post-training pipelines (Tulu 3, Olmo 3, Llama 2, Qwen3, DeepSeek-V3), reward-model benchmarks and process supervision, empirical DPO vs PPO studies, the GRPO successors and RLVR diagnostics (DAPO, Dr. GRPO, GSPO, ScaleRL, entropy, spurious rewards), on-policy distillation and distillation from stronger models, and the data side (Self-Instruct, Evol-Instruct, UltraChat, LESS, reasoning SFT recipes). Five tech reports go to `llm/foundation-models` because that is where the library keeps Llama 3 and OLMo 2.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Scaling Instruction-Finetuned Language Models | 2022 | 2210.11416 | llm/post-training/fine-tuning | Flan-PaLM/Flan-T5: scaling tasks and model size plus chain-of-thought data in instruction tuning; the canonical recipe behind the library's FLAN paper. |
| 2 | The Flan Collection: Designing Data and Methods for Effective Instruction Tuning | 2023 | 2301.13688 | llm/post-training/fine-tuning | Ablates which data mixtures and tricks (mixed prompt settings, task balancing) make instruction tuning work; the open reference mixture. |
| 3 | DoRA: Weight-Decomposed Low-Rank Adaptation | 2024 | 2402.09353 | llm/post-training/fine-tuning | Splits weights into magnitude and direction to close part of the LoRA vs full fine-tuning gap; the most used LoRA successor. |
| 4 | The Unlocking Spell on Base LLMs: Rethinking Alignment via In-Context Learning | 2023 | 2312.01552 | llm/post-training/fine-tuning | URIAL: alignment tuning mostly changes style tokens, so a few in-context examples nearly match it; the evidence behind the superficial alignment hypothesis. |
| 5 | Orca: Progressive Learning from Complex Explanation Traces of GPT-4 | 2023 | 2306.02707 | llm/post-training/fine-tuning | Distilling explanation traces from a stronger model rather than only answers; the template for distillation from stronger models. |
| 6 | MiniLLM: On-Policy Distillation of Large Language Models | 2023 | 2306.08543 | llm/post-training/fine-tuning | Reverse-KL distillation on the student's own samples; early on-policy distillation for generative LLMs. |
| 7 | On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes | 2023 | 2306.13649 | llm/post-training/fine-tuning | GKD: distils on student-generated sequences with flexible divergences; the basis of on-policy distillation used in recent open reports. |
| 8 | A Survey of On-Policy Distillation for Large Language Models | 2026 | 2604.00626 | llm/post-training/fine-tuning | Maps the now-standard on-policy distillation stage of frontier post-training pipelines. |
| 9 | Small Models Struggle to Learn from Strong Reasoners | 2025 | 2502.12143 | llm/post-training/fine-tuning | Small students do worse when distilled from long-CoT teachers; shows a learnability gap and mixed-distillation fix. |
| 10 | Tulu 3: Pushing Frontiers in Open Language Model Post-Training | 2024 | 2411.15124 | llm/post-training/fine-tuning | Fully open SFT, DPO and RLVR pipeline with data, evals and recipes; the reference open post-training report. |
| 11 | Olmo 3 | 2025 | 2512.13961 | llm/post-training/fine-tuning | Fully open Think and Instruct models with SFT, DPO and RLVR stages documented end to end; successor to OLMo 2. |
| 12 | Nemotron-Cascade 2: Post-Training LLMs with Cascade RL and Multi-Domain On-Policy Distillation | 2026 | 2603.19220 | llm/post-training/fine-tuning | Recent report on sequential domain-wise RL plus on-policy distillation to merge capabilities. |
| 13 | Learning to summarize from human feedback | 2020 | 2009.01325 | llm/post-training/preference-learning | The first large-scale reward-model plus PPO pipeline for LMs; the direct precursor of InstructGPT. |
| 14 | Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback | 2023 | 2307.15217 | llm/post-training/preference-learning | The standard critical survey of RLHF failure modes in feedback, reward models and policy optimisation. |
| 15 | ORPO: Monolithic Preference Optimization without Reference Model | 2024 | 2403.07691 | llm/post-training/preference-learning | Folds preference optimisation into SFT with an odds-ratio term; a widely used single-stage alternative to SFT+DPO. |
| 16 | Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study | 2024 | 2404.10719 | llm/post-training/preference-learning | Controlled comparison finding well-tuned PPO beats DPO, especially out of distribution. |
| 17 | Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback | 2024 | 2406.09279 | llm/post-training/preference-learning | Ablates data, reward model, and policy training choices; the Tulu 2.5 practical guide to preference tuning. |
| 18 | Preference Fine-Tuning of LLMs Should Leverage Suboptimal, On-Policy Data | 2024 | 2404.14367 | llm/post-training/preference-learning | Explains when on-policy sampling and negative gradients help, unifying DPO-style and RL-style methods. |
| 19 | Self-Rewarding Language Models | 2024 | 2401.10020 | llm/post-training/preference-learning | The model judges its own outputs to build preference data for iterative DPO; origin of self-improving alignment loops. |
| 20 | RLHF Workflow: From Reward Modeling to Online RLHF | 2024 | 2405.07863 | llm/post-training/preference-learning | Reproducible recipe for reward modelling and online iterative DPO, used to build strong open reward models. |
| 21 | RewardBench: Evaluating Reward Models for Language Modeling | 2024 | 2403.13787 | llm/post-training/preference-learning | The standard benchmark for reward models; needed to read any reward-modelling result. |
| 22 | RewardBench 2: Advancing Reward Model Evaluation | 2025 | 2506.01937 | llm/post-training/preference-learning | Harder, best-of-N-style reward model benchmark with stronger correlation to downstream performance. |
| 23 | Skywork-Reward-V2: Scaling Preference Data Curation via Human-AI Synergy | 2025 | 2507.01352 | llm/post-training/preference-learning | Top open reward models from curated 26M-pair preference data; shows curation quality over scale. |
| 24 | Generative Verifiers: Reward Modeling as Next-Token Prediction | 2024 | 2408.15240 | llm/post-training/preference-learning | Reward models that judge via generating verdicts and CoT, scaling with test-time compute; bridge to LLM judges. |
| 25 | Let's Verify Step by Step | 2023 | 2305.20050 | llm/post-training/preference-learning | Process supervision (PRM800K) beats outcome supervision for reward models on maths; the foundation of process reward models. |
| 26 | A Comprehensive Survey of Reward Models: Taxonomy, Applications, Challenges, and Future | 2025 | 2504.12328 | llm/post-training/preference-learning | Survey mapping reward model types, training, evaluation and uses in RLHF and reasoning. |
| 27 | DAPO: An Open-Source LLM Reinforcement Learning System at Scale | 2025 | 2503.14476 | llm/post-training/rl-for-reasoning | Open GRPO variant with clip-higher, dynamic sampling and token-level loss; the go-to recipe for long-CoT RL. |
| 28 | Understanding R1-Zero-Like Training: A Critical Perspective | 2025 | 2503.20783 | llm/post-training/rl-for-reasoning | Dr. GRPO: shows GRPO's length and std biases and that base models already show the 'aha'; fixes the objective. |
| 29 | Group Sequence Policy Optimization | 2025 | 2507.18071 | llm/post-training/rl-for-reasoning | Sequence-level importance ratios stabilise RL for MoE models; used in Qwen3 training. |
| 30 | Kimi k1.5: Scaling Reinforcement Learning with LLMs | 2025 | 2501.12599 | llm/post-training/rl-for-reasoning | Second major R1-era recipe: long-context RL, partial rollouts and length penalties without a value model. |
| 31 | SimpleRL-Zoo: Investigating and Taming Zero Reinforcement Learning for Open Base Models in the Wild | 2025 | 2503.18892 | llm/post-training/rl-for-reasoning | Zero-RL across ten open base models, showing how behaviour depends on the base model and data difficulty. |
| 32 | Spurious Rewards: Rethinking Training Signals in RLVR | 2025 | 2506.10947 | llm/post-training/rl-for-reasoning | Random or wrong rewards still improve Qwen-Math, cautioning that RLVR gains may come from base-model priors. |
| 33 | The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models | 2025 | 2505.22617 | llm/post-training/rl-for-reasoning | Explains policy entropy collapse and its link to performance ceilings, motivating Clip-Cov and KL-Cov. |
| 34 | Cognitive Behaviors that Enable Self-Improving Reasoners, or, Four Habits of Highly Effective STaRs | 2025 | 2503.01307 | llm/post-training/rl-for-reasoning | Verification and backtracking in the base model predict whether RL improves it; explains Qwen vs Llama gap. |
| 35 | STaR: Bootstrapping Reasoning With Reasoning | 2022 | 2203.14465 | llm/post-training/rl-for-reasoning | Rationale bootstrapping by filtering on correct answers; the ancestor of rejection-sampling and RLVR on reasoning. |
| 36 | Magistral | 2025 | 2506.10910 | llm/post-training/rl-for-reasoning | Mistral's pure-RL reasoning report with a GRPO variant, documenting what worked and what did not. |
| 37 | The Art of Scaling Reinforcement Learning Compute for LLMs | 2025 | 2510.13786 | llm/post-training/rl-for-reasoning | ScaleRL: large compute study fitting sigmoidal scaling curves and identifying which RL design choices matter. |
| 38 | RL's Razor: Why Online Reinforcement Learning Forgets Less | 2025 | 2509.04259 | llm/post-training/rl-for-reasoning | On-policy RL stays closer in KL to the base model than SFT, which explains less forgetting. |
| 39 | TTRL: Test-Time Reinforcement Learning | 2025 | 2504.16084 | llm/post-training/rl-for-reasoning | RL on unlabelled test questions with majority-vote rewards; shows label-free RLVR. |
| 40 | Does Math Reasoning Improve General LLM Capabilities? Understanding Transferability of LLM Reasoning | 2025 | 2507.00432 | llm/post-training/rl-for-reasoning | Finds RL-trained maths gains transfer while SFT-trained ones often do not; a caution for evaluating recipes. |
| 41 | Reinforcement Learning for LLM Post-Training: A Survey | 2024 | 2407.16216 | llm/post-training/rl-for-reasoning | Survey of RLHF, RLAIF, DPO and policy optimisation; an overview of the preference and RL side. |
| 42 | Llama-Nemotron: Efficient Reasoning Models | 2025 | 2505.00949 | llm/post-training/rl-for-reasoning | Open reasoning models built by distillation from R1, SFT and large-scale RL, with data released. |
| 43 | Self-Instruct: Aligning Language Models with Self-Generated Instructions | 2022 | 2212.10560 | llm/post-training/data | Bootstrapping instruction data from the model itself; the origin of Alpaca-style synthetic SFT data. |
| 44 | WizardLM: Empowering large pre-trained language models to follow complex instructions | 2023 | 2304.12244 | llm/post-training/data | Evol-Instruct: rewriting instructions into harder variants; the main method for evolving SFT data complexity. |
| 45 | Enhancing Chat Language Models by Scaling High-quality Instructional Conversations | 2023 | 2305.14233 | llm/post-training/data | UltraChat: a large synthetic multi-turn dialogue set, widely used in open SFT mixtures. |
| 46 | HelpSteer2: Open-source dataset for training top-performing reward models | 2024 | 2406.08673 | llm/post-training/data | Small, high-quality permissively licensed attribute-rated dataset that trained top reward models. |
| 47 | LESS: Selecting Influential Data for Targeted Instruction Tuning | 2024 | 2402.04333 | llm/post-training/data | Gradient-based selection of 5% of data that beats the full set; the standard targeted data selection method. |
| 48 | Self-Alignment with Instruction Backtranslation | 2023 | 2308.06259 | llm/post-training/data | Generates instructions for web documents and self-curates them; instruction data from unlabelled text. |
| 49 | Nemotron-4 340B Technical Report | 2024 | 2406.11704 | llm/post-training/data | Documents alignment with about 98% synthetic data and reward-model filtering; a real large-scale synthetic pipeline. |
| 50 | LIMO: Less is More for Reasoning | 2025 | 2502.03387 | llm/post-training/data | 817 curated examples elicit strong maths reasoning; the reasoning-era counterpart of LIMA. |
| 51 | s1: Simple test-time scaling | 2025 | 2501.19393 | llm/post-training/data | 1,000 curated reasoning traces plus budget forcing give a strong simple reasoning model. |
| 52 | OpenThoughts: Data Recipes for Reasoning Models | 2025 | 2506.04178 | llm/post-training/data | Systematic ablations of reasoning SFT data sources, filtering and teachers; the open reasoning-data recipe. |
| 53 | Llama 2: Open Foundation and Fine-Tuned Chat Models | 2023 | 2307.09288 | llm/foundation-models | Detailed open RLHF pipeline (reward models, rejection sampling, PPO, Ghost Attention); the first open account of chat post-training. |
| 54 | Qwen3 Technical Report | 2025 | 2505.09388 | llm/foundation-models | Four-stage post-training with thinking/non-thinking fusion and strong-to-weak distillation. |
| 55 | DeepSeek-V3 Technical Report | 2024 | 2412.19437 | llm/foundation-models | Post-training with R1 distillation, GRPO and self-rewarding; the widely used open frontier-scale pipeline. |
| 56 | DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models | 2025 | 2512.02556 | llm/foundation-models | Scaled post-training RL budget and agentic task synthesis; the latest DeepSeek report detailing its pipeline. |

## Added from "Considered" at Anton's request (2026-10-01)

| # | Paper | Year | arXiv / URL | Folder |
|--:|---|--:|---|---|
| 57 | A Comprehensive Survey of Direct Preference Optimization: Datasets, Theories, Variants, and Applications | 2024 | 2410.15595 | llm/post-training/preference-learning |
| 58 | SmolLM2: When Smol Goes Big -- Data-Centric Training of a Small Language Model | 2025 | 2502.02737 | llm/foundation-models |
| 59 | Textbooks Are All You Need | 2023 | 2306.11644 | llm/pretraining |
| 60 | Best Practices and Lessons Learned on Synthetic Data | 2024 | 2404.07503 | llm/pretraining |
| 61 | A Survey on Rubric-Guided Reinforcement Learning for Language Models | 2026 | 2608.27505 | llm/post-training/preference-learning |
| 62 | Large Language Model Post-Training: A Unified View of Off-Policy and On-Policy Learning | 2026 | 2604.07941 | llm/post-training |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| Qwen2.5 Technical Report | 2024 | 2412.15115 | llm/foundation-models | Superseded by Qwen3 for post-training detail |
| GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models | 2025 | 2508.06471 | llm/foundation-models | Model report with thin post-training detail; low priority |
| gpt-oss-120b & gpt-oss-20b Model Card | 2025 | 2508.10925 | llm/foundation-models | Model card, little reproducible recipe |
| Kimi K2: Open Agentic Intelligence | 2025 | 2507.20534 | llm/foundation-models | Agentic focus; belongs with the agents area list |
| Hermes 4 Technical Report | 2025 | 2508.18255 | llm/post-training/data | Niche uptake |
| MiMo: Unlocking the Reasoning Potential of Language Model | 2025 | 2505.07608 | llm/post-training/rl-for-reasoning | Pretraining-heavy, covered by the R1/Tulu/Olmo reports |
| Skywork Open Reasoner 1 Technical Report | 2025 | 2505.22312 | llm/post-training/rl-for-reasoning | Incremental over DAPO |
| VAPO: Efficient and Reliable Reinforcement Learning for Advanced Reasoning Tasks | 2025 | 2504.05118 | llm/post-training/rl-for-reasoning | Value-based variant, less used than DAPO |
| Open-Reasoner-Zero | 2025 | 2503.24290 | llm/post-training/rl-for-reasoning | Overlaps SimpleRL-Zoo and DAPO |
| Phi-4-reasoning Technical Report | 2025 | 2504.21318 | llm/post-training/rl-for-reasoning | Overlaps OpenThoughts and s1 |
| OpenAI o1 System Card | 2024 | 2412.16720 | llm/post-training/rl-for-reasoning | Safety-focused card without a training recipe |
| Reinforcement Pre-Training | 2025 | 2506.08007 | llm/post-training/rl-for-reasoning | Pretraining objective; little uptake |
| Predictable GRPO: A Closed-Form Model of Training Dynamics | 2026 | 2606.30789 | llm/post-training/rl-for-reasoning | Very new, theoretical, no uptake yet |
| Reinforcement Learning Finetunes Small Subnetworks in Large Language Models | 2025 | 2505.11711 | llm/post-training/rl-for-reasoning | Interesting but secondary to RL's Razor |
| Learning to Reason without External Rewards | 2025 | 2505.19590 | llm/post-training/rl-for-reasoning | Intuitor; overlaps TTRL on label-free RL |
| Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning | 2025 | 2506.01939 | llm/post-training/rl-for-reasoning | Covered by the entropy mechanism paper |
| Rethinking RL for LLM Reasoning: It's Sparse Policy Selection, Not Capability Learning | 2026 | 2605.06241 | llm/post-training/rl-for-reasoning | Recent; overlaps the library's Does RL Really Incentivize and Spurious Rewards |
| Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models | 2023 | 2312.06585 | llm/post-training/rl-for-reasoning | ReST-EM; superseded by RLVR at scale |
| RL on Incorrect Synthetic Data Scales the Efficiency of LLM Math Reasoning by Eight-Fold | 2024 | 2406.14532 | llm/post-training/rl-for-reasoning | Narrow maths study |
| Scaling Relationship on Learning Mathematical Reasoning with Large Language Models | 2023 | 2308.01825 | llm/post-training/rl-for-reasoning | Rejection-sampling fine-tuning; superseded |
| Defeating the Training-Inference Mismatch via FP16 | 2025 | 2510.26788 | llm/post-training/rl-for-reasoning | Engineering detail, narrow |
| On the Generalization of SFT: A Reinforcement Learning Perspective with Reward Rectification | 2025 | 2508.05629 | llm/post-training/fine-tuning | Little uptake so far |
| Random Policy Valuation is Enough for LLM Reasoning with Verifiable Rewards | 2025 | 2509.24981 | llm/post-training/rl-for-reasoning | Niche |
| Depth-Breadth Synergy in RLVR | 2025 | 2508.13755 | llm/post-training/rl-for-reasoning | Incremental variant |
| The Debate on RLVR Reasoning Capability Boundary | 2025 | 2510.04028 | llm/post-training/rl-for-reasoning | Covered by the library's Does RL Really Incentivize and ProRL |
| Secrets of RLHF in Large Language Models Part I: PPO | 2023 | 2307.04964 | llm/post-training/preference-learning | Superseded by Unpacking DPO and PPO and RLOO |
| Fine-Tuning Language Models from Human Preferences | 2019 | 1909.08593 | llm/post-training/preference-learning | Superseded by Learning to summarize and InstructGPT |
| AlpacaFarm: A Simulation Framework for Methods that Learn from Human Feedback | 2023 | 2305.14387 | llm/post-training/preference-learning | Simulated-feedback framework; limited current use |
| Zephyr: Direct Distillation of LM Alignment | 2023 | 2310.16944 | llm/post-training/preference-learning | Good but covered by UltraFeedback and Tulu 2.5-style papers |
| Direct Language Model Alignment from Online AI Feedback | 2024 | 2402.04792 | llm/post-training/preference-learning | OAIF; overlaps the on-policy preference paper |
| Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models | 2024 | 2401.01335 | llm/post-training/preference-learning | SPIN; incremental, limited uptake |
| Self-Play Preference Optimization for Language Model Alignment | 2024 | 2405.00675 | llm/post-training/preference-learning | SPPO; incremental |
| Direct Nash Optimization | 2024 | 2404.03715 | llm/post-training/preference-learning | Incremental |
| Nash Learning from Human Feedback | 2023 | 2312.00886 | llm/post-training/preference-learning | Theoretical, little uptake in practice |
| Step-DPO: Step-wise Preference Optimization for Long-chain Reasoning of LLMs | 2024 | 2406.18629 | llm/post-training/preference-learning | Niche |
| Token-level Direct Preference Optimization | 2024 | 2404.11999 | llm/post-training/preference-learning | Incremental DPO variant |
| A Comprehensive Survey of Direct Preference Optimization | 2024 | 2410.15595 | llm/post-training/preference-learning | Survey quota: reward model survey chosen |
| Interpretable Preferences via Multi-Objective Reward Modeling and Mixture-of-Experts | 2024 | 2406.12845 | llm/post-training/preference-learning | ArmoRM; covered by Skywork-Reward-V2 |
| Skywork-Reward: Bag of Tricks for Reward Modeling in LLMs | 2024 | 2410.18451 | llm/post-training/preference-learning | Superseded by Skywork-Reward-V2 |
| Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations | 2023 | 2312.08935 | llm/post-training/preference-learning | Process rewards are less used since outcome RLVR |
| Self-Taught Evaluators | 2024 | 2408.02666 | llm/post-training/preference-learning | Better suited to the LLM evaluation list |
| A Long Way to Go: Investigating Length Correlations in RLHF | 2023 | 2310.03716 | llm/post-training/preference-learning | Covered by SimPO and scaling-law papers in the library |
| OpenRubrics: Towards Scalable Synthetic Rubric Generation for Reward Modeling and LLM Alignment | 2025 | 2510.07743 | llm/post-training/preference-learning | Covered by Rubrics as Rewards in the library |
| A Survey on Rubric-Guided Reinforcement Learning for Language Models | 2026 | 2608.27505 | llm/post-training/preference-learning | Very new, survey quota |
| Large Language Model Post-Training: A Unified View of Off-Policy and On-Policy Learning | 2026 | 2604.07941 | llm/post-training/fine-tuning | Survey quota; OPD survey chosen |
| Revisiting On-Policy Distillation: Empirical Failure Modes and Simple Fixes | 2026 | 2603.25562 | llm/post-training/fine-tuning | Recent, no uptake yet |
| A Survey on Knowledge Distillation of Large Language Models | 2024 | 2402.13116 | llm/post-training/fine-tuning | Older; OPD survey chosen |
| An Empirical Study of Catastrophic Forgetting in LLMs During Continual Fine-tuning | 2023 | 2308.08747 | llm/post-training/fine-tuning | LoRA Learns Less and Forgets Less already covers it |
| Overtrained Language Models Are Harder to Fine-Tune | 2025 | 2503.19206 | llm/post-training/fine-tuning | Niche pretraining/fine-tuning interaction |
| Operationalising the Superficial Alignment Hypothesis via Task Complexity | 2026 | 2602.15829 | llm/post-training/fine-tuning | Little uptake; URIAL and LIMA cover the idea |
| Distilling Step-by-Step! | 2023 | 2305.02301 | llm/post-training/fine-tuning | Older; superseded by reasoning-trace distillation |
| Prefix-Tuning | 2021 | 2101.00190 | llm/post-training/fine-tuning | Superseded by LoRA |
| The Power of Scale for Parameter-Efficient Prompt Tuning | 2021 | 2104.08691 | llm/post-training/fine-tuning | Superseded by LoRA |
| Multitask Prompted Training Enables Zero-Shot Task Generalization (T0) | 2021 | 2110.08207 | llm/post-training/fine-tuning | Covered by FLAN and Flan Collection |
| Super-NaturalInstructions | 2022 | 2204.07705 | llm/post-training/fine-tuning | Covered by Flan Collection |
| Instruction Tuning with GPT-4 | 2023 | 2304.03277 | llm/post-training/data | Incremental over Alpaca/Self-Instruct |
| AlpaGasus: Training A Better Alpaca with Fewer Data | 2023 | 2307.08701 | llm/post-training/data | Superseded by LESS and Deita |
| What Makes Good Data for Alignment? (Deita) | 2023 | 2312.15685 | llm/post-training/data | Overlaps LESS |
| Best Practices and Lessons Learned on Synthetic Data | 2024 | 2404.07503 | llm/post-training/data | Generic position paper |
| OpenAssistant Conversations | 2023 | 2304.07327 | llm/post-training/data | Dataset with limited use in current recipes |
| How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources | 2023 | 2306.04751 | llm/post-training/data | Covered by Tulu 3 |
| Camels in a Changing Climate (Tulu 2) | 2023 | 2311.10702 | llm/post-training/fine-tuning | Superseded by Tulu 3 |
| Textbooks Are All You Need | 2023 | 2306.11644 | llm/post-training/data | Pretraining data; belongs to pretraining |
| SmolLM2 | 2025 | 2502.02737 | llm/foundation-models | Pretraining-focused |
