**Short answer: this paper doesn't say.** Page 3 is the survey's introduction and contribution list, with the topic-modelling illustration in Figure 2. The survey doesn't name a default model anywhere. It compares no models on any benchmark, and its only experiment tests a new diversity metric.

What the paper does give:

- **The conventional baseline is LDA**, and the survey defines topic modelling against it ([p. 1–2](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=1)).
- **The basic neural model is a VAE**, following NVDM and ProdLDA ([p. 6](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=6)).
- **FASTopic is the closest thing to an endorsement.** The survey calls its optimal-transport approach "a neat and efficient paradigm" that avoids complicated VAE or simple clustering structures ([p. 10](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=10)). The first author also wrote FASTopic and the TopMost toolkit, so this is not independent.
- **It argues against a neural default.** It reports benchmarks where conventional LDA still outperforms NTMs in some respects, and says coherence may disagree with humans for neural models ([p. 14–15](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=14)).
- **Clustering-based methods and TopicGPT don't give proper topic-word or doc-topic distributions** ([p. 9](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=9)). BERTopic is in that group.
- **For coherence, use Palmetto** ([p. 5](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=5)).

My own recommendation, not the paper's: use LDA (MALLET or tomotopy) as the baseline every new model has to beat. Reach for FASTopic when you need topic-word and doc-topic distributions as features, but treat its evidence as the authors' own automatic metrics. Use BERTopic or an LLM-based method when the goal is browsable, labelled themes rather than distributions.

The library's note for this paper already has this answer as a Q&A entry dated 2026-10-30. The topic-models folder has no review yet, so there is no area-level comparison to point to. The other two papers in `library/nlp/topic-models/` are FASTopic and "Is Automated Topic Model Evaluation Broken", and they would be the next things to read before deciding.
