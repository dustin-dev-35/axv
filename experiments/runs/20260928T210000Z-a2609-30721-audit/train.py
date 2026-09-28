import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.stats import norm

OUT = Path(__file__).resolve().parent
Z975 = 1.959963984540054

L_RAW = 64
T_RAW = 1728
N_SUBJECTS = 22
SESSIONS_PER_SUBJECT = 2
N_SESSIONS = N_SUBJECTS * SESSIONS_PER_SUBJECT
ACC_A = 0.8
ACC_B = 0.8
DISAGREE_RATE = 0.15
DISAGREE_SD = 0.02
SESSION_SD = 0.25
MODEL_PAIR_RHO = 0.3

M_REPS = 2000
M_REPS_B = 1000
M_REPS_C = 500
M_REPS_D = 500
M_REPS_E = 2000
M_REPS_F = 2000
SEEDS = (0, 1, 2)
RHO_GRID = (0.0, 0.34, 0.50, 0.70, 0.80, 0.85, 0.90)
RHO_MATCH = 0.70

Q_A = norm.ppf(1.0 - ACC_A)
Q_B = norm.ppf(1.0 - ACC_B)


def stride_of(overlap):
    return int(round(L_RAW * (1.0 - overlap)))


def n_windows(overlap):
    return (T_RAW - L_RAW) // stride_of(overlap) + 1


def bandwidth(overlap, nw, tbar_windows, k_override=None):
    k0 = int(math.ceil(L_RAW / stride_of(overlap))) - 1
    knw = int(math.floor(4.0 * (tbar_windows / 100.0) ** (2.0 / 9.0)))
    k_main = k_override if k_override is not None else max(knw, 2 * k0)
    return dict(k0=k0, knw=knw, k_main=int(k_main), k_used=int(min(k_main, nw - 1)))


def sign_chain_ar1(rng, nw, rho_d, fresh_p):
    s = np.empty((N_SESSIONS, nw))
    s[:, 0] = np.where(rng.random(N_SESSIONS) < fresh_p, 1.0, -1.0)
    for t in range(1, nw):
        stay = rng.random(N_SESSIONS) < rho_d
        draw = np.where(rng.random(N_SESSIONS) < fresh_p, 1.0, -1.0)
        s[:, t] = np.where(stay, s[:, t - 1], draw)
    return s


def sign_chain_block(rng, nw, mean_run, fresh_p):
    s = np.empty((N_SESSIONS, nw))
    p_flip = 1.0 / mean_run
    cur = np.where(rng.random(N_SESSIONS) < fresh_p, 1.0, -1.0)
    for t in range(nw):
        flip = rng.random(N_SESSIONS) < p_flip
        cur = np.where(flip, np.where(rng.random(N_SESSIONS) < fresh_p, 1.0, -1.0), cur)
        s[:, t] = cur
    return s


def long_run_inflation(shape, param):
    if shape == "ar1":
        return (1.0 + param) / (1.0 - param)
    return param


def paired_contrast(rng, nw, param, shape="ar1", session_sd=SESSION_SD):
    delta = rng.normal(0.0, session_sd, size=N_SESSIONS)
    fresh_p = (1.0 + delta) / 2.0
    if shape == "ar1":
        s = sign_chain_ar1(rng, nw, param, fresh_p)
    else:
        s = sign_chain_block(rng, nw, param, fresh_p)
    p_dis = np.clip(rng.normal(DISAGREE_RATE, DISAGREE_SD, size=N_SESSIONS), 0.02, 0.98)
    gate = rng.random((N_SESSIONS, nw)) < p_dis[:, None]
    return (gate * s).astype(np.float64)


def iid_reject(D):
    n = D.size
    se = D.std(ddof=1) / math.sqrt(n)
    return se > 0 and abs(D.mean() / se) > Z975


def hac_var(D, nw, overlap, k_override=None):
    n = D.size
    c = n / (n - N_SESSIONS)
    k = bandwidth(overlap, nw, n / N_SESSIONS, k_override=k_override)["k_used"]
    t = D.reshape(N_SESSIONS, nw)
    u = t - t.mean(axis=1, keepdims=True)
    total = float((u * u).sum())
    for h in range(1, k + 1):
        total += 2.0 * (1.0 - h / (k + 1.0)) * float((u[:, : nw - h] * u[:, h:]).sum())
    return c * total / (n * n)


