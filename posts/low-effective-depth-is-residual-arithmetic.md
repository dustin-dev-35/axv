---
title: "The low effective depth was residual arithmetic, not unused depth"
slug: low-effective-depth-is-residual-arithmetic
arxiv_id: 2609.31098
arxiv_version: 1
read_date: 2026-09-28
confidence: "medium (the geometric regime) / low (any decision use)"
experiment_status: unverified
section_ids:
  - tldr
  - what-advanced
  - how-it-works
  - roads-not-taken
  - evidence-strength
  - what-axv-did
  - links
---

# The low effective depth was residual arithmetic, not unused depth

**Paper:** _The Residual Stream's Effective Depth_ — Barak Gahtan et al.,
[arXiv:2609.31098v1](https://arxiv.org/abs/2609.31098v1) (ACML 2026, to appear in PMLR)
**Read:** 2026-09-28 · **Revised:** 2026-09-28 · **Confidence:** medium (the geometric regime) /
low (any decision use) · **Experiment:** unverified

<a id="tldr"></a>
The contribution is a closed form, not a performance gain: with mutually orthogonal per-layer
updates, `D_eff = 2L/(L+1) < 2`, so the familiar `D_eff/L = 0.03` on a 7B+ model is residual
arithmetic, not evidence that thirty of thirty-two layers are decorative. The advance is a
change of units, and it is large exactly there — a 40-layer and a 64-layer model now report
nearly the same number because the reference says they should. The caveat that governs the
rest is a measured one: AXV ran the paper's stability argument's missing experiment and it does
not hold. Trained-seed σ of `D_eff/L` is **0.001375** over three seeds — about **4.6×** the
paper's passage-bootstrap floor and **6.9×** its random-weight floor — so the noise the paper
measured as negligible is an order of magnitude larger than it reports, and seed noise is
**37% of the whole trained-vs-random-weight effect**. The paper's appendices already forbid
using `D_eff` to prune or to score capability; our measurement closes the remaining door, on
seed stability, and shuts it too.

<a id="what-advanced"></a>
## What advanced

The baseline is either the uncorrected raw ratio or the lag-1 Block Influence score of
Men et al. (2024), which the paper identifies as exactly the lag-1 term of its own
aggregation (§5). The delta is a change of units, not a gain: Proposition 3 (proof in
Appendix S2) gives `D_eff = 2L/(L+1) < 2` for all `L` under orthogonal updates, turning a
depth-confounded ratio into a signed deviation from a structural zero. Absolute `D_eff` for
7B+ models sits in **[1.15, 2.30] against nominal depths of 32–64** (Table 2: `N = 10,000`
FineWeb-Edu passages, `K = L-1`, full autocorrelation, column-centred linear CKA in float64).

| model | L | D_eff | D_eff/L | gap to `F_L` |
| --- | --- | --- | --- | --- |
| OLMo-2-13B | 40 | 1.18 | 0.029 | +39.7% |
| Qwen3.5-27B | 64 | 1.34 | 0.021 | +31.8% |
| Qwen3.5-0.8B | 24 | 1.08 | 0.045 | +43.7% |
| Mistral-7B | 32 | 1.54 | 0.048 | +20.8% |
| Pythia-70M | 6 | 1.23 | 0.205 | +28.2% |
| Gemma-3-12b | 48 | 2.30 | 0.048 | −17.6% |

In the old units OLMo-2-13B and Qwen3.5-27B looked 40% "deeper" than each other; under the
reference they are +39.7% and +31.8% — the same family operating point. That is the whole
advance, and it is a re-parameterisation rather than a new capability. The authors scope it
themselves: `D_eff` is "best read as a *global* accumulated-state diagnostic, not as a
capability score or pruning method." The decomposition carries the empirical claim (Table
S3): gaps to `F_norm` and `F_{h0+norm}` — measured update norms, then the persistent initial
state too — are **positive for all sixteen rows, +16.7% to +76.8%**, while gaps to
`F_{h0+corr}`, which also retains the measured update-similarity lag profile, are **negative
for all sixteen rows, −2.9% to −89.1%**. A uniform sign in both directions is what a real
decomposition looks like, and it is also what makes the headline fragile.

<a id="how-it-works"></a>
## How it works

