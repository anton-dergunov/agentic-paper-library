Proposal for **llm/text-analytics** (12 papers, with no review yet):

The folder holds two families:
- **Organising a corpus into topics or categories:** TopicGPT, ClusterLLM, GoalEx, TnT-LLM, Clio and LLooM.
- **Describing a corpus in natural-language hypotheses** (Zhong et al.'s line): Describing Differences (D3), Goal Driven Discovery (D5), Explaining Datasets in Words and HypotheSAEs.

Two papers don't fit either family.

## Proposed changes

1. **Move "Can Large Language Models Transform Computational Social Science?" to `data-centric-ml/labels-and-annotation`.** It tests zero-shot LLMs as classifiers and annotators against fine-tuned models and crowdworkers. That folder already holds the papers it belongs with: *ChatGPT Outperforms Crowd-Workers*, *Is GPT-3 a Good Data Annotator?*, *Automated Annotation with Generative AI Requires Validation* and *LLM Hacking*.

2. **Move "BERTopic" to `nlp/tasks-and-methods`, and add topic modelling to that folder's scope:**
   `Classification, extraction, summarization, QA, topic modelling and other tasks with pre-LLM methods.`
   - **Why:** BERTopic uses sentence embeddings, clustering and class-based TF-IDF, with no LLM. Your filing rule puts a method that predates LLMs in its general area.
   - **Downside:** it would sit apart from TopicGPT and ClusterLLM, which use it as their baseline.
   - The skipped Top2Vec and CTM (*Pre-training is a Hot Topic*) entries would move with it, since they're pre-LLM topic models too.

   If you'd rather keep the classical baseline next to its LLM successors, skip this one.

3. **Rescope `llm/text-analytics`** to cover what it actually holds. The current scope leaves out the hypothesis papers:
   `Using LLMs to analyse text collections — LLM topic modelling and clustering, taxonomy and concept induction, usage insights, describing corpora and their differences as natural-language hypotheses.`

**Not proposed:** splitting the folder into `corpus-structure/` and `hypothesis-generation/`. The division is real, but it would leave folders of 6 and 4 papers, and GoalEx sits in both families.

## Resulting tree (with 1–3 applied)

```
llm/text-analytics/                       10
  ClusterLLM, Clio, Concept Induction (LLooM), GoalEx,
  TnT-LLM, TopicGPT,
  Describing Differences (D3), Goal Driven Discovery (D5),
  Explaining Datasets in Words, HypotheSAEs
data-centric-ml/labels-and-annotation/   +1  Can LLMs Transform Computational Social Science?
nlp/tasks-and-methods/                    +1  BERTopic
```

Separately, `catalog/skipped.yaml` lists three of this folder's skips as 2020 when their arXiv IDs say otherwise: *Prompting LLMs for Topic Modeling* (2312) and *Text Clustering as Classification with LLMs* (2410) are 2023 and 2024. I can fix those dates while I'm applying the changes.

Which changes should I apply?
