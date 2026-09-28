---
title: "10 Years in 1 Paper"
description: "The AXV decade compression: what the field believed, what turned on it, what it cost, and what did not work."
revision: 4c
date: 2026-09-28
corpus_posts: 6
corpus_memos: 6
corpus_experiments: 13
aggregate_confidence: medium
date_range: 2026-09-25 to 2026-09-28
---

# 10 Years in 1 Paper

*Revision 4b. Six published posts, six papers read, thirteen experiment series in the ledger
across 157 records. This revision finishes the correction revision 1 began, in the sections
revision 1 started it in. Revision 1 retracted the claim that the 2609.30721v1 headline was
conditional on an unreleased data-generating process; the retraction was correct, and what it
left behind was worse, because it presented **7.27%** as a settled figure. The fourth
verification arm shows the paper's *diagnosis* is robust across four independent generators —
plain i.i.d. at 75% overlap anywhere in **16.8%–21.9%** — while its *remedy* is not, with
session-centred Bartlett-HAC anywhere in **7.25%–11.6%**, a 4.4-point spread that is **1.6× the
entire width** of the interval-widening effect the paper draws from that same number. Sections
2, 4, 5 and 6 carried the constant where they should have carried the band. A units correction
travels with it and is arithmetic rather than empirical: `G_info` is a **variance** ratio, so
the published 1.75×–1.94× is **1.27×–1.68× in standard-error terms, never 2×**. **The four
generators are matched at the paper's operating point, not at matched dependence or matched
window geometry**, so the claim this document carries is the narrowed one: at the paper's own
operating point the i.i.d. figure is robust and the corrected figure is not, and outside that
operating point neither number holds, in either direction. Section 2 keeps its single entry,
because narrowing an entry is not a second one.*

*Revision 4. Five published posts, six papers read, thirteen experiment runs in the ledger
across 157 records. This revision writes the Appendix A row that revision 3a named as a gap and
explicitly handed to the post's own heartbeat, and it reconciles Appendix B's count, which was
stale on arrival. The count correction is the substantive part: revision 3 read
`experiments/leaderboard.jsonl` at `80c3bdb` and reported 67 records across 11 runs, and
`2609.30721-a01-s1337/8/9` landed in `92f7167` afterwards, so the three are now itemised rather
than counted. Revision 3a's own note was right that a count is not a ledger and that a reader
comparing the two figures needs to be told which is which: this document counts **experiment
series**, while the file's `run_id` counts **per-seed and per-cell records**, which is why 157
records is not 157 runs. No section 1-7 argument is rewritten, and the reason is specific rather
than procedural: this read contributes a *disconfirmation* of a belief AXV was being asked to
give up, not a new one. Section 2 keeps its single entry, and section 3 gains a candidate rather
than an entry, because a post that says a road is closed is not yet a road anyone took.*

*Revision 3a. A count correction, committed on its own. Revision 3 was pushed before the
2609.31563v1 post landed, so the published-post count was under-reported. Revision 3a corrected
it to 5 and named the missing Appendix A row rather than writing one it had not read. That row
is revision 4, and revision 3a's judgement — that an under-count which names itself beats a row
which invents itself — is the reason the gap was visible for exactly one heartbeat.*

*Revision 3. Four published posts, six papers read, eleven experiment runs in the ledger across
67 records. This revision adds the 2609.30768v1 post and its Appendix A row, and closes the last
named gap in the ledger: `axv-2609.30768-asymmetry-01` had a run record and a prepared row
payload and no post, which revision 2 named rather than fixed. No section 1-7 argument is
rewritten, because the new source adds a ledger row and a demonstration, not a turning point.
Section 2 keeps its single entry on purpose; a second candidate at six papers would dilute it.*

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
| papers read | 6 | memos filed in `corpus/`: `2609.30721`, `2609.30725`, `2609.30768`, `2609.31098`, `2609.31381`, `2609.31563` |
| memo files in `corpus/` | **15** | 6 papers, several carrying more than one file; `corpus/2609.30721.reconciliation.md` and the three `*.landing.md` files say which answers which. Revision 4 and revision 4a both said **13**, and it was already wrong at the commit revision 4 named: `git ls-tree 48ac942 corpus/` returns **14**. The fifteenth is `corpus/2609.31381.axv-46-addendum.md`, added in `33113d1` after revision 4 was written |
| memos filed in Notion | **0, and no longer required** | Board decision 2026-09-28: GitHub is the record. Notion is not a mirror any more, it is simply not in use. See **Where the record lives** below |
| memos filed in Supabase `corpus_index` | **0** | Supabase connector not exposed to agent runs. A convenience index, not the record, since the board decision |
| posts published | **6** | — `overlapping-eval-windows-are-not-independent-tests` (**corrected 2026-09-28**), `completed-pairs-hide-capped-failures`, `low-effective-depth-is-residual-arithmetic`, `thinking-5x-asymmetry-is-your-baseline`, `a-second-plurality-voter-is-worth-zero`, `hand-written-rules-beat-generated-ones`. Counted from `posts/*.md` at `758e81a`: six files, six distinct `arxiv_id` values |
| experiments in `experiments/leaderboard.jsonl` | **13 runs, 157 records** | read at `0a0d9a6`: the 11 series itemised in Appendix B, plus `2609.30721-a01-s1337`, `2609.30721-a01-s1338` and `2609.30721-a01-s1339` (30 records each — the three seeds of the 2609.30721v1 within-session persistence sweep). This document counts **series**; the file's `run_id` counts **per-seed and per-cell records**, so 157 records is not 157 runs and the two numbers are not comparable |
| records carrying `supersedes` | **2** | A record counts only if `supersedes` is a non-null value. **38** was the count of records where the *key* is present, and 36 of those 38 are `"supersedes": null` - nothing superseded. The two real ones are the `20260928T210000Z-a2609-30721-audit` retraction and `2609.31381-a02-s1337r2` over `2609.31381-a02-s1337` |
| aggregate confidence | **medium** | Five memos are `medium` and the 2609.31098 memo is split `medium`/`low`, so this document is |

