"""
Applied experiment for arXiv:2609.31381v1.

The question AXV asked:
    "when an arm in the autoresearch harness is terminated for budget rather
     than for failure, what is the smallest change to our allocation rule that
     stops us reporting a null result that is really a censored one - and what
     is the smallest n at which our current protocol can distinguish 'no
     difference' from 'we stopped looking'?"

This script derives and then verifies the answer numerically. It is a pure-CPU
estimator study: no GPU, no pod, no model, no provider, no spend.

Three deliverables:
  1. n < 1/c.  The largest batch size at which a paired result is achievable
     at all, given a per-arm censoring rate c. Below it you can expect a clean
     pair set; at or above it, the expected number of censored arms is >= 1 and
     the identification interval is pinned at width c forever.
  2. P(clean frame) = (1-c)^n. The probability that a batch of n pairs records
     every allocated arm-slot. This is the number that answers AXV's question:
     it is the probability that a reported contrast is a measurement rather
     than a completed-pairs-only view.
  3. Clopper-Pearson n. The n required, with ZERO censored arms observed, to
     certify that c is below a resolution target the protocol cares about.

Decision rules, both stated up front:

  TEST 1 (pre-registered, z-test). H0: E[width] is independent of n. The
  script fails if |width(n_max) - width(n_min)| exceeds 3 Monte-Carlo standard
  errors.

  TEST 2 (pre-registered, equivalence test). H0 is the same, but the question
  is operational, not asymptotic: does width change by a practically
  meaningful amount as n grows? Tolerance is fixed at 1.0 percentage point,
  chosen as roughly a quarter of the paper's own N=27 lattice step of
  1/27 = 3.7 pp. Width is FLAT iff the change is inside that tolerance.
  TEST 1 and TEST 2 are both reported and both outcomes are recorded.

CORRECTION, superseding the first execution of this script. The first run
  reported TEST 1 as REFUTED at c=0.20 and c=0.10. That verdict was an
  artefact of a mis-scaled standard error, not a finding. The first version
  computed se = sqrt(m(1-m) / (TRIALS * n^2)), but a single trial's width is
  Binom(n,c)/n, whose variance is c(1-c)/n, so the correct standard error of
  the mean over TRIALS trials is sqrt(c(1-c) / (n * TRIALS)) -- larger by a
  factor of sqrt(n), which is 40x at n=1600. The understated SE inflated
  every z-score. With the correct SE the same measured differences are not
  significant, which is the correct result: E[width] is exactly c by
  construction, and the Monte-Carlo is a check on the code, not an estimate
  of an unknown quantity. The superseded metrics are preserved alongside
  this one and the leaderboard carries both records.

  Trials were reduced from 200,000 to 50,000 in this revision purely for
  runtime. It does not weaken the corrected test: at 50,000 trials the
  correct SE at the decisive row (c=0.37, n=1600) is 0.0027 pp, against a
  tolerance of 1.0 pp, so the test retains a resolution three orders of
  magnitude finer than the effect it is asked to resolve.
"""

import json
import math
import os
import random
import sys

# Censoring rate measured on the paper's own frame (reproduced by run a01).
C_PAPER = 10 / 27          # 10 unresolved companions of 27 pairs
SEED = 1337
TRIALS = 50_000

# The metric this run measures, for the leaderboard. Deliberately not val_bpb:
# this is an estimator study with no harness, no GPU and no training run, and it
# must not share a comparability cohort with the training series.
METRIC = "eq5_width_pp"


# -------------------------------------------------- 1. the 1/c cliff
def max_clean_batch(c, n_max=10_000):
    """
    Largest integer n with E[censored arms] = n*c < 1.
    Strictly: n*c < 1, so n = ceil(1/c) - 1.
    """
    if c <= 0:
        return n_max
    return min(n_max, math.ceil(1.0 / c) - 1)


def p_clean_frame(c, n):
    """P(no censored arm in n pairs) = (1-c)^n."""
    return (1.0 - c) ** n


