# ML Model Development – Syed Rubaiyat Karim

This folder contains machine-learning model experiments for the network anomaly detection project. The models use the preprocessed UNSW-NB15 dataset to identify unusual network traffic and possible cyberattacks.

## Included notebooks

### 1. Isolation Forest Model

**File:** [Isolation_Forest_Model_Rubaiyat.ipynb](https://github.com/Labannya22/COIT20265/blob/main/ml_models_syed_rubaiyat/Isolation_Forest_Model_Rubaiyat.ipynb)

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

The Dense Autoencoder learns to reconstruct normal network traffic. Traffic with a high reconstruction error can be identified as anomalous.

This notebook is included for baseline training, testing and comparison with Isolation Forest.

### 3. Hybrid Isolation Forest and Autoencoder Model

**File:** [Hybrid_IF_AE_Model.ipynb](https://github.com/Labannya22/COIT20265/blob/main/ml_models_syed_rubaiyat/Hybrid_IF_AE_Model.ipynb)

The hybrid model combines Isolation Forest anomaly scores with Autoencoder reconstruction errors. The purpose is to examine whether combining the two detection methods can improve attack detection while controlling false-positive alerts.

## Dataset and preprocessing

The experiments use the UNSW-NB15 network intrusion dataset. The shared preprocessing pipeline converts the selected raw features into 41 model-ready features.

The models use:

* Normal-only records for unsupervised training
* Normal calibration records for threshold selection
* Mixed development records for model comparison
* The official test set for final evaluation

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

