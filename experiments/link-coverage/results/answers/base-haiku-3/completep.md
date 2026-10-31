**Main idea:** the paper asks how a transformer's hyperparameters should change as you make it deeper, and gives a rule (CompleteP) that makes the learning rate and init carry over from small models to large ones, while keeping every layer actually learning. The authors report 12–34% compute savings over µP at 1.9B parameters (p. 1; p. 2).

**The problem.** µP already lets you tune on a small model and reuse the settings when you widen it. Depth is harder. Each residual block adds its output to the stream, and the paper scales that output by L^{-α} (Eq. 1, p. 2). The two candidates are α = 0.5 (the standard choice in prior work) and α = 1.

- **Transfer:** with α = 0.5, the best learning rate and init shift as depth grows, so you must re-tune at each depth. With α = 1, the L = 2 settings stay near-optimal up to 128 layers (Figures 2–3, p. 5). The transfer evidence is shown only in figures.
- **Laziness:** the authors argue that at α = 0.5 the blocks can end up close to their linearisation, so depth and nonlinearity go unused. Their definition is in the note's Q&A-free digest (p. 9, Eq. 4), and the argument is a heuristic toy-model derivation (p. 7, p. 10).

**The rule.** Setting α = 1 gives "CompleteP". For pre-LN transformers trained with AdamW, the paper also rescales the learning rates of hidden, bias and LayerNorm parameters, AdamW's ε, weight decay, and the unembedding (Table 1, p. 4). It calls the LayerNorm, bias and ε corrections essential for stability at α = 0.5 (p. 2, Figure 7).

**Results.**

- At 1.5B non-embedding parameters, the 11.8% FLOP saving over µP comes from the compute-optimal shape (N = 1984, L = 32). The 34.4% saving comes from the 179-layer model (Table 2, p. 7).
- CompleteP keeps N:L ≈ 11.8 within 1% of compute-optimal loss, where µP needs N:L ≈ 38.7 (p. 6, Figure 4f). So you can pick deeper, narrower shapes without losing efficiency.
- At 200 tokens per parameter, CompleteP has the lowest loss in all four settings in Table 3 (p. 7). The margins at the optimal shapes are small, and no variance is reported.

**Caveats.**

- One dataset (SlimPajama), one architecture family, and four parameterisations compared.
- Seed counts and run-to-run variance for the upstream losses are not in the main text.
- At the optimal shape, several downstream tasks do not favour CompleteP, and the differences are within standard error (p. 7).
- The scaling-law fit uses only 3 points.
- The paper's own notes give inconsistent exponents for the learning rate (p. 8 vs p. 9).

**Relation to the library.** This extends µP from width to depth ([[Tensor Programs V]], in the library, uses µP as the baseline here), and all of its training uses AdamW with decoupled weight decay.
