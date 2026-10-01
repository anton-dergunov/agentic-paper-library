# Reading list: systems

The library's systems folders hold the GPU-training core (ZeRO, Megatron-LM, GPipe, PipeDream, FSDP, DDP, Horovod, GShard, activation recomputation, DeepSeek-V3 hardware reflections), a thin inference folder (FlashAttention 1 and 2, FlexGen, S-LoRA, Efficiently Scaling Transformer Inference, Inference economics), a production-ML folder of Google/Microsoft classics (Hidden Technical Debt, ML Test Score, Rules of ML, SE for ML) plus two interview studies, and thirteen classic systems papers (GFS, Bigtable, Chubby, Spanner, Memcache at Facebook, HyperLogLog, skip lists, power of two choices). The list adds: the pre-LLM training substrate (DistBelief, parameter server, TensorFlow, Ray, mixed precision, sublinear-memory checkpointing), automatic parallelism (GSPMD, Alpa), 2024-2026 production training reports (MegaScale, MegaScale-MoE, TorchTitan, cluster reliability, DiLoCo, Zero Bubble) and recsys training infrastructure (Persia, DLRM training efficiency, data ingestion); the modern LLM serving stack that the inference folder lacks (Orca, PagedAttention, Sarathi-Serve, prefill/decode disaggregation, Mooncake, SGLang, FlashAttention-3, FlashInfer, MoE serving) and recsys serving (DeepRecSys, GPU parameter server, SilverTorch); the production-ML papers on data validation, TFX, deployment challenges, observability, feature stores and the 2024-2025 practitioner studies; and the classic distributed-systems canon that search and recommendation infrastructure rests on (MapReduce, Dynamo, Raft, Spark RDDs, Borg, ZooKeeper, Kafka, TAO, Dremel, Dataflow, LSM-trees, Tail at Scale, Dapper, Lamport clocks, Count-Min). LLM-specific efficiency algorithms (quantization, speculative decoding) are left to llm/efficiency. Most computer-systems papers are not on arXiv; URLs were checked and load with the right title.

## Proposed

