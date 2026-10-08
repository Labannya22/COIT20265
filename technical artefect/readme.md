
# COIT20265 — Final Technical Artefacts

## Project Title

**Explainable and False-Positive-Aware Hybrid Unsupervised Network Anomaly Detection for Australian SME Financial Services**

**University:** CQUniversity Australia  
**Unit:** COIT20265 — Networks and Information Security Project  
**Group:** PG3  
**Term:** HT2 2026

---

## 1. Project Overview

This repository contains the final technical artefacts developed by Group PG3 for the COIT20265 Networks and Information Security Project.

Our project focuses on developing and evaluating an unsupervised network anomaly detection prototype for Australian small and medium-sized financial services organisations.

The system uses six anomaly detection models, benchmark datasets, and practical network traffic collected through a GNS3/VMware laboratory with Zeek monitoring.

The project also investigates cross-dataset performance, false-positive behaviour, threshold recalibration, and dashboard-based security monitoring.

The technical artefacts document the complete project lifecycle, from requirements and architecture design to implementation, testing, risk assessment, and ethical considerations.

---

## 2. Technical Artefacts

The project includes ten technical artefacts.

| No. | Technical Artefact | Description |
|---|---|---|
| TA1 | System Requirements and Architecture Design Report | Defines the project problem, objectives, requirements, stakeholders, system architecture, and design decisions. |
| TA2 | UNSW-NB15 Dataset Preparation and Data Engineering Report | Documents dataset profiling, cleaning, duplicate handling, feature selection, preprocessing, and preparation of model-ready data. |
| TA3 | NF-CSE-CIC-IDS2018-v2 Cross-Dataset Preparation and Compatibility Engineering | Explains cross-dataset feature mapping, preprocessing compatibility, sampling, and preparation for external-domain evaluation. |
| TA4 | Isolation Forest, Autoencoder and Hybrid Model Development | Documents model architecture, normal-only training, parameter settings, anomaly scoring, hybrid fusion, and validation thresholds. |
| TA5 | Local Outlier Factor, One-Class Support Vector Machine and Deep Support Vector Data Description Model Design and Implementation | Explains the implementation, configuration, training, evaluation, and integration of three additional anomaly detection models. |
| TA6 | Three-Stage Anomaly Detection Testing and Evaluation: Threshold Evaluation Framework and Calibration Analysis | Evaluates model performance, threshold transfer, target-domain recalibration, and threshold sensitivity across UNSW-NB15 and NF-CSE. |
| TA7 | GNS3/Zeek Practical Network Dataset Engineering and Three-Stage Evaluation of Unsupervised Network Anomaly Detection | Documents laboratory design, virtual machine configuration, traffic generation, Zeek monitoring, practical dataset preparation, and model evaluation. |
| TA8 | Dashboard Design, Implementation and Integration | Describes Streamlit dashboard development, model integration, result visualisation, SQLite alert storage, and interface testing. |
| TA9 | Risk Assessment and Security Controls Report | Identifies technical and operational risks, evaluates security controls, and recommends risk treatment measures. |
| TA10 | Ethical, Legal and Professional Considerations Report | Evaluates privacy, legal obligations, professional responsibilities, responsible AI use, and ethical implications. |

---

## 3. Technical Artefact Files

All ten final technical artefacts are stored in the `Technical_Artefacts/` directory.

```text
Technical_Artefacts/
├── PG3_TA1_System_Requirements_Architecture.docx
├── PG3_TA2_UNSW_NB15_Dataset_Engineering.docx
├── PG3_TA3_NF_CSE_CIC_IDS2018_v2_Dataset_Engineering.docx
├── PG3_TA4_IF_AE_Hybrid_Model_Implementation.docx
├── PG3_TA5_LOF_OCSVM_DeepSVDD_IMPLEMENTATION.docx
├── PG3_TA6_Three_Stage_Testing_and_Threshold_RESULTS.docx
├── PG3_TA7_Zeek_dataset_implementation_testing.docx
├── PG3_TA8_Dashboard_Implementation_Artefact.docx
├── PG3_TA9_Risk_Assessment_Security_Controls.docx
└── PG3_TA10_Ethical_Legal_Professional_Considerations.docx
```

**Note:** The filenames above should be updated if the final uploaded files use revised names.

---

## 4. Technologies and Tools

The project uses the following technologies:

