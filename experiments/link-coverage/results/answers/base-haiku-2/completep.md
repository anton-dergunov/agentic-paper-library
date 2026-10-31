**Main idea:** Deep transformers are hard to tune and train inefficiently under the usual scaling rules. The authors propose a scaling rule, **CompleteP**, that fixes both problems, so you can tune hyperparameters on a small model and reuse them on a deep one, and get more compute efficiency from the result.

**The mechanism.** Each residual block adds its output to the residual stream, and that output is multiplied by a depth-dependent factor. With depth $L$ and a single exponent $\alpha$, the update is $h_{\ell+1} = h_\ell + L^{-\alpha} F_\ell(h_\ell)$ (Eq. 1, p. 2). Prior work offered two candidates, $\alpha = 0.5$ and $\alpha = 1$. The paper's point is that $\alpha$ controls two things at once:

- **Hyperparameter transfer.** The paper finds that only $\alpha = 1$ lets the optimal learning rate and initialization scale carry across depths (2 to 128 layers). Earlier work had argued that transfer across depth was impossible at any $\alpha$ (p. 2).
- **Lazy learning.** With $\alpha = 0.5$, the theory says layers can stay in a regime where each layer learns only features close to its linearization. Depth and nonlinearity then go unused. With $\alpha = 1$, every layer keeps learning non-linear features (p. 2). The authors name this setting CompleteP because it is the unique $\alpha$ that gives complete feature learning as width and depth grow.

**Extra rules.** Making this work in a modern pre-LayerNorm, AdamW transformer also requires rescaling the LayerNorm learning rate, the bias learning rate, AdamW's weight decay and AdamW's $\epsilon$ (Table 1, p. 4). The authors say these changes are essential for stable training at $\alpha = 0.5$ (p. 2).

**Results.**
- A 1.9B-parameter model trained with $\alpha = 1$ saves 11.8% of FLOPs over µP at the optimal shape, and 34.4% at 179 layers (p. 2).
- Revisiting the width-to-depth question, the paper finds that a width:depth ratio near 10 stays close to compute-optimal, where earlier work favoured about 100. CompleteP keeps a wider range of shapes efficient (p. 2, Fig. 1 right).

**Caveats.** The experiments are dense decoder-only language models trained on SlimPajama at 20 tokens per parameter, on Cerebras hardware. The paper leaves out mixture-of-experts and parallel sub-networks (p. 3). The "lazy" argument is a theoretical one in the infinite-limit setting, so the empirical evidence carries most of the weight.

Related in this library: this sits in `deep-learning/optimizers-and-schedules/`, next to the µP-style hyperparameter-transfer work. I haven't checked the other papers in the area, so I can't say how it compares with them yet.
