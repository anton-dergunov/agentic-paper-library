**Main idea:** the paper proposes a way to set a transformer's hyperparameters as it gets deeper, so that the best learning rate stays the same across depths and every layer keeps learning real features. They call it **CompleteP**.

**The problem.** Scaling a model up means choosing many hyperparameters again, and the learning rate is the costly one. Under some parameterizations, the optimal learning rate drifts as depth grows, so you either re-tune at each size or accept a worse run (abstract, p. 1). Some parameterizations do transfer the learning rate across depth but still put the network in a "lazy" regime, where each layer learns only features close to its linearization. Then the extra depth and nonlinearity go unused (p. 1).

**The mechanism.** Each residual block is added to the stream with a depth-dependent factor:

$$h_{\ell+1} = h_\ell + L^{-\alpha}\, F_\ell(h_\ell), \qquad \ell \in \{1,\dots,L\}$$

Here $F_\ell$ is the $\ell$-th block (attention or MLP), $L$ is depth, and $\alpha \in [0.5, 1]$ is the one knob ([p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2), Eq. 1). Earlier work argued for $\alpha = 0.5$ in practice and considered transfer impossible at any $\alpha$. Other work found $\alpha = 1$ learns better as $L \to \infty$ (p. 2). The authors compare the two and find $\alpha = 1$ is consistently more compute-efficient, through better hyperparameter transfer and faster pretraining (Figure 1, p. 1). They call $\alpha = 1$ CompleteP because it is the unique choice that keeps every layer learning features as width and depth grow.

**What is new:**
- **Depth-wise transfer.** The authors claim $\alpha = 1$ is the only option that transfers the learning rate and init scale across depth, which earlier theory had called impossible (p. 2).
- **A refined criterion.** They require every layer's representation to stay non-lazy, nonlinear with respect to the parameters of that layer and all earlier ones. Only $\alpha = 1$ satisfies this.
- **Extensions for modern training.** Pre-LN transformers with AdamW need rescaled LayerNorm learning rates, weight decay, bias learning rates and AdamW ε. The authors say these are essential for stable training with $\alpha = 0.5$ (p. 2; Table 1, Section D).

**Results:** models from 75M to 1.9B parameters, trained at 20 tokens per parameter. The 1.9B models with $\alpha = 1$ save 11.8% FLOPs over µP at the optimal shape and 34.4% for a 179-layer model (p. 2). The abstract gives the range as 12–34%. The headline gains grow with depth, and CompleteP keeps a wider range of width-to-depth ratios compute-efficient.

**Caveats.** I read only pages 1–2, so the lazy-learning theory (Section 6) and the scaling-law details are unchecked. The results come from Cerebras CS-3 runs. Their reference implementation is a nanoGPT fork (EleutherAI, `completep` branch).

**Related in the library:** the µP line of work is the obvious neighbour, but I haven't checked which of its papers are filed here. Its `notes/` file, if one exists, would list them.
