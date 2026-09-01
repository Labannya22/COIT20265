# Anomalous Traffic

This folder contains controlled anomalous traffic generated in the GNS3 laboratory.

## Scenarios

- Nmap port scan
- HTTP request burst
- DNS query burst
- Bulk file transfer

---

## Raw Zeek Data

For each attack, selected fields were extracted from Zeek `conn.log`.

The main 13 raw Zeek fields were:

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

These fields contain information such as:

- source and destination IP addresses;
- source and destination ports;
- protocol;
- service;
- connection duration;
- transferred bytes;
- packet counts; and
- connection state.

---

## Individual Attack Files

nmap_features_raw.tsv: Contains the raw Zeek connection information from the controlled Nmap port scan.
The scan generated connection attempts to many different destination ports on the Ubuntu Server.

## http_features_raw.tsv

Contains the raw Zeek connection information from the HTTP request burst.

Repeated HTTP GET requests were generated against the web service running on the Ubuntu Server.

## dns_features_raw.tsv

Contains the raw Zeek connection information from the DNS query burst.

Repeated DNS queries were generated against the DNS service using the test domain: app.lab


## bulk_features_raw.tsv

Contains the raw Zeek connection information from the bulk-transfer experiment.

A large test file was transferred to the Ubuntu Server using SCP to generate high-volume network traffic.

---

## Combined Attack Data

### `all_attack_features_raw.tsv`

The four attack datasets were combined into one file.

An additional attack-type field was used to identify which attack scenario each connection belonged to.

The attack categories include:

```text
nmap_scan
http_burst
dns_burst
bulk_transfer
```

---

## Normal and Attack Traffic Combined

### `all_traffic_features_raw.tsv`

This file combines the normal traffic with all controlled attack traffic.

The final traffic distribution was:

| Traffic Type | Records |
|---|---:|
| Normal | 12 |
| Nmap scan | 1,002 |
| HTTP burst | 200 |
| DNS burst | 199 |
| Bulk transfer | 3 |
| **Total** | **1,416** |

A `traffic_type` field is included so that each record can be linked to its original traffic scenario.

---

## 21 Portable Features

### `gns3_all_traffic_21_features.csv`

The raw Zeek information was converted into 21 useful network features.

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

Some features came directly from Zeek.

Other features were calculated from the raw connection information.

Examples include:

- packet rate;
- source and destination traffic load;
- average packet size;
- recent connection behaviour;
- protocol;
- service; and
- connection state.

---

## 41 Model-Ready Features

### `gns3_all_traffic_41_features.csv`

The 21 portable features were passed through the same preprocessing pipeline used during machine-learning model training.

The categorical features:

```text
proto
service
state
```

were converted into numerical columns.

The process was:

```text
21 portable features
        |
        v
preprocessing
        |
        v
41 numerical model features
```

The final file contains:

```text
1,416 rows
41 model features
0 missing values
```

This file is ready to be used with the trained anomaly-detection models.

---

## Metadata

### `gns3_all_traffic_metadata.csv`

This file keeps information about the original traffic records.

It includes:

- traffic type;
- timestamp;
- source IP;
- source port;
- destination IP;
- destination port;
- normal/attack label; and
- attacker-source information.

The metadata is kept separately so that the machine-learning input contains only the required model features.
