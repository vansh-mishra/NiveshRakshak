from __future__ import annotations

import json
import math
import re
from collections import Counter
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
TEMPLATES = ROOT / "templates"
HOST = "127.0.0.1"
PORT = 5000

# -----------------------------
# Tiny self-contained ML layer
# -----------------------------
# The hackathon prototype intentionally avoids third-party runtime dependencies.
# We train a small TF-IDF + logistic-regression model in pure Python so the demo
# can run with only the Python standard library installed.

TRAIN_DATA = [
    ("guaranteed 30 percent return invest today limited offer", 1),
    ("deposit money now and double your money in seven days", 1),
    ("exclusive telegram trading group guaranteed profit", 1),
    ("send payment to this personal account to activate trading", 1),
    ("act now or you will miss this investment opportunity", 1),
    ("sebi approved guaranteed daily profit trading app", 1),
    ("verify your demat account through this urgent link", 1),
    ("your account is blocked pay fee to withdraw profits", 1),
    ("receive 50 percent assured return with no risk", 1),
    ("limited slots join our premium investment group today", 1),
    ("pay clearance fee before withdrawal", 1),
    ("whatsapp stock tips guaranteed profit", 1),
    ("send otp to unlock your trading account", 1),
    ("government approved investment double money quickly", 1),
    ("invest ten thousand and withdraw one lakh next week", 1),
    ("click verify link and confirm your account immediately", 1),
    ("our sebi officer will help you get guaranteed returns", 1),
    ("telegram premium signal group assured profit", 1),
    ("pay tax first to release your investment profit", 1),
    ("urgent demat verification required today", 1),
    ("read the annual report and risk disclosure before investing", 0),
    ("market investments involve risk and returns are not guaranteed", 0),
    ("please review the official investor information document", 0),
    ("long term investing requires understanding risk and diversification", 0),
    ("check the registered intermediary details before opening an account", 0),
    ("compare fees and read the product disclosure document", 0),
    ("invest only after understanding the risks and charges", 0),
    ("use official channels to verify a financial intermediary", 0),
    ("do not share passwords or otp with anyone", 0),
    ("learn about market risk before investing", 0),
    ("verify information from official regulatory sources", 0),
    ("investing can result in loss and no return is guaranteed", 0),
]

WORD_RE = re.compile(r"[a-zA-Z0-9%]+")


def tokenize(text: str):
    return WORD_RE.findall(text.lower())


class TinyTfIdfLogReg:
    def __init__(self):
        self.vocab = {}
        self.idf = []
        self.weights = []
        self.bias = 0.0

    def fit(self, texts, labels, epochs=500, lr=0.08):
        documents = [tokenize(t) for t in texts]
        df = Counter()
        for tokens in documents:
            df.update(set(tokens))
        terms = sorted(df)
        self.vocab = {term: i for i, term in enumerate(terms)}
        n = len(documents)
        self.idf = [math.log((1 + n) / (1 + df[t])) + 1 for t in terms]
        X = [self._vectorize_tokens(tokens) for tokens in documents]
        self.weights = [0.0] * len(terms)
        self.bias = 0.0
        for _ in range(epochs):
            grad_w = [0.0] * len(terms)
            grad_b = 0.0
            for row, y in zip(X, labels):
                z = self.bias + sum(w * x for w, x in zip(self.weights, row))
                p = 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))
                err = p - y
                grad_b += err
                for j, x in enumerate(row):
                    if x:
                        grad_w[j] += err * x
            scale = 1.0 / n
            self.bias -= lr * grad_b * scale
            for j in range(len(self.weights)):
                self.weights[j] -= lr * grad_w[j] * scale
        return self

    def _vectorize_tokens(self, tokens):
        counts = Counter(tokens)
        total = sum(counts.values()) or 1
        vec = [0.0] * len(self.vocab)
        for term, count in counts.items():
            idx = self.vocab.get(term)
            if idx is not None:
                vec[idx] = (count / total) * self.idf[idx]
        return vec

    def predict_proba(self, text: str) -> float:
        vec = self._vectorize_tokens(tokenize(text))
        z = self.bias + sum(w * x for w, x in zip(self.weights, vec))
        return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))


MODEL = TinyTfIdfLogReg().fit([x for x, _ in TRAIN_DATA], [y for _, y in TRAIN_DATA])

