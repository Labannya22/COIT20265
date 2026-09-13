# Model Testing and Evaluation

This folder documents the final testing and evaluation of the anomaly-detection system across three different network environments.

The objective of the testing stage was to determine how well models trained using normal UNSW-NB15 traffic performed on:

1. the held-out UNSW-NB15 benchmark test set;
2. the NF-CSE-CIC-IDS2018-v2 cross-dataset sample; and
3. independently generated GNS3/Zeek practical network traffic.

All cross-dataset and practical evaluations used the same saved preprocessing pipeline, trained models and validation-derived thresholds. No models were retrained using NF-CSE-CIC-IDS2018-v2 or GNS3/Zeek test data.

## Detection Approaches

Six anomaly-detection approaches were evaluated:

| Model | Type |
|---|---|
| Isolation Forest | Unsupervised anomaly detection |
| Dense Autoencoder | Reconstruction-based anomaly detection |
| Hybrid IF+AE | Score-level fusion of Isolation Forest and Autoencoder |
| Local Outlier Factor | Density-based anomaly detection |
| One-Class SVM | Boundary-based anomaly detection |
| Deep SVDD | Deep one-class representation learning |

The Hybrid IF+AE model was not trained as a separate model. It combines the normalised anomaly scores produced by Isolation Forest and the Autoencoder.

The final hybrid score was calculated as:

```text
Hybrid Score =
0.5 × Normalised IF Score
+
0.5 × Normalised AE Score
```

---

## Training and Threshold Calibration

UNSW-NB15 was the only dataset used for model development.

The testing design followed this structure:

```text
UNSW-NB15 Normal Training Data
        |
        v
Train Models
        |
        v
UNSW-NB15 Normal Validation Data
        |
        v
Calibrate Thresholds
0.5%, 1%, 3% false-positive budgets
        |
        v
Freeze Models + Thresholds
        |
        +--------------------+
        |                    |
        v                    v
UNSW-NB15 Test         NF-CSE-CIC-IDS2018-v2
                             |
                             v
                       GNS3/Zeek Traffic
```

The **1% validation false-positive budget** was used as the main operating point for final comparison.

A 1% threshold budget means that the threshold was selected to produce approximately 1% false positives on the normal UNSW-NB15 validation set.

It does **not** mean that the false-positive rate must remain at 1% when the same threshold is transferred to a different test distribution.

---

# 1. UNSW-NB15 Benchmark Testing

The final UNSW-NB15 evaluation contained:

```text
Total records : 82,332
Normal        : 37,000
Attack        : 45,332
Features      : 41
Missing values: 0
Infinite values: 0
```

All six detection approaches were evaluated using the same held-out test set.

## Results at the 1% Operating Point

| Model | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Dense Autoencoder | 0.9364 | 0.6327 | **0.7552** | 5.27% | 0.8785 | 0.9011 |
| Hybrid IF+AE | **0.9440** | 0.6259 | 0.7527 | 4.55% | 0.8767 | **0.9057** |
| Isolation Forest | 0.9401 | 0.6171 | 0.7451 | 4.82% | 0.8510 | 0.8974 |
| Deep SVDD | 0.9274 | 0.5945 | 0.7246 | 5.70% | 0.8871 | 0.8955 |
| LOF | 0.9364 | 0.5227 | 0.6709 | **4.35%** | **0.8975** | 0.8887 |
| One-Class SVM | 0.8939 | 0.3396 | 0.4922 | 4.94% | 0.7943 | 0.8375 |

## Interpretation

No single model was best across every metric.

The Dense Autoencoder produced the highest Recall and F1 score, while the Hybrid IF+AE achieved the highest Precision and PR-AUC with a lower false-positive rate than the Autoencoder.

LOF produced the lowest FPR and highest ROC-AUC, although its lower Recall shows that more attacks were missed.

One-Class SVM produced the weakest overall benchmark result because of its comparatively low Recall.

The Hybrid IF+AE therefore represents a useful operational compromise rather than a universally superior model.

---

# 2. NF-CSE-CIC-IDS2018-v2 Cross-Dataset Testing

NF-CSE-CIC-IDS2018-v2 was used to test whether the UNSW-trained models and thresholds could transfer to a different public network environment.

The original dataset contains approximately 18.9 million flows.

A controlled sample of **700,000 records** was used:

```text
Normal records : 400,000
Attack records : 300,000
Total          : 700,000
```

The NF-CSE data was converted into the same portable representation and then passed through the saved UNSW-NB15 preprocessor.

