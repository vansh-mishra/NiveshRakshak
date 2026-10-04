# NiveshRakshak — SANGYAN Working Prototype

**AI-Powered Investor Safety & Scam Resilience Platform**

This version is designed as a hackathon MVP that runs with the **Python standard library only** on the backend.

## What works

- Text-based investment scam screening.
- Transparent warning-sign rules.
- Pure-Python TF-IDF + logistic-regression demo model.
- URL risk signals.
- Risk score: LOW / MEDIUM / HIGH.
- Explainable reasons and safer next steps.
- English / Hinglish / Hindi presentation.
- Browser-side screenshot OCR using Tesseract.js (internet is needed for the CDN on the first load).
- Official SEBI Investor, SCORES and entity-status links.
- No buy/sell/hold recommendations.
- `/api/health` endpoint for a quick deployment check.

## Run on Windows / Linux / macOS

Python 3.10+ is recommended.

```bash
python app.py
```

Open:

`http://127.0.0.1:5000`

No `pip install` step is required for the backend.

## Recommended 45-second judge demo

1. Click **Load demo message**.
2. Click **Analyze for risk**.
3. Show the HIGH risk result and four warning signals.
4. Switch language to Hindi or Hinglish and analyze again.
5. Upload a screenshot of a suspicious message and show browser-side OCR.
6. Show **SEBI Investor / SCORES / Verify entity** links.

## Architecture

User -> Text / Screenshot / URL -> Preprocessing -> Rule Engine + Tiny TF-IDF/LogReg -> Risk Assessment -> Explanation -> Safety Guidance -> Official Resources

## Responsible-AI boundary

This is an early-warning prototype, not an official SEBI verifier or legal/financial-advice system. A LOW result does not guarantee that a message, URL, or entity is genuine.

## Important data note

The ML training examples in `app.py` are synthetic demo examples. They are for demonstrating the pipeline only. Before claiming real-world performance, replace them with a properly sourced and legally usable dataset, add train/validation/test splits, and report precision, recall, F1-score and false-positive/false-negative rates.
