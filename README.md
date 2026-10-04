# NiveshRakshak
## PROJECT LINK: https://niveshrakshak.onrender.com
**AI-Powered Investor Safety & Scam Resilience Platform**

NiveshRakshak is an investor-safety application that helps users assess suspicious financial messages, screenshots, and URLs before taking potentially harmful actions. It combines lightweight machine learning, transparent safety rules, URL heuristics, screenshot OCR, and simple multilingual presentation to provide an explainable early-warning assessment.

> **Check Before You Trust.**

## Overview

Online financial scams often use guaranteed-return claims, urgency, requests for money or credentials, impersonation of trusted institutions, social-media investment groups, and suspicious links. NiveshRakshak is designed to give a user a simple first layer of protection when they encounter this type of content.

The application does not decide whether an investment should be made. Instead, it identifies potential warning signs, explains them in understandable language, and provides safer next steps.

## What the Project Does

NiveshRakshak accepts three main forms of input:

- **Financial messages** pasted by the user.
- **Screenshots** containing suspicious financial content.
- **URLs** that the user wants to screen for risk indicators.

The system then:

1. Extracts and preprocesses the available content.
2. Applies a lightweight text-classification model when message text is available.
3. Applies transparent rules for common financial-scam indicators.
4. Analyzes URL characteristics when a URL is supplied or detected in a message.
5. Combines the signals into a risk score and risk level.
6. Shows the warning signals that contributed to the result.
7. Provides safer next-step guidance.
8. Links users to official investor-protection resources.

## Key Features

### 1. Financial Message Risk Analysis

The system evaluates message content for patterns associated with potentially harmful financial solicitations, including:

- Guaranteed or unrealistic return claims
- Urgent pressure to act
- Requests for OTPs, passwords, PINs, or payments
- Claims of regulatory or institutional approval
- Investment solicitations through informal channels such as Telegram or WhatsApp
- Withdrawal-fee or blocked-withdrawal patterns

### 2. Explainable Risk Assessment

The application does not only return a classification. It shows the warning signals that influenced the assessment and provides a plain-language explanation for each signal.

Example:

```text
HIGH RISK

Warning signals:
- Guaranteed / unrealistic return claim
- Urgency / pressure to act
- Sensitive credential / payment request
- Possible regulatory / brand impersonation

Safer next steps:
- Do not transfer money under pressure.
- Do not share OTPs, passwords, or PINs.
- Verify the entity independently.
```

### 3. URL Risk Analysis

The URL analyzer checks characteristics such as:

- HTTPS usage
- Raw IP-address URLs
- Punycode domains
- URL shorteners
- Unusual domain structure
- Higher-risk TLD signals
- Investment or deceptive domain wording
- Possible regulator/brand impersonation patterns

A URL result is treated as a risk assessment, not as proof that a website is fraudulent.

### 4. Screenshot OCR

Users can upload a screenshot of a suspicious message. Browser-side OCR extracts readable text and sends the extracted content through the same message-analysis workflow.

The current implementation uses Tesseract.js from a browser CDN, so screenshot OCR requires network access when the OCR library must be loaded.

### 5. English, Hindi, and Hinglish Presentation

The interface provides English, Hindi, and Hinglish result presentation to reduce the amount of financial terminology a first-time user needs to understand.

The current prototype provides multilingual presentation and selected Hindi/Hinglish safety patterns. The underlying ML tokenizer is still primarily English-oriented, so broader multilingual model support remains a future enhancement.

### 6. Safety-Oriented Guidance

The system provides non-advisory actions such as:

- Do not transfer money immediately.
- Do not share credentials or OTPs.
- Independently verify the organization or platform.
- Preserve suspicious messages or screenshots as evidence.
- Use official investor-support or grievance channels when appropriate.

## How the System Works

```text
User Input
   |
   +--> Message --------------------+
   |                               |
   +--> Screenshot --> OCR --------+--> Preprocessing
   |                               |
   +--> URL -----------------------+
                                   |
                         +---------+---------+
                         |                   |
                    Text ML Model       Rule Engine
                         |                   |
                         +---------+---------+
                                   |
                              URL Analysis
                                   |
                             Risk Assessment
                                   |
                         Explainable Result
                                   |
                           Safety Guidance
                                   |
                       Official Resources
```

## Technical Architecture

The prototype is intentionally lightweight so that it can be run locally with a standard Python installation.

### Backend

- Python
- Built-in HTTP server
- JSON API endpoint for analysis

### Machine Learning

- TF-IDF-style vectorization implemented in pure Python
- Logistic Regression implemented in pure Python
- Small demonstration training set included in the prototype

### Rule Engine

A transparent rule engine checks explicit safety indicators such as guaranteed returns, urgency, credential requests, payment requests, and possible impersonation.

### OCR

- Tesseract.js in the browser
- Hindi and English OCR languages configured in the current prototype

### Frontend

- HTML
- CSS
- JavaScript
- Responsive browser interface

## Risk Scoring

The prototype combines multiple signals rather than relying on a single keyword.

For message analysis, the displayed assessment uses:

- Rule-based signal score
- Text-model probability
- URL signals when a URL is supplied or extracted

For URL-only screening, the result is driven by URL heuristics and does not use the text-model probability because there is no message text.

