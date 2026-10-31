**Short answer: this survey doesn't name a default, so I'd not take a default from it alone.** On its own evidence, the safest go-to is a well-tuned LDA as the baseline, with an embedding-based model (BERTopic or FASTopic) as the modern option to compare against.

What the paper supports:

- **Page 3 is only the setup.** It defines topics as word distributions and documents as topic mixtures (Figure 2, p. 3), then introduces the VAE framework that most neural topic models use (p. 4 onward). It does not compare models.
- **Classic LDA is still a serious contender.** Section 6.1.1 says some benchmarking studies find conventional LDA can still outperform NTMs in certain respects (p. 13, citing Doan and Hoang 2021 and Hoyle et al. 2022). The survey attributes this partly to inconsistent evaluation.
- **Embedding-based models are the newer direction.** Top2Vec and BERTopic cluster document embeddings and derive topics from them (p. 9). FASTopic replaces VAE or clustering with optimal transport between pretrained document embeddings and topic and word embeddings (p. 10). The survey describes these designs but does not benchmark them against each other.
- **Evaluation is the weak point.** Coherence and diversity metrics may disagree with human judgment, and preprocessing choices change results (pp. 13–14). Whatever you pick, judge it with more than one metric and a quick human read of the topics.

My recommendation, from this paper plus that caveat: run LDA first as the baseline. If you want a single modern default to build on, use BERTopic or FASTopic. FASTopic is the newer and more fully specified option, and its paper is in the library at `library/nlp/topic-models/`. I have not read its note or results, so check its claims there before adopting it. The survey is from 2024, so it can't tell you what's newest now.
