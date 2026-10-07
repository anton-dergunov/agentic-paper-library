# Zep: A Temporal Knowledge Graph Architecture for Agent Memory

type: system

## Digest

- Zep = memory-layer service; core engine Graphiti (open source). Graph with three tiers: episodes (raw messages, non-lossy), semantic entities + fact edges, communities (clusters with summaries); episodic/semantic split borrowed from AriGraph, communities from GraphRAG (p. 2).
- Ingestion per message: entity extraction with the last n=4 messages as context plus a reflexion-style pass; entity resolution by embedding (1024-d) + full-text candidates, then an LLM dedup prompt; writes via predefined Cypher, not LLM-generated queries (p. 3).
- Facts are edges; dedup only among edges between the same entity pair; the same fact may be attached to several pairs (hyper-edge emulation) (p. 3).
- Bitemporal: T' (t'_created, t'_expired, ingestion order) and T (t_valid, t_invalid, world time), resolved from relative dates via the message's t_ref. An LLM checks new edges against related ones; on overlapping contradiction the old edge's t_invalid = new edge's t_valid; newer info always wins (p. 3).
- Communities: label propagation instead of GraphRAG's Leiden, because it extends incrementally (new node joins the plurality community of its neighbours); drifts, so periodic full refresh (p. 4).
- Retrieval f = constructor ∘ reranker ∘ search. Search: cosine, BM25, BFS n-hops (seedable with recent episodes). Rerankers: RRF, MMR, episode-mentions frequency, node distance to a centroid, cross-encoder. Context = facts with date ranges + entity summaries (p. 4–5).
- Setup: BGE-m3 embed/rerank, gpt-4o-mini builds the graph; top 20 edges+nodes on LME, top 10 on DMR (p. 5–6).
- DMR (500 convs, ~60 msgs each): Zep 94.8% vs MemGPT 93.4% vs full context 94.4% (gpt-4-turbo); 98.2% vs full context 98.0% (gpt-4o-mini). Authors call DMR too easy and ambiguous (p. 6, Table 1).
- LongMemEval_s (~115k tokens): gpt-4o-mini 63.8% vs 55.4% full context; gpt-4o 71.2% vs 60.2%; context 1.6k vs 115k tokens; latency ~3 s vs ~30 s (~90% less) (p. 7, Table 2).
- By type (gpt-4o): preference 20.0→56.7, temporal 45.1→62.4, multi-session 44.3→57.9, knowledge-update 78.2→83.3; single-session-assistant drops 94.6→80.4 (p. 7, Table 3).
- MemGPT could not be run on LME (no history ingestion). No ablations; no other memory systems compared; vendor-run on its hosted service (p. 7).

## Related in library

- MemGPT Towards LLMs as Operating Systems: the baseline on DMR; agent-managed paging vs external temporal graph.
- LongMemEval Benchmarking Chat Assistants on Long-Term Interactive Memory: the main benchmark; its question types structure the results.
- Mem0 Building Production-Ready AI Agents with Scalable Long-Term Memory: later production memory system with a graph variant; evaluates against Zep.
- HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models: KG memory with PageRank retrieval, static corpus, no time.

## Q&A

### 2026-10-07: How are outdated facts invalidated, and what is the LongMemEval result?

Invalidation (p. 3, §2.2.3):

- Each fact edge has four timestamps: t'_created / t'_expired (when the system learned or retired it) and t_valid / t_invalid (when it held in the world). Relative dates ("two weeks ago") are turned into dates using the message's t_ref.
- When a new edge arrives, an LLM compares it with semantically related existing edges. If they contradict and their validity periods overlap, the old edge's t_invalid is set to the new edge's t_valid. Newer information always wins.
- The old edge is kept, not deleted, so the history stays queryable, and retrieval returns facts with their validity ranges (p. 4).

LongMemEval_s (p. 7, Table 2). The baseline is full context: the whole ~115k-token history in the prompt, not another memory system. MemGPT could not be run on LME (p. 7, §4.3.1).

| Model | Full context | Zep | Context tokens | Latency |
|---|---|---|---|---|
| gpt-4o-mini | 55.4% | 63.8% | 115k → 1.6k | 31.3 s → 3.20 s |
| gpt-4o | 60.2% | 71.2% | 115k → 1.6k | 28.9 s → 2.58 s |

- The paper's "+15.2%" and "+18.5%" are relative gains. In absolute terms they are +8.4 and +11.0 points.
- Knowledge-update is the category invalidation targets, and the gain there is small: 78.2 → 83.3 with gpt-4o, and a drop of 76.9 → 74.4 with gpt-4o-mini (p. 7, Table 3). The authors attribute the drop to weaker models misreading the temporal data. There is no ablation that isolates invalidation.