```text
NF-CSE Raw Data
        |
        v
Portable Feature Mapping
        |
        v
21 Portable Features
        |
        v
Saved UNSW Preprocessor
        |
        v
41 Model Features
        |
        v
Frozen Models + Frozen Thresholds
```

No model retraining or threshold recalibration was performed using labelled NF-CSE test data.

## Results at the 1% UNSW-Calibrated Operating Point

| Model | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| LOF | 0.4446 | 0.9958 | **0.6147** | 93.30% | 0.5685 | 0.4353 |
| Isolation Forest | 0.4440 | 0.9973 | 0.6144 | 93.67% | 0.4640 | 0.3792 |
| Dense Autoencoder | 0.4286 | 1.0000 | 0.6000 | 100% | 0.1256 | 0.2966 |
| Hybrid IF+AE | 0.4286 | 1.0000 | 0.6000 | 100% | 0.2860 | 0.3186 |
| One-Class SVM | 0.4286 | 1.0000 | 0.6000 | 100% | **0.8890** | **0.9131** |
| Deep SVDD | 0.4286 | 1.0000 | 0.6000 | 100% | 0.8427 | 0.7390 |

## Interpretation

The very high Recall values do **not** indicate successful cross-dataset deployment.

Most normal NF-CSE flows were also classified as anomalous.

For example, four models produced an FPR of 100%, meaning that every normal record was classified as an anomaly at the transferred UNSW threshold.

This demonstrates significant score-distribution and threshold-transfer shift between UNSW-NB15 and NF-CSE-CIC-IDS2018-v2.

An important observation is that One-Class SVM achieved:

```text
ROC-AUC = 0.8890
PR-AUC  = 0.9131
```

while still producing:

```text
FPR = 100%
```

This shows the difference between:

```text
Ranking ability
        vs
Fixed-threshold calibration
```

A model may still rank attacks above normal traffic reasonably well while the threshold transferred from another dataset is unsuitable.

For this reason, the reported NF-CSE experiment preserves the original UNSW thresholds rather than recalibrating them using labelled NF-CSE test data.

---

# 3. GNS3/Zeek Practical Testing

The GNS3/Zeek dataset was created independently from the public benchmark datasets.

It combines traffic generated inside the GNS3 laboratory with traffic originating from a separate physical laptop.

## Practical Dataset Composition

```text
Internal GNS3 records : 1,416
External laptop       : 1,631
--------------------------------
Total                 : 3,047
```

The final scenario distribution was:

| Scenario | Records |
|---|---:|
| Nmap scan | 2,006 |
| DNS burst | 600 |
| HTTP burst | 401 |
| SSH failed login | 20 |
| Normal | 16 |
| Bulk transfer | 3 |
| ICMP burst | 1 |
| **Total** | **3,047** |

The dataset therefore contains:

```text
Attack records : 3,031
Normal records : 16
```

---

## Practical Feature Conversion

Raw Zeek records were not passed directly to the models.

The final processing pipeline was:

```text
Zeek Connection Data
        |
        v
13 Raw Zeek Fields
        |
        v
21 Portable Network Features
        |
        v
Saved UNSW Preprocessor
        |
        v
41 Model-Ready Features
```

The final checks produced:

```text
21-feature dataset shape : (3047, 21)
Missing values           : 0

Final model feature shape: (3047, 41)
```

This confirmed that all practical traffic could be processed by the frozen UNSW-trained models.

---

## GNS3/Zeek Results at the 1% Operating Point

| Model | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| LOF | 0.9967 | **0.9987** | **0.9977** | 62.50% | 0.8141 | 0.9956 |
| Hybrid IF+AE | 0.9964 | **0.9987** | 0.9975 | 68.75% | **0.9851** | 0.9999 |
| Dense Autoencoder | 0.9964 | 0.9980 | 0.9972 | 68.75% | 0.9274 | 0.9989 |
| Isolation Forest | 0.9974 | 0.9960 | 0.9967 | 50.00% | 0.9842 | **0.9999** |
| Deep SVDD | 0.9951 | 0.9974 | 0.9962 | 93.75% | 0.8160 | 0.9954 |
| One-Class SVM | **0.9977** | 0.9924 | 0.9950 | **43.75%** | 0.9177 | 0.9980 |

---

## Scenario-Level Detection

At the 1% operating point:

| Scenario | IF | AE | Hybrid | LOF | OCSVM | Deep SVDD |
|---|---:|---:|---:|---:|---:|---:|
| Nmap scan | 100% | 100% | 100% | 100% | 99.75% | 100% |
| DNS burst | 99.17% | 100% | 100% | 100% | 98.83% | 100% |
| HTTP burst | 98.25% | 98.50% | 99.00% | 99.50% | 97.26% | 98.00% |
| SSH failed | 100% | 100% | 100% | 100% | 100% | 100% |
| Bulk transfer | 100% | 100% | 100% | 33.33% | 100% | 100% |
| ICMP burst | 100% | 100% | 100% | 100% | 100% | 100% |