def hac_reject(D, nw, overlap, k_override=None):
    v = hac_var(D, nw, overlap, k_override=k_override)
    return v > 0 and abs(D.mean() / math.sqrt(v)) > Z975


def sc0_reject(D, nw):
    return hac_reject(D, nw, 0.0, k_override=0)


def flat_rho_equivalent(inflation, n):
    r = (inflation - 1.0) / (inflation + 1.0)
    return r


def null_arm(overlap, rho_d, seed, m_reps, shape="ar1", session_sd=SESSION_SD):
    rng = np.random.default_rng(seed)
    nw = n_windows(overlap)
    r_iid = r_hac = r_sc0 = 0
    for _ in range(m_reps):
        D = paired_contrast(rng, nw, rho_d, shape, session_sd)
        r_iid += iid_reject(D)
        r_hac += hac_reject(D, nw, overlap)
        r_sc0 += sc0_reject(D, nw)
    p_i, p_h, p_s = r_iid / m_reps, r_hac / m_reps, r_sc0 / m_reps
    return dict(
        overlap=overlap, rho_d=rho_d, shape=shape, session_sd=session_sd, seed=seed, reps=m_reps, n_windows=nw,
        n_rows=int(nw * N_SESSIONS), n_sessions=N_SESSIONS,
        type1_iid=p_i, type1_hac=p_h, type1_sc0=p_s,
        mcse_iid=math.sqrt(p_i * (1 - p_i) / m_reps),
        mcse_hac=math.sqrt(p_h * (1 - p_h) / m_reps),
        mcse_sc0=math.sqrt(p_s * (1 - p_s) / m_reps),
        bandwidth=bandwidth(overlap, nw, nw),
        ar1_variance_inflation=long_run_inflation(shape, rho_d),
    )


def info_growth_arm(seed, m_reps, shape, session_sd):
    rng = np.random.default_rng(1_000_000 + seed)
    nw0, nw75 = n_windows(0.0), n_windows(0.75)
    k_p0 = bandwidth(0.0, nw0, nw0)["k_main"]
    k_p75 = bandwidth(0.75, nw75, nw75)["k_main"]
    acc = {kk: [] for kk in ("v0_paper", "v75_paper", "v0_fixed", "v75_fixed")}
    for _ in range(m_reps):
        p0 = RHO_MATCH * 0.0
        p75 = RHO_MATCH * 1.0
        d0 = paired_contrast(rng, nw0, p0, shape, session_sd)
        d75 = paired_contrast(rng, nw75, p75, shape, session_sd)
        acc["v0_paper"].append(hac_var(d0, nw0, 0.0))
        acc["v75_paper"].append(hac_var(d75, nw75, 0.75))
        acc["v0_fixed"].append(hac_var(d0, nw0, 0.0, k_override=k_p75))
        acc["v75_fixed"].append(hac_var(d75, nw75, 0.75, k_override=k_p75))
    mean = {kk: float(np.mean(v)) for kk, v in acc.items()}
    return dict(
        seed=seed, reps=m_reps, shape=shape, session_sd=session_sd,
        nominal_row_growth=nw75 / nw0, k_main_0pct=k_p0, k_main_75pct=k_p75,
        fixed_bandwidth_k=k_p75,
        g_info_paper=mean["v0_paper"] / mean["v75_paper"],
        g_info_fixed=mean["v0_fixed"] / mean["v75_fixed"],
        var_0pct_paper=mean["v0_paper"], var_75pct_paper=mean["v75_paper"],
        var_0pct_fixed=mean["v0_fixed"], var_75pct_fixed=mean["v75_fixed"],
    )


def fmt(r):
    return dict(
        overlap=r["overlap"], rho_d=r["rho_d"], seed=r["seed"], reps=r["reps"],
        n_rows=r["n_rows"], k_main=r["bandwidth"]["k_main"],
        type1_iid=r["type1_iid"], type1_hac=r["type1_hac"], type1_sc0=r["type1_sc0"],
        mcse_iid=r["mcse_iid"], mcse_hac=r["mcse_hac"],
    )


