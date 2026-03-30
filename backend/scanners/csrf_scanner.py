"""
DAST CSRF (Cross-Site Request Forgery) Scanner Module
Checks POST forms for missing CSRF tokens and insecure cookie configurations.
"""

import requests
import logging

logger = logging.getLogger(__name__)

# Common CSRF token field names
CSRF_TOKEN_NAMES = [
    "csrf_token", "_token", "csrfmiddlewaretoken", "_csrf",
    "csrf", "xsrf_token", "_xsrf", "authenticity_token",
    "__requestverificationtoken", "antiforgerytoken",
    "csrf-token", "xsrf-token", "__csrf_magic",
    "token", "formtoken", "form_token",
]

# Common CSRF header names
CSRF_HEADER_NAMES = [
    "x-csrf-token", "x-xsrf-token", "x-csrftoken",
    "x-requested-with",
]


class CSRFScanner:
    """Cross-Site Request Forgery vulnerability scanner."""

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

    def scan(self, endpoints, target_url, cookies=None):
        """
        Scan for CSRF vulnerabilities.

        Args:
            endpoints: List of endpoint dicts from crawler
            target_url: Base target URL
            cookies: List of cookie dicts from crawler

        Returns:
            List of vulnerability dicts in standard format
        """
        vulnerabilities = []

        # Check POST forms for missing CSRF tokens
        post_forms = [ep for ep in endpoints if ep.get("method", "").upper() == "POST"]
        vulns = self._check_missing_csrf_tokens(post_forms, target_url)
        vulnerabilities.extend(vulns)

        # Check cookie SameSite attributes
        if cookies:
            vulns = self._check_cookie_samesite(cookies, target_url)
            vulnerabilities.extend(vulns)

        # Check for CSRF protection in responses
        vulns = self._check_csrf_headers(target_url)
        vulnerabilities.extend(vulns)

        return vulnerabilities

    def _check_missing_csrf_tokens(self, post_forms, target_url):
        """Check POST forms for missing CSRF token fields."""
        vulnerabilities = []

        for form in post_forms:
            endpoint = form.get("endpoint", target_url)
            params = form.get("parameters", [])
            has_csrf = form.get("has_csrf_token", False)

            if not has_csrf:
                # Double-check by looking at parameter names
                param_names = [p.get("name", "").lower() for p in params]
                has_csrf = any(
                    csrf_name in param_names
                    for csrf_name in CSRF_TOKEN_NAMES
                )

            if not has_csrf and params:
                # Check if form has any state-changing parameters
                state_changing_params = [
                    p for p in params
                    if p.get("type") not in ["hidden", "submit", "button"]
                    or p.get("name", "").lower() not in CSRF_TOKEN_NAMES
                ]

                if state_changing_params:
                    param_list = ", ".join(
                        p.get("name", "unnamed") for p in state_changing_params[:5]
                    )
                    vulnerabilities.append({
                        "name": "Missing CSRF Token",
                        "severity": "High",
                        "location": endpoint,
                        "parameter": "CSRF Token Field",
                        "description": (
                            f"POST form at '{endpoint}' does not contain a CSRF token. "
                            f"Form parameters: [{param_list}]. Without CSRF protection, "
                            f"an attacker can forge requests on behalf of authenticated users."
                        ),
                        "impact": (
                            "An attacker can create a malicious page that submits this form "
                            "on behalf of authenticated users without their knowledge, "
                            "potentially changing passwords, transferring funds, or "
                            "modifying account settings."
                        ),
                        "recommendation": (
                            "Implement CSRF tokens in all state-changing forms. Use the "
                            "synchronizer token pattern or double-submit cookie pattern. "
                            "Set SameSite cookie attribute to 'Strict' or 'Lax'."
                        ),
                        "evidence": (
                            f"POST form at {endpoint} | "
                            f"No CSRF token field found among parameters: [{param_list}]"
                        ),
                    })

        return vulnerabilities

    def _check_cookie_samesite(self, cookies, target_url):
        """Check cookies for insecure SameSite configuration."""
        vulnerabilities = []
        checked = set()

        for cookie in cookies:
            cookie_name = cookie.get("name", "")
            if cookie_name in checked:
                continue
            checked.add(cookie_name)

            same_site = cookie.get("sameSite", "").lower()

            if same_site == "none" or same_site == "" or same_site == "none":
                secure = cookie.get("secure", False)

                severity = "High" if not secure else "Medium"

                vulnerabilities.append({
                    "name": "Insecure Cookie SameSite Configuration",
                    "severity": severity,
                    "location": target_url,
                    "parameter": f"Cookie: {cookie_name}",
                    "description": (
                        f"Cookie '{cookie_name}' has SameSite={same_site or 'not set'}. "
                        f"{'Cookie is also not marked as Secure.' if not secure else ''} "
                        f"This allows the cookie to be sent with cross-site requests, "
                        f"enabling CSRF attacks."
                    ),
                    "impact": (
                        "Cross-site requests will include this cookie, allowing "
                        "attackers to forge authenticated requests from malicious sites."
                    ),
                    "recommendation": (
                        "Set the SameSite attribute to 'Strict' or 'Lax' for all "
                        "session and authentication cookies. If SameSite=None is "
                        "required, ensure the Secure flag is also set."
                    ),
                    "evidence": (
                        f"Cookie: {cookie_name} | "
                        f"SameSite: {same_site or 'not set'} | "
                        f"Secure: {secure}"
                    ),
                })

        return vulnerabilities

    def _check_csrf_headers(self, target_url):
        """Check if the application uses CSRF protection headers."""
        vulnerabilities = []

        try:
            # Make a request and check response headers
            response = self.session.get(target_url, timeout=self.timeout, verify=False)

            # Check if any CSRF-related headers are present
            response_headers_lower = {k.lower(): v for k, v in response.headers.items()}

            has_csrf_header = any(
                header in response_headers_lower
                for header in CSRF_HEADER_NAMES
            )

            # Check meta tags for CSRF token
            if "csrf" not in response.text.lower() and "xsrf" not in response.text.lower():
                if not has_csrf_header:
                    vulnerabilities.append({
                        "name": "No CSRF Protection Detected",
                        "severity": "Medium",
                        "location": target_url,
                        "parameter": "Application-wide",
                        "description": (
                            "No CSRF protection mechanism detected in the application. "
                            "No CSRF tokens found in page source or response headers."
                        ),
                        "impact": (
                            "The entire application may be vulnerable to Cross-Site "
                            "Request Forgery attacks on all state-changing operations."
                        ),
                        "recommendation": (
                            "Implement application-wide CSRF protection using a security "
                            "framework. Use the synchronizer token pattern, double-submit "
                            "cookie pattern, or custom request headers."
                        ),
                        "evidence": (
                            "No CSRF tokens in page source | "
                            "No CSRF protection headers in response"
                        ),
                    })

        except Exception as e:
            logger.debug(f"Error checking CSRF headers: {e}")

        return vulnerabilities