# -----------------------------
# Transparent safety signals
# -----------------------------

FLAG_RULES = [
    {
        "key": "guaranteed_return",
        "label": "Guaranteed / unrealistic return claim",
        "explanation": "Promises of guaranteed or unusually high returns can be a warning sign and should be independently verified.",
        "weight": 28,
        "patterns": [
            r"\bguaranteed\s+(?:return|profit|income)\b",
            r"\bassured\s+(?:return|profit)\b",
            r"\b(?:\d+\s*%|double|triple)\b.{0,40}\b(?:return|profit|money|days?)\b",
            r"\bno\s+risk\b.{0,30}\b(?:return|profit)\b",
            r"\bपक्का\b.{0,30}\bमुनाफा\b",
            r"\bगारंटीड\b",
        ],
    },
    {
        "key": "urgency",
        "label": "Urgency / pressure to act",
        "explanation": "Pressure to invest or pay immediately can reduce the user's opportunity to verify the claim.",
        "weight": 17,
        "patterns": [
            r"\bact\s+now\b",
            r"\blimited\s+(?:offer|slot|time)\b",
            r"\b(?:invest|deposit|pay|join).{0,20}\btoday\b",
            r"\blast\s+chance\b",
            r"\bdo\s+not\s+miss\b",
            r"\btur(?:a|n)\b.{0,25}\b(?:invest|pay)\b",
            r"\bअभी\b.{0,25}\b(?:निवेश|पैसा|जमा)\b",
        ],
    },
    {
        "key": "credential_or_payment",
        "label": "Sensitive credential / payment request",
        "explanation": "Requests for OTPs, PINs, passwords or money transfers should be treated cautiously.",
        "weight": 28,
        "patterns": [
            r"\b(?:otp|pin|password|passcode)\b",
            r"\bshare\s+(?:your|the)\s+(?:otp|pin|password)\b",
            r"\bpay\s+(?:a|the)\s+(?:fee|tax|charge)\b",
            r"\bdeposit\s+(?:money|funds)\b",
            r"\bpay(?:ment)?\s+to\s+(?:this|my)\s+(?:personal|private)\s+account\b",
            r"\b(?:personal|private)\s+upi\b",
            r"\bओटीपी\b|\bपासवर्ड\b|\bपिन\b",
        ],
    },
    {
        "key": "impersonation",
        "label": "Possible regulatory / brand impersonation",
        "explanation": "Claims of being 'SEBI approved' or a government official should be independently verified; scammers may impersonate trusted institutions.",
        "weight": 23,
        "patterns": [
            r"\b(?:sebi|nsdl|nse|bse)\s+approved\b",
            r"\bofficial\s+sebi\b",
            r"\bsebi\s+(?:officer|agent|representative)\b",
            r"\bgovernment\s+approved\b",
            r"\bसेबी\b.{0,40}\bअधिकृत\b",
            r"\bसरकार\b.{0,40}\bअप्रूव(?:ed)?\b",
        ],
    },
    {
        "key": "social_channel",
        "label": "High-risk solicitation through informal channels",
        "explanation": "Investment solicitations through social or messaging channels should be checked against official sources before acting.",
        "weight": 10,
        "patterns": [
            r"\btelegram\b",
            r"\bwhatsapp\b|\bwhats\s*app\b",
            r"\binstagram\b",
            r"\b(?:trading|investment)\s+group\b",
            r"\btelegram\s+(?:signal|premium|vip)\b",
        ],
    },
    {
        "key": "withdrawal_block",
        "label": "Blocked withdrawal / fee-to-withdraw pattern",
        "explanation": "Requests for additional money to unlock or release profits are a major warning pattern.",
        "weight": 28,
        "patterns": [
            r"\b(?:account|withdrawal).{0,30}\b(?:blocked|frozen|suspended)\b",
            r"\bpay\s+(?:another|additional)\s+fee.{0,40}\bwithdraw\b",
            r"\b(?:tax|clearance|unlock)\s+fee.{0,40}\b(?:withdraw|release)\b",
            r"\bनिकासी\b.{0,30}\b(?:फीस|टैक्स)\b",
        ],
    },
]

URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rb.gy", "is.gd"}
SUSPICIOUS_TLDS = {"zip", "top", "click", "work", "shop", "xyz", "live", "buzz"}


