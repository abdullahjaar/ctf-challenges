# Permutational Hell

**Event:** Playgrounds CTF · **Category:** Forensics · **Author:** jaarabd

## Description

> A network capture contains streams with something hidden. Unfortunately the packets were shuffled and nothing reassembles correctly. Can you recover the original file?
>
> Note: wrap the flag with `PlaygroundsCTF{}`

## Files

- [`final_challenge.pcap`](final_challenge.pcap) (325 KB, SHA-256 `cf1861c28b94083959c65c778b04b2cfafd8ce069b5071334a79af05f9e2c0c0`)

## Solution

### 1. Triage the capture

The capture holds 285 packets: DNS, ICMP echo requests, random TCP noise, and a lot of UDP traffic from `5.5.5.5:9999`. The UDP traffic is all decoys:

| Payload | Decoded |
| :-- | :-- |
| `PlaygroundsCTF{this_is_not_the_flag}` | fake flag |
| `FLAG{nope_not_here}`, `PCAP_STEG_FAKE_FLAG` | fake flags |
| `73 74 69 6c 6c 20 6e 6f 74 ...` | hex: `still not here,try harder` |
| `-. --- .--. . / ... - .. .-.. .-..` | Morse: `NOPE STILL NOT THIS` |

The real data is a single TCP flow, `10.0.0.5:4444 -> 10.0.0.10:80`. It has 10 segments, each with a 30,639 byte payload of hex characters split by newlines.

```bash
tshark -r final_challenge.pcap -Y "tcp.srcport==4444" -T fields -e frame.number -e tcp.seq_raw -e tcp.len
```

### 2. Notice why Follow Stream fails

The segments are out of order in the capture, and their sequence numbers are `0, 1000, 2000, ... 9000` even though each one carries 30,639 bytes. Real sequence numbers would advance by the payload length, so Wireshark's reassembly sees overlaps and gaps and produces garbage. The sequence number is really a chunk index.

Only the segment with `seq=0` starts with `89504e47`, the PNG magic in hex, which confirms both the file type and the ordering key.

### 3. Reorder and decode

Sort the segments by sequence number, concatenate the payloads, strip the newlines, and hex decode:

```bash
pip install scapy
python3 solve.py final_challenge.pcap
```

[`solve.py`](solve.py):

```python
chunks = [p for p in pkts if TCP in p and Raw in p and p[TCP].sport == 4444]
chunks.sort(key=lambda p: p[TCP].seq)
hexstream = b"".join(bytes(p[Raw].load) for p in chunks).replace(b"\n", b"")
open("recovered.png", "wb").write(bytes.fromhex(hexstream.decode()))
```

The result is a 1219x661 PNG with the flag handwritten on the left side.

### 4. Flag

```
PlaygroundsCTF{follow_stream_find_th3_dream}
```

## Design notes

- **Sequence numbers as the puzzle.** Shuffling packets alone is not enough, because Wireshark reorders by sequence number automatically. Setting the sequence numbers to chunk indices instead of byte offsets breaks automatic reassembly, so the player has to understand what the field is supposed to mean and rebuild the stream by hand.
- **Hex encoding plus newlines.** The image is sent as hex text with line breaks, so carving tools like `binwalk` or `foremost` find no PNG in the raw capture.
- **Decoys test different habits.** Plaintext fake flags catch players who run `strings | grep`, and the hex and Morse decoys reward decoding without leading anywhere. The real flow is the only one with a consistent, large payload size.
- **Flag inside an image.** The flag is handwritten in the picture rather than stored as text, so no string search on the decoded file reveals it.
