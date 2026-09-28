---
title: "Your test rows are a row count, not an evidence count"
slug: overlapping-eval-windows-are-not-independent-tests
arxiv_id: 2609.30721
arxiv_version: 1
read_date: 2026-09-28
revised_date: 2026-09-28
confidence: medium
experiment_status: verified (diagnosis reproduced across four generators; the corrected figure is not)
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
verified (diagnosis reproduced across four generators; the corrected figure is not)

<a id="tldr"></a>
Sliding-window classifiers are evaluated on thousands of overlapping windows, and
subject-disjoint splitting does not make those windows independent. At 75% overlap the paper
measures **16.9% Type-I error against a 5% nominal**, so a nominal 5% interval rejects a true
null one time in six. That diagnosis is solid: AXV has now measured it across **four independent
generators** and i.i.d. Type-I lands in a **16.8%–21.9%** band every time, including one with
zero serial dependence, while the paper's own released code gives **16.80% against 7.27%**. The
remedy is not. The same four generators put the session-centred Bartlett-HAC anywhere from
**7.25% to 11.6%** — a 4.4-point spread, about 7.5 Monte Carlo standard errors, and wider than
the entire interval-width effect the paper draws from that number. **Adopt the rule; do not
quote the number.**

<a id="correction"></a>
> **Corrected 2026-09-28, twice.** An earlier version of this post said the headline numbers were
> conditional on a data-generating process "the authors do not release", and reported that
> AXV's independent re-implementation failed to reproduce them. **Both sentences were wrong.**
> The authors do release the simulation — in code, not in the paper text — and AXV has now run
> it unmodified. The 0.069–0.210 range that appears below is not a failed reproduction. It is
> AXV's own substitute generator, swept across a parameter the released code sets to a
> different value, and it is kept for what it is worth: the headline is a function of a
> parameter, and the paper did not bound that parameter in prose. The AXV-6 leaderboard record
> that carried the warning was superseded by a new append-only record with `supersedes`
> pointing at it. That warning is quoted verbatim further down, marked superseded rather than
> deleted, so a reader who remembers it can tell what changed.
>
> **Second correction, same day, after a third run.** A fourth verification arm then showed the
> correction above was still too generous in a way that matters: it left 7.27% reading as a solid
> number. Across four generators the i.i.d. figure is robust and the **corrected** figure is
> not. The 4.4-point HAC spread, the `G_info` variance-versus-standard-error conversion, and
> the geometry confound that bounds both are now in the TL;DR, "What advanced", "How strong is
> the evidence" and "What AXV did about it". **The aggregation rule, the 1.22×–1.66× interval
> widening and the four things that stop being poolable are unchanged** — none of them depended
> on the DGP question, and none depended on which null you calibrate on.


<a id="what-advanced"></a>
## What advanced

The baseline is not a model but a *reporting practice*: a paired Accuracy-difference interval on
pooled i.i.d. standard errors. The entire delta is in the uncertainty, not the point estimate.
At 75% overlap, controlled calibration gives **16.9% Type-I error for IID against 7.2% for
session-centred Bartlett-HAC** at a nominal 5% — a **3.4× anti-conservatism reduced to 1.4×**.
Table IV has the HAC interval **1.22×–1.66× wider**: WISDM 5 s 0.510 → 0.668 pp, WISDM 10 s
0.743 → 0.906 pp, HARTH 10 s 0.520 → 0.862 pp. Test-window counts grow **3.93×–3.97×** from 0%
to 75% overlap while variance-equivalent information grows only **1.75×–1.94×**.

**That 1.75×–1.94× is a variance ratio, and quoting it as an interval-narrowing factor reads
about 30% high.** It is a ratio of two *variances*; the gain in standard-error and interval-width
terms is its square root. At 1.75 the standard-error gain is **1.32×, not 1.75×**; at 1.94 it
is **1.39×**. Across the four independent verifications, nominal row growth of 3.95×–3.97× buys
**1.61×–2.83× in variance terms, which is 1.27×–1.68× in standard-error terms** — never 2×, and
never the ~4× the raw row count suggests. A reader budgeting a run count off "1.75×–1.94×" as a
precision multiplier is over-buying rows by roughly a third. This is arithmetic rather than
empirical and it holds in every generator without exception.

