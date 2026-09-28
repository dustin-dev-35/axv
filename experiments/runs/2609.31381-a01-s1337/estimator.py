"""
Reproduction of the finite-frame identification bounds of arXiv:2609.31381v1.

Claim under test (paper, Sec 5.2 / Eq. 5):
    "The finite-frame bounds are Delta_27 in [-9/27, 1/27], or [-33.3, +3.7]
     percentage points."
and (abstract, Sec 5.2):
    "the 15 completed pairs show identical success: 12/15 per arm."

This script is a direct transcription of the paper's own definitions, fed the
paper's own per-run tables (Tables 7 and 8). It calls no model, no provider, and
no GPU. It is an ESTIMATOR reproduction, not a re-run of the 86-run agent
campaign, and it is recorded as such.

No variable is changed. This is the reference implementation.
"""

import json
import math
import os
import sys

# ---------------------------------------------------------------- paper data
# Table 7: the fifteen completed paired/capture boundary runs.
# Task, Y_F, Y_P  (1 = correct final answer by request K=12, 0 = otherwise)
# Transcribed from arXiv:2609.31381v1 Table 7, cross-checked against the
# eleven-row joint-success stratum of Table 10 (tomlkit-datetimes and
# urllib3-headers are the two rows the HTML table body splits across a
# page break; both are (1,1) and both appear in Table 10).
TABLE7 = [
    ("click-parameters",        1, 1),   # fitting
    ("packaging-compatibility", 0, 1),   # fitting
    ("boltons-indexedset",      1, 1),   # fitting
    ("cerberus-errors",         0, 0),
    ("dotenv-stream",           1, 1),
    ("filelock-basics",         1, 1),
    ("filelock-contention",     1, 1),
    ("funcy-colls",             0, 0),
    ("more-itertools-recipes",  1, 1),
    ("more-itertools-window",   1, 1),
    ("pathspec-match",          1, 1),
    ("six-moves",               1, 0),
    ("sqlparse-grouping",       1, 1),
    ("tomlkit-datetimes",       1, 1),   # fitting
    ("urllib3-headers",         1, 1),
]

# Table 8: the twelve stopped paired/capture boundary runs.
# "?" denotes an unexecuted companion (unknown outcome).
TABLE8 = [
    # task,                    Y_F, Y_P
    ("attrs-define",            None, 0),
    ("docutils-nodes",          1,    0),
    ("docutils-tree",           None, 0),
    ("markdown-extensions",     None, 0),
    ("marshmallow-fields",      None, 0),
    ("pathspec-util",           1,    0),
    ("pyparsing-helpers",       None, 0),
    ("pyparsing-parse",         0,    None),
    ("rich-table",              0,    None),
    ("sqlalchemy-core",         0,    None),
    ("tabulate-formats",        None, 0),
    ("tomlkit-roundtrip",       None, 0),
]

# Table 4 / Table 11 stratum splits (17 runs with both bounded outcomes known).
FITTING = {"click-parameters", "packaging-compatibility",
           "boltons-indexedset", "tomlkit-datetimes"}


# ------------------------------------------------- the paper's definitions
def interval(y):
    """Sec 4.1: [l, u] for known success, known failure, unknown outcome."""
    if y is None:
        return (0, 1)
    return (y, y)


def manski_bounds(pairs):
    """
    Eq. 5. For the finite-frame contrast
        Delta_N = (1/N) * sum_i (Y_iP - Y_iF)
    the sharp worst-case interval is
        [ (1/N) sum_i (l_iP - u_iF),  (1/N) sum_i (u_iP - l_iF) ].
    """
    n = len(pairs)
    lo = sum(interval(p)[0] - interval(q)[1] for _, q, p in pairs) / n
    hi = sum(interval(p)[1] - interval(q)[0] for _, q, p in pairs) / n
    return lo, hi


def endpoint_counts(pairs):
    """Table 3: per-arm correct / known bounded failure / unexecuted."""
    out = {}
    for name, idx in (("full", 1), ("projected", 2)):
        c = sum(1 for p in pairs if p[idx] == 1)
        f = sum(1 for p in pairs if p[idx] == 0)
        u = sum(1 for p in pairs if p[idx] is None)
        out[name] = {"correct": c, "known_bounded_failure": f, "unexecuted": u}
    return out


def joint_success(pairs):
    """
    Sec 4.2 / A.1: J = {i : Y_F = Y_P = 1}. Every incomplete pair has at least
    one known zero, so no missing outcome can move a run into or out of J.
    """
    return [n for n, q, p in pairs if q == 1 and p == 1]


