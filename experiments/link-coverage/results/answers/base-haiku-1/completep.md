**Main idea:** make the learning rate and other hyperparameters stay the same as a transformer gets deeper, and make sure every layer still learns real features. Tune on a small model, then train a deep one without re-tuning. The paper calls its rule **CompleteP**.

**The problem.** µP already lets you tune small and train large when you scale *width*. Scaling *depth* is harder, because the optimal learning rate often shifts as layers are added, so you either re-tune (expensive) or accept a worse model ([p. 1, abstract](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1)). The authors also argue that some rules that do transfer hyperparameters can still leave layers in a "lazy" regime, where each layer only learns features close to its linearization, so extra depth and nonlinearity go unused.

**The mechanism.** Each residual block is scaled before it is added to the residual stream:

$$h_{\ell+1} = h_\ell + L^{-\alpha}\, F_\ell(h_\ell), \qquad \ell \in \{1,\dots,L\}$$

Here $L$ is depth, $F_\ell$ is the attention or MLP block, and $\alpha \in [0.5, 1]$ sets how strongly the block's contribution shrinks with depth ([p. 2, Eq. 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2)). Prior work favoured either $\alpha = 0.5$ (Yang et al.) or $\alpha = 1$ (Bordelon et al.). The paper finds $\alpha = 1$ is consistently more compute-efficient, with better hyperparameter transfer and faster pre-training. CompleteP is the unique $\alpha$ that keeps feature learning complete as width and depth grow ([p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2)).

**Beyond the residual scaling.** For modern Pre-LN transformers trained with AdamW, the parameterization also rescales LayerNorm learning rates, bias learning rates, weight decay and Adam's ε as functions of depth and width (Table 1). The authors say these changes are needed for stable training with $\alpha = 0.5$ ([p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2)).

**Results (from pages 1–2 only; I haven't checked the tables).** At 1.9B parameters, CompleteP saves 11.8% of FLOPs over µP for compute-optimal shapes and 34.4% for a 179-layer model. Overall the abstract reports 12–34% gains, and the method keeps a wider range of width-to-depth ratios compute-efficient.

Related work in the library: the paper sits in `deep-learning/optimizers-and-schedules/`, and it builds on µP and the depth-scaling line of work it cites (Yang et al., Bordelon et al., Large et al.). I haven't checked which of those are in the library.
