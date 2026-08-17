# Hybrid Unsupervised Network Anomaly Detection

**COIT20265 – Networks and Information Security Project, HT2 2026**

This project develops an **explainable and false-positive-aware hybrid unsupervised network anomaly detection system**.

The main approach combines **Isolation Forest (IF)** and a **Dense Autoencoder (AE)**. The hybrid model is compared with other unsupervised anomaly-detection models, including **One-Class SVM (OCSVM)**, **Deep SVDD**, and a **Local Outlier Factor (LOF) baseline**.

The system is trained using **normal network traffic only** and evaluated using:

- **UNSW-NB15**
- **NF-CSE-CIC-IDS2018-v2**
- Independently generated **GNS3/Zeek laboratory traffic**

---

## System Workflow

```text
                         Normal Training Data
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
 Isolation Forest            Autoencoder               OCSVM
          |                       |                       |
          v                       v                       v
      IF Score                AE Score              OCSVM Score
          |                       |                       |
          +-----------+-----------+                       |
                      |                                   |
                      v                                   |
                IF + AE Hybrid                            |
                      |                                   |
                      +-------------------+---------------+
                                          |
                                          v
                                Final Model Comparison
                                  + LOF Baseline
                                          ^
                                          |
                                     Deep SVDD
```

The **Isolation Forest and Autoencoder anomaly scores are combined to create the main IF + AE hybrid detector**.

The final comparison includes:

- IF + AE Hybrid
- OCSVM
- Deep SVDD
- LOF baseline

Calibration and threshold selection will be used during evaluation to support false-positive-aware anomaly detection.

---

## Evaluation Data

### 1. UNSW-NB15

UNSW-NB15 is the primary benchmark dataset.

The preprocessing work for this dataset has been completed. Normal training data is used for unsupervised model training, while the labelled test data is used for evaluation.

### 2. NF-CSE-CIC-IDS2018-v2

NF-CSE-CIC-IDS2018-v2 is the second benchmark dataset.

This dataset is currently being processed to evaluate whether the developed models can generalise beyond UNSW-NB15.

### 3. GNS3 / Zeek Dataset

A practical network dataset is independently generated using the GNS3 laboratory.

The current normal traffic contains:

- HTTP
- DNS
- SSH
- ICMP

The traffic is captured as PCAP and processed using **Zeek** to create connection-level information for practical model testing.

---

## Model Progress

| Model | Purpose | Status |
|---|---|---|
| Isolation Forest | Main unsupervised anomaly detector |  Implemented |
| Dense Autoencoder | Reconstruction-based anomaly detector |  Implemented |
| IF + AE Hybrid | Main hybrid detector |  Implemented |
| One-Class SVM | Comparison model |  In progress |
| Deep SVDD | Comparison model |  In progress |
| Local Outlier Factor | Baseline comparison |  In progress |

---

## Current Project Progress

| Area | Team Member | Progress |
|---|---|---|
| Dataset Processing | **Labannya Barua** |  UNSW-NB15 processing completed; currently working on NF-CSE-CIC-IDS2018-v2 |
| Model Development | **Syed Rubaiyat Karim** |  IF, AE and IF+AE Hybrid implemented; OCSVM and Deep SVDD currently in progress |
| Virtual Network and Traffic Generation | **Arjita Saha** |  GNS3/Zeek environment configured and normal HTTP, DNS, SSH and ICMP dataset created |
| Dashboard and Integration | **Mst Sinha Naznin** |  Dashboard implemented and three model outputs integrated; LOF implementation/integration currently in progress |

---

## GNS3 / Zeek Laboratory

The practical laboratory contains four systems:

| System | Address / Mode |
|---|---|
| Ubuntu Client | `192.168.10.10/24` |
| Ubuntu Server | `192.168.10.20/24` |
| Kali Attacker | `192.168.10.30/24` |
| Zeek Sensor | Passive monitoring |

Current laboratory progress:

- [x] Four-role GNS3 topology
- [x] Isolated `192.168.10.0/24` network
- [x] Zeek 8.0.9 monitoring
- [x] HTTP traffic
- [x] DNS traffic
- [x] SSH traffic
- [x] ICMP traffic
- [x] Clean normal PCAP
- [x] Zeek log generation
- [x] Connection feature extraction
- [ ] Nmap reconnaissance traffic
- [ ] Controlled bulk/exfiltration-like traffic
- [ ] Final Zeek-to-model feature mapping

Detailed laboratory documentation is available under:

```text
gns3/
```

---

## Dashboard

The dashboard presents anomaly-detection results in an analyst-friendly format.

Current dashboard work includes:

- dashboard interface implemented;
- three model outputs integrated;
- model anomaly results displayed;
- model comparison support;
- LOF implementation/integration currently in progress.

Further work will include:

- final hybrid-model integration;
- calibration results;
- severity information;
- explainability output.

---

## Current Development Status

### Completed

- [x] UNSW-NB15 preprocessing
- [x] Isolation Forest implementation
- [x] Dense Autoencoder implementation
- [x] IF + AE Hybrid implementation
- [x] GNS3/Zeek laboratory setup
- [x] Normal HTTP/DNS/SSH/ICMP dataset generation
- [x] Clean normal PCAP capture
- [x] Zeek log generation
- [x] Connection feature extraction
- [x] Dashboard implementation
- [x] Three model outputs integrated into the dashboard

### In Progress

- [ ] NF-CSE-CIC-IDS2018-v2 preprocessing
- [ ] OCSVM implementation
- [ ] Deep SVDD implementation
- [ ] LOF implementation/integration
- [ ] Controlled Nmap traffic
- [ ] Controlled bulk/exfiltration-like traffic
- [ ] Calibration and final model comparison
- [ ] Final dashboard integration
- [ ] Explainability and severity presentation

---

## Team

- **Labannya Barua** – Dataset and Data Engineering
- **Syed Rubaiyat Karim** – Machine-Learning and Hybrid Model Development
- **Arjita Saha** – GNS3 Virtual Network, Traffic Generation and Zeek Validation
- **Mst Sinha Naznin** – Dashboard, Model Integration and Explainability
