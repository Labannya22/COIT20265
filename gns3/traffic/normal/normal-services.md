# Normal Traffic Services

## Ubuntu Client
IP address: `192.168.10.10/24`

## Ubuntu Server
IP address: `192.168.10.20/24`

The server was configured to provide the following normal services:

### HTTP
Python HTTP server on TCP port 80.

### DNS
dnsmasq on port 53.

Local DNS record:

`app.lab -> 192.168.10.20`

### SSH
OpenSSH server on TCP port 22.

## Normal Traffic Generated

The Ubuntu client generated:

- HTTP GET requests
- DNS queries
- SSH sessions
- ICMP connectivity traffic

The traffic was captured passively by the Zeek sensor.
