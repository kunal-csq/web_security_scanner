"""
DAST XSS (Cross-Site Scripting) Scanner Module
Tests endpoints for reflected and stored XSS using payload injection
and optional Selenium DOM analysis.
"""

import requests
import logging
import html
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# ------------------------------------
# XSS Payloads
# ------------------------------------
REFLECTED_PAYLOADS = [
    '<script>alert(1)</script>',
    '"><svg onload=alert(1)>',
    '<img src=x onerror=alert(1)>',
    "'-alert(1)-'",
    '<body onload=alert(1)>',
    '"><img src=x onerror=alert(1)>',
    "javascript:alert(1)",
    '<iframe src="javascript:alert(1)">',
    '<details open ontoggle=alert(1)>',
    '{{7*7}}',  # Template injection probe
]

DOM_PAYLOADS = [
    '<script>document.write("XSS_MARKER_DOM")</script>',
    '<img src=x onerror=document.title="XSS_MARKER_DOM">',
    '"><script>document.title="XSS_MARKER_DOM"</script>',
]

CONTEXT_PAYLOADS = {
    "html_tag": [
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
        '<img src=x onerror=alert(1)>',
    ],
    "html_attr": [
        '" onmouseover="alert(1)',
        "' onmouseover='alert(1)",
        '" autofocus onfocus="alert(1)',
    ],
    "javascript": [
        "';alert(1);//",
        '";alert(1);//',
        "-alert(1)-",
        "</script><script>alert(1)</script>",
    ],
}