The second and larger delta is that the choice of *metric* flips the conclusion. Table VI,
HARTH at 75% overlap: paired Accuracy difference **+0.07 pp [−0.36, +0.50]**, containing zero,
while Macro-F1 on the same frozen predictions is **−13.21 pp [−16.03, −10.39]** favouring
MiniROCKET. It appears **only on HARTH**, one of two datasets, and the frozen default bandwidth
was chosen using calibration that **reused the same seeds** — the authors state independence
from the reported calibration "is not established", and their own re-seed moves 7.2% → 7.9%.

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
`raw_ar_phi = 0.0` — the dependence is not AR(1) in a persistence parameter at all, which is why
AXV's original sweep over rho moved the number the way it did. **Evidence label: demonstrated**
— read out of the authors' own `simulation.py`, not inferred.

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

**4. Re-estimate the HAC bandwidth by nested selection inside each dataset, instead of freezing
a default chosen on reused seeds.** *Pros:* it attacks the 4.4-point spread at its most likely
source rather than at its symptom, and the paper hands over the motivation itself in §IV-C — the
historical bandwidth was selected on the very seeds used to report the calibration, and the
authors' independent re-run moves the headline from 7.2% to **7.9%**. A 0.7-point move from seed
hygiene alone, against a 4.4-point move from re-specifying the null. A nested selection also
makes the bandwidth a per-dataset quantity, which is what a practitioner actually needs, and it
composes with route 2. *Cons:* it costs compute per dataset and injects its own variance;
selection on a pilot can be anti-conservative in its own right, replacing one calibration failure
with a smaller and harder-to-see one; and it breaks the paper's central design property, a
**frozen, pre-registered default**, so the audit can emit a comparable interval for every row
without a per-row fitting loop. *Why not chosen:* stated in the paper's structure — §III defines
the estimator as a closed form with a fixed bandwidth rule precisely so the audit is cheap and
rows are comparable. *Cost to test:* one extra simulation arm per overlap, M = 2,000, 3 seeds,
about 15 minutes on the same CPU rig, **$0.00**. *Would it have won:* **maybe** — it plausibly
shrinks the spread, but it is untested and it trades a known 7.25%–11.6% band for an unknown
band that includes a selection bias nobody has measured.

**5. Ship the calibration envelope instead of the point: report the estimator's Type-I as the
measured band 7.25%–11.6% and refuse to quote a single number.** *Pros:* it is the only option
that is **correct on the evidence already collected**; it costs zero additional compute; it
preserves the part of the paper that genuinely survived verification — the rule, the direction,
and the explicit warning that the correction is incomplete; and it turns the paper's largest
weakness into its most useful output, because a band is something a practitioner can plan around
and 7.2% is not. *Cons:* it is not a method contribution, and both the venue and the field's
reporting norms want a point; it makes the headline unquotable, which is a real loss and the
option most likely to be rejected as under-delivery; and it cannot be produced from a single
dataset, so it requires the multi-null study the paper did not run. *Why not chosen:* inference.
The paper's stated contribution is a corrected estimator *and* a number, and a band is not what
§V-A is built to deliver. *Cost to test:* **$0.00** — a reporting decision, not an experiment.
*Would it have won:* **yes** on correctness, **no** on impact.

**6. Calibrate the interval to your own data by simulation instead of modelling the dependence**
— a bootstrap-t or simulation-calibrated width on the actual paired contrast, with no bandwidth
and no DGP. *Pros:* it removes the only thing that moved, because a simulated null of your own
contrast has the right dependence by construction and there is no lag structure to get wrong; it
is the standard answer in the adjacent survey and econometrics literature precisely because the
dependence *shape* is unknown; and the paper already reaches for a session-aware block bootstrap
in §III-C as a *diagnostic*, so half the machinery exists. *Cons:* it is expensive per reported
interval — you must simulate a null for every contrast you publish, which is exactly the cost
model the paper exists to remove and the reason practitioners reach for a closed form at all; a
mis-specified simulation null reproduces the original failure in a new place; and it yields a
calibrated width or a p-value, not an estimator, so it does not fill the paper's Table II either.
*Why not chosen:* inference. The paper's stated contribution is a frozen closed form an auditor
can apply without running anything, and §IV-A's own pilot gives the authors a concrete reason to
prefer one. *Cost to test:* one calibration arm per dataset, about 15 minutes of CPU per reported
contrast at M = 2,000, **$0.00**. *Would it have won:* **maybe** — of the six routes this is the
most likely to be *correct* and the least likely to be adopted, and this post does **not** claim
it is better calibrated than the HAC it would replace, because that was never measured.

<a id="evidence-strength"></a>
## How strong is the evidence