The displayed value is a **risk score**, not a calibrated probability of fraud.

## Why the Approach Is Useful

### Explainability

The user can see the specific warning signals rather than receiving an unexplained model label.

### Hybrid Detection

Machine learning helps identify language patterns, while explicit rules provide transparent safety signals that can be inspected and updated.

### Low Complexity

The core application can run without a third-party Python ML runtime, which makes the prototype easier to set up and demonstrate.

### User-Centered Safety

The system focuses on what the user should understand and do next instead of producing trading recommendations.

### Extensible Architecture

The input, detection, explanation, and resource layers are separated conceptually, allowing additional languages, models, verification sources, and input methods to be added later.

## Privacy and Safety Principles

NiveshRakshak is designed as an investor-protection tool and does not require trading credentials, OTP collection, or SMS access for its core workflow.

The project does not provide:

- Buy, sell, or hold recommendations
- Stock-price predictions
- Trading signals
- Broker or financial-product promotion
- Speculative investment advice

Users should avoid submitting unnecessary sensitive financial information.

## Scalability

The current prototype is intentionally small, but the architecture can be extended in several directions.

### 1. More Indian Languages

The detection and explanation layers can be extended from English/Hindi/Hinglish to additional Indian languages using multilingual NLP models and localized safety content.

### 2. Stronger Claim Verification

A future version can extract claims such as “SEBI approved” or “registered intermediary” and compare them against authoritative sources before presenting an evidence-backed verification status.

### 3. Better URL Intelligence

The URL layer can evolve from heuristics into a dedicated phishing/financial-risk model using larger, legally usable datasets and additional lexical and structural features.

### 4. Voice Interaction

Speech-to-text and text-to-speech can provide a voice-first workflow for users with low digital literacy or limited comfort with text-heavy interfaces.

### 5. Larger Scam Intelligence

A structured and continuously updated knowledge layer can support more scam categories, new fraud patterns, known deceptive techniques, and source traceability.

### 6. Production Deployment

The backend can be moved from the lightweight built-in server to a production WSGI/ASGI deployment, with caching, observability, rate limiting, scalable model serving, and a persistent knowledge store.

## Current Strengths

- Clear investor-safety purpose
- Explainable warning signals
- Hybrid ML + rule-based design
- Text, screenshot, and URL input paths
- Simple user workflow
- English/Hindi/Hinglish presentation
- No investment recommendations
- No OTP/SMS harvesting in the core workflow
- Easy local execution
- Modular path toward stronger verification and multilingual support

## Current Limitations

The current version is a working prototype rather than a production-grade fraud-detection service.

### Limited Training Data

The included ML examples are synthetic demonstration examples. They are suitable for demonstrating the pipeline but are not sufficient for claiming real-world detection performance.

### No Production Model Evaluation Yet

The project should not claim production-level accuracy until it is evaluated on a properly sourced and legally usable dataset with separate training, validation, and test sets.

Recommended evaluation metrics include:

- Precision
- Recall
- F1-score
- False-positive rate
- False-negative rate
- Confusion matrix

### Heuristic URL Screening

The URL analyzer currently evaluates URL characteristics. It does not provide a definitive reputation verdict, perform comprehensive threat-intelligence lookups, or guarantee that a website is legitimate.

### Limited Multilingual ML

The interface supports English, Hindi, and Hinglish presentation, but the current text model is primarily English-oriented. Full multilingual detection requires a multilingual NLP model and a properly labelled multilingual dataset.

### OCR Dependency

Screenshot OCR depends on the browser loading the Tesseract.js library. Poor image quality, stylized text, or complex screenshots may reduce extraction quality.

### No Official Entity Verification Engine Yet

The current prototype links to official resources and provides impersonation-related risk signals, but it does not yet perform comprehensive real-time verification of every claimed financial entity.

## Planned Improvements

The next technical improvements should focus on depth rather than adding unrelated features:

1. Replace synthetic training examples with a properly sourced dataset.
2. Build a rigorous evaluation pipeline.
3. Add a dedicated multilingual NLP model.
4. Add claim extraction and evidence-backed verification.
5. Add official entity matching and source tracing.
6. Add voice input and accessible voice responses.
7. Improve URL detection with a dedicated model and larger feature set.
8. Move OCR toward a more controlled privacy-preserving deployment.
9. Add monitoring, rate limiting, logging, and production deployment controls.

## Local Setup

### Requirements

- Python 3.10 or newer
- A modern web browser
- Internet access for browser-side OCR library loading

### Run

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The current backend uses the Python standard library, so no `pip install` step is required for the core application.

## Example Test Message

```text
SEBI approved investment opportunity. Invest ₹10,000 today and receive guaranteed 40% return in 7 days. Send your OTP to activate your account.
```

Expected behavior: the system should identify multiple warning indicators and return a high-risk assessment.

## Example URL Test

```text
https://profit-sebi-verify.top/login
```

Expected behavior: the system should identify URL characteristics that warrant additional verification.

## Disclaimer

NiveshRakshak is an early-warning and educational prototype. Its results are not definitive legal, regulatory, or financial judgments. A low-risk result does not prove that a message, URL, or organization is legitimate. Users should independently verify important financial claims using authoritative sources before taking action.
