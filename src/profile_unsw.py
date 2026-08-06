"""
UNSW-NB15 data profiling
COIT20265 - WBS 3.0 - Labannya Barua

Produces the evidence for the Week 5 data-quality report.
Reads nothing but the raw CSVs. Writes nothing but a report and figures.
No cleaning, no modelling - this script only observes.

Usage:
    python profile_unsw.py --data-dir data/raw --out reports
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Columns that must never reach a model.
# id      : row index; correlates with class ordering in the official partition
# attack_cat : the label in text form
LEAKAGE_COLS = ["id", "attack_cat"]
LABEL_COL = "label"

# Features known to be unavailable from Zeek conn.log.
# Listed here only so the report can quantify what portability will cost.
NOT_IN_CONN_LOG = [
    "sttl", "dttl", "swin", "dwin", "stcpb", "dtcpb",
    "tcprtt", "synack", "ackdat", "sjit", "djit",
    "sinpkt", "dinpkt", "sloss", "dloss",
]


def load(data_dir: Path):
    train = pd.read_csv(data_dir / "UNSW_NB15_training-set.csv", low_memory=False)
    test = pd.read_csv(data_dir / "UNSW_NB15_testing-set.csv", low_memory=False)
    return train, test


def section(title, lines):
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")


def profile_shape(train, test, lines):
    section("1. Shape and class balance", lines)
    lines.append(f"- Training partition: {train.shape[0]:,} rows x {train.shape[1]} columns")
    lines.append(f"- Testing partition:  {test.shape[0]:,} rows x {test.shape[1]} columns")
    lines.append(f"- Columns identical across partitions: {list(train.columns) == list(test.columns)}")
    lines.append("")
    lines.append("| Partition | Normal (0) | Attack (1) | Normal share |")
    lines.append("|---|---|---|---|")
    for name, df in [("Training", train), ("Testing", test)]:
        n0 = int((df[LABEL_COL] == 0).sum())
        n1 = int((df[LABEL_COL] == 1).sum())
        lines.append(f"| {name} | {n0:,} | {n1:,} | {n0 / len(df):.1%} |")
    lines.append("")
    lines.append("Attack categories in the training partition:")
    lines.append("")
    lines.append("| Category | Count | Share |")
    lines.append("|---|---|---|")
    vc = train["attack_cat"].value_counts()
    for cat, n in vc.items():
        lines.append(f"| {cat} | {n:,} | {n / len(train):.2%} |")


def profile_missing(train, test, lines):
    section("2. Missing and duplicate records", lines)
    for name, df in [("Training", train), ("Testing", test)]:
        nulls = df.isna().sum()
        nulls = nulls[nulls > 0]
        dupes = df.duplicated().sum()
        dupes_nolabel = df.drop(columns=LEAKAGE_COLS, errors="ignore").duplicated().sum()
        lines.append(f"**{name} partition**")
        lines.append("")
        if nulls.empty:
            lines.append("- No null values in any column.")
        else:
            lines.append("- Columns containing nulls:")
            for c, n in nulls.items():
                lines.append(f"  - `{c}`: {n:,} ({n / len(df):.2%})")
        lines.append(f"- Exact duplicate rows: {dupes:,}")
        lines.append(f"- Duplicate rows ignoring id/attack_cat: {dupes_nolabel:,}")
        lines.append("")


def profile_infinities(train, test, lines):
    """rate, sload and dload divide by dur. When dur is 0 they blow up.
    An unhandled inf silently destroys a scaler, so this must be quantified."""
    section("3. Infinite and extreme values", lines)
    lines.append("`rate`, `sload` and `dload` are derived by dividing by `dur`.")
    lines.append("Where `dur` is zero these become infinite or undefined.")
    lines.append("")
    lines.append("| Partition | Column | Infinite | NaN | Max finite |")
    lines.append("|---|---|---|---|---|")
    for name, df in [("Training", train), ("Testing", test)]:
        num = df.select_dtypes(include=[np.number])
        for c in num.columns:
            v = num[c]
            n_inf = int(np.isinf(v).sum())
            n_nan = int(v.isna().sum())
            if n_inf or n_nan:
                finite = v[np.isfinite(v)]
                mx = f"{finite.max():,.2f}" if len(finite) else "n/a"
                lines.append(f"| {name} | `{c}` | {n_inf:,} | {n_nan:,} | {mx} |")
    lines.append("")
    for name, df in [("Training", train), ("Testing", test)]:
        if "dur" in df.columns:
            z = int((df["dur"] == 0).sum())
            lines.append(f"- {name}: rows with `dur` exactly 0: {z:,} ({z / len(df):.2%})")


def profile_dtypes(train, lines):
    """ct_ftp_cmd is frequently read as object with blank strings.
    is_ftp_login is documented as binary but contains values above 1."""
    section("4. Data type and encoding problems", lines)
    obj_cols = [c for c in train.columns if not pd.api.types.is_numeric_dtype(train[c])]
    lines.append(f"Object-typed columns: {', '.join(f'`{c}`' for c in obj_cols)}")
    lines.append("")
    for c in ["ct_ftp_cmd", "is_ftp_login", "is_sm_ips_ports"]:
        if c not in train.columns:
            continue
        s = train[c]
        lines.append(f"**`{c}`** (dtype `{s.dtype}`)")
        uniq = s.unique()
        shown = [str(u) for u in uniq[:8]]
        more = " ..." if len(uniq) > 8 else ""
        lines.append(f"- {len(uniq)} distinct values; first few: {shown}{more}")
        coerced = pd.to_numeric(s, errors="coerce")
        bad = int(coerced.isna().sum() - s.isna().sum())
        if bad > 0:
            lines.append(f"- {bad:,} values cannot be coerced to numeric (blank or non-numeric strings)")
        if c in ("is_ftp_login", "is_sm_ips_ports"):
            over = int((coerced > 1).sum())
            if over:
                lines.append(f"- {over:,} values exceed 1 despite being documented as a binary flag")
        lines.append("")


def profile_categoricals(train, test, lines):
    """High cardinality in proto matters: one-hot encoding it naively
    creates ~130 sparse columns. Categories present in test but not
    train are the reason handle_unknown='ignore' is needed."""
    section("5. Categorical features", lines)
    for c in ["proto", "service", "state"]:
        if c not in train.columns:
            continue
        tr, te = set(train[c].unique()), set(test[c].unique())
        lines.append(f"**`{c}`**")
        lines.append(f"- Distinct values in training: {len(tr)}")
        lines.append(f"- Present in test but absent from training: {sorted(te - tr)}")
        vc = train[c].value_counts()
        rare = int((vc < 50).sum())
        lines.append(f"- Values appearing fewer than 50 times: {rare} of {len(vc)}")
        top = ", ".join(f"`{k}` ({v:,})" for k, v in vc.head(6).items())
        lines.append(f"- Most frequent: {top}")
        if c == "service":
            n_dash = int((train[c] == "-").sum())
            lines.append(f"- `-` used for unknown service: {n_dash:,} rows ({n_dash / len(train):.1%})")
        lines.append("")


def profile_separability(train, lines):
    """Ranks features by how far apart the normal and attack distributions sit.
    Not a modelling step - this is evidence for the feature-portability argument."""
    section("6. Univariate separability and the portability cost", lines)
    num = train.select_dtypes(include=[np.number]).drop(
        columns=[LABEL_COL] + [c for c in LEAKAGE_COLS if c in train.columns],
        errors="ignore")
    y = train[LABEL_COL]
    rows = []
    for c in num.columns:
        v = num[c].replace([np.inf, -np.inf], np.nan)
        a, b = v[y == 0].dropna(), v[y == 1].dropna()
        if len(a) < 10 or len(b) < 10:
            continue
        pooled = np.sqrt((a.var() + b.var()) / 2)
        if pooled == 0 or np.isnan(pooled):
            continue
        rows.append((c, abs(a.mean() - b.mean()) / pooled))
    sep = pd.DataFrame(rows, columns=["feature", "effect_size"]).sort_values(
        "effect_size", ascending=False)

    lines.append("Standardised mean difference between normal and attack flows.")
    lines.append("Larger values indicate the feature separates the classes more strongly.")
    lines.append("")
    lines.append("| Rank | Feature | Effect size | Available from conn.log? |")
    lines.append("|---|---|---|---|")
    for i, (_, r) in enumerate(sep.head(20).iterrows(), 1):
        avail = "No" if r["feature"] in NOT_IN_CONN_LOG else "Yes or derivable"
        lines.append(f"| {i} | `{r['feature']}` | {r['effect_size']:.2f} | {avail} |")

    top10 = set(sep.head(10)["feature"])
    lost = sorted(top10 & set(NOT_IN_CONN_LOG))
    lines.append("")
    lines.append(f"**Of the ten most separable features, {len(lost)} cannot be obtained "
                 f"from a Zeek conn.log record: {', '.join(f'`{c}`' for c in lost) or 'none'}.**")
    lines.append("")
    lines.append("This quantifies the cost of cross-source portability and is the evidence "
                 "for reporting benchmark and laboratory results against a single reduced "
                 "feature set rather than against all 42 features.")
    return sep


def plot_separability(sep, out: Path):
    top = sep.head(20).iloc[::-1]
    colors = ["#C55A11" if f in NOT_IN_CONN_LOG else "#1F4E79" for f in top["feature"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["feature"], top["effect_size"], color=colors)
    ax.set_xlabel("Standardised mean difference (normal vs attack)")
    ax.set_title("Feature separability and Zeek availability")
    handles = [plt.Rectangle((0, 0), 1, 1, color="#1F4E79"),
               plt.Rectangle((0, 0), 1, 1, color="#C55A11")]
    ax.legend(handles, ["Available or derivable from conn.log", "Not in conn.log"],
              loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "feature_separability.png", dpi=150)
    plt.close(fig)


def plot_distributions(train, out: Path):
    cols = [c for c in ["dur", "sbytes", "dbytes", "spkts", "dpkts", "rate"]
            if c in train.columns]
    y = train[LABEL_COL]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, c in zip(axes.ravel(), cols):
        v = train[c].replace([np.inf, -np.inf], np.nan)
        for lab, colour, name in [(0, "#1F4E79", "normal"), (1, "#C55A11", "attack")]:
            d = v[y == lab].dropna()
            d = np.log1p(d[d >= 0])
            ax.hist(d, bins=60, alpha=0.55, color=colour, label=name, density=True)
        ax.set_title(f"{c} (log1p)")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "core_feature_distributions.png", dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw")
    ap.add_argument("--out", default="reports")
    a = ap.parse_args()

    data_dir, out = Path(a.data_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    train, test = load(data_dir)

    lines = ["# UNSW-NB15 data-quality report",
             "",
             "Generated by `profile_unsw.py`. Observation only: no cleaning applied.",
             f"Source: official partition, `{data_dir}`."]

    profile_shape(train, test, lines)
    profile_missing(train, test, lines)
    profile_infinities(train, test, lines)
    profile_dtypes(train, lines)
    profile_categoricals(train, test, lines)
    sep = profile_separability(train, lines)

    plot_separability(sep, out)
    plot_distributions(train, out)

    section("7. Figures", lines)
    lines.append("- `feature_separability.png`")
    lines.append("- `core_feature_distributions.png`")

    section("8. Decisions this evidence supports", lines)
    lines.append("1. Drop `id` and `attack_cat` at load time; hold `label` separately. (R-04)")
    lines.append("2. Replace infinities arising from zero-duration flows before scaling.")
    lines.append("3. Coerce `ct_ftp_cmd` to numeric and treat blanks explicitly.")
    lines.append("4. Use `RobustScaler`; the distributions above are heavily skewed.")
    lines.append("5. One-hot encode with `handle_unknown='ignore'`; Zeek will emit unseen categories.")
    lines.append("6. Restrict the portable feature set to conn.log-derivable fields, and report "
                 "the separability cost of doing so rather than concealing it. (R-01)")

    (out / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    sep.to_csv(out / "feature_separability.csv", index=False)

    print(f"Wrote {out / 'data_quality_report.md'}")
    print(f"Wrote {out / 'feature_separability.csv'}")
    print(f"Wrote 2 figures to {out}")


if __name__ == "__main__":
    main()
