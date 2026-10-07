I've read the folder, its scope, the whole topic tree and nearby folders. Here is my proposal. I haven't moved or edited anything yet.

## `llm/text-analytics`: proposal

The folder hangs together. All but one of its 12 papers take a collection of texts and find its structure in a form people can read: topics, clusters, taxonomies, concepts, or descriptions of how two corpora differ. It doesn't need splitting. The scope line describes it poorly, and one paper belongs elsewhere.

1. **Move *Can Large Language Models Transform Computational Social Science?* → `data-centric-ml/labels-and-annotation`.** The paper scores zero-shot LLMs label by label on 25 classification tasks against fine-tuned models and human annotators. Its own conclusion is that LLMs can serve as "zero-shot data annotators" (abstract, p. 1). That is the "LLMs as annotators" question already covered in that folder, next to *Is GPT-3 a Good Data Annotator?*. Nothing in the paper finds structure in a corpus.
2. **Rescope `llm/text-analytics`.** About a third of the folder is missing from the current line: four papers describe differences between corpora or generate hypotheses (D3, D5, *Explaining Datasets in Words*, HypotheSAEs), and GoalEx does goal-driven clustering. New scope:
   > Using LLMs to analyse text collections — topic modelling and clustering, taxonomy and concept induction, describing differences between corpora, hypothesis generation, usage insights from conversation logs.
3. **Fix the years of three entries in `catalog/skipped.yaml`.** They say 2020 but their arXiv ids are later: *Prompting Large Language Models for Topic Modeling* (2312.09693 → 2023) and *Text Clustering as Classification with LLMs* (2410.00927 → 2024). *Top2Vec* (2008.09470) and *Pre-training is a Hot Topic* (2004.03974) are correctly 2020. That makes two entries to fix, not three. These years show in the folder's "Considered, not added" table.

**Considered, not proposed:**
- **Moving BERTopic to `nlp/tasks-and-methods`.** The library's rule says "general before LLM-specific", and BERTopic is a pre-LLM method. But it is the baseline every LLM topic model here is measured against. The papers on topic modelling you decided to skip (Top2Vec, *Pre-training is a Hot Topic*) are also filed under this folder. Moving BERTopic alone would split topic modelling across two areas. I'd keep it here; say if you want the rule applied anyway.
- **A split into "organising a corpus" (7 papers) and "explaining datasets / hypothesis discovery" (4).** The division is real, but 4 papers is too few for a folder. Worth revisiting if the second group grows.
- **Moving in *Which Economic Tasks are Performed with AI?* and *How People Use ChatGPT* (both in `ai-and-society/`).** They use Clio-style pipelines, but what they contribute is findings about AI use, not a method. They're filed in the right place.

**Resulting tree** (if 1–3 are applied):
```
llm/text-analytics/ (11)   — rescoped as in 2
  BERTopic · TopicGPT · ClusterLLM · GoalEx · TnT-LLM · LLooM · Clio
  D3 (Describing Differences…) · D5 (Goal Driven Discovery…)
  Explaining Datasets in Words · HypotheSAEs
data-centric-ml/labels-and-annotation/ (27 → 28)
  + Can Large Language Models Transform Computational Social Science?
```

None of these papers has a note in `notes/` yet, and the folder has no review, so a move won't break any review links.

Which changes should I apply? Reply with the numbers, e.g. "1–3".