def main():
    t0 = time.time()
    res = dict(
        run_id=OUT.name, kind="cpu-only-reanalysis", arxiv="2609.30721v1",
        objective=("Test whether the reported Type-I error pair (16.9 percent iid vs 7.2 "
                   "percent session-centred Bartlett-HAC at 75 percent overlap) and the "
                   "variance-equivalent information growth 1.75 to 1.94 are reproducible."),
        design=dict(
            n_subjects=N_SUBJECTS, sessions_per_subject=SESSIONS_PER_SUBJECT,
            n_sessions=N_SESSIONS, window_length_raw=L_RAW, raw_duration_per_session=T_RAW,
            margin_accuracy_a=ACC_A, margin_accuracy_b=ACC_B,
            disagreement_rate=DISAGREE_RATE, disagreement_sd=DISAGREE_SD,
            model_pair_rho=MODEL_PAIR_RHO, nominal_alpha=0.05,
            seeds=list(SEEDS), reps_arm_a=M_REPS, reps_arm_b=M_REPS_B,
            reps_arm_d=M_REPS_D, reps_arm_e=M_REPS_D, reps_arm_f=M_REPS_B,
            matched_inflation=5.667, matched_param={"ar1": 0.70, "block": 5.67},
            dgp_disclosure=("arXiv 2609.30721v1 section IV-A does not publish its null "
                            "data-generating process. This run publishes its own and sweeps "
                            "dependence magnitude, correlation shape, and between-session "
                            "heterogeneity, all of which are unidentifiable from the paper."),
        ),
        arm_a_within_session_dependence=[],
        arm_b_overlap_axis=[],
        arm_c_between_session_aggregation=[],
        arm_d_information_growth=[],
        arm_e_correlation_shape=[],
    )

    for seed in SEEDS:
        for rho in RHO_GRID:
            res["arm_a_within_session_dependence"].append(
                null_arm(0.75, rho, seed, M_REPS, "ar1", session_sd=0.0))
    for seed in SEEDS:
        for ov in (0.0, 0.5, 0.75):
            res["arm_b_overlap_axis"].append(
                null_arm(ov, RHO_MATCH * (ov / 0.75), seed, M_REPS, "ar1", session_sd=0.0))
    for seed in SEEDS:
        for ov in (0.0, 0.75):
            for sd in (0.10, 0.25, 0.40):
                res["arm_c_between_session_aggregation"].append(
                    null_arm(ov, 0.0, seed, M_REPS_F, "ar1", session_sd=sd))
    for seed in SEEDS:
        res["arm_d_information_growth"].append(
            info_growth_arm(seed, M_REPS_D, "ar1", 0.0))
    for seed in SEEDS:
        for shape, param in (("ar1", 0.70), ("block", 5.67)):
            res["arm_e_correlation_shape"].append(
                null_arm(0.75, param, seed, M_REPS_E, shape, session_sd=0.0))

    def agg(rows, key, val):
        sel = [r for r in rows if r[key] == val]
        if not sel:
            return None
        f = lambda k: sum(r[k] for r in sel) / len(sel)
        g = lambda k: max(r[k] for r in sel) - min(r[k] for r in sel)
        return dict(seeds=len(sel), reps=sel[0]["reps"], n_rows=sel[0]["n_rows"],
                    k_main=sel[0]["bandwidth"]["k_main"],
                    type1_iid=f("type1_iid"), type1_hac=f("type1_hac"), type1_sc0=f("type1_sc0"),
                    iid_spread=g("type1_iid"), hac_spread=g("type1_hac"))

    res["summary"] = dict(
        arm_a_by_rho=[dict(param=r, ar1_inflation=(1 + r) / (1 - r),
                           **agg(res["arm_a_within_session_dependence"], "rho_d", r))
                      for r in RHO_GRID],
        arm_b_by_overlap=[dict(overlap=ov, **agg(res["arm_b_overlap_axis"], "overlap", ov))
                          for ov in (0.0, 0.5, 0.75)],
        arm_c_by_session_sd=[dict(overlap=ov, session_sd=sd,
                                  **agg([r for r in res["arm_c_between_session_aggregation"]
                                         if r["overlap"] == ov], "session_sd", sd))
                             for ov in (0.0, 0.75) for sd in (0.10, 0.25, 0.40)],
        arm_d_by_seed=res["arm_d_information_growth"],
        arm_e_by_shape=[dict(shape=sh, param=pa, ar1_inflation=pa,
                             **agg([r for r in res["arm_e_correlation_shape"]
                                    if r["shape"] == sh], "rho_d", pa))
                        for sh, pa in (("ar1", 0.70), ("block", 5.67))],
        paper_targets=dict(iid_type1_75pct=0.169, hac_type1_75pct=0.072,
                           hac_reseeded=0.079, hac_wisdm5s_hist=0.089,
                           hac_wisdm5s_reseeded=0.067, hac_mcse_pp=0.58,
                           info_growth_range=(1.75, 1.94),
                           nominal_row_growth_range=(3.93, 3.97),
                           hac_over_iid_width_ratio_range=(1.22, 1.66),
                           centering_ratio_at_0pct=(0.81, 0.83)),
    )
    res["elapsed_seconds"] = round(time.time() - t0, 2)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

    L = []
    L.append("AXV CPU re-analysis of arXiv 2609.30721v1")
    L.append("run_id=%s  seeds=%s  alpha=0.05  gpu=none  usd_spent=0.00" % (OUT.name, list(SEEDS)))
    L.append("paper targets: iid_type1@75=0.169  hac_type1@75=0.072  nominal=0.05")
    L.append("")
    L.append("ARM A  within-session dependence only (session_sd=0), 75%% overlap, %d reps x %d seeds"
             % (M_REPS, len(SEEDS)))
    L.append(" param  infl    type1_iid  type1_hac  type1_sc0  iid_sprd  hac_sprd")
    for r in res["summary"]["arm_a_by_rho"]:
        L.append(" %.2f  %5.2f    %8.4f   %8.4f   %8.4f   %8.4f   %8.4f" % (
            r["param"], r["ar1_inflation"], r["type1_iid"], r["type1_hac"], r["type1_sc0"],
            r["iid_spread"], r["hac_spread"]))
    L.append("")
    L.append("ARM B  overlap axis, dependence coupled to overlap (session_sd=0), %d reps x %d seeds"
             % (M_REPS, len(SEEDS)))
    L.append(" ovlp  n_rows  K_main  type1_iid  type1_hac  type1_sc0  iid_sprd  hac_sprd")
    for r in res["summary"]["arm_b_by_overlap"]:
        L.append(" %.2f  %6d    %2d     %8.4f   %8.4f   %8.4f   %7.4f  %7.4f" % (
            r["overlap"], r["n_rows"], r["k_main"], r["type1_iid"], r["type1_hac"],
            r["type1_sc0"], r["iid_spread"], r["hac_spread"]))
    L.append("")
    L.append("ARM C  between-session heterogeneity only, no serial dependence, %d reps x %d seeds"
             % (M_REPS_F, len(SEEDS)))
    L.append(" ovlp  session_sd  n_rows  type1_iid  type1_hac  type1_sc0")
    for r in res["summary"]["arm_c_by_session_sd"]:
        L.append(" %.2f     %.2f      %6d    %8.4f   %8.4f   %8.4f" % (
            r["overlap"], r["session_sd"], r["n_rows"], r["type1_iid"], r["type1_hac"],
            r["type1_sc0"]))
    L.append("")
    L.append("ARM D  variance-equivalent information growth 0%% -> 75%%, %d reps x %d seeds"
             % (M_REPS_D, len(SEEDS)))
    r0 = res["arm_d_information_growth"][0]
    L.append(" nominal_row_growth=%.3f  K_main 0pct=%d  K_main 75pct=%d  fixed_K=%d"
             % (r0["nominal_row_growth"], r0["k_main_0pct"], r0["k_main_75pct"], r0["fixed_bandwidth_k"]))
    L.append(" seed  g_paper  g_fixed   var0_paper  var75_paper  var0_fixed  var75_fixed")
    for r in res["arm_d_information_growth"]:
        L.append(" %d   %6.4f  %6.4f    %.3e    %.3e    %.3e   %.3e" % (
            r["seed"], r["g_info_paper"], r["g_info_fixed"], r["var_0pct_paper"],
            r["var_75pct_paper"], r["var_0pct_fixed"], r["var_75pct_fixed"]))
    L.append("")
    L.append("ARM E  correlation shape at matched long-run variance, 75%% overlap, %d reps x %d seeds"
             % (M_REPS_E, len(SEEDS)))
    L.append(" shape  param  infl    type1_iid  type1_hac  type1_sc0  iid_sprd  hac_sprd")
    for r in res["summary"]["arm_e_by_shape"]:
        L.append(" %-6s %5.2f  %5.2f    %8.4f   %8.4f   %8.4f   %8.4f   %8.4f" % (
            r["shape"], r["param"], r["ar1_inflation"], r["type1_iid"], r["type1_hac"],
            r["type1_sc0"], r["iid_spread"], r["hac_spread"]))
    L.append("")
    L.append("elapsed_seconds=%.2f" % res["elapsed_seconds"])
    (OUT / "train.log").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()