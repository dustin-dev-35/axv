---
title: "Your test rows are a row count, not an evidence count"
slug: overlapping-eval-windows-are-not-independent-tests
arxiv_id: 2609.30721
arxiv_version: 1
read_date: 2026-09-28
confidence: medium
experiment_status: verified (partially)
section_ids:
  - tldr
  - what-advanced
  - how-it-works
  - roads-not-taken
  - evidence-strength
  - what-axv-did
  - links
---

# Your test rows are a row count, not an evidence count

**Paper:** _When 10,000 Windows Are Not 10,000 Tests: Auditing Statistical Confidence in
Sliding-Window Time-Series Classification_ — Xinze Shi, Litian Zhang and Binrui Shi,
[arXiv:2609.30721v1](https://arxiv.org/abs/2609.30721v1) (ICTAI 2026)
**Read:** 2026-09-28 · **Confidence:** medium · **Experiment:** verified (partially)

<a id="tldr"></a>
Sliding-window classifiers are evaluated on thousands of overlapping windows, and
subject-disjoint splitting does not make those windows independent. At 75% overlap the paper
measures **16.9% Type-I error against a 5% nominal**, so a nominal 5% interval rejects a true
null one time in six. The advance is large in kind and narrow in scope: a reporting practice,
not a model, on two wearable datasets. The caveat that governs everything: every headline
number is conditional on a data-generating process the authors do not release. We re-ran the
estimator across that unpublished parameter and got IID Type-I anywhere from **0.069 to 0.210**
at the same overlap. The direction is robust. The numbers are not portable.

<a id="what-advanced"></a>
## What advanced

The baseline is not a model but a *reporting practice*: a paired Accuracy-difference interval on
pooled i.i.d. standard errors. The entire delta is in the uncertainty, not the point estimate.
At 75% overlap, controlled calibration gives **16.9% Type-I error for IID against 7.2% for
session-centred Bartlett-HAC** at a nominal 5% — a **3.4× anti-conservatism reduced to 1.4×**.
Table IV has the HAC interval **1.22×–1.66× wider**: WISDM 5 s 0.510 → 0.668 pp, WISDM 10 s
0.743 → 0.906 pp, HARTH 10 s 0.520 → 0.862 pp. Test-window counts grow **3.93×–3.97×** from 0%
to 75% overlap while variance-equivalent information grows only **1.75×–1.94×**.

The second and larger delta is that the choice of *metric* flips the conclusion. Table VI,
HARTH at 75% overlap: paired Accuracy difference **+0.07 pp [−0.36, +0.50]**, containing zero,
while Macro-F1 on the same frozen predictions is **−13.21 pp [−16.03, −10.39]** favouring
MiniROCKET. Two flags: it appears **only on HARTH**, one of two datasets, and the frozen
default bandwidth was chosen using calibration that **reused the same seeds** — the authors
state independence from the reported calibration "is not established". Their own re-seed moved
HAC 7.2% → 7.9% and 8.85% → 6.7%, a 2.12 combined-MCSE disagreement they keep as two outcomes
rather than resolve.

<a id="how-it-works"></a>
## How it works

Overlapping windows share raw samples, so adjacent predictions are mechanically correlated, and
errors persist within a recording and a subject. The paired contrast `D = C_A − C_B` is
therefore a *dependent* sequence, not independent draws: nominal window count is a row count,
not an evidence count. The paper turns that into a rule — declare the target population, choose
the aggregation rule, identify the highest independent unit, then pick the matching estimator.
**Evidence label: partially-evidenced.** The centring and bandwidth machinery is genuinely
isolated and ablated: §V-B decomposes the width ratio into a centring ratio times a dependence
ratio (0.83 × 1.11 = 0.92 for WISDM 5 s, 0.81 × 1.03 = 0.84 for WISDM 10 s), and a Macro-F1
influence-function interval is checked against a 1,999-replicate session-aware block bootstrap
with near-identical results. What is *not* demonstrated is the calibration of the frozen default
bandwidth, and the paper says so.

<a id="roads-not-taken"></a>
## The roads not taken

**1. A moving-block or stationary bootstrap on the window contrast, instead of HAC.** *Pros:*
resampling validity for stationary dependence is a weaker assumption than getting the lag
structure right; block length is one knob rather than a bandwidth-plus-centring choice; it
extends to any metric including Macro-F1 with no separate influence-function construction,
which removes the largest single piece of machinery in the paper. *Cons:* pointwise asymptotic
validity converges slower than the closed-form Bartlett estimator, so at the fixed-record
target with few contributing sessions it can be materially anti-conservative — and the paper
itself reports that its multistage bootstrap is "retained as a diagnostic because pilot
calibration found it over-conservative for the fixed-record target", which is evidence against
this route in exactly the regime that matters here. It is also inference, not measurement: the
paper reports no head-to-head block-bootstrap calibration at that target. *Why not chosen:*
the authors needed a closed-form width per target so the audit can emit a comparable interval
per row of the results table, and §IV-A's own pilot result gives them a concrete reason to
prefer HAC. *Cost to test:* one simulation arm per overlap, about 15 minutes on the same CPU
rig used here. *Would it have won:* **maybe** — likely wins on Macro-F1, plausibly loses on the
fixed-record target where the paper already saw the bootstrap under-cover.

**2. Aggregate to the highest independent unit first and skip the variance estimator entirely.**
Compute one number per session and per subject, then run ordinary inference on those. *Pros:*
this is the paper's own new-subject target, and our run shows it is by far the most robust arm
in the whole design — equal-subject paired inference stayed at **0.023–0.044** Type-I across
every overlap and every dependence strength, and at **0.032** under the heterogeneity that
wrecked everything else. It is the cheapest rule to state, the easiest to audit, and the least
dependent on bandwidth. It needs no assumption about the *shape* of within-session dependence,
only about the number of clusters. *Cons:* it throws away within-session information, so it is
strictly less powerful per unit of compute — the paper's percentile bootstrap over 22 subject
clusters is visibly noisy and §VII concedes that HARTH's 22 clusters "limit the reliability of
sandwich and percentile-bootstrap intervals". With AXV's 3 seeds there are 3 clusters, below
the point where any cluster-robust interval is trustworthy at all. *Why not chosen:* inference,
not fact; the authors want to answer the fixed-record question too, and aggregating to subjects
does not answer it. *Cost to test:* zero — the estimator is already implemented and measured in
this run. *Would it have won:* **yes for AXV's actual protocol, no for the paper's stated
scope** — and that split is the finding, not a hedge.

**3. More independent units at the same cost.** AXV buys 3 seeds; three sessions or
checkpoints from the same run are the same dollars and are not independent in the way a new
seed is. *Pros:* attacks the cluster count directly, which is the binding constraint — the
equal-subject arm's power is set by the number of clusters, and checkpoints are free once the
pod is up. *Cons:* training-set randomness is not propagated across overlapping folds, and the
paper explicitly declines to treat five out-of-fold folds as five inference units; adjacent
checkpoints are *more* autocorrelated than adjacent windows, so the correction is harder, not
easier. *Why not chosen:* not discussed by the paper; it is a budget question, not a statistics
one. *Would it have won:* **no** — it buys correlated units and then pays the HAC correction on
top, which is strictly worse than buying independent ones.

<a id="evidence-strength"></a>
## How strong is the evidence

**Most likely way the claim is wrong:** the headline factors — 16.9%, 7.2%, 1.75×–1.94×,
1.22×–1.66× — are all conditional on a data-generating process the authors do not release. Our
sweep produced IID Type-I anywhere from **0.069 to 0.210** at 75% overlap depending on a
persistence parameter the paper never states. Quoting 16.9% as "the" overlap penalty quotes one
point in a range the paper has not bounded. Second: the metric-flip result is single-dataset.
Third: the real-data intervals come from *frozen* prediction files, so there is no training-seed
variance at all — which removes noise and also removes the only way the result could be checked
against a different fold assignment.

**Ablations: strong and unusually candid.** Centring-versus-dependence decomposition, Macro-F1
influence function versus block bootstrap, per-session bandwidth, HAC bandwidth grid, WISDM
length sensitivity, common-session recomputation, class-level breakdown, nested-overlap purity
check. The authors added an independently seeded post-review calibration *after noticing their
own seed reuse* and reported it against themselves, and they retain two disagreeing estimates
rather than averaging them.

**Baselines: the right posture, honestly declared.** The estimators are classical (Newey–West
1987) and the paper is explicit that its contribution is "the executable claim-to-analysis
mapping, not a new generic variance estimator"; Table I records "not shown" for Binette–Reiter
2024, Hong et al. 2026 and Anglin 2026. Breadth is the limit the paper names itself: two
datasets, two classifier families.

<a id="what-axv-did"></a>
## What AXV did about it

**verified (partially)** — the paper's operational claim is real and AXV should adopt the rule,
but AXV should not quote the paper's numbers. No pod: the claim is about a variance estimator on
binary paired outcomes, not GPU-bound, so provisioning the PRO 6000 MIG 24GB at $0.59/hr would
have spent budget to compute the same number more slowly. **$0.00 of $3.25; $3.25 remaining.**
Harness `train.py` at `experiments/runs/verify-2609.30721-typei-20260928/`, numpy and scipy,
`harness_commit` null and `diff.patch` empty by design. **63 conditions** (3 overlaps × 5
persistence levels × 3 seeds, plus 2 heterogeneity arms × 2 persistence × 3 overlaps × 3 seeds,
plus 15 information-growth); M = 1,000 Monte-Carlo sets per condition. Metric: Type-I error at
5% nominal. Baseline: none, `leaderboard.jsonl` was empty at 0 bytes. Spread at rho = 0.99, 75%
overlap: IID **0.199 / 0.218 / 0.212**, HAC 0.081 / 0.080 / 0.087, equal-subject 0.027 / 0.039
/ 0.029. Eight of eight pre-registered prediction checks hold; the latent is Gaussian and
thresholded, not Bernoulli-AR, so absolute values are conditional on that choice.

**Leaderboard warnings, verbatim:** "Cohort is CPU-only. This record is NOT comparable with any
runpod-pro6000-mig24gb-torch280-cu130 record and must not be used as its baseline." / "Not a
replication of the paper's simulation. The paper does not release its DGP parameters; the
estimator is the paper's and the data-generating process is AXV's, swept over dependence
strength rather than tuned to match the paper's numbers." / "n=3 seeds. Each seed is an
independent repetition of the full 63-condition Monte-Carlo study, not one draw from a single
study."

**What it confirmed.** IID Type-I at 75% overlap ran **0.069 (rho = 0) to 0.210 (rho = 0.99)**
against a 0.05 nominal, while session-centred HAC ran **0.036 to 0.083** over the same surface,
and the IID−HAC gap was non-negative at every overlap and every persistence level. Nominal row
growth 3.97×; information growth **2.81×** with mechanical overlap alone and **2.62×** at
rho = 0.99 — mechanical overlap costs 41% of the nominal information and AR(1) persistence
adds only 7% more.

**The finding the paper does not make.** Under a shared subject/session *difficulty* shift, IID
Type-I was **0.059** — a shared difficulty shift moves both arms together and cancels in
`C_A − C_B`. Only when the heterogeneity acts on the **model-pair difference** does misalignment
appear, and then severely: **IID 0.776, HAC 0.800, equal-subject 0.032**. Both window-level
estimators are catastrophic, and the session-centred fix is no better than plain IID. Since
AXV's `delta` is always a paired contrast, AXV is largely protected against the shared-difficulty
form and exposed to the differential form: **safe when both arms see the same data, seed family
and difficulty, unsafe when something makes one arm systematically easier on a subset of
runs.** That is the clause most likely to be violated by accident, and the argument for
aggregating to the independent unit as AXV's default.

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.30721v1> · <https://arxiv.org/pdf/2609.30721v1>
- AXV memo: `corpus/2609.30721.md` in `dustin-dev-35/axv` — seven of seven sections, nothing
  omitted.
- AXV run: `experiments/runs/verify-2609.30721-typei-20260928/`, records in
  `experiments/leaderboard.jsonl`.
- Related AXV posts: none yet. This is the first post in the corpus.
