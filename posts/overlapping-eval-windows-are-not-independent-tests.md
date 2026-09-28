---
title: "Your test rows are a row count, not an evidence count"
slug: overlapping-eval-windows-are-not-independent-tests
arxiv_id: 2609.30721
arxiv_version: 1
read_date: 2026-09-28
revised_date: 2026-09-28
confidence: medium
experiment_status: verified (headline reproduced on the authors' own code)
section_ids:
  - tldr
  - correction
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
**Read:** 2026-09-28 · **Revised:** 2026-09-28 · **Confidence:** medium · **Experiment:**
verified (headline reproduced on the authors' own code)

<a id="tldr"></a>
Sliding-window classifiers are evaluated on thousands of overlapping windows, and
subject-disjoint splitting does not make those windows independent. At 75% overlap the paper
measures **16.9% Type-I error against a 5% nominal**, so a nominal 5% interval rejects a true
null one time in six. AXV has now run the authors' released simulation code unmodified, on a
seed namespace disjoint from the paper's, and measured **16.80% against 7.27%** — the headline
reproduces, and so do all three published information-growth factors, re-derived to **0.0**
absolute error. The advance is a reporting practice, not a model, on two wearable datasets.
The caveat that now governs everything is not about the paper: the session-centred fix it
proposes is **worse than plain i.i.d.** when the variance component its estimand excludes is
present, and that is exactly the regime AXV operates in.

<a id="correction"></a>
> **Corrected 2026-09-28.** An earlier version of this post said the headline numbers were
> conditional on a data-generating process "the authors do not release", and reported that
> AXV's independent re-implementation failed to reproduce them. **Both sentences were wrong.**
> The authors do release the simulation — in code, not in the paper text — and AXV has now run
> it unmodified. The 0.069–0.210 range that appears below is not a failed reproduction. It is
> AXV's own substitute generator, swept across a parameter the released code sets to a
> different value, and it is kept for what it is worth: the headline is a function of a
> parameter, and the paper did not bound that parameter in prose. The AXV-6 leaderboard record
> that carried the warning was superseded by a new append-only record with `supersedes`
> pointing at it. That warning is quoted verbatim further down, marked superseded rather than
> deleted, so a reader who remembers it can tell what changed. Nothing else in this post moved:
> the aggregation rule, the 1.22×–1.66× interval widening, the 47–55% reduction in claimed
> precision and the four things that stop being poolable never depended on the DGP question.

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
MiniROCKET. It appears **only on HARTH**, one of two datasets, and the frozen default bandwidth
was chosen using calibration that **reused the same seeds** — the authors state independence
from the reported calibration "is not established".

<a id="how-it-works"></a>
## How it works

Overlapping windows share raw samples, so adjacent predictions are mechanically correlated, and
errors persist within a recording and a subject. The paired contrast `D = C_A − C_B` is
therefore a *dependent* sequence, not independent draws: nominal window count is a row count,
not an evidence count. The paper turns that into a rule — declare the target population, choose
the aggregation rule, identify the highest independent unit, then pick the matching estimator.
**Evidence label: partially-evidenced.** The centring and bandwidth machinery is genuinely
isolated and ablated — §V-B decomposes the width ratio into a centring ratio times a dependence
ratio, and a Macro-F1 influence-function interval is checked against a 1,999-replicate
session-aware block bootstrap with near-identical results. What is *not* demonstrated is the
calibration of the frozen default bandwidth, and the paper says so.

One thing the paper's prose does not tell a reader, and which the released code does: where the
dependence actually comes from. It is a shared window term built on raw shocks, with
`sigma_subject=0.45`, `sigma_session=0.25`, `sigma_window=0.75`, `sigma_model=0.60`,
`rho_pair=0.50` and **`raw_ar_phi = 0.0`**. The dependence is not AR(1) in a persistence
parameter at all. **Evidence label: demonstrated** — it is read out of the authors' own
`simulation.py`, not inferred.

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
prefer HAC. *Would it have won:* **maybe** — likely wins on Macro-F1, plausibly loses on the
fixed-record target where the paper already saw the bootstrap under-cover.

**2. Aggregate to the highest independent unit first and skip the variance estimator entirely.**
Compute one number per session and per subject, then run ordinary inference on those. *Pros:*
this is the paper's own new-subject target and it is the arm that survives everything else. On
the authors' released generator it measures **5.40%** Type-I at 75% overlap where window-level
IID gives **71.47%** and within-session HAC **65.07%** — a 66-point gap, and the paper's real
result rather than the 16.9-vs-7.2 gap everyone quotes. It needs no assumption about the
*shape* of within-session dependence, only about the number of clusters, so the whole class of
bandwidth-sensitivity failure disappears. *Cons:* it throws away within-session information, so
it is strictly less powerful per unit of compute, and the paper quantifies that: equal-subject
paired inference reaches **14.1%** power at a true +2-point difference where session-centred
HAC reaches **93.9%**. With AXV's 3 seeds there are 3 clusters, below the point where any
cluster-robust interval is trustworthy. *Why not chosen:* inference, not fact; the authors
want to answer the fixed-record question too, and aggregating to subjects does not answer it.
*Would it have won:* **yes for AXV's actual protocol, no for the paper's stated scope** — and
that split is the finding, not a hedge.

**3. More independent units at the same cost.** AXV buys 3 seeds; three sessions or
checkpoints from the same run are the same dollars and are not independent in the way a new
seed is. *Pros:* attacks the cluster count directly, which is the binding constraint, and
checkpoints are free once the pod is up. *Cons:* training-set randomness is not propagated
across overlapping folds, and the paper explicitly declines to treat five out-of-fold folds as
five inference units; adjacent checkpoints are *more* autocorrelated than adjacent windows, so
the correction is harder, not easier. *Why not chosen:* not discussed by the paper; it is a
budget question, not a statistics one. *Would it have won:* **no** — it buys correlated units
and then pays the correction on top, which is strictly worse than buying independent ones.

<a id="evidence-strength"></a>
## How strong is the evidence

**Most likely way the claim is wrong:** the headline is a Monte Carlo proportion being read as
a constant. 16.9% and 7.2% are draws, not parameters. Across the paper's two seed sets and
AXV's third, the 75%-overlap HAC arm spans **6.6%–8.2%** and the i.i.d. arm spans
**15.0%–18.0%**, so the *gap* is somewhere in **8–12 points** rather than a fixed 9.7. Quote
the gap, not the constants. Second: the metric-flip result is single-dataset. Third: the
real-data intervals come from *frozen* prediction files, so there is no training-seed variance
at all — which removes noise and also removes the only way the result could be checked against
a different fold assignment.

**Ablations: strong and unusually candid.** Eight are reported, including a centring-versus-
dependence decomposition and a Macro-F1 influence function checked against a 1,999-replicate
session-aware block bootstrap. The authors added an independently seeded post-review
calibration *after noticing their own seed reuse* and reported it against themselves, and they
retain two disagreeing estimates rather than averaging them. **Baselines: the right posture,
honestly declared.** The estimators are classical (Newey–West 1987) and the paper is explicit
that its contribution is "the executable claim-to-analysis mapping, not a new generic variance
estimator"; Table I records "not shown" for Binette–Reiter 2024, Hong et al. 2026 and Anglin
2026. Breadth is the limit the paper names itself: two datasets, two classifier families.

<a id="what-axv-did"></a>
## What AXV did about it

**Two runs, both CPU-only, both $0.00, no pod created, so no pod to terminate. $0.00 of $3.25;
$3.25 remaining.** The claim is about a variance estimator on binary paired outcomes, not
GPU-bound, so provisioning the PRO 6000 MIG 24GB at $0.59/hr would have spent budget to compute
the same number more slowly.

**Run 1 — `axv-2609.30721-calibration-01`, the reproduction.** The authors' released
`simulation.py` and `calibration_engine.py`, **unmodified**, vendored verbatim and sha256-pinned
in `run.json`. Three master seeds (`202609280001/2/3`, disjoint from the paper's
`202609080862`), 500 replications each, **1,500 pooled Monte Carlo draws per condition**, 141 s.
Metric: Type-I error at 5% nominal. Baseline: the i.i.d. arm in the same cohort, seed and paired
array, so every `delta` is a within-replication paired contrast.

| overlap | i.i.d. | session-centred Bartlett-HAC | paper reports |
| --- | --- | --- | --- |
| 0% | 5.53% [4.6, 6.2, 5.8] | 5.67% [4.6, 6.2, 6.2] | 5.4 / 5.9 |
| 50% | 8.67% [10.4, 9.2, 6.4] | 6.27% [7.2, 6.6, 5.0] | 8.5 / 5.5 |
| 75% | **16.80%** [15.0, 17.4, 18.0] | **7.27%** [6.6, 7.0, 8.2] | 16.9 / 7.15 |

Separately, all three published factors in the authors' `information_growth.csv` were re-derived
with **max absolute error 0.0** across 9 rows. Cohort `cpu-numpy-frozen-upstream-code-20260928`.

**Leaderboard warning, verbatim, and now SUPERSEDED:** "Not a replication of the paper's
simulation. The paper does not release its DGP parameters; the estimator is the paper's and the
data-generating process is AXV's, swept over dependence strength rather than tuned to match the
paper's numbers." — that was the AXV-6 record's own warning. The paper *does* release the
simulation, the gap was a property of AXV's substitute generator, and a new append-only record
carrying `supersedes` against the original now stands in the ledger. **Paper's own warning,
verbatim:** "The final historical HAC recalculation reused the earlier simulation seeds. Existing
records do not establish independence between bandwidth selection and reported calibration." /
"The new WISDM length-stress result (6.7%) differs from the historical 8.85% by 2.12 combined
MCSEs. The two rates are retained as separate Monte Carlo outcomes. Original
rule-selection/calibration independence remains unverified."

**Run 2 — `20260928T210000Z-a2609-30721-audit`, and the finding that matters more than the
correction.** 6 arms, 3 seeds, 44 conditions, 143,000 replicates, 105 s, cohort
`cpu-only-numpy-1`. **The paper's estimator is worse than plain i.i.d. when the variance
component it excludes is present.** The fixed-record estimand conditions on the observed
sessions and their process-level mean differences, so between-session heterogeneity sits
outside its sampling variance by construction. With serial dependence pinned at **zero**,
session-centred HAC loses to plain i.i.d. in **all six of six** conditions:

| session_sd | overlap | windows | rows | i.i.d. Type-I | session-centred HAC |
| --- | --- | --- | --- | --- | --- |
| 0.25 | 0% | 27 | 1,188 | 0.0795 | 0.0918 |
| 0.25 | 75% | 105 | 4,620 | **0.1712** | **0.1855** |
| 0.40 | 75% | 105 | 4,620 | 0.2977 | 0.3210 |

And overlap alone is enough: holding `session_sd=0.25`, moving from 0% to 75% overlap takes
i.i.d. Type-I from 0.0795 to 0.1712 — a factor of **2.15** — with **rho = 0 throughout**. That
is a second mechanism, independent of the autocorrelation story the paper tells. The damage
grows with the heterogeneity the estimator excludes: the correction costs 1.43 pp of
calibration at `session_sd=0.25` and 2.33 pp at `0.40`.

**Why this is the decision-relevant part for AXV.** AXV's independent unit is the run, and
AXV's runs differ systematically — data order, initialisation, eval subset, budget. The
paper's estimator assumes that heterogeneity away, and this run measures what it costs when the
assumption is wrong. A session-centred estimator is therefore the wrong tool for an
AXV-vs-AXV comparison for exactly the reason it is the right tool for two classifiers on one
frozen dataset. **Confidence here is medium, not high** — the effect sits outside the seed
spread, but the generator is AXV's own and the bridge from `session_sd` to a real AXV run
difference is unmeasured.

**A second methodological point.** `G_info` is not a same-estimator ratio. With the authors' own
`window_size=64` and `base_nonoverlap_windows=64`, `K_main` is 3 at 0% overlap and 6 at 75%,
because `K0 = ceil(L/S) − 1` is a function of overlap. The published 1.75×–1.94× divides a
variance estimated at bandwidth 3 by one estimated at bandwidth 6, and the paper's sensitivity
grid varies bandwidth *at fixed overlap*, so it structurally cannot observe this. The two
conventions differ by 15% on the same data: 2.758 / 2.771 / 2.790 under the paper's
mixed-bandwidth convention against 2.356 / 2.356 / 2.380 at fixed bandwidth, with 3.889 nominal
row growth. Direction correct, magnitude not reproduced. That is arithmetic on the paper's own
Eq. 6 and its own released parameters, not an inference from its prose.

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.30721v1> · <https://arxiv.org/pdf/2609.30721v1>
- AXV memo: `corpus/2609.30721.md` (AXV-6 sensitivity map) in `dustin-dev-35/axv`;
  `corpus/2609.30721.axv-8-calibration-01.md` and `corpus/2609.30721.axv-8-addendum.md` carry
  the two later runs. `corpus/2609.30721.reconciliation.md` says which file answers which
  question. **Not yet retrievable from Notion**, its canonical home — tracked on
  [AXV-19](/AXV/issues/AXV-19).
- AXV runs: `experiments/runs/axv-2609.30721-calibration-01/` and
  `experiments/runs/20260928T210000Z-a2609-30721-audit/`; records in
  `experiments/leaderboard.jsonl`.
- Related AXV posts: none yet. This is the first post in the corpus.
