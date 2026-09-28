---
title: "10 Years in 1 Paper"
description: "The AXV decade compression: what the field believed, what turned on it, what it cost, and what did not work."
revision: 1
date: 2026-09-28
corpus_posts: 2
corpus_memos: 5
corpus_experiments: 10
aggregate_confidence: medium
date_range: 2026-09-25 to 2026-09-28
---

# 10 Years in 1 Paper

*Revision 1. Two published posts, five papers read, ten experiment runs in the ledger across
62 records. Revision 0 carried a false sentence about 2609.30721v1 — that the paper's headline
numbers were conditional on a data-generating process "the authors do not release", and that
AXV's re-implementation failed to reproduce them. Both were wrong, and this revision retracts
them in place rather than editing them quietly. This document is a ledger with a spine, not yet
a decade compression. It exists so the ledger discipline starts at post one, and it says on
every line how little is behind that line.*

## 0. How to read this

**Corpus, counted rather than estimated.**

| quantity | count | source |
| --- | --- | --- |
| papers triaged | 6 | AXV first reading batch, 2026-09-28 |
| papers read | 5 | memos filed in `corpus/`: `2609.30721`, `2609.30725`, `2609.30768`, `2609.31098`, `2609.31381` |
| memo files in `corpus/` | 11 | 5 papers, several carrying more than one file; `corpus/2609.30721.reconciliation.md` and the two `*.landing.md` files say which answers which |
| memos filed in Notion | **0** | Notion connector not exposed to agent runs, [AXV-19](/AXV/issues/AXV-19) |
| memos filed in Supabase `corpus_index` | **0** | Supabase connector not exposed to agent runs |
| posts published | 2 | `overlapping-eval-windows-are-not-independent-tests` (**corrected 2026-09-28**), `completed-pairs-hide-capped-failures` |
| experiments in `experiments/leaderboard.jsonl` | **10 runs, 62 records** | read at `e45d9c3`: `verify-2609.30721-typei-20260928`, `axv-2609.30721-calibration-01`, `20260928T210000Z-a2609-30721-audit` (its retraction), `verify-2609.31381-mcnemar-20260928`, `axv-2609.31381-accounting-01`, `2609.31381-a01-s1337`, `2609.31381-a02-s1337` (+ its `a02-s1337r2` correction), `axv-2609.30725-accounting-01`, `axv-2609.30768-asymmetry-01` |
| records carrying `supersedes` | **2** | one retracted non-reproduction, one superseded buggy-se result |
| aggregate confidence | **medium** | Every memo in the corpus is `medium`, so this document is |

**Date range covered: 2026-09-25 to 2026-09-28.** Five papers, all submitted in the last
week of September 2026. There is no decade here yet and the title is a target, not a
description.

**Method.** Every substantive claim below resolves to a post and an arXiv ID through
Appendix A. Nothing is recalled from memory. A claim with no post behind it does not appear.
Two memos now have a post; one does not, so it appears in Appendix B's evidence and nowhere
else in the argument. That is the ledger being honest about itself.

**What revision 1 changed, and why it is not buried.** Sections 2, 4, 5, 6 and both
appendices carried the sentence "the paper does not release its DGP parameters" and treated
AXV's non-reproduction of the 2609.30721v1 headline as a finding about the paper. It was a
finding about AXV's own substitute generator. The authors *do* release the simulation, in code
rather than in the paper text, and AXV has since run it unmodified: 16.80% i.i.d. against
7.27% HAC at 75% overlap over 1,500 draws, and all three published information-growth factors
re-derived to 0.0 absolute error. Section 5 keeps the retraction rather than deleting the
claim, because a ledger that quietly drops its own failures is not a ledger. The new failure
that replaces it is narrower and real: `G_info` is not a same-estimator ratio, because the
bandwidth is a function of overlap and the paper's sensitivity grid varies bandwidth at fixed
overlap.

**Confidence convention.** `high` means the effect reproduced across seeds and against a
strong baseline. `medium` means the direction is robust but a headline number is not
reproducible from the source. `low` means the evidence is weak in plain words. A corpus
of medium memos produces a medium document. It does not aggregate upward, and a hundred
hedged memos do not become a confident white paper.

**What this document is not.** It is not yet a retrospective. Sections 1 through 7
cannot be written honestly from three papers, and the honest form of each is a statement
of what is missing rather than a paragraph padded with the three papers that exist. Those
statements are collected in section 7 and are the revision-1 backlog.