Duplicates removed (2026-10-01), each kept on the list that files it best: 37 Underspecification Presents Challenges for Credibility in Modern Machine Learning (on deep-and-representation-learning).

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | Large Scale Distributed Deep Networks | 2012 | https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/40565.pdf | ml-systems/distributed-training | DistBelief: asynchronous SGD with model and data parallelism; origin of large-scale deep-learning systems and of sharded embedding training. |
| 2 | Scaling Distributed Machine Learning with the Parameter Server | 2014 | https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-li_mu.pdf | ml-systems/distributed-training | The parameter-server architecture that still underlies sparse-embedding recommender training. |
| 3 | TensorFlow: A system for large-scale machine learning | 2016 | 1605.08695 | ml-systems/distributed-training | Dataflow-graph design and distributed execution of the framework behind Google's production ranking models and TFX. |
| 4 | Ray: A Distributed Framework for Emerging AI Applications | 2017 | 1712.05889 | ml-systems/distributed-training | Task/actor runtime now used for RL, data processing and LLM post-training and serving; fits no better folder. |
| 5 | Mixed Precision Training | 2017 | 1710.03740 | ml-systems/distributed-training | FP16 training with master weights and loss scaling; the base of every later low-precision training recipe. |
| 6 | Training Deep Nets with Sublinear Memory Cost | 2016 | 1604.06174 | ml-systems/distributed-training | Gradient checkpointing: trade recompute for activation memory; precursor of the library's activation-recomputation paper. |
| 7 | GSPMD: General and Scalable Parallelization for ML Computation Graphs | 2021 | 2105.04663 | ml-systems/distributed-training | Sharding-annotation compiler behind JAX/XLA parallelism and GShard; how TPU-scale training is expressed. |
| 8 | Alpa: Automating Inter- and Intra-Operator Parallelism for Distributed Deep Learning | 2022 | 2201.12023 | ml-systems/distributed-training | Formulates parallelism search as a hierarchical optimisation; the reference for automatic parallelisation. |
| 9 | Zero Bubble Pipeline Parallelism | 2023 | 2401.10241 | ml-systems/distributed-training | Splits backward into input and weight gradients to remove pipeline bubbles; used in current pipeline schedules. |
| 10 | DiLoCo: Distributed Low-Communication Training of Language Models | 2023 | 2311.08105 | ml-systems/distributed-training | Local-step training with outer optimiser that cuts cross-datacenter communication by orders of magnitude; basis of decentralised training work. |
| 11 | MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs | 2024 | 2402.15627 | ml-systems/distributed-training | ByteDance's account of full-stack optimisation and fault diagnosis at 10k-GPU scale. |
| 12 | Revisiting Reliability in Large-Scale Machine Learning Research Clusters | 2024 | 2410.21680 | ml-systems/distributed-training | Meta's failure statistics from 11 months of cluster operation; what actually breaks in large training runs. |
| 13 | TorchTitan: One-stop PyTorch native solution for production ready LLM pre-training | 2024 | 2410.06511 | ml-systems/distributed-training | Composable 4D-parallel reference implementation (FSDP2, TP, PP, CP, float8); a practical map of the modern stack. |
| 14 | MegaScale-MoE: Large-Scale Communication-Efficient Training of Mixture-of-Experts Models in Production | 2025 | 2505.11432 | ml-systems/distributed-training | Production MoE training with communication overlap and compression; 1.88x over Megatron-LM. |
| 15 | Efficient Training of Large Language Models on Distributed Infrastructures: A Survey | 2024 | 2407.20018 | ml-systems/distributed-training | The best recent survey covering parallelism, communication, fault tolerance and cluster scheduling for LLM training. |
| 16 | Persia: An Open, Hybrid System Scaling Deep Learning-based Recommenders up to 100 Trillion Parameters | 2021 | 2111.05897 | ml-systems/distributed-training | Hybrid synchronous dense / asynchronous embedding training for huge recommenders; complements Monolith in the library. |
| 17 | Understanding Training Efficiency of Deep Learning Recommendation Models at Scale | 2020 | 2011.05497 | ml-systems/distributed-training | Meta's characterisation of DLRM training bottlenecks across hardware; shows why recsys training differs from LLM training. |
| 18 | Understanding Data Storage and Ingestion for Large-Scale Deep Recommendation Model Training | 2021 | 2108.09373 | ml-systems/distributed-training | Meta's data pipeline for recommender training, showing preprocessing and storage, not GPUs, are often the bottleneck. |
| 19 | Orca: A Distributed Serving System for Transformer-Based Generative Models | 2022 | https://www.usenix.org/system/files/osdi22-yu.pdf | ml-systems/inference-and-serving | Iteration-level (continuous) batching; the idea every LLM server now uses. |
| 20 | Efficient Memory Management for Large Language Model Serving with PagedAttention | 2023 | 2309.06180 | ml-systems/inference-and-serving | vLLM: paged KV cache that removes fragmentation and raises throughput several-fold; the reference serving paper. |
| 21 | Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve | 2024 | 2403.02310 | ml-systems/inference-and-serving | Chunked prefill with stall-free batching; standard scheduling technique in vLLM and SGLang. |
| 22 | DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving | 2024 | 2401.09670 | ml-systems/inference-and-serving | Separates prefill and decode onto different GPUs to meet TTFT/TPOT SLOs; the disaggregated-serving reference. |
| 23 | Splitwise: Efficient generative LLM inference using phase splitting | 2023 | 2311.18677 | ml-systems/inference-and-serving | Microsoft's phase splitting across hardware types, with cost and power analysis; companion to DistServe. |
| 24 | Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving | 2024 | 2407.00079 | ml-systems/inference-and-serving | Kimi's production architecture with a distributed KV-cache pool and overload-aware scheduling. |
| 25 | SGLang: Efficient Execution of Structured Language Model Programs | 2023 | 2312.07104 | ml-systems/inference-and-serving | RadixAttention prefix reuse plus a programming model for multi-call LLM programs; one of the two main open engines. |
| 26 | FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision | 2024 | 2407.08608 | ml-systems/inference-and-serving | Hopper-specific attention kernel with FP8 and asynchrony; continues the FlashAttention papers in the library. |
| 27 | FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving | 2025 | 2501.01005 | ml-systems/inference-and-serving | Block-sparse KV-cache attention engine used inside vLLM, SGLang and others. |
| 28 | MegaScale-Infer: Serving Mixture-of-Experts at Scale with Disaggregated Expert Parallelism | 2025 | 2504.02263 | ml-systems/inference-and-serving | Disaggregates attention and expert FFNs for MoE decoding; the reference for serving DeepSeek-style models. |
| 29 | Towards Efficient Generative Large Language Model Serving: A Survey from Algorithms to Systems | 2023 | 2312.15234 | ml-systems/inference-and-serving | Survey linking algorithmic and system-level serving optimisations. |
| 30 | Clipper: A Low-Latency Online Prediction Serving System | 2016 | 1612.03079 | ml-systems/inference-and-serving | Classic prediction-serving design with batching, caching and model selection; the pre-LLM baseline for ML serving. |
| 31 | DeepRecSys: A System for Optimizing End-To-End At-scale Neural Recommendation Inference | 2020 | 2001.02772 | ml-systems/inference-and-serving | Meta's tail-latency-aware scheduling of recommendation inference across CPUs and accelerators. |
| 32 | A GPU-specialized Inference Parameter Server for Large-Scale Deep Recommendation Models | 2022 | 2210.08804 | ml-systems/inference-and-serving | HugeCTR hierarchical parameter server with GPU embedding cache; how embeddings are served at scale. |
| 33 | SilverTorch: A Unified Model-based System to Democratize Large-Scale Recommendation on GPUs | 2025 | 2511.14881 | ml-systems/inference-and-serving | Meta folds retrieval indexing and filtering into the model on GPUs; current reference for GPU recsys serving. |
| 34 | Data Validation for Machine Learning | 2019 | https://mlsys.org/Conferences/2019/doc/2019/167.pdf | ml-systems/production-ml | Google's schema-based data validation catching skew and drift in TFX; the standard answer to training-serving skew. |
| 35 | Towards ML Engineering: A Brief History Of TensorFlow Extended (TFX) | 2020 | 2010.02013 | ml-systems/production-ml | How Google's production ML platform evolved and what lessons it drew. |
| 36 | Challenges in Deploying Machine Learning: a Survey of Case Studies | 2020 | 2011.09926 | ml-systems/production-ml | Organises deployment problems by pipeline stage; the usual survey citation. |
| 38 | Towards Observability for Production Machine Learning Pipelines | 2021 | 2108.13557 | ml-systems/production-ml | Argues for ML-specific monitoring of pipelines and data; basis of the mltrace tooling. |
| 39 | Machine Learning Operations (MLOps): Overview, Definition, and Architecture | 2022 | 2205.02302 | ml-systems/production-ml | Defines MLOps components and roles from interviews and literature; the common reference framing. |
| 40 | Overton: A Data System for Monitoring and Improving Machine-Learned Products | 2019 | 1909.05372 | ml-systems/production-ml | Apple's declarative, slice-based approach to monitoring and improving production models. |
| 41 | Managed Geo-Distributed Feature Store: Architecture and System Design | 2023 | 2305.20077 | ml-systems/production-ml | One of few papers describing a production feature store (online/offline consistency, geo-replication). |
| 42 | "We Have No Idea How Models will Behave in Production until Production": How Engineers Operationalize Machine Learning | 2024 | 2403.16795 | ml-systems/production-ml | Interview study of ML engineers' deployment and monitoring practice; updates the library's 2022 interview study. |
| 43 | Understanding Practitioners Perspectives on Monitoring Machine Learning Systems | 2025 | 2509.25195 | ml-systems/production-ml | Survey of 91 practitioners on monitoring practice and gaps. |
| 44 | MapReduce: Simplified Data Processing on Large Clusters | 2004 | https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf | computer-systems | The batch-processing model behind web-scale indexing and feature pipelines; companion to GFS and Bigtable in the library. |
| 45 | Dynamo: Amazon's Highly Available Key-value Store | 2007 | https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf | computer-systems | Consistent hashing, quorums and eventual consistency; the template for highly available stores. |
| 46 | In Search of an Understandable Consensus Algorithm (Raft) | 2014 | https://raft.github.io/raft.pdf | computer-systems | The consensus protocol most modern systems use; complements Chubby and Spanner. |
| 47 | Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing | 2012 | https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf | computer-systems | Spark's lineage-based fault tolerance; the standard substrate of data and feature pipelines. |
| 48 | Large-scale cluster management at Google with Borg | 2015 | https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/ | computer-systems | Cluster scheduler and ancestor of Kubernetes; background for how training and serving jobs are scheduled. |
| 49 | The Tail at Scale | 2013 | https://research.google/pubs/the-tail-at-scale/ | computer-systems | Why fan-out services such as search are dominated by tail latency, and hedging and tied requests as remedies. |
| 50 | Dapper, a Large-Scale Distributed Systems Tracing Infrastructure | 2010 | https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/ | computer-systems | Origin of distributed tracing, needed to debug multi-stage ranking pipelines. |
| 51 | Time, Clocks, and the Ordering of Events in a Distributed System | 1978 | https://lamport.azurewebsites.net/pubs/time-clocks.pdf | computer-systems | Logical clocks and happens-before; the conceptual base for Spanner's time API and replication. |
| 52 | The Log-Structured Merge-Tree (LSM-Tree) | 1996 | https://www.cs.umb.edu/~poneil/lsmtree.pdf | computer-systems | Write-optimised storage structure under Bigtable, RocksDB and most feature and index stores. |
| 53 | ZooKeeper: Wait-free coordination for Internet-scale systems | 2010 | https://www.usenix.org/legacy/event/atc10/tech/full_papers/Hunt.pdf | computer-systems | Open coordination service counterpart to Chubby, used by Kafka, Hadoop and Solr. |
| 54 | Kafka: a Distributed Messaging System for Log Processing | 2011 | https://pages.cs.wisc.edu/~akella/CS744/F17/838-CloudPapers/Kafka.pdf | computer-systems | The log abstraction behind streaming feature, event and feedback pipelines for recommenders. |
| 55 | TAO: Facebook's Distributed Data Store for the Social Graph | 2013 | https://www.usenix.org/system/files/conference/atc13/atc13-bronson.pdf | computer-systems | Read-optimised graph store with caching on top of MySQL; companion to Scaling Memcache and relevant to graph-based recommendation. |
| 56 | Dremel: Interactive Analysis of Web-Scale Datasets | 2010 | https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets-2/ | computer-systems | Columnar nested storage and tree execution behind BigQuery and Parquet; how large logs for training data are queried. |
| 57 | The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing | 2015 | https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf | computer-systems | Event-time windows and watermarks (Beam/Flink); the model for real-time feature and metric streams. |
| 58 | An Improved Data Stream Summary: The Count-Min Sketch and its Applications | 2005 | https://dsf.berkeley.edu/cs286/papers/countmin-latin2004.pdf | computer-systems | Frequency sketch used for heavy hitters and feature counts; sits next to HyperLogLog in the library. |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| Software-Hardware Co-design for Fast and Scalable Training of DLRMs (Neo) | 2021 | 2104.05158 | ml-systems/distributed-training | Skipped earlier |
| Pathways: Asynchronous Distributed Dataflow for ML | 2022 | 2203.12533 | ml-systems/distributed-training | Cut for depth; GSPMD and GShard cover the TPU stack |
| DeepSpeed Ulysses | 2023 | 2309.14509 | ml-systems/distributed-training | Ring Attention already in library; narrow |
| Mesh-TensorFlow | 2018 | 1811.02084 | ml-systems/distributed-training | Superseded by GSPMD |
| Streaming DiLoCo | 2025 | 2501.18512 | ml-systems/distributed-training | Incremental over DiLoCo |
| ZeRO++ | 2023 | 2306.10209 | ml-systems/distributed-training | Incremental over ZeRO (in library) |
| Deep Gradient Compression | 2017 | 1712.01887 | ml-systems/distributed-training | Gradient compression little used in practice |
| Tutel | 2022 | 2206.03382 | ml-systems/distributed-training | MoE kernel library; GShard and MegaScale-MoE cover it |
| Characterization of LLM Development in the Datacenter | 2024 | 2403.07648 | ml-systems/distributed-training | Overlaps Revisiting Reliability |
| TPU v4 / In-Datacenter Performance Analysis of a TPU | 2023 / 2017 | 2304.01433, 1704.04760 | ml-systems/distributed-training | Hardware papers; no folder for accelerator design |
| The Ultra-Scale Playbook (Hugging Face) | 2025 | https://huggingface.co/spaces/nanotron/ultrascale-playbook | ml-systems/distributed-training | Book-length web guide, not a reference write-up of one method |
| Deep Learning Recommendation Model (DLRM), Monolith | 2019 / 2022 | 1906.00091, 2209.07663 | recommender-systems | Already in library |
| Ring Attention | 2023 | 2310.01889 | llm/architecture | Already in library |
| Gandiva: Introspective Cluster Scheduling for Deep Learning | 2018 | https://www.usenix.org/system/files/osdi18-xiao.pdf | ml-systems/distributed-training | Cluster-scheduler niche; Borg and the reliability papers cover the ground |
| AlpaServe | 2023 | 2302.11665 | ml-systems/inference-and-serving | Superseded by later schedulers |
| FastServe | 2023 | 2305.05920 | ml-systems/inference-and-serving | Preemptive scheduling idea with little uptake |
| Llumnix | 2024 | 2406.03243 | ml-systems/inference-and-serving | Incremental; Mooncake and DistServe cover scheduling |
| NanoFlow | 2024 | 2408.12757 | ml-systems/inference-and-serving | Kernel-level niche |
| Preble | 2024 | 2407.00023 | ml-systems/inference-and-serving | Overlaps SGLang prefix reuse |
| vAttention | 2024 | 2405.04437 | ml-systems/inference-and-serving | Alternative to PagedAttention; narrower uptake |
| LMCache | 2025 | 2510.09665 | ml-systems/inference-and-serving | Recent, little uptake in the literature yet; Mooncake covers KV pooling |
| Punica; Fairness in Serving LLMs (VTC) | 2023 | 2310.18547, 2401.00588 | ml-systems/inference-and-serving | S-LoRA in library covers multi-adapter serving; VTC niche |
| FlowKV, Arrow, BanaServe, BucketServe | 2025 | 2504.03775, 2505.11916, 2510.13223, 2507.17120 | ml-systems/inference-and-serving | Incremental disaggregation variants |
| BurstGPT | 2024 | 2401.17644 | ml-systems/inference-and-serving | Workload dataset; narrow |
| DeepSpeed-MoE | 2022 | 2201.05596 | ml-systems/inference-and-serving | MegaScale-Infer is the more current MoE serving paper |
| TensorFlow-Serving | 2017 | 1712.06139 | ml-systems/inference-and-serving | Clipper covers the idea |
| Deep Learning Inference in Facebook Data Centers | 2018 | 1811.09886 | ml-systems/inference-and-serving | Dated characterisation; DeepRecSys preferred |
| Comparative Analysis of LLM Inference Serving Systems (vLLM vs TGI) | 2025 | 2511.17593 | ml-systems/inference-and-serving | Narrow benchmark; engine versions date quickly |
| Monitoring and explainability of models in production | 2020 | 2007.06299 | ml-systems/production-ml | Short overview; observability papers cover it |
| Towards CRISP-ML(Q) | 2020 | 2003.05155 | ml-systems/production-ml | Process model with little uptake |
| Software Engineering Challenges of Deep Learning | 2018 | 1810.12034 | ml-systems/production-ml | SE for ML case study already in library |
| ease.ml/ci | 2019 | 1903.00278 | ml-systems/production-ml | Niche statistical CI |
| ML-Enabled Systems Model Deployment and Monitoring | 2024 | 2402.05333 | ml-systems/production-ml | Overlaps the two practitioner studies proposed |
| Data Cascades in High-Stakes AI; TFX KDD 2017 paper | 2021 / 2017 | n/a | ml-systems/production-ml | No stable open URL found (data-cascades page 404); data-centric folder fits Data Cascades |
| Ad Click Prediction: a View from the Trenches; Practical Lessons from Predicting Clicks on Ads at Facebook | 2013 / 2014 | n/a | search-and-ranking/ads | Already in library |
| Paxos Made Simple | 2001 | https://lamport.azurewebsites.net/pubs/paxos-simple.pdf | computer-systems | Raft and Chubby/Spanner in library cover consensus |
| Consistent hashing, Bloom filters, Cassandra, F1, Aurora, RocksDB, Pregel | various | n/a | computer-systems | Cut for depth; Dynamo, LSM-tree and Dremel cover the lessons; Pregel belongs to graphs |
| Lambda/Kappa architecture, Flink, Delta Lake, Snowflake | various | n/a | computer-systems | Data-engineering rather than classic systems; Dataflow Model carries the idea |
