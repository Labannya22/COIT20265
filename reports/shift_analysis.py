"""
Distribution shift between training and testing normal traffic
COIT20265 - WBS 3.0 - Labannya Barua

The sanity check found that thresholds calibrated on normal validation
data do not transfer to the test partition:

    budget 0.5%  ->  actual FPR 0.70%   (1.4x)
    budget 1.0%  ->  actual FPR 2.13%   (2.1x)
    budget 3.0%  ->  actual FPR 9.90%   (3.3x)

That gap breaks the false-positive-budget mechanism the proposal claims
as an innovation, so it needs an explanation with numbers behind it, not
a guess.

The hypothesis: normal traffic in the testing partition is not drawn
from the same distribution as normal traffic in the training partition.
If true, a threshold learned on one does not hold on the other.

This script tests that hypothesis three ways:

  1. Can a classifier tell training normals from testing normals?
     (adversarial validation - if AUC is near 0.5 the two are
     interchangeable; near 1.0 they are trivially distinguishable)
  2. Which individual features have shifted most?
  3. How much of the budget miss disappears if the threshold is
     calibrated on test normals instead? (upper bound on what better
     calibration could achieve)

Usage:
    python shift_analysis.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_auc_score

RANDOM_STATE = 42
BUDGETS = [0.005, 0.01, 0.03]


def load(p):
    d = np.load(p)
    return (d["X"], d["y"]) if "y" in d else (d["X"], None)


def psi(expected, actual, bins=10):
    """Population Stability Index. Standard industry measure of drift.
    < 0.1 stable, 0.1-0.25 moderate shift, > 0.25 significant shift."""
    qs = np.quantile(expected, np.linspace(0, 1, bins + 1))
    qs[0], qs[-1] = -np.inf, np.inf
    e = np.histogram(expected, bins=qs)[0] / len(expected)
    a = np.histogram(actual, bins=qs)[0] / len(actual)
    e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def main():
    Path("reports").mkdir(exist_ok=True)

    X_tr, _ = load("data/processed/train_normal.npz")
    X_val, _ = load("data/processed/val_normal.npz")
    X_test, y_test = load("data/processed/test_full.npz")
    cols = json.load(open("config/feature_order.json"))["output_columns"]

    X_test_norm = X_test[y_test == 0]
    X_train_norm = np.vstack([X_tr, X_val])

    L = ["# Distribution shift analysis", "",
         "Why thresholds calibrated on training-partition normal traffic do "
         "not hold on the testing partition.", ""]

    L += ["## 1. Setup", "",
          f"- Normal rows from the training partition: {len(X_train_norm):,}",
          f"- Normal rows from the testing partition: {len(X_test_norm):,}",
          f"- Features: {X_tr.shape[1]}", ""]

    # ---------- 1. adversarial validation ----------
    X = np.vstack([X_train_norm, X_test_norm])
    origin = np.r_[np.zeros(len(X_train_norm)), np.ones(len(X_test_norm))]

    clf = RandomForestClassifier(
        n_estimators=200, max_depth=8, min_samples_leaf=50,
        random_state=RANDOM_STATE, n_jobs=-1)
    proba = cross_val_predict(clf, X, origin, cv=3,
                              method="predict_proba", n_jobs=-1)[:, 1]
    adv_auc = roc_auc_score(origin, proba)

    L += ["## 2. Can the two sources be told apart?", "",
          "A classifier is trained to predict only which partition a normal "
          "flow came from. If the two sets were interchangeable it would be "
          "unable to do better than chance.", "",
          f"- **Adversarial AUC: {adv_auc:.3f}**", ""]

    if adv_auc < 0.60:
        L.append("The two sets are close to interchangeable. Distribution "
                 "shift does not explain the budget miss; look instead at "
                 "the shape of the score distribution tail.")
    elif adv_auc < 0.80:
        L.append("The two sets are distinguishable but not trivially so. "
                 "Moderate shift is present and plausibly accounts for part "
                 "of the budget miss.")
    else:
        L.append("**The two sets are easily distinguishable.** Normal traffic "
                 "in the testing partition is materially different from "
                 "normal traffic in the training partition. A threshold "
                 "calibrated on one cannot be expected to hold on the other, "
                 "which explains the observed budget miss directly.")
    L.append("")

    # ---------- 2. per-feature shift ----------
    rows = []
    for i, c in enumerate(cols):
        a, b = X_train_norm[:, i], X_test_norm[:, i]
        rows.append({
            "feature": c,
            "psi": psi(a, b),
            "train_mean": a.mean(),
            "test_mean": b.mean(),
            "train_p99": np.quantile(a, 0.99),
            "test_p99": np.quantile(b, 0.99),
        })
    shift = pd.DataFrame(rows).sort_values("psi", ascending=False)
    shift.to_csv("reports/feature_shift.csv", index=False)

    n_sig = int((shift["psi"] > 0.25).sum())
    n_mod = int(((shift["psi"] > 0.10) & (shift["psi"] <= 0.25)).sum())

    L += ["## 3. Which features shifted?", "",
          "Population Stability Index per feature. Below 0.1 is stable, "
          "0.1 to 0.25 is moderate, above 0.25 is significant.", "",
          f"- Features with significant shift: **{n_sig} of {len(cols)}**",
          f"- Features with moderate shift: {n_mod}", "",
          "| Feature | PSI | Train mean | Test mean | Train p99 | Test p99 |",
          "|---|---|---|---|---|---|"]
    for _, r in shift.head(12).iterrows():
        L.append(f"| `{r['feature']}` | {r['psi']:.3f} | {r['train_mean']:.2f} | "
                 f"{r['test_mean']:.2f} | {r['train_p99']:.2f} | {r['test_p99']:.2f} |")
    L.append("")
    L.append("The p99 columns matter most. Thresholds are set from the upper "
             "tail of the normal score distribution, so a feature whose 99th "
             "percentile has moved will push scores across the threshold even "
             "when its average is unchanged.")
    L.append("")

    # ---------- 3. how much is recoverable by better calibration? ----------
    iforest = joblib.load("models/iforest_sanity.joblib")
    s_val = -iforest.score_samples(X_val)
    s_test = -iforest.score_samples(X_test)
    s_test_norm = s_test[y_test == 0]

    L += ["## 4. Upper bound on what better calibration could achieve", "",
          "Thresholds are re-derived from the test-partition normal scores. "
          "This is not a legitimate procedure - it consults data that must "
          "stay sealed - and is computed only to bound how much of the miss "
          "is calibration and how much is irreducible shift.", "",
          "| Budget | FPR, calibrated on validation | FPR, calibrated on test normals |",
          "|---|---|---|"]
    for bud in BUDGETS:
        thr_val = np.quantile(s_val, 1 - bud)
        thr_orc = np.quantile(s_test_norm, 1 - bud)
        fpr_val = float((s_test_norm >= thr_val).mean())
        fpr_orc = float((s_test_norm >= thr_orc).mean())
        L.append(f"| {bud:.1%} | {fpr_val:.2%} | {fpr_orc:.2%} |")
    L.append("")
    L.append("The right-hand column is what a perfectly calibrated threshold "
             "would deliver. The gap between the two columns is the cost of "
             "the shift.")
    L.append("")

    # ---------- 4. figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    ax[0].hist(-iforest.score_samples(X_train_norm), bins=80, density=True,
               alpha=0.6, color="#1F4E79", label="training normals")
    ax[0].hist(s_test_norm, bins=80, density=True,
               alpha=0.6, color="#C55A11", label="testing normals")
    ax[0].axvline(np.quantile(s_val, 0.99), ls="--", color="k", lw=1)
    ax[0].text(np.quantile(s_val, 0.99), ax[0].get_ylim()[1] * 0.9,
               " 1% threshold", fontsize=8, rotation=90, va="top")
    ax[0].set_title("Normal score distributions, both partitions")
    ax[0].set_xlabel("anomaly score")
    ax[0].legend()

    top = shift.head(15).iloc[::-1]
    colours = ["#C55A11" if v > 0.25 else "#E8A33D" if v > 0.10 else "#1F4E79"
               for v in top["psi"]]
    ax[1].barh(top["feature"], top["psi"], color=colours)
    ax[1].axvline(0.10, ls=":", color="grey", lw=1)
    ax[1].axvline(0.25, ls="--", color="grey", lw=1)
    ax[1].set_title("Per-feature distribution shift (PSI)")
    ax[1].set_xlabel("PSI")
    ax[1].tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig("reports/distribution_shift.png", dpi=150)
    plt.close(fig)

    L += ["## 5. Figures", "",
          "- `reports/distribution_shift.png`",
          "- `reports/feature_shift.csv` (all features, full PSI table)", "",
          "## 6. What this means for the project", "",
          "1. The false-positive budget cannot be treated as a promise "
          "derived once from the training partition. It holds only while the "
          "traffic resembles what the threshold was calibrated on.",
          "2. Calibration data must come from the same source as the traffic "
          "being scored. For the Week 9 laboratory work this means the "
          "threshold has to be recalibrated on normal GNS3 traffic, not "
          "carried over from UNSW-NB15.",
          "3. The gap between stated budget and observed false-positive rate "
          "should be reported as a result in its own right. It is a finding "
          "about the limits of the method, not a defect to be hidden.",
          "4. For the machine-learning workstream: consider reporting the "
          "operating point by observed FPR on a held-out set rather than by "
          "the requested budget alone, so the two are never confused."]

    Path("reports/shift_analysis.md").write_text("\n".join(L), encoding="utf-8")

    print(f"  adversarial AUC            {adv_auc:.3f}")
    print(f"  features with PSI > 0.25   {n_sig} of {len(cols)}")
    print(f"  most shifted feature       {shift.iloc[0]['feature']} "
          f"(PSI {shift.iloc[0]['psi']:.3f})")
    print()
    print("Wrote reports/shift_analysis.md, reports/feature_shift.csv,")
    print("      reports/distribution_shift.png")


if __name__ == "__main__":
    main()
