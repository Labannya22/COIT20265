# ML Model Development – Syed Rubaiyat Karim

This folder contains machine-learning model experiments for the network anomaly detection project. The models use the preprocessed UNSW-NB15 dataset to identify unusual network traffic and possible cyberattacks.

## Included notebooks

### 1. Isolation Forest Model

**File:** [Isolation_Forest_Model_Rubaiyat.ipynb](https://github.com/Labannya22/COIT20265/blob/main/ml_models_syed_rubaiyat/Isolation_Forest_Model_Rubaiyat.ipynb)

The model implementation can be viewed and executed in Google Colab: [Open Model Notebook in Google Colab](https://colab.research.google.com/drive/1FoZumclAwmI9JTq9dcmauGnfdot3JXDw) 

The Isolation Forest model was trained using normal network traffic. Six model configurations were compared using separate training, calibration and development data.

IF-2 was selected as the final configuration based on its ROC-AUC and PR-AUC performance. The official UNSW-NB15 test set was kept separate during model selection and was only used for the final evaluation.

Final official test results:

* ROC-AUC: 0.851
* PR-AUC: 0.897
* Precision at the 1% calibration budget: 0.938
* Recall at the 1% calibration budget: 0.618
* F1-score at the 1% calibration budget: 0.745

The notebook also evaluates the official and deduplicated test sets and produces comparison tables, confusion matrices, ROC and precision-recall curves, anomaly-score graphs and prediction results.

### 2. Dense Autoencoder Model

**File:** [Dense_Autoencoder_Model.ipynb](https://github.com/Labannya22/COIT20265/blob/main/ml_models_syed_rubaiyat/Dense_Autoencoder_Model.ipynb)

The model implementation can be viewed and executed in Google Colab:   [Open Model Notebook in Google Colab](https://colab.research.google.com/drive/1FoZumclAwmI9JTq9dcmauGnfdot3JXDw)

The Dense Autoencoder learns to reconstruct normal network traffic. Traffic with a high reconstruction error can be identified as anomalous.

This notebook is included for baseline training, testing and comparison with Isolation Forest.

### 3. Hybrid Isolation Forest and Autoencoder Model

**File:** [Hybrid_IF_AE_Model.ipynb](https://github.com/Labannya22/COIT20265/blob/main/ml_models_syed_rubaiyat/Hybrid_IF_AE_Model.ipynb)

The model implementation can be viewed and executed in Google Colab:  [Open Model Notebook in Google Colab](https://colab.research.google.com/drive/1J_3kuGjgPivttk9q0VtEYUIwE8xqczI3) 

The hybrid model combines Isolation Forest anomaly scores with Autoencoder reconstruction errors. The purpose is to examine whether combining the two detection methods can improve attack detection while controlling false-positive alerts.

## Dataset and preprocessing

The experiments use the UNSW-NB15 network intrusion dataset. The shared preprocessing pipeline converts the selected raw features into 41 model-ready features.

The models use:

* Normal-only records for unsupervised training
* Normal calibration records for threshold selection
* Mixed development records for model comparison
* The official test set for final evaluation

## 4. One-Class SVM (OCSVM)

The One-Class SVM model was developed by **Mst Sinha Naznin**. It learns a decision boundary around normal network-traffic records. Records outside this boundary are identified as potential anomalies.

The model was evaluated using different false-positive budgets. Its dashboard displays the OCSVM score, threshold, prediction status, actual class and record-level details.

**Files:**

* `One_Class_SVM_Model.ipynb`
* `ocsvm_dashboard_results.csv`


```

## 5. Local Outlier Factor (LOF)

The Local Outlier Factor model was developed by **Mst Sinha Naznin**. LOF compares the local density of each network record with the density of its neighbouring records. A record with a significantly different local density is considered a potential anomaly.

The LOF dashboard presents the anomaly score, threshold, prediction status, actual class and detailed results for a selected record.

**Files:**

* `LOF_Baseline_Model.ipynb`
* `lof_dashboard_results.csv`

```

## 6. Deep SVDD

The Deep Support Vector Data Description model was developed by **Mst Sinha Naznin**. Deep SVDD learns a compact representation of normal network traffic around a central point. Records located farther from the learned normal centre receive higher anomaly scores and may be classified as anomalies.

The Deep SVDD dashboard displays the anomaly score, threshold, detection status, severity and selected-record details.

**Files:**

* `Deep_SVDD_Model.ipynb`
* `deep_svdd_dashboard_results.csv`


```

## Final Six-Model Comparison

A final comparison dashboard was created to compare all six anomaly-detection approaches:

1. Isolation Forest
2. Autoencoder
3. Hybrid IF+AE
4. One-Class SVM
5. Local Outlier Factor
6. Deep SVDD

The dashboard compares Precision, Recall, F1 score, Actual FPR, false alerts per 1,000 normal records, ROC-AUC, PR-AUC and confusion-matrix results.

**Files:**

* `Final_Model_Comparison.ipynb`
* `final_model_ranking_1pct.csv`


## Reproducibility

The notebooks use fixed random seeds and recorded model parameters. The Isolation Forest configuration, trained model, result tables, predictions and graphs are saved as reproducible artefacts.

The shared project dataset and preprocessing files must be uploaded and extracted in Google Colab before running the notebooks.

## Current progress

* ML environment configured
* Model inputs and preprocessing pipeline confirmed
* Isolation Forest model selection completed
* Final Isolation Forest evaluation completed
* Reproducible Isolation Forest configuration recorded
* Dense Autoencoder notebook added
* Hybrid Isolation Forest–Autoencoder notebook added

## Next steps

* Run the Dense Autoencoder notebook from a clean Colab runtime
* Verify its training, validation and testing process
* Record its ROC-AUC, PR-AUC, precision, recall, F1-score and false-positive rate
* Test and validate the hybrid anomaly-scoring method
* Compare all models using the same data partitions and evaluation measures
* Test an OCSVM baseline using normal UNSW-NB15 traffic
* Save the final models, configurations, tables and graphs
* Review relevant research literature and justify the final model selection

## Contributors

The machine-learning work is part of the group network anomaly detection project. The notebooks were developed and organised through group collaboration, with Syed Rubaiyat Karim responsible for the Isolation Forest, Auto encoder and hybrid isolation.

