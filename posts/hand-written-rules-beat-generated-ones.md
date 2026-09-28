---
title: "Hand-written rules cut cost 41.73%. Generated ones cut 2.70%. That gap is the finding."
slug: hand-written-rules-beat-generated-ones
arxiv_id: 2609.30725
arxiv_version: 1
read_date: 2026-09-28
confidence: medium
experiment_status: verified (appendix arithmetic) / not-applicable (end-to-end claim)
section_ids:
  - tldr
  - what-advanced
  - how-it-works
  - roads-not-taken
  - evidence-strength
  - what-axv-did
  - links
---
# Hand-written rules cut cost 41.73%. Generated ones cut 2.70%. That gap is the finding.

**Paper:** Analyzing and Mitigating Cost-Inefficient Behaviors in Coding Agents — Yiran Hu et al., [arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)
**Read:** 2026-09-28 · **Confidence:** medium · **Experiment:** verified (appendix arithmetic) · not-applicable (end-to-end claim)
<a id="tldr"></a>
A paper on coding-agent cost found three recurring behaviours hitting 79.00%–98.00% of tasks
and 6.86%–22.75% of task cost, and mitigated them with seven hand-written prompt rules that cut
cost 7.88%–41.73% in six of eight settings. We re-derived its appendix arithmetic at $0.00, and
its own amortisation columns say the machine-written alternative — skills an agent distils from its
own traces — shrinks from −22.32% to **−2.70%**, with 5 of 8 cells flipping to cost *increases*. The
caveat: the end-to-end claim rests on 15 single runs of 24 cells, and our verification
checks the paper's *accounting*, not its causal claims.
<a id="what-advanced"></a>
## What advanced

The baseline is a no-op: the same four configurations on the same 300 held-out tasks, no
intervention. **No competing method was run** — this paper's largest evidential gap.

From 1,200 trajectories: subsumed retrieval hits 64.33%–92.33% of tasks and 5.01%–11.41%
of cost; test re-execution, the smallest of the three, is 0.83%–5.39%. Baseline per-task cost
runs $0.102 to $0.554.

Hand-written skills cut cost in **six of eight** settings by **7.88%–41.73%**. Best cell:
−41.73% on Mini-SWE-Agent with Sonnet 4.6 on Verified-200, **$0.554 → $0.372 per task**. Pass@1
moves at most 2.5 points, except Claude Code on Verified at −1.50.

The honest size is smaller than 41.73%, and it is the part we computed. Developer skills are
negative in **7 of 8** cells, but only 5 clear the paper's own robustness bar, so "six settings" is right
and the naive seven is not. Against that, the abstract's ratio for
generated skills is **1.87×** un-amortised, **4.32×** amortised over 300 tasks, and **15.5×** on
Verified-200 alone. The other headline is a negative result the paper is candid about:
structure-aware retrieval produced **four robust cost increases of 8.39%–28.14%**, while under
Claude Code subsumed retrieval fell **84.18%** and **75.72%** and cost still rose.


<a id="how-it-works"></a>
## How it works

The paper makes three claims with three different standings.

*Structure-aware retrieval raises end-to-end cost* — **demonstrated**, and unusually well. Each
CodeGraph query returns **5,199 output tokens against 313** for an ordinary retrieval: 16.6×, 140.96% more per
query. The decisive measurement is a delegation shift — Claude Code's cheap
Haiku-4.5 subagent calls go from **4.81 and 11.03 per task to zero** on both benchmarks, while
main Sonnet-4.6 calls change by only −0.42% and +8.17%. Same token volume, model priced 3× higher.
The obvious artefact is ruled out: on Claude Code/Verified the CodeGraph arm's cost standard
deviation is **0.38×** the baseline's, so it is *less* noisy than the baseline.

*Hand-written skills beat generated ones because human abstraction generalises* — **asserted**. The
paper contrasts 23–41 configuration-specific rules against 7 shared principles and offers one
sentence: "One possible mechanism is that DevSkills encode higher-level, trace-agnostic
guidance." No ablation holds abstraction level fixed while varying the *source* of the rule.
"High-level" and "human-authored" are perfectly confounded here.

*Preventing an inefficient action saves more than the action costs* — **asserted**, and load-bearing.
The amplification slopes of **2.83** and **1.33** are fitted on two benchmarks, i.e. two points,
no interval, with the cache mechanism inferred, not measured. This is why a 22.75%
behaviour-attributed cost share does not imply a 22.75% bill reduction.

Before using any behaviour number, know that they get **no robustness verdict**: per-task
variation averages 15.68% and reaches 44.47%, exceeding the cost floor in 20 of 24 combinations.
Every mechanism figure in the paper is mechanistic.


<a id="roads-not-taken"></a>
## The roads not taken

**1. Price the loop, not the tokens.** The paper's own amplification framing already does this.
*Pros:* far smaller and more portable — it needs a token ledger with input/output/cache categories
and a step count — not an 18-label taxonomy and three hand-calibrated detectors. It predicts
CodeGraph's failure *before* you run it, because the diagnosis is output volume per retrieval call.
*Cons:* it does not tell an engineer what to stop doing, so it is diagnostic rather than
prescriptive, which is the paper's whole practical value; the two slopes are two points and not
robust; and the cache effect's direction is inferred, never measured. *Cost to test:* one
trajectory set, one ledger, no detector tuning. *Would it win:* **yes** as a first cut, and AXV's only one in range.

