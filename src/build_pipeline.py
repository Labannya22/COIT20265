"""
UNSW-NB15 preprocessing pipeline
COIT20265 - WBS 3.0 - Labannya Barua

Produces the Week 5 deliverables:

    models/preprocessor.joblib      fitted transformer (train-only fit)
    config/feature_order.json       exact output column order
    config/feature_dictionary.csv   UNSW -> Zeek conn.log mapping
    data/processed/*.npz            train / validation / test arrays
    data/lab_samples/fixture.csv    small sample for teammates
    reports/pipeline_report.md      what was done and why

Design decisions this script implements, all traceable to the
data-quality report and duplicate audit:

  1. `id` and `attack_cat` are dropped at load. `label` is held
     separately and never enters the transformer.               (R-04)
  2. Normal rows are DEDUPLICATED BEFORE the train/validation split.
     42% of the training partition is duplicated; splitting first
     would place copies of the same flow on both sides, so the model
     would memorise the validation data and the calibrated threshold
     would be too tight.                                          (R-04)
  3. The feature set is restricted to fields obtainable from a Zeek
     conn.log record, either directly, by arithmetic, or by
     recomputing a sliding-window count. TTL-dependent features are
     excluded because conn.log carries no TTL.                    (R-01)
  4. The transformer is fitted on the training split only.
  5. Categorical encoding uses handle_unknown='ignore'. The testing
     partition already contains `state` values ACC and CLO that the
     training partition does not, so this is an observed need.
  6. Heavy-tailed numeric features are log1p transformed before
     scaling; the distributions in the profiling report are strongly
     right-skewed. RobustScaler then handles remaining outliers.

Usage:
    python build_pipeline.py --data-dir data/raw
"""

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, RobustScaler

RANDOM_STATE = 42
VAL_FRACTION = 0.20
RARE_PROTO_MIN = 50

DROP_AT_LOAD = ["id", "attack_cat"]
LABEL = "label"

# ---------------------------------------------------------------------
# Portable feature set.
# Every entry must be obtainable from Zeek conn.log. See
# config/feature_dictionary.csv for the field-by-field mapping.
# ---------------------------------------------------------------------

# Counts and volumes read straight from conn.log, or one division away.
NUMERIC_BASE = [
    "dur", "spkts", "dpkts", "sbytes", "dbytes",
    "rate", "sload", "dload", "smean", "dmean",
]

# Sliding-window connection counts. conn.log does not contain these;
# they must be recomputed from the stream of connection records using
# the same window definition on both benchmark and laboratory data.
NUMERIC_CT = [
    "ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm",
]

# Binary flag, derivable by comparing the connection endpoints.
NUMERIC_BINARY = ["is_sm_ips_ports"]

CATEGORICAL = ["proto", "service", "state"]

NUMERIC = NUMERIC_BASE + NUMERIC_CT + NUMERIC_BINARY
SELECTED = NUMERIC + CATEGORICAL

# Excluded, with the reason recorded for the report and the marker.
EXCLUDED = {
    "sttl": "TTL not present in conn.log",
    "dttl": "TTL not present in conn.log",
    "ct_state_ttl": "derived from TTL, not present in conn.log",
    "swin": "TCP window size requires packet inspection",
    "dwin": "TCP window size requires packet inspection",
    "stcpb": "TCP base sequence number requires packet inspection",
    "dtcpb": "TCP base sequence number requires packet inspection",
    "tcprtt": "TCP handshake timing requires packet inspection",
    "synack": "TCP handshake timing requires packet inspection",
    "ackdat": "TCP handshake timing requires packet inspection",
    "sjit": "inter-packet jitter requires packet inspection",
    "djit": "inter-packet jitter requires packet inspection",
    "sinpkt": "inter-packet arrival time requires packet inspection",
    "dinpkt": "inter-packet arrival time requires packet inspection",
    "sloss": "retransmission counts require packet inspection",
    "dloss": "retransmission counts require packet inspection",
    "trans_depth": "requires http.log, out of MVP scope",
    "response_body_len": "requires http.log, out of MVP scope",
    "ct_flw_http_mthd": "requires http.log, out of MVP scope",
    "is_ftp_login": "requires ftp.log, out of MVP scope",
    "ct_ftp_cmd": "requires ftp.log, out of MVP scope",
}

