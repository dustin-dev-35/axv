---
title: "10 Years in 1 Paper"
description: "The AXV decade compression: what the field believed, what turned on it, what it cost, and what did not work."
revision: 0
date: 2026-09-28
corpus_posts: 1
corpus_memos: 3
corpus_experiments: 2
aggregate_confidence: medium
date_range: 2026-09-25 to 2026-09-28
---

# 10 Years in 1 Paper

*Revision 0. One published post, three memos, two experiments in the ledger. This document
is a ledger with a spine, not yet a decade compression. It exists so the ledger discipline
starts at post one, and it says on every line how little is behind that line.*

## 0. How to read this

**Corpus, counted rather than estimated.**

| quantity | count | source |
| --- | --- | --- |
| papers triaged | 6 | AXV first reading batch, 2026-09-28 |
| papers read | 3 | memos filed in `corpus/` |
| memos written | 3 | `2609.30721`, `2609.30725`, `2609.31381` |
| memos filed in GitHub `corpus/` | 3 | `9398d3a`, header line added in `ff150d3` |
| memos filed in Notion | **0** | Notion connector not exposed to agent runs |
| memos filed in Supabase `corpus_index` | **0** | Supabase connector not exposed to agent runs |
| posts published | 1 | `overlapping-eval-windows-are-not-independent-tests` |
| experiments in `experiments/leaderboard.jsonl` | **3 runs, 29 records** | `verify-2609.30721-typei-20260928`, `verify-2609.31381-mcnemar-20260928`, `axv-2609.30725-accounting-01` |
| aggregate confidence | **medium** | Every memo in the corpus is `medium`, so this document is |

**Date range covered: 2026-09-25 to 2026-09-28.** Three papers, all submitted in the last
week of September 2026. There is no decade here yet and the title is a target, not a
description.

**Method.** Every substantive claim below resolves to a post and an arXiv ID through
Appendix A. Nothing is recalled from memory. A claim with no post behind it does not appear.
Two of the three memos have no post yet, so they appear in Appendix B's evidence and nowhere
else in the argument. That is the ledger being honest about itself.

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
calibration on the paper's side, and an independent 63-condition re-implementation on AXV's.
Confidence `medium`, and `medium` for a specific reason: the simulation's data-generating
process is not released, so AXV's re-implementation produced IID Type-I anywhere from **0.069 to
0.210** at the same overlap. The direction is robust; the constants are not portable.

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

The corpus supports one cost statement, and it is specific — and AXV's own measurement of it is
larger than the paper's.

**Measurement cost of overlapping evaluation.** The paper reports that test-window counts grow
**3.93×–3.97×** from 0% to 75% overlap while variance-equivalent information grows only
**1.75×–1.94×** — a 47–55% reduction in claimed precision — and on real data the paired
interval-width inflation is 1.22× to 1.66× across three settings. AXV's re-implementation
measured the reduction as **larger**: information growth **2.81×** with mechanical overlap
alone and **2.62×** at high persistence, against 3.97× nominal row growth, i.e. mechanical
overlap costs 41% of the nominal information and AR(1) persistence adds only 7% more. The field
has been paying this on every dense-window result and not naming it, and the size of the bill is
not yet pinned down by anyone.

**What this section cannot yet say:** compute cost, capital cost, data cost, and abandoned
ideas. None of those are in the corpus. Named as a gap, not padded.

## 5. What did not work

This is the section a small corpus can still do honestly, because failure is per-paper and does
not need a decade.

**The paper's headline constants do not survive a parameter sweep.** AXV re-implemented the
estimators and swept the unreleased persistence parameter as a function rather than guessing one
value. The same estimator produces IID Type-I anywhere from **0.069 to 0.210** at 75% overlap
against a 0.05 nominal. The paper's 16.9% is one point in a range the paper has not bounded. The
direction replicated on a parameter-free reimplementation; the numbers did not port.

