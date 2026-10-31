The survey doesn't name a default, and page 3 doesn't address the question. Page 3 is the introduction, the contributions list and the topic-modeling illustration. The paper is a 2024 survey that organises neural topic models by architecture (VAE, embeddings, graphs, pre-trained language models, clustering) and doesn't rank them.

Where the paper does give direction:

- **The basic neural baseline is the VAE-based model** (NVDM, ProdLDA). The survey treats it as the reference architecture that the others extend ([p. 6](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods%2C%20Applications%2C%20and%20Challenges.pdf?page=6)).
- **Embedding-based and clustering-based methods are the newer direction.** It covers ETM and NSTM, and clustering approaches such as Top2Vec and BERTopic ([p. 7](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods%2C%20Applications%2C%20and%20Challenges.pdf?page=7), [pp. 9–10](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods%2C%20Applications%2C%20and%20Challenges.pdf?page=9)).
- **Evaluation:** it recommends the Palmetto tool and the CV coherence metric ([p. 5](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods%2C%20Applications%2C%20and%20Challenges.pdf?page=5)).
- **Caveat:** the survey itself says the topic-diversity metrics are unresolved ([p. 5](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods%2C%20Applications%2C%20and%20Challenges.pdf?page=5)). The library's "Is Automated Topic Model Evaluation Broken?" paper goes further and questions automated coherence for neural models.

My recommendation, which is my judgement rather than the paper's:

- **Default for discovering topics in a corpus:** a document-embedding model, with BERTopic as the practical choice. Embed the documents with a sentence-transformer, cluster them, and label each cluster with c-TF-IDF. This is how most applied work gets done now.
- **Newer option:** FASTopic, which the library also holds. It reports better coherence, diversity and speed than the baselines it was tested against ([p. 9](http://pdf.invalid/nlp/topic-models/FASTopic.%20Pretrained%20Transformer%20is%20a%20Fast%2C%20Adaptive%2C%20Stable%2C%20and%20Transferable%20Topic%20Model.pdf?page=9)). Those numbers are the authors' own, and I haven't checked its tables.
- **Always report LDA as the baseline.** The survey's own preliminaries use it as the reference for what a topic model is.
- **Judge the output by reading the topics**, not only by coherence scores, given the evaluation caveats above.

This is a 2024 survey, and the field has moved since, so check recent work before settling on a default. I haven't searched the web for newer comparisons.