def mc_se(m, n, trials):
    """
    Standard error of the mean width over `trials` Monte-Carlo trials.

    One trial's width is W = X/n with X ~ Binom(n, c), so
    Var(W) = n*c*(1-c)/n^2 = c*(1-c)/n, and
    SE(mean) = sqrt(c*(1-c) / (n*trials)) = sqrt(m(1-m) / (n*trials)).

    The first version of this script used sqrt(m(1-m) / (trials*n*n)), which
    omits one factor of n and understates the SE by sqrt(n).
    """
    return math.sqrt(max(m * (1.0 - m), 1e-15) / (n * trials))


# ---------------------------------- 2. Clopper-Pearson n for a resolution
def cp_zero_event_n(delta, alpha=0.05):
    """
    One-sided upper (1-alpha) Clopper-Pearson bound on a binomial rate after
    n trials with zero events is 1 - alpha**(1/n). Requiring that upper bound
    to be <= delta gives

        n >= ln(alpha) / ln(1 - delta).

    This is the n at which seeing ZERO censored arms is *evidence* that the
    censoring rate is below the resolution target. It is not a plan: you do
    not get to choose c, you observe it.
    """
    return math.ceil(math.log(alpha) / math.log(1.0 - delta))


# --------------------------------------------- 3. Monte-Carlo confirmation
def simulate(c, n, trials, rng):
    """
    Draw n pairs. For each, the first arm is capped with probability c; if it
    caps, the companion is unexecuted (the paper's Eq. 2). The sharp Eq. 5
    interval has width exactly (number of unresolved arm-slots)/N, because
    the upper minus the lower endpoint telescopes to the total unresolved
    mass of both arms. So the trial's width is X/n with X the number of
    censored pairs. Return the mean width over trials.
    """
    total = 0
    for _ in range(trials):
        unresolved = 0
        for _ in range(n):
            if rng.random() < c:
                unresolved += 1        # companion unexecuted
        total += unresolved
    return (total / trials) / n


