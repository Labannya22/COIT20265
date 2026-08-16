# Distribution shift analysis

Why thresholds calibrated on training-partition normal traffic do not hold on the testing partition.

## 1. Setup

- Normal rows from the training partition: 51,331
- Normal rows from the testing partition: 37,000
- Features: 41

## 2. Can the two sources be told apart?

A classifier is trained to predict only which partition a normal flow came from. If the two sets were interchangeable it would be unable to do better than chance.

- **Adversarial AUC: 0.641**

The two sets are distinguishable but not trivially so. Moderate shift is present and plausibly accounts for part of the budget miss.

## 3. Which features shifted?

Population Stability Index per feature. Below 0.1 is stable, 0.1 to 0.25 is moderate, above 0.25 is significant.

- Features with significant shift: **6 of 41**
- Features with moderate shift: 4

| Feature | PSI | Train mean | Test mean | Train p99 | Test p99 |
|---|---|---|---|---|---|
| `dload` | 0.394 | -0.28 | -0.77 | 0.63 | 0.62 |
| `dmean` | 0.347 | 0.14 | -0.29 | 1.34 | 1.33 |
| `dbytes` | 0.331 | -0.03 | -0.41 | 1.79 | 1.59 |
| `dpkts` | 0.329 | -0.03 | -0.27 | 1.82 | 1.56 |
| `spkts` | 0.300 | 0.02 | -0.12 | 1.39 | 1.20 |
| `rate` | 0.285 | -0.22 | -0.35 | 1.18 | 1.34 |
| `sbytes` | 0.231 | -0.07 | -0.25 | 1.68 | 1.98 |
| `sload` | 0.207 | -0.21 | -0.36 | 1.86 | 1.93 |
| `dur` | 0.202 | 0.54 | 0.68 | 5.49 | 5.45 |
| `smean` | 0.176 | 0.37 | 0.37 | 3.34 | 3.51 |
| `ct_dst_ltm` | 0.087 | -0.08 | -0.23 | 2.59 | 3.15 |
| `ct_src_ltm` | 0.080 | 0.09 | -0.03 | 2.25 | 2.46 |

The p99 columns matter most. Thresholds are set from the upper tail of the normal score distribution, so a feature whose 99th percentile has moved will push scores across the threshold even when its average is unchanged.

## 4. Upper bound on what better calibration could achieve

Thresholds are re-derived from the test-partition normal scores. This is not a legitimate procedure - it consults data that must stay sealed - and is computed only to bound how much of the miss is calibration and how much is irreducible shift.

| Budget | FPR, calibrated on validation | FPR, calibrated on test normals |
|---|---|---|
| 0.5% | 0.70% | 0.50% |
| 1.0% | 2.13% | 1.01% |
| 3.0% | 9.90% | 3.01% |

The right-hand column is what a perfectly calibrated threshold would deliver. The gap between the two columns is the cost of the shift.

## 5. Figures

- `reports/distribution_shift.png`
- `reports/feature_shift.csv` (all features, full PSI table)

## 6. What this means for the project

1. The false-positive budget cannot be treated as a promise derived once from the training partition. It holds only while the traffic resembles what the threshold was calibrated on.
2. Calibration data must come from the same source as the traffic being scored. For the Week 9 laboratory work this means the threshold has to be recalibrated on normal GNS3 traffic, not carried over from UNSW-NB15.
3. The gap between stated budget and observed false-positive rate should be reported as a result in its own right. It is a finding about the limits of the method, not a defect to be hidden.
4. For the machine-learning workstream: consider reporting the operating point by observed FPR on a held-out set rather than by the requested budget alone, so the two are never confused.