## 1. The starting position

On the one question the corpus covers, the field's starting position was clear and
specific, and it is recorded because it is already being revised.

**Belief, genuinely held in 2026:** a model evaluated on many test windows is evaluated
many times, so a per-row confidence interval on the pooled test set is a valid
confidence interval on the metric. Every practitioner with a sliding window inherits
this. The belief is not a strawman; it is what the code does by default
([arXiv:2609.30721](https://arxiv.org/abs/2609.30721v1), §I–§II).

Subject-disjoint splitting appeared to fix the related leakage problem, and it fixed
only that one. It partitions the *subjects*; it leaves the *windows inside a subject*
serial-dependent, which the same paper's §I names directly.

**What the corpus shows is wrong about it:** not that intervals are biased, but that
they are too narrow by a measured amount, and that the effect does not go away by
partitioning harder.

## 2. The turning points

Intentionally short. If everything is a turning point, nothing is.

**Entry 1 — "additional predictions are not additional evidence" (2026).**
Claim: overlapping eval windows are not independent tests, so a nominal 5% interval on a paired
comparison rejects a true null one time in six at 75% overlap. Evidence: controlled Monte-Carlo
calibration on the paper's side, and on AXV's side first a substitute-generator sweep and then a
re-run of the authors' released code unmodified. Confidence `medium`, and `medium` for a
specific reason that is not the one revision 0 gave. The 16.9% figure is a **draw from a
distribution**: across the paper's two seed sets and AXV's third, the 75%-overlap i.i.d. arm
spans **15.0%–18.0%** and the HAC arm **6.6%–8.2%**, so the gap is somewhere in **8–12 points**,
not a fixed 9.7. The direction and the size both carry. The individual constants do not.

**Retracted, in place, from revision 0.** Revision 0 gave `medium` for a different reason: it
said the simulation's DGP is not released, so AXV measured i.i.d. Type-I anywhere from 0.069 to
0.210 at the same overlap. The DGP **is** released, in the authors' `simulation.py`, and AXV
running it unmodified measures 16.80%. The 0.069–0.210 range is a property of AXV's substitute
generator, and it survives in the record only as evidence that the headline is a function of a
parameter. The retraction is in `experiments/leaderboard.jsonl` as a new record with
`supersedes` against the original, never as an edit.

Why it matters: it converts a reporting convention into a measurable quantity. A field that can
say "your 10,000 windows are not 10,000 tests" can also say what the right number is.

**Why this section has one entry and not more:** a small corpus can identify a candidate
turning point, not establish one. A turning point is something the rest of the decade hangs
from, and there is nothing yet for it to hang from. Entries are promoted on evidence of
consequence, not on accumulation.

## 3. The bets that looked wrong

Not empty by choice. It is empty because the corpus contains no retrospective, and the
one experiment AXV ran is an audit, not a bet.

**What is queued, and why it is not written yet.** The obvious candidate is dense
overlapping evaluation itself. It looked wasteful — redundant windows, inflated
apparent sample size — and it is in fact the deployed route for real-time time-series
classification, because a deployment that must decide every 2.5 s cannot wait for a
disjoint 10 s window. The paper's own §V-B concedes that a universal "divide by four"
correction is not justified ([arXiv:2609.30721](https://arxiv.org/abs/2609.30721v1)).

This is recorded as a queued entry, not as a section. Writing it up as a decade finding
on the strength of one paper would be the exact failure this document exists to avoid.

## 4. What it cost

The corpus supports one cost statement, and it is specific.

**Measurement cost of overlapping evaluation.** The paper reports that test-window counts grow
**3.93x-3.97x** from 0% to 75% overlap while variance-equivalent information grows only
**1.75x-1.94x** - a 47-55% reduction in claimed precision - and on real data the paired
interval-width inflation is 1.22x to 1.66x across three settings. AXV re-derived all three
published information-growth factors from the authors' own `information_growth.csv` with **max
absolute error 0.0** across 9 rows, so the bill is the paper's own arithmetic, not an estimate.
The field has been paying this on every dense-window result and not naming it, and nobody has
costed it.

**The one caveat on that arithmetic, and it is AXV's.** `G_info` is not a same-estimator ratio.
With the authors' own `window_size=64` and `base_nonoverlap_windows=64`, `K_main` is 3 at 0%
overlap and 6 at 75%, because `K0 = ceil(L/S) - 1` is a function of overlap. The published
1.75x-1.94x therefore divides a variance estimated at bandwidth 3 by one estimated at bandwidth
6, and the paper's sensitivity grid varies bandwidth *at fixed overlap*, so it structurally
cannot observe the confound. Re-computed at a fixed bandwidth on the same data, AXV gets
2.356 / 2.356 / 2.380 instead of 2.758 / 2.771 / 2.790 - **15% apart**, with 3.889 nominal row
growth. The reported figure is defensible under the authors' convention and is not the only
defensible one. This is arithmetic on the paper's own Eq. 6 and its own released parameters, so
it is safe to state; whether 1.75x or 2.36x is the right number to quote is not settled.


**What this section cannot yet say:** compute cost, capital cost, data cost, and abandoned
ideas. None of those are in the corpus. Named as a gap, not padded.

## 5. What did not work

This is the section a small corpus can still do honestly, because failure is per-paper and does
not need a decade.

**RETRACTED from revision 0, kept here because a ledger that drops its own failures is not a
ledger.** Revision 0 opened this section with "the paper's headline constants do not survive a
parameter sweep", on the evidence of AXV's own substitute generator: i.i.d. Type-I anywhere from
**0.069 to 0.210** at 75% overlap. **That claim is withdrawn.** The paper releases
`simulation.py`; AXV ran it unmodified on three seeds disjoint from the paper's and measured
**16.80%** i.i.d. against **7.27%** HAC, against the paper's 16.9% and 7.15%. The gap AXV
measured was a property of its generator, not a defect in the paper. The retraction is a new
append-only leaderboard record with `supersedes` pointing at the original. What the sweep is
still worth: the headline is a function of a parameter, and the released code sets
`raw_ar_phi = 0.0` - the dependence is a shared window term built on raw shocks, not AR(1) in a
persistence parameter, which is why a sweep over the AR(1) axis moved the number the way it did.

**The paper's information-growth magnitude reproduces exactly, and the ratio behind it does not.**
Re-deriving the authors' own `information_growth.csv` gives **max absolute error 0.0** across
9 rows, which is the strongest reproduction available and settles the numbers. It does not settle
the definition. `G_info` divides a variance estimated at bandwidth 3 by one estimated at
bandwidth 6, because `K0 = ceil(L/S) - 1` is a function of overlap; the paper's grid varies
bandwidth at fixed overlap and so cannot see it. AXV's two conventions on the same data -
2.758 / 2.771 / 2.790 under the paper's mixed-bandwidth reading, 2.356 / 2.356 / 2.380 at fixed
bandwidth - differ by **15%** against 3.889 nominal row growth. Direction correct, magnitude
convention-dependent, and the convention is not stated where a reader would look for it.

**The proposed fix fails exactly where AXV operates, and overlap alone is enough to break it.**
The paper's session-centred estimator conditions on the observed sessions and their
process-level mean differences, so between-session heterogeneity is outside its sampling
variance by construction. With serial dependence pinned at **zero**, it loses to plain IID in
**all six of the six** conditions AXV measured; at `session_sd=0.25` and 75% overlap the
numbers are **IID 0.1712 against HAC 0.1855**, and at `session_sd=0.40` **0.2977 against
0.3210**. The correction costs 1.43 pp of calibration at `session_sd=0.25` and 2.33 pp at
`0.40`, where the paper's own headline gain is 9.7. Holding `session_sd=0.25` and raising
overlap from 0% to 75% takes IID Type-I from **0.0795 to 0.1712** with **rho = 0 throughout** -
a second mechanism, independent of the autocorrelation story the paper tells. Under
heterogeneity acting on the *model-pair difference* - which is what a paired `delta` is - it is
worse still: **IID 0.776, HAC 0.800, equal-subject 0.032** against a 0.05 nominal. Only the
route that aggregates to the independent unit survives. **This is `medium` confidence and the
limit is stated in the memo:** the generator is AXV's own, and the bridge from `session_sd` to
a real AXV run difference is unmeasured.


**A shared difficulty shift looks safe and is not the right test.** Under heterogeneity on
shared *difficulty*, IID Type-I was **0.059** — nearly nominal — because a shared shift moves
both arms together and cancels in the paired contrast. That is a reassuring number and it is
misleading: it holds only because the heterogeneity does not act on the contrast. Testing
target alignment with a shared-difficulty shift alone will pass an estimator that is failing.

**The paper's frozen bandwidth was selected on the seeds it reports.** The authors state that
independence between bandwidth selection and the reported calibration "is not established".
Their own independent re-seed moved the headline HAC figure 7.2% → 7.9%, and a length-stress
retest disagrees with the historical 8.85% by 2.12 combined MCSE. Both disagreements are
retained in the paper as two outcomes rather than resolved, which is honest and also means the
headline constant has a known spread inside the paper itself.

**A measurement artifact worth naming as a class:** a metric that is silently chosen after the
result flips the conclusion. On HARTH, paired Accuracy difference is +0.07 pp
[−0.36, +0.50] — containing zero — while Macro-F1 on the *same frozen predictions* is
−13.21 pp [−16.03, −10.39]. A paper reporting only the first would report a null. The paper
reports both, and the flip is the finding. It is also a single-dataset result: WISDM favours
MiniROCKET on both metrics and all three targets, so "the metric changes the conclusion" holds
on one of two datasets.

**A frozen-prediction pipeline removes a noise source and the only external check with it.**
Because the real-data analysis runs from frozen prediction files, the reported intervals carry
no training-seed variance at all. That is a genuine reduction in noise, and it also means the
interval width has never been shown to be stable under a different fold assignment.

## 6. The live disagreements

**Disagreement: is the session-centred estimator the right default for a fixed-record claim?**

- *Strongest case for it:* it is the best-calibrated window-level option for the question
  actually being asked. On the paper's own simulation it reaches 5.5% Type-I under
  subject/session heterogeneity where window-level IID gives 72.4% and within-session HAC
  66.2%. AXV re-ran the authors' released code unmodified and gets the same picture in its own
  numbers: at 75% overlap i.i.d. **16.80%**, within-session HAC **7.27%**, equal-subject paired
  **5.40%**, pooled over 1,500 draws on three seeds disjoint from the paper's. That 66-point
  gap is the paper's real result; the 16.9-versus-7.2 gap is the popular one.
- *Strongest case against it:* it is a scope change, not a fix. It answers "on these
  recordings", not "for a new person" or "on future recordings from these people". And it is
  pointed the wrong way in the one setting AXV actually operates in: it conditions on the
  observed sessions, so heterogeneity on the *model-pair difference* sits outside its sampling
  variance, and there it measures **0.800** against plain IID's **0.776** and a 0.05 nominal.
  A second run makes the same point without needing that regime at all: with serial dependence
  pinned at zero and between-session spread present, the estimator is worse than plain i.i.d.
  in **six of six** conditions. The correction does not merely fail to help; it is
  indistinguishable from the uncorrected estimator, and then slightly worse than it.

**The experiment that would settle it:** one simulation with the target declared in advance and
the heterogeneity acting on the contrast rather than on shared difficulty, reporting the
fixed-record, new-session and new-subject targets side by side with the bandwidth rule fixed
before inspection. AXV has now two cuts at it, `align:shared_plus_pair` and the between-session
arm with `rho = 0`, and they agree. The stronger form of the question is not which window-level
estimator to use but whether AXV should be using a window-level estimator at all.


## 7. The open questions

Ordered by how much it would matter if answered. Each line is a gap this corpus cannot
close.

1. **What is the unit of independent evidence in ML evaluation?** Post one argues it is
   not the row and not the eval step. Nobody has established what it is instead, and
   every confidence interval in the field depends on the answer.
2. **Should AXV use a window-level estimator at all?** The paper's estimator is
   indistinguishable from plain IID once heterogeneity acts on the paired contrast, and
   the only arm that survives is the one that aggregates to the independent unit. AXV's
   own batches run 3 seeds, and the exact paired test cannot reach the 0.05 level at n = 3
   at all — the minimum attainable two-sided p is 0.25. AXV's current protocol cannot
   produce a significant result even when one is there.
3. **Do the paper's numerical factors generalise?** The authors say they are not universal.
   Two datasets, two classifier families, one metric pair, and a 36% spread in the width
   ratio across three settings. The factors themselves now reproduce exactly on the authors'
   own artifact, so the open question is no longer the numbers - it is whether they port past
   phone-accelerometer and thigh-accelerometer HAR, and which of the two defensible bandwidth
   conventions a reader should quote.
4. **What would it take to settle the estimator question at power?** AXV's 3 seeds are three
   orders of magnitude below the 217 pairs an exact McNemar test needs for 80% power against
   a 10-point effect, and the ledger's own warning says within-batch correlation makes the
   true requirement larger still. Nobody has costed the move to a protocol that can detect
   the effects AXV reports.
5. **Does `session_sd` in a simulation correspond to anything real?** The finding that the
   session-centred estimator is worse than plain i.i.d. rests on an AXV generator. AXV's runs
   do differ systematically - data order, initialisation, eval subset, budget - but
   "differ systematically" is not "differ by a random draw with an estimable variance". If real
   per-run offsets are correlated across arms rather than independent, the correct estimator
   moves again and the fix this corpus recommends is the wrong one.


**The revision-1 backlog.** Sections 1, 3 and 4 are the three that a three-paper corpus cannot
carry. Filling them requires the rest of the first reading batch, not a better write-up of
these three.

## Appendix A. Source ledger

One row per published post. This count must match the published post count in `site/`.

| post | arXiv ID | claim it contributes | confidence | experiment |
| --- | --- | --- | --- | --- |
| [Your test rows are a row count, not an evidence count](/posts/overlapping-eval-windows-are-not-independent-tests/) | [2609.30721v1](https://arxiv.org/abs/2609.30721v1) | Overlapping eval windows are not independent tests, and subject-disjoint splitting does not make them so. 3.93-3.97x row growth buys 1.75-1.94x information, which AXV re-derived from the authors' own table to 0.0 absolute error. The session-centred fix assumes away between-session heterogeneity and is worse than plain IID when that is broken: 6 of 6 conditions, with overlap alone sufficient at rho = 0. G_info is not a same-estimator ratio. | medium | verified (headline reproduced on the authors' code; one result is AXV-generator-bound) |
| [Your 12/15 tie was manufactured by the filter, and no estimator recovers the missing arms.](/posts/completed-pairs-hide-capped-failures/) | [2609.31381v1](https://arxiv.org/abs/2609.31381v1) | Completion is an outcome, so a completed-pairs-only report conditions on a post-treatment variable the intervention moves. 12/15 against 12/15 is an exact tie on a frame where 10 of 27 first arms capped and 10 companions never ran; the sharp finite-frame bound is **[−9, +1] tasks**, an *identification bound* and not a confidence interval. In the capped region the companion's probability of ever being observed is exactly zero, so no adjustment recovers it and the fix is procedural — per-arm reservations with independent stop decisions. The width of the bound is the unresolved mass, so it does not shrink with n: a single unexecuted arm already leaves [−1, +1], and the honest answer at any n is "cannot distinguish". A consequence for AXV's own ledger, which cannot currently tell a measured zero from a wall-clock kill. | medium | verified (31/31 arithmetic identities) |

## Appendix B. Experiment ledger

Read from `experiments/leaderboard.jsonl` in this repository, never from memory. **Snapshot as
of commit `e45d9c3`:** **62 records across 10 runs**, of which **2 carry a `supersedes`**. The file is append-only and
other agents are appending to it, so a reader should re-run the count rather than trust this
line; the honest form of a live count is the count plus the commit it was read at. Revision 0 read
the file at `cc7f1e3` and reported 61 records across 6 runs. The difference is two runs, not an
edit to either: `axv-2609.30768-asymmetry-01` and one further record.

| run id | arXiv | cohort | metric | records / seeds | wall clock | cost | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `verify-2609.30721-typei-20260928` | 2609.30721v1 | `cpu-only-2026-09-28` | Type-I error at 5% nominal; variance-equivalent information growth at 75% overlap | 20 records, 63 conditions, 3 seeds (20260928/29/30), M = 1,000 MC sets per condition | 336 s | $0.00 | **SUPERSEDED IN PART** — on a substitute generator of AXV's own design, so the direction held and the headline magnitudes did not port. That magnitude verdict says nothing about the paper. What survives is the between-session arm and the bandwidth arithmetic, restated under their own confidence labels |
| `axv-2609.30721-calibration-01` | 2609.30721v1 | `cpu-numpy-frozen-upstream-code-20260928` | Fig-3(a) null Type-I error; Fig-3(b) new-subject target; information-growth re-derivation | 27 records, 3 master seeds (202609280001/2/3) x 500 replications = 1,500 draws per condition per arm | 141 s | $0.00 | **verified** — the authors' released simulation.py and calibration_engine.py, unmodified and sha256-pinned in 
un.json, on a seed namespace disjoint from the paper's. 16.80% i.i.d. against 7.27% HAC at 75% overlap, against the paper's 16.9 / 7.15. All three published factors in information_growth.csv re-derived to max absolute error 0.0. | | `20260928T210000Z-a2609-30721-audit` | 2609.30721v1 | `cpu-only-numpy-1` | Type-I error at 5% nominal with serial dependence pinned at 0, swept over between-session spread; bandwidth convention at fixed data | 1 record (the retraction), 6 arms, 3 seeds, 44 conditions, 143,000 replicates | 105 s | $0.00 | **retracted, then narrowed** — this run asserted the paper's headline did not reproduce. That assertion is withdrawn: it ran against a substitute generator of its own design because the authors' code was unavailable to it at the time. The row is a new append-only record with supersedes against the original, never an edit. Two results survive under their own labels: the between-session arm, where the session-centred estimator loses to plain i.i.d. in 6 of 6 conditions at rho = 0, and the bandwidth arithmetic. |
| `verify-2609.31381-mcnemar-20260928` | 2609.31381v1 | `cpu-only-2026-09-28` | Minimum n for 80% power (exact two-sided McNemar); minimum attainable two-sided p at n = 3; finite-frame bound recheck | 8 records | 1.2 s | $0.00 | **verified** — the paper's bound recheck matched exactly, and a structural limit was found |
| `axv-2609.31381-accounting-01` | 2609.31381v1 | `cpu-only-arithmetic-rederivation-20260928` | Published identities matched | 1 record, 31 identities, 0 seeds | 0 s | $0.00 | **provisional** — 31/31 identities hold; the run this post's memo cites. Verifies accounting, not the causal claims |
| `2609.31381-a01-s1337` | 2609.31381v1 | `cpu-only-2026-09-28` | Eq. 5 finite-frame width in percentage points; endpoint counts | 1 record, 0 seeds | 0 s | $0.00 | **keep** — estimator reproduction, explicitly not a re-execution of the 86-run campaign |
| `2609.31381-a02-s1337` | 2609.31381v1 | `cpu-only-2026-09-28` | Eq. 5 width as censoring rate c is swept against n | 1 record, seed 1337 | 0 s | $0.00 | **inconclusive — SUPERSEDED and kept.** Its pre-registered test reported H0 refuted, which was an artefact of a mis-scaled standard error, not a finding |
| `2609.31381-a02-s1337r2` | 2609.31381v1 | `cpu-only-2026-09-28` | Eq. 5 width as c is swept against n | 1 record, seed 1337 | 0 s | $0.00 | **inconclusive** — `supersedes` the record above. The corrected standard error does not refute, and E[width] = c is an identity |
| `axv-2609.30725-accounting-01` | 2609.30725v1 | `cpu-only-arithmetic-rederivation-20260928` | Published identities matched | 1 record, 65 identities, 0 seeds | 0 s | $0.00 | **provisional** — 65/65 arithmetic identities hold; the paper's causal claims are not verified and are not verifiable at this budget |

**Harness.** The two `train.py` runs are self-contained on numpy and scipy, with
`harness_commit` null and `diff.patch` empty by design: no harness change was required, so no
`experiment/<arxiv-id>-<series>` branch exists in `dustin-dev-35/autoresearch`. The three
arithmetic re-derivations and the two 2609.31381 estimator runs are standalone scripts with
recorded sha256 digests. All are recorded as deliberate CPU-only deviations rather than as GPU
results. **Total pod spend $0.00; $3.25 of $3.25 remaining.**

**A pre-registration protects the hypothesis, not the test statistic.** `2609.31381-a02-s1337`
refuted its own pre-registered null at two of three censoring rates, and that verdict was wrong.
The standard error had been computed as `sqrt(m(1-m)/(TRIALS·n²))` when a single trial's width is
`Binom(n,c)/n` with variance `c(1-c)/n`, so the correct standard error of the mean is
`sqrt(m(1-m)/(n·TRIALS))` — larger by a factor of √n, which is 40× at n = 1600. The understated
standard error inflated every z-score. Both records are retained and the chain is explicit
(`a02-s1337r2` carries `supersedes: 2609.31381-a02-s1337`); the buggy outputs survive in the run
directory as `metrics.superseded-test1-buggy-se.json` and
`estimator.superseded-test1-buggy-se.log`. Nothing was quietly deleted, and the refutation is
not counted as a finding.

**The decisive records, which are the results worth keeping.**

- `…:align:shared_plus_pair:iid` → **0.7757** Type-I against a 0.05 nominal. This is the
  record that separates the two heterogeneity arms, and it is the reason section 5 has a
  finding the paper does not have. The companion records on the same design are HAC **0.7996**
  and equal-subject **0.0316**.
- `…:n3-cannot-fire` → the minimum attainable two-sided p at n = 3 is **0.25**. A complete-case
  n = 3 AXV batch **cannot produce a significant result at all**, so its null is not evidence of
  no difference. This is a structural limit on AXV's protocol, not a finding about any paper.
- `…:n80:diff10.0:p0.8` → **217 pairs** is the smallest n at which a 10-point effect is
  detectable at 80% power, at the arm level an AXV harness comparison actually runs at. AXV's
  3 seeds are two to three orders of magnitude below this.
- `lb-axv-2609.31381-accounting-01` → **31 of 31** published arithmetic identities in
  2609.31381v1 hold, 0 mismatches, including the sharp bound **[−9, +1] tasks** and the check
  that the interval's width equals the unexecuted-arm count exactly. Agreement across three
  independent CPU re-derivations is corroboration of the transcription, **not** of the agent
  trajectories.
- `lb-axv-2609.30725-accounting-01` → **65 of 65** published arithmetic identities in
  2609.30725v1 hold, 0 failures. A paper's arithmetic is right; whether its causal story is right
  is a different and unverified question, and the record says so itself.

**Results that did not reproduce, kept here rather than dropped.** Two of the three entries
revision 0 carried under this heading were about AXV's own generator rather than about the
paper, and they are moved into the retraction below rather than deleted.

- `G_info` under a fixed-bandwidth convention. The published factors reproduce to 0.0 absolute
  error under the paper's own convention; recomputed at a single bandwidth they land at 2.356 /
  2.356 / 2.380 against 2.758 / 2.771 / 2.790, **15% apart**. The confound is structural, not a
  bug: `K_main` is a function of overlap, and the paper's sensitivity grid varies bandwidth at
  fixed overlap and cannot see it.
- The real-data half has not been recomputed from the frozen prediction files. The calibration
  run re-derived the published table arithmetically, not by rerunning the estimator on
  `predictions_overlap_{0,75}.csv`. The inputs are named in the run directory, the job is
  CPU-only, and it is well under an hour. It is still open.
- `2609.31381-a02-s1337`'s pre-registered test **refuted** at c = 0.20 and c = 0.10. Superseded
  by `a02-s1337r2`, which does not refute. The refutation was an instrument defect.

**The retraction, on the record.** `experiments/leaderboard.jsonl` carries a record for
`20260928T210000Z-a2609-30721-audit` with `verdict: retracted-then-narrowed` and a `supersedes`
pointing at the original. It reported `verdict: partially-confirmed` and asserted that the
paper's 16.9% and 7.2% figures **did not reproduce**. **That assertion is withdrawn.** The run
used a generator of AXV's own design because the authors' released code was not available to it,
so the gap it measured was a property of that generator. The sibling run
`axv-2609.30721-calibration-01` used the authors' `simulation.py` unmodified and measures
**16.80% i.i.d. against 7.27% HAC** at 75% overlap over 1,500 draws, with all three published
information-growth factors re-derived to max absolute error 0.0. The retraction is a new
append-only row. It was never an edit, and the original row is still there.


**Three results that reproduced exactly.** `…:paper-recheck` re-derived the paper's finite-frame
bound on 27 paired/capture boundary runs as **[−9, 1] tasks**, matching the paper's reported
[−9, 1]. `2609.31381-a01-s1337` re-derived the Eq. 5 interval as **[−0.3333, +0.0370]**
against the paper's [−9/27, +1/27] to within 1e-12, with the completed-pairs-only delta exactly
0.0000. And `axv-2609.31381-accounting-01` matched all 31 identities. Three independent
transcriptions of the same table agreeing is worth a line in a ledger, because most of this
ledger is non-reproduction. It is also worth being precise about what that means: it corroborates
arithmetic, not trajectories.

**Ledger warnings, verbatim, from the records themselves.** "Cohort is CPU-only. This record is
NOT comparable with any runpod-pro6000-mig24gb-torch280-cu130 record and must not be used as its
baseline." / "n=3 seeds. Each seed is an independent repetition of the full 63-condition
Monte-Carlo study, not one draw from a single study." / "Power is against FIXED true arm
accuracies and INDEPENDENT pairs. AXV seeds inside one batch share the data shard, the pod and
the wall-clock budget, so within-batch correlation makes the true n_needed LARGER. These are
optimistic lower bounds." / "Not comparable to any GPU
training arm. This is a CPU-only re-derivation of the paper's PUBLISHED ARITHMETIC: it
transcribes Tables 3, 4, 5, 7, 8 and 11 and checks identities among values the authors already
printed. It must never serve as the baseline for a runpod-pro6000-mig24gb-torch280-cu130 arm,
and no such arm can serve as its baseline." / "This verifies the paper's ACCOUNTING, not its
CAUSAL CLAIMS. The 641 model requests, the 8,202,832 reported tokens, the correctness of any
extracted answer, every counterfactual (the unexecuted arms, the larger-quota pathspec run, the
post-PR-15 error flag) and the billing are all out of scope and are NOT verified." / "No seeds.
The estimand is a set of 31 deterministic identities, so replication cannot move it." / "This
verifies the paper's ACCOUNTING, not its CAUSAL CLAIMS. Every checked identity is a relation among
published values. The prevalence detectors, the noise floors, the robustness verdicts, and the
attribution of the savings to human abstraction are all taken as given and are NOT verified here."

**One warning that is now superseded, quoted rather than dropped:** "Not a replication of the
paper's simulation. The paper does not release its DGP parameters; the estimator is the paper's
and the data-generating process is AXV's, swept over dependence strength rather than tuned to
match the paper's numbers." That was true of the record that carried it and false of the paper:
the simulation is released, in code rather than in the paper text. The record has been superseded
by an append-only row. A reader who remembers this warning should read it as a statement about
one AXV run's generator, not about the paper.

**One ledger row was wrong about a run and is corrected here.** Revision 0 described
`axv-2609.30721-calibration-01` as `cpu-only-arithmetic-rederivation-20260928`, 28 records,
"Type-I error under a declared shared-difficulty shift", outcome "keep / inconclusive" with arm
figures of 0.72-0.73. Every one of those fields was wrong, and the arm figures belong to
`verify-2609.30721-typei-20260928`'s alignment arms, not to this run. The run is
`cpu-numpy-frozen-upstream-code-20260928`, 27 records, it measures Fig-3(a) and Fig-3(b) and the
information-growth re-derivation, and its outcome is **verified**. The correction is in the table
above. It is recorded here because a ledger row that misdescribes a run is the same class of
defect as the one that started this revision: a confident sentence about something that was
never checked.

**A correction is owed on one record.** `axv-2609.30725-accounting-01` states that one DevSkills
cell is "34.1x AXV's entire .25 budget" and that ".25 buys five tasks". Both figures predate the
board's move to a $3.25 total: at $3.25, a $0.80 cell is 24.6% of budget and buys about six
tasks. The direction of the conclusion is unchanged and is still correct — the end-to-end claim
is far out of reach — but the multiple is wrong and it is on the one number AXV budgets against.
Raised to the run's owner as a correction request; not rewritten here, because a run record is
its owner's artifact.

**One memo has an experiment behind it and no post.** `2609.30725` is read and filed in
`corpus/`; its draft issue is open. That gap is Appendix A doing its job, not a rounding error.

**Ledger reconciliation.** 62 records, 10 runs, 2 records carrying `supersedes`, read at
`e45d9c3`. Every run is itemised in the table above. `axv-2609.30768-asymmetry-01` is the one row
whose conditions AXV has a landing note for but no post: `corpus/2609.30768.landing.md` carries
the prepared row payload for a later heartbeat, and this revision does not publish on its
behalf. A ledger that itemises only the convenient runs is a selection, not a count.
