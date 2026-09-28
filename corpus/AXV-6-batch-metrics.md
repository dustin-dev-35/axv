# AXV-6 batch synthesis — are the metrics we budget and conclude against real?

Three papers, one question. Lens reading batch, 2026-09-28. Children: AXV-8 (2609.30721v1),
AXV-9 (2609.31381v1), AXV-10 (2609.30725v1). Full memos in `corpus/2609.30721.md`,
`corpus/2609.31381.md`, `corpus/2609.30725.md`. This file is the batch-level answer. It is not
a substitute for the memos and it does not restate them.

## The short answer

**No. Not one of the three is a metric AXV should be concluding against as published, and the
reason is the same in all three cases: each headline number is conditional on a design choice
the paper does not release, and AXV's own protocol is weaker than the effect sizes in every
one of them.**

Concretely, four things follow and they are the actionable output of this batch.

## 1. AXV's `delta` is not a measurement, and at n=3 it cannot become one

This is from 2609.31381v1 and it is the most important number in the batch.
Verification run `verify-2609.31381-mcnemar-20260928`, leaderboard record
`verify-2609.31381-mcnemar-20260928:n3-cannot-fire`.

| true paired difference | arms at | n for 80% power |
| --- | --- | --- |
| +10 pp | 0.90 vs 0.80 | **217** |
| +20 pp | 0.90 vs 0.70 | **72** |
| +40 pp | 0.90 vs 0.50 | **26** |
| +10 pp | 0.80 vs 0.70 | 315 |
| +10 pp | 0.70 vs 0.60 | 379 |
| +10 pp | 0.60 vs 0.50 | 412 |

And the floor underneath all of it: **at n = 3 the exact two-sided paired test cannot reach
the 0.05 level at all.** The minimum attainable two-sided p-value with 3 pairs is 0.25, and
the empirical rejection rate under the null was 0.0000. It is not a weak test, it is a test
that cannot fire.

These are *optimistic* lower bounds. AXV's seeds inside one batch share the data shard, the
pod and the wall-clock budget, so within-batch correlation pushes the true requirement
**higher**, not lower. The relevant contrast is with the paper's own power requirement in
2609.30725v1: detecting a 10-point cost difference there needs 80% power against a baseline
cost CV of 2.44–8.35%, achieved with 3 replicates per baseline cell and a 1.90s minimum
robust effect. AXV is two orders of magnitude away from that, on a budget of $3.25 total.

**Consequence for AXV's schema.** `experiment_runs.delta` as currently defined cannot be
compared to anything and must not be reported with a p-value or a confidence interval. The
honest fields are: the point difference, the n, the seed list, the censoring state, and — when
censoring occurred — the finite-frame bound instead of a point estimate.

## 2. Censoring is the smaller half of the problem, and it is free to fix

2609.31381v1's arithmetic, independently recomputed and confirmed
(`verify-2609.31381-mcnemar-20260928:paper-recheck`, `matches_paper: true`): 15 completed pairs
give 12/15 correct for each arm, an exact tie. All 27 realized intervention boundaries give
projected-minus-full in **[−9, +1] tasks, [−33.3, +3.7] pp**. A true 33-point deficit appeared
as an exact zero because the runner suppressed the companion whenever the first arm failed to
complete: `Pr(M_i2 = 1 | C_i1 = 0, A_i1, X_i) = 0`.

Censoring did not shrink a small effect. It removed every observation that carried it.

The smallest change that fixes it is a scheduling rule, not an estimator: **do not gate the
companion on the first arm's completion.** It costs no code. It costs dollars, and AXV cannot
currently pay it — $3.25 is 5 h 31 m of pod time company-wide at $0.59/hr. So the interim is
the third alternative in the AXV-9 memo: report the bound, not the estimate, and never report
it with a confidence level, because it is sharp only for a fixed recorded frame.

## 3. Where AXV is actually exposed, which is narrower than the paper says

2609.30721v1 says overlapping or shared test rows make an IID interval on a paired comparison
anti-conservative, and that is true and replicates. But the paper's dramatic target-
misalignment result — IID Type-I 72.4% against equal-subject 5.5% — depends on a design choice
the paper does not release, and my sweep (`verify-2609.30721-typei-20260928`, 63 conditions,
3 seeds, M = 1,000 per condition) found something sharper.

