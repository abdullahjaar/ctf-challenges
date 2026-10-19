# Inbox Zero

**Event:** Playgrounds CTF · **Category:** Forensics · **Author:** jaarabd

## Description

> One email. Many clues.

## Files

- [`phishing.eml`](phishing.eml)

Players analyse the email offline and answer 11 questions over a netcat service. Answers are case insensitive. Each question allows 3 attempts, and failing one ends the session, so guessing does not work.

## Solution

Open the file in a text editor, not a mail client. A mail client renders the HTML and hides most of the headers.

| # | Question | Answer | Where to find it |
| :-- | :-- | :-- | :-- |
| 1 | What is the recipient's email address? | `sarah.mitchell@techcorp.io` | `To:` and `Delivered-To:` headers |
| 2 | What company/brand is being impersonated? | `paypal` | `From:` display name, subject, body |
| 3 | What is the MIME boundary identifier? | `----=_Part_67890_123456789.1735041165000` | `boundary=` in the `Content-Type` header |
| 4 | What is the X-Mailer header value? | `MailChimp Spoof Engine v2.8` | `X-Mailer:` header |
| 5 | What timezone was the email sent from? | `+0300` | `Date: Tue, 24 Dec 2025 14:12:45 +0300` |
| 6 | What are the two suspicious transaction amounts? | `847.99,1250.00` | Plain text and HTML body |
| 7 | What is the primary malicious domain in the email body? | `paypal-secure-login.com` | "Verify" link and footer links |
| 8 | What is the session/token parameter in the malicious URL? | `a8f9e2d7c6b1` | `?session=` in the verify link |
| 9 | What is the Message-ID domain? | `phishkit.org` | `Message-ID: <...@phishkit.org>` |
| 10 | How many hops did this email take? | `5` | Count the `Received:` headers |
| 11 | Find the hidden email address in the Reply-To header (Base64). | `support@paypal-secure.com` | Decode the local part of `Reply-To:` |

### Notes on the harder questions

**Q5, timezone.** The `Received` headers use mixed offsets: the internal hops at `techcorp.io` are in `-0800 (PST)`, while the originating hops and the `Date:` header are in `+0300`. The sender's timezone is the one set by the sending client in `Date:`.

**Q10, hops.** Each relay prepends one `Received:` header, so they read bottom to top:

```
[103.94.108.25]            -> sender.phishkit.org
sender.phishkit.org        -> mail-out.shadyhost.ru   (185.220.101.67)
mail-out.shadyhost.ru      -> relay-smtp.cloudmailer.net
relay-smtp.cloudmailer.net -> mx2.techcorp.io
mx2.techcorp.io            -> mail.techcorp.io
```

```bash
grep -c '^Received:' phishing.eml
# 5
```

**Q11, Reply-To.** The local part of the address is base64:

```
Reply-To: c3VwcG9ydEBwYXlwYWwtc2VjdXJlLmNvbQ==@notifications.sender.net
```

```bash
echo c3VwcG9ydEBwYXlwYWwtc2VjdXJlLmNvbQ== | base64 -d
# support@paypal-secure.com
```

### Flag

```
PlaygroundsCTF{3m41l_f0r3n51c5_m4573r}
```

## Other indicators in the email

Not asked, but part of a full analysis:

- **Spoofed sender.** `From: service@paypal.com`, but `Return-Path` is `noreply@paypal-secure.com`.
- **Authentication results.** SPF, DKIM and DMARC all fail, with `dmarc=fail action=quarantine`.
- **Originating IP.** `103.94.108.25`, in `X-Originating-IP` and the SPF result.
- **More base64.** The `uid` in the verify link decodes to a Unix timestamp, and the unsubscribe `id` decodes to the victim's address.
- **Tracking pixel.** A hidden 1x1 image at `tracking.phishkit.org` reports the campaign (`paypal2025`) and the target when the email is opened.

## Design notes

- **Covers the phishing triage checklist.** The questions follow the order a SOC analyst works through a reported email: who it targets, who it pretends to be, header metadata, the payload URL, routing, and hidden data.
- **Raw format on purpose.** Questions 3, 4, 9 and 10 can only be answered from the raw headers, which teaches players to read `.eml` source instead of the rendered message.
- **Strict attempt limit.** Three attempts per question and one shared session stop players from brute forcing answers such as the hop count.
- **Realistic layering.** The email mixes real techniques (display name spoofing, lookalike domains, tracking pixels, urgency) with CTF style hidden data (base64 in `Reply-To`, `uid` and `id`).
