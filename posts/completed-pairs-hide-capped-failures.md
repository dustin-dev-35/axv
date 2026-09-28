---
title: "Your 12/15 tie was manufactured by the filter, and no estimator recovers the missing arms"
slug: completed-pairs-hide-capped-failures
arxiv_id: 2609.31381
arxiv_version: 1
read_date: 2026-09-28
confidence: medium
experiment_status: verified
section_ids:
  - tldr
  - what-advanced
  - how-it-works
  - roads-not-taken
  - evidence-strength
  - what-axv-did
  - links
---

# Your 12/15 tie was manufactured by the filter, and no estimator recovers the missing arms

**Paper:** _Completed Pairs Hide Capped Failures: A ReVerPi Case Study of Selective Context
Projection_ — Guangzhe Zhang, [arXiv:2609.31381v1](https://arxiv.org/abs/2609.31381v1)
**Read:** 2026-09-28 · **Confidence:** medium · **Experiment:** verified

<a id="tldr"></a>
An agent A/B runner reported **12/15 correct for each arm — an exact tie** — on a campaign
where 10 of 27 first arms exhausted a request cap and **all ten companion arms were never
executed at all**. The tie is not a property of the two systems. It is a property of the filter.
Put the missing arms back as bounds and projected-minus-full lands in **[−9, +1] tasks out of
27** — an *identification bound* of **[−33.3%, +3.7%]**, not a confidence interval, and not
narrowable by modelling, because in the capped region the companion's probability of ever being
observed is exactly zero. The fix is procedural: give each arm its own reservation and an
independent stop decision. The caveat: the accounting is checkable and AXV re-derived all of it
with zero mismatches, but the *directional* reading — that projection is worse — rests on one
case, `pathspec-util`, whose recorded failure is confounded with an error-flag defect the paper
itself declines to say would have changed the outcome.

<a id="what-advanced"></a>
## What advanced

The baseline is not a weaker system. It is **the standard report**: analyse the pairs where both
arms completed, which is the normal presentation for an A/B with a per-run resource cap.

**The filter, §5.1 and Figure 2.** 86 submitted runs, 641 completed model requests, 8,202,832
reported tokens (74.9% of input cached). 44 paired/capture runs finish before the
projection-eligibility rule ever fires, 5 stop in capture, 27 reach a verified intervention
boundary. Of those 27, **12 stop** — and in **10 of 10** first-arm request caps the companion was
never executed.

**The bounded contrast, Table 3.** Over all 27 boundary runs: full 14 correct / 6 known bounded
failure / 7 unexecuted; projected 12 / 12 / 3. Full's success count is 14–21, projected's is
12–15, so projected-minus-full lies in **[−9, +1] tasks**. The completed-pair view reports a tie;
the full frame cannot exclude projection losing nine tasks.

**The selector's tie is a fitting artefact, Table 4.** On the 17 runs where both bounded
outcomes are known, always-full and the frozen selector both record 3 failures. Split by whether
a run participated in fitting the threshold: the 4 fitting pairs give 1 full failure against 0
selector failures; the 13 runs outside fitting give **2 against 3** — one extra failure — with
logical tokens going 1,419,197 → **1,541,879, i.e. +8.64%**. Over all 17 the token change is
+0.89%. The 3/17 tie is sustained by one fitting case, `packaging-compatibility`, where projected
is correct and full is wrong.

**Cost on the fully ascertained stratum, Table 5.** The 11 jointly correct pairs are identified
with certainty: 1,267,036 logical tokens for full against 949,774 for projected, ratio **0.750**
(25.0% less in aggregate) — but the geometric mean is 0.883 and the **median is 1.292**, with 7
of 11 pairs increasing. Suffix requests go 35 → 55, **+57%**. **The aggregate is one task:** the
largest single saving is `more-itertools-recipes` at 418,364 full tokens against 35,826
projected, and removing it flips the sum ratio to **1.077**. The paper keeps the case and says so.

**The mechanism case, Table 8.** `pathspec-util` is the omitted, selector-chosen projected
continuation. Full answers in 3 suffix requests and 84,202 suffix tokens. Projected spends 12
requests and 237,629 tokens (**2.82×**) and returns no answer, after a successful archive search
and then two exact reads refused by the shared 3-call quota.

Compute is minutes of tokens and **no GPU**. The archive is published with SHA-256
`2b57e318…22f29c`, 12,980 listed artifacts, and 73 of 76 runs passing the source-level auditor.

<a id="how-it-works"></a>
## How it works

**Why the companion is missing. Evidence: demonstrated.** The runner executes branches
sequentially and breaks when a branch's state is not `completed`. A request-cap exhaustion leaves
the state not completed; a wrong answer does not. So first-arm caps *deterministically* suppress
companion execution — and because that suppression is a function of the first arm's endpoint, in
the capped region the probability of ever observing the companion is exactly zero. Adjustment is
not merely hard there, it is impossible, and inverse-observation weighting divides by zero.
Appendix A.3 gives the algebra; the 10/10 counts confirm it. The positivity failure is
structural, not statistical, and it transfers to any harness with a shared budget and a
sequential scheduler.

**Why projection costs more work. Evidence: partially-evidenced.** Removing a passage forces a
search and then an exact read, and both draw on a combined three-call quota, so a continuation
can exhaust its recovery budget *after* it has already succeeded at retrieving. The
`pathspec-util` trace establishes retrieval success followed by refusal. But the paper states
that neither the sufficiency of the retrieved fragments nor the outcome of a hypothetical larger
quota is established; the error-flag defect means the model-visible text was a bare
`ReVer halted: recovery_quota` line with no error semantics; and the alternative reading — that
the agent would have kept flailing regardless, or that a fourth read would have sufficed — is
not excluded by anything in the record.

<a id="roads-not-taken"></a>
## The roads not taken

**1. Fix the runner, keep the campaign.** Give each arm its own pre-authorised reservation and an
independent execution decision, so a first-arm cap no longer suppresses its companion. *Pros:*
the paper names this as its first design lesson, and it is a small change to one loop. Every
unresolved coordinate becomes a known one, which collapses [−9, +1] toward a point estimate and
eliminates the entire class of bound. It costs no new theory, no new model, no new data, and
nothing about the projection mechanism is disturbed, so the paper's other results survive intact.
*Cons:* it is **not** a re-analysis. It needs the 27 boundary runs re-executed, with new provider
calls and new randomness, and the raw archive is not distributed, so the new frame is not
comparable to the old one. The fix does not raise the budget, so a re-run is exposed to the same
cap and may censor again — which means the reservation has to be generous enough to absorb a cap,
and that changes what is being measured. And the re-run inherits a model the paper cannot
authenticate. *Why not chosen,* stated by the authors: the object was the *existing* frame's
identification problem, and the archived record could not be re-executed. *Cost to test:* 27
boundary runs' worth of provider tokens, on the order of a few dollars of API spend and no pod.
*Would it have won:* **yes**, trivially and by construction.

**2. Report only the fully ascertained stratum and drop the contrast.** *Pros:* the 11 jointly
correct pairs are identified without any assumption, because every one of the 16 non-members has
at least one observed zero, so no assignment to an unexecuted companion can move a run into or
out of the stratum. This is the one estimand in the paper with zero missingness — no bounds, no
positivity argument, no monotonicity assumption — and it still answers a real question: what
projection costs when it works. *Cons:* the stratum is selected on the intervention itself.
Eligibility needs two completed full-observation requests and at least 10 KiB of repeatedly
exposed content, and 44 of 76 runs never reached a boundary at all, so it is exactly the runs
with the most history and plausibly the most retrieval work. Reporting it alone invites a reader
to take a within-success cost ratio for an end-to-end effect, and it silently discards the 12 runs
where the intervention actually hurt — which *is* the finding. *Why not chosen,* inference: a
methodological case study whose thesis is about selection cannot then restrict itself to the
selected part. *Cost to test:* zero; the stratum is already fully enumerated. *Would it have
won:* **yes** as a clean secondary result, **no** as the headline.

**3. Publish cost-only accounting with a completion bit, and make no success claim.** The cost
side is where the record is dense — 641 requests, 8.2M tokens, 12,980 artifacts, and three
summaries that already disagree in a way that matters. *Pros:* no estimand debate at all. A
report saying "25.0% fewer tokens in aggregate, +57% requests, median pair 29% *more* tokens, and
12 of 27 runs never completed" is publishable on the existing record and is arguably the more
useful artefact for an engineer. *Cons:* costs in the 12 stopped pairs are expenditures without an
answer, so cost-per-success is undefined there, and the per-task cost number silently changes
estimand depending on whether caps are counted. The aggregate is fragile to one case, as the
leave-one-out flip to 1.077 shows. And it drops the paper's sharpest contribution, which is about
*which runs you get to see*, not about price. *Why not chosen,* inference: the author is making
an argument about estimands, and a cost-only paper would not carry it. *Cost to test:* zero.
*Would it have won:* **maybe** — publishable, but it answers the cheaper question.

<a id="evidence-strength"></a>
## How strong is the evidence

**The single most likely way this claim is wrong:** a reader takes "[−9, +1] means projection
is roughly fine" instead of "[−9, +1] means the completed-pair tie was manufactured by the
filter." The width of that interval is exactly the 10 unexecuted arms. The missingness result is
robust; the effect sizes are not.

**Seeds: one stochastic continuation per arm**, by the paper's own statement, with no seed
replication anywhere. For an A/B whose headline is a 12/15-against-12/15 tie, that is the
binding limitation — not the bounds.

**Ablations: genuinely strong for a case study.** Table 11 compares always-full (3 failures),
always-projected (5), the frozen threshold (3) and a hindsight oracle (2, with 2.0% less logical
expenditure). 14 leave-one-source-out folds choose the same threshold in 12 of 14, with held-out
predictions giving 4 failures against the frozen rule's 3. Appendix C adds a strict whole-object
scoring contract that moves 3/5/3 to 4/6/4 **without changing the ordering**, plus a concrete
decoder counterexample, `{"a":0,"a":1}`.

**Baselines: the right control for the policy question, and no comparison at all for the system
one.** Always-full is correct. But LLMLingua, Selective Context, observation masking and
summarisation are all cited and none is run through this harness — so the paper cannot say
whether ReVerPi is a *good* context-projection design, only how to evaluate one.

**Data is the weakest dimension.** Tasks are investigator-authored over installed package
subsets, often two questions per source; the appendix states repeatedly that "source labels do
not establish independence"; the model identity is proxy-reported and "does not authenticate
backend weights"; the read-only adapter is not the complete Pi product; and raw requests, session
databases, provider configuration and invoices are not distributed, so **no dollar figure is
derivable and no independent replay is possible.** Breadth is one harness (Pi 0.84.2), one
model, one task family, 27 boundary runs.

<a id="what-axv-did"></a>
## What AXV did about it

**verified — by arithmetic re-derivation from the paper's published tables, not by
re-execution.** Run `axv-2609.31381-accounting-01` at
`experiments/runs/axv-2609.31381-accounting-01/`. **Harness:** one script,
`axv_recheck_2609_31381.py`, which transcribes Tables 3, 4, 5, 7, 8 and 11 plus the §5.1 and
§5.4 counts with the table reference in a comment beside every input, then checks **31
identities**; `metrics.json` records all 31 with the recomputed value, the paper's value, the
tolerance and a pass flag. **31/31 match, 0 mismatches.** **Runs: no seeds, and that is the
honest value rather than a missing one** — the estimand is a set of deterministic identities,
sharp by construction, so replication cannot move them. **Baseline:** always-full on the same 17
runs, from Tables 4 and 11; comparability key `arithmetic-rederivation-20260928`. **$0.00. No
pod, nothing to terminate.**

**Leaderboard warnings, verbatim:** "Not comparable to any GPU training arm. This is a CPU-only
re-derivation of the paper's PUBLISHED ARITHMETIC: it transcribes Tables 3, 4, 5, 7, 8 and 11
and checks identities among values the authors already printed. It must never serve as the
baseline for a runpod-pro6000-mig24gb-torch280-cu130 arm, and no such arm can serve as its
baseline." / "This verifies the paper's ACCOUNTING, not its CAUSAL CLAIMS. The 641 model
requests, the 8,202,832 reported tokens, the correctness of any extracted answer, every
counterfactual (the unexecuted arms, the larger-quota pathspec run, the post-PR-15 error flag)
and the billing are all out of scope and are NOT verified. The paper states the ancillary files
are not distributed and that no substitute exists for independently replaying the private
service." / "No seeds. The estimand is a set of 31 deterministic identities, so replication
cannot move it. A single execution is not being reported as a stochastic result; the result is
the identity set." / "Two further CPU-only re-derivations of the same paper,
2609.31381-a01-s1337 and verify-2609.31381-mcnemar-20260928, agree exactly on the central bounds.
Agreement across three independent code paths is corroboration of the transcription, not of the
agent trajectories."

**The caveat is the whole boundary of that `verified`.** What is **not** verified is the 641 model
requests, the 8,202,832 reported tokens, the correctness of any extracted answer, and every
counterfactual — the unexecuted arms, the larger-quota `pathspec-util` run, the post-PR-15 error
flag. All need the raw archive, and the paper's own words apply: "The ancillary files do not
provide a substitute for independently replaying the private service." A genuine re-run needs the
private provider, a pinned model and a fixed budget — on the order of 86 runs' worth of tokens, a
few dollars of API spend and **no pod**, so it is affordable to AXV in principle. It is not
reproducible from the published artifact, and no amount of arithmetic on the tables will make it
so. Carried verbatim from Appendix F: "This adaptive, complete-case sample does not acquire a
population guarantee from reproducing the formula."

**And the answer to AXV's own question, which is the useful part.** The smallest change is
smaller than a rule change: one column and one write. AXV's ledger has `metric_value` but nothing
distinguishing *a measured zero* from *a run that hit the wall clock*, and every terminated arm
currently writes a value. Four rules, in the paper's terms: a budget-terminated run records its
**endpoint, not a metric** (`metric_value` null, plus an `endpoint` reason of `budget_exhausted`,
`pod_terminated` or `wall_clock_cap` — null is not a gap in the record, it is the finding);
**never let one arm's endpoint suppress the other** (AXV sizes pods per *batch*, not per arm, so
one arm hitting the wall clock can end the batch — per-arm reservations with independent stop
decisions are the fix); **separate a bounded failure from an unexecuted arm in the type system**
and never average across them; and **never compute a delta from fewer than both arms' endpoints** —
if either arm is unexecuted there is no delta, only a bound or a note.