# UNSW field -> Zeek conn.log source. Written to the feature dictionary.
ZEEK_MAP = {
    "dur": ("Direct", "duration"),
    "spkts": ("Direct", "orig_pkts"),
    "dpkts": ("Direct", "resp_pkts"),
    "sbytes": ("Direct", "orig_ip_bytes (NOT orig_bytes: UNSW includes headers)"),
    "dbytes": ("Direct", "resp_ip_bytes (NOT resp_bytes: UNSW includes headers)"),
    "rate": ("Derived", "(orig_pkts + resp_pkts) / duration"),
    "sload": ("Derived", "orig_ip_bytes * 8 / duration"),
    "dload": ("Derived", "resp_ip_bytes * 8 / duration"),
    "smean": ("Derived", "orig_ip_bytes / orig_pkts"),
    "dmean": ("Derived", "resp_ip_bytes / resp_pkts"),
    "is_sm_ips_ports": ("Derived", "id.orig_h == id.resp_h AND id.orig_p == id.resp_p"),
    "ct_srv_src": ("Recomputed", "count over last 100 conns sharing service + id.orig_h"),
    "ct_srv_dst": ("Recomputed", "count over last 100 conns sharing service + id.resp_h"),
    "ct_dst_ltm": ("Recomputed", "count over last 100 conns sharing id.resp_h"),
    "ct_src_ltm": ("Recomputed", "count over last 100 conns sharing id.orig_h"),
    "ct_src_dport_ltm": ("Recomputed", "count over last 100 conns sharing id.orig_h + id.resp_p"),
    "ct_dst_sport_ltm": ("Recomputed", "count over last 100 conns sharing id.resp_h + id.orig_p"),
    "ct_dst_src_ltm": ("Recomputed", "count over last 100 conns sharing id.orig_h + id.resp_h"),
    "proto": ("Direct", "proto"),
    "service": ("Direct", "service ('-' in UNSW maps to empty field in Zeek)"),
    "state": ("Lossy", "conn_state; different vocabulary, needs documented lookup"),
}


def feature_key(df: pd.DataFrame, cols) -> pd.Series:
    return pd.util.hash_pandas_object(df[cols], index=False)


def group_rare_proto(s: pd.Series, keep) -> pd.Series:
    return s.where(s.isin(keep), "other")


