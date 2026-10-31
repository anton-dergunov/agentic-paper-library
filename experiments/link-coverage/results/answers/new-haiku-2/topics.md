I'll check the paper's text on page 3, plus the area review and any existing note, before answering.

No review or note covers this folder yet, so I'll read page 3 of the paper directly.

Page 3 doesn't name a default model. Before I say anything about FASTopic as a candidate, I'll read its abstract, since it is the newer paper in the same folder.

The paper doesn't name a default model. Page 3 is the setup section: the LDA problem setting, the topic-word and doc-topic distributions (β, θ), and the evaluation metrics. The only model it singles out there is the VAE-based neural topic model, which it calls "the most basic and popular NTM" (p. 3). That is a teaching baseline, not a recommendation, and a January 2024 survey can't tell you what is default now.

The newer paper in this folder is FASTopic (May 2024, p. 1 abstract). It replaces VAE-based models with pretrained Transformer document embeddings plus learned topic and word embeddings, and claims better speed, stability and transferability than the baselines in its experiments. I've only read the abstract and the opening figure, so I haven't checked its tables. Those are the authors' own results.

My recommendation:

- **Try FASTopic first** if you want a current default. It is the most recent method here and is built on the same kind of pretrained embeddings most modern pipelines already use.
- **Keep BERTopic as the reference point.** FASTopic's own figure compares against it, and it is the common practical alternative. I haven't read its paper, so I can't say how it compares on your data.
- **Don't trust a single number for choosing.** The coherence paper in this folder (2021, p. 1 abstract) argues automated coherence was never validated for neural topic models and disagrees with human judgment. Check the topics by reading them on your own corpus before you commit.

Nothing in the library is a settled default yet. The `nlp/topic-models` folder has no literature review, so there is no area-level answer to point to. If you want, I can read FASTopic's results tables and compare them against the baselines it reports, so the recommendation rests on its numbers rather than its abstract.
