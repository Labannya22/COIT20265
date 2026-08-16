# Isolation Forest sanity check

Untuned baseline run to verify the portable feature set separates the classes before other workstreams build on it. Not a model deliverable; work package 4.0 will supersede this.

## 1. Separation

- Effect size between normal and attack scores: **1.24**
- ROC-AUC: **0.795**
- PR-AUC (average precision): **0.845**
- Base rate of attacks in the test set: 55.1%

The feature set separates the classes despite excluding every TTL and packet-level feature. Work package 4.0 can proceed on this basis.

## 2. False-positive budget calibration

Thresholds are taken from the normal validation scores only. Test labels are not consulted until the threshold is fixed.

| Budget | Threshold | Precision | Recall | F1 | Actual FPR | False alerts per 1,000 normal |
|---|---|---|---|---|---|---|
| 0.5% | 0.6577 | 0.976 | 0.234 | 0.378 | 0.70% | 7.0 |
| 1.0% | 0.6383 | 0.942 | 0.282 | 0.434 | 2.13% | 21.3 |
| 3.0% | 0.5928 | 0.880 | 0.592 | 0.708 | 9.90% | 99.0 |

If the actual FPR column sits close to the budget column, the calibration transfers from validation to test. A large gap would mean the validation split is not representative of unseen normal traffic, which is exactly what deduplicating before the split was meant to prevent.

## 3. Official versus deduplicated test set

Reported at the 1% budget. Both figures are shown because 1,337 normal test rows are identical, on the portable feature set, to normal training rows.

| Test set | Rows | Precision | Recall | F1 | FPR |
|---|---|---|---|---|---|
| Official partition | 82,332 | 0.942 | 0.282 | 0.434 | 2.13% |
| Deduplicated | 80,995 | 0.943 | 0.282 | 0.434 | 2.18% |

A higher FPR on the deduplicated set is the expected direction: removing memorised flows removes easy correct answers. The gap is the size of the optimism in the official figure.

## 4. Figure

- `reports/sanity_check_scores.png`

## 5. Handover note

For the machine-learning workstream: this run is untuned and uses Isolation Forest defaults with 200 estimators. It establishes a floor, not a target. The threshold mechanism above is the one the hybrid score should reuse, since calibrating on normal validation scores is what ties the operating point to a stated false-positive budget rather than to accuracy.