class XSSScanner:
    """Cross-Site Scripting vulnerability scanner."""

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def scan(self, endpoints, target_url):
        """
        Scan all endpoints for XSS vulnerabilities.

        Args:
            endpoints: List of endpoint dicts from crawler
            target_url: Base target URL

        Returns:
            List of vulnerability dicts in standard format
        """
        vulnerabilities = []

        for endpoint in endpoints:
            ep_url = endpoint.get("endpoint", target_url)
            method = endpoint.get("method", "GET").upper()
            params = endpoint.get("parameters", [])

            for param in params:
                param_name = param.get("name", "")
                if not param_name:
                    continue

                # Skip non-injectable types
                if param.get("type") in ["submit", "button", "file", "image"]:
                    continue

                # Reflected XSS tests
                vulns = self._test_reflected_xss(ep_url, method, param_name)
                vulnerabilities.extend(vulns)

        return vulnerabilities

    def _test_reflected_xss(self, url, method, param_name):
        """Test for reflected XSS with baseline comparison to reduce false positives."""
        vulnerabilities = []

        # Get baseline response to filter out content that already exists on page
        baseline = self._make_request(url, method, {param_name: "safetest123"})
        baseline_text = baseline.text if baseline else ""

        for payload in REFLECTED_PAYLOADS:
            try:
                response = self._make_request(url, method, {param_name: payload})
                if not response:
                    continue

                response_text = response.text

                # Check if payload is reflected unescaped AND not in baseline
                if payload in response_text and payload not in baseline_text:
                    xss_type = self._classify_xss(response_text, payload)
                    context = self._detect_context(response_text, payload)

                    vulnerabilities.append({
                        "name": f"Cross-Site Scripting ({xss_type})",
                        "severity": "High" if xss_type == "Reflected" else "Critical",
                        "location": url,
                        "parameter": param_name,
                        "description": (
                            f"{xss_type} XSS detected in parameter '{param_name}'. "
                            f"The payload is reflected unescaped in the {context} context "
                            f"of the response, allowing arbitrary JavaScript execution."
                        ),
                        "impact": (
                            "An attacker can execute arbitrary JavaScript in the victim's "
                            "browser, leading to session hijacking, cookie theft, "
                            "keylogging, phishing, and defacement."
                        ),
                        "recommendation": (
                            "Implement context-aware output encoding. Use Content-Security-Policy "
                            "headers. Validate and sanitize all user inputs. Use frameworks "
                            "with built-in XSS protection (React, Angular)."
                        ),
                        "evidence": (
                            f"Payload: {payload} | "
                            f"Type: {xss_type} | "
                            f"Context: {context} | "
                            f"Payload reflected unescaped in response body"
                        ),
                    })
                    break  # One confirmed per param is enough

                # Partial reflection REMOVED — too many false positives

            except Exception as e:
                logger.debug(f"Error testing XSS on {url}: {e}")

        return vulnerabilities

    def scan_dom_xss(self, driver, endpoints, target_url):
        """
        Use Selenium to test for DOM-based XSS.

        Args:
            driver: Selenium WebDriver instance
            endpoints: List of endpoint dicts
            target_url: Base target URL

        Returns:
            List of vulnerability dicts
        """
        vulnerabilities = []

        for endpoint in endpoints:
            ep_url = endpoint.get("endpoint", target_url)
            params = endpoint.get("parameters", [])

            for param in params:
                param_name = param.get("name", "")
                if not param_name:
                    continue

                for payload in DOM_PAYLOADS:
                    try:
                        # Build test URL with payload in query param
                        test_url = f"{ep_url}?{param_name}={payload}"
                        driver.get(test_url)

                        import time
                        time.sleep(2)

                        # Check page title for our marker
                        if "XSS_MARKER_DOM" in driver.title:
                            vulnerabilities.append({
                                "name": "Cross-Site Scripting (DOM-Based)",
                                "severity": "High",
                                "location": ep_url,
                                "parameter": param_name,
                                "description": (
                                    f"DOM-based XSS confirmed in parameter '{param_name}'. "
                                    f"The payload was executed in the browser DOM, modifying "
                                    f"the page title to our marker value."
                                ),
                                "impact": (
                                    "An attacker can execute JavaScript through DOM manipulation, "
                                    "leading to session hijacking and data theft."
                                ),
                                "recommendation": (
                                    "Sanitize all DOM sinks (innerHTML, document.write, eval). "
                                    "Use textContent instead of innerHTML. Implement CSP."
                                ),
                                "evidence": (
                                    f"Payload: {payload} | "
                                    f"DOM Evidence: document.title changed to 'XSS_MARKER_DOM'"
                                ),
                            })
                            break

                        # Check page source for unescaped payload
                        page_source = driver.page_source
                        if payload in page_source:
                            vulnerabilities.append({
                                "name": "Cross-Site Scripting (DOM Reflected)",
                                "severity": "High",
                                "location": ep_url,
                                "parameter": param_name,
                                "description": (
                                    f"XSS payload reflected in DOM for parameter '{param_name}'. "
                                    f"The payload appears unescaped in the rendered page source."
                                ),
                                "impact": (
                                    "Browser may execute the injected script, enabling "
                                    "session hijacking and credential theft."
                                ),
                                "recommendation": (
                                    "Encode all user input before DOM insertion. "
                                    "Use safe DOM APIs like textContent."
                                ),
                                "evidence": (
                                    f"Payload: {payload} | "
                                    f"DOM Evidence: Payload found in rendered page source"
                                ),
                            })
                            break

                    except Exception as e:
                        logger.debug(f"Error testing DOM XSS: {e}")

        return vulnerabilities

    def _classify_xss(self, response_text, payload):
        """Classify XSS type based on reflection analysis."""
        # Check if stored (appears even without the payload in the request)
        # For reflected scan, default to Reflected
        return "Reflected"

    def _detect_context(self, response_text, payload):
        """Detect the HTML context where the payload is reflected."""
        idx = response_text.find(payload)
        if idx == -1:
            return "unknown"

        # Check surrounding content
        before = response_text[max(0, idx - 100):idx].lower()

        if "<script" in before and "</script>" not in before:
            return "JavaScript"
        elif re.search(r'<\w+[^>]*\w+=\s*["\']?[^"\']*$', before):
            return "HTML attribute"
        else:
            return "HTML body"

    def _check_partial_reflection(self, response_text, payload):
        """Check if payload is partially reflected (some chars encoded)."""
        # Check if the alphanumeric parts of the payload appear
        alpha_parts = re.findall(r'[a-zA-Z0-9]+', payload)
        if len(alpha_parts) >= 2:
            return all(part in response_text for part in alpha_parts if len(part) > 2)
        return False

    def _make_request(self, url, method, params, timeout=None):
        """Make an HTTP request with the given parameters."""
        timeout = timeout or self.timeout
        try:
            if method == "GET":
                return self.session.get(url, params=params, timeout=timeout, verify=False)
            elif method == "POST":
                return self.session.post(url, data=params, timeout=timeout, verify=False)
            else:
                return self.session.get(url, params=params, timeout=timeout, verify=False)
        except Exception as e:
            logger.debug(f"Request error: {e}")
            return None
