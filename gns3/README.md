# GNS3 Virtual Network and Traffic Generation Laboratory

This directory contains the controlled virtual-network laboratory developed for the **COIT20265 Network Anomaly Detection Project**.

The laboratory is designed to generate reproducible normal and controlled anomalous network traffic, capture PCAP files, generate Zeek logs, and prepare connection-level information for later anomaly-detection testing.

---

## Final Laboratory Topology

<p align="center">
  <img src="screenshots/final_connecting_from_gns3.png"
       alt="Final four-role GNS3 topology"
       width="900">
</p>

**Figure 1. Final four-role GNS3 laboratory topology.**

The laboratory contains four main roles:

| Role | System | Address / Mode | Purpose |
|---|---|---|---|
| Normal Client | Ubuntu Client | `192.168.10.10/24` | Generates legitimate network traffic |
| Application/File Server | Ubuntu Server | `192.168.10.20/24` | Provides normal network services |
| Controlled Attacker | Kali Linux | `192.168.10.30/24` | Used for authorised controlled testing |
| Monitoring Sensor | Zeek Sensor | Passive interface | Captures and analyses network traffic |

All systems are connected through a GNS3 Ethernet Hub.

---

## Laboratory Network

**Network:** `192.168.10.0/24`

**Subnet mask:** `255.255.255.0`

During final controlled experiments:

- no default gateway is configured;
- no GNS3 NAT node is connected;
- no GNS3 Cloud node is connected;
- no external router is connected.

This design keeps controlled experimental traffic inside the authorised laboratory environment.

Temporary external connectivity was used only when required for software installation and was removed before the final controlled traffic capture.

---

## Technologies Used

- GNS3
- VMware Workstation
- Ubuntu 26.04
- Kali Linux
- Zeek 8.0.9
- tcpdump
- Wireshark
- dnsmasq
- OpenSSH
- Python HTTP server

---

## Current Progress

### Environment and Topology

- [x] GNS3 installed and configured
- [x] VMware virtual machines integrated with GNS3
- [x] Four-role topology designed
- [x] Ubuntu client added
- [x] Ubuntu server added
- [x] Kali attacker added
- [x] Zeek sensor added
- [x] Ethernet Hub used for passive traffic observation

### Network Configuration

- [x] `192.168.10.0/24` laboratory network configured
- [x] Ubuntu client configured as `192.168.10.10`
- [x] Ubuntu server configured as `192.168.10.20`
- [x] Kali attacker configured as `192.168.10.30`
- [x] Client/server connectivity verified
- [x] Zeek passive monitoring interface configured
- [x] VMware DHCP contamination identified and corrected
- [x] Final capture restricted to the authorised laboratory subnet

### Zeek Monitoring

- [x] Zeek 8.0.9 installed
- [x] Zeek executable path configured
- [x] Passive interface `ens33` configured
- [x] Packet visibility verified using tcpdump
- [x] Normal traffic PCAP captured
- [x] PCAP processed using Zeek
- [x] Zeek protocol logs generated
- [x] Connection fields extracted

### Normal Traffic

- [x] HTTP service configured
- [x] HTTP GET requests generated
- [x] DNS service configured
- [x] `app.lab` DNS record created
- [x] DNS queries generated
- [x] SSH service configured
- [x] SSH sessions generated
- [x] ICMP connectivity traffic generated
- [x] Clean normal PCAP captured
- [x] Zeek logs inspected
- [x] `conn_features.tsv` generated
- [x] PCAP and log files exported to the host computer
- [x] Experimental files uploaded to GitHub

### Completed Attack and Integration Work

- [x] Controlled Nmap reconnaissance
- [x] Controlled bulk/exfiltration-like transfer
- [x] HTTP request burst
- [x] DNS query burst
- [x] Separate PCAPs and Zeek logs generated
- [x] Attack connection fields extracted
- [x] Normal and attack traffic combined
- [x] Zeek-to-model feature mapping completed
- [x] 21 portable network features generated
- [x] 41 model-ready numerical features generated
- [x] External physical-laptop connectivity configured
- [x] External Nmap validation completed
- [ ] Final model testing using laboratory traffic
- [ ] Final dashboard integration

## Current Normal-Traffic Pipeline

```text
Ubuntu Client
192.168.10.10
       |
       | HTTP / DNS / SSH / ICMP
       v
Ubuntu Server
192.168.10.20
       |
       v
GNS3 Ethernet Hub
       |
       v
Zeek Sensor
Passive Monitoring
       |
       v
tcpdump
       |
       v
normal_web_dns_ssh.pcap
       |
       v
Zeek
       |
       +---- conn.log
       +---- http.log
       +---- dns.log
       +---- ssh.log
       +---- files.log
       +---- packet_filter.log
       |
       v
conn_features.tsv
       |
       v
Future preprocessing and anomaly-detection pipeline

```

## Controlled Attack Traffic

After normal traffic generation was completed, four controlled attack
scenarios were created against the Ubuntu server.

