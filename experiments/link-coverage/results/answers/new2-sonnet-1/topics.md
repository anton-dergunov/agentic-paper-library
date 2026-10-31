The survey doesn't pick a default model. It compares no models on any benchmark, and its only experiment tests a new diversity metric. So the answer below is my reading of it, plus what the library's note on the paper says.

**What the survey says**
- **Nearest to an endorsement is FASTopic.** The survey calls it "a neat and efficient paradigm" that avoids the "complicated VAE or simple clustering structures" ([p. 10](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=10&rect=236,268,290,279)). It embeds documents with a pretrained Transformer and uses optimal transport between document, topic and word embeddings. The first author (Xiaobao Wu) also wrote FASTopic and the TopMost toolkit, so this isn't independent.
- **It doesn't crown a neural winner.** Metrics are used inconsistently and may not match human judgment for neural models. Some benchmarks even find that [conventional LDA can still outperform neural topic models](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=14&rect=79,482,248,493) (p. 14). Preprocessing choices alone change the results.
- **Clustering methods and TopicGPT have a limitation.** Top2Vec, BERTopic and TopicGPT [cannot produce proper doc-topic or topic-word distributions](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=9&rect=305,494,449,505) (p. 9). Their advantage is efficiency.

**My practical reading (not from the paper)**
- **You need topic distributions as features:** start with FASTopic. Its evidence is the authors' own automatic-metric results, so check it on your corpus.
- **You want a baseline to beat:** use LDA (MALLET or tomotopy). Given the evaluation problems above, it is the safest comparison.
- **You want browsable, labelled themes:** BERTopic or an LLM-based method such as TopicGPT. This fits only if you don't need distributions.

FASTopic is in the library at `library/nlp/topic-models/`. Its paper has the actual comparisons, which this survey lacks (the note puts them at FASTopic p. 6–7, Tables 1–3). The note says its metrics are automatic ones, and the Hoyle et al. paper in the same folder questions how far coherence can be trusted. Want me to read both and give a more grounded recommendation?

I made no changes, so there is no commit message to suggest.