On the smallest n: **there is no such n, and that is the point.** The sharp finite-frame bound is
`unexecuted arms − 1 ≤ |projected − full| ≤ unexecuted arms` in task units, so a single unexecuted
arm leaves the bound at [−1, +1], which contains zero. The honest answer is always "cannot
distinguish". AXV can only tell "no difference" from "we stopped looking" by **not stopping
looking**, or by reporting a bound as a bound. The number that makes this sharp at AXV's scale:
the single largest saving in the paper's whole campaign was **one task**, and removing it flipped
the aggregate from 0.750 to 1.077. One task out of 11 jointly successful pairs was decisive in a
published campaign with 641 model requests behind it. AXV's own deltas are single-digit
percentages on a handful of runs, and any of them can be carried by one arm. So: pre-register a
practical-equivalence margin, report any interval spanning it as inconclusive rather than as a
null, publish the margin in the record *before* the run, and accept that most comparisons at this
budget will be inconclusive — and say so. Under $3.25 with 5.5 hours of total pod time, the two
arms of one comparison cost the same whether or not the first one completed. **The cheapest
available correctness win in AXV's whole experiment programme is to stop letting the first arm's
wall clock decide the second arm's existence.**

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.31381v1> · <https://arxiv.org/pdf/2609.31381v1>
- AXV memo: `corpus/2609.31381.md` in `dustin-dev-35/axv` — eight of eight sections, nothing
  omitted. Landing note and estimator addendum: `corpus/2609.31381.landing.md`,
  `corpus/2609.31381.estimator-a01a02.md`.
- AXV run: `experiments/runs/axv-2609.31381-accounting-01/`, records in
  `experiments/leaderboard.jsonl`.
- Related AXV post: [Your test rows are a row count, not an evidence
  count](/posts/overlapping-eval-windows-are-not-independent-tests/) — the same mistake in a
  different place. A nominal row count is not an evidence count, and a filter applied after the
  fact is how a null gets manufactured.
