---
id: ocr-opencv-pin
title: "OpenCV is held at 4.12"
converter: pdf
takes: [engine]
status: open
cost: "engine: small, once a release qualifies"
---

# OpenCV is held at 4.12

`engine` · pdf · open

**Broken.** Later OpenCV releases crash now and then inside the OCR on Apple silicon ([`experiments/ocr-engines`](../experiments/ocr-engines/README.md)); 4.12 crashed one paper of the 2026-10-14 run all the same.

**Fix.** Waiting: lift the pin, and the numpy override that goes with it, when a release converts "Canaries in the Coal Mine" ten times without a crash.

**What it gives.** Fewer failed PDF conversions.

**Cost.** Engine: small, once a release qualifies.

**Examples.** "Canaries in the Coal Mine".
