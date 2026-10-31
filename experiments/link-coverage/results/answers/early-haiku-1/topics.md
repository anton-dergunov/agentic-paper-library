**Short answer: the paper doesn't name a default model.** Page 3 only sets up the survey: it reviews neural topic models (NTMs), their applications and their challenges, and it says nothing about which one to use ([Survey, p. 3](http://pdf.invalid/nlp/topic-models/A%20Survey%20on%20Neural%20Topic%20Models.%20Methods,%20Applications,%20and%20Challenges.pdf?page=3)). Its only experiment checks a new diversity metric, not any model. Its closest hint is for FASTopic (p. 10), but FASTopic and the survey's toolkit share a first author, so that isn't independent.

The paper also gives reasons not to pick a neural winner on its evidence:
- It cites benchmarks where conventional LDA still beats NTMs in some respects (p. 14–15).
- Automatic coherence may disagree with human judgment for neural models (p. 14–15). [Hoyle et al., "Is Automated Topic Model Evaluation Broken"](http://pdf.invalid/nlp/topic-models/Is%20Automated%20Topic%20Model%20Evaluation%20Broken.%20The%20Incoherence%20of%20Coherence.pdf?page=1) makes this case in more detail.
- Preprocessing alone changes results (p. 14).

My recommendation, based on the library's three topic-model papers rather than this survey alone:
- **Baseline:** LDA (MALLET or tomotopy). It is the bar to beat, and the survey and Hoyle et al. both treat it as competitive.
- **Default neural candidate:** FASTopic. It is the most recent of the three, has a PyPI package, and beats the others on most automatic measures in its own paper. Its evidence is only automatic metrics run by the authors, so check its topics by hand on your own data.
- **If you want browsable, labelled themes rather than word and document distributions:** BERTopic or an LLM-based method. The survey notes that clustering-based methods such as Top2Vec and BERTopic, and TopicGPT, don't give proper topic-word and doc-topic distributions (p. 9).

The survey is also not recent enough to say what is the default now. I haven't searched for newer work; if you want that, I can do a web search for 2025–2026 topic-model comparisons.