---

## Practical-Test Interpretation

The models detected most generated attack scenarios successfully.

However, the practical dataset contains only **16 normal records**.

Because of this small normal sample:

```text
1 false positive = 6.25 percentage points of FPR
```

Therefore, the practical FPR values are highly sensitive to only a few normal classifications.

The very high Precision, Recall and F1 scores must also be interpreted carefully because the dataset is strongly attack-heavy.

For practical evaluation, the project therefore considers:

```text
FPR
ROC-AUC
PR-AUC
Scenario-level detection
```

in addition to Precision, Recall and F1.

Hybrid IF+AE and Isolation Forest showed particularly strong ranking performance on the practical traffic, while One-Class SVM produced the lowest observed FPR.

---

# Cross-Environment Comparison

The three testing environments produced substantially different behaviour.

| Environment | Main Finding |
|---|---|
| UNSW-NB15 | Stable benchmark performance with meaningful differences between models |
| NF-CSE-CIC-IDS2018-v2 | Severe threshold-transfer and distribution-shift problem |
| GNS3/Zeek | Strong attack detection, but FPR is unstable because only 16 normal records are available |

The testing demonstrates that strong benchmark performance alone is not sufficient evidence of deployment readiness.

The same model and threshold can behave very differently when network distributions change.

---

# Key Testing Finding

The most important conclusion from the final evaluation is:

> Models trained on one benchmark dataset may retain useful anomaly-ranking behaviour when transferred to another network, but the original detection threshold may no longer be appropriately calibrated.

For a real deployment, a practical approach would therefore be to preserve the trained anomaly models while calibrating thresholds using a representative window of benign traffic from the target organisation.

The labelled cross-dataset test sets used in this project were not used for threshold tuning.

---

# Reproducibility

To maintain consistency across all test environments:

- the UNSW-NB15 preprocessor was saved and reused;
- the 41-feature model order was preserved using the saved feature-order configuration;
- models were not retrained for NF-CSE or GNS3/Zeek testing;
- thresholds were derived only from normal UNSW validation data;
- the same scoring direction was used, where higher scores represent greater anomaly;
- all final evaluation outputs were saved for comparison.

The overall evaluation pathway was:

```text
Raw Test Dataset
        |
        v
Portable Feature Mapping
        |
        v
21 Features
        |
        v
Saved UNSW Preprocessor
        |
        v
41 Features
        |
        v
Frozen Models
        |
        v
Anomaly Scores
        |
        v
Saved Validation Thresholds
        |
        v
Normal / Anomaly Decision
        |
        v
Evaluation Metrics
```

---

# Limitations

The final testing should be interpreted with the following limitations:

- NF-CSE feature distributions differ substantially from UNSW-NB15.
- NF-CSE recent-connection features were calculated within the processed sample rather than the complete 18.9-million-flow temporal stream.
- Fixed UNSW thresholds showed poor transfer to NF-CSE.
- The practical GNS3/Zeek dataset contains only 16 normal records.
- The practical dataset is highly attack-heavy.
- Several practical scenarios contain very small record counts, particularly bulk transfer and ICMP.
- GNS3/Zeek results should therefore be interpreted as practical proof-of-concept evidence rather than a production deployment benchmark.

---

# Final Testing Status

| Component | Status |
|---|---|
| UNSW-NB15 six-model evaluation | Complete |
| NF-CSE preprocessing | Complete |
| NF-CSE six-model cross-dataset evaluation | Complete |
| Internal GNS3 traffic generation | Complete |
| External physical-laptop traffic generation | Complete |
| Internal + external practical dataset integration | Complete |
| Zeek 21-feature conversion | Complete |
| 41-feature model conversion | Complete |
| GNS3/Zeek six-model evaluation | Complete |
| Cross-environment comparison | Complete |
| Dashboard integration of additional datasets | Final integration / verification |

---

## Summary

The final testing stage evaluated six anomaly-detection approaches across benchmark, cross-dataset and independently generated practical traffic.

The results show that the Hybrid IF+AE approach provides a strong operational compromise on UNSW-NB15, while cross-dataset and practical testing demonstrate that threshold calibration is highly dependent on the target network environment.

The completed evaluation therefore supports the project's main design principle: anomaly detection should be assessed not only by benchmark accuracy, but also by false-positive behaviour, threshold transfer, explainability and performance under changing network conditions.