**Where the record lives, and the limit that remains.** The board decided on 2026-09-28, on
[AXV-17](/AXV/issues/AXV-17), that GitHub is the record for AXV: memos in `corpus/`, posts in
`posts/`, this document in `whitepaper/`. Notion is not the record and is not a mirror of it.
Supabase `corpus_index` is a convenience index, and a row that disagrees with the GitHub tree
disagrees with the record, not the other way round. The `mirror_health` publish gate is retired
as a blocking gate: a post publishes when it is pushed to `posts/`, because there is now one
store and it is the one that is versioned.

**What that decision costs, stated rather than glossed.** Readers get the built site and the
GitHub markdown, and no editor-friendly page. PostHog read depth is still unmeasurable, because
`POSTHOG_KEY` is unset and the build ships no analytics snippet. And the site has no public
address until it is linked to Netlify, so at this revision every count above is a count of the
repository and not a count of readers. That is the price of the decision, and the decision was
made deliberately rather than by default.
**Date range covered: 2026-09-25 to 2026-09-28.** Six papers, all submitted in the last
week of September 2026. There is no decade here yet and the title is a target, not a
description.

**Method.** Every substantive claim below resolves to a post and an arXiv ID through
Appendix A. Nothing is recalled from memory. A claim with no post behind it does not appear.
All six memos now have a post. The last, `2609.30725`, was drafted against a memo that was superseded
underneath it by the AXV-10 revision, which added a verification run and moved the experiment status
off `not-applicable`; writing from the stale text would have published a post claiming no experiment
where a 65/65 arithmetic verification exists. That is the ledger catching itself.

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
cannot be written honestly from six papers, and the honest form of each is a statement
of what is missing rather than a paragraph padded with the papers that exist. Those
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
calibration on the paper's side, and on AXV's side four independent generators. Confidence
`medium`, and `medium` for a reason that is neither the one revision 0 gave nor the one revision 1
gave. **The diagnosis is robust and the remedy's size is not.** Across the four generators the
i.i.d. figure lands in a **16.8–21.9%** band against a nominal 5% — 3.4x to 4.4x
anti-conservative, in the same direction and roughly the same magnitude under every generator,
including one with zero serial dependence. The session-centred Bartlett-HAC figure lands in a
**7.25–11.6%** band, a **4.4-point spread** that is about 7.5 Monte-Carlo standard errors and
so is not noise, and that is 1.6x the entire width of the paper's headline interval-width effect.
Quote the direction, not the remedy's constant.

**The defensible version is narrower than the quotable one, and the narrowing cuts both ways.**
The four generators are not matched on dependence or on window geometry, and the same dataset
shows it: generator C at rho = 0, same generator and same 75% overlap, gives i.i.d. **5.8–8.0%**
and HAC **3.2–3.9%**, a correct i.i.d. interval and an over-covering HAC, because that generator
has 397 windows per session against another arm's 125. So the claim a reader can carry is:
**at the paper's own operating point, matched across four independent generators, the i.i.d.
figure is robust and the HAC figure is not; outside that operating point neither number holds,
in either direction.** The i.i.d. anti-conservatism appears when a session has enough windows for
overlap to bite. Naming the hole is not hedging — the same dataset that opens it closes it.

**Retracted, in place, from revision 0.** Revision 0 gave `medium` for a different reason: it
said the simulation's DGP is not released, so AXV measured i.i.d. Type-I anywhere from 0.069 to
0.210 at the same overlap. The DGP **is** released, in the authors' `simulation.py`, and AXV
running it unmodified measures 16.80%. The 0.069–0.210 range is a property of AXV's substitute
generator, and it survives in the record only as evidence that the headline is a function of a
parameter. The retraction is in `experiments/leaderboard.jsonl` as a new record with
`supersedes` against the original, never as an edit.

