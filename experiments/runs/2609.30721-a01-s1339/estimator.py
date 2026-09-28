"""
arXiv:2609.30721v1 -- Arm A01
Controlled Type-I calibration and design-effect audit: i.i.d. observed-record
inference vs session-centred Bartlett-HAC on overlapping sliding-window sequences.

WHAT THE PAPER PUBLISHES (Sec. III-C, III-D, IV-A, V-A, Fig. 3a, Table IV):
  - window length L = 64 raw samples; test overlap 0 / 50 / 75 percent
  - null: both arms at 0.8 marginal accuracy, paired binary correctness D_ijt
  - i.i.d. observed-record interval: Dbar +- 1.960 sqrt(Var(D)/N)
  - session-centred Bartlett-HAC (Eq. 5): u_ijt = D_ijt - Dbar_ij,
        Varhat = (c/N^2) sum_ij [ sum_t u^2 + 2 sum_{h=1..K} w_h sum_t u_t u_{t+h} ],
        w_h = 1 - h/(K+1),  c = N/(N-R),  K_0 = ceil(L/S) - 1,
        K_main = max( floor(4*(Tbar/100)^(2/9)), 2*K_0 )
  - headline at 75% overlap: i.i.d. Type-I 16.9% vs HAC 7.2% (7.9% re-seeded);
    rows grow 3.93-3.97x but G_info = Var_hac(0)/Var_hac(75) is only 1.75-1.94x;
    HAC/i.i.d. width ratio 1.22-1.66x

WHAT THE PAPER DOES NOT PUBLISH: within-session persistence rho, subject count,
session duration, pair correlation between arms, and which of its own conditions
backs Fig. 3(a). Those are ours, declared here, and are the object of the sweep.

GENERATOR. Raw latents are a unit-variance Gaussian AR(1) with parameter rho;
BURN steps are discarded. A window score is the mean of its L raw latents divided
by the analytic sd of that mean, so each arm sits at exactly 0.8 window accuracy at
every overlap (a deliberate control: it removes the separate effect by which denser
overlap can raise point accuracy, leaving only the dependence effect). The two
arms' raw latents are correlated at PAIR_RHO. D_ijt = 1{A correct} - 1{B correct}.

rho = 0 is the MECHANICAL-OVERLAP-ONLY condition: the sole source of cross-window
dependence is windows reusing raw samples, and window-score correlation at window
lag h is (L - hS)/L. rho > 0 adds dependence at 0% overlap too, which is the paper's
"extended AR(1) dependence" condition.

DESIGN EFFECT. Var(D) is measured from the pooled draws, and
DE(r) = Var_true(r) * N_r / Var_pooled(D). DE < 1 means the i.i.d. standard error is
too small, i.e. anti-conservative. G_info = DE(75)/DE(0) * (N_0/N_75).

PRIMARY, PRE-REGISTERED:
  T1  rho=0.00 : i.i.d. Type-I at 75% overlap within 2 pp of 5%, AND G_info within
                 0.15 of 1.00.   Is the headline a mechanical-overlap effect at all?
  T2  rho=0.80 : i.i.d. Type-I at 75% overlap exceeds 8%, AND HAC < i.i.d.
                 Does the paper's claim reproduce under dependence beyond overlap?
  T3  G_info spans more than 0.5 across the rho grid -> 1.75-1.94 is a dataset
                 readout, not a constant.
  T4  At the top of the grid HAC Type-I at 75% overlap still exceeds 5% by more
                 than 1 pp -> the correction is incomplete, as the paper states.
"""

import json
import math
import os
import sys

import numpy as np
from scipy.signal import lfilter
from scipy.stats import norm

L_RAW = 64
OVERLAPS = (0.0, 0.5, 0.75)
N_SUBJECTS = 40
SESS_PER_SUBJ = 2
N_SESS = N_SUBJECTS * SESS_PER_SUBJ
T_RAW = 2048
BURN = 512
ACC = 0.8
ZSTAR = float(norm.ppf(1.0 - ACC))   # window correct iff standardized score > ZSTAR
PAIR_RHO = 0.5
Z975 = 1.959963984540054
N_MC = 2000
BLOCK = 250
RHO_GRID = (0.0, 0.30, 0.60, 0.80, 0.95)
RHO_PRIMARY = 0.80

OUT = os.path.dirname(os.path.abspath(__file__))


def n_windows(S):
    return (T_RAW - L_RAW) // S + 1


