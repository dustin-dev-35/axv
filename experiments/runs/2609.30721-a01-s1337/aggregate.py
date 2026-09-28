"""Aggregate the three seeds of arm A01 into metrics_aggregate.json.

Mirrors the `repeats` field in run.json: every number a memo cites from this arm
must be a min-max range over these three seeds, not a single run.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
SEEDS = ["2609.30721-a01-s1337", "2609.30721-a01-s1338", "2609.30721-a01-s1339"]

data = [json.load(open(os.path.join(RUNS, s, "metrics.json"), encoding="utf-8")) for s in SEEDS]
seeds = [d["seed"] for d in data]


def cell(rho, ovl, field):
    return [d["by_rho"][str(rho)][ovl][field] for d in data]


def gspan(field):
    return [d["by_rho"][str(rho)]["G_info_from_DE"] for d in data for rho in d["by_rho"]]


out = {
    "arm": "A01",
    "arxiv_id": "2609.30721",
    "arxiv_version": "v1",
    "seeds": seeds,
    "n_seeds": len(seeds),
    "n_mc_per_cell": data[0]["protocol"]["n_mc"],
    "cells": [],
    "tests_per_seed": {s: d["tests"] for s, d in zip(seeds, data)},
    "reproduction_status_per_seed": {s: d["reproduction_status"] for s, d in zip(seeds, data)},
}

for rho in data[0]["protocol"]["rho_grid"]:
    for ovl in ("0.0", "0.5", "0.75"):
        c = data[0]["by_rho"][str(rho)][ovl]
        out["cells"].append({
            "rho": rho, "overlap": float(ovl),
            "n_windows_per_session": c["n_windows_per_session"],
            "N_windows": c["N_windows"], "R_sessions": c["R_sessions"],
            "bandwidth_K": c["bandwidth_K"],
            "iid_type1": cell(rho, ovl, "iid_type1"),
            "iid_type1_min": min(cell(rho, ovl, "iid_type1")),
            "iid_type1_max": max(cell(rho, ovl, "iid_type1")),
            "hac_type1": cell(rho, ovl, "hac_type1"),
            "hac_type1_min": min(cell(rho, ovl, "hac_type1")),
            "hac_type1_max": max(cell(rho, ovl, "hac_type1")),
            "design_effect_DE": cell(rho, ovl, "design_effect_DE"),
            "lag1_corr_D": cell(rho, ovl, "lag1_corr_D"),
            "mean_arm_accuracy_A": cell(rho, ovl, "mean_arm_accuracy_A"),
            "mean_arm_accuracy_B": cell(rho, ovl, "mean_arm_accuracy_B"),
        })

g = gspan("G_info_from_DE")
out["G_info_across_rho_and_seeds"] = {
    "min": min(g), "max": max(g), "span": max(g) - min(g),
    "n_values": len(g),
}
gi = [d["by_rho"]["0.0"]["G_info_from_DE"] for d in data]
out["G_info_mechanical_only_rho0"] = {"values": gi, "min": min(gi), "max": max(gi)}
gh = [d["by_rho"]["0.0"]["G_info_from_hac_var"] for d in data]
out["G_info_from_hac_estimator_rho0"] = {"values": gh, "min": min(gh), "max": max(gh)}
iid75 = [d["by_rho"]["0.0"]["0.75"]["iid_type1"] for d in data]
hac75 = [d["by_rho"]["0.0"]["0.75"]["hac_type1"] for d in data]
out["headline_rho0_overlap75"] = {
    "iid_type1": iid75, "iid_min": min(iid75), "iid_max": max(iid75),
    "hac_type1": hac75, "hac_min": min(hac75), "hac_max": max(hac75),
    "nominal": 0.05,
    "paper_iid": 0.169, "paper_hac_historical": 0.0715, "paper_hac_reseeded": 0.079,
}
out["pre_registered_tests"] = {
    "T1_mechanical_only_iid_calibrated":
        all(d["tests"]["T1_mechanical_only_iid_calibrated"] for d in data),
    "T1_mechanical_only_G_info_near_one":
        all(d["tests"]["T1_mechanical_only_G_info_near_one"] for d in data),
    "T2_extended_iid_anticonservative_at_75":
        all(d["tests"]["T2_extended_iid_anticonservative_at_75"] for d in data),
    "T2_extended_hac_below_iid_at_75":
        all(d["tests"]["T2_extended_hac_below_iid_at_75"] for d in data),
    "T3_G_info_span_gt_0.5":
        all(d["tests"]["T3_G_info_span_gt_0.5"] for d in data),
    "T4_hac_still_anticonservative_at_top_of_grid":
        all(d["tests"]["T4_hac_still_anticonservative_at_top_of_grid"] for d in data),
}
out["interpretation"] = {
    "T1_refuted": "Mechanical overlap alone produces the whole headline. i.i.d. "
                  "Type-I is far above 5% at 75% overlap and G_info is well away "
                  "from 1.00 with zero extra serial dependence. AXV's pre-registered "
                  "hypothesis that the effect needs beyond-overlap dependence is "
                  "refuted; the result is recorded unrevised.",
    "T2_confirmed": "i.i.d. anti-conservativeness appears and HAC reduces it, "
                    "matching the paper directionally on all three seeds.",
    "T3_refuted": "G_info is comparatively stable across the persistence grid, so "
                  "it is not a wildly dataset-specific constant. AXV's stated "
                  "hypothesis that it varies by more than 0.5 is not supported.",
    "T4_confirmed": "HAC remains anti-conservative at 75% overlap across the grid, "
                    "matching the paper's own residual-miscalibration caveat.",
    "circularity_note": "G_info_from_hac_var is a ratio of the estimator's own "
                        "variance estimates and inherits its bias. G_info_from_DE "
                        "measures the same ratio against Monte Carlo ground truth. "
                        "The two agree to within about 10%, so the estimator is not "
                        "badly biased here, but only the DE version is checkable.",
    "se_note": "G_info is a VARIANCE ratio. In standard-error terms the same "
               "information gain is sqrt(G_info): 1.30x at G_info=1.68, not 1.68x.",
}

with open(os.path.join(HERE, "metrics_aggregate.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)

h = out["headline_rho0_overlap75"]
print("=" * 88)
print("arXiv:2609.30721v1 -- arm A01 aggregate over seeds %s" % seeds)
print("=" * 88)
print("\nHEADLINE, mechanical-overlap-only (rho=0), 75%% overlap, %d MC sets x %d seeds:"
      % (out["n_mc_per_cell"], out["n_seeds"]))
print("  iid  Type-I : %.2f - %.2f %%   (paper 16.9%%)" % (100 * h["iid_min"], 100 * h["iid_max"]))
print("  HAC  Type-I : %.2f - %.2f %%   (paper 7.2%% historical / 7.9%% re-seeded)"
      % (100 * h["hac_min"], 100 * h["hac_max"]))
print("  nominal     : 5.00 %%\n")
print("G_info, 0%% -> 75%% overlap, %.2fx more rows:" % data[0]["by_rho"]["0.0"]["row_growth"])
gi = out["G_info_mechanical_only_rho0"]
gh = out["G_info_from_hac_estimator_rho0"]
print("  paper's own estimator ratio : %.4f - %.4f  (paper Table IV 1.75-1.94)"
      % (gh["min"], gh["max"]))
print("  against Monte Carlo truth  : %.4f - %.4f" % (gi["min"], gi["max"]))
g = out["G_info_across_rho_and_seeds"]
print("  across rho grid and seeds   : %.4f - %.4f  (span %.4f, n=%d)"
      % (g["min"], g["max"], g["span"], g["n_values"]))
print("\nPRE-REGISTERED TESTS, all three seeds:")
for k, v in out["pre_registered_tests"].items():
    print("  %-46s %s" % (k, v))
print("\nPER-SEED DETAIL, rho=0:")
print("  %-6s %-9s %-9s %-9s %-9s" % ("seed", "iid@0%", "hac@0%", "iid@75%", "hac@75%"))
for d, s in zip(data, seeds):
    b = d["by_rho"]["0.0"]
    print("  %-6d %-9.2f %-9.2f %-9.2f %-9.2f"
          % (s, 100 * b["0.0"]["iid_type1"], 100 * b["0.0"]["hac_type1"],
             100 * b["0.75"]["iid_type1"], 100 * b["0.75"]["hac_type1"]))
print("\n" + out["interpretation"]["T1_refuted"])
print(out["interpretation"]["T3_refuted"])
print(out["interpretation"]["se_note"])
print("\nwrote metrics_aggregate.json")