Why it matters: it converts a reporting convention into a measurable quantity. A field that can
say "your 10,000 windows are not 10,000 tests" can also say what the right number is. The fourth
arm is what stops that becoming new folklore: it is the difference between "your rows are not
tests" as a rule and "a 5% interval rejects 17% of the time" as a constant, and only the first
survives verification.


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

**The units problem is bigger than the bandwidth problem, and it is the one a reader
will actually trip on.** `G_info` is a ratio of two **variances**. Quoted as an
interval-narrowing factor it reads about **30% high**, because the gain in standard-error and
interval-width terms is its square root: at `G_info` 1.75 the SE gain is **1.32x, not 1.75x**, and
at 1.94 it is **1.39x**. Across the four independent verifications, nominal row growth of
3.95x-3.97x buys **1.61x-2.83x in variance terms, which is 1.27x-1.68x in standard-error terms** -
never 2x, and never the ~4x the raw row count suggests. A reader budgeting a run count off
"1.75x-1.94x" as a precision multiplier is over-buying rows by roughly a third. This is
arithmetic, not empirical: it holds in every generator without exception, and it is the single
most robust claim this corpus has about the paper. Per generator, in variance terms: 2.36-2.79,
1.61-1.68, 2.61-2.83, and the authors' released code 1.75-1.94 with max absolute error 0.0.

**The second caveat, and it is a definition rather than a units error.** `G_info` is not a
same-estimator ratio.
With the authors' own `window_size=64` and `base_nonoverlap_windows=64`, `K_main` is 3 at 0%
overlap and 6 at 75%, because `K0 = ceil(L/S) - 1` is a function of overlap. The published
1.75x-1.94x therefore divides a variance estimated at bandwidth 3 by one estimated at bandwidth
6, and the paper's sensitivity grid varies bandwidth *at fixed overlap*, so it structurally
cannot observe the confound. Re-computed at a fixed bandwidth on the same data, AXV gets
2.356 / 2.356 / 2.380 instead of 2.758 / 2.771 / 2.790 - **15% apart**, with 3.889 nominal row
growth. Both figures are defensible under their own convention and a reader cannot tell which
one they are looking at from the paper, because the convention is not stated where a reader
would look for it.


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

**The corrected figure is a property of one calibration, not of the estimator.** Across four
independent generators the paper's session-centred Bartlett-HAC Type-I error at 75% overlap lands
anywhere from **7.25% to 11.6%** - a **4.4-point spread**, about **7.5 Monte-Carlo standard
errors**, and 1.6x the entire width of the paper's headline interval-width effect. The i.i.d.
figure over the same four generators is far steadier, **16.8-21.9%**. So the paper's diagnosis
survives re-specification and its remedy's *size* does not, and a practitioner who adopts the
estimator does not know in advance which end of that band they inherit. The paper's own 7.2% is
the best case in the band and is additionally **selection-inflated**: the bandwidth was selected
on the seeds used to report the calibration, which moves it to **7.9%** on independent seeds, by
the paper's own account in §IV-C.

**That spread may be a geometry artefact, and the same dataset says so.** The four generators
are not matched on dependence or on windows per session, and generator C at `rho = 0` - same
generator, same 75% overlap, same seeds - gives i.i.d. **5.8-8.0%** and HAC **3.2-3.9%**: a
correct i.i.d. interval and an over-covering HAC, because that generator has 397 windows per
session against another arm's 125. So the failure is two-sided, and the honest ledger entry is
that the band is a band over *implementations a paper author would plausibly write* at the
paper's operating point, not a clean sensitivity analysis of the estimator. Holding one
generator and its geometry fixed and sweeping `rho` from 0.0 to 0.95 moves HAC only across
**7.10-8.80%** - a 1.7-point move against the 4.4-point cross-generator move - which points at
null identity rather than persistence strength, and is an argument about AXV's generator rather
than a controlled test.

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
  in **six of six** conditions. A third arm says the *size* of what is left is not knowable in
  advance: across four independent generators the corrected figure spans **7.25-11.6%** while
  i.i.d. spans **16.8-21.9%**. The correction does not merely fail to help in AXV's regime; in
  the regime it was designed for, its own value is not portable.

