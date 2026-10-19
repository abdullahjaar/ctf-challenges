# Crypto Heist

**Event:** CSCCTF v7 · **Category:** Forensics (event category: Doctors' Bounties) · **Points:** 500, dynamic · **Author:** jaarabd

## Description

> A user's crypto wallet was drained after he followed instructions from someone claiming to be from "Wallet Support." He provided his recovery seed, confirmed a wallet address, and ran a verification command. By the time he realized it was a scam, the funds were gone.
>
> His workstation was still running when we arrived. We captured a memory dump before anything was touched. Investigate the dump and recover the following:
>
> 1. The first three words of the recovery seed he provided
> 2. The wallet address he confirmed
> 3. The domain the attacker exfiltrated data to
> 4. The username of the workstation account
>
> Flag format: `CSCCTF{word1-word2-word3_walletaddress_domain_username}`

## Files

- `memchall.zip` containing `cryptoheist.raw`, a Windows 10 memory dump: [download from Google Drive](https://drive.google.com/file/d/1gLeLCaIlYPvxNdobI_WaVnPah6ishNzJ/view?usp=sharing)

## Solution

Tool: [Volatility 3](https://github.com/volatilityfoundation/volatility3).

### 1. Verify the dump

```bash
vol -f cryptoheist.raw windows.info
```

Windows 10 build 19041, x64.

### 2. Find the relevant processes

```bash
vol -f cryptoheist.raw windows.pslist
```

Two user processes stand out, both children of `explorer.exe`, so the user launched them himself:

| Process | PID |
| :-- | :-- |
| `notepad.exe` | 4016 |
| `powershell.exe` | 2544 |

### 3. Domain and seed from PowerShell

The victim ran `curl` with `seed.txt` as the request body. PowerShell read the file into its own memory, so both the URL and the seed phrase are in its heap.

```bash
vol -f cryptoheist.raw windows.memmap --pid 2544 --dump
strings pid.2544.dmp | grep -iE "curl|abandon"
```

This shows the full `curl` command, sending data to **`wallet-recovery-support.xyz`**, and the full BIP39 phrase:

```
abandon ability able about above absent absorb abstract absurd abuse access accident
```

First three words: **`abandon-ability-able`**.

**Alternative: recover `seed.txt` from the file cache.**

```bash
vol -f cryptoheist.raw windows.filescan | grep -i seed.txt
# 0xa185656b54f0  \Users\abd123\AppData\Local\Temp\seed.txt

vol -f cryptoheist.raw windows.dumpfiles --virtaddr 0xa185656b54f0
```

The extracted file contains the same phrase.

### 4. Wallet address from Notepad

Notepad keeps its buffer as UTF-16LE, so plain `strings` misses it. `-e l` searches for 16-bit little endian strings:

```bash
vol -f cryptoheist.raw windows.memmap --pid 4016 --dump
strings -e l pid.4016.dmp | grep "0x"
```

```
address : 0x4B2c8F9a3E7d5C1b6A8F4e2D9c7B3a5E1F8d2C6b
```

### 5. Username from environment variables

```bash
vol -f cryptoheist.raw windows.envars | grep USERNAME
```

**`abd123`**, which matches the user folder in the `seed.txt` path.

### 6. Flag

```
CSCCTF{abandon-ability-able_0x4B2c8F9a3E7d5C1b6A8F4e2D9c7B3a5E1F8d2C6b_wallet-recovery-support.xyz_abd123}
```

## Design notes

- **Built from a real staged incident.** The dump came from a Windows 10 VirtualBox VM where I acted out the scam: typed the address in Notepad, saved the seed to `%TEMP%`, and ran the exfiltration command from PowerShell. The dump was then captured with DumpIt, so every artifact sits where a real investigation would find it.
- **Four answers, four techniques.** Each piece of the flag needs a different Volatility workflow: per-process memory dumping, file cache recovery, UTF-16 string search, and environment block parsing. A player who knows only one plugin cannot finish.
- **Two valid paths to the seed.** The seed is recoverable from PowerShell's heap or from the cached file. Allowing both rewards players who understand either the process view or the filesystem view of memory.
- **UTF-16 trap.** The Notepad step fails with default `strings`, which teaches that Windows applications store most text as wide characters.
- **Composite flag.** Combining four answers into one flag means no single lucky grep solves it, and the format makes partial progress easy for players to check.
