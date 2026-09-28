"""Print the prediction checks and the seed-averaged surface from metrics.json."""
import json
import os

import train

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")
res = json.load(open(p, encoding="utf-8"))
res["predictions"] = train.check_predictions(res)
json.dump(res, open(p, "w", encoding="utf-8"), indent=2)

print("\n=== Type-I error surface (mean over 3 seeds, nominal 0.05) ===")
print(f"{'rho':>6} | {'IID ov0':>8} {'ov50':>8} {'ov75':>8} | {'HAC ov0':>8} {'ov50':>8} {'ov75':>8} | gap@75")
for row in res["predictions"]["surface_iid_vs_hac"]["rows"]:
    print("{:>6} | {:>8.3f} {:>8.3f} {:>8.3f} | {:>8.3f} {:>8.3f} {:>8.3f} | {:>7.3f}".format(
        row["rho"], *row["iid"], *row["hac"], row["gap"][2]))

print("\n=== Prediction checks ===")
for k, v in res["predictions"].items():
    if k == "surface_iid_vs_hac":
        continue
    print("{}: {}".format(k, "HOLDS" if v["holds"] else "FAILS"))
    print("    {}".format(v["detail"]))

print("\n=== Per-seed spread at rho=0.99, ov=75 (IID / HAC / SUBJ) ===")
for r in res["calibration"]:
    if r["rho"] == 0.99 and r["overlap"] == 75:
        print("  seed {}  IID={:.3f}+-{:.3f}  HAC={:.3f}+-{:.3f}  SUBJ={:.3f}+-{:.3f}".format(
            r["seed"], r["iid"], r["iid_mcse"], r["hac"], r["hac_mcse"],
            r["subj"], r["subj_mcse"]))