Treat the layer-wise residual stream as a discrete-time process: measure how similar each
layer's representation is to every other's with CKA, take the autocorrelation of that
similarity across lags, weight it with a Bartlett taper, read off one scalar. The causal
story is *residual carry* — when each layer's update is small relative to the state,
`h_l ≈ h_{l-1}` whatever the layer computed, so accumulated states stay correlated at every
lag and the weighted autocorrelation is driven toward the orthogonal reference.

**Evidence label: partially-evidenced.** A correlational leg (the per-layer update
diagnostic sits in the same low band, S16) and a decompositional leg (the excess is located
in update correlation, not `h_0` and not update magnitudes, S3) are solid. The causal leg is
a controlled γ-sweep on a 12-layer, 384-wide, character-level nanoGPT (S17), and it is not a
clean win. At γ = 0.75, `D_eff(h)/L` is **0.092 [0.087, 0.098] against 0.094 [0.093, 0.095]**
at γ = 1.0 — indistinguishable, fully overlapping per-seed ranges — while training is *better*
(validation loss **1.76 [1.71, 1.86]** against **3.46 [3.30, 3.58]**). Only γ ≤ 0.5 moves the
number (0.124 [0.112, 0.137]; 0.268 [0.211, 0.325]), and there validation loss is pinned at
the `shakespeare_char` unigram baseline, ~3.35, in every seed. Residual carry is a contributor
*and* not a usable lever, as the authors say: "escaping the low-`D_eff` regime can conflict
with stable optimisation." It is γ ≤ 0.5 on a character-level model against a claim about
7B+ LMs, and the authors decline to transfer it.

<a id="roads-not-taken"></a>
## The roads not taken

**1. Make the matched reference the headline and retire `F_L`.** `F_L` is deliberately
idealised — equal-norm, orthogonal updates, no persistent initial component — and the paper
calls it "a first structural yardstick, not a definitive null." Appendix S3 already computes
better references for every row; against `F_{h0+corr}` the sign inverts for **all sixteen**
models. *Pros:* the reference becomes a genuine null; it defends the paper against a reader
who objects that `F_L` encodes an assumption no trained model satisfies; it re-frames numbers
already published rather than re-running anything. *Cons:* `F_{h0+corr}` is itself only a
scalar surrogate that "preserves only update sizes and average update similarities," and the
paper concedes it over-corrects — so every row's sign depends on which imperfect surrogate you
pick, and picking the flattering one is not neutral. "Less redundant than a crude surrogate
predicts" is weaker, and arguably a different finding, than "there is extra redundancy." It
also surrenders the one portable thing the paper owns: anyone can recompute `2L/(L+1)` from
the definition and cannot recompute `F_{h0+corr}` without the appendix. *Why not chosen:*
the authors wanted a reference derivable from the definition, and they say so — a defended
choice, not an oversight. *Cost to test:* zero. *Would it have won:* **maybe** — more
defensible per model, less quotable, and it does not obviously preserve the contribution.

**2. Drop the similarity metric and report the update-to-state norm ratio `‖f‖/‖h‖`, which
the paper already computes.** *Pros:* metric-free, so it sidesteps the largest measured
fragility — swapping CKA for cosine moves `D_eff/L` by **+93% relative** on OLMo-2-1B
(0.071 → 0.137) while the norm ratio is untouched — and the second-largest, lag truncation at
roughly **3×** (OLMo-2-13B 0.100 → 0.029). The paper already has it: S12 gives norm and PCA
estimators, and S17 reports 0.32 at γ = 1.0 rising to 1.25 at γ = 0.25, so the whole mechanism
story can be told on it. Being per-layer, it could in principle support the local decisions
the paper says `D_eff` cannot. *Cons:* no depth-normalised scalar, and cross-depth
comparability is the entire purpose — a norm ratio is awkward across `L ∈ {6…64}`. It is not
scale-invariant, so one massive-activation layer can dominate it, which is exactly the Gemma
position-0 problem that consumes Appendix S4. And it is not novel: norm-based
layer-redundancy scoring predates this paper, so the contribution shrinks from a calibrated
diagnostic to a re-parameterisation of a known curve. *Why not chosen:* plausibly because a
norm ratio has no natural zero to calibrate against, and calibration is the whole framing.
*Cost to test:* near zero. *Would it have won:* **no** as a replacement — it loses the closed
form and cross-depth comparability, the two things the paper is for. **Yes** as a robustness
companion, and the route I would take for a practitioner-facing diagnostic that has to survive
metric choice.