# ------------------------------------------------------------------- report
def main():
    log = []

    def say(s=""):
        print(s)
        log.append(s)

    allpairs = ([(n, f, p) for n, f, p in TABLE7] +
                [(n, f, p) for n, f, p in TABLE8])
    n = len(allpairs)

    say("=" * 74)
    say("arXiv:2609.31381v1  --  finite-frame bound reproduction")
    say("=" * 74)
    say()
    say(f"paired/capture boundary runs: N = {n}"
        f"  ({len(TABLE7)} completed + {len(TABLE8)} stopped)")
    say()

    # ---- Table 3 reproduction -------------------------------------------
    say("--- Table 3: bounded outcomes over all 27 boundaries ---")
    ec = endpoint_counts(allpairs)
    say(f"{'recorded endpoint':<26}{'Full':>8}{'Projected':>12}")
    for k, lbl in (("correct", "Correct"),
                   ("known_bounded_failure", "Known bounded failure"),
                   ("unexecuted", "Unexecuted")):
        say(f"{lbl:<26}{ec['full'][k]:>8}{ec['projected'][k]:>12}")
    say()

    expect3 = {"full": {"correct": 14, "known_bounded_failure": 6,
                        "unexecuted": 7},
               "projected": {"correct": 12, "known_bounded_failure": 12,
                             "unexecuted": 3}}
    t3_ok = ec == expect3

    # ---- completed-pairs-only "null" ------------------------------------
    c15 = [(nm, f, p) for nm, f, p in TABLE7]
    succ_f = sum(1 for _, f, _ in c15 if f == 1)
    succ_p = sum(1 for _, _, p in c15 if p == 1)
    null_delta = (succ_p - succ_f) / len(c15)

    say("--- Sec 5.2: the completed-pairs-only view (the reported 'null') ---")
    say(f"  completed pairs: {len(c15)}")
    say(f"  full successes:     {succ_f}/{len(c15)}")
    say(f"  projected successes:{succ_p}/{len(c15)}")
    say(f"  projected - full:   {null_delta:+.4f}   <-- exactly zero")
    say()

    # ---- Eq. 5 headline bound ------------------------------------------
    lo, hi = manski_bounds(allpairs)
    paper_lo, paper_hi = -9 / 27, 1 / 27
    bounds_ok = (abs(lo - paper_lo) < 1e-12 and abs(hi - paper_hi) < 1e-12)

    say("--- Eq. 5: finite-frame bounds on projected - full ---")
    say(f"  reproduced:  [{lo:+.4f}, {hi:+.4f}]  = "
        f"[{lo*100:+.1f}, {hi*100:+.1f}] percentage points")
    say(f"  paper:       [{paper_lo:+.4f}, {paper_hi:+.4f}]  = "
        f"[{paper_lo*100:+.1f}, {paper_hi*100:+.1f}] percentage points")
    say(f"  MATCH: {bounds_ok}")
    say()
    say(f"  interval WIDTH: {(hi - lo)*100:.1f} percentage points"
        f"   (width/N = {(hi - lo)/n:.4f})")
    say(f"  unresolved companions: "
        f"{ec['full']['unexecuted'] + ec['projected']['unexecuted']} of {2*n}"
        f" arm-slots  ->  {ec['full']['unexecuted'] + ec['projected']['unexecuted']}/{n}"
        f" = {(ec['full']['unexecuted'] + ec['projected']['unexecuted'])/n:.4f}")
    say()

    # ---- J = 11 stratum -------------------------------------------------
    J = joint_success(allpairs)
    say("--- Sec 4.2 / A.1: observed jointly successful stratum ---")
    say(f"  |J| = {len(J)}")
    say(f"  members: {', '.join(J)}")
    say(f"  every non-member is ruled out by an observed zero, so membership")
    say(f"  is fully identified: {len(J) == 11}")
    say()

    # ---- the width is a function of the censor rate, not of n ----------
    say("--- Sec A.1 sharpness: interval width vs N, at fixed censor rate ---")
    say(f"{'N':>6}{'width (pp)':>14}{'width/N':>12}   interpretation")
    for N in (27, 54, 108, 270, 540, 2700):
        k = int(round(N * (ec['full']['unexecuted'] +
                           ec['projected']['unexecuted']) / n))
        w = k / N
        say(f"{N:>6}{w*100:>14.1f}{w/N:>12.4f}   same width, wider lattice")
    say()
    say("  Width = (number of unresolved companions)/N. Multiplying N by 10")
    say("  multiplies the expected count of unresolved companions by 10 and")
    say("  leaves the width unchanged. N buys precision on the location of")
    say("  the interval, never on its width.")
    say()

    metrics = {
        "n_boundary_runs": n,
        "n_completed_pairs": len(c15),
        "n_stopped_pairs": len(TABLE8),
        "table3_reproduced": t3_ok,
        "endpoint_counts": ec,
        "completed_pairs_only_delta": null_delta,
        "completed_pairs_only_full": f"{succ_f}/{len(c15)}",
        "completed_pairs_only_projected": f"{succ_p}/{len(c15)}",
        "eq5_lower": lo,
        "eq5_upper": hi,
        "eq5_width": hi - lo,
        "eq5_matches_paper": bounds_ok,
        "joint_success_stratum_size": len(J),
        "unresolved_companions": (ec['full']['unexecuted'] +
                                  ec['projected']['unexecuted']),
        "censor_rate_c": (ec['full']['unexecuted'] +
                          ec['projected']['unexecuted']) / n,
        "reproduction_status": "verified" if (t3_ok and bounds_ok) else "failed",
    }

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "metrics.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "estimator.log"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")

    say("=" * 74)
    say(f"REPRODUCTION: {metrics['reproduction_status'].upper()}")
    say("=" * 74)
    return 0 if (t3_ok and bounds_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
