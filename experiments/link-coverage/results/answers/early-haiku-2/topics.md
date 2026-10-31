The paper doesn't name a default model, and page 3 doesn't either. Page 3 is the preliminaries: it sets up the LDA problem (K latent topics, topic-word and doc-topic distributions, Figure 2) and says nothing about which model to use. The survey itself is from January 2024, so it is almost three years old for a question about "nowadays".

What the survey does say, which bears on a default:

- **LDA is still the reference point.** The survey notes (p. 16) that some benchmarking studies found conventional LDA can still outperform neural topic models, mostly because of inconsistent metrics and preprocessing across papers.
- **The neural baseline is VAE-based.** The most basic neural topic model is the VAE framework, with NVDM and ProdLDA as the pioneering examples (p. 4).
- **Embedding-based alternatives exist.** Top2Vec and BERTopic cluster document embeddings and derive topics from cluster terms (p. 9). FASTopic (p. 10, §3.11) replaces the VAE with optimal transport between document and topic embeddings and is presented as fast and stable. The survey gives no benchmark numbers for these.
- **Metric choice is shaky.** Section 6.1 (p. 15) says coherence and diversity metrics may not agree with human judgment for neural models, so choosing a model on coherence scores alone is weak evidence.

My recommendation, based on this survey plus the other papers in `library/nlp/topic-models/`:

- **Default starting point: BERTopic.** It is simple, works with off-the-shelf pretrained embeddings, and is the most widely used of the embedding-based methods. Use plain LDA as the baseline you must beat.
- **Consider FASTopic** if you need speed and stability on a larger corpus. Its own paper is in the same folder, and I haven't checked its reported results against the baselines.

Caveat: this rests on the survey's descriptions, not on numbers I've checked. Before you commit to one, read the FASTopic paper's results and the coherence paper (*Is Automated Topic Model Evaluation Broken?*), and compare candidates on your own data with a human check. The folder has no literature review yet (`reviews/nlp/topic-models.md` doesn't exist), so I could not check this against a review either. If you want, I can write one.
