# GNS3 Data Processing

This folder contains the processed GNS3 and Zeek traffic data prepared for the machine-learning models.
The main purpose of this stage was to convert the raw Zeek connection data into the same feature format used by the trained anomaly-detection models.

The processing notebook is available here: [GNS3 Data Processing Notebook in Google Colab](https://colab.research.google.com/drive/1qW0VUimTsEQOPwHnigX-GYFDBCvBWG5r#scrollTo=JVI20_eBST17)

---

## Data Processing Flow

The GNS3 traffic followed this process:

```text
Raw Zeek Traffic
      |
      v
13 Raw Zeek Fields
      |
      v
Feature Engineering
      |
      v
21 Portable Features
      |
      v
Saved Preprocessing Pipeline
      |
      v
41 Numerical Model Features
```

---

## Input Data

The starting dataset was:

### `all_traffic_features_raw.tsv`

This file contains the combined normal and controlled attack traffic generated in the GNS3 laboratory.

The dataset contains:

| Traffic Type | Records |
|---|---:|
| Normal | 12 |
| Nmap scan | 1,002 |
| HTTP burst | 200 |
| DNS burst | 199 |
| Bulk transfer | 3 |
| **Total** | **1,416** |

The raw Zeek connection information contained 13 main fields:

```text
ts
id.orig_h
id.orig_p
id.resp_h
id.resp_p
proto
service
duration
orig_ip_bytes
resp_ip_bytes
orig_pkts
resp_pkts
conn_state
```

A `traffic_type` column was also included to identify the source scenario of each record.

---

## 21 Portable Features

The raw Zeek information was converted into 21 network features.

The 21 features are:

```text
dur
spkts
dpkts
sbytes
dbytes
rate
sload
dload
smean
dmean
ct_srv_src
ct_srv_dst
ct_dst_ltm
ct_src_ltm
ct_src_dport_ltm
ct_dst_sport_ltm
ct_dst_src_ltm
is_sm_ips_ports
proto
service
state
```

The first 18 features are numerical features.

The remaining three are categorical features:

```text
proto
service
state
```

Some features were taken directly from the Zeek connection data, while others were calculated during feature engineering.

Examples of calculated features include:

- packet rate;
- source traffic load;
- destination traffic load;
- average source packet size;
- average destination packet size; and
- recent connection-count behaviour.

The processed 21-feature dataset was saved as:

### `gns3_all_traffic_21_features.csv`

The final shape was:

```text
1,416 rows × 21 features
```

---

## Converting 21 Features to 41 Features

The machine-learning models require numerical input.

However, the 21-feature dataset still contained text-based categorical values in:

```text
proto
service
state
```

For example, these fields can contain values such as:

```text
tcp
udp
http
dns
ssh
FIN
REQ
RST
```

The same saved preprocessing pipeline used during model training was applied to the GNS3 data.

The categorical values were converted into numerical 0/1 columns using one-hot encoding.

The process was:

```text
21 Features
   |
   | 18 numerical features
   | 3 categorical features
   v
Saved Preprocessor
   |
   v
41 Numerical Features
```

This step does not add new network information. It changes the existing categorical information into the numerical format expected by the trained models.

---

## Final 41-Feature Dataset

The final machine-learning input was saved as:

### `gns3_all_traffic_41_features.csv`

The final result was:

```text
1,416 rows
41 numerical model features
0 missing values
```

This dataset is ready to be passed to the trained anomaly-detection models.

---

## Metadata

The traffic information that is not directly used as model input was stored separately in:

### `gns3_all_traffic_metadata.csv`

The metadata keeps information such as:

- traffic type;
- timestamp;
- source IP address;
- source port;
- destination IP address;
- destination port; and
- normal or attack label.

Keeping this information separate allows the machine-learning input file to contain only the features required by the models.

---

## Files in This Folder

| File | Description |
|---|---|
| `gns3_all_traffic_21_features.csv` | 21 portable network features created from Zeek data |
| `gns3_all_traffic_41_features.csv` | 41 numerical features ready for the trained models |
| `gns3_all_traffic_metadata.csv` | Traffic type, labels and connection information |

---

## Final Processing Result

```text
Raw traffic records:        1,416
Portable features:          21
Model-ready features:       41
Missing values:             0
```

The final processing pipeline successfully converted the GNS3 and Zeek laboratory traffic into the same numerical feature format required by the trained anomaly-detection models.
