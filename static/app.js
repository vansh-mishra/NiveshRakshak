const $ = (id) => document.getElementById(id);

const demos = {
  scam: "Join our exclusive SEBI-approved Telegram trading group. Guaranteed 40% return. Deposit ₹10,000 today. Send payment to this personal UPI account and share your OTP to activate your trading account.",
  safe: "Please read the investor information document, review the risk disclosure, and verify the registered intermediary through official sources before investing. Returns are not guaranteed.",
  hindi: "आज ही निवेश करें। आपको गारंटीड 30% मुनाफा मिलेगा। अभी ₹10,000 जमा करें और अपना OTP भेजें ताकि अकाउंट एक्टिवेट हो सके।",
};

$("fill-demo").addEventListener("click", () => {
  $("message").value = demos.scam;
  $("url").value = "https://profit-sebi-verify.top/login";
  window.scrollTo({top: 0, behavior: "smooth"});
});

document.querySelectorAll("[data-demo]").forEach(btn => {
  btn.addEventListener("click", () => {
    $("message").value = demos[btn.dataset.demo];
  });
});

$("screenshot").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const status = $("ocr-status");
  status.textContent = "Reading screenshot in your browser…";
  try {
    if (!window.Tesseract) throw new Error("OCR library unavailable. Paste the text manually.");
    const result = await Tesseract.recognize(file, "eng+hin", { logger: (m) => {
      if (m.status === "recognizing text" && typeof m.progress === "number") {
        status.textContent = `Reading screenshot… ${Math.round(m.progress * 100)}%`;
      }
    }});
    const text = (result.data.text || "").trim();
    if (!text) throw new Error("No readable text found in the image.");
    $("message").value = text;
    status.textContent = "OCR complete. Extracted text is ready to analyze.";
  } catch (e) {
    status.textContent = `OCR unavailable: ${e.message}`;
  }
});

$("analyze").addEventListener("click", async () => {
  const message = $("message").value.trim();
  const url = $("url").value.trim();
  const language = $("language").value;
  const error = $("error");
  error.classList.add("hidden");
  if (!message && !url) {
    error.textContent = "Enter a message or URL before analyzing.";
    error.classList.remove("hidden");
    return;
  }

  const button = $("analyze");
  button.disabled = true;
  button.innerHTML = "Analyzing…";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message, url, language})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed.");
    renderResult(data);
  } catch (e) {
    error.textContent = e.message;
    error.classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.innerHTML = "Analyze for risk <span>→</span>";
  }
});

function renderResult(data) {
  const result = $("result");
  const levelClass = data.risk_level.toLowerCase();
  const labels = {
    en: {risk: "Potential risk", flags: "Warning signals", next: "Safer next steps", model: "Model transparency", none: "No strong text-based warning pattern was detected."},
    hinglish: {risk: "Potential risk", flags: "Warning signals", next: "Safer next steps", model: "Model transparency", none: "Koi strong text-based warning pattern detect nahi hua."},
    hi: {risk: "संभावित जोखिम", flags: "चेतावनी संकेत", next: "सुरक्षित अगले कदम", model: "मॉडल पारदर्शिता", none: "कोई मजबूत टेक्स्ट-आधारित चेतावनी पैटर्न नहीं मिला।"}
  }[data.language];

  const flags = data.flags.length ? data.flags.map(f => `
    <div class="signal">
      <div class="signal-dot">!</div>
      <div><strong>${escapeHtml(f.label)}</strong><p>${escapeHtml(f.explanation)}</p></div>
    </div>`).join("") : `<p class="muted">${labels.none}</p>`;

  const urlSignals = data.url_signals.length ? `
    <div class="subblock"><div class="kicker">URL SIGNALS</div>${data.analyzed_url ? `<p class="muted" style="word-break:break-all"><strong>Analyzed URL:</strong> ${escapeHtml(data.analyzed_url)}</p>` : ""}${data.url_signals.map(s => `<div class="url-signal"><strong>${escapeHtml(s.label)}</strong><span>${escapeHtml(s.explanation)}</span></div>`).join("")}</div>` : (data.analyzed_url ? `<div class="subblock"><div class="kicker">URL CHECK</div><p class="muted" style="word-break:break-all"><strong>Analyzed URL:</strong> ${escapeHtml(data.analyzed_url)}</p><p class="muted">No strong URL warning signal was detected. This does not prove that the website is legitimate.</p></div>` : "");

  const steps = data.safety_steps.map((s, i) => `<li><span>${i+1}</span>${escapeHtml(s)}</li>`).join("");
  const modeText = data.analysis_mode === "url_only" ? "URL-only screening" : data.analysis_mode === "text_and_url" ? "Message + URL screening" : "Message screening";
  result.innerHTML = `
    <div class="result-top">
      <div><div class="kicker">${labels.risk} • ${modeText}</div><div class="risk-title ${levelClass}">${escapeHtml(data.risk_level)}</div><p class="summary">${escapeHtml(data.summary)}</p></div>
      <div class="score-ring"><div>${data.risk_score}</div><span>/100</span></div>
    </div>
    <div class="result-grid">
      <div class="subblock"><div class="kicker">${labels.flags}</div>${flags}</div>
      ${urlSignals}
      <div class="subblock"><div class="kicker">${labels.next}</div><ol class="steps">${steps}</ol></div>
    </div>
    <div class="transparency"><div><strong>${labels.model}</strong><p>${data.analysis_mode === "url_only" ? `This result is driven by URL heuristics. No text ML probability is used because no message was supplied. The prototype is an early-warning aid, not a regulatory verdict.` : `Hybrid score = ${Math.round(data.rule_score)} rule-signal points + ${data.model_probability}% model probability. The prototype is an early-warning aid, not a regulatory verdict.`}</p></div><div class="mini-stat"><b>${data.analysis_mode === "url_only" ? data.url_signals.length : data.model_probability + "%"}</b><span>${data.analysis_mode === "url_only" ? "URL signals" : "ML probability"}</span></div></div>
    <div class="result-actions"><a href="https://investor.sebi.gov.in/" target="_blank" class="secondary">Open SEBI Investor</a><a href="https://scores.sebi.gov.in/" target="_blank" class="secondary">Open SCORES</a><a href="https://scores.sebi.gov.in/entity-status" target="_blank" class="secondary">Verify entity</a></div>
  `;
  result.classList.remove("hidden");
  result.scrollIntoView({behavior: "smooth", block: "start"});
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#039;","\"":"&quot;"}[ch]));
}
