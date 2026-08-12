# Hybrid Unsupervised Network Anomaly Detection

COIT20265 Networks and Information Security Project, HT2 2026.

An explainable, false-positive-aware hybrid anomaly detection system combining
Isolation Forest and a Dense Autoencoder, evaluated on UNSW-NB15 and on
independently generated GNS3/Zeek traffic.

## Status

| Work package | Owner | Status |
|---|---|---|
| 2.0 Research and requirements | Labannya Barua | Complete (Assessment 1) |
| 3.0 Dataset and data engineering | Labannya Barua | Complete to 21 Aug schedule |
| 4.0 Individual model development | Syed Rubaiyat Karim | Unblocked, sample available |
| 5.0 Hybrid scoring and thresholding | Syed Rubaiyat Karim | Blocked on 4.0 |
| 6.0 Explainability and severity | Mst Sinha Naznin | Fixture available |
| 7.0 Virtual network and traffic | Arjita Saha | Draft feature map available |


## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# place UNSW_NB15_training-set.csv and UNSW_NB15_testing-set.csv in data/raw/
python src/profile_unsw.py --data-dir data/raw --out reports
python src/audit_duplicates.py --data-dir data/raw --out reports
python src/build_pipeline.py --data-dir data/raw
python src/sanity_check.py
python src/shift_analysis.py
```

## Repository layout

```
config/     feature_order.json, feature_dictionary.csv
data/       raw/ processed/ lab_samples/     (gitignored)
docs/       handover notes and decisions
models/     preprocessor.joblib               (gitignored)
reports/    generated reports and figures
src/        scripts
```

## Using the pipeline

**Do not refit the preprocessor.** It is fitted on the training split only;
refitting on any other data introduces leakage (R-04).

```python
import joblib, json, numpy as np

pre  = joblib.load("models/preprocessor.joblib")
cfg  = json.load(open("config/feature_order.json"))

train = np.load("data/processed/train_normal.npz")["X"]   # fit models on this
val   = np.load("data/processed/val_normal.npz")["X"]     # calibrate thresholds here
test  = np.load("data/processed/test_full.npz")           # test["X"], test["y"]
dedup = np.load("data/processed/test_dedup.npz")          # report both
```

`cfg["output_columns"]` is the authoritative column order. Any data entering
the models must match it exactly.

## Key findings

Full detail in `docs/HANDOVER_DATA_ENGINEERING.md`. Three results change how the system
must be built:

1. **The portable feature set works.** Excluding every TTL and packet-level
   feature still gives ROC-AUC 0.795 and PR-AUC 0.845 under an untuned
   Isolation Forest.

2. **Thresholds do not transfer between data sources.** A threshold set for a
   1% false-positive budget on validation data produced 2.13% on the test
   partition. Recalibrated on test normals it produces 1.01%. The percentile
   method is sound; the calibration data must match the scoring data.

3. **`sttl` is excluded deliberately.** It is the most separable feature in the
   dataset (effect size 1.94) and unobtainable from conn.log. Reported metrics
   will sit below published UNSW-NB15 results for this reason.

## Data

UNSW-NB15 official partition (Moustafa & Slay 2015). Not committed to the
repository. Download to `data/raw/` before running anything.

## Team

Labannya Barua, Syed Rubaiyat Karim, Arjita Saha, Mst Sinha Naznin.
