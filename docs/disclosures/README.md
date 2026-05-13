# Disclosures

This directory contains records of vulnerabilities discovered with Vex and
disclosed to upstream vendors.

Each disclosure lives in its own file, named `YYYY-MM-vendor-shortname.md`,
and includes a status header (Draft / Submitted / Acknowledged / Fixed /
Public). Drafts are kept here for transparency about the work; specific
exploit details for unfixed issues are redacted until vendors respond.

## How to submit (general workflow)

1. Draft the disclosure in this directory using the existing files as a
   template. Include: summary, deterministic reproduction, evidence, severity
   assessment, suggested mitigations, disclosure timeline.
2. Submit through the vendor's preferred channel:

   | Vendor | Channel |
   |---|---|
   | Anthropic | HackerOne (`anthropic`) or `safety@anthropic.com` |
   | OpenAI | Bugcrowd (`openai`) or `security@openai.com` |
   | Google / Gemini | <https://bughunters.google.com> |
   | Microsoft Copilot | MSRC <https://msrc.microsoft.com/report> |
   | Hugging Face | <https://huggingface.co/security> |
   | Mistral / Cohere / X.ai | check their `security.txt` or DM |

3. Update the disclosure file's status header as the vendor responds.
4. When the issue is fixed (or formally declined and the 90-day window has
   passed), update to `Public` and link any vendor advisory.

## Current disclosures

| File | Vendor | Status | Severity |
|---|---|---|---|
| [`2026-05-anthropic-reversed-encoding.md`](2026-05-anthropic-reversed-encoding.md) | Anthropic | Draft | Low |
