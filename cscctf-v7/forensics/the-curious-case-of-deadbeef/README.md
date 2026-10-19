# The Curious Case of DEADBEEF

**Event:** CSCCTF v7 · **Category:** Forensics · **Points:** 500, dynamic · **Author:** jaarabd

## Description

> A collection of recovered files has been provided from a suspicious compromise. Follow the evidence and uncover the hidden secret.

## Files

- [`ftp.pcap`](ftp.pcap)
- [`challenge_1.pcap`](challenge_1.pcap)
- [`dropper`](dropper) (ELF 64-bit x86-64, stripped)
- [`vault.enc`](vault.enc) (50 MB)

## Solution

The flag is inside an encrypted disk image. Decrypting it needs four pieces of information, each hidden in a different artifact:

| Piece | Source |
| :-- | :-- |
| Passphrase | GitHub repo found through decrypted HTTPS traffic |
| Salt | C2 traffic in `challenge_1.pcap` |
| Iteration count | `dropper` binary |
| Algorithm | `dropper` binary |

### 1. Recover the TLS keys from FTP

Open `ftp.pcap` in Wireshark, follow the FTP data stream (`Follow > TCP Stream`), and save the transferred file as `sslkeys.log`. It is a TLS key log file.

### 2. Decrypt the HTTPS traffic

Open `challenge_1.pcap` and load the key log under `Edit > Preferences > Protocols > TLS > (Pre)-Master-Secret log filename`. The HTTPS traffic decrypts and shows several HTTP GET requests to numbered endpoints.

Follow each stream in order, collect the base64 chunks, join them and decode. The result is a PowerShell script full of fake news style comments.

### 3. Find the GitHub repo

Short string variables scattered between the comments concatenate into a URL:

```
https://github.com/phantom-build/build-utils
```

The `main` branch looks clean. The `dev-legacy` branch has a single suspicious commit that adds `utils/decoder.py`.

### 4. Deobfuscate the passphrase

`decoder.py` hides the passphrase behind several layers: hex to string, base64 decode, ROT13 and string reversal. Run the file or trace the layers by hand to recover the passphrase.

### 5. Reverse the dropper

Load `dropper` into Ghidra and find the PBKDF2 call. It uses a hardcoded iteration count of `0x539` (**1337**), and the surrounding code confirms **AES-256-CBC** as the cipher.

### 6. Get the salt from the C2 traffic

Back in `challenge_1.pcap`, filter for the C2 channel:

```
tcp.port == 4444
```

The server sends:

```
salt is: 4445414442454546
```

As ASCII the salt is `DEADBEEF`, which is where the challenge gets its name.

### 7. Decrypt and mount the vault

With all four pieces:

| Parameter | Value |
| :-- | :-- |
| Algorithm | AES-256-CBC |
| KDF | PBKDF2, 1337 iterations |
| Salt | `4445414442454546` |
| Passphrase | from `decoder.py` |

Decrypt `vault.enc` with `openssl` using these parameters, mount the resulting disk image, and read the flag:

```bash
sudo mount -o loop vault.img /mnt/vault
cat /mnt/vault/home/jaar/.config/cache/sys/flag.txt
```

### 8. Flag

```
CSCCTF{3xf1l_w4s_r1ght_th3r3_4ll_4l0ng}
```

## Design notes

- **Every artifact matters.** Each handed out file supplies one decryption parameter, so a player who skips any of them cannot finish. The challenge tests whether players can keep track of evidence across network captures, a binary and an external source.
- **Chained network forensics.** The key log is hidden in plaintext FTP, and it unlocks the HTTPS capture. This mirrors a real investigation, where one weak protocol often exposes a stronger one.
- **Realistic attacker tradecraft.** Chunked exfiltration over numbered endpoints, a PowerShell stager buried in noise comments, a payload staged on an innocent looking GitHub branch, and a C2 channel on port 4444 are all patterns seen in real intrusions.
- **Reversing for parameters, not the flag.** The dropper only gives away the KDF settings. Players have to understand what the code does rather than search it for strings.
- **Hidden path.** The flag sits deep in a dot directory (`.config/cache/sys/`) inside the mounted image, so players who only list the top level miss it.
