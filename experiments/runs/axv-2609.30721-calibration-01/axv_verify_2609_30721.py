"""AXV independent re-verification of arXiv:2609.30721v1, Figure 3 calibration.

Arms (one variable: the inference rule applied to the SAME paired difference array):
  A. iid_z                    -- pooled IID normal interval (the paper's IID arm)
  B. original_global_bandwidth -- session-centred Bartlett-HAC, N/(N-R), global K
                              (the paper's "formal session-centred Bartlett-HAC" arm)

Conditions: the paper's Figure 3(a) balanced long-memory AR(1) null designs at
0/50/75 percent overlap, and the Figure 3(b) mixed-hierarchy new-subject design
at 75 percent, plus equal_subject_t as the target-matched arm for (b).

Seeds: three master seeds that are independent of the paper's
master_seed=202609080862 and of its smoke seed 202609080863.

Upstream code, used unmodified:
  run_inference_revision.py  (sha256 recorded in run.json)
  inference_frozen_code/simulation.py
  inference_frozen_code/calibration_engine.py
No file in the upstream tree is patched. The only change is `master` on the
line that selects the seed namespace.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_inference_revision as riv  # noqa: E402

REPETITIONS = 500
MASTER_SEEDS = (202609280001, 202609280002, 202609280003)

CONDITIONS = []
for _ov in (0, 50, 75):
    CONDITIONS.append(
        dict(
            id=f"balanced_ar1_o{_ov}_d0.00",
            kind="balanced",
            regime="long_memory",
            overlap=_ov,
            effect=0.0,
            phi=0.6,
            subject_count=24,
            sessions_per_subject=2,
            window_size=64,
            base_nonoverlap_windows=64,
        )
    )
CONDITIONS.append(
    dict(
        id="balanced_hierarchy_o75_d0.00",
        kind="balanced",
        regime="mixed_hierarchy",
        overlap=75,
        effect=0.0,
        phi=0.0,
        subject_count=24,
        sessions_per_subject=2,
        window_size=64,
        base_nonoverlap_windows=64,
    )
)

PRIMARY = ("iid_z", "original_global_bandwidth")
HIERARCHY_EXTRA = ("equal_subject_t",)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    started = time.time()
    out = HERE / "raw"
    out.mkdir(exist_ok=True)

    records = []
    for cond in CONDITIONS:
        lengths, subjects = riv.condition_arrays(cond)
        plan = riv.make_plan(lengths, cond["overlap"])
        arms = PRIMARY + (HIERARCHY_EXTRA if cond["regime"] == "mixed_hierarchy" else ())
        for master in MASTER_SEEDS:
            rejects = {a: 0 for a in arms}
            valid = {a: 0 for a in arms}
            width_sum = {a: 0.0 for a in arms}
            var_sum = {a: 0.0 for a in arms}
            for rep in range(REPETITIONS):
                seed = riv.seed_for(master, cond["id"], rep, "formal_evaluation")
                diff = riv.draw(cond, np.random.default_rng(seed))
                res = riv.evaluate(
                    diff, plan, cond["effect"],
                    subjects if cond["regime"] == "mixed_hierarchy" else None,
                )
                for row in res:
                    a = row["method"]
                    if a not in rejects:
                        continue
                    if row["valid"] != 1:
                        continue
                    valid[a] += 1
                    rejects[a] += int(row["reject_null"])
                    width_sum[a] += float(row["ci_width"])
                    var_sum[a] += float(row["variance"])
            for a in arms:
                records.append(
                    dict(
                        condition=cond["id"],
                        overlap_percent=cond["overlap"],
                        regime=cond["regime"],
                        arm=a,
                        master_seed=master,
                        replications=REPETITIONS,
                        valid_runs=valid[a],
                        reject_count=rejects[a],
                        type_i_error=rejects[a] / valid[a] if valid[a] else None,
                        mean_ci_width=width_sum[a] / valid[a] if valid[a] else None,
                        mean_variance=var_sum[a] / valid[a] if valid[a] else None,
                        n_windows=int(plan["N"]),
                        n_sessions=int(plan["R"]),
                        k0=int(plan["k0"]),
                        k_global=int(plan["global_k"]),
                    )
                )
            print(
                f"{cond['id']} seed={master} "
                + " ".join(
                    f"{a}={rejects[a]}/{valid[a]}" for a in arms
                ),
                flush=True,
            )

    summary = []
    for cond in CONDITIONS:
        for a in PRIMARY + (HIERARCHY_EXTRA if cond["regime"] == "mixed_hierarchy" else ()):
            sel = [r for r in records if r["condition"] == cond["id"] and r["arm"] == a]
            per_seed = [r["type_i_error"] for r in sel]
            pooled_rej = sum(r["reject_count"] for r in sel)
            pooled_val = sum(r["valid_runs"] for r in sel)
            summary.append(
                dict(
                    condition=cond["id"],
                    overlap_percent=cond["overlap"],
                    regime=cond["regime"],
                    arm=a,
                    pooled_type_i_error=pooled_rej / pooled_val,
                    pooled_rejects=pooled_rej,
                    pooled_valid=pooled_val,
                    per_seed_type_i_error=per_seed,
                    seed_spread=max(per_seed) - min(per_seed),
                    seed_sd=float(np.std(per_seed, ddof=1)),
                )
            )

    (HERE / "metrics.json").write_text(
        json.dumps(dict(summary=summary, per_seed=records), indent=2) + "\n",
        encoding="utf-8",
    )

    upstream = {
        "run_inference_revision.py": sha256_file(HERE / "run_inference_revision.py"),
        "inference_frozen_code/simulation.py": sha256_file(HERE / "inference_frozen_code" / "simulation.py"),
        "inference_frozen_code/calibration_engine.py": sha256_file(HERE / "inference_frozen_code" / "calibration_engine.py"),
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            dict(
                upstream=upstream,
                repetitions=REPETITIONS,
                master_seeds=MASTER_SEEDS,
                conditions=[c["id"] for c in CONDITIONS],
                arms=list(PRIMARY) + list(HIERARCHY_EXTRA),
            ),
            sort_keys=True,
        ).encode()
    ).hexdigest()

    run = dict(
        run_id=HERE.name,
        arxiv_id="2609.30721",
        arxiv_version="v1",
        claim_under_test=(
            "At 75% overlap, IID observed-record inference has 16.9% Type-I error versus "
            "7.2% for session-centred Bartlett-HAC, and for a new-subject target under "
            "subject/session heterogeneity IID reaches 72.4% while equal-subject paired "
            "inference reaches 5.5%."
        ),
        config_fingerprint=fingerprint,
        comparability_key="cpu-numpy-frozen-upstream-code-20260928",
        harness_commit="local/dirty: upstream artifact pinned by sha256, driver added",
        environment=dict(
            python=platform.python_version(),
            numpy=np.__version__,
            platform=platform.platform(),
            gpu="none (CPU-only Monte Carlo)",
        ),
        repetitions_per_seed=REPETITIONS,
        master_seeds=list(MASTER_SEEDS),
        upstream_sha256=upstream,
        paper_master_seed=202609080862,
        seconds=round(time.time() - started, 3),
        started_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    (HERE / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(config_fingerprint=fingerprint, seconds=run["seconds"])))


if __name__ == "__main__":
    main()
