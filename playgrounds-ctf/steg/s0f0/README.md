# S0F0

**Event:** Playgrounds CTF · **Category:** Steganography · **Author:** jaarabd

## Description

> Check the limits.

## Files

- [`s0f0.jpg`](s0f0.jpg) (525x175 JPEG, SHA-256 `33133a45ed34268de584ce4ade31358e10cdd698a4ff9236fd38a9927fed7109`)

## Solution

### 1. Notice the crop

The image shows the top of a dog's head, cut off just below the nose. A 525x175 frame is an unusual 3:1 aspect ratio for a photo, and the challenge name is the hint: `SOF0` is the JPEG Start of Frame (baseline) marker, which stores the image dimensions.

### 2. Read the SOF0 header

SOF0 starts with `FF C0`. Its layout:

| Offset from marker | Size | Field |
| :-- | :-- | :-- |
| +2 | 2 | Segment length |
| +4 | 1 | Sample precision |
| +5 | 2 | **Height** |
| +7 | 2 | Width |
| +9 | 1 | Number of components |

```bash
xxd s0f0.jpg | grep -i "ffc0"
```

```
FF C0 00 11 08 00 AF 02 0D 03
                 ^^^^^ ^^^^^
            height=175 width=525
```

### 3. Increase the height

The compressed scan data after the header still contains every row of the original image. Decoders only render as many rows as the header says, so raising the height brings the hidden part back. Patch `00 AF` (175) to `01 5E` (350) in a hex editor, or:

```bash
python3 solve.py s0f0.jpg 350
```

[`solve.py`](solve.py) finds the `FF C0` marker and rewrites the two height bytes.

Any value that is too large still works: the decoder fills the rows past the end of the data with grey. The true height is the point where the grey begins, around 350.

### 4. Flag

The full image shows the rest of the dog, with the flag written in the bottom right corner:

```
PlaygroundsCTF{cr0pp3d_bu7_n07_g0n3}
```

## Design notes

- **Header vs. data.** The challenge teaches that image dimensions are just metadata. Editing the header changes what is displayed without touching the pixel data, so "cropped" content can still be in the file.
- **Visual hint.** Cropping the photo just below the dog's nose makes the image look obviously incomplete, which nudges players to ask where the rest went.
- **No tooling shortcut.** `strings`, `exiftool`, `binwalk` and LSB tools find nothing, because the flag is drawn in the pixels of the cut off rows. The player has to understand the JPEG structure and edit it by hand.
- **Same trick in other formats.** PNG stores dimensions in the `IHDR` chunk, but it is protected by a CRC, so the PNG version of this challenge also requires fixing or brute forcing the checksum. JPEG has no checksum, which keeps this one beginner friendly.