A **shared** subject/session difficulty shift moves both arms together and **cancels in
C_A − C_B**. IID Type-I under shared-difficulty heterogeneity was **0.059**, essentially
nominal. Target misalignment only appears when the heterogeneity acts on the **model-pair
difference**, and then it is severe: IID **0.776**, within-session HAC **0.800**, equal-subject
paired **0.032**.

Since AXV's `delta` is always a paired contrast, this is a real narrowing of the risk. AXV is
largely protected against the shared-difficulty form and exposed to the differential form.
In operational terms: AXV is safe when both arms see the same data, the same seed family and
the same difficulty, and unsafe when something makes one arm systematically easier on a subset
of the runs.

The direction of the paper's claim did replicate across the whole sweep. IID Type-I at 75%
overlap ran **0.069 (rho=0) to 0.210 (rho=0.99)** against nominal 0.05, while session-centred
HAC ran **0.036 to 0.083** over the same surface, and the IID−HAC gap was non-negative at every
overlap and every persistence level. The *magnitudes* did not replicate and could not: the
paper does not release its DGP parameters, and its headline 16.9% sits somewhere between this
sweep's rho=0.95 (0.100) and rho=0.99 (0.210).

One decomposition worth keeping: nominal row growth at 75% overlap is 3.97x, information
growth is 2.81x with mechanical overlap alone and 2.62x at rho=0.99. **Mechanical overlap costs
41% of the nominal information; AR(1) persistence adds only 7% more.** For AXV the shared
structure, not the error persistence, is the dominant price of "just run more rows".

## 4. The cost paper's transferable result is a shape, not a number

2609.30725v1's 41.73% is a comparison between a human's 7 principles tuned on 1,200
trajectories of exactly their two benchmarks and a model's 23–41 rules generated from the same
1,200 trajectories, with **15 of 24 approach cells at n = 1** and **no published token price
schedule** — so no dollar figure in that paper is independently reproducible. On the paper's
own appendix arithmetic, charging the $37.59 and $22.76 synthesis costs collapses the two
largest agent-synthesised savings to −2.70% and −0.49% and leaves **no setting with a robust
cost-of-pass improvement**.

What survives is narrower and more useful: **a small number of human-authored behavioural
principles measurably reduce agent cost without measurably reducing Pass@1, and a much larger
automatically generated rule set does not.** AXV already writes its instructions this way, so
this one needs no experiment — it needs AXV to notice it is already doing the thing that
worked.

The paper's other result is a clean negative and AXV should not repeat its mistake:
structure-aware retrieval cut Claude Code's subsumed retrieval by 75.72–84.18% and still
**increased** cost by 8.30% and robustly 12.19%, because it pushed work off a model priced 3x
cheaper. A metric moving in the right direction is not a cost moving in the right direction.

## What this costs

**$0.00.** No RunPod pod was provisioned in this heartbeat and none exists. Total account
spend remains $0.0151 from a pre-existing pod. Budget remaining: **$3.25 of $3.25.**

Both verification runs are CPU-only and are recorded in cohort `cpu-only-2026-09-28`, which is
**not comparable** with any `runpod-pro6000-mig24gb-torch280-cu130` record. That warning is on
every leaderboard record verbatim. Neither run is a replication of its paper's simulation: the
estimator is the paper's, the data-generating process is AXV's, and the design was swept over
dependence strength rather than tuned to match the paper's published numbers. Tuning to match
would have made the test circular.

## What is still missing from the record

- **Notion Corpus, Supabase index, PostHog events: not written.** All three connections report
  `state: ready` through `connections_search`, but this agent run has exactly two bound tools
  (`connections_search`, `connection_request`) and no `mcp__notion__*`, `mcp__supabase__*` or
  `mcp__posthog__*` namespace. Confirmed by `tools/list` on the runtime-tools MCP endpoint.
  This independently reproduces the AXV-1 and AXV-2 findings rather than relying on them. GitHub
  *is* writable and the memos, the run directories and `leaderboard.jsonl` are committed there.
  So the corpus has its versioned history and is missing its canonical page and its index. The
  memos are durable; they are not filed in the three places the storage contract requires.
- The 2609.30725v1 transfer question is unrun, and the reason is cost, not capability. It is
  recorded in the memo as `not-applicable` with the harness named.
- AXV-11, AXV-12 and AXV-13 (2609.31098v1, 2609.30768v1, 2609.31563v1) are standalone children
  of AXV-2 and were **not** read in this heartbeat. This wake was scoped to AXV-6.
