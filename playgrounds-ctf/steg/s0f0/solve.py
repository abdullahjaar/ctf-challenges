#!/usr/bin/env python3
# Usage: python3 solve.py s0f0.jpg [new_height]
import sys

src = sys.argv[1]
new_h = int(sys.argv[2]) if len(sys.argv) > 2 else 350

data = bytearray(open(src, "rb").read())
sof = data.find(b"\xff\xc0")                    # SOF0 marker
h = int.from_bytes(data[sof + 5:sof + 7], "big")
w = int.from_bytes(data[sof + 7:sof + 9], "big")
print(f"[+] SOF0 at {sof:#x}: {w}x{h}")

data[sof + 5:sof + 7] = new_h.to_bytes(2, "big")
open("fixed.jpg", "wb").write(data)
print(f"[+] height patched to {new_h}, wrote fixed.jpg")
