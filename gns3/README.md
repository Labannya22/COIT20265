# GNS3 Virtual Network and Traffic Generation Laboratory

This directory contains the controlled virtual-network laboratory developed for the **COIT20265 Network Anomaly Detection Project**.

The laboratory is designed to generate reproducible normal and controlled anomalous network traffic, capture PCAP files, generate Zeek logs, and prepare network-flow information for later anomaly-detection testing.

---

## Final Laboratory Topology

<p align="center">
  <img src="screenshots/final_connecting_from_gns3.png"
       alt="Final four-role GNS3 topology"
       width="850">
</p>

**Figure 1. Final four-role GNS3 laboratory topology.**

The laboratory contains four main roles:

| Role | System | Address / Mode | Purpose |
|---|---|---|---|
| Normal Client | Ubuntu Client | `192.168.10.10/24` | Generates legitimate network traffic |
| Application Server | Ubuntu Server | `192.168.10.20/24` | Provides HTTP, DNS and SSH services |
| Controlled Attacker | Kali Linux | `192.168.10.30/24` | Used for authorised controlled testing |
| Monitoring Sensor | Zeek Sensor | Passive monitoring interface | Captures and analyses network traffic |

---

## Network

**Laboratory subnet:** `192.168.10.0/24`

During controlled experiments:

- no default gateway is configured;
- no GNS3 NAT node is connected;
- no GNS3 Cloud node is connected;
- no external router is connected.

This keeps controlled experimental traffic inside the authorised laboratory.

---

## Technologies Used

- GNS3
- VMware Workstation
- Ubuntu Server
- Ubuntu Client
- Kali Linux
- Zeek 8.0.9
- tcpdump
- Wireshark
- dnsmasq
- OpenSSH
- Python HTTP server

---

## Current Progress

### Laboratory Setup

- [x] GNS3 installed and configured
- [x] VMware virtual machines integrated with GNS3
- [x] Additional VMnet networking configured
- [x] Four-role topology created
- [x] Ubuntu client added
- [x] Ubuntu server added
- [x] Kali attacker added to topology
- [x] Zeek sensor added
- [x] Ethernet Hub configured for passive monitoring

### Network Configuration

- [x] `192.168.10.0/24` laboratory network configured
- [x] Ubuntu client configured as `192.168.10.10`
- [x] Ubuntu server configured as `192.168.10.20`
- [x] Zeek passive monitoring interface configured
- [x] Client/server connectivity verified
- [x] VMware DHCP contamination identified and corrected

### Zeek Monitoring

- [x] Zeek 8.0.9 installed
- [x] Zeek executable path configured
- [x] Passive interface `ens33` configured
- [x] Passive packet visibility verified with tcpdump
- [x] PCAP capture completed
- [x] PCAP successfully processed using Zeek
- [x] Protocol logs generated

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
- [x] Zeek normal traffic logs inspected
- [x] Connection features extracted
- [x] Experimental files exported from Zeek VM

### Remaining Work

- [ ] Legitimate file-transfer / backup traffic
- [ ] Controlled Nmap reconnaissance
- [ ] Controlled bulk/exfiltration-like transfer
- [ ] Separate PCAPs for attack scenarios
- [ ] Complete Zeek-to-model feature mapping
- [ ] Integrate practical traffic with anomaly-detection pipeline

---

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
       |
       v
conn_features.tsv
       |
       v
Future anomaly-detection pipeline
