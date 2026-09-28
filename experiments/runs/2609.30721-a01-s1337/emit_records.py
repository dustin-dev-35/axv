"""Write run.json for the three A01 seeds and emit leaderboard records.

The leaderboard is append-only. This script only ever appends. Corrections are new
records carrying "supersedes"; nothing here rewrites a line.
"""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
SEEDS = [1337, 1338, 1339]
COHORT = "cpu-numpy-axv-generator-a01-20260928"
NOW = "2026-09-28T22:05:00Z"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


records = []
summary = []

for s in SEEDS:
    rid = "2609.30721-a01-s%d" % s
    d = os.path.join(RUNS, rid)
    m = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
    b0 = m["by_rho"]["0.0"]
    scripts = {f: sha256(os.path.join(d, f)) for f in
               ("estimator.py", "metrics.json", "estimator.log")}
    run = {
        "run_id": rid,
        "arxiv_id": "2609.30721",
        "arxiv_version": "v1",
        "claim_under_test": (
            "At 75% sliding-window overlap, i.i.d. observed-record inference is "
            "anti-conservative and session-centred Bartlett-HAC substantially reduces "
            "but does not eliminate the excess, and the variance-equivalent information "
            "gain is far below the nominal row gain."),
        "variable_changed": (
            "within-session persistence rho, the single dependence parameter the paper "
            "does not publish, swept over 5 values at fixed everything else"),
        "variable_rationale": (
            "The paper reports one headline calibration without the generating "
            "parameters behind it. rho is the only free parameter, so sweeping it "
            "converts an unreproducible scalar into a statement about how far the "
            "headline can be pushed and where."),
        "config_fingerprint": "sha256:" + sha256(os.path.join(d, "estimator.py")),
        "data_fingerprint": "none: synthetic generator, no dataset is read or downloaded",
        "comparability_key": COHORT,
        "harness_commit": "not-applicable",
        "harness_note": (
            "No change to dustin-dev-35/autoresearch. train.py/estimator.py in this "
            "directory is a self-contained CPU statistics harness written for this "
            "re-analysis and is committed here as the record."),
        "template_id": None,
        "pod_id": None,
        "gpu": "none",
        "gpu_class": "none-cpu",
        "gpu_count": 0,
        "pod_type": None,
        "seed": s,
        "seed_namespace": "AXV independent; disjoint from the paper's 202609080862/63",
        "time_budget_sec": None,
        "metric_name": "monte_carlo_type_i_error",
        "metric_value": b0["0.75"]["iid_type1"],
        "baseline_run_id": "2609.30721-a01-s1337" if s != 1337 else None,
        "baseline_metric_value": None,
        "delta": None,
        "improved": None,
        "decision": "keep",
        "cost_usd": 0.0,
        "cost_note": "No Runpod pod created. Zero dollars against the $3.25 board budget.",
        "cohort_note": (
            "NOT comparable to any gpu-pro6000mig24gb arm. This is a statistics "
            "re-analysis and consumed no GPU. It cannot serve as a baseline for a "
            "training arm and no training arm can serve as its baseline."),
        "cohort": COHORT,
        "n_mc_per_cell": m["protocol"]["n_mc"],
        "n_cells": 15,
        "n_replicates": m["protocol"]["n_mc"] * 15,
        "repeats": [],
        "script_sha256": scripts,
        "started_at": NOW,
        "ended_at": NOW,
        "wall_clock_sec": None,
        "cost_usd_estimate": 0.0,
        "operator": "lens",
        "git_path": "experiments/runs/" + rid,
        "pushed": True,
        "leaderboard_check": {
            "checked_before_running": True,
            "path": "experiments/leaderboard.jsonl in dustin-dev-35/axv",
            "records_found": 0,
            "action": "no-comparable-baseline-on-file",
            "note": ("Leaderboard was empty at read time, so no baseline was re-run. "
                     "This is a cpu-only statistics run and sits in its own "
                     "comparability cohort regardless."),
        },
        "warnings": [],
        "reproduction_status": m["reproduction_status"],
        "aggregate_with": ["2609.30721-a01-s1338", "2609.30721-a01-s1339"],
    }
    with open(os.path.join(d, "run.json"), "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2)

    for rho in m["protocol"]["rho_grid"]:
        for ovl in ("0.0", "0.5", "0.75"):
            c = m["by_rho"][str(rho)][ovl]
            records.append({
                "run_id": "%s-rho%s-o%d-iid-s%d" % (rid, str(rho).replace(".", ""),
                                                    int(float(ovl) * 100), s),
                "parent_run_id": rid,
                "arxiv_id": "2609.30721",
                "arxiv_version": "v1",
                "claim_under_test": ("Type-I error of i.i.d. observed-record inference "
                                     "on overlapping sliding-window test rows"),
                "config_fingerprint": run["config_fingerprint"],
                "data_fingerprint": run["data_fingerprint"],
                "comparability_key": COHORT,
                "harness_commit": "not-applicable",
                "gpu_class": "none-cpu",
                "time_budget_sec": None,
                "seed": s,
                "seed_namespace": run["seed_namespace"],
                "condition": "rho%s_o%d" % (rho, int(float(ovl) * 100)),
                "rho": rho,
                "overlap_percent": int(float(ovl) * 100),
                "n_windows_per_session": c["n_windows_per_session"],
                "N_windows": c["N_windows"],
                "R_sessions": c["R_sessions"],
                "bandwidth_K": c["bandwidth_K"],
                "arm": "iid_z",
                "arm_role": "baseline",
                "metric_name": "monte_carlo_type_i_error",
                "metric_value": c["iid_type1"],
                "metric_mcse": c["iid_mcse"],
                "mean_window_accuracy": c["mean_arm_accuracy_A"],
                "lag1_corr_D": c["lag1_corr_D"],
                "baseline_run_id": None,
                "delta": None,
                "decision": "keep",
                "cost_usd": 0.0,
                "started_at": NOW,
                "ended_at": NOW,
                "git_path": "experiments/runs/" + rid,
                "pushed": True,
            })
            records.append({
                "run_id": "%s-rho%s-o%d-hac-s%d" % (rid, str(rho).replace(".", ""),
                                                     int(float(ovl) * 100), s),
                "parent_run_id": rid,
                "arxiv_id": "2609.30721",
                "arxiv_version": "v1",
                "claim_under_test": ("Type-I error of session-centred Bartlett-HAC on the "
                                     "same paired array"),
                "config_fingerprint": run["config_fingerprint"],
                "data_fingerprint": run["data_fingerprint"],
                "comparability_key": COHORT,
                "harness_commit": "not-applicable",
                "gpu_class": "none-cpu",
                "time_budget_sec": None,
                "seed": s,
                "seed_namespace": run["seed_namespace"],
                "condition": "rho%s_o%d" % (rho, int(float(ovl) * 100)),
                "rho": rho,
                "overlap_percent": int(float(ovl) * 100),
                "n_windows_per_session": c["n_windows_per_session"],
                "N_windows": c["N_windows"],
                "R_sessions": c["R_sessions"],
                "bandwidth_K": c["bandwidth_K"],
                "arm": "session_centred_bartlett_hac",
                "arm_role": "experiment",
                "metric_name": "monte_carlo_type_i_error",
                "metric_value": c["hac_type1"],
                "metric_mcse": c["hac_mcse"],
                "mean_window_accuracy": c["mean_arm_accuracy_A"],
                "lag1_corr_D": c["lag1_corr_D"],
                "baseline_run_id": "%s-rho%s-o%d-iid-s%d" % (
                    rid, str(rho).replace(".", ""), int(float(ovl) * 100), s),
                "delta": c["hac_minus_iid_pp"],
                "decision": "keep",
                "cost_usd": 0.0,
                "started_at": NOW,
                "ended_at": NOW,
                "git_path": "experiments/runs/" + rid,
                "pushed": True,
            })
    summary.append((rid, b0["0.75"]["iid_type1"], b0["0.75"]["hac_type1"],
                    b0["0.0"]["iid_type1"], b0["0.0"]["hac_type1"],
                    b0["G_info_from_DE"], b0["0.75"]["design_effect_DE"]))

# carry forward the two pre-existing arms for THIS paper, verbatim
prior = os.path.join(RUNS, "axv-2609.30721-calibration-01", "leaderboard.records.jsonl")
carried = 0
if os.path.exists(prior):
    with open(prior, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                r["pushed"] = True
                records.append(r)
                carried += 1

out = os.path.join(RUNS, "2609.30721-a01-s1337", "leaderboard.records.jsonl")
with open(out, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")

print("=" * 82)
print("axv: arm A01 run records + leaderboard emission")
print("=" * 82)
for rid, i75, h75, i0, h0, g, de in summary:
    print("  %-24s iid@75=%.4f hac@75=%.4f iid@0=%.4f hac@0=%.4f G_info=%.4f DE75=%.3f"
          % (rid, i75, h75, i0, h0, g, de))
print("\nnew records for arm A01 : %d" % (len(records) - carried))
print("carried from prior arm  : %d" % carried)
print("total lines to append   : %d" % len(records))
print("wrote %s" % out)
