# GNS3 IP Addressing Plan

| Role | Hostname | IP Address | Subnet Mask | Default Gateway |
|---|---|---|---|---|
| Normal Client | Ubuntu-client | 192.168.10.10 | 255.255.255.0 | None |
| Application/File Server | Ubuntu-server | 192.168.10.20 | 255.255.255.0 | None |
| Controlled Attacker | Kali-attacker | 192.168.10.30 | 255.255.255.0 | None |
| Monitoring Sensor | Zeek-sensor | Passive monitoring interface | N/A | None |

## Network

**Network:** `192.168.10.0/24`

## Isolation

No default gateway, NAT node, Cloud node, or external router is used during controlled experiments.

This ensures that generated test traffic remains inside the isolated GNS3 laboratory environment and cannot intentionally reach external or unauthorised systems.