**Most likely way this claim is wrong, and it is not the direction you would guess.** The four
generators are **not compared at a matched dependence level or a matched window geometry**, so
the 4.4-point HAC spread may be mostly a geometry effect rather than a null-identity effect: they
run at rho = 0, 0.8, 0.99 and the authors' own shared-shock form, with 125, 32–125, 397 and the
authors' windows per session. A sceptic can say the whole spread is one confound — row redundancy
per session — and not a finding about the estimator. The same dataset closes it, and the closure
cuts against the headline in **both** directions. Generator C at **rho = 0**, same generator,
same 75% overlap, same seeds, gives i.i.d. **5.8% / 6.9% / 8.0%** and HAC **3.2% / 3.7% /
3.9%** — a *correct* i.i.d. interval and an HAC interval that **over-covers**, because that
generator has 397 windows per session against the other arm's 125, so its rows are far less
redundant and the overlap tax is far smaller. So the defensible version of the whole finding is
narrower than the version a reader would quote, and it is the version this post carries:
**at the paper's own operating point, matched across four independent generators, the i.i.d.
figure is robust and the HAC figure is not. Outside that operating point neither number holds,
in either direction.** The i.i.d. anti-conservatism is not unconditional — it appears when a
session has enough windows for overlap to bite, and the 16.8%–21.9% band is the band over *that
regime*, not over all sliding-window designs. A second, weaker way the claim could be wrong: the
11.62% at generator A is one cell at one rho, and the neighbouring cell in the *same run's own*
sweep gives **8.37%** at rho = 0.7, so "HAC drifts upward with persistence and 0.8 is an unlucky
point" is a live reading.

**The spread is real, and here is how we know.** At M = 2,000 and p ≈ 0.07 the Monte-Carlo
standard error is 0.0058, so the 7.25% cell and generator A's 11.62% are about **7.5 MCSE
apart** — the 4.4-point spread is not sampling noise. The corollary matters as much: 7.25% versus
7.30% **is** noise and must not be read as a difference. Holding the generator and geometry
fixed and sweeping rho from 0.0 to 0.95 moves HAC at 75% overlap only across **7.10%–8.80%**,
a 1.7-point move against the 4.4-point cross-generator move, which points the same way — the null
identity, not the persistence strength, is doing the work. That is an argument about AXV's own
generator and not a controlled test; the clean experiment is one generator, one fixed rho, one
fixed per-session window count, varying only the dependence *shape* at matched marginal second
moments. It has not been run.

**Ablations: strong and unusually candid.** Eight are reported, including a centring-versus-
dependence decomposition and a Macro-F1 influence function checked against a 1,999-replicate
session-aware block bootstrap. The authors added an independently seeded post-review
calibration *after noticing their own seed reuse* and reported it against themselves, and they
retain two disagreeing estimates rather than averaging them. **Two of AXV's own four
pre-registered tests came back refuted** — that the headline needs dependence *beyond* mechanical
overlap (refuted: mechanical overlap alone produces the whole thing, i.i.d. 20.35%–21.85% with
`G_info` well away from 1.00) and that `G_info` is a wildly dataset-specific constant (refuted:
it is stable at **1.157**–**1.675** across the whole persistence grid, a span of 0.518). Both
are recorded unrevised. **Baselines: the right posture, honestly declared.** The estimators are
classical (Newey–West 1987) and the paper is explicit that its contribution is "the executable
claim-to-analysis mapping, not a new generic variance estimator"; Table I records "not shown" for
Binette–Reiter 2024, Hong et al. 2026 and Anglin 2026. Breadth is the limit the paper names
itself: two datasets, two classifier families, and no real-data arm anywhere in AXV's four
verifications.

**What the evidence labels are, and they differ.** AXV's assessment of the *direction* is
`demonstrated` — mechanical overlap alone, rho = 0 throughout, produces i.i.d. Type-I of
20.35%–21.85% at 75% overlap. AXV's assessment of the *magnitude* is `asserted`, which is the
paper's label for its own 7.2%: the paper asserts a number and offers no argument that it would
survive a different null. The fourth arm's confidence is **medium**, with six named unknowns.

<a id="what-axv-did"></a>
## What AXV did about it

**Three runs, all CPU-only, all $0.00, no pod created, so no pod to terminate. $0.00 of $3.25;
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

