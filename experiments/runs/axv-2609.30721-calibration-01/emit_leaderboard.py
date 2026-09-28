"""Emit the leaderboard records for axv-2609.30721-calibration-01.

One record per (condition, arm, seed). Append-only. The paired contrast AXV
actually cares about is `delta` = HAC Type-I error minus IID Type-I error for
the SAME seed and the SAME condition, because both arms consume the identical
paired difference array per replication.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_ID = HERE.name
COHORT = "cpu-numpy-frozen-upstream-code-20260928"
FINGERPRINT = json.loads((HERE / "run.json").read_text(encoding="utf-8"))["config_fingerprint"]
DATA_FINGERPRINT = "generator:run_inference_revision.draw+simulation.py (no dataset; see run.json upstream_sha256)"
GIT_PATH = f"experiments/runs/{RUN_ID}"
NOW = datetime.now(timezone.utc).isoformat()

metrics = json.loads((HERE / "metrics.json").read_text(encoding="utf-8"))
per_seed = metrics["per_seed"]

ARM_ROLE = {
    "iid_z": "baseline",
    "original_global_bandwidth": "treatment",
    "equal_subject_t": "treatment-target-matched",
}


def main() -> None:
    lines = []
    by_key = {(r["condition"], r["arm"], r["master_seed"]): r for r in per_seed}
    for rec in per_seed:
        if rec["arm"] == "iid_z":
            continue
        base = by_key.get((rec["condition"], "iid_z", rec["master_seed"]))
        delta = None
        if base is not None:
            delta = rec["type_i_error"] - base["type_i_error"]
        lines.append(
            dict(
                run_id=f"{RUN_ID}-{rec['condition']}-a{rec['arm'][:4]}-s{rec['master_seed']}",
                parent_run_id=RUN_ID,
                arxiv_id="2609.30721",
                arxiv_version="v1",
                claim_under_test=(
                    "IID observed-record inference is anti-conservative at 75 percent "
                    "sliding-window overlap; session-centred Bartlett-HAC is not, and only "
                    "the target-matched equal-subject arm is calibrated for a new-subject target"
                ),
                config_fingerprint=FINGERPRINT,
                data_fingerprint=DATA_FINGERPRINT,
                comparability_key=COHORT,
                harness_commit=(
                    "unpushed; upstream artifact pinned by sha256 in run.json "
                    "(Paperclip GitHub capability_rejected in this run)"
                ),
                gpu_class="none-cpu",
                time_budget_sec=3600,
                seed=rec["master_seed"],
                seed_namespace="AXV independent; disjoint from paper master_seed 202609080862",
                condition=rec["condition"],
                overlap_percent=rec["overlap_percent"],
                regime=rec["regime"],
                arm=rec["arm"],
                arm_role=ARM_ROLE[rec["arm"]],
                metric_name="monte_carlo_type_i_error",
                metric_value=rec["type_i_error"],
                reject_count=rec["reject_count"],
                valid_runs=rec["valid_runs"],
                mean_ci_width=rec["mean_ci_width"],
                mean_variance=rec["mean_variance"],
                baseline_run_id=(
                    f"{RUN_ID}-{rec['condition']}-aiid_-s{rec['master_seed']}"
                    if base is not None
                    else None
                ),
                delta=delta,
                decision=(
                    "keep" if rec["arm"] == "original_global_bandwidth" else "inconclusive"
                ),
                cost_usd=0.0,
                started_at=rec.get("started_at", NOW),
                ended_at=NOW,
                git_path=GIT_PATH,
                pushed=False,
            )
        )
        if base is not None:
            lines.append(
                dict(
                    run_id=f"{RUN_ID}-{rec['condition']}-aiid_-s{rec['master_seed']}",
                    parent_run_id=RUN_ID,
                    arxiv_id="2609.30721",
                    arxiv_version="v1",
                    claim_under_test="baseline arm: pooled IID normal interval on the same paired array",
                    config_fingerprint=FINGERPRINT,
                    data_fingerprint=DATA_FINGERPRINT,
                    comparability_key=COHORT,
                    harness_commit=(
                        "unpushed; upstream artifact pinned by sha256 in run.json"
                    ),
                    gpu_class="none-cpu",
                    time_budget_sec=3600,
                    seed=rec["master_seed"],
                    seed_namespace="AXV independent; disjoint from paper master_seed 202609080862",
                    condition=rec["condition"],
                    overlap_percent=rec["overlap_percent"],
                    regime=rec["regime"],
                    arm="iid_z",
                    arm_role="baseline",
                    metric_name="monte_carlo_type_i_error",
                    metric_value=base["type_i_error"],
                    reject_count=base["reject_count"],
                    valid_runs=base["valid_runs"],
                    mean_ci_width=base["mean_ci_width"],
                    mean_variance=base["mean_variance"],
                    baseline_run_id=None,
                    delta=None,
                    decision="keep",
                    cost_usd=0.0,
                    started_at=base.get("started_at", NOW),
                    ended_at=NOW,
                    git_path=GIT_PATH,
                    pushed=False,
                )
            )
    seen = {}
    for x in lines:
        seen.setdefault(x["run_id"], x)
    lines = [seen[k] for k in sorted(seen)]
    (HERE / "leaderboard.records.jsonl").write_text(
        "\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8"
    )
    print(f"{len(lines)} records")


if __name__ == "__main__":
    main()
