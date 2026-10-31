**Main idea:** Training deep transformers is expensive, and the usual scaling rules make it hard to reuse hyperparameters (especially learning rate) when you add layers. The paper proposes a scaling rule, CompleteP, that fixes this and makes deep models more compute-efficient.

**The problem (p. 1, abstract).** A parameterization is a rule for how model and optimizer hyperparameters should change as the model grows. Some rules don't transfer the best learning rate across depth, so you either re-tune at every size, which is expensive, or accept worse training. The authors also argue that some rules that do transfer can still put the layers in a "lazy" regime, where each layer learns only features close to its linear approximation. Then the extra depth and nonlinearity add little.

**The mechanism (p. 2, Eq. 1).** Each residual block's output is scaled by a depth factor before it is added to the residual stream:

$$h_{\ell+1} = h_\ell + L^{-\alpha} F_\ell(h_\ell), \quad \ell \in \{1,\dots,L\}$$

Here $L$ is the number of layers, $F_\ell$ is the block (attention or MLP), and $\alpha \in [0.5, 1]$ sets how strongly the update shrinks with depth. The two candidates were $\alpha = 0.5$, which Yang et al. favoured, and $\alpha = 1$, which Bordelon et al. favoured. The paper finds $\alpha = 1$ is consistently better, both for learning-rate transfer across depth and for training speed (Figure 1, p. 1).

**What CompleteP adds.** Setting $\alpha = 1$ is the core. The authors also rescale LayerNorm, the bias learning rates, AdamW's weight decay and AdamW's ε (Table 1, p. 2). They call the result CompleteP because $\alpha = 1$ is the unique choice that keeps feature learning complete as width and depth scale (Section 6).

**Results.**
- Only $\alpha = 1$ gives depth-wise hyperparameter transfer, which the authors say Yang et al. thought impossible (p. 2).
- For 1.9B-parameter models (1.5B non-embedding), CompleteP saves 11.8% of FLOPs over µP at the optimal shape and 34.4% for a 179-layer model (p. 2). The abstract's 12–34% range comes from these numbers.
- It allows a wider range of width-to-depth ratios to stay compute-efficient, which helps when hardware or deployment constraints call for unusual shapes (Figure 1, right).

I read only page 1 and the start of page 2, so the Table 1 details and the derivations come from later pages I haven't checked. There's no note for this paper yet; I can write one with `paperlib read` if you want the full digest.
