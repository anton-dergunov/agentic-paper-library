I'll check what the library already has on this paper, then read the text.

## Main idea

**To train a deep transformer well, scale each residual block's output by 1/L (L is the number of layers). That one choice makes the best learning rate transfer across depth, and it keeps every layer learning real features. The authors call this "CompleteP".**

### Intuition

A transformer layer adds its output to a running "residual stream": $h_{\ell+1} = h_\ell + L^{-\alpha} F_\ell(h_\ell)$ ([Eq. 1, p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2&rect=219,296,505,311)). Here $F_\ell$ is the attention or MLP block, and $\alpha \in [0.5, 1]$ sets how strongly each block is damped as the network gets deeper.

- **The earlier choice, $\alpha = 0.5$, is the "$1/\sqrt{L}$" rule.** Yang et al. argued it works best in practice, and also argued that depth-wise hyperparameter transfer is impossible at any $\alpha$ (p. 2).
- **This paper picks $\alpha = 1$.** Take a 100-layer model with the 1/L scaling. Each block then nudges the stream only a little, but together the blocks still produce a large total change.
- **The practical payoff is the same as µP gave for width.** Tune the learning rate and initialisation on a shallow model (2 layers), then reuse them on a deep one (up to 128 layers) without re-tuning. In the authors' runs, only $\alpha = 1$ keeps the optimum stable across depth. SP, µP and $\alpha = 0.5$ all see it shift (p. 5, Figures 2–3, shown in figures only).

### Why "lazy" matters

Transfer alone isn't enough, the authors argue. A parameterisation can have hyperparameters that transfer and still be *lazy*. In a lazy layer, training only moves the output as far as a linear approximation around initialisation predicts, so depth and nonlinearity go unused.

- **The test is a toy width-1 model (p. 10, Eqs. 5–7).** A block's linear update is $\Theta(1/L)$ and its nonlinear update is $\Theta(L^{\alpha-2})$. They match only at $\alpha=1$. For $\alpha=0.5$ the nonlinear part fades relative to the linear one at a $1/\sqrt{L}$ rate (Figure 6).
- **"Complete feature learning" is the new requirement.** No layer may be lazy with respect to any of its parameters or earlier ones. Only $\alpha=1$ satisfies it, hence the name.
- **The paper itself calls the theory a heuristic.** It is derived at a fixed token count, while most experiments fix tokens per parameter (p. 7, p. 10).

### Practical extras

The 1/L factor alone isn't the whole recipe. [Table 1 (p. 4)](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=4&rect=107,263,505,513) also rescales these with width and depth:

- the LayerNorm and bias learning rates
- AdamW's weight decay
- AdamW's ε

The authors say these corrections are essential for stable training at $\alpha=0.5$ (p. 2, Figure 7). That makes the comparison fairer to the baseline.

### Results (1.5B non-embedding parameters, 20 tokens per parameter)

- **Validation loss at the best shape** ([Table 2, p. 7](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=7&rect=107,339,505,481)): CompleteP 2.286, µP 2.302, α=0.5 2.326.
- **FLOP savings versus µP:** 11.8% at the best shape and 34.4% for the deepest model (179 layers). These are the "12–34%" in the abstract.
- **Flexible shapes** ([Figure 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don't%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1&rect=108,534,505,698), right; p. 6): the optimal width-to-depth ratio $N{:}L$ stays below about 60. The common rule of thumb is about 100. Under CompleteP, a ratio of 11.8 is still within 1% of optimal loss, against 38.7 for µP. So deep, narrow models stop being penalised.

### Relation to the library

- **Extends [Tensor Programs V (µP)](../notes/Tensor%20Programs%20V.%20Tuning%20Large%20Neural%20Networks%20via%20Zero-Shot%20Hyperparameter%20Transfer.md).** µP gives "tune small, train large" across width. This paper extends it to depth, and µP is the main baseline.
- **Builds on [Decoupled Weight Decay Regularization](../notes/Decoupled%20Weight%20Decay%20Regularization.md).** All runs use AdamW, and CompleteP adds scaling rules for its decay and ε.

### Caveats

- **Evidence base:** the authors' own runs on one dataset (SlimPajama) and one architecture family, up to 1.5B non-embedding parameters.
- **Scaling-law fit:** it uses only 3 points.
- **Variance:** upstream losses report no seeds or variance. At the best shape the margins are small, and the downstream differences are within the standard error.
- **Scope:** "only α=1 works" compares four parameterisations (SP, µP, α=0.5, α=1).

The note has no Q&A entries yet, and nothing new was settled here, so I left it unchanged.
