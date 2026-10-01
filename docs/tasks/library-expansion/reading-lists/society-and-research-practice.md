# Reading list: society and research practice

The library's ai-and-society folder has five papers: the GPTs are GPTs labour-exposure estimate, Guidelines for Human-AI Interaction, Machine Love, We Won't Be Missed and one acceptance-of-imperfect-AI user study. research-practice has thirteen: general advice (How to read a paper, writing a manuscript, Machine Learning that Matters, ML pitfalls, Questionable practices in ML), Why Most Published Findings Are False and IR-specific critiques. This list adds the measured evidence on AI's economic effect (productivity experiments, usage logs from ChatGPT and Claude, employment data, one review), plus persuasion, human-AI team and energy papers; and, for research practice, the statistical and reporting standards (variance, leakage, REFORMS, aggregate reporting), peer-review reliability and the new question of LLMs in reviewing and in AI-scientist systems. Curiosities is not covered. Benchmark-validity papers sit in the LLM evaluation list. Note that arXiv ids were checked with arxiv-lookup; four items are NBER or Stanford pages checked to load with the right title.

## Proposed

Duplicates removed (2026-10-01), each kept on the list that files it best: 21 Deep Reinforcement Learning at the Edge of the Statistical Precipice (on rl-and-robotics).

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Generative AI at Work | 2023 | https://www.nber.org/papers/w31161 | ai-and-society | Field study of 5,000 customer-support agents: AI assistance raised productivity about 14%, most for novices; the reference causal estimate of LLM productivity effects. |
| 2 | Shifting Work Patterns with Generative AI | 2025 | 2504.11436 | ai-and-society | Six-month randomised experiment on 6,000 knowledge workers with an integrated assistant; shows where time savings appear (email, documents) and where they do not (meetings). |
| 3 | The Impact of AI on Developer Productivity: Evidence from GitHub Copilot | 2023 | 2302.06590 | ai-and-society | Controlled experiment finding developers with Copilot finish a task 55% faster; the most cited coding-assistant productivity result. |
| 4 | Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity | 2025 | 2507.09089 | ai-and-society | METR randomised trial where experienced developers were 19% slower with AI despite believing they were faster; essential counterweight to self-reported gains. |
| 5 | Which Economic Tasks are Performed with AI? Evidence from Millions of Claude Conversations | 2025 | 2503.04761 | ai-and-society | Anthropic Economic Index: maps real usage onto O*NET tasks and separates automation from augmentation; the template for measuring AI use from conversation logs. |
| 6 | How People Use ChatGPT | 2025 | https://www.nber.org/papers/w34255 | ai-and-society | Privacy-preserving analysis of 1.5M ChatGPT conversations: usage is mostly non-work guidance, information seeking and writing; the largest consumer-usage measurement. |
| 7 | Working with AI: Measuring the Applicability of Generative AI to Occupations | 2025 | 2507.07935 | ai-and-society | Microsoft study of 200k Copilot conversations scoring occupations by AI applicability; usage-based successor to exposure estimates such as GPTs are GPTs (in library). |
| 8 | Canaries in the Coal Mine? Six Facts about the Recent Employment Effects of Artificial Intelligence | 2025 | https://digitaleconomy.stanford.edu/publication/canaries-in-the-coal-mine/ | ai-and-society | Payroll data show a 16% relative employment decline for 22-25 year olds in AI-exposed occupations; the key empirical labour-market paper of 2025. |
| 9 | AI and jobs. A review of theory, estimates, and evidence | 2025 | 2509.15265 | ai-and-society | Survey of the theory and the ex-post evidence on AI and employment from RCTs, field experiments and digital traces; the one review to read for this folder. |
| 10 | When combinations of humans and AI are useful: A systematic review and meta-analysis | 2024 | 2405.06087 | ai-and-society | Meta-analysis of 106 experiments: human-AI teams often do worse than the best of either alone, especially on decision tasks; guides human-in-the-loop design. |
| 11 | The Levers of Political Persuasion with Conversational AI | 2025 | 2507.13919 | ai-and-society | Large experiments (77k participants) on what makes chatbots persuasive: post-training and information density, not personalisation; shows a cost of accuracy. |
| 12 | Gradual Disempowerment: Systemic Existential Risks from Incremental AI Development | 2025 | 2501.16946 | ai-and-society | Argues that incremental automation can erode human influence over economy, culture and states without any single catastrophic event; complements We Won't Be Missed (in library). |
| 13 | Energy and Policy Considerations for Deep Learning in NLP | 2019 | 1906.02243 | ai-and-society | First widely cited estimate of the carbon cost of training NLP models; started the reporting of compute and emissions. |
| 14 | Power Hungry Processing: Watts Driving the Cost of AI Deployment? | 2023 | 2311.16863 | ai-and-society | Measures inference energy across tasks and models; shows generative and multi-purpose models cost far more per query, the reference for deployment-side energy. |
| 15 | Are GANs Created Equal? A Large-Scale Study | 2017 | 1711.10337 | research-practice | Under a fair hyperparameter budget no GAN variant beats the original; the classic case that claimed progress comes from tuning budgets. |
| 16 | Troubling Trends in Machine Learning Scholarship | 2018 | 1807.03341 | research-practice | Names four recurring flaws (explanation vs speculation, missing ablations, mathiness, language misuse); a standard text on how to write and review ML papers. |
| 17 | Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program) | 2020 | 2003.12206 | research-practice | Reports the code-submission policy, checklist and reproducibility challenge at NeurIPS 2019, with what they changed; origin of the standard ML checklist. |
| 18 | Leakage and the Reproducibility Crisis in ML-based Science | 2022 | 2207.07048 | research-practice | Survey of 17 fields finding data leakage in 329 papers; taxonomy of eight leakage types that every practitioner should check against. |
| 19 | REFORMS: Reporting Standards for Machine Learning Based Science | 2023 | 2308.07832 | research-practice | Consensus 32-item checklist for reporting ML-based studies, covering study design to claims; the practical reporting standard. |
| 20 | Accounting for Variance in Machine Learning Benchmarks | 2021 | 2103.03098 | research-practice | Quantifies all sources of benchmark variance (seeds, data splits, hyperparameter tuning) and proposes cheaper estimators; tells how many runs a comparison needs. |
| 22 | The AI Review Lottery: Widespread AI-Assisted Peer Reviews Boost Paper Scores and Acceptance Rates | 2024 | 2405.02150 | research-practice | Finds at least 15.8% of ICLR 2024 reviews LLM-assisted and scoring higher; first evidence of how LLMs change peer review outcomes. |
| 23 | Detecting AI-Generated Content in Academic Peer Reviews | 2026 | 2602.00319 | research-practice | Tracks AI-generated review text at ICLR over time, about 20% in 2025; measures how fast LLM use spread in reviewing. |
| 24 | Can large language models provide useful feedback on research papers? A large-scale empirical analysis | 2023 | 2310.01783 | research-practice | GPT-4 feedback overlaps human reviewers about as much as reviewers overlap each other, and 57% of authors found it helpful; the basis for AI-assisted reviewing. |
| 25 | Inconsistency in Conference Peer Review: Revisiting the 2014 NeurIPS Experiment | 2021 | 2109.09774 | research-practice | Repeats the NeurIPS consistency experiment: reviewers agree on accept/reject barely beyond chance; why single scores and leaderboards of papers are noisy. |
| 26 | Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results, and a Promising Future? | 2025 | 2502.14297 | research-practice | Independent evaluation of the AI Scientist (in library) finding frequent poor experiments and literature review; a model of how to check AI-research claims. |
| 27 | The More You Automate, the Less You See: Hidden Pitfalls of AI Scientist Systems | 2025 | 2509.08713 | research-practice | Identifies failure modes of AI-scientist pipelines (benchmark selection, data leakage, metric misuse, post-hoc bias) that hide in final papers; asks for trace logs. |
| 28 | CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark | 2024 | 2409.11363 | research-practice | Benchmark of 270 tasks where agents must reproduce published results from code; tests AI-assisted reproducibility. |
| 29 | Position: Machine Learning Conferences Should Establish a "Refutations and Critiques" Track | 2025 | 2506.19882 | research-practice | Proposes a venue for papers that correct published claims, arguing that the field lacks a mechanism for error correction. |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| Your Brain on ChatGPT: Accumulation of Cognitive Debt when Using an AI Assistant for Essay Writing Task | 2025 | 2506.08872 | ai-and-society | Small sample (54), EEG inference widely criticised; weak evidence |
| On the Conversational Persuasiveness of Large Language Models: A Randomized Controlled Trial | 2024 | 2403.14380 | ai-and-society | Levers of Political Persuasion supersedes it |
| On the Opportunities and Risks of Foundation Models | 2021 | 2108.07258 | ai-and-society | Broad 200-page report, only partly about society; dated |
| International AI Safety Report | 2025 | 2501.17805 | ai-and-society | Policy report, not a research paper |
| Making AI Less "Thirsty" | 2023 | 2304.03271 | ai-and-society | Overlaps the energy papers; cut for depth |
| Large Language Models, Small Labor Market Effects (Danish adoption study) | 2025 | https://www.nber.org/papers/w33777 | ai-and-society | NBER page now shows a retitled version; unclear it is the same paper, and Canaries covers the labour-market evidence |
| The Effects of Generative AI on High-Skilled Work (Cui et al.) | 2024 | n/a | ai-and-society | No stable open URL found; Copilot and METR papers cover developers |
| Experimental evidence on the productivity effects of generative AI (Noy and Zhang) | 2023 | n/a | ai-and-society | Not on arXiv, publisher page blocked; Generative AI at Work covers it |
| Anthropic Economic Index reports (2025-2026 editions) | 2026 | n/a | ai-and-society | Web reports without arXiv papers; first report proposed |
| Clio: Privacy-Preserving Insights into Real-World AI Use | 2024 | 2412.13678 | llm/text-analytics | Already in library |
| Deep Reinforcement Learning that Matters; Are We Really Making Much Progress? | 2017 | 1709.06560, 1907.06902 | reinforcement-learning/methodology, recommender-systems/evaluation | Already in library |
| The AI Scientist, AI Scientist-v2, Can LLMs Generate Novel Research Ideas, Ideation-Execution Gap | 2024 | 2408.06292, 2504.08066, 2409.04109, 2506.20803 | llm/agents | Already in library |
| Do ImageNet Classifiers Generalize to ImageNet? | 2019 | 1902.10811 | research-practice | Good benchmark-overfitting evidence; cut for depth (better fit in deep-learning) |
| Show Your Work: Improved Reporting of Experimental Results | 2019 | 1909.03004 | research-practice | Useful but covered by Accounting for Variance and the NeurIPS checklist |
| Reproducibility in Machine Learning-based Research: Overview, Barriers and Drivers | 2024 | 2406.14325 | research-practice | Survey overlapping Improving Reproducibility and REFORMS |
| Is Your Paper Being Reviewed by an LLM? Benchmarking AI Text Detection in Peer Review | 2025 | 2502.19614 | research-practice | Overlaps Detecting AI-Generated Content in Academic Peer Reviews |
| Position: The AI Conference Peer Review Crisis Demands Author Feedback and Reviewer Rewards | 2025 | 2505.04966 | research-practice | Opinion; no uptake yet |
| Accelerating scientific discovery with Co-Scientist | 2025 | 2502.18864 | research-practice | Systems paper for biomedical discovery, not research practice |
| The Automated LLM Speedrunning Benchmark | 2025 | 2506.22419 | llm/evaluation/benchmarks | Niche benchmark |
| NeurIPS 2023 LLM Efficiency Fine-tuning Competition | 2025 | 2503.13507 | research-practice | Narrow competition report |
| Statistical significance testing in NLP (Dror et al.); Winner's Curse? (Sculley) | 2018 | n/a | research-practice | Not on arXiv or no stable open URL found |
| Papers on writing and reading (Ten simple rules, Craft of Research); Stochastic Parrots | 2021 | n/a | research-practice / ai-and-society | Books or not on arXiv; skipped |
