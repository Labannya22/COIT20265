# GNS3 and Zeek Practical Network Testbed

This directory contains the practical network environment developed for the project.

The laboratory was designed to generate controlled normal and anomalous network traffic, capture the traffic using Zeek, convert it into the feature format required by the trained machine-learning models, and evaluate model behaviour using practical network data.

## Laboratory Environment

The main GNS3 laboratory contains four roles:

| Role | Hostname | IP / Mode | Purpose |
|---|---|---|---|
| Normal Client | Ubuntu-client | 192.168.10.10/24 | Generates normal traffic |
| Application Server | Ubuntu-server | 192.168.10.20/24 | Provides HTTP, DNS and SSH services |
| Controlled Attacker | Kali-attacker | 192.168.10.30/24 | Generates controlled anomalous traffic |
| Monitoring Sensor | Zeek-sensor | Passive ens33 | Captures and analyses traffic |

All systems are connected through a GNS3 Ethernet hub on the isolated network: 192.168.10.0/24

During the internal experiments, no default gateway, NAT node or external router was used.

## Normal Traffic

The following normal traffic was generated between the Ubuntu client and Ubuntu server:

- HTTP GET requests
- DNS queries
- SSH sessions
- ICMP traffic

## Controlled Anomalous Traffic

The following authorised anomalous scenarios were generated from the Kali attacker:

- Nmap reconnaissance
- HTTP request burst
- DNS query burst
- Bulk file transfer

## Internal Dataset

The final internal Zeek dataset contains:

| Traffic Type | Records |
|---|---:|
| Normal | 12 |
| Nmap scan | 1,002 |
| HTTP burst | 200 |
| DNS burst | 199 |
| Bulk transfer | 3 |
| Total | 1,416 |

## Traffic Capture

Traffic was captured using tcpdump and analysed using Zeek.

Zeek generated structured logs including:

- conn.log
- http.log
- dns.log
- ssh.log
- files.log
- packet_filter.log

Connection-level information was then extracted for machine-learning preprocessing.

## Data Processing

The practical traffic followed this processing pipeline:

<p align="center">
  <img src="screenshots/gns3_feature_processing_flow.png"
       alt="GNS3 and Zeek feature-processing workflow"
       width="700">
</p>

**Figure. GNS3 and Zeek feature-processing workflow.**


The final model-ready dataset contains:

- 1,416 records
- 41 numerical model features
- 0 missing values

The same preprocessing pipeline used during model development was reused for the practical traffic. No new scaler or encoder was fitted to the GNS3 test data.

## External Physical-Laptop Validation

Additional validation was performed using Kali Linux running on a separate physical laptop.

The external Kali address was: 192.168.4.52

The target Ubuntu server remained: 192.168.10.20

Routing was configured through the Windows host so that traffic from the external network could reach the GNS3 environment.

A controlled external Nmap scan was captured and analysed by Zeek. Approximately 1,004 Zeek connection records were extracted.

This experiment demonstrated that the monitoring workflow could also capture traffic originating outside the original internal virtual-machine environment.


## Scope

All attack traffic was generated only against systems created for the authorised university project laboratory.

No unauthorised or public systems were scanned or attacked.

The practical dataset is relatively small and contains substantially more attack traffic than normal traffic. Therefore, it is used as a proof-of-concept practical evaluation rather than a production network baseline.
