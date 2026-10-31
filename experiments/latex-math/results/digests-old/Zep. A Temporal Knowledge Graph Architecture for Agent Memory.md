# Zep: A Temporal Knowledge Graph Architecture for Agent Memory

type: system
family: temporal knowledge-graph memory for LLM agents (graph-based RAG)
evidence: DMR (500 multi-session conversations from MemGPT's setup) against full-conversation, session-summary and MemGPT-as-reported baselines; LongMemEvals (average ~115k tokens) against full-context baselines only; strength: two benchmarks, vendor-run (all authors are Zep AI), no variance or repeat runs reported, no ablations, MemGPT not run on LongMemEval

## Digest

- Claim: Zep, a memory layer service built on Graphiti, a temporally-aware knowledge graph engine, ingests conversational and business data and keeps a history of facts. It claims to beat MemGPT on DMR (p. 1) and to raise LongMemEval accuracy by up to 18.5% while cutting latency by 90% (p. 1).
- Graph structure (p. 2): three tiers. Episode subgraph: raw messages, text or JSON, kept non-lossy. Semantic entity subgraph: entities plus fact-edges, with hyper-edges for multi-entity facts (p. 3). Community subgraph: entity clusters with map-reduce summaries.
- Bi-temporal model (p. 2–3): timeline T holds event validity (tvalid, tinvalid); timeline T′ holds ingestion time (t′created, t′expired). The paper calls this a novel advance but does not compare it against other systems.
- Invalidation (p. 3): an LLM compares a new edge with related existing edges. On a temporal overlap, the older edge's tinvalid is set to the new edge's tvalid, and new information is prioritized. The paper reports no accuracy measure for this step.
- Entity extraction (p. 3): uses the current message plus the last n = 4 messages, a reflexion-inspired reflection pass, and 1024-dimensional name embeddings. Duplicates are resolved by an LLM over cosine and full-text candidates. Graph writes use fixed Cypher queries, not LLM-generated queries.
- Fact deduplication (p. 3) only searches edges between the same entity pair.
- Communities (p. 4): label propagation replaces Leiden. A new node joins the plurality community of its neighbours, and periodic full refreshes are still needed. The paper says this cuts latency and LLM cost but gives no measurement.
- Retrieval (p. 4–5): f = χ(ρ(ϕ(α))), with cosine, BM25 (Neo4j Lucene) and n-hop breadth-first search. Rerankers are RRF, MMR, episode-mention frequency, node distance and cross-encoder. The paper does not say which reranker or search combination the experiments used, and n for the BFS is not given.
- Models (p. 5): BGE-m3 for embedding and reranking; gpt-4o-mini-2024-07-18 for graph construction; gpt-4o-mini and gpt-4o-2024-11-20 as chat agents; gpt-4-turbo-2024-04-09 for DMR comparability with MemGPT.
- DMR, gpt-4-turbo (p. 6, Table 1): Zep 94.8% vs MemGPT 93.4% (MemGPT figure "reported in [3]", not rerun), full-conversation 94.4%, session summaries 78.6%, recursive summarization 35.3%.
- DMR, gpt-4o-mini (p. 6, Table 1): Zep 98.2% vs full-conversation 98.0% and session summaries 88.0%. The authors could not reproduce MemGPT with this model.
- The text calls the Zep margins over full-conversation "marginal" (p. 6). It also calls DMR inadequate: single-turn fact retrieval, ambiguous wording, and only 60 messages per conversation, which fit in context. The headline DMR result is therefore over a benchmark the authors discount.
- DMR retrieval and judging (p. 5–6): the judge model for DMR is not named. Retrieval is described as 20 edges and entity nodes on p. 5, and as top 10 nodes and edges on p. 6.
- LongMemEvals (p. 6–7): average ~115,000 tokens, six question types. Answers are judged by GPT-4o using prompts from [7], which the authors say correlate highly with humans (p. 7).
- LongMemEval accuracy (p. 7, Table 2): gpt-4o-mini full-context 55.4% vs Zep 63.8%; gpt-4o full-context 60.2% vs Zep 71.2%. Latency is 31.3 s vs 3.20 s and 28.9 s vs 2.58 s, but the table does not name the latency statistic. Average context is 115k tokens vs 1.6k.
- Infrastructure caveat (p. 6–7): Zep was queried over a network from a consumer laptop in Boston to AWS us-west-2. The authors say the baselines had no such network latency. The latency comparison therefore is not like-for-like as disclosed.
- Per-type results (p. 7, Table 3): for gpt-4o-mini, Zep is higher on 4 of 6 types and lower on single-session-assistant (81.8% → 75.0%) and knowledge-update (76.9% → 74.4%). The Delta column does not seem to use one base throughout, so recompute before quoting it.
- Single-session-assistant is lower with Zep for both models. The authors say further work is needed (p. 8).
- Conclusion overreach (p. 8): "state-of-the-art performance on existing memory benchmarks" rests on two benchmarks. MemGPT is compared only as reported on DMR, and has no LongMemEval result because the authors could not get it to answer questions (p. 7).
- Not in the paper: ablations of the bi-temporal fields, invalidation, community search or rerankers; repeat runs or variance; a latency breakdown by stage; accuracy of entity or fact extraction; the effect of the non-lossy episode links, which the authors say are "not directly examined" (p. 3).
- The paper's own inconsistencies: top-k retrieval is 20 edges and entity nodes (p. 5) but top 10 nodes and edges for DMR (p. 6); the gpt-4o gain of 18.5% (p. 7) does not follow from the Table 2 pair 60.2% → 71.2% on the same relative basis that 15.2% follows from 55.4% → 63.8% (p. 7, Table 2); the gpt-4o single-session-user row in Table 3 repeats the gpt-4o-mini row exactly (p. 7, Table 3).

## Related in library

## Q&A

### 2026-10-26: How to read the LongMemEval deltas

- The "15.2%" and "18.5%" gains in the text, and the Delta column of Table 3, are **relative** changes, not percentage points (p. 7). In points: +8.4 (gpt-4o-mini, 55.4→63.8) and +11.0 (gpt-4o, 60.2→71.2) (p. 7, Table 2).
- 71.2/60.2 = 1.183, so the stated 18.5% is slightly off; 63.8/55.4 = 1.152 matches (our arithmetic).
- In Table 3 the single-session-user row is identical for both models (81.4→92.9), which may be a copy error in the paper (p. 7, Table 3).
- Scores are judged by GPT-4o with LongMemEval's prompts; the only baseline is full context (~115k tokens) (p. 7).