def match_flags(text: str):
    hits = []
    score = 0
    for rule in FLAG_RULES:
        matched = any(re.search(p, text, re.IGNORECASE) for p in rule["patterns"])
        if matched:
            hits.append({
                "key": rule["key"],
                "label": rule["label"],
                "explanation": rule["explanation"],
                "weight": rule["weight"],
            })
            score += rule["weight"]
    return hits, min(score, 100)


URL_RE = re.compile(r"https?://[^\s<>\"\']+", re.IGNORECASE)
BARE_DOMAIN_RE = re.compile(r"(?<![@\w.-])(?:[a-z0-9-]+\.)+(?:com|in|org|net|gov|xyz|top|site|online|shop|click|live|io)(?:/[^^\s<>\"\']*)?", re.IGNORECASE)
OFFICIAL_DOMAINS = {
    "sebi.gov.in",
    "scores.sebi.gov.in",
}

def extract_url_from_text(text: str) -> str:
    if not text:
        return ""
    match = URL_RE.search(text)
    if match:
        return match.group(0).rstrip(".,);]>")
    match = BARE_DOMAIN_RE.search(text)
    if match:
        return match.group(0).rstrip(".,);]>")
    return ""

def analyze_url(url: str):
    if not url:
        return {"score": 0, "signals": [], "domain": ""}

    candidate = url.strip().strip("<>").rstrip(".,);]")
    if not re.match(r"^https?://", candidate, re.IGNORECASE):
        candidate = "https://" + candidate
    parsed = urlparse(candidate)
    domain = (parsed.hostname or "").lower()
    score = 0
    signals = []

    if not domain:
        return {
            "score": 60,
            "signals": [("Invalid or unreadable URL", "The URL could not be parsed reliably. Do not open or submit sensitive information until it is verified.")],
            "domain": "",
        }

    # Known official domains are only an identity signal, never a guarantee of safety.
    if domain in OFFICIAL_DOMAINS:
        signals.append(("Recognized official-domain pattern", "This exact domain matches an official SEBI domain used by the prototype. The specific page or claim still requires verification."))
    if parsed.scheme.lower() != "https":
        score += 18
        signals.append(("No HTTPS", "The URL is not using an encrypted HTTPS connection."))
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", domain):
        score += 28
        signals.append(("IP address", "The URL uses a raw IP address rather than a normal domain."))
    if "xn--" in domain:
        score += 18
        signals.append(("Punycode domain", "Punycode can be legitimate, but it deserves additional verification."))
    if domain in URL_SHORTENERS:
        score += 15
        signals.append(("URL shortener", "The destination is hidden behind a shortened URL."))
    if domain.count("-") >= 3 or len(domain) > 45:
        score += 10
        signals.append(("Unusual domain structure", "The domain has characteristics worth independently verifying."))

    # A few digits alone are weak; multiple digits in an unusual financial domain are stronger.
    if sum(ch.isdigit() for ch in domain) >= 2:
        score += 5
        signals.append(("Digits in domain", "Digits are not proof of fraud, but the domain should be independently verified."))

    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if tld in SUSPICIOUS_TLDS:
        score += 10
        signals.append(("Higher-risk TLD signal", f"The .{tld} TLD is treated only as a weak verification signal."))

    deceptive_terms = ("profit", "bonus", "double", "withdraw", "verify-sebi", "sebi-invest", "sebi-verify", "investment-login")
    if any(term in domain for term in deceptive_terms):
        score += 12
        signals.append(("Investment-related / deceptive domain keyword", "The domain contains wording commonly used in investment or verification lures and should be independently verified."))

    # Combination signal: brand/regulator-like term + investment/deception term is more concerning
    # than either term alone.
    has_regulator = any(term in domain for term in ("sebi", "nsdl", "nse", "bse", "gov"))
    has_lure = any(term in domain for term in ("profit", "bonus", "verify", "invest", "investment", "trading", "withdraw", "login"))
    if has_regulator and has_lure and domain not in OFFICIAL_DOMAINS:
        score += 25
        signals.append(("Possible impersonation pattern", "The domain combines a regulator/brand-like term with a financial or verification lure. Independently verify the entity before acting."))

    # URL-only input should produce a meaningful risk tier when multiple signals exist.
    distinct_signals = len(signals)
    if domain not in OFFICIAL_DOMAINS:
        if distinct_signals >= 3:
            score = max(score, 70)
        elif distinct_signals == 2:
            score = max(score, 40)
        elif distinct_signals == 1 and score > 0:
            score = max(score, 30)

    return {"score": min(score, 100), "signals": signals, "domain": domain}


def risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def language_pack(lang: str):
    if lang == "hi":
        return {
            "title": "जोखिम आकलन",
            "high": "उच्च जोखिम",
            "medium": "मध्यम जोखिम",
            "low": "कम जोखिम",
            "what_detected": "क्या पाया गया",
            "safer": "सुरक्षित अगले कदम",
            "summary_high": "कई चेतावनी संकेत पाए गए। वित्तीय कार्रवाई से पहले स्वतंत्र रूप से सत्यापन करें।",
            "summary_medium": "कुछ चेतावनी संकेत पाए गए। दबाव में कार्रवाई न करें और दावों का स्वतंत्र सत्यापन करें।",
            "summary_low": "इस प्रोटोटाइप ने कोई मजबूत चेतावनी पैटर्न नहीं पाया। इसका अर्थ यह नहीं है कि सामग्री निश्चित रूप से सुरक्षित है।",
        }
    if lang == "hinglish":
        return {
            "title": "Risk Assessment",
            "high": "HIGH RISK",
            "medium": "MEDIUM RISK",
            "low": "LOW RISK",
            "what_detected": "Kya detect hua",
            "safer": "Safer next steps",
            "summary_high": "Kai warning signs mile hain. Financial action se pehle independently verify karein.",
            "summary_medium": "Kuch warning signs mile hain. Pressure mein action na lein aur claims ko verify karein.",
            "summary_low": "Is prototype ko koi strong warning pattern nahi mila. LOW ka matlab guaranteed safe nahi hai.",
        }
    return {
        "title": "Risk Assessment",
        "high": "HIGH RISK",
        "medium": "MEDIUM RISK",
        "low": "LOW RISK",
        "what_detected": "What we detected",
        "safer": "Safer next steps",
        "summary_high": "Multiple warning indicators were detected. Verify independently before taking financial action.",
        "summary_medium": "Some warning indicators were detected. Do not act under pressure; verify the sender, entity and claims independently.",
        "summary_low": "No strong warning pattern was detected by this prototype. A LOW result does not guarantee that content is genuine or safe.",
    }


def localize_flag(flag, lang):
    # Keep the safety logic stable and localize the presentation layer.
    if lang == "hi":
        labels = {
            "guaranteed_return": "गारंटीड / असामान्य रिटर्न का दावा",
            "urgency": "जल्दी कार्रवाई करने का दबाव",
            "credential_or_payment": "OTP / पासवर्ड / भुगतान से जुड़ी मांग",
            "impersonation": "नियामक या ब्रांड की संभावित नकल",
            "social_channel": "अनौपचारिक चैनल के माध्यम से निवेश प्रस्ताव",
            "withdrawal_block": "निकासी रोकने / अतिरिक्त शुल्क का पैटर्न",
        }
        return {**flag, "label": labels.get(flag["key"], flag["label"])}
    if lang == "hinglish":
        labels = {
            "guaranteed_return": "Guaranteed / unrealistic return claim",
            "urgency": "Jaldi action lene ka pressure",
            "credential_or_payment": "OTP / password / payment request",
            "impersonation": "Regulatory ya brand impersonation ka signal",
            "social_channel": "Informal channel se investment solicitation",
            "withdrawal_block": "Withdrawal block / extra-fee pattern",
        }
        return {**flag, "label": labels.get(flag["key"], flag["label"])}
    return flag