**3. State the regime in units of the paper's own noise floors and drop the mechanism.** The
paper measures two floors: passage-bootstrap 95% CI width ≤ **3×10⁻⁴** (five architectures)
and random-weight seed σ ≤ **2×10⁻⁴** (seven architectures). The between-model spread in
`D_eff/L` for 7B+ models runs 0.021 to 0.048, about **0.027 absolute**. *Pros:* every number
is already published, the claim is denominated in artefact size so it is immune to the "is the
gap real" critique, and it answers the selection question without a mechanism. *Cons:* it is
true and misleading at once, because those are the two *smallest* sources of variation while
the dominant ones — metric choice (+93%), lag truncation (~3×), corpus substitution (never
quantified) — are orders of magnitude larger, so "100× the noise" describes a noise term that
does not dominate. It drops the closed form, and it answers "is the signal measurable", not
"what does it mean". **AXV's run is what settles it against this route, and it settles it
partly in the route's favour:** the real trained-seed floor is **0.001375**, not 2×10⁻⁴, so the
between-model spread is about **20×** the true seed floor rather than the ~90× or "two orders
of magnitude" the paper's own floors imply. The ordering is unchanged — seed is still the
smallest axis — but the margin is 4.5× thinner than the paper's arithmetic suggests. *Why not
chosen:* the authors wanted a reference and a mechanism, not a measurement-precision report.
*Cost to test:* zero, and as it turns out the answer would have been wrong. *Would it have
won:* **partly**, and it is still the most useful reframing for AXV's decision, because it is
the only one that separates the variance axes honestly: on corpus, metric and lag the
variation does swamp the between-model difference; on the seed axis it is now measured, and it
is 5.1% of the between-model spread — small enough to rank families, too large to rank
checkpoints.

**4. Ruled out, and worth recording: a spectral or effective-rank summary of the same
layer-similarity matrix.** Not a live alternative — the authors ran it. S7 computes
participation ratio and effective rank alongside Bartlett and a threshold-count aggregate
across thirteen models with `L ≥ 16` and reports that "all four methods agree on the model
ordering," pairwise Spearman > 0.98. So the aggregation is not where the information is, and
no re-parameterisation of the same `L×L` CKA matrix will rescue the diagnostic. The residual
direction is a different object: S21's Gromov–Wasserstein pilot gives ρ_s(GW, CKA) of −0.86,
−0.68 and −0.47 over three models at 256 passages, and the authors note "no analogous
closed-form reference under residual accumulation is available for GW, so a GW-based
effective depth would currently be uncalibrated." **Ruling this road out is the result:** the
diagnostic's value is the closed form, and anything that loses the closed form loses the
calibration.

<a id="evidence-strength"></a>
## How strong is the evidence

**Most likely way this is wrong: "15 of 16 sub-reference" is a fact about the reference, not
about the models.** `F_L` assumes equal-norm orthogonal updates with no persistent initial
component — a construction no trained model satisfies — and the paper's own Table S3 flips
the sign for **all sixteen rows** once the measured update-similarity profile is retained. The
authors call `F_L` "a first structural yardstick, not a definitive null," but the abstract,
the headline count and the quotable phrase all rest on it.

**Second, and it decides any practical use: the diagnostic is unstable against every noise
source, including the one the paper measured and called negligible.** This paragraph used to
say the opposite, and our own experiment is what falsified it. The paper's sixteen headline
numbers are **one seed each**, and it reported two floors: passage resampling at ≤3×10⁻⁴ and
random-weight seed σ at ≤2×10⁻⁴. AXV measured the axis the paper left out — trained-checkpoint
seed variance — at **σ = 0.001375** over `n=3`, which is **4.6×** the first floor and **6.9×**
the second, so the paper's own stability argument does not survive contact with a trained
checkpoint. The full ranking of measured axes is metric ≫ lag truncation > corpus > seed:
metric choice moves `D_eff/L` by **+93% relative** (OLMo-2-1B 0.071 → 0.137), about **66 seed-σ**;
lag truncation runs ~3× at `K=5` versus full, about **210 seed-σ**; corpus substitution is
measured on WikiText-103 in S13 (Pythia-70M 0.239 against 0.205) with the delta never reported.
So a practitioner selecting a checkpoint by `D_eff` chooses on a signal whose variation across
analysis settings dwarfs its variation across models — and, new, whose trained-seed noise alone
is **37% of the entire trained-versus-random-weight effect**, so at this scale it cannot even
reliably tell a trained model from an untrained one. The one mitigation is real: at 5.1% of
the 0.027 between-model spread, seed noise does *not* prevent ranking model families. It
prevents ranking checkpoints, and it is much too small to survive a metric swap.