def win_mean_sd(rho):
    """sd of the mean of L consecutive unit-variance AR(1) samples."""
    k = np.arange(L_RAW)
    R = rho ** np.abs(k[:, None] - k[None, :])
    return math.sqrt(float(R.sum()) / (L_RAW ** 2))


def ar1_unit(x, rho):
    """Unit-variance AR(1): y[t] = rho*y[t-1] + N(0, 1-rho^2), driven from 0.

    BURN steps are discarded by the caller, so the non-stationary start never
    reaches the retained window grid.
    """
    return lfilter([1.0], [1.0, -rho], x * math.sqrt(max(1.0 - rho ** 2, 0.0)), axis=1)


def window_scores(z, S, starts, sd):
    c = np.concatenate([np.zeros((z.shape[0], 1)), np.cumsum(z, axis=1)], axis=1)
    return (c[:, starts + L_RAW] - c[:, starts]) / (L_RAW * sd)


def contrast_block(rng, rho, m, S, sd):
    span = T_RAW + BURN
    u1 = rng.standard_normal((m, N_SESS, span))
    u2 = PAIR_RHO * u1 + math.sqrt(1.0 - PAIR_RHO ** 2) * rng.standard_normal(u1.shape)
    n = n_windows(S)
    starts = np.arange(n) * S
    out = np.empty((m, N_SUBJECTS, SESS_PER_SUBJ, n), dtype=np.int8)
    accA, accB = [], []
    for k in range(N_SESS):
        s, j = divmod(k, SESS_PER_SUBJ)
        a = (window_scores(ar1_unit(u1[:, k, :], rho)[:, BURN:], S, starts, sd) > ZSTAR)
        b = (window_scores(ar1_unit(u2[:, k, :], rho)[:, BURN:], S, starts, sd) > ZSTAR)
        out[:, s, j, :] = a.astype(np.int8) - b.astype(np.int8)
        accA.append(a.mean())
        accB.append(b.mean())
    return out, float(np.mean(accA)), float(np.mean(accB))


def iid_reject(D):
    flat = D.reshape(D.shape[0], -1).astype(np.float64)
    se = np.sqrt(flat.var(axis=1, ddof=1) / flat.shape[1])
    with np.errstate(divide="ignore", invalid="ignore"):
        return (np.abs(flat.mean(axis=1)) / se) > Z975


