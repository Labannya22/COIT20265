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

## 4. LOF Baseline Model

First, I imported the required Python libraries, including NumPy, Pandas, Matplotlib, Joblib and LocalOutlierFactor from Scikit-learn. I also set a fixed random seed and defined the project folders for processed data, trained models, configuration files and reports.

Next, I loaded three processed NPZ files. The normal training dataset was used to teach the model normal network behaviour. The normal validation dataset was used to select the thresholds, and the full test dataset contained both normal and attack records for final evaluation.

Before training, I checked the shape of the datasets, the number of input features and whether the data contained any missing or infinite values.

I then configured Local Outlier Factor for novelty detection and fitted it using normal training records. LOF compares every network record with its nearest neighbours and calculates its local density. If a record has a significantly different density from its neighbours, it is considered unusual.

After fitting the model, I generated LOF scores for the training, validation and test records. I converted the scoring direction so that a higher LOF score consistently means that the record looks more anomalous.

I then used the normal validation scores to calculate thresholds for 0.5-percent, 1-percent and 3-percent false-positive budgets. For the final dashboard and model comparison, I selected the 1-percent budget as the default operating point. Its threshold was approximately 1.801.

For each test record, I compared its LOF score with the threshold. If the score was equal to or higher than the threshold, I assigned prediction one, meaning Anomaly. Otherwise, I assigned prediction zero, meaning Normal.

After producing the predictions, I evaluated the model using Precision, Recall, F1 score, Actual FPR, false alerts per 1,000 records, ROC-AUC, PR-AUC and confusion-matrix values.

At the default operating point, LOF achieved 93.64 percent precision, 52.27 percent recall and an F1 score of approximately 0.671. It produced approximately 43 false alerts per 1,000 normal records, which was the lowest false-alert rate among the six compared models.

Finally, I created a dashboard-ready dataframe containing 82,332 records. It includes the record ID, actual class, LOF score, predictions for each budget, default threshold, final status and prediction correctness.

I saved the trained model as a Joblib file, the model settings as a JSON file, the evaluation results and dashboard data as CSV files, and the score-distribution graph as a PNG file. I then connected the dashboard-result CSV to my Streamlit dashboard for interactive presentation and record-level investigation.


## 4. Deep SVDD Model

This notebook implements the Deep Support Vector Data Description model for network anomaly detection. The model is trained using normal network records and learns to map normal traffic into a compact area around a central point. Records located close to this centre are treated as normal, while records located farther away receive higher anomaly scores and may be classified as anomalies.

The notebook loads the normal training data, normal validation data and full test data. It checks the input dimensions and data quality before training the Deep SVDD network. After training, it calculates an anomaly score for every validation and test record based on its distance from the learned normal centre.

Thresholds are calculated for 0.5-percent, 1-percent and 3-percent false-positive budgets. The 1-percent budget is used as the default operating point for the dashboard and final model comparison. Its default threshold is approximately 0.0000549.

At the default operating point, Deep SVDD achieved 92.74 percent precision, 59.45 percent recall and an F1 score of approximately 0.725. Its actual false-positive rate was 5.7 percent, which represents approximately 57 false alerts per 1,000 normal records. Among One-Class SVM, LOF and Deep SVDD, Deep SVDD achieved the highest F1 score.

The notebook generates a dashboard-ready CSV containing 82,332 record-level results. The output includes the record ID, actual class, Deep SVDD score, predictions at different budgets, default threshold, final status and prediction correctness. The trained model, configuration, evaluation results and score-distribution graph are also saved as technical artefacts.





