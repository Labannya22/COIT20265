"""
Isolation Forest sanity check
COIT20265 - WBS 3.0 handover artefact - Labannya Barua

This is NOT the model deliverable. Work package 4.0 belongs to the
machine-learning workstream. The purpose here is narrower and comes
before it: to confirm that the portable feature set separates normal
from attack traffic at all, before three other workstreams commit to
building on it.

No tuning. Defaults only. One question: does the score distribution
separate?

It also demonstrates the false-positive-budget mechanism end to end,
so the threshold logic is understood before it is formally built:

    1. fit on normal training rows only
    2. score the normal validation rows
    3. set the threshold at the percentile matching the budget
    4. apply that threshold to the test set, unchanged

Usage:
    python sanity_check.py
"""

from pathlib import Path

import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_recall_fscore_support, roc_auc_score)

RANDOM_STATE = 42
BUDGETS = [0.005, 0.01, 0.03]          # allowed share of normal flows alerted


def load(p):
    d = np.load(p)
    return (d["X"], d["y"]) if "y" in d else (d["X"], None)


def evaluate(scores, y, thr):
    """scores: higher means more anomalous. Positive class is attack."""
    pred = (scores >= thr).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(
        y, pred, average="binary", zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fp_per_1k = fpr * 1000
    return dict(precision=p, recall=r, f1=f1, fpr=fpr,
                fp_per_1k_normal=fp_per_1k, tp=tp, fp=fp, fn=fn, tn=tn)


def main():
    Path("reports").mkdir(exist_ok=True)

    X_tr, _ = load("data/processed/train_normal.npz")
    X_val, _ = load("data/processed/val_normal.npz")
    X_test, y_test = load("data/processed/test_full.npz")
    X_ded, y_ded = load("data/processed/test_dedup.npz")

    print(f"train {X_tr.shape}  val {X_val.shape}  test {X_test.shape}")
    print("fitting Isolation Forest on normal training rows only ...")

    iforest = IsolationForest(
        n_estimators=200,
        max_samples="auto",
        contamination="auto",     # unused: we threshold ourselves
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ).fit(X_tr)

    # score_samples returns higher = more normal. Negate so higher = more anomalous.
    s_val = -iforest.score_samples(X_val)
    s_test = -iforest.score_samples(X_test)
    s_ded = -iforest.score_samples(X_ded)

    L = ["# Isolation Forest sanity check", "",
         "Untuned baseline run to verify the portable feature set separates "
         "the classes before other workstreams build on it. Not a model "
         "deliverable; work package 4.0 will supersede this.", ""]

    # ---------- does it separate at all? ----------
    a, b = s_test[y_test == 0], s_test[y_test == 1]
    pooled = np.sqrt((a.var() + b.var()) / 2)
    effect = abs(a.mean() - b.mean()) / pooled if pooled else 0.0
    roc = roc_auc_score(y_test, s_test)
    pr = average_precision_score(y_test, s_test)

    L += ["## 1. Separation", "",
          f"- Effect size between normal and attack scores: **{effect:.2f}**",
          f"- ROC-AUC: **{roc:.3f}**",
          f"- PR-AUC (average precision): **{pr:.3f}**",
          f"- Base rate of attacks in the test set: {y_test.mean():.1%}", ""]

    if roc < 0.60:
        L.append("**The feature set does not separate the classes.** This is "
                 "the failure Oroian et al. (2024) report for Isolation Forest "
                 "on UNSW-NB15. Raise before work package 4.0 begins.")
    elif roc < 0.75:
        L.append("Separation is weak but present. Usable as a starting point; "
                 "the hybrid design and threshold calibration are doing real "
                 "work rather than decorating an already-solved problem.")
    else:
        L.append("The feature set separates the classes despite excluding "
                 "every TTL and packet-level feature. Work package 4.0 can "
                 "proceed on this basis.")
    L.append("")

    # ---------- false-positive budgets ----------
    L += ["## 2. False-positive budget calibration", "",
          "Thresholds are taken from the normal validation scores only. "
          "Test labels are not consulted until the threshold is fixed.", "",
          "| Budget | Threshold | Precision | Recall | F1 | Actual FPR | "
          "False alerts per 1,000 normal |",
          "|---|---|---|---|---|---|---|"]

    rows = []
    for bud in BUDGETS:
        thr = float(np.quantile(s_val, 1 - bud))
        m = evaluate(s_test, y_test, thr)
        rows.append((bud, thr, m))
        L.append(f"| {bud:.1%} | {thr:.4f} | {m['precision']:.3f} | "
                 f"{m['recall']:.3f} | {m['f1']:.3f} | {m['fpr']:.2%} | "
                 f"{m['fp_per_1k_normal']:.1f} |")
    L.append("")
    L.append("If the actual FPR column sits close to the budget column, the "
             "calibration transfers from validation to test. A large gap "
             "would mean the validation split is not representative of unseen "
             "normal traffic, which is exactly what deduplicating before the "
             "split was meant to prevent.")
    L.append("")

    # ---------- official vs deduplicated test set ----------
    L += ["## 3. Official versus deduplicated test set", "",
          "Reported at the 1% budget. Both figures are shown because "
          "1,337 normal test rows are identical, on the portable feature "
          "set, to normal training rows.", "",
          "| Test set | Rows | Precision | Recall | F1 | FPR |",
          "|---|---|---|---|---|---|"]
    thr_1pct = float(np.quantile(s_val, 0.99))
    for name, s, y in [("Official partition", s_test, y_test),
                       ("Deduplicated", s_ded, y_ded)]:
        m = evaluate(s, y, thr_1pct)
        L.append(f"| {name} | {len(y):,} | {m['precision']:.3f} | "
                 f"{m['recall']:.3f} | {m['f1']:.3f} | {m['fpr']:.2%} |")
    L.append("")
    L.append("A higher FPR on the deduplicated set is the expected direction: "
             "removing memorised flows removes easy correct answers. The gap "
             "is the size of the optimism in the official figure.")
    L.append("")

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    ax[0].hist(a, bins=80, alpha=0.6, density=True, color="#1F4E79", label="normal")
    ax[0].hist(b, bins=80, alpha=0.6, density=True, color="#C55A11", label="attack")
    for bud, thr, _ in rows:
        ax[0].axvline(thr, ls="--", lw=1, color="k")
        ax[0].text(thr, ax[0].get_ylim()[1] * 0.92, f" {bud:.1%}",
                   fontsize=8, rotation=90, va="top")
    ax[0].set_title("Test score distribution with budget thresholds")
    ax[0].set_xlabel("anomaly score (higher = more anomalous)")
    ax[0].legend()

    ax[1].hist(s_val, bins=80, alpha=0.75, density=True, color="#2E7D32")
    ax[1].set_title("Normal validation scores (used to set thresholds)")
    ax[1].set_xlabel("anomaly score")
    fig.tight_layout()
    fig.savefig("reports/sanity_check_scores.png", dpi=150)
    plt.close(fig)

    L += ["## 4. Figure", "", "- `reports/sanity_check_scores.png`", "",
          "## 5. Handover note", "",
          "For the machine-learning workstream: this run is untuned and uses "
          "Isolation Forest defaults with 200 estimators. It establishes a "
          "floor, not a target. The threshold mechanism above is the one the "
          "hybrid score should reuse, since calibrating on normal validation "
          "scores is what ties the operating point to a stated false-positive "
          "budget rather than to accuracy."]

    Path("reports/sanity_check.md").write_text("\n".join(L), encoding="utf-8")
    joblib.dump(iforest, "models/iforest_sanity.joblib")

    print()
    print(f"  ROC-AUC        {roc:.3f}")
    print(f"  PR-AUC         {pr:.3f}")
    print(f"  effect size    {effect:.2f}")
    print()
    for bud, thr, m in rows:
        print(f"  budget {bud:>5.1%}   precision {m['precision']:.3f}   "
              f"recall {m['recall']:.3f}   F1 {m['f1']:.3f}   "
              f"actual FPR {m['fpr']:.2%}")
    print()
    print("Wrote reports/sanity_check.md and reports/sanity_check_scores.png")


if __name__ == "__main__":
    main()
