The survey doesn't pick a default. It compares no models on any benchmark, and its only experiment tests its new diversity metric. My answer below rests on the paper plus its library note.

**What the survey says**
- It comes closest to an endorsement with FASTopic, which it calls ["a neat and efficient paradigm"](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=10&rect=163,296,292,306) (p. 10). FASTopic and the TopMost toolkit share a first author with the survey, so this isn't independent evidence.
- It argues against crowning a neural winner. Metrics are inconsistent, so some benchmarks find that ["conventional LDA can still outperform"](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=14&rect=79,482,248,493) neural topic models in some respects (p. 14). Preprocessing alone changes results, and neural models are sensitive to hyperparameters and to a large number of topics.
- Top2Vec, BERTopic and TopicGPT can't give proper document-topic or topic-word distributions (p. 9).

**My practical reading (not from the paper)**
- **Default:** BERTopic if you want browsable, labelled themes in a corpus of mostly short-to-medium documents. It is a pipeline of embeddings, UMAP, clustering and c-TF-IDF keywords, and it is easy to run and inspect.
- **If you need real distributions:** FASTopic, when you need document-topic and topic-word distributions as features. Its evidence is the authors' automatic metrics only (FASTopic paper, p. 6–7, Tables 1–3).
- **Baseline to beat:** LDA (MALLET or tomotopy). Given the survey's own caveats, don't adopt a neural model without checking it against LDA on your data.
- **Evaluation:** judge candidates on your own corpus with human inspection. The survey itself says coherence and diversity scores can disagree with human judgment.

The library also has the FASTopic paper and *Is Automated Topic Model Evaluation Broken* (Hoyle et al.), if you want to check the metric concern.

The library has no BERTopic paper. Its place in my recommendation comes from my general knowledge and the survey's description of it. I can run `paperlib info` on it, or search for recent head-to-head comparisons, if you want that backed up.

I changed nothing, so there's no commit message to suggest.