def analyze(message: str, url: str, lang: str = "en"):
    text = (message or "").strip()
    explicit_url = (url or "").strip()
    embedded_url = extract_url_from_text(text)
    effective_url = explicit_url or embedded_url
    model_probability = MODEL.predict_proba(text) * 100 if text else 0.0
    flags, rule_score = match_flags(text) if text else ([], 0)
    url_result = analyze_url(effective_url) if effective_url else {"score": 0, "signals": [], "domain": ""}

    # The transparent rule engine has more weight so the result can be explained.
    text_score = round(0.72 * rule_score + 0.28 * model_probability)
    final_score = max(text_score, url_result["score"])
    if flags and any(f["key"] in {"credential_or_payment", "withdrawal_block"} for f in flags):
        final_score = max(final_score, 72)
    if len(flags) >= 3:
        final_score = max(final_score, 75)
    final_score = min(100, int(round(final_score)))

    level = risk_level(final_score)
    pack = language_pack(lang)
    summary = pack["summary_high"] if level == "HIGH" else pack["summary_medium"] if level == "MEDIUM" else pack["summary_low"]
    localized_flags = [localize_flag(f, lang) for f in flags]

    safety_steps = {
        "en": [
            "Do not transfer money because of pressure, guaranteed-return claims or social-media solicitations.",
            "Never share OTPs, PINs, passwords or other sensitive credentials.",
            "Verify the entity independently using official sources before acting.",
            "Keep screenshots, URLs and transaction details if you suspect fraud.",
        ],
        "hi": [
            "दबाव, गारंटीड रिटर्न या सोशल-मीडिया संदेश के कारण तुरंत पैसा ट्रांसफर न करें।",
            "OTP, PIN, पासवर्ड या अन्य संवेदनशील जानकारी साझा न करें।",
            "कार्रवाई से पहले आधिकारिक स्रोतों से इकाई/प्लेटफॉर्म का स्वतंत्र सत्यापन करें।",
            "संदेह होने पर स्क्रीनशॉट, URL और लेन-देन की जानकारी सुरक्षित रखें।",
        ],
        "hinglish": [
            "Pressure, guaranteed return ya social-media message ki wajah se turant money transfer na karein.",
            "OTP, PIN, password ya sensitive details share na karein.",
            "Action se pehle official sources se entity/platform ko independently verify karein.",
            "Suspicion ho to screenshot, URL aur transaction details save rakhein.",
        ],
    }[lang if lang in {"en", "hi", "hinglish"} else "en"]

    return {
        "risk_score": final_score,
        "risk_level": level,
        "model_probability": round(model_probability),
        "rule_score": rule_score,
        "summary": summary,
        "flags": localized_flags,
        "url_signals": [{"label": a, "explanation": b} for a, b in url_result["signals"]],
        "domain": url_result["domain"],
        "analyzed_url": effective_url,
        "safety_steps": safety_steps,
        "language": lang,
        "analysis_mode": "text_and_url" if text and effective_url else "text_only" if text else "url_only",
        "model": "Tiny TF-IDF + Logistic Regression (pure Python demo) + transparent rule engine",
    }


# -----------------------------
# HTTP application
# -----------------------------


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length > 256_000:
        raise ValueError("Request is too large")
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8")) if raw else {}


def send_bytes(handler, payload: bytes, content_type="text/html; charset=utf-8", status=HTTPStatus.OK):
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


class Handler(BaseHTTPRequestHandler):
    server_version = "NiveshRakshak/1.0"

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            payload = (TEMPLATES / "index.html").read_bytes()
            send_bytes(self, payload)
            return
        if parsed.path == "/api/health":
            send_bytes(self, json.dumps({"status": "ok", "model": "tiny-tfidf-logreg", "version": "1.0"}).encode(), "application/json")
            return
        if parsed.path.startswith("/static/"):
            rel = parsed.path[len("/static/"):].replace("..", "")
            file = STATIC / rel
            if file.exists() and file.is_file():
                ct = "text/css" if file.suffix == ".css" else "application/javascript" if file.suffix == ".js" else "application/octet-stream"
                send_bytes(self, file.read_bytes(), ct)
                return
        send_bytes(self, b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            send_bytes(self, b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return
        try:
            data = read_json(self)
            message = str(data.get("message", ""))[:20_000]
            url = str(data.get("url", ""))[:2_000]
            lang = str(data.get("language", "en"))
            if not message and not url:
                raise ValueError("Enter a message or URL to analyze.")
            result = analyze(message, url, lang)
            send_bytes(self, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json")
        except Exception as exc:
            send_bytes(self, json.dumps({"error": str(exc)}).encode("utf-8"), "application/json", HTTPStatus.BAD_REQUEST)


def main():
    print(f"NiveshRakshak running at http://{HOST}:{PORT}")
    print("Prototype: investor-safety risk screening only; not official SEBI verification.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping NiveshRakshak...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
