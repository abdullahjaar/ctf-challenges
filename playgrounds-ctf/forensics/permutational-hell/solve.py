#!/usr/bin/env python3
# Usage: python3 solve.py final_challenge.pcap
import sys
from scapy.all import rdpcap, TCP, Raw

pkts = rdpcap(sys.argv[1])
chunks = [p for p in pkts if TCP in p and Raw in p and p[TCP].sport == 4444]
chunks.sort(key=lambda p: p[TCP].seq)

hexstream = b"".join(bytes(p[Raw].load) for p in chunks).replace(b"\n", b"")
with open("recovered.png", "wb") as f:
    f.write(bytes.fromhex(hexstream.decode()))
print(f"[+] {len(chunks)} segments reordered, wrote recovered.png")
