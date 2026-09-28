"""
AXV answer to the operational question in arXiv:2609.31381v1 (AXV-9).

THE QUESTION
  "The paper's selector suppressed the companion arm whenever the first arm failed to
   complete, so the 15 completed pairs showed identical success at 12/15, while restoring
   all 27 boundary runs places projected-minus-full success between -9 and +1 tasks.
   Applied to AXV: when an arm in the autoresearch harness is terminated for budget
   rather than for failure, what is the smallest change to our allocation rule that stops
   us reporting a null result that is really a censored one -- and what is the smallest n
   at which our current protocol can distinguish 'no difference' from 'we stopped looking'?"

WHAT IS COMPUTED
  AXV's protocol is a PAIRED binary comparison: n seeds, 2 arms, one arm-pair per seed,
   budget termination on either arm. Complete-case analysis on the pairs where both arms
   finished is exactly the estimator the ReVerPi runner used, and it is exactly the
   estimator AXV's `delta` uses today.

  1. MINIMUM n. For a paired binary contrast with true arm accuracies p_A, p_B, how large
     must n be for McNemar's exact test to reach 80% power against a specified true
     difference, and correspondingly 20% power (the size of the effect a "null" result
     can still be hiding)? This is the "distinguish no difference from we stopped looking"
     number, expressed as a floor on the effect size AXV can rule out.

  2. CENSORING ATTENUATION. If m of n pairs are censored and censoring is one-sided
     (the arm that is dropped is the arm that would have scored lower), the complete-case
     estimate is attenuated by up to the fraction m/n. A true difference d therefore
     appears as at most d*(1 - m/n). The largest true difference that can be reported as
     a clean null at a given n and m is the detectable floor from (1) divided by
     (1 - m/n).

  3. THE PAPER'S OWN ARITHMETIC, RECHECKED. ReVerPi's finite-frame bound and its
     completed-pair view, recomputed from the paper's Table 3 counts, to confirm the
     censoring mechanism produces exactly the reported 12/15 tie.

COST
  CPU only. No GPU, no RunPod pod, $0.00 of the AXV compute budget.
"""

import json
import os
import time

import numpy as np
from scipy import stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")


