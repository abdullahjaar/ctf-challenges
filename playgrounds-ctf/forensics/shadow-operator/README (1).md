# Shadow Operator

**Event:** Playgrounds CTF · **Category:** Forensics · **Author:** jaarabd

## Description

> A DMP file was collected from a command shell after an attacker gained access to the machine. Inspect the dump and recover what the attacker was trying to run.

## Files

- [`cmd.DMP`](cmd.DMP) (19.5 MB, SHA-256 `4884a120ad6e14acc4cf1d8d7b941cf18efc02eede199714427fc990c1fc3414`)

## Solution

### 1. Identify the file

```bash
file cmd.DMP
```

```
cmd.DMP: Mini DuMP crash report, 16 streams, Wed Nov 19 14:42:48 2025, 0x421826 type
```

It is a Windows minidump of a `cmd.exe` process. A full memory forensics framework is not needed: the process memory holds the console input history, so the question is how to pull strings out of it.

### 2. Search for wide strings

Windows stores command lines and console buffers as UTF-16LE. Plain `strings` only finds ASCII and returns nothing useful:

```bash
strings -a cmd.DMP | grep -i encodedcommand     # no results
```

Searching for 16-bit little endian strings finds the attacker's command:

```bash
strings -el cmd.DMP | grep -i encodedcommand
```

```
powershell -EncodedCommand UGxheWdyb3VuZHNDVEZ7NGFzeXlfYmFieV9EVU1QISEhfQ==
```

### 3. Decode the payload

```bash
echo UGxheWdyb3VuZHNDVEZ7NGFzeXlfYmFieV9EVU1QISEhfQ== | base64 -d
```

### 4. Flag

```
PlaygroundsCTF{4asyy_baby_DUMP!!!}
```

## Design notes

- **Intended difficulty: easy.** This was the entry-level forensics challenge of the set. It teaches two habits: recognise a minidump, and know that Windows memory is mostly UTF-16LE, so `strings -el` is the first thing to run.
- **Realistic attacker technique.** `powershell -EncodedCommand` is a common way to hide a command line from casual inspection and from naive logging. Spotting the flag and decoding base64 is the same step an analyst takes when triaging a real incident.
- **Captured from a live shell.** The dump was taken from a real `cmd.exe` session after typing the command, so the string sits in the console history buffer next to genuine process data such as the environment block and loaded module paths, instead of being planted in a synthetic file.
- **Known simplification.** A real `-EncodedCommand` argument is base64 of UTF-16LE text. This one encodes UTF-8 so that it decodes cleanly with `base64 -d`, which kept it beginner friendly. PowerShell would not run it as is.
