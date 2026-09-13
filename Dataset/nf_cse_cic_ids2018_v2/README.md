# NF-CSE-CIC-IDS2018-v2 Preprocessing

## Purpose

NF-CSE-CIC-IDS2018-v2 was selected as a second network-security dataset to evaluate whether the project’s anomaly-detection system can generalise beyond UNSW-NB15. The processed NF-CSE data is intended for cross-dataset testing only. No model was trained and no new scaler was fitted using NF-CSE records.

## Dataset Overview

The original CSV is approximately 3 GB and contains 18,893,708 network-flow records with 45 columns. Each row represents a network flow described through attributes such as protocol, ports, transferred bytes, packet counts, flow duration and TCP flags. The dataset also provides a binary label distinguishing normal and attack traffic and an attack-category field.

## Processing Method

Because loading the complete dataset into Colab memory could cause runtime disconnection, the CSV was streamed in chunks of 200,000 records. Column names were standardised, positive and negative infinite values were converted to missing values, duplicate records were removed within each chunk, and invalid or non-numeric labels were excluded.

A fixed random seed of 42 was used to create a reproducible bounded sample containing 400,000 normal and 300,000 attack records. Attack sampling was stratified by attack category to retain representation of the available attack types.

Source and destination IP addresses were used temporarily when calculating connection-based attributes but were excluded from the final model matrix. The `Label` and `Attack` fields were also excluded from the input features to prevent target leakage.

## Feature Alignment

The NF-CSE schema differs from the UNSW-NB15 schema used by the existing project models. Therefore, compatible traffic attributes were mapped into 21 portable features covering duration, packets, bytes, rates, loads, mean packet sizes, protocol, service, connection state and recent-connection statistics.

Protocol values were mapped into common categories such as TCP, UDP and other. Services were approximated using known source and destination ports, while connection states were inferred from protocol and TCP-flag information. Seven recent-connection attributes were calculated using a rolling window of the previous 100 sampled flows.

The previously fitted UNSW preprocessing pipeline was reused to encode and transform the 21 portable attributes into the exact 41-feature representation required by the existing models. Reusing the UNSW preprocessor avoids fitting transformations on the NF-CSE test dataset and reduces cross-dataset information leakage.

## Validation Results

The final processing workflow produced:

| Technical attribute | Result |
|---|---:|
| Raw records inspected | 18,893,708 |
| Duplicates removed within chunks | 5 |
| Selected normal records | 400,000 |
| Selected attack records | 300,000 |
| Total selected records | 700,000 |
| Portable features | 21 |
| Final model features | 41 |
| Missing values | 0 |
| Infinite values | 0 |
| Random seed | 42 |
| Model training on NF-CSE | No |
| New scaler fitted on NF-CSE | No |

The final matrix passed shape, label-count, feature-order and finite-value checks before being saved.

## Technical Artefacts

The repository contains:

- `NF_CSE_CIC_IDS2018_v2_Preprocessing_complete.ipynb` — complete preprocessing and verification notebook
- `processing_summary.json` — machine-readable processing summary
- `attack_distribution.csv` — selected and source attack-category counts
- `feature_order_41.json` — required order of the final 41 model features
- `nf_cse_41_preview.csv` — small preview of the transformed model matrix
- `nf_cse_selected_attack_distribution.png` — visualisation of selected attack categories

The original 3 GB CSV is not stored in GitHub because of its size. The complete processed matrix is retained in the project’s approved Google Drive or Microsoft Teams storage when it exceeds GitHub’s file-size limit.

## Reproducibility

The workflow requires:

1. `NF-CSE-CIC-IDS2018-v2.csv`
2. The fitted UNSW `preprocessor.joblib`
3. The corresponding UNSW `feature_order.json`
4. Python packages including pandas, NumPy, scikit-learn, joblib and Matplotlib

The notebook should be run from top to bottom using the fixed seed. Processing is complete when the final section reports:

- text
ALL FINAL CHECKS PASSED
Limitations

Duplicate detection is performed within individual chunks rather than globally across the complete CSV. Service and connection-state values are approximated because NF-CSE and UNSW-NB15 use different schemas. Recent-connection statistics are calculated over the previous 100 sampled flows rather than the complete unsampled stream. The selected attack sample also reflects the dataset’s original imbalance, with some attack categories having substantially more records than others.

# Individual Contribution

Following the team’s feature-alignment update, Syed Rubaiyat Karim configured the revised workflow in Google Colab, verified the required dataset and preprocessing dependencies, executed the complete processing pipeline, checked the generated 21-feature and 41-feature representations, and prepared the resulting technical evidence for GitHub and Microsoft Teams.

# Colab Notebook

## Colab Notebook

[Open the NF-CSE-CIC-IDS2018-v2 Preprocessing Notebook](https://colab.research.google.com/drive/1N-SOe23ULur_bL8Vk-9FWxY-bgB762IT)