**The paper's information-growth magnitude did not reproduce.** AXV measured **2.81×** with
mechanical overlap alone and **2.62×** at rho = 0.99, against **3.97×** nominal row growth. The
paper reports **1.75×–1.94×**. The shape of the claim survived — overlap does cost most of the
nominal information, and AR(1) persistence adds only 7% more — but the magnitude is roughly
1.5× larger than reported. A magnitude that is wrong in the conservative direction is still
wrong, and quoting the paper's figure would understate the effect AXV actually measured.

**The proposed fix fails exactly where AXV operates.** The paper's session-centred estimator
conditions on the observed sessions and their process-level mean differences, so
between-session heterogeneity is outside its sampling variance by construction. Under
heterogeneity acting on the *model-pair difference* — which is what a paired `delta` is — the
numbers are **IID 0.776, HAC 0.800, equal-subject 0.032** against a 0.05 nominal. The
session-centred estimator is **no better than plain IID**, and both are catastrophic. Only the
route that aggregates to the independent unit survives.

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
  66.2%. AXV's re-implementation agrees on the direction and bounds it: across every overlap
  and every dependence strength, session-centred HAC ran **0.036 to 0.083** against a 0.05
  nominal while IID ran **0.069 to 0.210**, and the IID−HAC gap was non-negative everywhere.
- *Strongest case against it:* it is a scope change, not a fix. It answers "on these
  recordings", not "for a new person" or "on future recordings from these people". And it is
  pointed the wrong way in the one setting AXV actually operates in: it conditions on the
  observed sessions, so heterogeneity on the *model-pair difference* sits outside its sampling
  variance, and there it measures **0.800** against plain IID's **0.776** and a 0.05 nominal.
  The correction does not merely fail to help; it is indistinguishable from the uncorrected
  estimator while both are 15× nominal.

**The experiment that would settle it:** one simulation with the target declared in advance and
the heterogeneity acting on the contrast rather than on shared difficulty, reporting the
fixed-record, new-session and new-subject targets side by side with the bandwidth rule fixed
before inspection. AXV's `align:shared_plus_pair` arm is a first cut at it, not the experiment.
The stronger form of the question is not which window-level estimator to use but whether AXV
should be using a window-level estimator at all.

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
   ratio across three settings. AXV's re-implementation put the information-growth factor
   roughly 1.5× above the paper's, which is a measure of how unpinned this is.
4. **What would it take to settle the estimator question at power?** AXV's 3 seeds are three
   orders of magnitude below the 217 pairs an exact McNemar test needs for 80% power against
   a 10-point effect, and the ledger's own warning says within-batch correlation makes the
   true requirement larger still. Nobody has costed the move to a protocol that can detect
   the effects AXV reports.

**The revision-1 backlog.** Sections 1, 3 and 4 are the three that a three-paper corpus cannot
carry. Filling them requires the rest of the first reading batch, not a better write-up of
these three.

## Appendix A. Source ledger

One row per published post. This count must match the published post count in `site/`.

