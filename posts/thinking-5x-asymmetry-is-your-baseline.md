---
title: "Thinking's 5x bias asymmetry is a property of your baseline, not of thinking"
slug: thinking-5x-asymmetry-is-your-baseline
arxiv_id: 2609.30768
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

<!--
  loom draft provenance, not reader-facing:
  Built from the one complete Lens memo of arXiv:2609.30768v1 (corpus/2609.30768.md, commit
  e45d9c3) and the run it cites (experiments/runs/axv-2609.30768-asymmetry-01). Nothing here is
  stronger than that memo and no claim is drawn from any other source. The memo is complete —
  all seven sections present — so it cleared the completeness gate. The memo's own Notion Corpus
  page does not exist (AXV-19), so the artifact-level publish gate is closed; see the issue.
  Length: ~2,000 words against the 900–1,600 target. The alternatives section was not cut; the
  mechanism and evidence sections were.
-->

# Thinking's 5x bias asymmetry is a property of your baseline, not of thinking

**Paper:** _Does Thinking Help Fairness? Reasoning Tokens Resolve Some Biases but Create More_ — Deng Pan et al., [arXiv:2609.30768v1](https://arxiv.org/abs/2609.30768v1)
**Read:** 2026-09-28 · **Confidence:** medium · **Experiment:** verified

<a id="tldr"></a>
A 32B reasoning model with its thinking phase enabled creates about 5x more counterfactual
fairness disagreements than it repairs, and the paper reports that as an invariant across all
nine model-dataset cells. It is not an invariant: the observed ratio spans **2.4x to 48.3x**,
and 80% of the log-variance in it comes from a variable describing the *non-thinking* arm. The
real nine-of-nine result is the complementary half, and it is a better story — per pair,
thinking is **6x to 45x more inclined to undo a counterfactual disagreement than to start one**.
The caveat is that the harm is still real: 3,508 new high-confidence disagreements were created.
That is a statement about a near-degenerate baseline, not a constant of deliberation. And only
the accounting is verified here, by arithmetic re-derivation from the paper's published tables.

<a id="what-advanced"></a>
## What advanced

A measurement, not a number — and the measurement is the metric split. The literature holds two
camps with opposite verdicts on whether reasoning tokens help or hurt fairness. On the same 32B
models, the same thinking tokens, the same 5,000 records per cell, this paper shows the two
camps are reading different metrics off the same systems.

| metric | across the nine cells | reads as |
| --- | --- | --- |
| counterfactual flip rate `D_cf` | rises **9 of 9**, by +0.016 to +0.122 | thinking hurts, always |
| demographic-parity gap `D_group` | moves at most **0.017** absolute, and **flips sign across datasets** | helps on Adult, hurts on COMPAS |

QwQ-32B on Adult reads `D_group` of **-0.017** ("thinking helps") and on COMPAS **+0.034**
("thinking hurts"), from the same arms. That is a checkable reason the camps disagree, and it
needs no interpretation from AXV.

The control is genuinely good and is the paper's real strength: a within-model, within-prompt
paired ablation holds the model, the 4-bit quantisation, the template and the record fixed, and
varies only whether the thinking phase runs. Every prior result on both sides is a cross-model
or cross-prompt comparison. This is not. The group-level blind spot falls out of the same
design: aggregate rates `T^α ≈ T^α'` to within 0.014 / 0.017 / 0.012 on every entry, while the
pair-level cell-c tilt `asym(c)` reaches **0.53** on QwQ-COMPAS. A demographic-parity audit
reads the marginal and is structurally unable to see the joint.

The headline number is what does not hold up. Pooled, `c/b = 3508/620 = 5.658` against the
text's "≈5.7x" — and per cell the same ratio is 2.41, 4.57, 2.91, 23.40, 4.92, 8.39, **44.75**,
**48.30**. Two flags belong beside the good control: the headline sits on a metric of the
authors' construction (cells b and c are defined in §3.2 by this paper), and a pooled figure is
presented as a per-cell invariant.

<a id="how-it-works"></a>
## How it works

Two causal accounts, and the split between them matters more than either half.

**Why the created count outruns the resolved count — demonstrated.** The non-thinking arm is
close to flip-free on all nine cells: `D_cf` runs 0.002 to 0.032, so almost the whole pair
population sits in the agreeing state. Cell c draws on that large population; cell b can draw
only on the 0.2–3.2% already flipping. The count ratio factors exactly:

`c/b = F × G`, where `F = (1 − D_cf_nothink) / D_cf_nothink` is **entirely a property of the
non-thinking arm**, and `G = p(agree → M) / p(M → agree)` is the only term describing the
thinking transition.

`F` spans **30.1 to 498.5**, a 16.6x spread. `G` spans 0.022 to 0.168, a 7.6x spread, and is
**below 1 in all nine cells**. The observed ratio spans 20.1x. Decomposing the log-variance:
**80% from `F`, 20% from `G`**, with `pearson(ln F, ln c/b) = 0.872` and `spearman(F, c/b) =
0.867`. The count ratio is a baseline-population artefact wearing a reasoning costume.

The authors say so themselves. §4.4 calls the asymmetry "a structural consequence of any
non-trivial transition probability acting on an imbalanced nothink population." Appendix H,
Table 12 goes further: an explicit independence model with *no* within-pair correlation already
predicts `|c| > |b|` in every cell, and the observed ratios come in **5 to 100x below** that
first-order prediction. The mechanism section is the stronger contribution. The gotcha is in
the abstract, not in the paper.

**Why thinking is a confidence amplifier — asserted, and partly circular.** The anchor/mover
account is evidenced by `CDPG` trajectories rising in cells c and d and decaying in cells a
and b. But cell c is *defined* as "the pair flipped under thinking", so averaging `|CDPG_K|`
inside cell c and obtaining 0.835 is entailed by the definition rather than evidence for it.
The non-tautological part — the depth profile and the anchor/mover split — rests on 54, 56 and
**16** cell-c pairs (Table 6), with no spread, no interval and no seed reported on any
trajectory in the paper.

<a id="roads-not-taken"></a>
## The roads not taken

**1. Report the rate ratio, not the count ratio.** Replace `|c| / |b|` with
`p(agree → M) / p(M → agree)`: the per-pair rate at which thinking flips an agreeing pair
against the rate at which it returns an already-flipping pair. Mechanism: the count ratio is a
product of a transition rate and a starting-population ratio, and only the first term is about
thinking. *Pros:* computable from Tables 4, 13 and 14 as already printed, so it costs nothing
and needs no new inference; it stays inside one order of magnitude across cells where the count
ratio spans 20x; and it is the stronger claim, because it is true in **all nine** cells rather
than in the median. *Cons:* it throws away the operationally important half. If the baseline
barely flips, then thinking producing 105 new counterfactual disagreements is a real harm
whether or not the rate ratio is flattering, and a reader given only `G` could conclude the
problem is smaller than it is. A practitioner needs the created count; a mechanism claim needs
the rate. *Why not chosen* (inference): the count ratio is what survives an McNemar test on
paired binary outcomes, and the authors built a paired design around it. *Cost to test:* zero,
arithmetic on published tables. *Would it have won:* **yes**, and it is a better paper.

**2. Swap the non-thinking arm for a real one, and drop `CDPG`.** Two independent changes to
one design. First, Qwen3-32B ships a trained `/no_think` mode, and the paper's baseline is
instead a pre-filled empty `<think></think>` block — a prompt hack the authors concede in §6
("a small fraction of generations may still emit reasoning tokens after this prefix"). Second,
drop the `CDPG` instrument: the headline comes from Table 2, which is one greedy decode per arm,
so it needs 45,000 decodes, not the stated 900,000 forward passes. *Pros:* a control designed
for the purpose instead of inferred from a prefix, and a **95%** compute drop, which on a small
budget is the difference between a feasible and an infeasible replication. *Cons:* the
within-model pairing that makes the McNemar test valid is partly lost, because `/no_think` is a
mode boundary the model was trained across rather than a single forward pass; and removing
`CDPG` deletes the anchor/mover account, the only evidence that thinking is a *directional*
sharpening rather than added noise — the paper would keep the result and lose the explanation.
*Why not chosen* (stated for `CDPG`): the paper is explicitly diagnostic and positions the
instruments as the contribution. *Cost to test:* one 8B model, one dataset, both arms, well
under an hour. *Would it have won:* **maybe** — the cheaper, more honest control is clearly
better, but the within-model pairing is a real design strength.

**A third test AXV was asked to run, which cannot answer the question as posed.** The idea was
to re-run the ablation on a set where the two options differ only on an attribute the model has
never seen varied, and read a surviving ratio as "the finding is about reasoning." That
inference does not hold. Swapping the attribute changes *what is being protected* but leaves
the quantity that drives the ratio untouched: the non-thinking arm will still be near
flip-free on a weak attribute, so `F` stays large and `c/b` stays large. A surviving ratio
would show the same near-degenerate baseline — a false positive for the reading the test is
meant to avoid. The construct that has to vary is `D_cf_nothink`, and the cheapest way to vary
it is not a new run at all: hold `G` fixed and read the ratio off the nine existing cells, where
`D_cf_nothink` already spans 0.002 to 0.032. The paper's own Table 12 did the stronger version,
and the arithmetic is the run below.

<a id="evidence-strength"></a>
## How strong is the evidence

**Most likely way this is wrong, and it is a misreading rather than a defect.** A reader takes
"roughly 5 times in all nine" as a constant of thinking. It is the pooled value of a ratio whose
per-cell values span 2.4x to 48.3x, and 80% of the variance behind it belongs to a baseline
population that is a property of three datasets rather than of reasoning. The McNemar tests are
decisive for `c ≠ b`, a much weaker claim than `c ≈ 5b`, and the paper's significance column
tests the former while its headline asserts the latter. The paper is not concealing this: Table
12 prints the per-cell ratios and §4.4 names the structural cause. **Second, and independent:**
the `CDPG` depth-resolved trajectory rests on 16 to 56 pairs with no spread reported, and its
headline average is partly entailed by the cell definition. Do not read it as strong evidence.

**Seeds: one, and correctly.** Greedy decoding (T=0) makes each flip a deterministic function
of the trace, the right way to rule out *sampling* variance in the c-versus-b comparison. It does
not rule out the variance that matters. Quantisation, prompt template and dataset sample are
each fixed at one setting, so there is no way to separate a property of thinking from a
property of this prompt under this quantisation. The 5,000 records are a single unreported
sample of 48,842 on Adult.

**Ablations: partial, and pointed at the wrong target.** Appendix C sweeps the `CDPG`
segmentation `K ∈ {5, 10, 20}`, but only on Qwen3-32B, only on the propagation *slope*, and
`c/b` is invariant to `K` by construction — the ablation cannot move the headline. Appendix D
adds two off-lineage models at N=1,000 and is the most valuable check in the paper. There is
**no** ablation of the empty-block baseline, **no** ablation of the natural-language template,
and **no** contamination test.

**Data is the weakest dimension, and it is unaddressed.** Adult, COMPAS and Credit are among
the most widely reproduced tabular datasets in existence, and a 32B model has near-certainly
seen the UCI Adult CSV *with labels* in pretraining. Rendering to prose with a deterministic
template blocks memorisation of the prose form, not of the record-to-label mapping. A
memorising model produces near-deterministic answers that move only under attention, which is
exactly the regime where this effect lives. No held-out or synthetic split is run. The paper
also never reports how many of the 3,508 created flips were decided by a side within ~0.1 of the
0.5 threshold — the single number that would bound how much of the effect is quantisation plus
jitter. Effective N falls to 1,430 on R1-COMPAS because the non-thinking arm refuses to answer
on 72% of records.

<a id="what-axv-did"></a>
## What AXV did about it

**verified** — and specifically *verified by arithmetic re-derivation from the paper's published
tables, not by re-execution.* Run `axv-2609.30768-asymmetry-01`, cohort
`cpu-only-arithmetic-rederivation-20260928`. **No pod, no GPU, 0 GPU-seconds, $0.00 of the
$3.25 budget**, so no baseline-reuse decision arose and no baseline was re-run. Wall clock 660 s.
**Zero seeds, and that is the honest value rather than a missing one:** the estimand is a set of
9 deterministic identities on counts the authors already printed, so replication cannot move
it. A single execution is not reported as a stochastic result; the result is the identity set.

Harness: one script, `axv_recheck_2609_30768.py`, transcribing Tables 2, 4, 7, 9, 12, 13 and 14
with the table reference in a comment beside every input, then checking **9 identities. 9/9
matched, 0 mismatches.** They are: `a + b + c + d = N` in all cells; the pair-state row counts
reproducing `N`, which is what validates the transcription (exact 9/9); cell `b` from Table 4 as
75/143/23 against the published 75/143/23; cell `c` within 2.0 pairs, the rounding floor of
3-decimal conditionals; cell `d` exact as 32/2/1; the nine per-cell ratios against Table 12's
own `actual` column all within 0.35; pooled `c/b = 5.658` against "≈5.7x"; the decomposition
`c/b = F × G` in 9/9 with `F` reproducing Table 9's `D_cf` column from row counts; and the
parity baseline — at `D_cf_nothink = 0.087` the ratio is 1, a rate the paper's own non-thinking
arm never reached in any cell (observed 0.002–0.032) but which is an ordinary minority flip rate.

**The decomposition, which is the point of the run.** Pooled, `5.66 = 59.2 × 0.0956`.

| cell | N | b | c | c/b | F (nothink) | G (thinking) |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-Adult | 5000 | 75 | 362 | 4.83 | 45.7 | 0.106 |
| Qwen3-COMPAS | 5000 | 143 | 344 | 2.41 | 33.5 | 0.072 |
| Qwen3-Credit | 4996 | 23 | 105 | 4.57 | 207.2 | 0.022 |
| QwQ-Adult | 5000 | 152 | 443 | 2.91 | 30.1 | 0.097 |
| QwQ-COMPAS | 5000 | 15 | 351 | 23.40 | 332.3 | 0.070 |
| QwQ-Credit | 4984 | 121 | 595 | 4.92 | 39.2 | 0.125 |
| R1-Adult | 4999 | 77 | 646 | 8.39 | 50.0 | 0.168 |
| R1-COMPAS | 1430 | 4 | 179 | 44.75 | 356.5 | 0.126 |
| R1-Credit | 4995 | 10 | 483 | 48.30 | 498.5 | 0.097 |

The genuine, consistent, nine-of-nine finding is the other half: **in every cell, thinking
returns an already-flipping pair to agreement 6x to 45x more often per pair than it flips an
agreeing pair.** That is a real property of the thinking transition, it is the paper's better
claim, and it is not the number the abstract leads with.

**Leaderboard warnings, copied verbatim.** "Not comparable to any GPU training arm. This is a
CPU-only re-derivation of the paper's PUBLISHED ARITHMETIC: it transcribes Tables 2, 4, 7, 9, 12,
13 and 14 and checks identities among values the authors already printed. It must never serve
as the baseline for a runpod-pro6000-mig24gb-torch280-cu130 arm, and no such arm can serve as
its baseline." / "This verifies the paper's ACCOUNTING, not its CAUSAL CLAIMS. Every model
generation, every logit, the CDPG instrument, the Bias Transition Matrix, the anchor/mover
account and the asym(c) tilts are out of scope and are NOT verified. The paper's contamination
status on three memorised tabular benchmarks is untested." / "No seeds. The estimand is a set
of 9 deterministic identities, so replication cannot move it." / "The AXV leaderboard tool's
'baseline' subcommand is BROKEN: NameError: name 'cohort_alerts' is not defined at
axv_leaderboard.py:302. The substantive pre-check was run through 'search', which reported 'no
matching runs' for this fingerprint. Reported, not fixed here." / "Leaderboard 'verify' reports
364 problems across 61 pre-existing records, including duplicate run_id
verify-2609.30721-typei-20260928 appearing 20 times and verify-2609.31381-mcnemar-20260928
appearing 8 times. Both predate this run."

**What this does not verify, and it is the whole boundary of the word `verified`.** Every model
generation, every logit, `CDPG`, the Bias Transition Matrix, the anchor/mover account and the
`asym(c)` tilts are untouched. A within-pair bootstrap over the 3,508 created and 620 resolved
pairs needs only the per-pair Yes/No predictions the paper does not publish; the released code
at `github.com/pd90506/fairness_audit` is stated to contain them, and that is the one check
worth a GPU, because it would move every count here from the authors' arithmetic to AXV's
measurement. **The paper's causal claim about thinking is not verified by this run, and nothing
here should be read as verifying it.** The paper's own words apply: "The paper is diagnostic: it
introduces two dynamic instruments … and evaluation of concrete mitigation strategies against
these instruments is left to future work."

<a id="links"></a>
## Links

- arXiv: <https://arxiv.org/abs/2609.30768v1> · <https://arxiv.org/pdf/2609.30768v1>
- AXV memo: `corpus/2609.30768.md` in `dustin-dev-35/axv` — all seven sections present, full
  text including Appendices A–I.
- AXV run: `experiments/runs/axv-2609.30768-asymmetry-01/`; record
  `lb-axv-2609.30768-asymmetry-01` in `experiments/leaderboard.jsonl`.
- Related AXV posts: [Your test rows are a row count, not an evidence count](/posts/overlapping-eval-windows-are-not-independent-tests/)
  — a different measurement defect, the same discipline: a pooled number is not an invariant.
  [Your 12/15 tie was manufactured by the filter, and no seed count repairs it.](/posts/completed-pairs-hide-capped-failures/)
  — a paper whose *appendix* is the real result, which is also the pattern here.
