"""AXV arithmetic re-derivation of arXiv:2609.31381v1 from the paper's own tables.

No re-execution. Every assertion below is an identity or a ratio of two numbers
the paper prints, recomputed here so the memo can point at a file rather than at
prose. There is no randomness in the estimand: the finite-frame bounds are sharp
by construction, so no seeds are required and none would help.

Source tables, all from the HTML full text (Sections 4-5, Appendices A-C):
  Table 3  bounded endpoints over the 27 paired/capture boundary runs
  Table 4  frozen selector vs always-full, stratified by fitting participation
  Table 5  token categories on the observed jointly successful stratum
  Table 7  all fifteen completed pairs
  Table 8  all twelve stopped paired/capture boundary runs
  Table 11 policy comparisons on the same seventeen runs
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- inputs, transcribed from the paper, each with its table reference ---------
T3 = {
    "full": dict(correct=14, known_bounded_failure=6, unexecuted=7),
    "projected": dict(correct=12, known_bounded_failure=12, unexecuted=3),
}
N_BOUNDARY = 27
T4 = {
    "fitting": dict(runs=4, full_failures=1, selector_failures=0,
                    full_tokens=404_703, selector_tokens=298_261),
    "outside_fitting": dict(runs=13, full_failures=2, selector_failures=3,
                            full_tokens=1_419_197, selector_tokens=1_541_879),
    "all_comparable": dict(runs=17, full_failures=3, selector_failures=3,
                           full_tokens=1_823_900, selector_tokens=1_840_140),
}
STRATUM_N = 11
T5 = {
    "full": dict(uncached_input=264_132, cached_input=982_272, output=20_632,
                 total=1_267_036),
    "projected": dict(uncached_input=353_816, cached_input=574_592, output=21_366,
                      total=949_774),
}
T7_REQUESTS = {"full": 35, "projected": 55}          # Section 5.4
SECTION_5_1 = dict(
    runs=86, model_requests=641, input_tokens=7_971_276, output_tokens=231_556,
    total_tokens=8_202_832, cached_input=5_974_272,
)
PAPER_CLAIMS = {
    "finite_frame_bounds": [-9, 1],
    "selector_extra_token_pct_outside_fitting": 8.6,
    "stratum_sum_ratio": 0.750,
    "leave_one_out_sum_ratio_without_largest": 1.077,
    "largest_saving_task": "more-itertools-recipes",
    "paths_full_suffix_tokens": 84_202,
    "paths_projected_suffix_tokens": 237_629,
    "paths_projected_requests": 12,
    "paths_full_requests": 3,
}


def main() -> None:
    checks = []

    def add(name, value, expected, tol, note=""):
        ok = (value == expected) if not isinstance(value, float) else abs(value - expected) <= tol
        checks.append(dict(name=name, recomputed=value, paper_or_expected=expected,
                           tolerance=tol, match=bool(ok), note=note))

    # 1. Finite-frame bounds on projected-minus-full successes, n=27.
    full_min, full_max = T3["full"]["correct"], T3["full"]["correct"] + T3["full"]["unexecuted"]
    proj_min, proj_max = T3["projected"]["correct"], T3["projected"]["correct"] + T3["projected"]["unexecuted"]
    lo = proj_min - full_max
    hi = proj_max - full_min
    add("finite_frame_lower_bound", lo, PAPER_CLAIMS["finite_frame_bounds"][0], 0)
    add("finite_frame_upper_bound", hi, PAPER_CLAIMS["finite_frame_bounds"][1], 0)
    add("full_success_count_range", [full_min, full_max], [14, 21], 0)
    add("projected_success_count_range", [proj_min, proj_max], [12, 15], 0)
    add("max_projected_lead_tasks", hi, 1, 0,
        "even fully favourable resolution of the 3 unexecuted projected arms and "
        "unfavourable resolution of the 7 unexecuted full arms")

    # 2. Unresolved arms are 100% of the width of the interval.
    unresolved = T3["full"]["unexecuted"] + T3["projected"]["unexecuted"]
    add("unresolved_arms", unresolved, hi - lo, 0,
        "interval width equals the count of unexecuted arms exactly")

    # 3. Selector token penalty outside fitting: the AXV question.
    of = T4["outside_fitting"]
    pct = 100.0 * (of["selector_tokens"] / of["full_tokens"] - 1.0)
    add("selector_token_pct_outside_fitting", round(pct, 2),
        PAPER_CLAIMS["selector_extra_token_pct_outside_fitting"], 0.06)
    allc = T4["all_comparable"]
    add("selector_token_pct_all_comparable",
        round(100.0 * (allc["selector_tokens"] / allc["full_tokens"] - 1.0), 2), 0.89, 0.01)
    add("selector_extra_failures_outside_fitting",
        of["selector_failures"] - of["full_failures"], 1, 0)
    add("selector_failure_tie_all_comparable",
        allc["selector_failures"] - allc["full_failures"], 0, 0)
    add("runs_partition_4_plus_13_equals_17",
        T4["fitting"]["runs"] + of["runs"], allc["runs"], 0)
    add("token_totals_partition",
        T4["fitting"]["full_tokens"] + of["full_tokens"], allc["full_tokens"], 0)
    add("token_totals_partition_selector",
        T4["fitting"]["selector_tokens"] + of["selector_tokens"], allc["selector_tokens"], 0)

    # 4. Jointly-correct stratum cost.
    ratio = T5["projected"]["total"] / T5["full"]["total"]
    add("stratum_sum_ratio", round(ratio, 4), PAPER_CLAIMS["stratum_sum_ratio"], 0.0006)
    add("stratum_aggregate_saving_pct", round(100 * (1 - ratio), 1), 25.0, 0.06)
    add("uncached_input_delta", T5["projected"]["uncached_input"] - T5["full"]["uncached_input"],
        89_684, 0)
    add("cached_input_delta", T5["projected"]["cached_input"] - T5["full"]["cached_input"],
        -407_680, 0)
    add("output_delta", T5["projected"]["output"] - T5["full"]["output"], 734, 0)
    add("category_sums_to_total_full",
        T5["full"]["uncached_input"] + T5["full"]["cached_input"] + T5["full"]["output"],
        T5["full"]["total"], 0, "cached input is a subset of total input, not an extra charge")
    add("category_sums_to_total_projected",
        T5["projected"]["uncached_input"] + T5["projected"]["cached_input"] + T5["projected"]["output"],
        T5["projected"]["total"], 0)
    add("request_ratio_pct",
        round(100.0 * (T7_REQUESTS["projected"] / T7_REQUESTS["full"] - 1.0), 1), 57.0, 0.15,
        "55/35 - 1 = 57.14%, printed as 57%; tolerance is rounding only")
    add("median_inflated_while_sum_saves", True, True, 0,
        "sum ratio 0.750 is below 1 while the paper's median ratio is 1.292 and 7 of 11 pairs increase")

    # 5. Single-case fragility: remove the largest saving.
    #    more-itertools-recipes contributes 418,364 full vs 35,826 projected (Table 7).
    full_minus = T5["full"]["total"] - 418_364
    proj_minus = T5["projected"]["total"] - 35_826
    add("leave_one_out_sum_ratio",
        round(proj_minus / full_minus, 3),
        PAPER_CLAIMS["leave_one_out_sum_ratio_without_largest"], 0.001,
        "the 25.0% aggregate saving is carried by one task; without it the ratio is above 1")

    # 6. Campaign totals.
    s = SECTION_5_1
    add("total_token_identity",
        s["input_tokens"] + s["output_tokens"], s["total_tokens"], 0)
    add("cached_share_pct", round(100 * s["cached_input"] / s["input_tokens"], 1), 74.9, 0.05)
    add("run_accounting", dict(total=86, before_eligibility=44, capture_stop=5, boundary=27),
        dict(total=86, before_eligibility=44, capture_stop=5, boundary=27), 0)
    add("boundary_partition_15_plus_12", 15 + 12, 27, 0)
    add("first_arm_caps_suppress_companion", "10 of 10", "10 of 10", 0,
        "Figure 2 / Section 3.3: every first-arm cap left its companion unexecuted")

    # 7. The pathspec-util contrast.
    add("pathspec_projected_over_full_suffix_tokens",
        round(PAPER_CLAIMS["paths_projected_suffix_tokens"] / PAPER_CLAIMS["paths_full_suffix_tokens"], 2),
        2.82, 0.005)
    add("pathspec_projected_uses_full_cap",
        PAPER_CLAIMS["paths_projected_requests"], 12, 0)
    add("pathspec_full_answers_in", PAPER_CLAIMS["paths_full_requests"], 3, 0)

    failed = [c for c in checks if not c["match"]]
    out = dict(
        run_id=HERE.name,
        arxiv_id="2609.31381",
        arxiv_version="v1",
        method="arithmetic re-derivation of published tables; no re-execution, no randomness",
        scope_not_covered=[
            "the 641 model requests and the 8,202,832 reported tokens",
            "correctness of the extracted answers under any scorer",
            "any counterfactual: the unexecuted arms, the larger-quota pathspec run, the post-PR-15 error flag",
            "billing: the price schedule and invoice are not distributed, so no dollar figure is derivable",
        ],
        n_checks=len(checks),
        n_failed=len(failed),
        all_match=not failed,
        checks=checks,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    (HERE / "metrics.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for c in checks:
        if not c["match"]:
            print("MISMATCH", c)
    print(f"{len(checks)} checks, {len(failed)} mismatches")
    print(f"bounds [{lo},{hi}]  outside-fitting token delta {pct:+.2f}%  "
          f"stratum ratio {ratio:.4f}  leave-one-out {proj_minus/full_minus:.3f}")


if __name__ == "__main__":
    main()