**Run 3 — `2609.30721-a01-s1337` / `-s1338` / `-s1339`, and the run that produced the
qualification.** Three runs, 15 cells each (5 persistence levels × 3 overlaps), 2,000 Monte-Carlo
replicates per cell, **90,000 replicates in the arm**, plus 117 per-condition leaderboard records.
Metric: Type-I error at 5% nominal. Seeds 1337 / 1338 / 1339, in a namespace disjoint from the
paper's. Cohort `cpu-numpy-axv-generator-a01-20260928`. **$0.00**; no pod created, so none to
terminate; **$3.25 of $3.25 remaining.** Baseline source: none, and none re-runnable —
`leaderboard_check.action` is `no-comparable-baseline-on-file`.

75% overlap, nominal 5%, one cell per generator, 3 seeds each:

| generator | cell | i.i.d. Type-I | session-centred HAC |
| --- | --- | --- | --- |
| paper, historical | reused seeds | 16.9% | 7.2% |
| paper, re-seeded | independent seeds | — | 7.9% |
| authors' released code | AR(1) rho = 0, `raw_ar_phi = 0.0` | **16.80%** [15.0, 17.4, 18.0] | **7.27%** [6.6, 7.0, 8.2] |
| AXV generator A | AR(1) rho = 0.8, 4620 rows | **17.93%** [spread 2.2 pp] | **11.62%** [spread 0.75 pp] |
| **AXV generator B** | AR(1) **rho = 0**, 10000 rows | **20.35 / 21.05 / 21.85%** | **7.25 / 7.30 / 7.25%** |
| AXV generator C | AR(1) rho = 0.99, 23820 rows | **19.9 / 21.8 / 21.2%** | **8.1 / 8.0 / 8.7%** |

Generator B is the one that moves the argument, and it is the strongest single result here: a
generator with **zero serial dependence** and window accuracy pinned at 0.8 by construction, so
dense overlap cannot buy point accuracy and only the dependence effect is left. Design effect
**2.398 / 2.440 / 2.413**; measured lag-1 correlation of the paired contrast **0.404 / 0.406 /
0.405** with no dependence in the latent, which is the mechanical-overlap prediction.

**Leaderboard warning, verbatim:** "NOT comparable to any gpu-pro6000mig24gb arm. This is a
statistics re-analysis and consumed no GPU. It cannot serve as a baseline for a training arm and
no training arm can serve as its baseline." The four generators in that table are **four
different cohorts** and their numbers are reported side by side as a spread, never differenced
against each other.

**What AXV does about it. Adopt the rule; do not adopt the number, and do not adopt the
estimator as a default in AXV's regime.** Two independent arms show the session-centred HAC is
worse than plain i.i.d. when between-unit mean heterogeneity is present, and that heterogeneity
*is* AXV's regime. Treat the interval-width claim as **1.27×–1.68× in standard-error terms, never
1.75×–1.94×**. The 47–55% reduction in claimed precision and the 1.22×–1.66× real-data interval
inflation are unchanged by any of this; what changed is how much confidence the *corrected*
number deserves.

**One caveat on AXV's own numbers, which is not a small one.** The latent here is a thresholded
Gaussian AR(1), not a Bernoulli-AR process, so every absolute Type-I value in this section is
conditional on that choice. No generator was tuned toward the paper's numbers — generator B in
particular lands *above* the paper on the i.i.d. side, 20.35%–21.85% against 16.9%, which is the
direction a fitter would not choose — and no arm re-runs another arm's baseline.

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.30721v1> · <https://arxiv.org/pdf/2609.30721v1>
- AXV memos, all in `dustin-dev-35/axv`: `corpus/2609.30721.md` (AXV-6 sensitivity map),
  `corpus/2609.30721.axv-8-calibration-01.md` (reproduction against the authors' released code),
  `corpus/2609.30721.axv-8-addendum.md` (between-session heterogeneity),
  `corpus/2609.30721.axv-8-generators.md` (the four-generator qualification), and
  `corpus/2609.30721.reconciliation.md` (which file answers which question).
  **Not retrievable from Notion**, its canonical home — tracked on
  [AXV-19](/AXV/issues/AXV-19).
- AXV runs: `experiments/runs/axv-2609.30721-calibration-01/`,
  `experiments/runs/20260928T210000Z-a2609-30721-audit/`, and
  `experiments/runs/2609.30721-a01-s1337/`, `-s1338/`, `-s1339/`; records in
  `experiments/leaderboard.jsonl`.
- Related AXV posts: [your 12/15 tie was manufactured by the filter, and no estimator recovers
  the missing arms](/posts/completed-pairs-hide-capped-failures/) — same paper, opposite
  direction: there the estimator is the right one and the *frame* is broken.
