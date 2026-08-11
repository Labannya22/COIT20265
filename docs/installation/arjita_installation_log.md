# Arjita Saha - Installation and Environment Setup Log

## Responsibility
GNS3 virtual network, controlled traffic generation, packet capture, Zeek monitoring and support for laboratory integration.

## Environment
- Host operating system: Windows 11 64-bit
- Installation started: 12 August 2026
- Student: Arjita Saha
- Student ID: 12297751

---

## Software Installation Record

| Software | Version | Purpose | Status | Notes |
|---|---|---|---|---|
| GNS3 Desktop | 2.2.61 | Build and manage the virtual laboratory network | Installed | GNS3 opens successfully |
| VMware Workstation Pro | 26H1 | Run the GNS3 VM and project virtual machines | Installed | Used instead of VirtualBox |
| GNS3 VM | 2.2.61 | Provide the virtualisation environment required by GNS3 | Installed/Imported | Imported into VMware Workstation |
| Wireshark | 4.6.7 | Packet capture and network troubleshooting | [Installed/Pending] | Version to be confirmed |
| Ubuntu Server | 26.04 LTS | Normal client/server and later Zeek sensor | Downloaded | VM installation still to be completed |
| Kali Linux | 2026.2 | Controlled testing machine | Downloaded | Pre-built VMware image |
| Zeek | 8.0 LTS | Network traffic monitoring and log generation | Downloaded |

---

## GNS3 Installation

GNS3 Desktop 2.2.61 was installed on the Windows host machine.

After installation, GNS3 VM was imported into VMware Workstation Pro and the GNS3 configuration was refreshed.

---

## VMware Workstation Pro

VMware Workstation Pro 26H1 was selected as the virtualisation platform.

VMware will be used to run:
- GNS3 VM
- Ubuntu virtual machines
- Kali Linux virtual machine
---

## Ubuntu

An Ubuntu Server ISO image has been downloaded.

Planned Ubuntu roles:
1. Normal client
2. Application/file server
3. Zeek monitoring sensor

The first implementation activity will use two Ubuntu virtual machines to test basic GNS3 connectivity before Kali and Zeek are added.

---

## Kali Linux

The official pre-built VMware Kali Linux image has been downloaded.

Planned role:
Controlled testing machine for authorised laboratory activities such as Nmap reconnaissance and dummy exfiltration-like traffic.

Status: Downloaded; integration with GNS3 will occur after the normal two-node network is stable.