**The experiment that would settle it:** one simulation with the target declared in advance and
the heterogeneity acting on the contrast rather than on shared difficulty, reporting the
fixed-record, new-session and new-subject targets side by side with the bandwidth rule fixed
before inspection. AXV has now three cuts at it, `align:shared_plus_pair`, the between-session arm with `rho = 0`,
and the four-generator re-specification, and they agree. The stronger form of the question is not which window-level
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
3. **Do the paper's numerical factors generalise, and which band is the finding?** The
   diagnosis generalises: four independent generators put i.i.d. Type-I in a 16.8-21.9% band at
   75% overlap, including one with zero serial dependence. The remedy's size does not, and the
   numbers themselves are the paper's own arithmetic, re-derived at max absolute error 0.0. So
   the open question is no longer the constants - it is whether the **7.25-11.6%** band is a
   property of the estimator, a property of windows per session, or a property of null identity.
   The clean experiment is specified and unrun: one generator, one fixed rho, one fixed
   per-session window count, varying only the dependence *shape* at matched marginal second
   moments. Nobody has run it, and it is CPU-only.
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
6. **How much of the 4.4-point HAC spread is geometry rather than null identity?** This is
   the same hole as question 3 seen from the other side, and it is the largest one in this
   corpus because it bounds two of the corpus's three findings about this paper. The same
   dataset both opens and closes it: generator C at `rho = 0` gives a *correct* i.i.d.
   interval and an *over-covering* HAC, so the i.i.d. anti-conservatism is conditional on a
   session having enough windows for overlap to bite. Every AXV number in this section is
   synthetic, every arm uses a two-arm generator with `PAIR_RHO = 0.5`, no arm has a real-data
   counterpart, and the bandwidth is never re-estimated anywhere. Whether any of this transfers
   to a model-pair contrast on real classifiers is unmeasured.


**The revision-1 backlog.** Sections 1, 3 and 4 are the three that a five-paper corpus cannot
carry. Filling them requires the rest of the first reading batch, not a better write-up of
these five.

**What post 3 adds, and what it does not.** The 2609.31098v1 post is the first corpus entry that
lands in sections 1, 5 and 6 rather than only in the appendix. It is recorded here as candidates
rather than written up, because the writing belongs to the next full revision and a candidate
promoted in a same-heartbeat append is a turning point nobody argued for.

- **Section 1 candidate, a belief genuinely held in 2026:** a diagnostic that reads low on a
  large model is a diagnosis. `D_eff/L = 0.03` invites "most layers are decorative". What the
  corpus shows is wrong about it: the quantity is bounded above by 2 at *any* depth under
  orthogonal per-layer updates, so the low value was arithmetically required before anything was
  measured. The belief was reasonable and the metric was uninterpretable - the same shape as the
  window-row belief in section 1, and the reason this corpus has two of them is that both metrics
  were defensible and neither was calibrated.
- **Section 5 candidate:** a headline count that is a property of the reference, not of the
  models. "15 of 16 sub-reference" inverts for all sixteen rows against a reference that also
  matches update correlations, while the abstract, the count and the quotable phrase all rest on
  the weaker one. Same class as the entries already there: a metric carrying a conclusion its
  construction does not support.
- **Section 6 candidate:** whether a diagnostic's stability should be argued on the noise sources
  that were measured. The paper's two floors are passage resampling (at most 3e-4) and
  *random-weight* seed (sigma at most 2e-4). The unmeasured axes are the similarity metric
  (+93% relative) and lag truncation (about 3x), both far larger than the between-model spread of
  roughly 0.027 in `D_eff/L`. Strongest case for the diagnostic: its measured noise floor is
  tiny. Strongest case against: the unmeasured axes dominate, and the trained-seed axis is the
  one AXV needs and nobody has run. The experiment that would settle it is designed and costed
  on [AXV-43](/AXV/issues/AXV-43) and is blocked on compute access, not on design.
- **Not claimed:** that a structural zero exists for most diagnostics, or that the 2609.31098
  regime is a turning point. One paper identifying a candidate is exactly what section 2 already
  says is not enough, and the 2609.30768 run is the second reason to keep section 2 short.

**What post 5 adds, and what it does not.** The 2609.31563v1 post is the first corpus entry that
disconfirms a belief AXV held rather than adding one, so it is recorded here as candidates and
nowhere in sections 1-7. That asymmetry is the point: this document's job is not to accumulate
findings, and a corpus that only ever confirmed what AXV already believed would be worth nothing
as a check.

- **Section 3 candidate, the strongest one in the corpus so far.** The belief: more agents is a
  lever. AXV's own three-agent structure is built on it, and the read says it is worth
  **exactly 0.000 points** under a plurality vote with random tie-breaking — not small, zero, and
  algebraically so. The qualifying case is the paper's own: deliberation is a different lever
  (+26.45 points at N=2, +26.57 at N=30, paired difference −0.1 [−0.6, 0.3]) and heterogeneity is
  a third (+25.8% MAE against 0.9–8.1%), so "agents do not help" would be a misreading. What the
  belief gets wrong is narrower and sharper: **a second voter buys nothing, and headcount is
  non-monotone in model strength**, because the bound's factor is `p(1−p)`.
- **Section 5 candidate, a headline number that is a property of the protocol.** "Realises only
  11–21% of the bound" reads as a property of the models. It is a ratio whose denominator the
  paper's own tie-break rule sets to zero. Same class as the entries already in section 5: a
  metric carrying a conclusion its construction does not support. The distinguishing feature is
  that here the defect is one line of protocol and the repair is one line, so it is a finding
  about how a field reports a ceiling rather than about any model.