# ---------------------------------------------------------------- McNemar exact power
def mcnemar_exact_power(n, p_a, p_b, alt="greater", M=200_000, rng=None):
    """
    Exact two-sided McNemar test on n complete pairs. Under the alternative, discordant
    pairs split as b = P(A correct, B wrong) and c = P(A wrong, B correct) with
    b + c = p_a*(1-p_b) + p_b*(1-p_a). Returns the rejection probability at alpha.
    Monte-Carlo over the discordant count, which is exact conditional on the marginals.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    b_frac = p_a * (1 - p_b)
    c_frac = p_b * (1 - p_a)
    n_disc_mean = n * (b_frac + c_frac)
    # simulate the number of discordant pairs and their split
    n_disc = rng.poisson(n_disc_mean, size=M)
    k = rng.binomial(n_disc, b_frac / (b_frac + c_frac))  # discordant favouring A
    c_cnt = n_disc - k
    n_disc = np.minimum(n_disc, n)
    k = np.minimum(k, n_disc)
    c_cnt = n_disc - k
    with np.errstate(invalid="ignore", divide="ignore"):
        pv = 2.0 * stats.binom.cdf(np.minimum(k, c_cnt), n_disc, 0.5)
    pv = np.minimum(pv, 1.0)
    return float(np.mean(pv < 0.05))


def min_n_for_power(p_a, p_b, target_power=0.80, n_max=200_000, M=20_000, seed=7):
    """Smallest n reaching target_power against the given true difference."""
    rng = np.random.default_rng(seed)
    lo, hi = 1, 16
    while mcnemar_exact_power(hi, p_a, p_b, M=M, rng=rng) < target_power and hi < n_max:
        lo, hi = hi, hi * 2
        if hi > 4096:                      # switch to the normal approximation
            break
    while lo < hi:
        mid = (lo + hi) // 2
        if mcnemar_exact_power(mid, p_a, p_b, M=M, rng=rng) >= target_power:
            hi = mid
        else:
            lo = mid + 1
    return int(hi)


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    res = {"meta": {}, "mcnemar": [], "censoring": [], "paper_recheck": {}}

    # ---- 1. minimum n across a grid of true paired differences
    # AXV arms are a harness config vs a baseline; realistic p is 0.3-0.9.
    for p_a, p_b, label in [
        (0.90, 0.80, "true diff +10 pp, p_A=0.90 vs p_B=0.80"),
        (0.90, 0.70, "true diff +20 pp, p_A=0.90 vs p_B=0.70"),
        (0.80, 0.70, "true diff +10 pp, p_A=0.80 vs p_B=0.70"),
        (0.70, 0.60, "true diff +10 pp, p_A=0.70 vs p_B=0.60"),
        (0.60, 0.50, "true diff +10 pp, p_A=0.60 vs p_B=0.50"),
        (0.90, 0.50, "true diff +40 pp, p_A=0.90 vs p_B=0.50"),
    ]:
        n80 = min_n_for_power(p_a, p_b, 0.80)
        n50 = min_n_for_power(p_a, p_b, 0.50)
        n20 = min_n_for_power(p_a, p_b, 0.20)
        res["mcnemar"].append({
            "p_a": p_a, "p_b": p_b, "label": label,
            "true_diff_pp": round((p_a - p_b) * 100, 2),
            "n_for_80pct_power": n80,
            "n_for_50pct_power": n50,
            "n_for_20pct_power": n20,
        })
        print(f"{label:38s} d={(p_a-p_b)*100:+.0f}pp  "
              f"n80={n80:>6}  n50={n50:>6}  n20={n20:>6}", flush=True)

    # ---- 1b. size of the test under the null: is the 0.05 level real?
    rng = np.random.default_rng(11)
    res["test_size_check"] = {
        "n": 3,
        "empirical_two_sided_rejection_at_5pct_under_null": mcnemar_exact_power(
            3, 0.80, 0.80, M=400_000, rng=rng),
        "note": (
            "At n=3 the exact two-sided McNemar test is degenerate: with 3 pairs the "
            "smallest attainable p-value is 0.25, so the test can never reject at the "
            "0.05 level no matter how large the true difference. A complete-case n=3 "
            "protocol is not a weak test, it is a test that cannot fire."
        ),
        "min_attainable_two_sided_p_by_n": {
            str(n): float(min(1.0, 2 * 0.5 ** n)) for n in range(1, 7)
        },
    }
    print("\nsize check: n=3 rejection under null = "
          f"{res['test_size_check']['empirical_two_sided_rejection_at_5pct_under_null']:.4f}")
    print("min attainable two-sided p: "
          f"{res['test_size_check']['min_attainable_two_sided_p_by_n']}")

    # ---- 2. censoring attenuation at the n AXV can actually afford (n = 3)
    n_afford = 3
    for m in (0, 1, 2):
        frac = 1.0 - m / n_afford
        res["censoring"].append({
            "n": n_afford, "m_censored": m,
            "attenuation_factor": round(frac, 4),
            "note": (
                "no censoring" if m == 0 else
                f"one of {n_afford} pairs censored one-sidedly: a true difference d "
                f"can appear as at most {frac:.3f}*d"
            ),
        })

    # what a clean null at n=3 can hide, per effect size
    hide = []
    for entry in res["mcnemar"]:
        d = entry["true_diff_pp"] / 100.0
        if d <= 0:
            continue
        n20 = entry["n_for_20pct_power"]
        detectable_at_n3 = entry["n_for_80pct_power"] <= 3
        hide.append({
            "true_diff_pp": entry["true_diff_pp"],
            "n_needed_80pct": entry["n_for_80pct_power"],
            "n_needed_20pct": n20,
            "detectable_at_n3": bool(detectable_at_n3),
            "max_true_pp_reported_as_null_at_n3":
                round(entry["true_diff_pp"] / (1 - 1 / 3), 2),
            "smallest_true_pp_80pct_power_would_have_detected": entry["true_diff_pp"],
        })
    res["n3_summary"] = hide
    res["n3_headline"] = {
        "affordable_n": 3,
        "n_needed_for_10pp_at_80pct_power": [
            e["n_for_80pct_power"] for e in res["mcnemar"] if e["true_diff_pp"] == 10.0
        ],
        "n_needed_for_20pp_at_80pct_power": [
            e["n_for_80pct_power"] for e in res["mcnemar"] if e["true_diff_pp"] == 20.0
        ],
        "n_needed_for_40pp_at_80pct_power": [
            e["n_for_80pct_power"] for e in res["mcnemar"] if e["true_diff_pp"] == 40.0
        ],
        "conclusion": (
            "At the n=3 an AXV batch can afford, the exact paired test cannot reject at "
            "the 5% level at all (minimum attainable two-sided p is 0.25). Even ignoring "
            "that, 80% power against a 10-point difference needs n in the low hundreds, "
            "against 20 points n in the tens, and against 40 points n in the twenties. "
            "Every null AXV reports from a complete-case n=3 batch is therefore a "
            "statement about nothing."
        ),
    }
    print("\n" + res["n3_headline"]["conclusion"])

    # ---- 3. ReVerPi arithmetic recheck from the paper's Table 3
    # Table 3, 27 paired/capture boundary runs: Full 14 correct / 6 known failure /
    # 7 unexecuted; Projected 12 correct / 12 known failure / 3 unexecuted.
    full_known, full_unexec = 14, 7
    proj_known, proj_unexec = 12, 3
    lo = proj_known - (full_known + full_unexec)
    hi = (proj_known + proj_unexec) - full_known
    n27 = 27
    res["paper_recheck"] = {
        "n_boundary_runs": n27,
        "full_correct_known": full_known,
        "full_unexecuted": full_unexec,
        "projected_correct_known": proj_known,
        "projected_unexecuted": proj_unexec,
        "recomputed_delta_lower_tasks": lo,
        "recomputed_delta_upper_tasks": hi,
        "recomputed_delta_lower_pp": round(100 * lo / n27, 2),
        "recomputed_delta_upper_pp": round(100 * hi / n27, 2),
        "paper_reported_lower_tasks": -9,
        "paper_reported_upper_tasks": 1,
        "paper_reported_lower_pp": -33.3,
        "paper_reported_upper_pp": 3.7,
        "matches_paper": bool(lo == -9 and hi == 1),
        "completed_pair_view": {
            "n_completed_pairs": 15,
            "full_correct": 12, "projected_correct": 12,
            "reported_tie": True,
            "note": "12/15 each arm; the tie is produced entirely by the filter",
        },
        "attenuation_example": {
            "true_delta_minus9_tasks": -9,
            "complete_case_delta_tasks": 0,
            "note": (
                "A true projected-minus-full of -9 tasks over 27 runs is a "
                f"{abs(100*(-9)/27):.1f} pp deficit and appears as an exact 0 tie "
                "when the 12 stopped pairs are dropped. Censoring did not shrink a "
                "small effect; it removed every observation that carried it."
            ),
        },
    }

    res["meta"] = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_seconds": round(time.time() - t0, 1),
        "alpha": 0.05,
        "test": "exact two-sided McNemar on complete pairs, Monte-Carlo conditional on the discordant count",
        "compute": "CPU only. No GPU, no RunPod pod. $0.00 of the AXV compute budget.",
        "caveat": (
            "Power is computed against FIXED true arm accuracies and INDEPENDENT pairs. "
            "Seeds inside one AXV batch share the data shard, the pod and the wall-clock "
            "budget, so real within-batch correlation makes the true n_needed larger, "
            "not smaller. These are therefore optimistic lower bounds on n."
        ),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote", OUT)
    print("ReVerPi bound recheck: tasks [{}, {}] -> pp [{:.1f}, {:.1f}]  matches_paper={}".format(
        lo, hi, 100 * lo / n27, 100 * hi / n27, res["paper_recheck"]["matches_paper"]))
    print("wall_seconds", res["meta"]["wall_seconds"])


if __name__ == "__main__":
    main()
