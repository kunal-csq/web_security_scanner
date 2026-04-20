"""
DAST Authentication Security Scanner Module
Checks session management, cookie security, and JWT token leakage.
"""

import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Session-related cookie name patterns
SESSION_COOKIE_PATTERNS = [
    "sessionid", "session_id", "sid", "phpsessid",
    "jsessionid", "asp.net_sessionid", "cfid", "cftoken",
    "connect.sid", "sess", "token", "auth", "jwt",
    "access_token", "refresh_token", "id_token",
]

# Known tracking/analytics cookies — NEVER flag these
TRACKING_COOKIES = {
    "_ga", "_gid", "_gat", "_fbp", "_fbc", "__cf_bm", "cf_clearance",
    "__cfduid", "_gcl_au", "NID", "1P_JAR", "CONSENT", "_hjid",
    "_hjSessionUser", "__gads", "__gpi", "_tt_enable_cookie", "APISID",
    "HSID", "SSID", "SID", "SAPISID", "__Secure-1PSID", "__Secure-3PSID",
}


class AuthScanner:
    """Authentication and session security scanner."""

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
        Scan for authentication and session security issues.

        Args:
            endpoints: List of endpoint dicts from crawler
            target_url: Base target URL
            cookies: List of cookie dicts from crawler

        Returns:
            List of vulnerability dicts in standard format
        """
        vulnerabilities = []

        # Check cookie security flags
        vulns = self._check_cookie_security(target_url, cookies)
        vulnerabilities.extend(vulns)

        # Check session ID rotation
        vulns = self._check_session_rotation(target_url)
        vulnerabilities.extend(vulns)

        # Check for sensitive data in response headers
        vulns = self._check_sensitive_headers(target_url)
        vulnerabilities.extend(vulns)

        return vulnerabilities

    def scan_jwt_leakage(self, driver, target_url):
        """
        Use Selenium to check localStorage/sessionStorage for JWT tokens.

        Args:
            driver: Selenium WebDriver instance
            target_url: Base target URL

        Returns:
            List of vulnerability dicts
        """
        vulnerabilities = []

        try:
            driver.get(target_url)
            import time
            time.sleep(3)

            # Check localStorage
            local_storage_items = driver.execute_script(
                """
                var items = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
                """
            )

            # Check sessionStorage
            session_storage_items = driver.execute_script(
                """
                var items = {};
                for (var i = 0; i < sessionStorage.length; i++) {
                    var key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
                """
            )

            # Look for JWT tokens in storage
            jwt_pattern = "eyJ"  # Base64 encoded JWT header prefix

            for storage_name, items in [
                ("localStorage", local_storage_items),
                ("sessionStorage", session_storage_items),
            ]:
                if not items:
                    continue

                for key, value in items.items():
                    if isinstance(value, str) and jwt_pattern in value:
                        vulnerabilities.append({
                            "name": "JWT Token in Browser Storage",
                            "severity": "High",
                            "location": target_url,
                            "parameter": f"{storage_name}.{key}",
                            "description": (
                                f"A JWT token was found stored in {storage_name} "
                                f"under key '{key}'. Storing JWTs in browser storage "
                                f"makes them accessible to JavaScript and vulnerable "
                                f"to XSS-based token theft."
                            ),
                            "impact": (
                                "If an XSS vulnerability exists, an attacker can steal "
                                "the JWT token and impersonate the user. JWT tokens in "
                                "storage are not protected by HttpOnly flag."
                            ),
                            "recommendation": (
                                "Store JWT tokens in HttpOnly secure cookies instead "
                                "of browser storage. If storage is required, use short "
                                "expiration times and implement token rotation."
                            ),
                            "evidence": (
                                f"JWT found in {storage_name}['{key}'] | "
                                f"Token prefix: {value[:50]}..."
                            ),
                        })

                    # Check for other sensitive-looking tokens
                    sensitive_keys = [
                        "token", "auth", "key", "secret",
                        "password", "credential", "api_key",
                    ]
                    if any(sk in key.lower() for sk in sensitive_keys):
                        if jwt_pattern not in (value or ""):
                            vulnerabilities.append({
                                "name": "Sensitive Token in Browser Storage",
                                "severity": "Medium",
                                "location": target_url,
                                "parameter": f"{storage_name}.{key}",
                                "description": (
                                    f"A potentially sensitive token '{key}' was found in "
                                    f"{storage_name}. Storing authentication tokens in "
                                    f"browser storage exposes them to XSS attacks."
                                ),
                                "impact": (
                                    "Authentication tokens accessible via JavaScript "
                                    "can be stolen through XSS attacks."
                                ),
                                "recommendation": (
                                    "Use HttpOnly cookies for sensitive tokens. "
                                    "If storage is needed, encrypt the values."
                                ),
                                "evidence": (
                                    f"Sensitive key '{key}' found in {storage_name}"
                                ),
                            })

        except Exception as e:
            logger.debug(f"Error checking JWT leakage: {e}")

        return vulnerabilities

    def _check_cookie_security(self, target_url, cookies=None):
        """Check cookie security flags (HttpOnly, Secure)."""
        vulnerabilities = []

        # Use cookies from crawler if available
        if cookies:
            for cookie in cookies:
                cookie_name = cookie.get("name", "")
                is_session = self._is_session_cookie(cookie_name)

                if not is_session:
                    continue

                # Check HttpOnly
                if not cookie.get("httpOnly", False):
                    vulnerabilities.append({
                        "name": "Missing HttpOnly Cookie Flag",
                        "severity": "High",
                        "location": target_url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": (
                            f"Session cookie '{cookie_name}' is not marked as HttpOnly. "
                            f"This allows JavaScript to access the cookie value, making "
                            f"it vulnerable to XSS-based session hijacking."
                        ),
                        "impact": (
                            "An attacker exploiting an XSS vulnerability can steal "
                            "the session cookie using document.cookie and hijack "
                            "the user's session."
                        ),
                        "recommendation": (
                            "Set the HttpOnly flag on all session and authentication "
                            "cookies to prevent JavaScript access."
                        ),
                        "evidence": (
                            f"Cookie: {cookie_name} | HttpOnly: False"
                        ),
                    })

                # Check Secure flag
                if not cookie.get("secure", False):
                    parsed = urlparse(target_url)
                    if parsed.scheme == "https":
                        vulnerabilities.append({
                            "name": "Missing Secure Cookie Flag",
                            "severity": "High",
                            "location": target_url,
                            "parameter": f"Cookie: {cookie_name}",
                            "description": (
                                f"Session cookie '{cookie_name}' is not marked as Secure "
                                f"despite the site using HTTPS. The cookie can be "
                                f"transmitted over unencrypted HTTP connections."
                            ),
                            "impact": (
                                "The session cookie can be intercepted by an attacker "
                                "performing a man-in-the-middle attack if the user "
                                "accesses the site over HTTP."
                            ),
                            "recommendation": (
                                "Set the Secure flag on all session cookies to ensure "
                                "they are only transmitted over HTTPS."
                            ),
                            "evidence": (
                                f"Cookie: {cookie_name} | Secure: False | "
                                f"Site uses HTTPS"
                            ),
                        })

        # Also check via HTTP requests
        try:
            response = self.session.get(
                target_url, timeout=self.timeout, verify=False
            )

            for cookie in response.cookies:
                cookie_name = cookie.name
                if not self._is_session_cookie(cookie_name):
                    continue

                # Check if already reported from crawler cookies
                if cookies and any(
                    c.get("name") == cookie_name for c in cookies
                ):
                    continue

                if not cookie.has_nonstandard_attr("HttpOnly"):
                    vulnerabilities.append({
                        "name": "Missing HttpOnly Cookie Flag",
                        "severity": "High",
                        "location": target_url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": (
                            f"Session cookie '{cookie_name}' does not have the "
                            f"HttpOnly flag set."
                        ),
                        "impact": (
                            "Session cookie accessible via JavaScript, enabling "
                            "XSS-based session hijacking."
                        ),
                        "recommendation": (
                            "Set the HttpOnly flag on all session cookies."
                        ),
                        "evidence": f"Cookie: {cookie_name} | HttpOnly: not set",
                    })

                if not cookie.secure:
                    vulnerabilities.append({
                        "name": "Missing Secure Cookie Flag",
                        "severity": "Medium",
                        "location": target_url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": (
                            f"Cookie '{cookie_name}' does not have the Secure flag."
                        ),
                        "impact": (
                            "Cookie may be transmitted over unencrypted connections."
                        ),
                        "recommendation": (
                            "Set the Secure flag on all sensitive cookies."
                        ),
                        "evidence": f"Cookie: {cookie_name} | Secure: False",
                    })

        except Exception as e:
            logger.debug(f"Error checking cookies via HTTP: {e}")

        return vulnerabilities

    def _check_session_rotation(self, target_url):
        """Check if session IDs change between requests (session fixation risk)."""
        vulnerabilities = []

        try:
            session1 = requests.Session()
            session1.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            })
            response1 = session1.get(target_url, timeout=self.timeout, verify=False)
            cookies1 = {c.name: c.value for c in response1.cookies}

            session2 = requests.Session()
            session2.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            })
            response2 = session2.get(target_url, timeout=self.timeout, verify=False)
            cookies2 = {c.name: c.value for c in response2.cookies}

            for name in cookies1:
                # Skip tracking cookies — they're SUPPOSED to be the same
                if name in TRACKING_COOKIES:
                    continue
                if self._is_session_cookie(name):
                    if name in cookies2 and cookies1[name] == cookies2[name]:
                        vulnerabilities.append({
                            "name": "Session Fixation Risk",
                            "severity": "Medium",
                            "location": target_url,
                            "parameter": f"Cookie: {name}",
                            "description": (
                                f"Session cookie '{name}' has the same value across "
                                f"different sessions. This may indicate that session "
                                f"IDs are not properly rotated."
                            ),
                            "impact": (
                                "An attacker can fix a known session ID and trick "
                                "a user into authenticating with it, then hijack "
                                "the authenticated session."
                            ),
                            "recommendation": (
                                "Regenerate session IDs after authentication and "
                                "at regular intervals. Invalidate old session IDs."
                            ),
                            "evidence": (
                                f"Cookie '{name}' identical across two separate "
                                f"sessions: {cookies1[name][:20]}..."
                            ),
                        })

        except Exception as e:
            logger.debug(f"Error checking session rotation: {e}")

        return vulnerabilities

    def _check_sensitive_headers(self, target_url):
        """Check for sensitive information in response headers."""
        vulnerabilities = []

        try:
            response = self.session.get(
                target_url, timeout=self.timeout, verify=False
            )
            headers = response.headers

            # Check for server information disclosure
            if "Server" in headers:
                server_value = headers["Server"]
                if any(
                    indicator in server_value.lower()
                    for indicator in ["apache/", "nginx/", "iis/", "express"]
                ):
                    vulnerabilities.append({
                        "name": "Server Version Disclosure",
                        "severity": "Low",
                        "location": target_url,
                        "parameter": "Server Header",
                        "description": (
                            f"The Server header reveals version information: "
                            f"'{server_value}'. This helps attackers identify "
                            f"known vulnerabilities for this server version."
                        ),
                        "impact": (
                            "Server version disclosure aids attackers in "
                            "identifying and exploiting known vulnerabilities."
                        ),
                        "recommendation": (
                            "Remove or obscure server version information "
                            "from the Server response header."
                        ),
                        "evidence": f"Server: {server_value}",
                    })

            # Check for X-Powered-By
            if "X-Powered-By" in headers:
                vulnerabilities.append({
                    "name": "Technology Stack Disclosure",
                    "severity": "Low",
                    "location": target_url,
                    "parameter": "X-Powered-By Header",
                    "description": (
                        f"The X-Powered-By header reveals technology: "
                        f"'{headers['X-Powered-By']}'. This aids attackers."
                    ),
                    "impact": (
                        "Framework disclosure helps attackers identify "
                        "framework-specific vulnerabilities."
                    ),
                    "recommendation": (
                        "Remove the X-Powered-By header from responses."
                    ),
                    "evidence": f"X-Powered-By: {headers['X-Powered-By']}",
                })

        except Exception as e:
            logger.debug(f"Error checking sensitive headers: {e}")

        return vulnerabilities

    def _is_session_cookie(self, cookie_name):
        """Check if a cookie name looks like a session cookie (excludes tracking)."""
        if cookie_name in TRACKING_COOKIES:
            return False
        name_lower = cookie_name.lower()
        return any(pattern in name_lower for pattern in SESSION_COOKIE_PATTERNS)