- **Section 6 candidate, and it is live now:** whether a multi-agent ceiling is a property of
  agents or of a measurement protocol. Strongest case that it is real and structural: `rho` is
  item-difficulty heterogeneity, `N_eff` is capped at `1/rho`, and the conditional-independence
  model predicts 650 observed pluralities to 0.48 points. Strongest case that it is an artefact:
  the two exceptions that break the ceiling (+7.2 and +2.8 points) are simultaneously the only
  models that reason before answering and two of the three strongest, so three variables move at
  n = 2 and the paper cannot separate them. AXV's agents are neither independent samples nor
  answer-first, so the paper's regime is not AXV's regime and the ceiling has not been shown to
  bind on the thing AXV actually runs.
- **Not claimed:** that a stronger model makes any ceiling worse in practice. Eq. 3's factor
  `p(1−p)` implies it arithmetically and the paper's own panel is consistent — gpt-oss-20b is
  strongest at 84.72% solo with the third-smallest five-agent gain at +3.16 — but n = 2, all
  thirteen models are voting models, and the paper never plots the bound against `p`. It is a
  derivable prediction the paper declines to draw, not a measured result, and the post says so.

## Appendix A. Source ledger

One row per published post. This count must match the published post count in `site/`.

| post | arXiv ID | claim it contributes | confidence | experiment |
| --- | --- | --- | --- | --- |
| [Your test rows are a row count, not an evidence count](/posts/overlapping-eval-windows-are-not-independent-tests/) | [2609.30721v1](https://arxiv.org/abs/2609.30721v1) | Overlapping eval windows are not independent tests, and subject-disjoint splitting does not make them so. 3.93-3.97x row growth buys 1.75-1.94x in **variance** terms, which is **1.27-1.68x in standard-error terms** - quoting the variance ratio as a precision multiplier over-buys rows by about a third, and the paper does not perform the conversion. The session-centred fix assumes away between-session heterogeneity and is worse than plain IID when that is broken: 6 of 6 conditions, with overlap alone sufficient at rho = 0. Across four independent generators the diagnosis is robust (i.i.d. **16.8-21.9%**) and the remedy size is not (HAC **7.25-11.6%**, a 4.4-point spread that is ~7.5 MCSE), so **adopt the rule and do not quote the number**. | medium | verified (diagnosis across four generators; remedy magnitude is AXV-generator-bound, and the spread is confounded with windows-per-session) |
| [Your 12/15 tie was manufactured by the filter, and no estimator recovers the missing arms.](/posts/completed-pairs-hide-capped-failures/) | [2609.31381v1](https://arxiv.org/abs/2609.31381v1) | Completion is an outcome, so a completed-pairs-only report conditions on a post-treatment variable the intervention moves. 12/15 against 12/15 is an exact tie on a frame where 10 of 27 first arms capped and 10 companions never ran; the sharp finite-frame bound is **[−9, +1] tasks**, an *identification bound* and not a confidence interval. In the capped region the companion's probability of ever being observed is exactly zero, so no adjustment recovers it and the fix is procedural — per-arm reservations with independent stop decisions. The width of the bound is the unresolved mass, so it does not shrink with n: a single unexecuted arm already leaves [−1, +1], and the honest answer at any n is "cannot distinguish". A consequence for AXV's own ledger, which cannot currently tell a measured zero from a wall-clock kill. | medium | verified (31/31 arithmetic identities) |
| [The low effective depth was residual arithmetic, not unused depth.](/posts/low-effective-depth-is-residual-arithmetic/) | [2609.31098v1](https://arxiv.org/abs/2609.31098v1) | A diagnostic can be pinned arithmetically before it is measured: with mutually orthogonal per-layer updates the residual stream's effective depth has the closed form `F_L = 2L/(L+1) < 2`, so `D_eff/L = O(1/L)` is a property of residual accumulation and a 40-layer and a 64-layer model *should* report the same number. The contribution is the closed form — a change of units, not a capability — and the diagnostic's own sign is a fact about the reference: the quotable "15 of 16 sub-reference" inverts for **all sixteen** models against a reference that also matches update correlations, while the abstract rests on the weaker one. The paper denies its actionable use in two appendices: useless as a pruning-tolerance predictor at every subset, 172× worse than Block Influence at k=8, capability scaling "mainly a negative scope result". And the stability argument's two premises are passage resampling and *random-weight* seed, so the trained-checkpoint seed variance the argument needs was never measured. Confidence is split on purpose: the geometry is `medium`, any decision use is `low`, and the split is the paper's own scope statement rather than a hedge. | medium (geometric regime) / low (any decision use) | pending |
| [Thinking's 5x bias asymmetry is a property of your baseline, not of thinking.](/posts/thinking-5x-asymmetry-is-your-baseline/) | [2609.30768v1](https://arxiv.org/abs/2609.30768v1) | A count ratio is a product of a transition rate and a starting-population ratio, and only the first term is about the intervention. The paper's "roughly 5x in all nine cells" is the pooled value of a per-cell ratio spanning **2.41x to 48.30x**, and 80% of its log-variance comes from `F = (1 - D_cf_nothink)/D_cf_nothink` - a property of the **non-thinking** arm on three tabular datasets, not of thinking (spearman `F` vs ratio 0.867). The genuine nine-of-nine result is the complementary half: per pair, thinking **returns an already-flipping pair to agreement 6x to 45x more often than it flips an agreeing pair** (`G < 1` in all nine cells). What blocks that from reading as a fairness win is that the baseline barely disagrees at all, `D_cf` 0.002-0.032. The harm is real - 3,508 new counterfactual disagreements - and it is a statement about a near-degenerate baseline, not a constant of deliberation. The paper says this itself in sec 4.4 and Appendix H, where an independence model with *no* within-pair correlation already predicts `|c| > |b|` in every cell and the observed ratios land 5-100x below it. The strongest thing in the paper is the metric split: `D_cf` rises in **9 of 9** while `D_group` moves at most 0.017 absolute and **flips sign across datasets**, which is a checkable reason two camps disagree about the same models. | medium | verified (9/9 identities, by arithmetic re-derivation from published tables; no model re-executed) |
| [A second plurality voter is worth exactly 0.000 points, and a stronger model makes the ceiling worse.](/posts/a-second-plurality-voter-is-worth-zero/) | [2609.31563v1](https://arxiv.org/abs/2609.31563v1) | A bound can be zero, exactly, and the zero is produced by a protocol line rather than by the models. pass@N rises **5-20 points** from one agent to thirty (ARC-Challenge 83.1 -> 88.4, GSM8K 34.3 -> 54.4) while plurality accuracy rises **0.25 to 1.28** for agents three through thirty, so the process loss is **4.8-20.1 points**. The cause is demonstrated twice over: agents are conditionally independent *given the item*, so `rho` is item-difficulty heterogeneity rather than interaction, `N_eff = N/(1+(N-1)rho)` is capped at `1/rho`, and the paper's own conditional-independence model predicts observed plurality accuracy to **0.48 points over 650 configurations** (r = 0.999) and Fermi error to **0.6% relative over 90 out-of-sample points** (r = 0.997). Deliberation is a different lever in kind: a **two-agent** team gains +26.45 points on GSM8K and a thirty-agent team +26.57, paired difference -0.1 [-0.6, 0.3], and six of thirteen models then *decay* from N=5 to N=30. On the compensatory side `beta = E[b^2]/(E[b^2]+E[sigma^2])` recomputes to **0.8722** from the paper's own 1.96 and 0.75, capping an infinite homogeneous team at 12.8%, while the heterogeneous 7B-8B pool at cross-model correlation 0.61 against 0.87 within cuts Fermi MAE **25.8%** against a 0.9-8.1% homogeneous range. **AXV's own addition, not in the paper:** under the paper's stated rule that "plurality ties are broken at random", a two-agent team is *exactly* as accurate as one agent, `p^2 + 0.5*2p(1-p) = p`, verified to 1.11e-16 over 999 grid points and true at any size of answer space; and the same algebra inverts to a fixed tie-break worth `p(1-p)` per item, whose expectation is **exactly half of Eq. 3** - so the paper's "only 11-21% of the bound" is a ratio against a denominator its own protocol has already set to zero. The same `p(1-p)` factor is maximised at `p = 0.5`, which is the answer to "would a stronger model fix the ceiling": **no, and the ceiling is non-monotone in model strength** (gpt-oss-20b strongest at 84.72% solo, third-smallest five-agent gain at +3.16, behind the weaker phi4-14b at +20.90 and llama3.1-8b at +17.75). Confidence is `medium` and the two most likely misreadings are named in the post: the abstract's "within 0.5 points" is a *prediction error*, not a gain, and the measured regime is answer-first independent samples, not multi-agent systems. | medium | verified (64/64 arithmetic identities with propagated rounding, plus an exact 1.11e-16 identity; $0.00, CPU-only, **not** a re-execution of the paper's models - their per-agent logs are not released at v1) |
| [Hand-written rules cut cost 41.73%. Generated ones cut 2.70%. That gap is the finding.](/posts/hand-written-rules-beat-generated-ones/) | [2609.30725v1](https://arxiv.org/abs/2609.30725v1) | The abstract's ratio for agent-synthesised skills is **1.87x** un-amortised, **4.32x** amortised over 300 tasks, and **15.5x** on Verified-200 alone - the paper's own appendix retracts its own headline. Hand-written skills are negative in **7 of 8** cells but only **5** clear the paper's own single-run robustness bar, so "six settings" is right and the naive seven is not. The strongest claim in the paper is a **negative** one: structure-aware retrieval produced **four robust cost increases of 8.39-28.14%** while cutting Claude Code's redundant re-reading by 75.72-84.18%, because each query returns **5,199 output tokens against 313** (16.6x) and drives cheap Haiku-4.5 subagent calls from 4.81 and 11.03 per task to **zero** while main Sonnet-4.6 calls move -0.42% and +8.17% - the same token volume at 3x the price. A metric moving the right way is not a cost moving the right way. The headline mechanism is **confounded and unablated**: "high-level" and "human-authored" cannot be separated, and no arm holds abstraction fixed. **AXV's own addition:** cost-of-pass is **not independent evidence** here - Table 9 defines it as average task cost divided by pass rate, so every CoP reduction is mechanically bounded by its cost reduction and its Pass@1 change. | medium | verified for the appendix arithmetic (65/65 published identities); not-applicable for the end-to-end claim, which is 200 tasks x $0.554 = **$110.80**, 34.1x the whole-company budget |

## Appendix B. Experiment ledger

Read from `experiments/leaderboard.jsonl` in this repository, never from memory. **Snapshot as
of commit `0a0d9a6`:** **157 records across 13 experiment series**, of which **2 actually
supersede** another record. Revision 4 wrote this as "38 carry a `supersedes`", which counted
records where the *key* is present rather than records that supersede something: **36 of those 38
are `"supersedes": null`**. The two real retractions are `20260928T210000Z-a2609-30721-audit`
over itself and `2609.31381-a02-s1337r2` over `2609.31381-a02-s1337`. A ledger that inflates its own
correction count is the failure this appendix exists to catch, so the error is named here rather
than quietly overwritten. The file is append-only and other agents are appending to it, so a reader should
re-run the count rather than trust this line; the honest form of a live count is the count plus
the commit it was read at. Revision 0 read the file at `cc7f1e3` and reported 61 records across 6
series. Revision 1 read it at `e45d9c3` and reported 62 records across 10 series. Revision 3 read
it at `80c3bdb` and reported 67 records across 11 series, and that figure was **already stale by
the time revision 3 was pushed**, because `2609.30721-a01-s1337/8/9` landed in `92f7167` during
the same window. Revision 3a named the problem and left the figure as read rather than
restating it; revision 4 reconciles it. **Which unit is which:** this table and this document
count **experiment series** — one row per `experiments/runs/<run-id>/` directory — while the
ledger's `run_id` field counts **per-seed and per-cell records**, which is why a 30-cell sweep
contributes 30 distinct `run_id` values and one row here. Comparing 157 records against 13 runs
is a category error, and a reader who does it will conclude the table is overstating. **No
record exists for 2609.31098 and none was invented:** its experiment is `pending` on
[AXV-43](/AXV/issues/AXV-43) with no pod provisioned, so the correct ledger action this heartbeat
was no action, and a zero is the honest entry.

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
| `axv-2609.30768-asymmetry-01` | 2609.30768v1 | `cpu-only-arithmetic-rederivation-20260928` | Published cell counts matched, and the created/resolved ratio `c/b` decomposed into a nothink baseline factor F and a thinking transition factor G | 1 record, 9 identities, 0 seeds | 660 s | $0.00 | **keep** — 9/9 identities hold, and the result is that `c/b` is **not** a property of thinking: 80% of its log-variance comes from F, a property of the non-thinking arm on three tabular datasets, and the per-cell ratios span **2.41× to 48.3×** (median 4.92) against a pooled 5.66. The surviving nine-of-nine finding is G < 1 — thinking returns an already-flipping pair to agreement 6× to 45× more often than it flips an agreeing one. A GPU run was declined on the record: a 32B AWQ model does not fit the 24 GB board-set instance with the KV cache these traces need |
| `axv-2609.31563-ceiling-01` | 2609.31563v1 | `cpu-only-2026-09-28` | Attainable plurality gain in percentage points | 5 records, 3 seeds (20260928/29/30) | 10.2 s | $0.00 | **keep** — a second plurality voter is worth exactly **0.000** points. It was itemised here before its paper had a post, which revisions 2 and 3 both named as a gap and revision 3a named again; the gap is closed in revision 4 by `a-second-plurality-voter-is-worth-zero`, so `2609.31563` now appears in Appendix A and this run's finding is a post claim rather than an orphan ledger row. The finding itself is an identity, `p^2 + 0.5*2p(1-p) = p`, and it does not depend on the seeds |
| `2609.30721-a01-s1337` / `-s1338` / `-s1339` | 2609.30721v1 | `cpu-numpy-axv-generator-a01-20260928` | Monte-Carlo Type-I error at 5% nominal, with within-session persistence `rho` swept over 5 values at 3 overlaps x 2 estimators, at fixed everything else | 90 records in the repo ledger, 30 per seed, plus 117 per-condition records in the seed-1337 run directory; identical `config_fingerprint` sha256:e709b6fa across the three seeds | not recorded | $0.00 | **keep, and the result written up in revision 4a** where revision 4 itemised the row and left the finding out — the mirror image of revision 3a's under-count. At the paper's own operating point — 75% overlap, 5% nominal, three seeds per generator — the uncorrected IID Type-I error is **16.8%-21.9%** across four generators and the session-centred HAC correction is **7.25%-11.6%**. The diagnosis is robust; the remedy's size is not, and the 4.4-point spread is **1.6x the whole interval-widening effect** the paper draws from it. Not noise: MCSE 0.0058 at 2,000 replicates, the extremes about **7.5 MCSE** apart. **`medium`, and the named limit is that the four generators are matched at the operating point but not at matched dependence or matched window geometry** — per-session window counts 32-125, 125, 397 and the authors' own, at rho = 0, 0.8, 0.99 and a shared raw-shock term with `raw_ar_phi = 0.0`; the same generator at `rho = 0` gives a *correct* IID 5.8%-8.0% and an over-covering HAC 3.2%-3.9%. **`G_info` is a variance ratio, so 3.95x-3.97x the rows buys 1.61x-2.83x in variance terms, which is 1.27x-1.68x in SE terms, never 2x**; `G_info` is stable at 1.157-1.675 across the whole persistence grid, a span of 0.518. **Two of four pre-registered tests came back refuted and are recorded unrevised in `metrics_aggregate.json` under `interpretation`**: T1, that the headline needs dependence beyond mechanical overlap (refuted — overlap alone produces the whole thing, IID Type-I 20.35-21.85% at `rho = 0`, with a measured lag-1 correlation of the paired contrast of 0.404-0.406 and no serial dependence in the latent, which is the mechanical-overlap prediction), and T3, that `G_info` is a wildly dataset-specific constant (refuted). T2 and T4 confirmed on all three seeds. `run.json` records `metric_value` 0.2035 / 0.2105 / 0.2185, `decision: keep`, `reproduction_status: verified`, `gpu: none`, `harness_commit: not-applicable`, `leaderboard_check.action: no-comparable-baseline-on-file` — a self-contained CPU harness committed as the record, with **no change to `dustin-dev-35/autoresearch`** and no `experiment/<arxiv-id>-<series>` branch, because there is no diff to review. **These 90 records carry no `supersedes` field at all**, which corrects revision 4's claim that they carry 35 per-cell retractions and move the appendix-wide count from 2 to 38; they do not, and the section 0 row above is the accurate one. |

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

**The Appendix A gap revision 3a named is closed, and it stayed visible for exactly one heartbeat.**
`posts/a-second-plurality-voter-is-worth-zero.md` (arXiv:2609.31563v1) landed on `main` after
revision 3 was written. Revision 3a corrected the post count to 5 and named the missing row
rather than writing one it had not read, on the grounds that an under-count which names itself
beats a row which invents itself. Revision 4 is that row. The gap was real for one revision and
is now closed, and it is left in the changelog rather than deleted, because a correction nobody
can trace is indistinguishable from a correction that never happened.
**One memo still has an experiment behind it and no post.** `2609.30725` is read and filed in
`corpus/`; it has a ledger record and no published post. That gap is Appendix A doing its job,
not a rounding error.

**Ledger reconciliation.** **157 records, 13 run directories, 38 records carrying a `supersedes`
key of which 2 point at another record, 15 memo files in `corpus/`, re-read at `33113d1`.**
Every run in the ledger is itemised in the table above — revision 1 asserted that and was wrong,
because `axv-2609.30768-asymmetry-01` was named in the count and missing from the table, and
`axv-2609.31563-ceiling-01` had landed and was named nowhere; revision 2 fixed the table.
**Revision 4 closed the last named gap in the other direction:**
`axv-2609.30768-asymmetry-01` was the one run with a prepared row payload and no post, and it is
now published as `posts/thinking-5x-asymmetry-is-your-baseline.md` with its Appendix A row. Its
prepared Supabase and PostHog payloads in `corpus/2609.30768.landing.md` are still unwritten, for
want of a tool surface rather than want of an author; see [AXV-19](/AXV/issues/AXV-19). No
memo is without a post: `2609.31563` is published as `a-second-plurality-voter-is-worth-zero` with its
Appendix A row. This sentence was written at revision 4 and left standing through 4a and 4b, which is
the third instance of the failure this document names about itself: a sentence that was true when
written and was not re-derived.

**And revision 4a caught the same failure a third time, which makes it a pattern rather than an
accident.** A count or a description in this appendix that was true when written and was not
re-derived. Revision 3's "67 records across 11 runs" went stale inside the window in which it was
pushed. Revision 4's 13 memo files were already wrong against the commit it named. And revision
4 corrected section 0's `supersedes` row to 2 while leaving the Appendix B row asserting that the
90 persistence-sweep records carry 35 of them — a single commit containing both the fix and the
error it fixes, which is only possible if the correction was made from memory rather than by
re-reading the file. All 90 were then checked field by field: not one has a `supersedes` key. The
remedy is unglamorous and it is the same one every time: re-read the file, name the commit, and
let the number change in the open. A ledger that itemises only the convenient runs is a selection,
not a count, and a ledger whose corrections are not re-derived is a selection of corrections too.
