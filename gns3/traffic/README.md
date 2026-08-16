# Traffic Scenarios

This directory contains controlled laboratory traffic scenarios.

Planned scenarios:
1. Normal web/DNS/SSH traffic
2. Legitimate backup or bulk transfer
3. Controlled Nmap reconnaissance
4. Dummy exfiltration-like transfer

# Normal Traffic Experiment

This experiment generates legitimate network traffic between the Ubuntu client and Ubuntu server for Zeek monitoring and anomaly-detection testing.

## Source

Ubuntu Client: `192.168.10.10`

## Destination

Ubuntu Server: `192.168.10.20`

## Traffic Types

- HTTP
- DNS
- SSH
- ICMP

## Packet Capture

Traffic is captured by the passive Zeek sensor using `tcpdump`.

Planned capture file:

`normal_web_dns_ssh.pcap`

## Zeek Logs

The captured traffic is processed using Zeek to generate:

- `conn.log`
- `http.log`
- `dns.log`
- `ssh.log`

## Extracted Features

The main connection-level fields include:

- Source IP
- Source port
- Destination IP
- Destination port
- Protocol
- Service
- Duration
- Originator bytes
- Responder bytes
- Originator packets
- Responder packets

## Isolation

The experiment is performed within the isolated `192.168.10.0/24` GNS3 laboratory network.