| post | arXiv ID | claim it contributes | confidence | experiment |
| --- | --- | --- | --- | --- |
| [Your sliding-window eval rows are not 4 tests. They are about 2.](/posts/overlapping-eval-windows-are-not-independent-tests/) | [2609.30721v1](https://arxiv.org/abs/2609.30721v1) | Overlapping eval windows are not independent tests, and subject-disjoint splitting does not make them so. 3.93–3.97× row growth buys 1.75–1.94× information. The session-centred fix assumes away between-run heterogeneity and is worse than plain IID when that is broken. | medium | partially-verified |

## Appendix B. Experiment ledger

Read from `experiments/leaderboard.jsonl` in this repository, never from memory. **Snapshot as
of commit `a3feb74`:** **29 records across 3 runs**. The file is append-only and other agents are
appending to it, so a reader should re-run the count rather than trust this line; the honest
form of a live count is the count plus the commit it was read at. No record carries a
`supersedes`, so nothing here has been corrected away.

| run id | arXiv | cohort | metric | records / seeds | wall clock | cost | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `verify-2609.30721-typei-20260928` | 2609.30721v1 | `cpu-only-2026-09-28` | Type-I error at 5% nominal; variance-equivalent information growth at 75% overlap | 20 records, 63 conditions, 3 seeds (20260928/29/30), M = 1,000 MC sets per condition | 336 s | $0.00 | **verified (partially)** — direction confirmed, headline magnitudes not reproduced |
| `verify-2609.31381-mcnemar-20260928` | 2609.31381v1 | `cpu-only-2026-09-28` | Minimum n for 80% power (exact two-sided McNemar); minimum attainable two-sided p at n = 3; finite-frame bound recheck | 8 records | 1.2 s | $0.00 | **verified** — the paper's bound recheck matched exactly, and a structural limit was found |
| `axv-2609.30725-accounting-01` | 2609.30725v1 | `cpu-only-arithmetic-rederivation-20260928` | Published identities matched | 1 record, 65 identities, 0 seeds | 0 s | $0.00 | **provisional** — 65/65 arithmetic identities hold; the paper's causal claims are not verified and are not verifiable at this budget |

**Harness.** The first two runs are `train.py`, self-contained on numpy and scipy, with
`harness_commit` null and `diff.patch` empty by design: no harness change was required, so no
`experiment/<arxiv-id>-<series>` branch exists in `dustin-dev-35/autoresearch`. The third is a
standalone arithmetic re-derivation script with a recorded sha256. All three are recorded as
deliberate CPU-only deviations rather than as GPU results. **Total pod spend $0.00; $3.25 of
$3.25 remaining.**

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
- `lb-axv-2609.30725-accounting-01` → **65 of 65** published arithmetic identities in
  2609.30725v1 hold, 0 failures. A paper's arithmetic is right; whether its causal story is right
  is a different and unverified question, and the record says so itself.

**Results that did not reproduce, kept here rather than dropped.**

- The paper's information-growth magnitude: AXV measured **2.81×** (mechanical overlap only)
  and **2.62×** (at rho = 0.99) against **3.97×** nominal row growth, where the paper reports
  **1.75×–1.94×**. Direction survived, magnitude did not.
- The paper's headline Type-I constants: IID ran **0.069** to **0.210** across the unreleased
  persistence parameter at 75% overlap, against the paper's single 16.9% figure.

**One result that reproduced exactly.** `…:paper-recheck` re-derived the paper's
finite-frame bound on 27 paired/capture boundary runs as **[−9, 1] tasks**, matching the
paper's reported [−9, 1]. A partial identification bound that reproduces is worth one line in a
ledger, because most of this ledger is non-reproduction.

**Ledger warnings, verbatim, from the records themselves.** "Cohort is CPU-only. This record is
NOT comparable with any runpod-pro6000-mig24gb-torch280-cu130 record and must not be used as its
baseline." / "Not a replication of the paper's simulation. The paper does not release its DGP
parameters; the estimator is the paper's and the data-generating process is AXV's, swept over
dependence strength rather than tuned to match the paper's numbers." / "n=3 seeds. Each seed is
an independent repetition of the full 63-condition Monte-Carlo study, not one draw from a single
study." / "Power is against FIXED true arm accuracies and INDEPENDENT pairs. AXV seeds inside
one batch share the data shard, the pod and the wall-clock budget, so within-batch correlation
makes the true n_needed LARGER. These are optimistic lower bounds." / "This verifies the paper's
ACCOUNTING, not its CAUSAL CLAIMS. Every checked identity is a relation among published values.
The prevalence detectors, the noise floors, the robustness verdicts, and the attribution of the
savings to human abstraction are all taken as given and are NOT verified here."

**A correction is owed on one record.** `axv-2609.30725-accounting-01` states that one DevSkills
cell is "34.1x AXV's entire .25 budget" and that ".25 buys five tasks". Both figures predate the
board's move to a $3.25 total: at $3.25, a $0.80 cell is 24.6% of budget and buys about six
tasks. The direction of the conclusion is unchanged and is still correct — the end-to-end claim
is far out of reach — but the multiple is wrong and it is on the one number AXV budgets against.
Raised to the run's owner as a correction request; not rewritten here, because a run record is
its owner's artifact.

**Two memos have experiments behind them and no post.** `2609.30725` and `2609.31381` are read
and filed in `corpus/`; only `2609.30721` has a published post. The other two draft issues are
open. That gap is Appendix A doing its job, not a rounding error.
