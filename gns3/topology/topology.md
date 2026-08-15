# Four-Role GNS3 Topology

This document describes the four-role GNS3 laboratory topology used for the COIT20265 Network Anomaly Detection project.

The laboratory is designed to generate normal and controlled anomalous network traffic inside an isolated environment while allowing a dedicated Zeek sensor to passively monitor the communication.

---

## Topology

```text
                         Ubuntu-client
                       192.168.10.10
                              |
                              |
                              |
Kali-attacker  -----------   Hub1   -----------  Ubuntu-server
192.168.10.30                                  192.168.10.20
                              |
                              |
                              |
                         Zeek-sensor
                       Passive Monitor
```

All four systems are connected to the same isolated GNS3 Ethernet Hub.

---

## Network Information

**Network:** `192.168.10.0/24`

**Subnet Mask:** `255.255.255.0`

**Default Gateway:** None

The laboratory does not use a NAT node, Cloud node, or external router during controlled experiments.

---

## Roles

### Ubuntu Client

The Ubuntu client acts as the normal user workstation and generates legitimate network activity.

**Hostname:** `Ubuntu-client`

**IP address:** `192.168.10.10/24`

Normal traffic generated from this machine includes:

* HTTP
* DNS
* SSH
* ICMP/ping
* File-access traffic
* Controlled file-transfer activity

The Ubuntu client primarily communicates with the Ubuntu server to create normal network behaviour for capture and analysis.

---

### Ubuntu Server

The Ubuntu server acts as the application and file server within the laboratory.

**Hostname:** `Ubuntu-server`

**IP address:** `192.168.10.20/24`

The server provides services used to generate normal network communication, including:

* HTTP
* DNS
* SSH
* File-transfer services

The server acts as the main destination for legitimate client traffic and controlled test traffic.

---

### Kali Linux

Kali Linux acts as the controlled attacker within the isolated laboratory environment.

**Hostname:** `Kali-attacker`

**IP address:** `192.168.10.30/24`

It is used only for authorised project testing.

Planned controlled activities include:

* Nmap port scanning
* Controlled network reconnaissance
* Controlled bulk file-transfer activity

All testing is restricted to the private GNS3 laboratory network.

No scanning or attack traffic is intentionally directed toward external systems.

---

### Zeek Sensor

The Zeek sensor acts as the passive network monitoring system.

**Hostname:** `Zeek-sensor`

**Monitoring mode:** Passive

The monitoring interface does not require a normal host IP address for packet observation.

The Zeek sensor observes traffic passing through the laboratory segment and generates network metadata and protocol logs.

Important Zeek logs include:

* `conn.log`
* `http.log`
* `dns.log`
* `ssh.log`

The connection logs provide information that can later be used for network anomaly analysis.

Relevant fields include:

* `id.orig_h` — originator/source IP address
* `id.orig_p` — originator/source port
* `id.resp_h` — responder/destination IP address
* `id.resp_p` — responder/destination port
* `proto` — transport protocol
* `service` — detected application service
* `duration` — connection duration
* `orig_bytes` — bytes sent by the originator
* `resp_bytes` — bytes sent by the responder
* `orig_pkts` — packets sent by the originator
* `resp_pkts` — packets sent by the responder

---

## Monitoring Design

A GNS3 Ethernet Hub is used as the central connection point for the laboratory.

The following systems are connected to the hub:

* Ubuntu Client
* Ubuntu Server
* Kali Attacker
* Zeek Sensor

The hub allows the Zeek monitoring interface to observe traffic generated between the other systems.

This enables the Zeek sensor to passively monitor:

* Ubuntu-client → Ubuntu-server traffic
* Ubuntu-server → Ubuntu-client traffic
* Kali-attacker → Ubuntu-server traffic
* Ubuntu-server → Kali-attacker traffic
* Normal protocol activity
* Controlled anomalous activity

The Zeek sensor does not need to act as the source or destination of the monitored communication.

---

## Normal Traffic

Normal traffic will primarily be generated between:

```text
Ubuntu-client
      |
      v
Ubuntu-server
```

Normal traffic types include:

* HTTP web requests
* DNS queries
* SSH sessions
* ICMP/ping
* Normal file transfers

These captures are used to represent legitimate network behaviour.

---

## Controlled Test Traffic

Controlled anomalous traffic will primarily be generated using:

```text
Kali-attacker
      |
      v
Ubuntu-server
```

Planned activities include:

* Nmap port scanning
* Controlled bulk file-transfer activity

These tests are performed only inside the isolated laboratory environment.

---

## Packet Capture

Traffic observed by the Zeek sensor will be captured into PCAP files for reproducible analysis.

Planned captures include:

```text
normal_web_dns_ssh.pcap
nmap_scan.pcap
bulk_transfer.pcap
```

The captured PCAP files can then be processed using Zeek to generate protocol and connection logs.

---

## Zeek Log Generation

The normal traffic capture is expected to generate logs such as:

```text
conn.log
http.log
dns.log
ssh.log
```

`conn.log` will be used as the primary connection-level record because it contains network-flow information such as:

* source and destination addresses
* source and destination ports
* protocol
* detected service
* connection duration
* transmitted bytes
* packet counts

These fields can later be mapped to the feature-processing and anomaly-detection stages of the project.

---

## Network Isolation

The laboratory network uses the private subnet:

`192.168.10.0/24`

During controlled experiments:

* No default gateway is configured.
* No GNS3 NAT node is connected.
* No GNS3 Cloud node is connected.
* No external router is connected.
* Controlled attack traffic remains inside the laboratory network.

External connectivity tests will also be performed to verify that the experimental machines cannot intentionally reach unauthorised external systems.

This design helps ensure that all testing is restricted to the authorised project environment.

---

## Topology Screenshot

The screenshot of the implemented GNS3 topology is stored in this directory as:

`four_role_topology.png`

Expected folder structure:

```text
gns3/
└── topology/
    ├── topology.md
    └── four_role_topology.png
```

---

## Implementation Purpose

This topology provides the practical laboratory environment required to validate the network anomaly detection system.

It allows the project to:

1. Generate controlled normal network traffic.
2. Generate controlled anomalous traffic.
3. Capture network packets.
4. Produce Zeek logs.
5. Extract network-flow information.
6. Evaluate anomaly-detection models using practical laboratory traffic.
7. Demonstrate an isolated and reproducible testing environment.