def build_transformer():
    """log1p then RobustScaler for skewed numerics; one-hot for categoricals.

    is_sm_ips_ports is already binary, so it is scaled but not logged.
    """
    skewed = NUMERIC_BASE + NUMERIC_CT
    log_then_scale = Pipeline([
        ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ("scale", RobustScaler()),
    ])
    return ColumnTransformer(
        transformers=[
            ("num_skewed", log_then_scale, skewed),
            ("num_binary", RobustScaler(), NUMERIC_BINARY),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Guard against division artefacts. The official partition contains no
    infinities, but the Zeek path will compute rate/sload/dload itself and
    zero-duration flows do occur (1.5% of rows), so the guard is kept here
    to ensure both paths behave identically."""
    out = df.copy()
    for c in NUMERIC:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    out[NUMERIC] = out[NUMERIC].replace([np.inf, -np.inf], np.nan)
    out[NUMERIC] = out[NUMERIC].fillna(0.0)
    out[NUMERIC] = out[NUMERIC].clip(lower=0.0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw")
    a = ap.parse_args()
    raw = Path(a.data_dir)

    for p in ["data/processed", "data/lab_samples", "models", "config", "reports"]:
        Path(p).mkdir(parents=True, exist_ok=True)

    L = ["# Preprocessing pipeline report", "",
         "Generated by `build_pipeline.py`.", ""]

    # ---------- load ----------
    train_raw = pd.read_csv(raw / "UNSW_NB15_training-set.csv", low_memory=False)
    test_raw = pd.read_csv(raw / "UNSW_NB15_testing-set.csv", low_memory=False)

    y_train_all = train_raw[LABEL].to_numpy()
    y_test = test_raw[LABEL].to_numpy()
    train_raw = train_raw.drop(columns=DROP_AT_LOAD, errors="ignore")
    test_raw = test_raw.drop(columns=DROP_AT_LOAD, errors="ignore")

    L += ["## 1. Feature selection", "",
          f"- Columns in source partition: {train_raw.shape[1] - 1} features plus label",
          f"- Retained as portable: {len(SELECTED)} "
          f"({len(NUMERIC)} numeric, {len(CATEGORICAL)} categorical)",
          f"- Excluded: {len(EXCLUDED)}", "",
          "Excluded features and reasons are listed in "
          "`config/feature_dictionary.csv`. The exclusions are driven by "
          "Zeek portability, not by predictive weakness: `sttl` is the "
          "single most separable feature in the dataset (effect size 1.94) "
          "and is excluded because conn.log carries no TTL field.", ""]

    # ---------- deduplicate normal rows, then split ----------
    train_norm = train_raw[y_train_all == 0][SELECTED].copy()
    n_before = len(train_norm)
    train_norm = train_norm.drop_duplicates().reset_index(drop=True)
    n_after = len(train_norm)

    rng = np.random.default_rng(RANDOM_STATE)
    perm = rng.permutation(n_after)
    n_val = int(round(n_after * VAL_FRACTION))
    val_idx, tr_idx = perm[:n_val], perm[n_val:]
    df_tr = train_norm.iloc[tr_idx].reset_index(drop=True)
    df_val = train_norm.iloc[val_idx].reset_index(drop=True)

    L += ["## 2. Deduplication and splitting", "",
          f"- Normal rows in training partition: {n_before:,}",
          f"- After deduplication on the selected features: {n_after:,} "
          f"({1 - n_after / n_before:.1%} removed)",
          f"- Training split: {len(df_tr):,} rows",
          f"- Validation split: {len(df_val):,} rows", "",
          "Deduplication is applied **before** the split. The duplicate "
          "audit found 42% of the training partition repeated; splitting "
          "first would place copies of the same flow in both training and "
          "validation, so the model would be scored on flows it had "
          "memorised and the calibrated threshold would sit too low. Real "
          "traffic would then exceed the stated false-positive budget.", ""]

    # ---------- rare proto grouping ----------
    proto_counts = df_tr["proto"].value_counts()
    keep_proto = set(proto_counts[proto_counts >= RARE_PROTO_MIN].index)
    for d in (df_tr, df_val):
        d["proto"] = group_rare_proto(d["proto"], keep_proto)

    L += ["## 3. Categorical handling", "",
          f"- `proto` values retained: {len(keep_proto)} of {len(proto_counts)}; "
          f"the remainder are grouped as `other` (fewer than {RARE_PROTO_MIN} "
          "occurrences each in the training split)",
          "- `service` value `-` is kept as an explicit category meaning "
          "'not identified', not treated as missing",
          "- `state` is one-hot encoded with `handle_unknown='ignore'`; "
          "the testing partition contains ACC and CLO, which the training "
          "partition does not", ""]

    # ---------- fit on training split only ----------
    pre = build_transformer()
    X_tr = pre.fit_transform(clean(df_tr))
    X_val = pre.transform(clean(df_val))
    out_cols = list(pre.get_feature_names_out())

    # ---------- test sets ----------
    df_test = test_raw[SELECTED].copy()
    df_test["proto"] = group_rare_proto(df_test["proto"], keep_proto)
    X_test = pre.transform(clean(df_test))

    # deduplicated test variant: drop test normals identical to a training normal
    key_tr_norm = set(feature_key(train_raw[y_train_all == 0], SELECTED))
    key_test = feature_key(test_raw, SELECTED)
    leak_mask = (y_test == 0) & key_test.isin(key_tr_norm).to_numpy()
    keep_mask = ~leak_mask
    X_test_dedup, y_test_dedup = X_test[keep_mask], y_test[keep_mask]

    L += ["## 4. Test sets", "",
          f"- Official testing partition: {len(y_test):,} rows "
          f"({int((y_test == 0).sum()):,} normal, {int((y_test == 1).sum()):,} attack)",
          f"- Normal test rows identical to a normal training row: "
          f"{int(leak_mask.sum()):,} ({leak_mask.sum() / (y_test == 0).sum():.2%} of test normals)",
          f"- Deduplicated variant: {len(y_test_dedup):,} rows", "",
          "Both variants are saved. All results must be reported against "
          "both and clearly labelled. The official partition is not "
          "silently modified.", ""]

    # ---------- save ----------
    np.savez_compressed("data/processed/train_normal.npz", X=X_tr)
    np.savez_compressed("data/processed/val_normal.npz", X=X_val)
    np.savez_compressed("data/processed/test_full.npz", X=X_test, y=y_test)
    np.savez_compressed("data/processed/test_dedup.npz", X=X_test_dedup, y=y_test_dedup)

    joblib.dump(pre, "models/preprocessor.joblib")

    Path("config/feature_order.json").write_text(json.dumps({
        "n_features_out": len(out_cols),
        "output_columns": out_cols,
        "input_numeric": NUMERIC,
        "input_categorical": CATEGORICAL,
        "proto_categories_kept": sorted(keep_proto),
        "rare_proto_label": "other",
        "random_state": RANDOM_STATE,
        "val_fraction": VAL_FRACTION,
    }, indent=2), encoding="utf-8")

    rows = []
    for f in SELECTED:
        kind, src = ZEEK_MAP[f]
        rows.append({"unsw_feature": f, "status": kind, "zeek_source": src,
                     "in_portable_set": "yes"})
    for f, why in EXCLUDED.items():
        rows.append({"unsw_feature": f, "status": "Not available",
                     "zeek_source": why, "in_portable_set": "no"})
    pd.DataFrame(rows).to_csv("config/feature_dictionary.csv", index=False)

    fixture = pd.DataFrame(X_tr[:500], columns=out_cols)
    fixture.to_csv("data/lab_samples/fixture.csv", index=False)

    L += ["## 5. Artefacts written", "",
          f"- `models/preprocessor.joblib` (fitted on the training split only)",
          f"- `config/feature_order.json` ({len(out_cols)} output columns)",
          f"- `config/feature_dictionary.csv` (UNSW to Zeek mapping)",
          f"- `data/processed/train_normal.npz` ({X_tr.shape})",
          f"- `data/processed/val_normal.npz` ({X_val.shape})",
          f"- `data/processed/test_full.npz` ({X_test.shape})",
          f"- `data/processed/test_dedup.npz` ({X_test_dedup.shape})",
          f"- `data/lab_samples/fixture.csv` (500 rows, correct schema)", "",
          "## 6. Notes for the team", "",
          "- **Rubaiyat**: load the `.npz` files directly. Do not refit the "
          "transformer. `feature_order.json` records the exact column order "
          "the models expect.",
          "- **Arjita**: `config/feature_dictionary.csv` lists every field "
          "your Zeek configuration must produce. Note that conn.log carries "
          "no TTL, so no TTL-based feature is obtainable from the default "
          "log; raise it now if the team wants one.",
          "- **Sinha**: `data/lab_samples/fixture.csv` has the correct shape "
          "and column names for dashboard development before integration.",
          "- The seven `ct_*` features are recomputed, not read. The Week 9 "
          "ingestion code must use the identical window definition, or the "
          "same column will mean different things on the two data sources."]

    Path("reports/pipeline_report.md").write_text("\n".join(L), encoding="utf-8")

    print(f"Train      {X_tr.shape}")
    print(f"Validation {X_val.shape}")
    print(f"Test full  {X_test.shape}   dedup {X_test_dedup.shape}")
    print(f"Output columns: {len(out_cols)}")
    print()
    print("Wrote models/preprocessor.joblib, config/feature_order.json,")
    print("      config/feature_dictionary.csv, reports/pipeline_report.md")


if __name__ == "__main__":
    main()