def hac_reject(D, S):
    M, I, J, n = D.shape
    R, N = I * J, I * J * n
    Df = D.astype(np.float64)
    u = Df - Df.mean(axis=3, keepdims=True)
    acc = (u ** 2).sum(axis=3)
    K0 = math.ceil(L_RAW / S) - 1
    K = min(max(int(math.floor(4 * (T_RAW / 100.0) ** (2.0 / 9.0))), 2 * K0), n - 1)
    for h in range(1, K + 1):
        w = 1.0 - h / (K + 1.0)
        acc = acc + 2.0 * w * (u[:, :, :, h:] * u[:, :, :, :-h]).sum(axis=3)
    var = (N / (N - R)) / (N ** 2) * acc.sum(axis=(1, 2))
    se = np.sqrt(np.maximum(var, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        rej = (np.abs(Df.reshape(M, N).mean(axis=1)) / se) > Z975
    return rej, var, K, float(np.mean(se <= 0))


def lag1_corr(D):
    u = D.astype(np.float64) - D.mean(axis=3, keepdims=True)
    a, b = u[:, :, :, :-1].ravel(), u[:, :, :, 1:].ravel()
    return float(np.corrcoef(a, b)[0, 1])


def mcse(p, m):
    return math.sqrt(max(p * (1.0 - p), 0.0) / m)


def run_cell(rng, rho, ovl, n_mc, sd):
    S = int(round(L_RAW * (1.0 - ovl)))
    n, R = n_windows(S), N_SESS
    N = R * n
    ni = nh = degen = 0
    means, vhac, pooled, acc, accB = [], [], [], [], []
    for _ in range(0, n_mc, BLOCK):
        m = min(BLOCK, n_mc)
        D, aA, aB = contrast_block(rng, rho, m, S, sd)
        ni += int(iid_reject(D).sum())
        rh, vh, K, dg = hac_reject(D, S)
        nh += int(rh.sum())
        degen += dg * m
        fl = D.reshape(m, -1).astype(np.float64)
        means.append(fl.mean(axis=1))
        pooled.append(fl.var(axis=1, ddof=1))
        vhac.append(vh)
        acc.append(aA); accB.append(aB)
    vt = float(np.var(np.concatenate(means), ddof=1))
    vpool = float(np.mean(np.concatenate(pooled)))
    vh = float(np.mean(np.concatenate(vhac)))
    pi, ph = ni / n_mc, nh / n_mc
    return {
        "rho": rho, "overlap": ovl, "stride": S, "n_windows_per_session": n,
        "N_windows": N, "R_sessions": R, "bandwidth_K": K, "c_factor": N / (N - R),
        "iid_type1": pi, "iid_mcse": mcse(pi, n_mc),
        "hac_type1": ph, "hac_mcse": mcse(ph, n_mc),
        "hac_minus_iid_pp": 100.0 * (ph - pi),
        "var_true": vt, "var_hac_mean": vh, "var_D_pooled": vpool,
        "design_effect_DE": vt * N / vpool,
        "degenerate_hac_frac": degen / float(n_mc),
        "mean_arm_accuracy_A": float(np.mean(acc)), "mean_arm_accuracy_B": float(np.mean(accB)),
        "lag1_corr_D": lag1_corr(D),
    }


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1337
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=" * 96)
    say("arXiv:2609.30721v1  --  arm A01: i.i.d. vs session-centred Bartlett-HAC")
    say(f"seed={seed}  N_MC={N_MC}  L={L_RAW}  T_raw={T_RAW}  subjects={N_SUBJECTS}"
        f"  sessions/subject={SESS_PER_SUBJ}  acc={ACC}  pair_rho={PAIR_RHO}")
    say("rho is OURS. The paper does not publish it. Structural replication only.")
    say("")

    res = {
        "seed": seed,
        "protocol": {
            "L_raw": L_RAW, "T_raw": T_RAW, "burn_in": BURN, "n_subjects": N_SUBJECTS,
            "sessions_per_subject": SESS_PER_SUBJ, "window_accuracy": ACC,
            "pair_rho": PAIR_RHO, "n_mc": N_MC, "block": BLOCK, "z": Z975,
            "rho_grid": list(RHO_GRID), "rho_primary": RHO_PRIMARY,
            "estimator": "session-centred Bartlett-HAC Eq.5, K=max(K_NW,2*K0), c=N/(N-R)",
            "window_rule": "correct iff (mean of L raw latents)/sd > z_{0.2}; sd analytic",
            "design_effect": "DE(r) = Var_true(r) * N_r / Var_pooled(D); DE<1 => iid too narrow",
            "control": "window accuracy pinned at 0.8 at every overlap, so the "
                       "point-prediction effect of overlap cannot drive the result",
            "generating_params_not_in_paper": ["rho", "n_subjects", "sessions_per_subject",
                                               "T_raw", "pair_rho", "window_labelling_rule",
                                               "which_condition_backs_fig_3a"],
        },
        "by_rho": {},
    }

    say("--- A. Type-I error, design effect and G_info by overlap, %d MC sets per cell ---" % N_MC)
    say(f"{'rho':>5} {'ovl':>5} {'nwin':>5} {'N':>6} {'K':>3} "
        f"{'IID%':>7} {'mcse':>5} {'HAC%':>7} {'mcse':>5} {'DE':>6} "
        f"{'r1(D)':>7} {'acc':>6}")
    say("-" * 96)
    for rho in RHO_GRID:
        sd = win_mean_sd(rho)
        per = {"window_score_sd": sd}
        for ovl in OVERLAPS:
            rng = np.random.default_rng([seed, int(rho * 1000), int(ovl * 1000)])
            per[str(ovl)] = run_cell(rng, rho, ovl, N_MC, sd)
        n0, n75 = per["0.0"]["n_windows_per_session"], per["0.75"]["n_windows_per_session"]
        per["row_growth"] = n75 / n0
        per["G_info_from_DE"] = (per["0.0"]["design_effect_DE"]
                                 / per["0.75"]["design_effect_DE"] * (n75 / n0))
        per["G_info_from_hac_var"] = per["0.0"]["var_hac_mean"] / per["0.75"]["var_hac_mean"]
        for ovl in OVERLAPS:
            c = per[str(ovl)]
            say(f"{rho:>5.2f} {ovl:>5.2f} {c['n_windows_per_session']:>5} "
                f"{c['N_windows']:>6} {c['bandwidth_K']:>3} "
                f"{100*c['iid_type1']:>7.2f} {100*c['iid_mcse']:>5.2f} "
                f"{100*c['hac_type1']:>7.2f} {100*c['hac_mcse']:>5.2f} "
                f"{c['design_effect_DE']:>6.3f} {c['lag1_corr_D']:>7.3f} "
                f"{c['mean_arm_accuracy_A']:>6.4f}")
        say(f"      -> rows {n75/n0:.3f}x   G_info(DE) {per['G_info_from_DE']:.4f}"
            f"   G_info(HAC var) {per['G_info_from_hac_var']:.4f}"
            f"   HAC/iid width {math.sqrt(per['G_info_from_hac_var']):.3f}x")
        res["by_rho"][str(rho)] = per
        say("")

    m0 = res["by_rho"]["0.0"]
    mp = res["by_rho"][str(RHO_PRIMARY)]
    top = res["by_rho"][str(RHO_GRID[-1])]
    gspan = (max(v["G_info_from_DE"] for v in res["by_rho"].values())
             - min(v["G_info_from_DE"] for v in res["by_rho"].values()))
    t = {
        "T1_mechanical_only_iid_calibrated": abs(m0["0.75"]["iid_type1"] - 0.05) <= 0.02,
        "T1_mechanical_only_G_info_near_one": abs(m0["G_info_from_DE"] - 1.0) <= 0.15,
        "T2_extended_iid_anticonservative_at_75": mp["0.75"]["iid_type1"] > 0.08,
        "T2_extended_hac_below_iid_at_75": mp["0.75"]["hac_type1"] < mp["0.75"]["iid_type1"],
        "T3_G_info_span_gt_0.5": bool(gspan > 0.5),
        "G_info_span": gspan,
        "T4_hac_still_anticonservative_at_top_of_grid": top["0.75"]["hac_type1"] > 0.06,
    }
    res["tests"] = t

    say("--- B. pre-registered verdicts ---")
    for k in ("T1_mechanical_only_iid_calibrated", "T1_mechanical_only_G_info_near_one",
              "T2_extended_iid_anticonservative_at_75", "T2_extended_hac_below_iid_at_75",
              "T3_G_info_span_gt_0.5", "T4_hac_still_anticonservative_at_top_of_grid"):
        say(f"  {k:<46}: {t[k]}")
    say("")
    say("--- C. summary: the number AXV needs is sqrt(DE), the iid SE inflation factor ---")
    say(f"{'rho':>5} {'IID75%':>8} {'HAC75%':>8} {'DE(75)':>8} {'DE(0)':>8} "
        f"{'G_info':>8} {'rows':>6} {'SEinfl75':>9} {'SEinfl0':>9}")
    for rho in RHO_GRID:
        v = res["by_rho"][str(rho)]
        say(f"{rho:>5.2f} {100*v['0.75']['iid_type1']:>8.2f} "
            f"{100*v['0.75']['hac_type1']:>8.2f} {v['0.75']['design_effect_DE']:>8.3f} "
            f"{v['0.0']['design_effect_DE']:>8.3f} {v['G_info_from_DE']:>8.4f} "
            f"{v['row_growth']:>6.2f} {math.sqrt(v['0.75']['design_effect_DE']):>9.3f} "
            f"{math.sqrt(v['0.0']['design_effect_DE']):>9.3f}")
    say("")
    say("  Paper Fig 3(a) at 75%: iid 16.9%, HAC 7.2% historical / 7.9% re-seeded.")
    say("  Paper Table IV: rows 3.93-3.97x, G_info 1.75-1.94x, HAC/iid width 1.22-1.66x.")
    say("  NOT numerically comparable: rho, subject count, session count, session")
    say("  duration, pair correlation and the condition behind Fig 3(a) are all")
    say("  unpublished. The claim under test is structural, not numerical.")
    say("")
    say("  Paper SEV note: G_info is a VARIANCE ratio. In standard-error terms the")
    say("  same information gain is sqrt(G_info), i.e. 1.32x at G_info=1.75, not 1.75x.")

    res["paper_reference"] = {
        "iid_75": 0.169, "hac_75_historical": 0.0715, "hac_75_reseeded": 0.079,
        "row_growth": [3.93, 3.97], "G_info": [1.75, 1.94], "hac_over_iid_width": [1.22, 1.66],
        "note": "reference only, not a numerical target for this replication",
    }
    res["reproduction_status"] = "verified" if (
        t["T2_extended_iid_anticonservative_at_75"]
        and t["T2_extended_hac_below_iid_at_75"]) else "unverified"

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    with open(os.path.join(OUT, "estimator.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
