# Reading list: LLM evaluation

The library's LLM-evaluation folders hold the judge-and-arena core (MT-Bench/Chatbot Arena, Arena-Hard, AlpacaEval-LC, G-Eval, Prometheus 2, FLASK, HELM, LM Evaluation Harness lessons, Adding Error Bars, multi-prompt evaluation, preference leakage, judge position bias and surveys), a few newer judge-reliability and simulated-user papers (Lost in Simulation, Sim2Real, Reliability without Validity) and mostly older dataset papers (Spider, HotpotQA, HellaSwag, MuSiQue). What is missing is the benchmarks that frontier models are reported on in 2025-2026 and the methodology around them. The list adds: the standard knowledge, reasoning, maths, code and instruction benchmarks and their harder successors (MMLU-Pro, GPQA, HLE, FrontierMath, ARC-AGI-2, LiveCodeBench, SWE-bench and its successors); agent and computer-use benchmarks (tau-bench, WebArena, OSWorld, BrowseComp, METR time horizons, GDPval); long-context benchmarks (RULER, HELMET, LongBench v2, NoLiMa); judge diagnostics and bias (JudgeBench, CALM, PoLL, self-preference, null-model attacks, 2026 judge-reliability audits); arena critique and statistics; contamination; statistical rigour and benchmark validity and saturation; and user-simulator realism. Benchmarks for RAG and memory, recommender and search evaluation are left to their own areas. LLMs Get Lost In Multi-Turn Conversation, GSM-Symbolic, IFEval and CheckList are already in the library under other folders.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Measuring Massive Multitask Language Understanding | 2020 | 2009.03300 | llm/evaluation/benchmarks | MMLU: 57-subject knowledge benchmark that defined headline LLM evaluation for years; needed to read any model report. |
| 2 | MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark | 2024 | 2406.01574 | llm/evaluation/benchmarks | Ten-option, reasoning-heavy successor that restores headroom and lowers prompt sensitivity; the usual replacement for saturated MMLU. |
| 3 | GPQA: A Graduate-Level Google-Proof Q&A Benchmark | 2023 | 2311.12022 | llm/evaluation/benchmarks | Expert-written science questions that search cannot answer; the standard hard-knowledge benchmark (Diamond subset) in frontier reports. |
| 4 | Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models | 2022 | 2206.04615 | llm/evaluation/benchmarks | BIG-bench: 200+ community tasks; the origin of broad capability suites and of the emergence debate. |
| 5 | Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them | 2022 | 2210.09261 | llm/evaluation/benchmarks | BBH: the 23 hard BIG-bench tasks used to measure chain-of-thought gains; a common reasoning baseline. |
| 6 | BIG-Bench Extra Hard | 2025 | 2502.19187 | llm/evaluation/benchmarks | Harder replacement for BBH after frontier models saturated it; an example of benchmark refresh. |
| 7 | Humanity's Last Exam | 2025 | 2501.14249 | llm/evaluation/benchmarks | Expert-written closed-ended questions across fields built as the last academic exam; frequently reported frontier-model number. |
| 8 | Measuring short-form factuality in large language models | 2024 | 2411.04368 | llm/evaluation/benchmarks | SimpleQA: short adversarially collected fact questions with single gradable answers; standard hallucination/factuality benchmark. |
| 9 | Evaluating Large Language Models Trained on Code | 2021 | 2107.03374 | llm/evaluation/benchmarks | Codex paper: HumanEval and the pass@k metric, still the base of code evaluation. |
| 10 | LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code | 2024 | 2403.07974 | llm/evaluation/benchmarks | Continuously collected competition problems with time-window contamination control; standard for reasoning-model code evaluation. |
| 11 | SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | 2023 | 2310.06770 | llm/evaluation/benchmarks | Real GitHub issues with test-based grading; the reference coding-agent benchmark (Verified variant widely reported). |
| 12 | SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks? | 2025 | 2509.16941 | llm/evaluation/benchmarks | Harder, contamination-resistant, multi-file successor as SWE-bench Verified saturates. |
| 13 | Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces | 2026 | 2601.11868 | llm/evaluation/benchmarks | Hard command-line tasks with containerised verification; now a standard agentic-coding number in model releases. |
| 14 | Measuring Mathematical Problem Solving With the MATH Dataset | 2021 | 2103.03874 | llm/evaluation/benchmarks | Competition-maths problems with step solutions; the base of maths evaluation, with MATH-500 still in reports. |
| 15 | FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI | 2024 | 2411.04872 | llm/evaluation/benchmarks | Unpublished research-level problems with auto-checkable answers; the maths benchmark where headroom remains. |
| 16 | ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems | 2025 | 2505.11831 | llm/evaluation/benchmarks | Harder abstraction puzzles that stay easy for humans; the main test of fluid-reasoning claims (extends the library's On the Measure of Intelligence). |
| 17 | Generalizing Verifiable Instruction Following | 2025 | 2507.02833 | llm/evaluation/benchmarks | IFBench: out-of-distribution verifiable constraints showing models overfit IFEval; also a RLVR training set. |
| 18 | LiveBench: A Challenging, Contamination-Limited LLM Benchmark | 2024 | 2406.19314 | llm/evaluation/benchmarks | Monthly refreshed questions with objective answers; the practical answer to contamination. |
| 19 | τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains | 2024 | 2406.12045 | llm/evaluation/benchmarks | Simulated user plus tools and policy documents, scored on final database state and pass^k reliability; the reference customer-service agent benchmark. |
| 20 | τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment | 2025 | 2506.07982 | llm/evaluation/benchmarks | Extends τ-bench so the user also acts on the world; tests coordination and is reported in frontier releases. |
| 21 | GAIA: a benchmark for General AI Assistants | 2023 | 2311.12983 | llm/evaluation/benchmarks | Simple-for-humans multi-step tool/browsing questions with exact answers; early general-assistant benchmark. |
| 22 | WebArena: A Realistic Web Environment for Building Autonomous Agents | 2023 | 2307.13854 | llm/evaluation/benchmarks | Self-hosted realistic websites with functional-correctness checks; the standard web-agent environment. |
| 23 | OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments | 2024 | 2404.07972 | llm/evaluation/benchmarks | Execution-based desktop tasks across real operating systems; the standard computer-use benchmark. |
| 24 | BrowseComp: A Simple Yet Challenging Benchmark for Browsing Agents | 2025 | 2504.12516 | llm/evaluation/benchmarks | Hard-to-find, easy-to-verify web questions; the standard deep-research agent benchmark. |
| 25 | TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks | 2024 | 2412.14161 | llm/evaluation/benchmarks | Simulated software company with colleagues, tools and checkpoint grading; shows how far agents are from real workplace tasks. |
| 26 | Measuring AI Ability to Complete Long Software Tasks | 2025 | 2503.14499 | llm/evaluation/benchmarks | METR time horizon: the human-time length of tasks an agent completes at 50% reliability, with a doubling trend; a widely cited way to express agent capability. |
| 27 | MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering | 2024 | 2410.07095 | llm/evaluation/benchmarks | 75 Kaggle competitions scored against human leaderboards; the ML-engineering agent benchmark. |
| 28 | GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks | 2025 | 2510.04374 | llm/evaluation/benchmarks | Expert-authored professional deliverables graded by experts across 44 occupations; evaluation of economic usefulness. |
| 29 | RULER: What's the Real Context Size of Your Long-Context Language Models? | 2024 | 2404.06654 | llm/evaluation/benchmarks | Synthetic long-context tasks beyond needle-in-a-haystack showing effective context is far below claimed. |
| 30 | LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks | 2024 | 2412.15204 | llm/evaluation/benchmarks | Realistic expert-made multi-domain long-context questions up to 2M words where humans score low; widely reported. |
| 31 | HELMET: How to Evaluate Long-Context Language Models Effectively and Thoroughly | 2024 | 2410.02694 | llm/evaluation/benchmarks | Shows synthetic long-context tasks predict real ones poorly and proposes a broader application-centric suite. |
| 32 | NoLiMa: Long-Context Evaluation Beyond Literal Matching | 2025 | 2502.05167 | llm/evaluation/benchmarks | Removes lexical overlap between question and needle, exposing steep long-context degradation. |
| 33 | The Leaderboard Illusion | 2025 | 2504.20879 | llm/evaluation/methods | Audits Chatbot Arena: undisclosed private testing, data access asymmetry and overfitting to the arena; essential critique of arena-style ranking. |
| 34 | A Statistical Framework for Ranking LLM-Based Chatbots | 2024 | 2412.18407 | llm/evaluation/methods | Extends Bradley-Terry/Elo with ties, covariates and proper uncertainty; how arena-style scores should be estimated. |
| 35 | JudgeBench: A Benchmark for Evaluating LLM-based Judges | 2024 | 2410.12784 | llm/evaluation/methods | Tests judges on objectively correct response pairs rather than human preference; shows strong judges barely beat chance on hard cases. |
| 36 | Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge | 2024 | 2410.02736 | llm/evaluation/methods | CALM framework quantifying twelve judge biases (position, verbosity, self-enhancement, authority, etc.); the most systematic bias catalogue. |
| 37 | Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models | 2024 | 2404.18796 | llm/evaluation/methods | PoLL: a panel of smaller diverse judges beats one large judge at lower cost and with less self-preference. |
| 38 | LLM Evaluators Recognize and Favor Their Own Generations | 2024 | 2404.13076 | llm/evaluation/methods | Links self-recognition to self-preference bias; explains why a model should not judge itself. |
| 39 | Self-Taught Evaluators | 2024 | 2408.02666 | llm/evaluation/methods | Trains judges from synthetic contrasting pairs without human labels; the recipe for open judge models (deferred from the post-training list). |
| 40 | Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences | 2024 | 2404.12272 | llm/evaluation/methods | EvalGen: criteria drift and the need for human-aligned grading of LLM graders; the basis of practical eval-tooling workflows. |
| 41 | Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates | 2024 | 2410.07137 | llm/evaluation/methods | A constant irrelevant output wins AlpacaEval and Arena-Hard; shows gameability of judge-based benchmarks. |
| 42 | Agent-as-a-Judge: Evaluate Agents with Agents | 2024 | 2410.10934 | llm/evaluation/methods | Agentic judges inspect intermediate steps and tools to grade agent work; template for judging trajectories. |
| 43 | The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation | 2026 | 2606.13685 | llm/evaluation/methods | Measures run-to-run flip rates of pairwise verdicts; quantifies judge noise that single-run evaluations hide. |
| 44 | When the Judge Changes, So Does the Measurement: Auditing LLM-as-Judge Reliability | 2026 | 2607.08535 | llm/evaluation/methods | Treats judge replacement as a measurement-validity problem; practical for versioning judges in production evals. |
| 45 | Benchmark Data Contamination of Large Language Models: A Survey | 2024 | 2406.04244 | llm/evaluation/methods | Maps contamination causes, detection and mitigation; the orienting survey. |
| 46 | Rethinking Benchmark and Contamination for Language Models with Rephrased Samples | 2023 | 2311.04850 | llm/evaluation/methods | Shows n-gram decontamination misses rephrased leaks; a 13B model trained on them matches GPT-4 on benchmarks. |
| 47 | A Careful Examination of Large Language Model Performance on Grade School Arithmetic | 2024 | 2405.00332 | llm/evaluation/methods | GSM1k: a fresh GSM8K-like set exposing overfitting in several model families; the canonical contamination test. |
| 48 | Quantifying Variance in Evaluation Benchmarks | 2024 | 2406.10229 | llm/evaluation/methods | Measures seed, checkpoint and data variance across benchmarks; tells how big a difference must be to matter. |
| 49 | Position: Don't Use the CLT in LLM Evals With Fewer Than a Few Hundred Datapoints | 2025 | 2503.01747 | llm/evaluation/methods | Normal-approximation confidence intervals fail on small evals; recommends Bayesian and exact alternatives (complements Adding Error Bars). |
| 50 | tinyBenchmarks: evaluating LLMs with fewer examples | 2024 | 2402.14992 | llm/evaluation/methods | IRT-based subset selection reproduces full benchmark scores with about 100 examples; cheap eval with quantified error. |
| 51 | A Sober Look at Progress in Language Model Reasoning: Pitfalls and Paths to Reproducibility | 2025 | 2504.07086 | llm/evaluation/methods | Shows reasoning-benchmark gains are fragile to seeds, decoding and formatting; proposes a standard evaluation framework. |
| 52 | Are Emergent Abilities of Large Language Models a Mirage? | 2023 | 2304.15004 | llm/evaluation/methods | Emergence largely arises from discontinuous metrics; foundation for choosing continuous metrics and reading scaling claims. |
| 53 | BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices | 2024 | 2411.12990 | llm/evaluation/methods | 46-criterion checklist scoring 24 benchmarks on design, implementation and documentation; practical benchmark-design standard. |
| 54 | Line Goes Up? Inherent Limitations of Benchmarks for Evaluating Large Language Models | 2025 | 2502.14318 | llm/evaluation/methods | Argues benchmark scores are weak proxies for capability and discusses distribution shift and saturation. |
| 55 | Measuring what Matters: Construct Validity in Large Language Model Benchmarks | 2025 | 2511.04703 | llm/evaluation/methods | Review of 445 benchmarks for whether they measure what they claim, with recommendations; validity lens for benchmark choice. |
| 56 | When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation | 2026 | 2602.16763 | llm/evaluation/methods | Analyses 60 benchmarks finding saturation driven by age and size, not by private test sets; evidence for benchmark design. |
| 57 | Establishing Best Practices for Building Rigorous Agentic Benchmarks | 2025 | 2507.02825 | llm/evaluation/methods | Agentic Benchmark Checklist after finding flawed task setup and grading in popular agent benchmarks that shift scores by up to 100%. |
| 58 | AI Agents That Matter | 2024 | 2407.01502 | llm/evaluation/methods | Argues agent evaluation must include cost, holdouts and reproducibility; shows complex agents often lose to simple baselines. |
| 59 | Flipping the Dialogue: Training and Evaluating User Language Models | 2025 | 2510.06552 | llm/evaluation/methods | User-specialised LMs are more realistic simulators than assistants prompted as users; relevant for multi-turn evaluation. |
| 60 | MirrorBench: A Benchmark to Evaluate Conversational User-Proxy Agents for Human-Likeness | 2026 | 2601.08118 | llm/evaluation/methods | Reproducible framework to score how human-like simulated users are; complements the library's Lost in Simulation and Sim2Real papers. |

## Added from "Considered" at Anton's request (2026-10-01)

| # | Paper | Year | arXiv / URL | Folder |
|--:|---|--:|---|---|
| 61 | A Survey on Large Language Model Benchmarks | 2025 | 2508.15361 | llm/evaluation/benchmarks |
| 62 | LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods | 2024 | 2412.05579 | llm/evaluation/methods |
| 63 | Questionable practices in machine learning | 2024 | 2407.12220 | research-practice |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| Program Synthesis with Large Language Models (MBPP) | 2021 | 2108.07732 | llm/evaluation/benchmarks | Saturated; HumanEval covers the ground |
| Training Verifiers to Solve Math Word Problems (GSM8K) | 2021 | 2110.14168 | llm/evaluation/benchmarks | Saturated; GSM1k and GSM-Symbolic (in library) carry the lesson |
| TruthfulQA: Measuring How Models Mimic Human Falsehoods | 2021 | 2109.07958 | llm/uncertainty-and-hallucination | Better fits the hallucination folder; saturated as a headline benchmark |
| Are We Done with MMLU? | 2024 | 2406.04127 | llm/evaluation/benchmarks | MMLU-Pro covers successor role |
| MathArena: Evaluating LLMs on Uncontaminated Math Competitions | 2025 | 2505.23281 | llm/evaluation/benchmarks | Good; overlaps LiveBench/LiveCodeBench idea, cut for depth |
| Omni-MATH | 2024 | 2410.07985 | llm/evaluation/benchmarks | Saturating; FrontierMath preferred |
| EvalPlus (Is Your Code Generated by ChatGPT Really Correct?) | 2023 | 2305.01210 | llm/evaluation/benchmarks | HumanEval+ is used but the idea is incremental; a fine later addition |
| BigCodeBench | 2024 | 2406.15877 | llm/evaluation/benchmarks | Less used than LiveCodeBench |
| CRUXEval | 2024 | 2401.03065 | llm/evaluation/benchmarks | Niche code-reasoning benchmark |
| SWE-Lancer | 2025 | 2502.12115 | llm/evaluation/benchmarks | Overlaps GDPval and SWE-bench Pro |
| WildBench | 2024 | 2406.04770 | llm/evaluation/benchmarks | Overlaps Arena-Hard in library |
| MultiChallenge | 2025 | 2501.17399 | llm/evaluation/benchmarks | Cut for depth; overlaps IFBench and LLMs Get Lost in Multi-Turn (in library) |
| MT-Bench-101 | 2024 | 2402.14762 | llm/evaluation/benchmarks | Older; MT-Bench in library |
| AgentBench | 2023 | 2308.03688 | llm/evaluation/benchmarks | Largely superseded by tau-bench, WebArena and OSWorld |
| Mind2Web | 2023 | 2306.06070 | llm/evaluation/benchmarks | Superseded by WebArena and OSWorld |
| ToolLLM | 2023 | 2307.16789 | llm/agents | Training and data paper as much as a benchmark; belongs to the agents list |
| The Tool Decathlon (Toolathlon) | 2025 | 2510.25726 | llm/evaluation/benchmarks | Promising but little uptake yet |
| ARE: Scaling Up Agent Environments and Evaluations (Gaia2) | 2025 | 2509.17158 | llm/evaluation/benchmarks | Little uptake yet |
| RE-Bench | 2024 | 2411.15114 | llm/evaluation/benchmarks | Overlaps METR time horizons and MLE-bench |
| PaperBench | 2025 | 2504.01848 | llm/evaluation/benchmarks | Niche research-replication benchmark |
| Vending-Bench | 2025 | 2502.15840 | llm/evaluation/benchmarks | Narrow; interesting for long-horizon coherence |
| Remote Labor Index | 2025 | 2510.26787 | llm/evaluation/benchmarks | Overlaps GDPval |
| Global MMLU | 2024 | 2412.03304 | llm/evaluation/benchmarks | Multilingual niche; MEGA in library |
| RULER alternatives: BABILong, InfiniteBench, Michelangelo | 2024 | 2406.10149, 2402.13718, 2409.12640 | llm/evaluation/benchmarks | Overlap RULER and HELMET |
| LongBench (v1) | 2023 | 2308.14508 | llm/evaluation/benchmarks | Superseded by LongBench v2 |
| A Survey on Evaluation of Large Language Models | 2023 | 2307.03109 | llm/evaluation/methods | Survey quota; A Survey on LLM-as-a-Judge and HELM in library |
| Evaluating Large Language Models: A Comprehensive Survey | 2023 | 2310.19736 | llm/evaluation/methods | Survey quota |
| A Survey on Large Language Model Benchmarks | 2025 | 2508.15361 | llm/evaluation/methods | Survey quota |
| LLMs-as-Judges: A Comprehensive Survey | 2024 | 2412.05579 | llm/evaluation/methods | A Survey on LLM-as-a-Judge already in library |
| From Generation to Judgment | 2024 | 2411.16594 | llm/evaluation/methods | Another judge survey; duplicates |
| JudgeLM | 2023 | 2310.17631 | llm/evaluation/methods | Superseded by Prometheus 2 (in library) |
| PandaLM | 2023 | 2306.05087 | llm/evaluation/methods | Superseded |
| LLMBar (Evaluating LLMs at Evaluating Instruction Following) | 2023 | 2310.07641 | llm/evaluation/methods | Overlaps JudgeBench |
| Large Language Models are Inconsistent and Biased Evaluators | 2024 | 2405.01724 | llm/evaluation/methods | Overlaps Justice or Prejudice |
| GEMBA: LLMs Are State-of-the-Art Evaluators of Translation Quality | 2023 | 2302.14520 | llm/evaluation/methods | Translation-specific |
| Can Large Language Models Be an Alternative to Human Evaluations? | 2023 | 2305.01937 | llm/evaluation/methods | Early; superseded by MT-Bench/Arena paper |
| Improving LLM-as-a-Judge Inference with the Judgment Distribution | 2025 | 2503.03064 | llm/evaluation/methods | Incremental |
| Limitations of the LLM-as-a-Judge Approach in Expert Knowledge Tasks | 2024 | 2410.20266 | llm/evaluation/methods | Narrow domain study |
| LLM-as-a-Judge & Reward Model: What They Can and Cannot Do | 2024 | 2409.11239 | llm/evaluation/methods | Overlaps Reliability without Validity (in library) |
| Diagnosing the Reliability of LLM-as-a-Judge via Item Response Theory | 2026 | 2602.00521 | llm/evaluation/methods | Recent, no uptake yet; judge-reliability slot taken by Coin Flip and When the Judge Changes |
| Rethinking Rubric Generation for Improving LLM Judge and Reward Modeling (RRD) | 2026 | 2602.05125 | llm/evaluation/methods | Recent, narrow; Checklists paper in library covers rubrics |
| Benchmark Health Index | 2026 | 2602.11674 | llm/evaluation/methods | Overlaps When AI Benchmarks Plateau |
| Elo Uncovered: Robustness and Best Practices in Language Model Evaluation | 2023 | 2311.17295 | llm/evaluation/methods | Covered by Statistical Framework for Ranking and Leaderboard Illusion |
| Search Arena | 2025 | 2506.05334 | llm/evaluation/methods | Search-augmented niche |
| Prompt-to-Leaderboard | 2025 | 2502.14855 | llm/evaluation/methods | Already in library (llm/routing) |
| How to Evaluate Reward Models for RLHF | 2024 | 2410.14872 | llm/post-training/preference-learning | Belongs to post-training; RewardBench proposed there |
| Fluid Language Model Benchmarking | 2025 | 2509.11106 | llm/evaluation/methods | Overlaps tinyBenchmarks |
| Toward an Evaluation Science for Generative AI Systems | 2025 | 2503.05336 | llm/evaluation/methods | Position paper; BetterBench and construct validity cover it |
| Holistic Agent Leaderboard | 2025 | 2510.11977 | llm/evaluation/methods | Infrastructure paper; cut for depth after AI Agents That Matter |
| Dynabench | 2021 | 2104.14337 | llm/evaluation/methods | Dated |
| Benchmarking Benchmark Leakage in LLMs | 2024 | 2404.18824 | llm/evaluation/methods | Overlaps contamination survey |
| Don't Make Your LLM an Evaluation Benchmark Cheater | 2023 | 2311.01964 | llm/evaluation/methods | Overlaps rephrased-samples paper |
| Investigating Data Contamination in Modern Benchmarks | 2023 | 2311.09783 | llm/evaluation/methods | Overlaps contamination survey |
| Questionable practices in machine learning | 2024 | 2407.12220 | llm/evaluation/methods | Broader than LLMs |
| Evaluating LLMs as Generative User Simulators for Conversational Recommendation | 2024 | 2403.09738 | recommender-systems/evaluation | Recommender-specific |
| DeepSWE (Datacurve) | 2026 | n/a (no arXiv paper found) | llm/evaluation/benchmarks | Web report only; unverified |
| SWE-bench Verified, SWE-Rebench, Chatbot-Arena style leaderboards, Berkeley Function Calling Leaderboard | 2024 | n/a | llm/evaluation/benchmarks | Blog posts or leaderboards without an arXiv paper |
| RAG and memory benchmarks; relevance-judgment papers (Don't Use LLMs to Make Relevance Judgments) | 2024 | n/a | other areas | Belong to llm/retrieval-augmented, llm/memory/benchmarks and search-and-ranking/evaluation |
