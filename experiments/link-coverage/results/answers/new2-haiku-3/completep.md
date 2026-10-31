The paper's main idea is a new way to scale transformer hyperparameters when you make the model deeper, which the authors call **CompleteP**.

**The problem.** A "parameterization" is the rule for how learning rate and other hyperparameters should change as the model grows. Under the usual rules, the best learning rate found on a small model does not carry over when depth changes, so you either re-tune at each size (expensive) or accept worse training. Even where the learning rate does transfer, the authors argue some rules put layers in a **lazy regime**: each layer learns only features close to its linearization, so the extra depth and nonlinearity go largely unused ([p. 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don%27t%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1)).

**The contribution.** CompleteP is a parameterization that does both at once:
- the optimal base hyperparameters stay stable as depth grows, so you tune once on a small model;
- every layer keeps learning non-lazily, so depth is actually used ([p. 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don%27t%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1)).

**Why it matters for compute.** It keeps a wider range of width-to-depth ratios compute-efficient, so you can choose shapes that suit your hardware or constraints. The abstract reports 12–34% compute-efficiency gains over the prior state of the art ([p. 1](http://pdf.invalid/deep-learning/optimizers-and-schedules/Don%27t%20be%20lazy.%20CompleteP%20enables%20compute-efficient%20deep%20transformers.pdf?page=1)). All experiments ran on Cerebras CS-3 systems, and a minimal implementation is linked from the abstract.

This answer rests only on the abstract and the first-page summary. I haven't read the body for the derivation, the exact scaling rule, or the experiment tables, and there is no note for this paper in `notes/` yet. If you want the mechanism itself, I can read pages 2 onward and write it up.
