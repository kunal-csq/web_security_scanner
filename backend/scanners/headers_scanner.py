"""
DAST Security Headers Scanner Module
Checks for missing or misconfigured HTTP security headers.
"""

import requests
import logging
import re

logger = logging.getLogger(__name__)


def check_headers(url):
    """
    Scan HTTP response headers for security issues.

    Args:
        url: Target URL to scan

    Returns:
        List of vulnerability dicts in standard format
    """
    vulnerabilities = []

    try:
        response = requests.get(url, timeout=10, verify=False)
        headers = response.headers

        # -----------------------------------------------
        # Content-Security-Policy (CSP)
        # -----------------------------------------------
        if "Content-Security-Policy" not in headers:
            vulnerabilities.append({
                "name": "Missing Content Security Policy",
                "severity": "High",
                "location": url,
                "parameter": "Content-Security-Policy",
                "description": (
                    "Content-Security-Policy header is missing. This header controls "
                    "which resources the browser is allowed to load, preventing XSS "
                    "and data injection attacks."
                ),
                "impact": (
                    "Without CSP, the browser will load any scripts, styles, and resources "
                    "without restriction. Attackers can inject malicious JavaScript via "
                    "Cross-Site Scripting (XSS) attacks."
                ),
                "recommendation": (
                    "Implement a strict Content-Security-Policy header. Start with: "
                    "Content-Security-Policy: default-src 'self'; script-src 'self'; "
                    "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                    "font-src 'self'; connect-src 'self'"
                ),
                "evidence": "Content-Security-Policy header not found in response",
            })
        else:
            csp_value = headers["Content-Security-Policy"]
            # Check for unsafe directives
            if "'unsafe-inline'" in csp_value and "script-src" in csp_value:
                vulnerabilities.append({
                    "name": "Weak Content Security Policy",
                    "severity": "Medium",
                    "location": url,
                    "parameter": "Content-Security-Policy",
                    "description": (
                        "CSP allows 'unsafe-inline' for scripts, which significantly "
                        "weakens XSS protection."
                    ),
                    "impact": (
                        "Inline scripts are allowed, reducing CSP effectiveness "
                        "against XSS attacks."
                    ),
                    "recommendation": (
                        "Remove 'unsafe-inline' from script-src directive. Use nonce "
                        "or hash-based CSP for inline scripts."
                    ),
                    "evidence": f"CSP: {csp_value[:200]}",
                })

            if "'unsafe-eval'" in csp_value:
                vulnerabilities.append({
                    "name": "CSP Allows Unsafe Eval",
                    "severity": "Medium",
                    "location": url,
                    "parameter": "Content-Security-Policy",
                    "description": (
                        "CSP allows 'unsafe-eval', enabling eval() and similar functions "
                        "that can execute arbitrary code strings."
                    ),
                    "impact": (
                        "Attackers can use eval-based techniques to bypass XSS filters."
                    ),
                    "recommendation": (
                        "Remove 'unsafe-eval' from CSP directives. Refactor code "
                        "to avoid eval(), new Function(), and setTimeout with strings."
                    ),
                    "evidence": f"CSP contains 'unsafe-eval': {csp_value[:200]}",
                })

            if "* " in csp_value or csp_value.strip().endswith("*"):
                vulnerabilities.append({
                    "name": "CSP Wildcard Source",
                    "severity": "Medium",
                    "location": url,
                    "parameter": "Content-Security-Policy",
                    "description": (
                        "CSP contains wildcard (*) source, allowing resources "
                        "from any origin."
                    ),
                    "impact": (
                        "Wildcard sources negate the purpose of CSP, allowing "
                        "attackers to load malicious resources from any domain."
                    ),
                    "recommendation": (
                        "Replace wildcard with specific trusted domains."
                    ),
                    "evidence": f"CSP: {csp_value[:200]}",
                })

        # -----------------------------------------------
        # X-Frame-Options
        # -----------------------------------------------
        if "X-Frame-Options" not in headers:
            vulnerabilities.append({
                "name": "Missing X-Frame-Options",
                "severity": "Medium",
                "location": url,
                "parameter": "X-Frame-Options",
                "description": (
                    "X-Frame-Options header is missing. This header prevents the page "
                    "from being embedded in iframes on other sites, protecting against "
                    "clickjacking attacks."
                ),
                "impact": (
                    "Attackers can embed the page in a transparent iframe and trick "
                    "users into clicking on hidden elements (clickjacking), potentially "
                    "performing unauthorized actions."
                ),
                "recommendation": (
                    "Add X-Frame-Options header set to DENY or SAMEORIGIN. "
                    "Also consider using CSP frame-ancestors directive."
                ),
                "evidence": "X-Frame-Options header not found in response",
            })

        # -----------------------------------------------
        # X-Content-Type-Options
        # -----------------------------------------------
        if "X-Content-Type-Options" not in headers:
            vulnerabilities.append({
                "name": "Missing X-Content-Type-Options",
                "severity": "Low",
                "location": url,
                "parameter": "X-Content-Type-Options",
                "description": (
                    "X-Content-Type-Options header is missing. Without this header, "
                    "browsers may MIME-sniff the response and interpret files as a "
                    "different content type than declared."
                ),
                "impact": (
                    "Attackers can upload files that are MIME-sniffed as executable "
                    "scripts, leading to XSS attacks through content type confusion."
                ),
                "recommendation": (
                    "Add header: X-Content-Type-Options: nosniff"
                ),
                "evidence": "X-Content-Type-Options header not found in response",
            })

        # -----------------------------------------------
        # Referrer-Policy
        # -----------------------------------------------
        if "Referrer-Policy" not in headers:
            vulnerabilities.append({
                "name": "Missing Referrer-Policy",
                "severity": "Low",
                "location": url,
                "parameter": "Referrer-Policy",
                "description": (
                    "Referrer-Policy header is missing. Without this header, the "
                    "browser may send the full URL (including sensitive query parameters) "
                    "as the Referer header when navigating to other sites."
                ),
                "impact": (
                    "Sensitive information in URLs (tokens, session IDs, search queries) "
                    "may leak to third-party sites via the Referer header."
                ),
                "recommendation": (
                    "Add Referrer-Policy header. Recommended values: "
                    "'strict-origin-when-cross-origin' or 'no-referrer'"
                ),
                "evidence": "Referrer-Policy header not found in response",
            })

        # -----------------------------------------------
        # Permissions-Policy (formerly Feature-Policy)
        # -----------------------------------------------
        if "Permissions-Policy" not in headers and "Feature-Policy" not in headers:
            vulnerabilities.append({
                "name": "Missing Permissions-Policy",
                "severity": "Low",
                "location": url,
                "parameter": "Permissions-Policy",
                "description": (
                    "Permissions-Policy header is missing. This header controls which "
                    "browser features (camera, microphone, geolocation, etc.) the page "
                    "and embedded iframes can use."
                ),
                "impact": (
                    "Without Permissions-Policy, embedded iframes and third-party scripts "
                    "can access sensitive browser APIs like camera, microphone, and "
                    "geolocation without restriction."
                ),
                "recommendation": (
                    "Add Permissions-Policy header to restrict unnecessary features: "
                    "Permissions-Policy: camera=(), microphone=(), geolocation=(), "
                    "payment=()"
                ),
                "evidence": "Permissions-Policy header not found in response",
            })

        # -----------------------------------------------
        # X-XSS-Protection (legacy but still checked)
        # -----------------------------------------------
        xss_protection = headers.get("X-XSS-Protection", "")
        if xss_protection and "0" in xss_protection:
            vulnerabilities.append({
                "name": "XSS Protection Disabled",
                "severity": "Low",
                "location": url,
                "parameter": "X-XSS-Protection",
                "description": (
                    "X-XSS-Protection is explicitly disabled (set to 0). While this "
                    "header is deprecated, disabling it removes an additional layer "
                    "of protection in older browsers."
                ),
                "impact": (
                    "Older browsers will not filter reflected XSS attacks."
                ),
                "recommendation": (
                    "Use Content-Security-Policy instead. If X-XSS-Protection is "
                    "set, use: X-XSS-Protection: 1; mode=block"
                ),
                "evidence": f"X-XSS-Protection: {xss_protection}",
            })

    except Exception as e:
        logger.error(f"Headers scan error: {e}")
        vulnerabilities.append({
            "name": "Headers Scan Failed",
            "severity": "Low",
            "location": url,
            "parameter": "HTTP Response",
            "description": f"Could not retrieve headers from {url}: {str(e)}",
            "impact": "Unable to assess header security configuration.",
            "recommendation": "Ensure the target URL is accessible and try again.",
            "evidence": f"Error: {str(e)}",
        })

    return vulnerabilities