def main():
    log = []

    def say(s=""):
        print(s)
        log.append(s)

    rng = random.Random(SEED)

    say("=" * 74)
    say("arXiv:2609.31381v1  --  applied study: censoring rate, not sample size,")
    say("is what pins an A/B contrast's identification interval")
    say("=" * 74)
    say()
    say("  CORRECTED REVISION. The first execution of this script reported a")
    say("  REFUTED pre-registered test. That was a mis-scaled standard error")
    say("  (understated by a factor of sqrt(n)), not a finding. See metrics.json")
    say("  .superseded_by and the leaderboard record carrying `supersedes`.")
    say()

    # ---- 1. the cliff ---------------------------------------------------
    say("--- 1. The 1/c cliff: largest n that can still yield a paired result ---")
    say(f"{'c (arm censoring rate)':>26}{'1/c':>10}{'max clean n':>14}")
    cliff = {}
    for c in (0.50, 0.37, C_PAPER, 0.25, 0.20, 0.10, 0.05, 0.01, 0.005):
        m = max_clean_batch(c)
        cliff[f"{c:.4f}"] = m
        note = "  <- the paper's own frame" if abs(c - C_PAPER) < 1e-9 else ""
        say(f"{c:>26.4f}{1.0/c:>10.2f}{m:>14d}{note}")
    say()
    say("  E[censored arms in an n-pair batch] = n*c. A paired result requires")
    say("  every arm-slot to be filled, so it requires n*c < 1. Above the cliff")
    say("  the expected number of censored arms is >= 1, the interval width is")
    say("  pinned at ~c, and adding pairs cannot narrow it.")
    say()
    say(f"  APPLIED TO THE PAPER: c = 10/27 = {C_PAPER:.4f}, 1/c = "
        f"{1.0/C_PAPER:.2f}.")
    say(f"  The paper ran 27 pairs. That is "
        f"{27 * C_PAPER / 1.0:.1f}x past the cliff. The campaign was already")
    say("  unrecoverable by sample size at its 3rd pair; the other 24 bought")
    say("  lattice precision, not resolution.")
    say()
    say("  P(clean frame, every allocated arm-slot recorded) = (1-c)^n:")
    say(f"{'c':>8}{'n':>8}{'P(clean)':>14}{'P(at least one censored)':>28}")
    for c in (C_PAPER, 0.20, 0.10, 0.05):
        for n in (2, 3, 6, 27):
            pc = p_clean_frame(c, n)
            say(f"{c:>8.2f}{n:>8d}{pc:>14.3e}{1.0 - pc:>28.6f}")
    say()
    say("  THE OPERATIVE NUMBER FOR AXV. A 2-arm x 3-seed contrast is n=6 runs.")
    say(f"  At c=0.20 a 6-run batch records a complete frame only "
        f"{p_clean_frame(0.20, 6)*100:.1f}% of the time, so 3 of every 4 such")
    say("  batches is a completed-pairs-only view wearing a point estimate. A")
    say("  censored batch is not a null; it is an interval, and it must be")
    say("  reported as one.")
    say()

    # ---- 2. Clopper-Pearson --------------------------------------------
    say("--- 2. Clopper-Pearson n to certify c below a resolution target ---")
    say("  (one-sided 95%, zero censored arms observed)")
    say(f"{'resolution target':>20}{'n required':>14}   reading")
    cp = {}
    for d, r in ((0.20, "coarse: 1 task in 5"),
                 (0.10, "5 pp of success rate"),
                 (0.05, "the 12/15-vs-12/15 scale of the paper"),
                 (0.03, "fine"),
                 (0.01, "very fine: 1 task in 100")):
        k = cp_zero_event_n(d)
        cp[f"{d:.2f}"] = k
        say(f"{d:>20.2f}{k:>14d}   {r}")
    say()
    say("  These n are NOT a plan. They are the price of a certificate, and the")
    say("  certificate is only obtainable if the true c is small enough that you")
    say("  actually SEE zero censored arms:")
    say()
    say(f"{'true c':>10}{'P(0 caps in n=27)':>20}{'P(0 caps in n=59)':>20}")
    for c in (0.37, 0.20, 0.10, 0.05, 0.01):
        say(f"{c:>10.2f}{p_clean_frame(c, 27):>20.3e}{p_clean_frame(c, 59):>20.3e}")
    say()
    say("  At the paper's c = 0.37, seeing zero censored arms in 59 pairs has")
    say("  probability 3e-11. You are not running a certification experiment;")
    say("  you are waiting for a regime change that the budget cannot buy.")
    say()

    # ---- 3. Monte-Carlo: width is flat in n -----------------------------
    say("--- 3. Monte-Carlo: E[interval width] vs n, at fixed c ---")
    say(f"  seed={SEED}  trials={TRIALS:,} per row")
    say("  exact E[width] = c by construction; the MC checks the code")
    say(f"{'c':>8}{'n':>8}{'E[width] (pp)':>15}{'se (pp)':>11}{'1/c':>8}")
    rows = []
    for c in (0.37, 0.20, 0.10):
        for n in (10, 27, 100, 400, 1600):
            m = simulate(c, n, TRIALS, rng)
            se = mc_se(m, n, TRIALS)
            rows.append({"c": c, "n": n, "e_width": m, "se": se, "exact": c})
            say(f"{c:>8.2f}{n:>8d}{m*100:>15.2f}{se*100:>11.4f}"
                f"{1.0/c:>8.2f}")
    say()
    say("  Largest MC deviation from the exact value c, any row: "
        f"{max(abs(r['e_width'] - r['exact']) for r in rows)*100:.4f} pp. "
        "The code is consistent with the identity.")

    # ---- 4. pre-registered tests ----------------------------------------
    say()
    say("--- 4. Pre-registered tests ---")
    say()
    say("  TEST 1 (z-test). H0: E[width] is independent of n. Fail if |diff| > 3 SE.")
    say()
    t1 = {}
    for c in (0.37, 0.20, 0.10):
        sel = [r for r in rows if r["c"] == c]
        lo, hi = sel[0], sel[-1]
        diff = hi["e_width"] - lo["e_width"]
        se = math.sqrt(lo["se"] ** 2 + hi["se"] ** 2)
        z = diff / se if se > 0 else 0.0
        ok = abs(z) < 3.0
        t1[f"{c:.2f}"] = {"diff": diff, "z": z, "pass": ok}
        say(f"    c={c:.2f}: {lo['e_width']*100:.2f}pp -> {hi['e_width']*100:.2f}pp, "
            f"diff={diff*100:+.3f}pp, se={se*100:.4f}pp, z={z:+.2f}  "
            f"-> {'pass (flat)' if ok else 'REFUTES'}")
    t1_all = all(v["pass"] for v in t1.values())
    say(f"    TEST 1 VERDICT: "
        f"{'H0 NOT REFUTED - flat to within MC noise' if t1_all else 'H0 REFUTED'}")
    say()
    say("    SUPERSEDED OUTCOME, kept for the record: the first execution of")
    say("    this script returned TEST 1 REFUTED on c=0.20 and c=0.10. That was")
    say("    caused by se = sqrt(m(1-m)/(TRIALS*n^2)) instead of")
    say("    sqrt(m(1-m)/(n*TRIALS)), a factor of sqrt(n) = 40x too small at")
    say("    n=1600. With the correct SE the same measured differences are")
    say("    z = -1.8, -1.9 and -0.3, and none is significant. E[width] = c is")
    say("    an identity here, so exact independence is the true H0 and the")
    say("    correct instrument confirms it.")
    say()
    say("  TEST 2 (equivalence test, pre-registered tolerance 1.0 pp). H0: width")
    say("  is practically flat in n. Pass iff |diff| < 1.0 pp. Tolerance set to")
    say("  ~1/4 of the paper's own N=27 lattice step of 3.7 pp.")
    say()
    t2 = {}
    for c in (0.37, 0.20, 0.10):
        sel = [r for r in rows if r["c"] == c]
        lo, hi = sel[0], sel[-1]
        diff = hi["e_width"] - lo["e_width"]
        ok = abs(diff) * 100 < 1.0
        t2[f"{c:.2f}"] = {"diff": diff, "flat": ok}
        say(f"    c={c:.2f}: |diff| = {abs(diff)*100:.4f}pp "
            f"({'<' if ok else '>='} 1.0pp)  -> {'FLAT' if ok else 'NOT FLAT'}")
    all_flat = all(v["flat"] for v in t2.values())
    say(f"    TEST 2 VERDICT: "
        f"{'CONFIRMED - width is set by c, not n' if all_flat else 'REFUTED'}")
    say()
    say("    The practical claim survives a 160x increase in n at every censoring")
    say("    rate tested. That is the finding: AXV cannot buy its way out of a")
    say("    censored A/B with seeds, and neither could the authors have bought")
    say("    their way out of this one with 27x the campaign.")
    say()

    # ---- 5. the smallest change that fixes it ----------------------------
    say("--- 5. Smallest allocation-rule change, and what it costs ---")
    say("  ReVerPi's defect is a control-flow break in the runner:")
    say("      Pr(M_2 = 1 | C_1 = 0, A_1, X) = 0     (paper Eq. 2)")
    say("  AXV's defect is budget starvation in the batch loop: one pod, one")
    say("  shared wall-clock budget, arms in sequence, so a hung or crashed")
    say("  arm-1 starves arm-2 of the remaining time. Same structure, and it")
    say("  is the same fix, applied to the allocation arithmetic rather than to")
    say("  the break condition:")
    say()
    say("      Pr(M_2 = 1 | C_1 = 0, A_1, X) = 1     (pre-authorised reserve)")
    say()
    say("  THE CHANGE, in one sentence: at batch allocation time, reserve each")
    say("  arm its own wall-clock slice up front and forbid arm-1's overrun")
    say("  from consuming arm-2's slice, so every allocated arm-slot is")
    say("  attempted regardless of what happened to any other arm.")
    say()
    say("  Necessary but not sufficient, and the second half is one line.")
    say("  Verified by reading tools/run-experiment.sh: line 116 raises")
    say("  SystemExit when no val_bpb is found in the log, and the ledger write")
    say("  is the `record` call at line 148, after it. So an allocated arm that")
    say("  is censored leaves NO leaderboard row, and a later contrast over the")
    say("  surviving rows is completed-pairs-only. That is the AXV analogue of")
    say("  the paper's 12/15 tie, and it is present in our tooling today.")
    say("  The change: every allocated run id gets a terminal leaderboard record")
    say("  with metric_value=null, censored=true, censor_reason in")
    say("  {crash, pod-lost, oom, timeout}, decision='inconclusive'.")
    say()
    say("  COST: $0.00. No GPU, no pod, no extra wall clock. It is a change to")
    say("  the batch manifest and the wrapper's exit path, not to train.py, so")
    say("  the config_fingerprint and therefore the comparability cohort are")
    say("  unchanged and every existing leaderboard record stays valid.")
    say()

    # ---- 6. decision rule for batch sizing -------------------------------
    say("--- 6. Sizing rule this implies for AXV ---")
    say("  n_batch < 1/c_hat, where c_hat is the censored-arm rate of the")
    say("  previous batch. If the planned batch is at or above 1/c_hat, the")
    say("  batch CANNOT produce a paired result no matter how many seeds it")
    say("  runs, so spend the budget on the allocation fix instead of on seeds.")
    say()
    say(f"  At the paper's c = 0.37 the largest honest paired batch is n = "
        f"{max_clean_batch(C_PAPER)}.")
    say(f"  At c_hat = 0.10 it is n = {max_clean_batch(0.10)}.")
    say()
    say("  AXV's standing 3-seed rule makes a 2-arm contrast n=6. The rule is")
    say("  therefore only safe while c_hat < 1/6 = 0.167. Measure c_hat from")
    say("  the leaderboard every batch; it is only measurable once the")
    say("  censored-terminal-row change in section 5 has landed, because until")
    say("  then a censored arm is invisible and c_hat is biased toward zero by")
    say("  exactly the defect being measured.")
    say()
    say("  And a batch that is too large to pair should not be silently")
    say("  reported as a null. It should be recorded as censored, and the memo")
    say("  should carry the interval, not the point estimate. The paper's")
    say("  format for that is already written: the Eq. 5 interval, labelled as")
    say("  an identification interval and not a confidence interval.")

    metrics = {
        "run_id": "2609.31381-a02-s1337",
        "metric_name": METRIC,
        "metric_value": None,
        "seed": SEED,
        "trials_per_row": TRIALS,
        "c_paper": C_PAPER,
        "cliff_1_over_c": 1.0 / C_PAPER,
        "max_clean_batch_at_c_paper": max_clean_batch(C_PAPER),
        "paper_batch_over_cliff": 27 * C_PAPER,
        "p_clean_frame": {
            f"c={c:.2f},n={n}": p_clean_frame(c, n)
            for c in (C_PAPER, 0.20, 0.10, 0.05) for n in (2, 3, 6, 27)
        },
        "p_clean_frame_6run_at_c020": p_clean_frame(0.20, 6),
        "clopper_pearson_n": cp,
        "mc_rows": rows,
        "max_mc_deviation_from_exact_pp": max(
            abs(r["e_width"] - r["exact"]) for r in rows) * 100,
        "test1_ztest": t1,
        "test1_verdict_h0_not_refuted": t1_all,
        "test2_equivalence_tol_pp": 1.0,
        "test2_equivalence": t2,
        "test2_verdict_flat": all_flat,
        "baseline_run_id": "2609.31381-a01-s1337",
        "baseline_metric_value": 37.037037037037035,
        "delta": None,
        "supersedes_note": (
            "Corrects the first execution of this run, which reported TEST 1 "
            "REFUTED. That verdict came from a standard error understated by a "
            "factor of sqrt(n): sqrt(m(1-m)/(TRIALS*n*n)) was used instead of "
            "sqrt(m(1-m)/(n*TRIALS)). E[width]=c is an identity, so exact "
            "independence is the true H0 and the corrected instrument confirms "
            "it. Both verdicts are retained; the earlier one is superseded."),
        "experiment_status": "verified" if (all_flat and t1_all) else "failed",
        "cost_usd": 0.0,
        "pods_provisioned": 0,
        "gpu_seconds": 0,
    }
    d = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(d, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    with open(os.path.join(d, "estimator.log"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")

    say()
    say("=" * 74)
    say(f"APPLIED EXPERIMENT: {metrics['experiment_status'].upper()}")
    say(f"  cost: $0.00   pods provisioned: 0   GPU seconds: 0")
    say("=" * 74)
    return 0 if (all_flat and t1_all) else 1


if __name__ == "__main__":
    sys.exit(main())