- Python for dataset processing, machine learning, and evaluation.
- Google Colab and Jupyter Notebook for model development and testing.
- Scikit-learn for Isolation Forest, LOF, One-Class SVM, and preprocessing.
- TensorFlow/Keras for Autoencoder implementation.
- PyTorch for Deep SVDD implementation.
- GNS3 and VMware for virtual network laboratory development.
- Ubuntu Linux and Kali Linux for network endpoints and controlled attack simulation.
- Zeek for passive network traffic monitoring.
- Streamlit for interactive security dashboards.
- SQLite for alert storage.
- Pandas and NumPy for data processing and analysis.

---

## 5. Machine Learning Models

Six anomaly detection approaches were developed and evaluated:

1. Isolation Forest (IF)
2. Dense Autoencoder (AE)
3. Hybrid Isolation Forest + Autoencoder (IF+AE)
4. Local Outlier Factor (LOF)
5. One-Class Support Vector Machine (OCSVM)
6. Deep Support Vector Data Description (Deep SVDD)

The models were trained using normal traffic from UNSW-NB15.

Their performance was subsequently evaluated using benchmark and external network traffic datasets.

The evaluation focuses on anomaly detection performance, false-positive rates, threshold transfer, and recalibration.

---

## 6. Testing and Evaluation

The project includes three main evaluation stages:

**Stage 1 — Original Threshold Evaluation**

Apply the original source-domain validation thresholds to assess model behaviour.

**Stage 2 — Target-Normal Threshold Recalibration**

Recalculate decision thresholds using target-domain normal traffic while keeping trained models unchanged.

**Stage 3 — Threshold Sensitivity Analysis**

Evaluate detector behaviour across multiple false-positive budgets.

The results demonstrate the challenges of transferring anomaly detection thresholds between different network environments.

Detailed quantitative results and limitations are presented in Technical Artefacts 6 and 7.

---

## 7. Supporting Source Code

The project implementation includes notebooks and source-code files covering:

- UNSW-NB15 profiling and preprocessing.
- NF-CSE-CIC-IDS2018-v2 preparation.
- Isolation Forest, Autoencoder, and Hybrid implementation.
- LOF, One-Class SVM, and Deep SVDD implementation.
- Cross-dataset model testing and evaluation.
- GNS3/Zeek evaluation and threshold recalibration.
- Streamlit dashboard development and integration.

Refer to the relevant technical artefacts and source-code directories for implementation details.

---

## 8. Supporting Demonstration Videos

Video demonstrations covering network configuration, dataset engineering, model evaluation, dashboard implementation, and project functionality are available in the **Group PG3 Microsoft Teams channel**.

These videos provide supporting evidence of the technical work completed during the project.

The recordings are not included directly in this repository.

---

## 9. Project Team

| Team Member | Main Technical Responsibilities |
|---|---|
| Labannya Barua | UNSW-NB15 dataset engineering, cross-domain testing, threshold analysis |
| Syed Rubaiyat Karim | NF-CSE dataset engineering, Isolation Forest, Autoencoder, Hybrid implementation |
| Arjita Saha | GNS3/VMware laboratory, Ubuntu/Kali/Zeek configuration, network traffic generation, practical testing |
| Mst Sinha Naznin | LOF, One-Class SVM, Deep SVDD, Streamlit dashboard implementation and integration |

All members contributed to the overall project development, integration, documentation, risk assessment, and ethical considerations.

---

## 10. Limitations

This project is a research and demonstration prototype rather than a production intrusion detection system.

Key limitations include:

- Differences between benchmark and practical network traffic.
- Sensitivity of model thresholds to changes in network environments.
- False-positive and false-negative trade-offs.
- Approximate feature compatibility across datasets.
- Limited representativeness of laboratory-generated traffic.
- Need for additional security controls before production deployment.

---

## 11. Conclusion

The ten technical artefacts document the development and evaluation of an explainable, false-positive-aware network anomaly detection prototype.

The project combines machine learning, network security engineering, practical traffic monitoring, model evaluation, and dashboard integration.

A central finding is that threshold calibration and environmental differences significantly affect anomaly detection performance.

The complete technical documentation provides evidence of the system's design, implementation, evaluation, limitations, and recommendations for future improvement.

---

**CQUniversity Australia**  
**COIT20265 — Networks and Information Security Project**  
**Group PG3 | HT2 2026**
