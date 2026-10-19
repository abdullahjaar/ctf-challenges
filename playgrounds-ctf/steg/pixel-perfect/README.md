# Pixel Perfect

**Event:** Playgrounds CTF · **Category:** Steganography · **Author:** jaarabd

## Description

> Nothing stands out.

## Files

- [`pixel_perfect.png`](pixel_perfect.png) (645x378 RGB PNG, SHA-256 `1a50b549fd75cfc1b5ace2cf4d0cd5600fb4cfbee1c17aafdc60ba7dfdbe6455`)

## Solution

### 1. Rule out the obvious

The image is a photomosaic diagram. `exiftool`, `strings` and `binwalk` show nothing unusual: no metadata, no appended data, no embedded files. The description ("Nothing stands out") points at data hidden in the pixels themselves, with no visible change.

### 2. Run zsteg

`zsteg` checks common least significant bit layouts in PNG and BMP files:

```bash
zsteg pixel_perfect.png
```

```
b1,rgb,lsb,xy       .. text: "33:PlaygroundsCTF{l34s7_516n1f1c4n7}"
```

`b1,rgb,lsb,xy` means: bit 0 of each R, G and B value, read in that channel order, pixel by pixel left to right, top to bottom. The `33:` prefix is the payload length in bytes, written before the message so an extractor knows where to stop.

### 3. Without zsteg

The same extraction in Python:

```python
from PIL import Image
import numpy as np

px = np.array(Image.open("pixel_perfect.png").convert("RGB"))
data = np.packbits((px & 1).flatten()).tobytes()
length, rest = data.split(b":", 1)
print(rest[: int(length)].decode())
```

### 4. Flag

```
PlaygroundsCTF{l34s7_516n1f1c4n7}
```

The flag is leetspeak for "least significant".

## Design notes

- **Intro to LSB steganography.** Changing bit 0 of a colour value shifts it by at most 1 out of 255, which is invisible to the eye. This challenge teaches the technique and the standard tool for detecting it.
- **Fitting carrier image.** A photomosaic is an image built from many smaller images, which mirrors the idea of data hidden at a level below what the eye takes in.
- **Lossless format required.** LSB data only survives in lossless formats like PNG. Saving the same image as JPEG destroys the payload, which is why LSB challenges ship as PNG or BMP.
