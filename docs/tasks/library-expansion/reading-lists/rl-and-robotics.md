# Reading list: rl-and-robotics

The library has the DQN, PPO and DreamerV3/Dreamer 4 anchors, the LinUCB news-bandit paper, OpenVLA, pi0 and PaLM-E, and a small methodology shelf (Deep RL that Matters, ALE). Off-policy evaluation and logged bandit feedback already sit in experimentation-and-metrics/causal-inference, so bandits here focus on exploration. This list fills in the classic actor-critic and offline RL line, recent RL scaling work (2024), the Dreamer predecessors plus world foundation models, evaluation standards for RL, and the robot-foundation-model chain RT-1 to pi*0.6.

## Proposed

Duplicates removed (2026-10-01), each kept on the list that files it best: 38 V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning (on deep-and-representation-learning).

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Trust Region Policy Optimization | 2015 | 1502.05477 | reinforcement-learning/deep-rl | The policy-gradient step-size theory PPO simplifies; needed to read PPO properly. |
| 2 | High-Dimensional Continuous Control Using Generalized Advantage Estimation | 2015 | 1506.02438 | reinforcement-learning/deep-rl | GAE, the advantage estimator inside PPO and most RLHF/LLM RL code. |
| 3 | Asynchronous Methods for Deep Reinforcement Learning | 2016 | 1602.01783 | reinforcement-learning/deep-rl | A3C: the actor-critic baseline that started parallel on-policy RL. |
| 4 | Continuous control with deep reinforcement learning | 2015 | 1509.02971 | reinforcement-learning/deep-rl | DDPG: first deep actor-critic for continuous actions. |
| 5 | Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor | 2018 | 1801.01290 | reinforcement-learning/deep-rl | SAC: the default off-policy continuous-control algorithm. |
| 6 | Addressing Function Approximation Error in Actor-Critic Methods | 2018 | 1802.09477 | reinforcement-learning/deep-rl | TD3: clipped double Q fix for overestimation, widely used baseline. |
| 7 | Rainbow: Combining Improvements in Deep Reinforcement Learning | 2017 | 1710.02298 | reinforcement-learning/deep-rl | Combines six DQN extensions; the reference value-based Atari agent (DQN is already here). |
| 8 | Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm | 2017 | 1712.01815 | reinforcement-learning/deep-rl | AlphaZero: self-play plus search, the template for MuZero and search-based RL. |
| 9 | Conservative Q-Learning for Offline Reinforcement Learning | 2020 | 2006.04779 | reinforcement-learning/deep-rl | CQL: the standard pessimism approach to offline RL, relevant to learning from logged data. |
| 10 | Offline Reinforcement Learning with Implicit Q-Learning | 2021 | 2110.06169 | reinforcement-learning/deep-rl | IQL: simple, stable offline RL baseline avoiding out-of-distribution actions. |
| 11 | Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems | 2020 | 2005.01643 | reinforcement-learning/deep-rl | The reference tutorial on offline RL. |
| 12 | Decision Transformer: Reinforcement Learning via Sequence Modeling | 2021 | 2106.01345 | reinforcement-learning/deep-rl | Casts RL as return-conditioned sequence modelling; bridge to LLM-style agents. |
| 13 | Stop Regressing: Training Value Functions via Classification for Scalable Deep RL | 2024 | 2403.03950 | reinforcement-learning/deep-rl | Replaces MSE value regression with cross-entropy; scales value-based RL with network size. |
| 14 | Bigger, Regularized, Optimistic: scaling for compute and sample-efficient continuous control | 2024 | 2405.16158 | reinforcement-learning/deep-rl | BRO: shows regularised large critics scale model-free RL; NeurIPS 2024 spotlight. |
| 15 | SimBa: Simplicity Bias for Scaling Up Parameters in Deep Reinforcement Learning | 2024 | 2410.09754 | reinforcement-learning/deep-rl | Architecture that lets RL parameters scale; recent scaling-in-RL reference. |
| 16 | Simplifying Deep Temporal Difference Learning | 2024 | 2407.04811 | reinforcement-learning/deep-rl | PQN: normalised parallel Q-learning without target networks or replay; shows how little DQN-style RL needs. |
| 17 | A Tutorial on Thompson Sampling | 2017 | 1707.02038 | reinforcement-learning/bandits | The standard practitioner introduction to Thompson sampling. |
| 18 | Introduction to Multi-Armed Bandits | 2019 | 1904.07272 | reinforcement-learning/bandits | Slivkins' compact survey covering stochastic, contextual and Bayesian bandits. |
| 19 | Unbiased Offline Evaluation of Contextual-bandit-based News Article Recommendation Algorithms | 2010 | 1003.5956 | reinforcement-learning/bandits | Replay method for offline bandit evaluation; companion to LinUCB paper already here. |
| 20 | Taming the Monster: A Fast and Simple Algorithm for Contextual Bandits | 2014 | 1402.0555 | reinforcement-learning/bandits | Practical optimal contextual bandit algorithm behind Vowpal Wabbit and Azure Personalizer. |
| 21 | Mostly Exploration-Free Algorithms for Contextual Bandits | 2017 | 1704.09011 | reinforcement-learning/bandits | Shows greedy works when contexts are diverse; matters for recommender exploration cost. |
| 22 | Neural Contextual Bandits with UCB-based Exploration | 2019 | 1911.04462 | reinforcement-learning/bandits | NeuralUCB: deep reward models with UCB exploration. |
| 23 | Deep Bayesian Bandits Showdown: An Empirical Comparison of Bayesian Deep Networks for Thompson Sampling | 2018 | 1802.09127 | reinforcement-learning/bandits | Empirical comparison of uncertainty methods for deep Thompson sampling; shows what works in practice. |
| 24 | Large-scale Validation of Counterfactual Learning Methods: A Test-Bed | 2016 | 1612.00367 | reinforcement-learning/bandits | Criteo dataset and benchmark for learning from logged bandit feedback in display advertising. |
| 25 | Cascading Bandits: Learning to Rank in the Cascade Model | 2015 | 1502.02763 | reinforcement-learning/bandits | Bandits for ranking lists with position-based click behaviour. |
| 26 | Can large language models explore in-context? | 2024 | 2403.15371 | reinforcement-learning/bandits | Finds LLMs fail at exploration in bandit tasks without intervention; links bandits to LLM agents. |
| 27 | Learning Latent Dynamics for Planning from Pixels | 2018 | 1811.04551 | reinforcement-learning/world-models | PlaNet: latent dynamics model with planning; origin of the Dreamer line. |
| 28 | Dream to Control: Learning Behaviors by Latent Imagination | 2019 | 1912.01603 | reinforcement-learning/world-models | Dreamer: policy learned inside the latent world model (V2, V3, 4 already here). |
| 29 | Mastering Atari with Discrete World Models | 2020 | 2010.02193 | reinforcement-learning/world-models | DreamerV2: discrete latents, human-level Atari; bridges V1 and V3 in the library. |
| 30 | Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model | 2019 | 1911.08265 | reinforcement-learning/world-models | MuZero: planning with a learned value-equivalent model. |
| 31 | When to Trust Your Model: Model-Based Policy Optimization | 2019 | 1906.08253 | reinforcement-learning/world-models | MBPO: short model rollouts with theory; standard model-based baseline. |
| 32 | Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models | 2018 | 1805.12114 | reinforcement-learning/world-models | PETS: ensembles of probabilistic dynamics models, reference for uncertainty in model-based RL. |
| 33 | TD-MPC2: Scalable, Robust World Models for Continuous Control | 2023 | 2310.16828 | reinforcement-learning/world-models | Single-hyperparameter-set latent MPC agent across 100+ tasks. |
| 34 | Transformers are Sample-Efficient World Models | 2022 | 2209.00588 | reinforcement-learning/world-models | IRIS: discrete-token transformer world model; basis for later token world models. |
| 35 | Genie: Generative Interactive Environments | 2024 | 2402.15391 | reinforcement-learning/world-models | Action-controllable world model learned from unlabelled video. |
| 36 | Diffusion for World Modeling: Visual Details Matter in Atari | 2024 | 2405.12399 | reinforcement-learning/world-models | DIAMOND: diffusion world model for training agents. |
| 37 | Cosmos World Foundation Model Platform for Physical AI | 2025 | 2501.03575 | reinforcement-learning/world-models | NVIDIA open world foundation models for robotics and driving. |
| 39 | A Comprehensive Survey on World Models for Embodied AI | 2025 | 2510.16732 | reinforcement-learning/world-models | Recent survey mapping world-model work for embodied agents. |
| 40 | Deep Reinforcement Learning at the Edge of the Statistical Precipice | 2021 | 2108.13264 | reinforcement-learning/methodology | Interquartile mean, performance profiles and confidence intervals; the reporting standard. |
| 41 | Revisiting the Arcade Learning Environment: Evaluation Protocols and Open Problems for General Agents | 2017 | 1709.06009 | reinforcement-learning/methodology | Sticky actions and protocol recommendations for Atari (ALE is already here). |
| 42 | OpenAI Gym | 2016 | 1606.01540 | reinforcement-learning/methodology | The environment interface that standardised RL experiments. |
| 43 | Gymnasium: A Standard Interface for Reinforcement Learning Environments | 2024 | 2407.17032 | reinforcement-learning/methodology | Maintained successor to Gym, the current API. |
| 44 | DeepMind Control Suite | 2018 | 1801.00690 | reinforcement-learning/methodology | Standard continuous-control benchmark. |
| 45 | Leveraging Procedural Generation to Benchmark Reinforcement Learning | 2019 | 1912.01588 | reinforcement-learning/methodology | Procgen: benchmark for generalisation and sample efficiency. |
| 46 | Implementation Matters in Deep Policy Gradients: A Case Study on PPO and TRPO | 2020 | 2005.12729 | reinforcement-learning/methodology | Shows code-level tricks, not the algorithm, drive PPO gains. |
| 47 | What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study | 2020 | 2006.05990 | reinforcement-learning/methodology | Large ablation giving evidence-based PPO implementation choices. |
| 48 | Deep Reinforcement Learning and the Deadly Triad | 2018 | 1812.02648 | reinforcement-learning/methodology | Empirical study of when bootstrapping, off-policy and function approximation diverge. |
| 49 | A Survey of Zero-shot Generalisation in Deep Reinforcement Learning | 2021 | 2111.09794 | reinforcement-learning/methodology | Maps generalisation benchmarks and methods. |
| 50 | RT-1: Robotics Transformer for Real-World Control at Scale | 2022 | 2212.06817 | robotics-and-embodied | First large transformer policy trained on real multi-task robot data. |
| 51 | RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control | 2023 | 2307.15818 | robotics-and-embodied | Defines the VLA recipe; co-trains on web and robot data. |
| 52 | Do As I Can, Not As I Say: Grounding Language in Robotic Affordances | 2022 | 2204.01691 | robotics-and-embodied | SayCan: LLM planning grounded by value functions; template for LLM-robot planning. |
| 53 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models | 2023 | 2310.08864 | robotics-and-embodied | Pooled cross-robot dataset behind most open VLA training. |
| 54 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | 2023 | 2303.04137 | robotics-and-embodied | Diffusion for action generation; dominant imitation-learning policy class. |
| 55 | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware | 2023 | 2304.13705 | robotics-and-embodied | ALOHA and ACT: low-cost teleoperation and action chunking. |
| 56 | Octo: An Open-Source Generalist Robot Policy | 2024 | 2405.12213 | robotics-and-embodied | Open generalist policy trained on Open X-Embodiment. |
| 57 | DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset | 2024 | 2403.12945 | robotics-and-embodied | Large diverse real-robot dataset widely used for fine-tuning. |
| 58 | FAST: Efficient Action Tokenization for Vision-Language-Action Models | 2025 | 2501.09747 | robotics-and-embodied | Compression-based action tokens that make autoregressive VLAs train well. |
| 59 | Gemini Robotics: Bringing AI into the Physical World | 2025 | 2503.20020 | robotics-and-embodied | Google's VLA built on Gemini; reference industrial system. |
| 60 | GR00T N1: An Open Foundation Model for Generalist Humanoid Robots | 2025 | 2503.14734 | robotics-and-embodied | Open dual-system humanoid foundation model. |
| 61 | $\pi_{0.5}$: a Vision-Language-Action Model with Open-World Generalization | 2025 | 2504.16054 | robotics-and-embodied | Co-trained VLA that performs household tasks in unseen homes (pi0 already here). |
| 62 | $\pi^{*}_{0.6}$: a VLA That Learns From Experience | 2025 | 2511.14759 | robotics-and-embodied | Offline RL from deployment experience for a VLA; link between RL and robotics. |
| 63 | A Survey on Vision-Language-Action Models for Embodied AI | 2024 | 2405.14093 | robotics-and-embodied | Most cited VLA survey. |
| 64 | Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World | 2017 | 1703.06907 | robotics-and-embodied | Foundational sim-to-real technique. |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| Deep Q-learning variants (Double DQN, Dueling, PER) | 2015 | 1509.06461 / 1511.06581 / 1511.05952 | reinforcement-learning/deep-rl | Covered by Rainbow. |
| Agent57 | 2020 | 2003.13350 | reinforcement-learning/deep-rl | Atari-specific engineering; narrow uptake. |
| Bigger, Better, Faster (BBF) | 2023 | 2305.19452 | reinforcement-learning/deep-rl | Atari-100k specific; BRO/SimBa cover scaling. |
| IMPALA | 2018 | 1802.01561 | reinforcement-learning/deep-rl | Distributed-systems focus; less relevant for Anton. |
| The Primacy Bias in Deep RL | 2022 | 2205.07802 | reinforcement-learning/deep-rl | Narrow; Policy Churn paper already covers the plasticity theme. |
| CrossQ | 2019 | 1902.05605 | reinforcement-learning/deep-rl | Superseded by BRO/SimBa. |
| Neural Thompson Sampling | 2020 | 2010.00827 | reinforcement-learning/bandits | Incremental over NeuralUCB. |
| EVOLvE: Evaluating and Optimizing LLMs For In-Context Exploration | 2024 | 2410.06238 | reinforcement-learning/bandits | Follow-up to the in-context exploration paper; narrower. |
| Epistemic Neural Networks | 2021 | 2107.08924 | reinforcement-learning/bandits | Uncertainty method, more general ML than bandits. |
| Learning to Optimize via Information-Directed Sampling | 2014 | 1403.5556 | reinforcement-learning/bandits | Theory-heavy, little practical uptake. |
| Supervised Pretraining Can Learn In-Context Reinforcement Learning | 2023 | 2306.14892 | reinforcement-learning/bandits | Research direction, not yet standard. |
| Dreamer-successors and GAIA-1 / UniSim | 2023 | 2309.17080 / 2310.06114 | reinforcement-learning/world-models | Covered by Genie/Cosmos; domain-specific. |
| Model-Based RL for Atari (SimPLe) | 2019 | 1903.00374 | reinforcement-learning/world-models | Superseded by Dreamer/IRIS. |
| Benchmarking Deep RL for Continuous Control | 2016 | 1604.06778 | reinforcement-learning/methodology | Superseded by DM Control and later studies. |
| A Closer Look at Deep Policy Gradients | 2018 | 1811.02553 | reinforcement-learning/methodology | Overlaps Implementation Matters. |
| Measuring and Characterizing Generalization in Deep RL | 2018 | 1812.02868 | reinforcement-learning/methodology | Covered by generalisation survey. |
| Behaviour Suite for RL | 2019 | 1908.03568 | reinforcement-learning/methodology | Little uptake. |
| Brax | 2021 | 2106.13281 | reinforcement-learning/methodology | Simulation tooling; low priority. |
| Isaac Gym / Isaac Lab | 2021 | 2108.10470 / 2511.04831 | robotics-and-embodied | Simulation tooling; low priority for Anton. |
| SmolVLA | 2025 | 2506.01844 | robotics-and-embodied | Small VLA; OpenVLA/pi0 cover the recipe. |
| Mobile ALOHA | 2024 | 2401.02117 | robotics-and-embodied | Incremental over ALOHA/ACT. |
| OpenVLA-OFT / SimpleVLA-RL | 2025 | 2502.19645 / 2509.09674 | robotics-and-embodied | Fast-moving fine-tuning recipes; pi*0.6 is the stronger RL-for-VLA reference. |
| Other VLA surveys (2507.10672 etc.) | 2025 | 2507.10672 | robotics-and-embodied | One survey is enough. |
| Code as Policies / VoxPoser / Eureka / Gato / RDT-1B / LIBERO | 2023 | 2209.07753 etc. | robotics-and-embodied | Useful but secondary; SayCan and RT-2 cover the LLM-robot line. |
| Off-policy evaluation and counterfactual risk minimisation papers | 2016 | various | reinforcement-learning/bandits | Already in experimentation-and-metrics/causal-inference or skipped there. |
| RLHF / RL for LLM reasoning | 2025 | - | - | Belongs in llm/post-training. |
