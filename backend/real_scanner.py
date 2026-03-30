import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime


# ---------------------------------
# 🔐 SECURITY HEADERS SCAN
# ---------------------------------
def scan_headers(url):

    vulnerabilities = []

    try:
        response = requests.get(url, timeout=5)

        headers = response.headers

        if "Content-Security-Policy" not in headers:
            vulnerabilities.append({
                "name": "Missing Content Security Policy",
                "severity": "High",
                "confidence": "High",
                "description":
                "Content-Security-Policy header is missing which can lead to XSS attacks."
            })

        if "X-Frame-Options" not in headers:
            vulnerabilities.append({
                "name": "Clickjacking Protection Missing",
                "severity": "Medium",
                "confidence": "High",
                "description":
                "X-Frame-Options header missing. Website can be embedded in malicious iframe."
            })

        if "Strict-Transport-Security" not in headers:
            vulnerabilities.append({
                "name": "HSTS Missing",
                "severity": "Medium",
                "confidence": "Medium",
                "description":
                "Strict-Transport-Security header missing. HTTPS downgrade possible."
            })

        if "X-Content-Type-Options" not in headers:
            vulnerabilities.append({
                "name": "MIME Sniffing Vulnerability",
                "severity": "Low",
                "confidence": "Medium",
                "description":
                "X-Content-Type-Options header missing. Browser may interpret files incorrectly."
            })

    except Exception:
        vulnerabilities.append({
            "name": "Connection Error",
            "severity": "Low",
            "confidence": "Low",
            "description": "Website could not be reached."
        })

    return vulnerabilities


# ---------------------------------
# 🔐 SSL CERTIFICATE SCAN
# ---------------------------------
def scan_ssl(url):

    vulnerabilities = []

    parsed = urlparse(url)
    hostname = parsed.hostname
    port = 443

    try:
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:

                cert = ssock.getpeercert()

                expiry = datetime.strptime(
                    cert['notAfter'],
                    "%b %d %H:%M:%S %Y %Z"
                )

                if expiry < datetime.utcnow():

                    vulnerabilities.append({
                        "name": "Expired SSL Certificate",
                        "severity": "Critical",
                        "confidence": "High",
                        "description":
                        "SSL certificate is expired. Man-in-the-middle attack possible."
                    })

    except Exception:

        vulnerabilities.append({
            "name": "SSL Configuration Issue",
            "severity": "Medium",
            "confidence": "Medium",
            "description":
            "SSL certificate could not be verified or TLS handshake failed."
        })

    return vulnerabilities


# ---------------------------------
# 🔐 HTTPS REDIRECT CHECK
# ---------------------------------
def scan_https_redirect(url):

    vulnerabilities = []

    if url.startswith("https"):
        return vulnerabilities

    try:

        http_url = url.replace("https://", "http://")

        response = requests.get(http_url, allow_redirects=False)

        if response.status_code != 301 and response.status_code != 302:

            vulnerabilities.append({
                "name": "HTTPS Redirection Missing",
                "severity": "High",
                "confidence": "High",
                "description":
                "Website does not redirect HTTP traffic to HTTPS."
            })

    except Exception:
        pass

    return vulnerabilities


# ---------------------------------
# 🔐 MAIN REAL SCAN FUNCTION
# ---------------------------------
def perform_real_scan(url, scans):

    results = []

    if "headers" in scans:
        results.extend(scan_headers(url))

    if "ssl" in scans:
        results.extend(scan_ssl(url))

    if "redirect" in scans:
        results.extend(scan_https_redirect(url))

    return results
