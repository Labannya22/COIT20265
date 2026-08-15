# GNS3 Laboratory
Planned contents:
- topology files
- IP addressing information
- configuration notes
- screenshots
- troubleshooting evidence

# GNS3 Laboratory Environment 
This folder contains the controlled GNS3 laboratory environment developed for the COIT20265 Network Anomaly Detection project. 

## Laboratory Roles The environment contains four main roles: 
1. Ubuntu Client — generates normal network traffic.
2.  Ubuntu Server — provides application and file services.
3.  Kali Linux — generates controlled anomalous/test traffic.
4.  Zeek Sensor — passively monitors network traffic and produces network logs.

## Network 
The laboratory uses the private subnet: 
192.168.10.0/24 

No default gateway is configured during experiments so that controlled traffic cannot reach external systems. 

## Main Components 
- VMware Workstation 
- GNS3
- Ubuntu Client
- Ubuntu Server
- Kali Linux
-  Zeek
-  Wireshark/tcpdump

## Planned Traffic Normal traffic: 
- HTTP
- DNS
- SSH


Controlled test traffic: 
- Nmap port scanning
-  Bulk file transfer


## Monitoring 
The Zeek sensor observes traffic from the isolated GNS3 network and produces logs such as: 
- conn.log
- http.log
- dns.log
- ssh.log
