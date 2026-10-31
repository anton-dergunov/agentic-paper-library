# Zep: A Temporal Knowledge Graph Architecture for Agent Memory

type: system
family: knowledge-graph agent memory (graph-based RAG), temporal KG
evidence: DMR (500 multi-session conversations from MemGPT's benchmark) and LongMemEvals (about 115k-token conversations), against full-conversation and session-summary baselines, MemGPT's self-reported DMR numbers, and full-context gpt-4o and gpt-4o-mini; strength: one benchmark pair, vendor-run (all authors at Zep AI), no ablations, single runs with no variance reported

## Digest

- Claim: Zep, a memory-layer service built on Graphiti (a temporally-aware knowledge graph engine), beats MemGPT on Deep Memory Retrieval (DMR), "94.8% vs 93.4%" (p. 1 abstract; p. 6, Table 1). On LongMemEvals it reports higher accuracy, "up to 18.5%," and about 90% lower latency than full-context baselines (p. 1; p. 7, Table 2).
- Mechanism: raw messages are stored as episode nodes. An LLM extracts entities (the speaker is always extracted, with the last n=4 messages as context, p. 3) and facts (edges) between entities. A reflexion-style pass reduces hallucination (p. 3). Entity names are embedded in 1024-dimensional vectors (p. 3).
- Graph structure (p. 2): three subgraphs, episodic (raw data), semantic (entities and facts), and community (cluster summaries). Facts can be hyperedges, extracted repeatedly between different entities.
- Bi-temporal model (p. 2–3): timeline $T$ is event/validity time and $T'$ is ingestion/transaction time. Each edge stores $t_{\text{valid}}, t_{\text{invalid}} \in T$ and $t'_{\text{created}}, t'_{\text{expired}} \in T'$.
- Invalidation (p. 3): an LLM compares a new edge with semantically related existing edges. On temporal overlap it sets the old edge's $t_{\text{invalid}}$ to the new edge's $t_{\text{valid}}$, and it always prioritizes new information. This mechanism is not evaluated on its own; only the knowledge-update and temporal-reasoning rows of Table 3 touch it (p. 7).
- Communities (p. 4): label propagation (not Leiden), extended incrementally by assigning each new node to its neighbors' plurality community. The authors say communities drift and periodic full refreshes are needed.
- Retrieval (p. 4–5): $f(\alpha)=\chi(\rho(\phi(\alpha)))=\beta$, where $\phi$ runs three searches (cosine, BM25, breadth-first over n hops), $\rho$ reranks, and $\chi$ formats facts with validity ranges and entity summaries. Five rerankers are described (RRF, MMR, episode-mentions, node-distance, cross-encoder), but the text does not say which one the experiments used (p. 5).
- Models (p. 5): BGE-m3 for embedding and reranking; gpt-4o-mini-2024-07-18 for graph construction; gpt-4o-mini or gpt-4o-2024-11-20 as the chat agent; gpt-4-turbo-2024-04-09 for the DMR runs comparable to MemGPT.
- DMR, gpt-4-turbo (p. 6, Table 1): Zep 94.8%; full-conversation 94.4%; MemGPT 93.4% (as reported in [3], not reproduced); conversation summaries 78.6%; recursive summarization 35.3%.
- DMR, gpt-4o-mini (p. 6, Table 1): Zep 98.2%; full-conversation 98.0%; conversation summaries 88.0%. MemGPT could not be reproduced with this model, "due to insufficient methodological details" (p. 6).
- The text itself calls the Zep margins "marginal" (p. 6): 0.4 points over full-conversation with gpt-4-turbo and 0.2 with gpt-4o-mini. The abstract's "outperforms" rests on MemGPT's published figure. Each cell is a single run, and no variance or confidence intervals appear in the text.
- The authors' own DMR critique (p. 6): each conversation has only 60 messages, which fits in context. Questions are single-turn fact retrieval with some ambiguous phrasing. Full-context baselines already score high.
- LongMemEvals (p. 6–7, Table 2): full-context vs Zep. gpt-4o-mini: 55.4% vs 63.8%; latency 31.3 s vs 3.20 s; 115k vs 1.6k average context tokens. gpt-4o: 60.2% vs 71.2%; latency 28.9 s vs 2.58 s. The text gives gains of 15.2% (gpt-4o-mini) and 18.5% (gpt-4o) (p. 7).
- Latency is not like-for-like. Zep was a hosted AWS us-west-2 service queried from a consumer laptop in Boston, which added network latency the baselines did not have (p. 6–7). Ingestion and graph-construction cost or latency is not reported in the text.
- Table 3 (p. 7): for gpt-4o-mini, Zep gains on four types (single-session-preference, temporal-reasoning, multi-session, single-session-user) and loses on single-session-assistant and knowledge-update. The authors call the single-session-assistant drop "a notable exception" (p. 8). Per-category question counts are not given; the text refers to [7] (p. 7).
- Judging (p. 6–7): DMR uses an unnamed "LLM judge." LongMemEvals uses GPT-4o with the question-specific prompts from [7], which the authors say correlate highly with humans.
- MemGPT on LongMemEvals failed: adding messages to archival memory "we were unable to achieve successful question responses" (p. 7). So LongMemEvals has no MemGPT baseline.
- Scope: there are no ablations (bi-temporal, reranker choice, BFS, communities). Experiments retrieve only the top edges and entity nodes (p. 5), so community and episode-linked retrieval are not evaluated (p. 3, p. 5).
- Overreach: the abstract's enterprise claims (business-data synthesis, cross-session synthesis, long-term context maintenance; p. 1) are not tested. The text says no existing benchmark assesses conversation-plus-business-data synthesis (p. 8). The conclusion's "state-of-the-art performance on existing memory benchmarks" (p. 8) rests on a DMR margin of under half a point and on LongMemEvals with no MemGPT comparison.
- The paper's own inconsistencies: retrieval depth is "20 most relevant edges and entity nodes" for all experiments (p. 5) but "top 10 most relevant nodes and edges" for DMR (p. 6); the headline 18.5% gain (p. 1, p. 7) does not reproduce from Table 2's 60.2% vs 71.2% under the same relative definition that gives the printed 15.2% for gpt-4o-mini (p. 7, Table 2); the gpt-4o single-session-user row in Table 3 repeats the gpt-4o-mini values exactly (81.4%, 92.9%, 14.1%) (p. 7, Table 3); the Table 3 "Delta" appears to be relative to the full-context score for gains but to the Zep score for declines (p. 7, Table 3); Section 4.2 says MemGPT "leads" at 93.4% while the same Table 1 shows full-conversation at 94.4% (p. 6, Table 1).

## Related in library

## Q&A

### 2026-10-26: How to read the LongMemEval deltas

- The "15.2%" and "18.5%" gains in the text, and the Delta column of Table 3, are **relative** changes, not percentage points (p. 7). In points: +8.4 (gpt-4o-mini, 55.4→63.8) and +11.0 (gpt-4o, 60.2→71.2) (p. 7, Table 2).
- 71.2/60.2 = 1.183, so the stated 18.5% is slightly off; 63.8/55.4 = 1.152 matches (our arithmetic).
- In Table 3 the single-session-user row is identical for both models (81.4→92.9), which may be a copy error in the paper (p. 7, Table 3).
- Scores are judged by GPT-4o with LongMemEval's prompts; the only baseline is full context (~115k tokens) (p. 7).
