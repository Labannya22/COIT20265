"""
UNSW-NB15 duplicate and cross-partition leakage audit
COIT20265 - WBS 3.0 - Labannya Barua

The profiling run found 74,072 duplicate rows in the training partition
(42%) and 28,380 in the testing partition (34%).

This script answers the three questions that matter before any pipeline
is built:

  Q1  Are duplicates confined to one class, or do identical feature
      vectors carry conflicting labels?  (label noise)
  Q2  Do rows in the testing partition also appear in the training
      partition?  (cross-partition leakage - R-04)
  Q3  Does the leakage sit specifically in the normal-only rows the
      unsupervised models will train on?  (the case that actually
      inflates our results)

Usage:
    python audit_duplicates.py --data-dir data/raw --out reports
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

DROP = ["id", "attack_cat"]
LABEL = "label"


def feature_key(df: pd.DataFrame) -> pd.Series:
    """A hashable signature of the feature vector, excluding id and labels."""
    cols = [c for c in df.columns if c not in DROP + [LABEL]]
    return pd.util.hash_pandas_object(df[cols], index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw")
    ap.add_argument("--out", default="reports")
    a = ap.parse_args()

    d, out = Path(a.data_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    train = pd.read_csv(d / "UNSW_NB15_training-set.csv", low_memory=False)
    test = pd.read_csv(d / "UNSW_NB15_testing-set.csv", low_memory=False)

    train = train.assign(_key=feature_key(train))
    test = test.assign(_key=feature_key(test))

    L = ["# Duplicate and leakage audit", "",
         "Follow-up to the data-quality report. Observation only.", ""]

    # ---------- Q1: label conflicts within a partition ----------
    L += ["## 1. Do identical feature vectors carry conflicting labels?", ""]
    for name, df in [("Training", train), ("Testing", test)]:
        g = df.groupby("_key")[LABEL].nunique()
        conflicted_keys = g[g > 1].index
        n_keys = len(conflicted_keys)
        n_rows = int(df["_key"].isin(conflicted_keys).sum())
        L.append(f"**{name} partition**")
        L.append("")
        L.append(f"- Distinct feature vectors: {df['_key'].nunique():,}")
        L.append(f"- Vectors appearing more than once: "
                 f"{int((df['_key'].value_counts() > 1).sum()):,}")
        L.append(f"- Vectors carrying BOTH labels: {n_keys:,}")
        L.append(f"- Rows affected by label conflict: {n_rows:,} "
                 f"({n_rows / len(df):.2%})")
        if n_keys:
            L.append("")
            L.append("  These rows are unlearnable: the same flow is labelled "
                     "normal in one record and attack in another. They place a "
                     "ceiling on achievable precision.")
        L.append("")

    # ---------- Q2: cross-partition overlap ----------
    L += ["## 2. Does the testing partition overlap the training partition?", ""]
    tr_keys = set(train["_key"])
    overlap_mask = test["_key"].isin(tr_keys)
    n_overlap = int(overlap_mask.sum())
    L.append(f"- Testing rows whose feature vector also appears in training: "
             f"**{n_overlap:,} of {len(test):,} ({n_overlap / len(test):.2%})**")
    L.append("")
    if n_overlap:
        by_label = test.loc[overlap_mask, LABEL].value_counts()
        L.append("| Test label | Overlapping rows | Share of that class in test |")
        L.append("|---|---|---|")
        for lab in [0, 1]:
            n = int(by_label.get(lab, 0))
            tot = int((test[LABEL] == lab).sum())
            nm = "Normal (0)" if lab == 0 else "Attack (1)"
            L.append(f"| {nm} | {n:,} | {n / tot:.2%} |")
        L.append("")

    # ---------- Q3: leakage into the normal-only training set ----------
    L += ["## 3. Leakage into the normal-only training path", ""]
    L.append("Our models are fitted on normal training rows only, so the "
             "case that inflates results is a normal test row that is "
             "identical to a normal training row.")
    L.append("")
    tr_norm_keys = set(train.loc[train[LABEL] == 0, "_key"])
    test_norm = test[test[LABEL] == 0]
    n_leak = int(test_norm["_key"].isin(tr_norm_keys).sum())
    L.append(f"- Normal test rows identical to a normal training row: "
             f"**{n_leak:,} of {len(test_norm):,} ({n_leak / len(test_norm):.2%})**")
    L.append("")

    tr_att_keys = set(train.loc[train[LABEL] == 1, "_key"])
    test_att = test[test[LABEL] == 1]
    n_att_leak = int(test_att["_key"].isin(tr_att_keys).sum())
    L.append(f"- Attack test rows identical to a training attack row: "
             f"{n_att_leak:,} of {len(test_att):,} ({n_att_leak / len(test_att):.2%})")
    L.append("")
    L.append("Attack overlap does not leak into our training path, because "
             "attack rows are never used for fitting. It is recorded here for "
             "completeness and because it affects how optimistic the benchmark "
             "comparison is in general.")
    L.append("")

    # ---------- duplication concentrated where? ----------
    L += ["## 4. Where the duplication is concentrated", ""]
    vc = train["_key"].value_counts()
    dup_keys = vc[vc > 1].index
    dup_rows = train[train["_key"].isin(dup_keys)]
    L.append("| Attack category | Rows | Duplicated rows | Share duplicated |")
    L.append("|---|---|---|---|")
    for cat in train["attack_cat"].value_counts().index:
        tot = int((train["attack_cat"] == cat).sum())
        dup = int((dup_rows["attack_cat"] == cat).sum())
        L.append(f"| {cat} | {tot:,} | {dup:,} | {dup / tot:.1%} |")
    L.append("")
    L.append(f"- Largest single repeat count: {int(vc.max()):,} identical rows")
    L.append("")

    # ---------- what this means ----------
    L += ["## 5. What this evidence supports", ""]
    if n_leak / max(len(test_norm), 1) > 0.01:
        L.append(f"1. **Cross-partition leakage is present.** {n_leak / len(test_norm):.1%} "
                 "of normal test rows are byte-identical to normal training rows. "
                 "Performance measured on the untouched official test set will be "
                 "optimistic. We will additionally report results on a deduplicated "
                 "test set and present both figures, rather than reporting only the "
                 "favourable one.")
    else:
        L.append("1. Cross-partition leakage in the normal-only path is negligible. "
                 "The official test partition can be used as supplied.")
    L.append("2. Deduplicate the normal training set before fitting. Repeated "
             "identical flows distort the learned normal profile by weighting "
             "some behaviours far above their true frequency, which directly "
             "shifts the score distribution the threshold is calibrated against.")
    L.append("3. Do NOT deduplicate the test set silently. Report both figures "
             "and state which is which.")
    L.append("4. Record the deduplication decision in the feature dictionary so "
             "the same rule is applied to Zeek records in Week 9.")

    (out / "duplicate_audit.md").write_text("\n".join(L), encoding="utf-8")

    print(f"Wrote {out / 'duplicate_audit.md'}")
    print()
    print(f"  Test rows overlapping training:        {n_overlap:,} "
          f"({n_overlap / len(test):.2%})")
    print(f"  Normal test rows leaking from training: {n_leak:,} "
          f"({n_leak / len(test_norm):.2%})   <-- the number that matters")


if __name__ == "__main__":
    main()
