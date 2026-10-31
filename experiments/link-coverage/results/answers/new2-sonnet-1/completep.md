**Main idea:** when you make a transformer deeper, scale each residual block's contribution by $1/L$ (and adjust a few optimizer settings to match). This is what the paper calls CompleteP. With it, the learning rate and init scale you tuned on a shallow model stay optimal as depth grows, and every layer keeps learning real features instead of making only tiny, nearly linear updates ("lazy" learning).

**Intuition.** µP (Tensor Programs V in the library) solved this for width: tune on a narrow model, then reuse the hyperparameters on a wide one. Depth is harder. A residual network adds $L$ blocks to the stream, so the output moves by a different amount as $L$ changes, and the best learning rate drifts. The usual fix is to put a multiplier $L^{-\alpha}$ on each block:

$$h^{\ell+1} = h^\ell + L^{-\alpha} F_\ell(h^\ell)$$

The paper's [Eq. 1, p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2&rect=219,296,505,311) uses $\alpha\in[0.5,1]$. Earlier work used $\alpha=0.5$. Here, $\alpha=0.5$ makes each block's update drift toward its linearization at rate $1/\sqrt{L}$, which is the lazy regime (p. 10, Figure 6). Only $\alpha=1$ keeps the nonlinear part of each block's update the same size as the linear part, which is the "complete" feature learning of the title. The paper calls this argument a heuristic on a toy width-1 model, not a proof (p. 7, p. 10).

**What it changes in practice** ([Table 1, p. 4](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=4&rect=107,263,505,513)). Besides the $L^{-1}$ multiplier, with AdamW:
- The hidden, bias and LayerNorm learning rates scale by $m_L^{\alpha-1}$.
- The AdamW ε in the residual blocks also scales with depth.
- The paper calls the LayerNorm, bias and ε corrections essential for stability at $\alpha=0.5$ (p. 2).

**Evidence.**
- **Transfer:** in [Figure 2, p. 5](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=5&rect=107,189,506,368), standard parameterization, µP and $\alpha=0.5$ all have optimal learning rate and init that shift with depth. Only $\alpha=1$ keeps them stable from 2 to 128 layers, and its loss keeps improving with depth.
- **Compute efficiency:** the headline "12–34% compute savings" is measured against µP at 1.5B non-embedding parameters ([Table 2, p. 7](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=7&rect=107,339,505,481)). The savings are 11.8% at the best width-to-depth shape and 34.4% at the deepest shape (179 layers).
- **Flexible shapes:** CompleteP keeps a much wider range of width-to-depth ratios near-optimal. At 1.5B, a ratio of 11.8 stays within 1% of the best loss, against 38.7 for µP (p. 6, Figure 4f).
- **Optimal depth:** the compute-optimal width-to-depth ratio stays below about 60, not the ~100 common in practice (p. 5–6).

**Caveats.**
- The gain at the optimal shape is modest; most of the 34% comes from deep, narrow models.
- All runs are the authors' own, on one dataset (SlimPajama) and one architecture family, up to 1.5B parameters.
- The main text doesn't report seeds or variance, and the transfer evidence is in figures only.
- The scaling-law fit uses only 3 points.

**Related in the library:** it extends Tensor Programs V (µP) from width to depth. All its runs use AdamW from Decoupled Weight Decay Regularization, and the paper adds depth-aware scaling rules for that optimizer's weight decay and ε.

This is from the library's note, with the key numbers checked against the cited pages. I didn't re-derive the theory section (pp. 9–10), so the "linear vs nonlinear term" argument above is the note's summary.
