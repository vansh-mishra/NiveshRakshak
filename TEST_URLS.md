# NiveshRakshak URL tests

Paste these into the **Suspicious URL** field:

- `https://profit-sebi-verify.top/login` -> should return a meaningful MEDIUM/HIGH URL risk result.
- `http://198.51.100.10/login` -> should trigger raw-IP and no-HTTPS signals.
- `https://scores.sebi.gov.in/` -> recognized official-domain pattern; LOW does not mean the content is guaranteed safe.
- `https://example.com` -> no strong URL warning signal.

You can also paste a full URL directly into the **Investment message** box. The backend now extracts the URL automatically.
