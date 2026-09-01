# NF-CSE-CIC-IDS2018-v2 Processing

## Why We Used NF-CSE-CIC-IDS2018-v2

NF-CSE-CIC-IDS2018-v2 provides a second and different source of labelled network traffic. This helps the group investigate whether the intrusion-detection approach can generalise beyond UNSW-NB15. It is also suitable because it represents both normal and attack traffic using detailed NetFlow attributes. Using a second dataset produces stronger evidence than evaluating the project on only one traffic environment.

## Dataset Understanding

The original CSV is approximately 3 GB and contains 18,893,708 network-flow records. Each row represents a network flow. Its columns describe properties such as source and destination ports, protocol, packet counts, transferred bytes, flow duration, TCP flags and other traffic statistics. The dataset also contains a binary label identifying normal or attack traffic and an attack-name field.

The key technical challenge was its size. Loading the complete file into Colab memory could cause the runtime to disconnect. Therefore, I processed it in chunks of 200,000 rows, allowing every row to be inspected while controlling memory usage.

## Technical Artefact

My second-dataset artefact consists of:

A reproducible Google Colab preprocessing notebook

train_normal.npz — normal-only training data

val_normal.npz — separate normal calibration data

test_full.npz — labelled normal and attack testing data

feature_order.json — the required order of the 40 input features

robust_scaler.joblib — the fitted preprocessing scaler

processing_summary.json — evidence of the completed processing

A compressed preprocessing evidence package

Collab: https://colab.research.google.com/drive/1liS4vvLZYAE7W5zO26g8spefoiVhItKN?usp=sharing

## Processing Method and Technical Attributes
The complete CSV was streamed in chunks instead of loading all 18.9 million rows into memory.
Column names were standardised, and the binary label field was checked.
Positive and negative infinite values were replaced with missing values.
Duplicate records were detected and removed within each chunk.
Records containing invalid labels were excluded.
A reproducible sample of 400,000 normal and 300,000 attack records was retained using a fixed random seed.
Source and destination IP addresses were removed because they are identifiers.
The Label and Attack columns were excluded from model inputs to prevent target leakage.
The remaining columns were converted to numeric values, while unusable and constant columns were removed, leaving 40 features.
Normal traffic was divided into training, calibration and testing subsets.
Missing-value replacements and clipping limits were calculated using only the normal training data.


A RobustScaler was fitted only on the normal training records and then applied to the remaining datasets.
Finally, all outputs were checked to confirm that no invalid or infinite values remained before they were saved.

## Evidence of Deep Technical Understanding

### Preventing data leakage

The IP addresses were removed because a model could memorise particular devices or networks instead of learning meaningful traffic behaviour. The label and attack name were excluded because they directly reveal the expected answer. I also fitted the scaler and calculated clipping limits from the normal training data only. Using test or attack data for these calculations would leak information into the preparation stage and make the evaluation less reliable.

### Reason for normal-only training

The anomaly-detection approach is designed to learn normal behaviour and assign higher anomaly scores to traffic that differs from it. Therefore, the training set contains only normal records. A separate normal calibration set supports threshold selection without using the final test set.

### Reason for RobustScaler and clipping

Network-flow values such as byte counts and durations can contain very large outliers. Quantile clipping limits the effect of extreme values, while RobustScaler uses robust statistics and is less sensitive to large outliers than ordinary standardisation. The same fitted transformation is then applied consistently to every dataset.

### Reproducibility and model compatibility

A fixed random seed makes the retained sample and data split reproducible. The feature-order file ensures that every team member supplies the same 40 variables to the models in the same order. The fitted scaler allows the exact preprocessing transformation to be reused rather than estimated again.

