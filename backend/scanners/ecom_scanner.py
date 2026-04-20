"""
Ecommerce Security Scanner Module
Performs 8 categories of passive/heuristic security checks specific to ecommerce websites.
All checks are non-destructive — no cart manipulation, no real purchases.

v2.0 — Accuracy rewrite: reduced false positives with baseline comparison,
SPA-aware checks, tracking cookie exclusion, and public API whitelisting.
"""

import requests
import re
import logging
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Suppress SSL warnings for scanning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# Tracking/analytics cookies that should never be flagged
TRACKING_COOKIES = {
    "_ga", "_gid", "_gat", "_fbp", "_fbc", "__cf_bm", "cf_clearance",
    "__cfduid", "_gcl_au", "NID", "1P_JAR", "CONSENT", "_hjid",
    "_hjSessionUser", "__gads", "__gpi", "_tt_enable_cookie",
}

# Public API paths that are SUPPOSED to be unauthenticated
PUBLIC_API_PATHS = {
    "/api/products", "/api/categories", "/api/search", "/api/catalog",
    "/api/v1/products", "/api/v1/categories", "/api/v1/search",
    "/api/v2/products", "/api/v2/categories",
}


class EcomScanner:
    """Ecommerce-specific security scanner with 8 sub-check categories."""

    def __init__(self, timeout=8):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(COMMON_HEADERS)
        self.session.verify = False
        self._homepage_text = None  # Cached for SPA detection

    def _get_homepage(self, url):
        """Get and cache homepage text for SPA baseline comparison."""
        if self._homepage_text is None:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                self._homepage_text = resp.text
            except Exception:
                self._homepage_text = ""
        return self._homepage_text

    def _is_spa_catchall(self, response_text, url):
        """Check if a response is just the SPA shell (React/Vue/Angular catch-all)."""
        homepage = self._get_homepage(url)
        if not homepage or not response_text:
            return False
        # If response is very similar to homepage, it's a SPA catch-all
        # (React apps return the same index.html for every route)
        if len(response_text) > 100 and abs(len(response_text) - len(homepage)) < 200:
            # Compare first 500 chars (the shell is usually identical)
            if response_text[:500] == homepage[:500]:
                return True
        return False

    def scan(self, url):
        """Run all ecommerce checks. Returns list of vulnerability dicts."""
        # Pre-cache homepage for SPA detection
        self._get_homepage(url)

        all_vulns = []
        checks = {
            "auth_account": self._check_auth_account,
            "access_control": self._check_access_control,
            "session_cookie": self._check_session_cookie,
            "ecom_logic": self._check_ecom_logic,
            "sensitive_data": self._check_sensitive_data,
            "security_misconfig": self._check_security_misconfig,
            "api_security": self._check_api_security,
            "bot_protection": self._check_bot_protection,
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(fn, url): name
                for name, fn in checks.items()
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results = future.result(timeout=30)
                    if results:
                        all_vulns.extend(results)
                    logger.info(f"[ECOM] {name}: {len(results or [])} issues")
                except Exception as e:
                    logger.error(f"[ECOM] {name} failed: {e}")

        return all_vulns

    # -----------------------------------------------
    # 1. Authentication & Account Security
    # -----------------------------------------------
    def _check_auth_account(self, url):
        vulns = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            body = resp.text.lower()

            login_paths = ["/login", "/signin", "/account/login", "/user/login", "/auth/login"]
            for path in login_paths:
                try:
                    login_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    login_body = login_resp.text.lower()

                    # Skip if it's a SPA catch-all (not a real login page)
                    if self._is_spa_catchall(login_resp.text, url):
                        continue

                    if login_resp.status_code == 200 and ("<form" in login_body):

                        # Check password field constraints
                        if 'type="password"' in login_body or "type='password'" in login_body:
                            if 'minlength' not in login_body and 'pattern=' not in login_body:
                                vulns.append({
                                    "name": "Weak Password Policy",
                                    "severity": "Medium",
                                    "location": urljoin(url, path),
                                    "parameter": "password",
                                    "description": "Login form does not enforce minimum password length or complexity requirements on the client-side.",
                                    "impact": "Users can set weak passwords, making accounts vulnerable to brute-force attacks.",
                                    "recommendation": "Enforce minimum 8-character passwords with complexity requirements (uppercase, numbers, symbols).",
                                    "evidence": f"Login form found at {path} without minlength/pattern attributes",
                                })

                        # Check for CAPTCHA — also check script tags for invisible CAPTCHA
                        captcha_keywords = ["captcha", "recaptcha", "hcaptcha", "turnstile", "g-recaptcha"]
                        has_captcha = any(kw in login_body for kw in captcha_keywords)
                        # Also check for CAPTCHA loaded via external script
                        if not has_captcha:
                            has_captcha = (
                                "recaptcha.net" in login_body
                                or "google.com/recaptcha" in login_body
                                or "hcaptcha.com" in login_body
                                or "challenges.cloudflare.com" in login_body
                            )

                        if not has_captcha:
                            vulns.append({
                                "name": "No CAPTCHA on Login",
                                "severity": "Low",
                                "location": urljoin(url, path),
                                "parameter": "login_form",
                                "description": "Login page has no visible CAPTCHA protection. Note: invisible CAPTCHA or server-side rate limiting may still be present.",
                                "impact": "If no server-side rate limiting exists, attackers can perform brute-force login attempts.",
                                "recommendation": "Implement reCAPTCHA, hCaptcha, or similar CAPTCHA on login forms.",
                                "evidence": f"No CAPTCHA elements found on {path}",
                            })

                        # REMOVED: brute-force rate-limit header check
                        # (rate limiting is server-side and not detectable passively)
                        break
                except Exception:
                    continue

            # Check for MFA indicators — search account/settings pages, not just homepage
            mfa_keywords = ["two-factor", "2fa", "mfa", "authenticator", "otp", "verification code"]
            mfa_pages = ["/account", "/settings", "/security", "/profile", "/account/security"]
            has_mfa = any(kw in body for kw in mfa_keywords)

            if not has_mfa:
                for mfa_path in mfa_pages:
                    try:
                        mfa_resp = self.session.get(urljoin(url, mfa_path), timeout=self.timeout)
                        if not self._is_spa_catchall(mfa_resp.text, url):
                            if any(kw in mfa_resp.text.lower() for kw in mfa_keywords):
                                has_mfa = True
                                break
                    except Exception:
                        continue

            if not has_mfa:
                vulns.append({
                    "name": "No MFA/2FA Detected",
                    "severity": "Low",
                    "location": url,
                    "parameter": "authentication",
                    "description": "No indication of Multi-Factor Authentication (MFA/2FA) support found on the site or its account/settings pages.",
                    "impact": "Accounts rely solely on passwords. Compromised credentials grant full access.",
                    "recommendation": "Implement MFA via TOTP (Google Authenticator), SMS, or email verification.",
                    "evidence": "No MFA/2FA/OTP keywords found in homepage or account pages",
                })

        except Exception as e:
            logger.error(f"Auth check error: {e}")
        return vulns

    # -----------------------------------------------
    # 2. Access Control
    # -----------------------------------------------
    def _check_access_control(self, url):
        vulns = []
        try:
            # Check common admin paths — with SPA-aware content validation
            admin_paths = [
                "/admin", "/admin/login", "/administrator", "/wp-admin",
                "/dashboard", "/manage", "/backend", "/control-panel",
                "/admin/dashboard", "/admin/index", "/cpanel",
                "/manager", "/moderator", "/webadmin",
            ]

            # Admin-specific content indicators (must be present for a real admin page)
            admin_indicators = [
                "admin", "dashboard", "login", "password", "username",
                "control panel", "manage", "settings",
            ]

            for path in admin_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout, allow_redirects=False)
                    if resp.status_code == 200:
                        # Skip SPA catch-all responses
                        if self._is_spa_catchall(resp.text, url):
                            continue
                        # Verify the page actually contains admin content
                        resp_lower = resp.text.lower()
                        has_admin_content = sum(
                            1 for ind in admin_indicators if ind in resp_lower
                        ) >= 2  # Need at least 2 indicators
                        if has_admin_content and "<form" in resp_lower:
                            vulns.append({
                                "name": "Admin Panel Exposed",
                                "severity": "Critical",
                                "location": urljoin(url, path),
                                "parameter": path,
                                "description": f"Admin panel accessible at {path} without authentication redirect.",
                                "impact": "Attackers can access admin functionality, potentially gaining full control of the ecommerce platform.",
                                "recommendation": "Restrict admin access by IP, require strong authentication, use non-guessable admin URLs.",
                                "evidence": f"HTTP 200 with admin form content at {path}",
                            })
                            break
                except Exception:
                    continue

            # Check for IDOR patterns — only on sensitive resources
            idor_paths = [
                "/order?id=1", "/order/1", "/orders/1",
                "/api/order/1", "/api/orders/1",
                "/invoice/1", "/receipt/1",
                "/user/1", "/profile/1", "/account/1",
            ]
            for path in idor_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if resp.status_code == 200 and len(resp.text) > 200:
                        # Skip SPA catch-all
                        if self._is_spa_catchall(resp.text, url):
                            continue
                        # Check if response actually contains order/user data
                        resp_lower = resp.text.lower()
                        data_indicators = ["order", "invoice", "email", "address", "phone", "total", "payment"]
                        has_data = sum(1 for ind in data_indicators if ind in resp_lower) >= 2
                        if has_data:
                            vulns.append({
                                "name": "Potential IDOR Vulnerability",
                                "severity": "High",
                                "location": urljoin(url, path),
                                "parameter": "id",
                                "description": f"Sequential ID endpoint {path} returns user/order data without strict authorization.",
                                "impact": "Attackers can enumerate IDs to access other users' orders, profiles, or invoices.",
                                "recommendation": "Use UUIDs instead of sequential IDs. Verify user ownership on every request.",
                                "evidence": f"HTTP 200 with data content returned for {path}",
                            })
                            break
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Access control check error: {e}")
        return vulns

    # -----------------------------------------------
    # 3. Session & Cookie Security
    # -----------------------------------------------
    def _check_session_cookie(self, url):
        vulns = []
        try:
            resp = self.session.get(url, timeout=self.timeout)

            # Check individual Set-Cookie headers for session cookies only
            set_cookie_headers = resp.raw.headers.getlist("Set-Cookie") if hasattr(resp.raw.headers, 'getlist') else []
            if not set_cookie_headers:
                raw_cookie = resp.headers.get("Set-Cookie", "")
                set_cookie_headers = [raw_cookie] if raw_cookie else []

            for cookie_str in set_cookie_headers:
                cookie_lower = cookie_str.lower()
                # Extract cookie name
                cookie_name = cookie_str.split("=")[0].strip() if "=" in cookie_str else ""

                # Skip tracking/analytics cookies
                if cookie_name in TRACKING_COOKIES:
                    continue

                if "secure" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing Secure Flag",
                        "severity": "Medium",
                        "location": url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": f"Cookie '{cookie_name}' is not marked with the Secure flag.",
                        "impact": "Cookie can be transmitted over unencrypted HTTP, allowing session hijacking via network sniffing.",
                        "recommendation": "Add Secure flag to all cookies: Set-Cookie: name=value; Secure",
                        "evidence": f"Cookie: {cookie_name} missing Secure flag",
                    })

                if "httponly" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing HttpOnly Flag",
                        "severity": "Medium",
                        "location": url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": f"Cookie '{cookie_name}' is not marked with HttpOnly flag.",
                        "impact": "JavaScript can access the cookie via document.cookie, enabling session theft through XSS.",
                        "recommendation": "Add HttpOnly flag: Set-Cookie: name=value; HttpOnly",
                        "evidence": f"Cookie: {cookie_name} missing HttpOnly flag",
                    })

                if "samesite" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing SameSite Attribute",
                        "severity": "Low",
                        "location": url,
                        "parameter": f"Cookie: {cookie_name}",
                        "description": f"Cookie '{cookie_name}' does not have SameSite attribute.",
                        "impact": "Cross-site requests will include this cookie, enabling CSRF attacks.",
                        "recommendation": "Set SameSite=Strict or SameSite=Lax on all cookies.",
                        "evidence": f"Cookie: {cookie_name} missing SameSite attribute",
                    })

            # Check cache headers
            cache_control = resp.headers.get("Cache-Control", "").lower()
            if "no-store" not in cache_control and "no-cache" not in cache_control:
                vulns.append({
                    "name": "Missing Cache-Control for Sensitive Pages",
                    "severity": "Low",
                    "location": url,
                    "parameter": "Cache-Control",
                    "description": "Sensitive ecommerce pages may be cached by browsers or proxies.",
                    "impact": "Personal data, order details, or session tokens could be stored in browser cache.",
                    "recommendation": "Set Cache-Control: no-store, no-cache, must-revalidate for authenticated pages.",
                    "evidence": f"Cache-Control: {cache_control or 'not set'}",
                })

        except Exception as e:
            logger.error(f"Session cookie check error: {e}")
        return vulns

    # -----------------------------------------------
    # 4. Ecommerce Logic Checks
    # -----------------------------------------------
    def _check_ecom_logic(self, url):
        vulns = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            body = resp.text
            body_lower = body.lower()

            # Check for client-side price fields ONLY inside <form> tags
            forms = re.findall(r'<form[^>]*>.*?</form>', body_lower, re.DOTALL)
            form_text = " ".join(forms)

            price_patterns = [
                r'name=["\']price["\']', r'name=["\']amount["\']',
                r'name=["\']total["\']', r'name=["\']cost["\']',
                r'type=["\']hidden["\'].*?name=["\']price',
            ]
            for pattern in price_patterns:
                if re.search(pattern, form_text):
                    vulns.append({
                        "name": "Client-Side Price Field Detected",
                        "severity": "Critical",
                        "location": url,
                        "parameter": "price/amount",
                        "description": "Hidden or form fields containing price/amount values found inside HTML forms. These can be modified by attackers before submission.",
                        "impact": "Attackers can change product prices to $0 or any amount, causing revenue loss.",
                        "recommendation": "Never trust client-side price values. Always calculate prices server-side from the product database.",
                        "evidence": f"Price field pattern matched inside <form> tag",
                    })
                    break

            # Check for cart-related hidden fields (only inside forms)
            cart_patterns = [
                r'name=["\']quantity["\'].*?type=["\']hidden',
                r'type=["\']hidden["\'].*?name=["\']quantity',
                r'name=["\']cart_total["\']',
                r'name=["\']discount["\'].*?type=["\']hidden',
            ]
            for pattern in cart_patterns:
                if re.search(pattern, form_text):
                    vulns.append({
                        "name": "Cart Tampering Risk",
                        "severity": "High",
                        "location": url,
                        "parameter": "quantity/cart_total",
                        "description": "Hidden form fields for cart quantities or totals found. These can be manipulated before checkout.",
                        "impact": "Attackers can modify quantities, totals, or discounts to pay less than intended.",
                        "recommendation": "Validate and recalculate all cart values server-side. Never trust client-submitted quantities or totals.",
                        "evidence": f"Cart field pattern matched inside <form> tag",
                    })
                    break

            # Check for coupon/promo inputs
            coupon_paths = ["/cart", "/checkout", "/basket"]
            for path in coupon_paths:
                try:
                    cart_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if self._is_spa_catchall(cart_resp.text, url):
                        continue
                    cart_body = cart_resp.text.lower()
                    if ("coupon" in cart_body or "promo" in cart_body or "discount" in cart_body):
                        if "limit" not in cart_body and "once" not in cart_body:
                            vulns.append({
                                "name": "Potential Coupon Abuse Vector",
                                "severity": "Medium",
                                "location": urljoin(url, path),
                                "parameter": "coupon_code",
                                "description": "Coupon/promo code input found without visible usage-limit indicators.",
                                "impact": "Same coupon may be applied multiple times or shared widely, causing revenue loss.",
                                "recommendation": "Enforce single-use coupons, per-user limits, and server-side validation.",
                                "evidence": f"Coupon input found at {path}",
                            })
                        break
                except Exception:
                    continue

            # Check for predictable order IDs
            order_patterns = [r'order[_-]?id["\s:=]+(\d+)', r'order[_-]?number["\s:=]+(\d+)']
            for pattern in order_patterns:
                match = re.search(pattern, body_lower)
                if match:
                    vulns.append({
                        "name": "Predictable Order IDs",
                        "severity": "High",
                        "location": url,
                        "parameter": "order_id",
                        "description": "Sequential/predictable order IDs detected in the page source.",
                        "impact": "Attackers can enumerate order IDs to access other customers' order details.",
                        "recommendation": "Use UUIDs or random tokens for order identifiers instead of sequential numbers.",
                        "evidence": f"Order ID pattern found: {match.group(0)[:60]}",
                    })
                    break

        except Exception as e:
            logger.error(f"Ecom logic check error: {e}")
        return vulns

    # -----------------------------------------------
    # 5. Sensitive Data Exposure
    # -----------------------------------------------
    def _check_sensitive_data(self, url):
        vulns = []
        try:
            # Check for exposed sensitive files
            sensitive_paths = [
                ("/.env", "Environment file (.env)"),
                ("/.git/HEAD", "Git repository (.git)"),
                ("/backup.sql", "Database backup"),
                ("/dump.sql", "Database dump"),
                ("/wp-config.php.bak", "WordPress config backup"),
                ("/config.php.bak", "Config backup"),
                ("/.DS_Store", "macOS DS_Store"),
            ]

            for path, desc in sensitive_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if resp.status_code == 200 and len(resp.text) > 10:
                        # Skip SPA catch-all
                        if self._is_spa_catchall(resp.text, url):
                            continue

                        # Extra validation: .env should contain KEY=VALUE, .git/HEAD should contain ref:
                        if path == "/.env" and "=" not in resp.text[:500]:
                            continue
                        if path == "/.git/HEAD" and "ref:" not in resp.text[:100]:
                            continue

                        severity = "Critical" if path in ["/.env", "/.git/HEAD", "/backup.sql", "/dump.sql"] else "High"
                        vulns.append({
                            "name": f"Exposed: {desc}",
                            "severity": severity,
                            "location": urljoin(url, path),
                            "parameter": path,
                            "description": f"{desc} is publicly accessible. This file may contain sensitive information.",
                            "impact": "Database credentials, API keys, or source code may be exposed to attackers.",
                            "recommendation": f"Block access to {path} via web server configuration. Remove sensitive files from the web root.",
                            "evidence": f"HTTP 200 returned for {path} with valid content ({len(resp.text)} bytes)",
                        })
                except Exception:
                    continue

            # Check for API keys in page source
            resp = self.session.get(url, timeout=self.timeout)
            api_patterns = [
                (r'["\']sk_live_[a-zA-Z0-9]{20,}["\']', "Stripe Secret Key"),
                (r'["\']AKIA[A-Z0-9]{16}["\']', "AWS Access Key"),
                (r'["\']ghp_[a-zA-Z0-9]{36}["\']', "GitHub Token"),
            ]
            # Note: Stripe publishable keys (pk_live_) and Google API keys are
            # intentionally excluded — they're designed to be public/client-side
            for pattern, key_type in api_patterns:
                if re.search(pattern, resp.text):
                    vulns.append({
                        "name": f"Exposed {key_type} in Source",
                        "severity": "Critical",
                        "location": url,
                        "parameter": "page_source",
                        "description": f"{key_type} found in the page HTML source code.",
                        "impact": "Attackers can use exposed API keys to access third-party services, make fraudulent payments, or steal data.",
                        "recommendation": "Remove API keys from client-side code. Use server-side proxies for API calls.",
                        "evidence": f"{key_type} pattern detected in HTML source",
                    })

        except Exception as e:
            logger.error(f"Sensitive data check error: {e}")
        return vulns

    # -----------------------------------------------
    # 6. Security Misconfiguration
    # -----------------------------------------------
    def _check_security_misconfig(self, url):
        vulns = []
        try:
            resp = self.session.get(url, timeout=self.timeout)

            # Check for debug mode / stack traces
            debug_indicators = [
                "traceback (most recent call last)", "debugging information",
                "stack trace:", "django debug", "laravel_debugbar", "xdebug",
                "phpmyadmin", "server error in", "asp.net error",
            ]
            body_lower = resp.text.lower()
            # REMOVED: "internal server error" — too generic, appears in custom error pages
            for indicator in debug_indicators:
                if indicator in body_lower:
                    vulns.append({
                        "name": "Debug Mode / Error Details Exposed",
                        "severity": "High",
                        "location": url,
                        "parameter": "debug_mode",
                        "description": "Application appears to be running in debug mode or exposing detailed error information.",
                        "impact": "Stack traces reveal internal paths, framework versions, and database details useful for attacks.",
                        "recommendation": "Disable debug mode in production. Set DEBUG=False. Use custom error pages.",
                        "evidence": f"Debug indicator found: '{indicator}'",
                    })
                    break

            # Check for directory listing
            common_dirs = ["/uploads/", "/static/", "/media/", "/assets/"]
            for dir_path in common_dirs:
                try:
                    dir_resp = self.session.get(urljoin(url, dir_path), timeout=self.timeout)
                    if dir_resp.status_code == 200 and "index of" in dir_resp.text.lower():
                        vulns.append({
                            "name": "Directory Listing Enabled",
                            "severity": "Medium",
                            "location": urljoin(url, dir_path),
                            "parameter": dir_path,
                            "description": f"Directory listing is enabled at {dir_path}, exposing all files.",
                            "impact": "Attackers can browse uploaded files, discover hidden resources, or find backup files.",
                            "recommendation": "Disable directory listing in web server config (Options -Indexes for Apache).",
                            "evidence": f"'Index of' page found at {dir_path}",
                        })
                        break
                except Exception:
                    continue

            # Check server header leakage
            server = resp.headers.get("Server", "")
            x_powered = resp.headers.get("X-Powered-By", "")
            if server and any(v in server.lower() for v in ["apache/", "nginx/", "iis/"]):
                vulns.append({
                    "name": "Server Version Disclosed",
                    "severity": "Low",
                    "location": url,
                    "parameter": "Server",
                    "description": f"Server header reveals version information: {server}",
                    "impact": "Attackers can lookup known vulnerabilities for the specific server version.",
                    "recommendation": "Remove or generalize the Server header. For Nginx: server_tokens off;",
                    "evidence": f"Server: {server}",
                })
            if x_powered:
                vulns.append({
                    "name": "Technology Stack Disclosed",
                    "severity": "Low",
                    "location": url,
                    "parameter": "X-Powered-By",
                    "description": f"X-Powered-By header reveals: {x_powered}",
                    "impact": "Reveals the technology stack, helping attackers target specific framework vulnerabilities.",
                    "recommendation": "Remove the X-Powered-By header from responses.",
                    "evidence": f"X-Powered-By: {x_powered}",
                })

        except Exception as e:
            logger.error(f"Security misconfig check error: {e}")
        return vulns

    # -----------------------------------------------
    # 7. API Security
    # -----------------------------------------------
    def _check_api_security(self, url):
        vulns = []
        try:
            # Check common API paths — skip known public endpoints
            api_paths = [
                "/api", "/api/v1", "/api/v2",
                "/api/products", "/api/users", "/api/orders",
                "/graphql", "/api/graphql",
            ]

            for path in api_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if resp.status_code == 200:
                        content_type = resp.headers.get("Content-Type", "").lower()
                        if "json" in content_type and len(resp.text) > 50:
                            # Skip public API paths — they're supposed to be open
                            if path in PUBLIC_API_PATHS:
                                continue

                            vulns.append({
                                "name": "Unauthenticated API Access",
                                "severity": "High",
                                "location": urljoin(url, path),
                                "parameter": path,
                                "description": f"API endpoint {path} returns data without requiring authentication.",
                                "impact": "Attackers can access user information or order details without login.",
                                "recommendation": "Require authentication tokens for all sensitive API endpoints. Use OAuth 2.0 or API keys.",
                                "evidence": f"JSON response ({len(resp.text)} bytes) at {path} without auth",
                            })

                        # Check for rate limiting (only on sensitive APIs)
                        rate_headers = ["x-ratelimit-limit", "x-ratelimit-remaining"]
                        has_rate = any(h in [k.lower() for k in resp.headers.keys()] for h in rate_headers)
                        if not has_rate and "json" in content_type and path not in PUBLIC_API_PATHS:
                            vulns.append({
                                "name": "API Missing Rate Limiting",
                                "severity": "Low",
                                "location": urljoin(url, path),
                                "parameter": "rate_limit",
                                "description": f"API endpoint {path} has no rate-limiting headers. Note: server-side rate limiting may still exist.",
                                "impact": "Without rate limiting, attackers can flood the API with requests.",
                                "recommendation": "Implement rate limiting (e.g., 100 requests/minute per IP).",
                                "evidence": f"No X-RateLimit headers at {path}",
                            })
                        break
                except Exception:
                    continue

            # Check for GraphQL introspection
            try:
                gql_resp = self.session.post(
                    urljoin(url, "/graphql"),
                    json={"query": "{ __schema { types { name } } }"},
                    timeout=self.timeout,
                )
                if gql_resp.status_code == 200 and "__schema" in gql_resp.text:
                    vulns.append({
                        "name": "GraphQL Introspection Enabled",
                        "severity": "Medium",
                        "location": urljoin(url, "/graphql"),
                        "parameter": "introspection",
                        "description": "GraphQL introspection is enabled, exposing the entire API schema.",
                        "impact": "Attackers can discover all queries, mutations, and data types to craft targeted attacks.",
                        "recommendation": "Disable introspection in production: { introspection: false }",
                        "evidence": "Introspection query returned __schema data",
                    })
            except Exception:
                pass

        except Exception as e:
            logger.error(f"API security check error: {e}")
        return vulns

    # -----------------------------------------------
    # 8. Bot & Abuse Protection
    # -----------------------------------------------
    def _check_bot_protection(self, url):
        vulns = []
        try:
            # Check registration page for CAPTCHA
            captcha_keywords = ["captcha", "recaptcha", "hcaptcha", "turnstile", "g-recaptcha"]
            captcha_scripts = ["recaptcha.net", "google.com/recaptcha", "hcaptcha.com", "challenges.cloudflare.com"]

            reg_paths = ["/register", "/signup", "/create-account", "/account/register"]
            for path in reg_paths:
                try:
                    reg_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if self._is_spa_catchall(reg_resp.text, url):
                        continue
                    if reg_resp.status_code == 200 and "<form" in reg_resp.text.lower():
                        reg_body = reg_resp.text.lower()
                        has_captcha = (
                            any(kw in reg_body for kw in captcha_keywords)
                            or any(script in reg_body for script in captcha_scripts)
                        )
                        if not has_captcha:
                            vulns.append({
                                "name": "No CAPTCHA on Registration",
                                "severity": "Low",
                                "location": urljoin(url, path),
                                "parameter": "registration_form",
                                "description": "Registration form has no visible CAPTCHA protection. Invisible CAPTCHA may still be present.",
                                "impact": "Bots can create fake accounts in bulk for spam, fraud, or inventory hoarding.",
                                "recommendation": "Add CAPTCHA to registration forms to prevent automated account creation.",
                                "evidence": f"Registration form at {path} without CAPTCHA",
                            })
                        break
                except Exception:
                    continue

            # REMOVED: "Weak Anti-Bot Defenses" check
            # It was checking X-Frame-Options, X-Content-Type-Options, HSTS
            # which are general security headers, NOT bot-specific defenses.
            # This duplicated the headers_scanner checks.

        except Exception as e:
            logger.error(f"Bot protection check error: {e}")
        return vulns
