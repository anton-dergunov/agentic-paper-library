The survey doesn't name a default model. Page 3 is only the introduction and the topic-model setup (Figure 2, the K topics and the two distributions), so it doesn't answer the question. The note for this paper already has a Q&A on exactly this, which I've drawn on below. I didn't re-check its page citations beyond page 3.

- **No model is endorsed.** The survey compares no models on any benchmark. Its only experiment checks a new diversity metric, TSD, against human ratings.
- **FASTopic is the closest thing to an endorsement.** The survey calls it "a neat and efficient paradigm" (p. 10). Its first author also wrote the TopMost toolkit the survey cites, so this isn't an independent view.
- **The survey warns against picking a neural winner.** It says benchmarks have found "conventional LDA can still outperform NTMs in certain aspects" (p. 14–15). It also says coherence may disagree with human judgment for neural models, and that preprocessing alone changes results (p. 14).
- **Some methods don't give proper distributions.** Clustering-based methods (Top2Vec, BERTopic) and TopicGPT can't supply proper doc-topic and/or topic-word distributions (p. 9).

My practical reading, which is mine and not the paper's: use LDA (MALLET or tomotopy) as the baseline to beat. Use FASTopic when you need the topic distributions as features, but its evidence is only the authors' automatic metrics (FASTopic paper, p. 6–7, Tables 1–3). Use BERTopic or an LLM-based method when you want browsable, labelled themes rather than distributions.
