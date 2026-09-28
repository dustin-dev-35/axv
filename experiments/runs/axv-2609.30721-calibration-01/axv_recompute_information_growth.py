"""AXV recheck of the real-data numbers in arXiv:2609.30721v1, from the authors'
own released result table.

This does not retrain anything. It recomputes, from
results/paper_ready_final/information_growth.csv (release v1.0.0), every
quantity the memo and abstract quote:

  1. nominal_window_growth  (the "nearly fourfold growth in test rows")
  2. inverse_hac_variance_information_growth  (the "1.75-1.94-fold" figure)
  3. ci_inflation_factor = hac_ci_width / iid_ci_width  (Table IV, HAC/IID)
  4. the alternative route: IID interval at 0% overlap versus the paper's
     HAC interval at 75% overlap, and the residual 0%-overlap HAC/IID ratio
     that decides whether plain IID is already close enough at 0% overlap.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "information_growth.csv"


def main() -> None:
    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8")))
    base = {}
    for r in rows:
        if float(r["overlap_percent"]) == 0:
            base[(r["dataset"], r["window_seconds"])] = r

    checks = []
    for r in rows:
        b = base[(r["dataset"], r["window_seconds"])]
        nominal_growth = float(r["nominal_window_count"]) / float(b["nominal_window_count"])
        info_growth = float(b["dependent_variance_K_main"]) / float(r["dependent_variance_K_main"])
        inflation = float(r["hac_ci_width"]) / float(r["iid_ci_width"])
        # alternative route: disjoint (0% overlap) windows with plain IID
        iid_at_0 = float(b["iid_ci_width"])
        hac_at_75 = float(r["hac_ci_width"]) if float(r["overlap_percent"]) == 75 else None
        checks.append(
            dict(
                dataset=r["dataset"],
                window_seconds=float(r["window_seconds"]),
                overlap_percent=int(r["overlap_percent"]),
                nominal_window_count=int(r["nominal_window_count"]),
                nominal_growth_recomputed=nominal_growth,
                nominal_growth_as_published=float(r["nominal_window_growth"]),
                information_growth_recomputed=info_growth,
                information_growth_as_published=float(r["inverse_hac_variance_information_growth"]),
                ci_inflation_recomputed=inflation,
                ci_inflation_as_published=float(r["ci_inflation_factor"]),
                iid_width_at_0pct=iid_at_0,
                hac_width_at_this_overlap=float(r["hac_ci_width"]),
                iid0_over_hac75=(iid_at_0 / hac_at_75) if hac_at_75 else None,
                hac0_over_iid0=float(b["ci_inflation_factor"]),
                hac_width_from_published_inflation=float(r["iid_ci_width"]) * inflation,
            )
        )

    worst = {
        "max_abs_error_nominal_growth": max(
            abs(c["nominal_growth_recomputed"] - c["nominal_growth_as_published"]) for c in checks
        ),
        "max_abs_error_information_growth": max(
            abs(c["information_growth_recomputed"] - c["information_growth_as_published"]) for c in checks
        ),
        "max_abs_error_ci_inflation": max(
            abs(c["ci_inflation_recomputed"] - c["ci_inflation_as_published"]) for c in checks
        ),
    }

    out = dict(
        source_file="information_growth.csv",
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_provenance="https://github.com/xinze8806-ship-it/sliding-window-confidence-audit release v1.0.0",
        recomputation_is="arithmetic identity check of the authors' published variance table; no retraining, no new predictions",
        consistency=worst,
        rows=checks,
        alternative_route_summary=[
            dict(
                dataset=c["dataset"],
                window_seconds=c["window_seconds"],
                iid_width_at_0pct_overlap=c["iid_width_at_0pct"],
                hac_width_at_75pct_overlap=c["hac_width_at_this_overlap"],
                ratio=c["iid0_over_hac75"],
                hac0_over_iid0=c["hac0_over_iid0"],
            )
            for c in checks
            if c["overlap_percent"] == 75
        ],
    )
    (HERE / "metrics_information_growth.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(worst, indent=2))
    for c in out["alternative_route_summary"]:
        print(
            f"{c['dataset']} {c['window_seconds']}s: IID@0%={c['iid_width_at_0pct_overlap']:.6f} "
            f"HAC@75%={c['hac_width_at_75pct_overlap']:.6f} ratio={c['ratio']:.3f} "
            f"HAC0/IID0={c['hac0_over_iid0']:.3f}"
        )


if __name__ == "__main__":
    main()