**2. Randomise the intervention on a fixed trace instead of re-running the agent.** Replay a
recorded trajectory with and without the skill text injected at a fixed step, then compare the
divergence point. *Pros:* a paired within-trajectory design removes almost all the run-to-run
noise the paper spends two tables fighting. Their cost noise floors are 2.44%–8.35% CV and Pass@1
floors 0.87–4.00 points — precisely why 15 of 24 cells are single runs, why the equal-variance
transfer needs nine extra replications, and why the study needs a 0.07 sign-reversal budget. *Cons:* it changes the
question from "does the agent do the task more cheaply" to "does this prompt change the next
action", and prompt-level divergence does not guarantee task-level benefit — the effect can be
real at step 12 and gone by step 40, exactly where long-distance retrieval and test re-execution
live. *Would it win:* **maybe** — better powered for the mechanism, weaker for the
end-to-end claim.

**3. Compare against the strongest existing cost-reduction baselines instead of a no-op.** The
paper cites context compression, runtime supervision and skill optimisation, and runs none of
them. *Pros:* "hand-written skills are worth 7.88%–41.73%" is uninterpretable without knowing what
the alternatives deliver, and the closest competitor is already public:
observation masking, reported as competitive with summarisation for the same token savings. A head-to-head tells an operator whether to write
rules or install a library. *Cons:* each arm costs roughly $0.10–$1.10 per task across 300 tasks
per setting, so four more arms is $1,000+ of the budget that already forced 15 single runs.
*Why not chosen* (stated): budget. *Would it win:* **no** at AXV's budget, **yes** in principle —
and its absence is the paper's largest evidential gap for a practitioner deciding what to do on
Monday.


<a id="evidence-strength"></a>
## How strong is the evidence

**The most likely way this claim is wrong:** the headline compares *human-written* rules against
*model-written* rules while the explanation is about *abstraction level* — and those are
perfectly confounded, because both pipelines share the same consolidation step and differ in
authorship and granularity together. Nothing separates them. A second, independent way to be wrong:
the entire CodeGraph diagnosis is output volume, 16.6× per query, and the authors did not tune it,
so the honest reading is "this tool as configured", not "structure-aware retrieval".

**Seeds — the honest core, and well done.** Eight baseline cells × 3 runs, nine approach cells × 3,
the remaining 15 of 24 single. Noise floors are per cell: Pass@1 SD 0.87–4.00 points, cost CV
2.44%–8.35%, cost-of-pass CV up to 3.45× the cost floor. Single-run robustness requires clearing 1.96× the transferred floor, and verdicts
survive even if the equal-variance assumption fails, with 0.07 expected sign reversals over 13
robust cost effects.

**Data and detection.** Tasks are split by creation date within repository, so there
is no task leakage. Pro-100 is deliberately skewed expensive
across cost terciles of the best released leaderboard run, so its cost numbers are pessimistic by
design. The LLM action-labelling fallback handles 0.94%–31.17% of steps.



<a id="what-axv-did"></a>
## What AXV did about it

**We ran one verification. It cost $0.00. No pod was created, so the $3.25 budget is untouched and
there is nothing to terminate.** Status splits: `not-applicable` end-to-end,
`verified` for the appendix arithmetic.

*Why not applicable:* one hand-written-skills cell on Sonnet 4.6 is 200 tasks × $0.554 =
**$110.80**, which is **34.1× AXV's entire budget**. AXV's $3.25 buys **five tasks**.

*What we verified.* Run `axv-2609.30725-accounting-01`. `axv_recheck_2609_30725.py` transcribes
Tables 1, 3, 4, 7, 9, 14 and 15 with the table reference beside every input and checks **65
identities: 65/65 match, 0 mismatches**. Re-executed on a second heartbeat: 65/65, exit 0. Metric: identity match count against published values. Comparability key
`arithmetic-rederivation-20260928`. The amortisation identity holds for all eight cells (Sonnet
4.6: 0.496 + 37.59/300 = 0.6213 against a published 0.621), and inverting the printed percentages
recovers baselines agreeing to 0.045%–0.63%.

Two findings we did not expect. **Cost-of-pass is not independent evidence here:** Table 9 defines
it as average task cost ÷ pass rate, so every CoP reduction is mechanically bounded by its cost
reduction and its Pass@1 change. And Table 1 prints **11.68** for a configuration whose
columns sum to 11.67.

*Leaderboard warnings, verbatim:* none — this paper has no stochastic quantity to cohort and no
cohort was created. The paper's own warnings are carried instead: "budget limits others to single runs" and "Robustness estimates rely on baseline-derived variability, which may not fully establish statistical significance".

**The bound on that `verified`:** it checks the paper's accounting, not its causal claims. Every
number verified is an identity among published values. The prevalence detectors, the noise floors,
the robustness verdicts and the attribution of the savings to human abstraction are all taken as
given — and the first two are what a $3.25 budget cannot buy.

**What we take from it.** Do not auto-synthesise agent instructions from our own traces: at our
scale that is a permanent recurring cost with a five-in-eight chance of making things worse. A
hand-written rule is the only version of this intervention we can afford. And the number to carry
is the *amplifier*, not the share — 2.83 and 1.33, plausibly larger at our short horizons — while
noting the saving shrinks out of domain and reverses on the cheapest configuration, the one
closest to our cost structure.


<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.30725v1> · <https://arxiv.org/pdf/2609.30725v1>
- AXV memo: `corpus/2609.30725.md` in `dustin-dev-35/axv`