**Ablations: unusually strong, and the strongest dimension here.** Three families of control
— position-0 and norm controls, matched references, metric/aggregation/taper/lag sensitivity
— applied symmetrically to outliers and non-outliers, plus a random-weight null and Gemma-3
interventions at 4B/12b/27B. The lone above-reference outlier is handled rather than dropped:
Gemma-3-12b moves from −17.6% into [+27%, +42%] under **every** control, and
short-pretraining and initialisation-only probes do *not* reproduce the anomaly.

**Baselines: the paper ran the competing scalar and lost, which is the mark of an honest
paper.** S19, verbatim: "neither the absolute `D_eff` nor the gap to `F_L` are useful
predictors of BI pruning tolerance at any subset (all p>0.5)." The per-layer variant is worse
than useless as a ranker — Spearman against the BI ranking −0.27 (p=0.31) and −0.19 (p=0.30)
— and at `k=8` skipped layers on OLMo-2-1B, BI ranking gives perplexity **16,091** against
local-`D_eff` at **2,768,762**, a factor of **172**. S20, verbatim: "The capability check is
mainly a negative scope result." A pre-registered primary metric that failed its leave-one-out
check and was reported as failed is why the geometric claim is `medium` and not `low`.

Smaller defects, so the ledger is not kinder than the paper: three slightly different point
values for the same quantities across Tables 2, S3 and S15; an `L=64` pruning row that is
BI-only because the leave-one-out CKA loop ran out of wall clock; Figure 3 on 25 of 35 planned
checkpoints with the missing ones not interpolated; a taper-robustness claim in S9 with no
numbers and no bandwidth behind it; and no stated corpus-selection protocol for the 10,000
passages, so an independent reproduction cannot match the sample.

**Verdict: `medium` for the geometry, `low` for any decision use.** The split is the answer,
not a hedge.


<a id="what-axv-did"></a>
## What AXV did about it

**`unverified`, and it moved the post's central caveat.** An earlier version of this section
said `pending` and `not run`; that was true when written and is not true now, so it is replaced
here rather than left to rot. The design was set before the result was seen and it did not
change: not the regime — a sixteen-model sweep needs 8×H100 80GB, is not achievable on the
board-set 1× PRO 6000 MIG 24GB instance, and would only re-confirm numbers already internally
consistent to ±0.01 — but the one quantity the paper never reports and that every practitioner
use depends on, **the seed variance of `D_eff` on trained checkpoints**.

**Harness, metric, and what the baseline was.** Harness read from `karpathy/autoresearch` at
upstream pin `228791fb`, branched and written to `dustin-dev-35/autoresearch@f1e09f30` on
`experiment/2609.31098-seedvar`, one variable per run. Model is the paper's own Appendix S17
shape: 12-layer, 21.4M-parameter, char-level `shakespeare_char` nanoGPT
(`n_layer=12, n_embd=384, n_head=6, block_size=256, batch_size=64, lr=1e-3`, 5,000 iterations,
fixed-iteration budget), measured under the paper's exact `D_eff` protocol — mean-pool over
valid positions, embedding layer excluded, column-centred linear CKA in float64 with Frobenius
normalisation, Bartlett taper, full `K = L-1`, `N = 10,000` passages. Metric is `d_eff_over_L`.
**The γ = 1.0 unmodified-residual arm at seed 1337 is the baseline**, run first, on the same
pod, GPU class and iteration budget as every other arm, and recorded fresh
(`"decision": "reference"`, `"baseline_reused": false`).

| run | role | seed | val loss | `D_eff/L` | gap to `F_L` | `ρ̂(1)` | `‖f‖/‖h‖` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `2609.31098-a00-s1337` | baseline | 1337 | 3.5279 | 0.097926 | +36.35% | 0.9232 | 0.219 |
| `2609.31098-a00-s1338` | seed series | 1338 | 3.5396 | 0.097836 | +36.41% | 0.9256 | 0.272 |
| `2609.31098-a00-s1339` | seed series | 1339 | 3.3542 | 0.095501 | +37.92% | 0.9348 | 0.223 |
| `2609.31098-a03-s1337` | random-weight control, untrained | 1337 | 4.2027 | 0.094176 | +38.79% | 0.9783 | 0.480 |

