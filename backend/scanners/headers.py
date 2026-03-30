import requests

def check_headers(url):

    vulnerabilities = []

    try:
        response = requests.get(url, timeout=10)
        headers = response.headers

        # -----------------------------
        # CSP
        # -----------------------------
        if "Content-Security-Policy" not in headers:
            vulnerabilities.append({
                "name": "Missing Content Security Policy",
                "severity": "High",
                "location": url,
                "parameter": "HTTP Header",
                "description": "Content-Security-Policy header is missing which allows execution of malicious scripts.",
                "impact": "Attackers may inject malicious JavaScript leading to Cross Site Scripting (XSS).",
                "recommendation": "Implement a strict Content-Security-Policy header.",
                "confidence": "High",
                "evidence": ["CSP header not found in response"]
            })

        # -----------------------------
        # X-FRAME
        # -----------------------------
        if "X-Frame-Options" not in headers:
            vulnerabilities.append({
                "name": "Clickjacking Protection Missing",
                "severity": "Medium",
                "location": url,
                "parameter": "HTTP Header",
                "description": "X-Frame-Options header missing. Website can be embedded inside iframe.",
                "impact": "Allows attackers to perform clickjacking attacks.",
                "recommendation": "Add X-Frame-Options: DENY or SAMEORIGIN",
                "confidence": "High",
                "evidence": ["X-Frame-Options header not found"]
            })

        # -----------------------------
        # HSTS
        # -----------------------------
        if "Strict-Transport-Security" not in headers:
            vulnerabilities.append({
                "name": "HSTS Missing",
                "severity": "Medium",
                "location": url,
                "parameter": "HTTP Header",
                "description": "Strict-Transport-Security header missing.",
                "impact": "Allows downgrade attacks and MITM attacks.",
                "recommendation": "Enable HSTS using Strict-Transport-Security header.",
                "confidence": "Medium",
                "evidence": ["HSTS header not found"]
            })

        # -----------------------------
        # MIME Sniffing
        # -----------------------------
        if "X-Content-Type-Options" not in headers:
            vulnerabilities.append({
                "name": "MIME Sniffing Vulnerability",
                "severity": "Low",
                "location": url,
                "parameter": "HTTP Header",
                "description": "X-Content-Type-Options header missing.",
                "impact": "Browser may interpret files as different MIME types.",
                "recommendation": "Add X-Content-Type-Options: nosniff",
                "confidence": "Medium",
                "evidence": ["X-Content-Type-Options header not found"]
            })

    except Exception as e:
        print(e)

    return vulnerabilities