All attack testing was performed only against systems belonging to the
authorised laboratory environment.

The four scenarios were:

1. Nmap port scan
2. Bulk file transfer
3. HTTP request burst
4. DNS query burst

---

### Nmap Port Scan

The Kali attacker at `192.168.10.30` performed a controlled Nmap scan
against the Ubuntu server at `192.168.10.20`.

<p align="center">
  <img src="screenshots/kali1.png"
       alt="Controlled Nmap scan from Kali"
       width="700">
</p>

**Figure 2. Controlled Nmap scan generated from the Kali attacker.**

Zeek captured connections from the Kali attacker to many different
destination ports on the Ubuntu server.

<p align="center">
  <img src="screenshots/kali2.png"
       alt="Nmap traffic observed by Zeek"
       width="850">
</p>

**Figure 3. Nmap scanning behaviour observed in the Zeek connection data.**

---

### Bulk File Transfer

A large test file was created on Kali and transferred to the Ubuntu
server using SCP.

The purpose of this test was to generate high-volume transfer traffic
that could later be analysed by the anomaly-detection models.

<p align="center">
  <img src="screenshots/kali3.png"
       alt="Bulk transfer test from Kali"
       width="700">
</p>

**Figure 4. Large test file created and transferred from Kali.**

The traffic was captured and processed using Zeek. The connection
information showed a large amount of transferred data over SSH.

<p align="center">
  <img src="screenshots/kali4.png"
       alt="Bulk transfer captured by Zeek"
       width="900">
</p>

**Figure 5. Bulk-transfer traffic recorded and analysed using Zeek.**

---

### HTTP Request Burst

A repeated HTTP request test was generated from Kali against the
web service running on the Ubuntu server.

Zeek generated `http.log` and recorded repeated successful HTTP GET
requests.

<p align="center">
  <img src="screenshots/kali5.png"
       alt="HTTP burst captured by Zeek"
       width="900">
</p>

**Figure 6. Repeated HTTP GET requests observed in the Zeek HTTP log.**

---

### DNS Query Burst

A DNS service was configured on the Ubuntu server using the test
domain `app.lab`.

The Kali attacker first confirmed that the DNS service was working
and then generated repeated DNS queries.

<p align="center">
  <img src="screenshots/kali6.png"
       alt="DNS burst generated from Kali"
       width="700">
</p>

**Figure 7. DNS queries generated from the Kali attacker.**

Zeek recorded the repeated DNS queries in `dns.log`.

<p align="center">
  <img src="screenshots/kali7.png"
       alt="DNS burst captured by Zeek"
       width="850">
</p>

**Figure 8. Repeated DNS queries observed in the Zeek DNS log.**

---

## Zeek Feature Extraction

For each traffic scenario, selected connection information was extracted
from the Zeek `conn.log`.

The main raw Zeek fields were:

- timestamp;
- source IP address;
- source port;
- destination IP address;
- destination port;
- protocol;
- service;
- duration;
- source IP bytes;
- destination IP bytes;
- source packet count;
- destination packet count; and
- connection state.

These 13 fields were used as the source information for later feature
engineering.

<p align="center">
  <img src="screenshots/kali9.png"
       alt="Zeek raw feature extraction"
       width="900">
</p>

**Figure 9. Extraction of connection information from Zeek logs.**

The generated feature files for the different attack scenarios were
checked before being combined.

<p align="center">
  <img src="screenshots/kali10.png"
       alt="Attack feature files"
       width="900">
</p>

**Figure 10. Verification of the raw Zeek feature files.**

---

## Combined Attack Dataset

The four attack datasets were combined into one file and an
`attack_type` field was added so that each record could be linked to
its original traffic scenario.

<p align="center">
  <img src="screenshots/kali11.png"
       alt="Combined attack dataset"
       width="900">
</p>

**Figure 11. Attack records combined into a single dataset.**

---

## Normal and Attack Traffic Integration

The earlier normal traffic was regenerated using the same Zeek fields
as the attack data.

<p align="center">
  <img src="screenshots/kali13.png"
       alt="Normal traffic feature extraction"
       width="900">
</p>

**Figure 12. Normal traffic converted into the same raw feature format.**

Normal and attack records were then combined into the final laboratory
traffic dataset.

The final dataset contained:

| Traffic Type | Records |
|---|---:|
| Normal | 12 |
| Nmap scan | 1,002 |
| HTTP burst | 200 |
| DNS burst | 199 |
| Bulk transfer | 3 |
| **Total** | **1,416** |

<p align="center">
  <img src="screenshots/kali14.png"
       alt="Final combined traffic dataset"
       width="900">
</p>

**Figure 13. Final normal and attack traffic dataset.**

---

## Feature Preparation for Machine Learning

The raw Zeek information was not used directly by the machine-learning
models.

The laboratory traffic followed this preparation process:

```text
13 raw Zeek fields
        |
        v
Feature engineering
        |
        v
21 portable network features
        |
        v
Existing preprocessing pipeline
        |
        v
41 numerical model features