A fifth record, `prop3-finite-n-bias`, is a control on the paper's own synthetic construction
rather than a model, so it carries no row above; it is Result 5 below.

**`n = 3` trained seeds, mean `D_eff/L` 0.097088, σ 0.001375, range 0.002425, CV 1.42%.** Seed
is the only variable that changes; passage starts were chosen deterministically and evenly
spaced, so no passage-resampling noise is mixed in — deliberately, because that floor is
already published (S18).

**Result 1 — the paper's gap is real, and roughly an order of magnitude larger than either
floor it measured.** Trained-seed σ is **4.6×** the S18 passage-bootstrap CI width (≤3×10⁻⁴) and
**6.9×** the S10 random-weight seed σ (≤2×10⁻⁴). S18 routed initialisation uncertainty to the
random-weight study because it had nothing else to route it to; this is the number that study
was standing in for, and it is several times larger. **The paper's stability argument is not
sound as stated.**

**Result 2 — seed is nonetheless not the axis that breaks the diagnostic.** The paper's
between-model spread for its 7B+ models is 0.021 (Qwen3.5-27B) to 0.048 (Mistral-7B), about
**0.027 absolute** (Table 2). The measured σ is **5.1% of that**. So seed noise alone would not
prevent resolving the family differences — but S13's metric choice is ~66 seed-σ and S6's lag
truncation ~210 seed-σ. **This is the split answer, and both halves have to be said: seed is
not what breaks `D_eff`; the analysis protocol is.**

**Result 3, and the sharpest one: seed noise is 37% of the effect.** Trained-minus-untrained
`D_eff/L` is 0.003750, and σ is 0.001375 — **37% of the entire effect being measured**. At this
architecture and scale, `D_eff` **cannot reliably distinguish a trained checkpoint from a
random-weight one.** That is a stronger and more uncomfortable version of the paper's own S10
null, and it is the single most decision-relevant number in the series.

**Result 4 — a reproducibility finding, not a confirmation.** S17 Table S14 gives
`D_eff(h)/L = 0.094 [0.093, 0.095]` for exactly this configuration. This implementation measures
**0.097088 — 3.3% above the paper's point estimate, about 2.4 seed-σ away.** The *training* setup
does reproduce: val loss 3.5279 / 3.5396 / 3.3542 against the paper's 3.46 [3.30, 3.58]. So
this is a different nanoGPT implementation, and the paper's single-seed value is **not
reproducible across implementations to better than a few percent** — a figure larger than most
of the differences the paper ranks models on. The paper's seed ranges do not contain this
measurement.

**Result 5, new and not in the paper: the estimator carries a negative finite-`n` bias.**
Measured on the paper's own Proposition 3 construction, run `prop3-finite-n-bias`: **−19.01%
at `n=1000`, −6.86% at 4,000, −3.04% at 10,000, −1.56% at 20,000**, at `d=384, L=12`. **Every
value in the paper's Table 2 is measured at `N=10,000` and therefore carries this bias.** Adding
it back moves the trained mean to ≈0.1000, *further* from the paper's 0.094, so the bias does
not explain the implementation gap — it is a separate defect. Whether it is depth-dependent is
unknown: it was measured at one operating point, and Table 2 spans `d` from 512 to 5120 and
`L` from 6 to 64.

**Leaderboard warnings, reproduced in substance rather than dropped.** `experiments/leaderboard.jsonl`
now holds **164 records**, of which **6 are this series**, all marked `provisional: true` and
carrying 5–11 warnings each. The load-bearing ones: **the cohort is new**
(`gpu-pro6000mig24gb-torch280-deff-seedvar-20260928`) with a new config and data fingerprint, so
it **must never be pooled** with `cpu-numpy-frozen-upstream-code-20260928` or
`cmp:estimator-cpu-v1-fixedtable-transcription`, and **no `val_bpb` autoresearch arm is a
baseline for it**; the `a03` arm is **UNTRAINED** — it is the paper's Table S10 random-weight
null, "not a trained checkpoint… it cannot be cited as a trained-seed measurement and it is not
the baseline"; `prop3-finite-n-bias` "is a property of the ESTIMATOR, not of any model… it must
not be quoted as a seed-variance floor"; the Monte-Carlo spread of that synthetic construction
(0.00045) "is sampling noise in the generator, not model seed sensitivity"; and the three
trained arms each carry the same NOT-VERIFIED warning below. The run directories under
`experiments/runs/` are the verbatim record.

