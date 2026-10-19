# Silent Document

**Event:** Playgrounds CTF · **Category:** Steganography · **Author:** jaarabd

## Description

> This PDF doesn't say much at first glance, but it speaks to those who look closer. Some secrets hide on the surface, others lie beneath. Find them.

## Files

- [`steganography.pdf`](steganography.pdf) (45 KB, SHA-256 `07b2d775d0504e26a04a49be0c06380e4f52fce7ac0f7c73599b1ee8383d4b39`)

## Solution

The flag is split in two, matching the description: one half "on the surface" of the page, one half "beneath" it inside the file structure.

### 1. Surface: hidden text

Opened in a viewer, the PDF is a two page essay about steganography. Extracting the text layer shows a line that is not visible on the page:

```bash
pdftotext steganography.pdf - | grep -i playgrounds
```

```
layer of information. PlaygroundsCTF{what_you_read
```

It is rendered in white (`#FFFFFF`) on the white page, at the end of the first paragraph. Selecting all text in a viewer (`Ctrl+A`) also highlights it.

```bash
python3 -c "
import pymupdf
for b in pymupdf.open('steganography.pdf')[0].get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            if 'Playgrounds' in s['text']: print(s['text'], hex(s['color']))
"
# PlaygroundsCTF{what_you_read  0xffffff
```

### 2. Beneath: embedded file

`pdfinfo` reports nothing unusual, but the document catalog references an `/EmbeddedFiles` name tree:

```bash
strings steganography.pdf | grep EmbeddedFiles
pdfdetach -list steganography.pdf
```

```
1 embedded files
1: part2.txt
```

```bash
pdfdetach -saveall steganography.pdf
cat part2.txt
# _isnt_all_there_is}
```

### 3. Flag

```
PlaygroundsCTF{what_you_read_isnt_all_there_is}
```

## Design notes

- **Two layers, two techniques.** The first half tests the presentation layer (what is rendered vs. what is in the text stream). The second half tests the file structure (objects a viewer never shows). The description hints at both: "on the surface" and "beneath".
- **The essay is part of the hint.** The document itself mentions that PDFs can hide content "in metadata fields, embedded objects, or unused streams", which points players toward the second half once they have found the first.
- **Beginner friendly on purpose.** Both halves fall to standard poppler tools (`pdftotext`, `pdfdetach`), so the challenge teaches the PDF triage workflow rather than requiring custom tooling.
