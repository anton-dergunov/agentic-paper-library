The paper's main idea is a single change to how transformer residual blocks are scaled with depth, plus a few matching rescalings, that lets hyperparameters transfer across depth and keeps every layer learning features rather than sitting in a near-linear "lazy" regime. The authors call this parameterisation **CompleteP**. [Abstract, p. 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don%27t%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1)

The problem they address:

- **Hyperparameter transfer fails with depth.** Under some parameterisations, the optimal learning rate and init scale found on a small model don't carry over to a deeper one, so you either re-tune at scale (expensive) or train sub-optimally.
- **Transfer alone isn't enough.** Even when hyperparameters transfer, some parameterisations leave layers in the lazy regime, where each layer only learns features close to its linearisation, so depth and nonlinearity go largely unused.

The mechanism is the residual scaling. Each block is added to the residual stream as h_{ℓ+1} = h_ℓ + L^{−α} F_ℓ(h_ℓ), where L is depth and α ∈ [0.5, 1] (Eq. 1, [p. 2](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don%27t%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=2)). The authors compare the two candidates from prior work, α = 0.5 and α = 1, and find α = 1 is consistently more compute-efficient. CompleteP is α = 1 together with rescalings of LayerNorm, bias learning rates, AdamW's weight decay and AdamW's ε.

Headline results (all on Cerebras CS-3):

- Only α = 1 transfers the learning rate and init standard deviation across depth from 2 to 128 layers.
- A 1.9B-parameter model with α = 1 saves 11.8% FLOPs over µP at its optimal shape and 34.4% for a 179-layer model.
- It supports a wider range of width-to-depth ratios at similar compute efficiency.

I read only page 1 (abstract and introduction), so the claim that α = 1 is the unique choice giving complete feature learning rests on Section 6, which I haven't checked. The paper is also marked `type: method` in the library. There is no note for it in `notes/` yet.