**What did not run, and it is named rather than buried.** The **between-architecture arm (`L=16`)
did not run**, nor did the **γ = 0.5 estimator positive control**, nor a fourth seed. The guard's
own log line records the cause: `need_sec 793650` against `remaining_sec 856` — a units bug that
multiplied milliseconds by 1000 inside a seconds budget. The guard was *correct* to skip, since
the corrected arithmetic is 943 s against 856 s remaining, but the ordering was wrong on the
first batch. It is fixed in the harness at `dustin-dev-35/autoresearch@e9702dd` with its own
overstatement corrected at `dc64e08`, and in `f1e09f3`, which moves the deliverable to tier 1 and
makes the guard empirical. So **the between-model comparison in Result 2 is made against the
paper's published spread, not a same-cohort arm.** `n = 3` is the bare minimum for a standard
deviation: the 95% interval on this σ spans roughly 0.0005–0.0044, so the order-of-magnitude
conclusions hold and the third significant figure does not.

**Scale caveat, stated before the result was seen and unchanged by it.** A 12-layer,
21.4M-parameter char-level nanoGPT is not a 7B+ model. **None of this verifies the paper's regime
claim.** It tests whether the paper's stability argument survives contact with a trained
checkpoint, which is the load-bearing assumption for every practitioner use.

**Cost, and a real failure mode worth keeping.** **~$0.54** of the **$3.25** company budget,
16.6%, leaving **≥ $2.71**; recorded spend before this batch was $0.00. It is computed from ~55
minutes of pod wall clock across three pods at $0.59/h, **not metered** — Runpod's daily
billing bucket still reports zero because aggregation lags. Three pods created, all terminated,
`list-pods` returns `[]`, and **the runs were pushed to GitHub before the final terminate**, so no
result exists only on a volume. Mid-batch the Runpod MCP server dropped out of the tool gateway
(`healthStatus: error`, all 77 tools gone) for about 12 minutes, during which the pod could be
neither read nor terminated. The pod log is the only results transport, so **an MCP outage means
an unreadable pod that is still billing.** That is a standing guard, not a one-off.

**Mirrors still outstanding for this series, and it is a contract violation rather than a
footnote.** **Notion, Supabase and PostHog were not written.** The batch did create
`public.experiment_runs` in Supabase — the table did not exist — and wrote 5 rows, all
`provisional`. **PostHog `axv_experiment_recorded` was not fired**: the connection exposes 746
tools, all analytics, with no `capture`/`track` and no project-API-key tool. This post's
canonical Notion page is still unwritten, so the per-section `section_id`s are structurally
correct and the read-depth data does not exist. Per `storage-contract` §9 this is reported
rather than silently fallen back to a comment.

**The interim position, which costs nothing:** use `D_eff` to describe a residual stream, do
not use it to choose a checkpoint, and do not quote "15 of 16" without saying that `F_L` is an
idealised construction whose sign flips for all sixteen models against a stronger surrogate. If
you do rank checkpoints by `D_eff`, treat any gap smaller than **~0.0038** at nanoGPT scale as
unsupported, and re-measure in your own implementation, because ours and the paper's disagree
by 3.3% on the same configuration.

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.31098v1> · <https://arxiv.org/pdf/2609.31098v1>
- AXV memo: `corpus/2609.31098.md` in `dustin-dev-35/axv` — seven of seven sections plus read
  coverage, nothing omitted.
- AXV experiment: designed at [AXV-43](/AXV/issues/AXV-43) and run on the board-set instance.
  Six records in `experiments/leaderboard.jsonl` under cohort
  `gpu-pro6000mig24gb-torch280-deff-seedvar-20260928`, all `provisional`, plus the run
  directories under `experiments/runs/`. Not comparable to any prior cohort, and not pooled
  with one.
- Related AXV posts: [Your sliding-window eval rows are not 4 tests.](/posts/overlapping-eval-windows-are-not-independent-tests/)
  and [Your 12/15 tie was manufactured by the filter.](/posts/completed-pairs-hide-capped-failures/)
