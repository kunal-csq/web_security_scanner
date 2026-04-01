"""
Ecommerce Security Scanner Module
Performs 8 categories of passive/heuristic security checks specific to ecommerce websites.
All checks are non-destructive — no cart manipulation, no real purchases.
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


class EcomScanner:
    """Ecommerce-specific security scanner with 8 sub-check categories."""

    def __init__(self, timeout=8):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(COMMON_HEADERS)
        self.session.verify = False

    def scan(self, url):
        """Run all ecommerce checks. Returns list of vulnerability dicts."""
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

            # Check for login forms with weak password policy indicators
            login_paths = ["/login", "/signin", "/account/login", "/user/login", "/auth/login"]
            for path in login_paths:
                try:
                    login_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if login_resp.status_code == 200 and ("<form" in login_resp.text.lower()):
                        login_body = login_resp.text.lower()

                        # Check password field constraints
                        if 'type="password"' in login_body or "type='password'" in login_body:
                            # Check for lack of password requirements
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

                        # Check for CAPTCHA
                        if "captcha" not in login_body and "recaptcha" not in login_body and "hcaptcha" not in login_body:
                            vulns.append({
                                "name": "No CAPTCHA on Login",
                                "severity": "Medium",
                                "location": urljoin(url, path),
                                "parameter": "login_form",
                                "description": "Login page has no CAPTCHA protection against automated attacks.",
                                "impact": "Attackers can perform brute-force login attempts without any rate-limiting challenge.",
                                "recommendation": "Implement reCAPTCHA, hCaptcha, or similar CAPTCHA on login forms.",
                                "evidence": f"No CAPTCHA elements found on {path}",
                            })

                        # Check for rate limiting headers
                        rate_headers = ["x-ratelimit-limit", "x-ratelimit-remaining", "retry-after"]
                        has_rate_limit = any(h in [k.lower() for k in login_resp.headers.keys()] for h in rate_headers)
                        if not has_rate_limit:
                            vulns.append({
                                "name": "No Brute-Force Protection Detected",
                                "severity": "High",
                                "location": urljoin(url, path),
                                "parameter": "rate_limiting",
                                "description": "No rate-limiting headers detected on the login endpoint.",
                                "impact": "Attackers can perform unlimited login attempts to guess credentials.",
                                "recommendation": "Implement rate limiting (e.g., max 5 attempts per minute) and account lockout after 10 failures.",
                                "evidence": "No X-RateLimit-* or Retry-After headers found",
                            })
                        break
                except Exception:
                    continue

            # Check for MFA indicators
            mfa_keywords = ["two-factor", "2fa", "mfa", "authenticator", "otp", "verification code"]
            has_mfa = any(kw in body for kw in mfa_keywords)
            if not has_mfa:
                vulns.append({
                    "name": "No MFA/2FA Detected",
                    "severity": "Medium",
                    "location": url,
                    "parameter": "authentication",
                    "description": "No indication of Multi-Factor Authentication (MFA/2FA) support found on the site.",
                    "impact": "Accounts rely solely on passwords. Compromised credentials grant full access.",
                    "recommendation": "Implement MFA via TOTP (Google Authenticator), SMS, or email verification.",
                    "evidence": "No MFA/2FA/OTP keywords found in page content",
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
            # Check common admin paths
            admin_paths = [
                "/admin", "/admin/login", "/administrator", "/wp-admin",
                "/dashboard", "/manage", "/backend", "/control-panel",
                "/admin/dashboard", "/admin/index", "/cpanel",
                "/manager", "/moderator", "/webadmin",
            ]
            for path in admin_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout, allow_redirects=False)
                    if resp.status_code == 200:
                        vulns.append({
                            "name": "Admin Panel Exposed",
                            "severity": "Critical",
                            "location": urljoin(url, path),
                            "parameter": path,
                            "description": f"Admin panel accessible at {path} without authentication redirect.",
                            "impact": "Attackers can access admin functionality, potentially gaining full control of the ecommerce platform.",
                            "recommendation": "Restrict admin access by IP, require strong authentication, use non-guessable admin URLs.",
                            "evidence": f"HTTP 200 returned for {path}",
                        })
                        break
                except Exception:
                    continue

            # Check for IDOR patterns (sequential order IDs)
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
                        vulns.append({
                            "name": "Potential IDOR Vulnerability",
                            "severity": "High",
                            "location": urljoin(url, path),
                            "parameter": "id",
                            "description": f"Sequential ID endpoint {path} returns data without strict authorization.",
                            "impact": "Attackers can enumerate IDs to access other users' orders, profiles, or invoices.",
                            "recommendation": "Use UUIDs instead of sequential IDs. Verify user ownership on every request.",
                            "evidence": f"HTTP 200 with content returned for {path}",
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
            cookies = resp.headers.get("Set-Cookie", "")

            if cookies:
                cookie_lower = cookies.lower()

                if "secure" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing Secure Flag",
                        "severity": "High",
                        "location": url,
                        "parameter": "Set-Cookie",
                        "description": "Session cookies are not marked with the Secure flag.",
                        "impact": "Cookies can be transmitted over unencrypted HTTP, allowing session hijacking via network sniffing.",
                        "recommendation": "Add Secure flag to all cookies: Set-Cookie: session=abc; Secure",
                        "evidence": f"Cookie header: {cookies[:150]}",
                    })

                if "httponly" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing HttpOnly Flag",
                        "severity": "High",
                        "location": url,
                        "parameter": "Set-Cookie",
                        "description": "Session cookies are not marked with HttpOnly flag.",
                        "impact": "JavaScript can access cookies via document.cookie, enabling session theft through XSS attacks.",
                        "recommendation": "Add HttpOnly flag: Set-Cookie: session=abc; HttpOnly",
                        "evidence": f"Cookie header: {cookies[:150]}",
                    })

                if "samesite" not in cookie_lower:
                    vulns.append({
                        "name": "Cookie Missing SameSite Attribute",
                        "severity": "Medium",
                        "location": url,
                        "parameter": "Set-Cookie",
                        "description": "Cookies do not have SameSite attribute, leaving them vulnerable to CSRF attacks.",
                        "impact": "Cross-site requests will include cookies, enabling CSRF attacks on payment and cart actions.",
                        "recommendation": "Set SameSite=Strict or SameSite=Lax on all cookies.",
                        "evidence": f"Cookie header: {cookies[:150]}",
                    })

            # Check session timeout
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

            # Check for client-side price fields
            price_patterns = [
                r'name=["\']price["\']', r'name=["\']amount["\']',
                r'name=["\']total["\']', r'name=["\']cost["\']',
                r'type=["\']hidden["\'].*?name=["\']price',
                r'data-price=', r'data-amount=',
            ]
            for pattern in price_patterns:
                if re.search(pattern, body_lower):
                    vulns.append({
                        "name": "Client-Side Price Field Detected",
                        "severity": "Critical",
                        "location": url,
                        "parameter": "price/amount",
                        "description": "Hidden or form fields containing price/amount values found in HTML. These can be modified by attackers before submission.",
                        "impact": "Attackers can change product prices to $0 or any amount, causing revenue loss.",
                        "recommendation": "Never trust client-side price values. Always calculate prices server-side from the product database.",
                        "evidence": f"Pattern matched: {pattern}",
                    })
                    break

            # Check for cart-related hidden fields
            cart_patterns = [
                r'name=["\']quantity["\'].*?type=["\']hidden',
                r'type=["\']hidden["\'].*?name=["\']quantity',
                r'name=["\']cart_total["\']',
                r'name=["\']discount["\'].*?type=["\']hidden',
            ]
            for pattern in cart_patterns:
                if re.search(pattern, body_lower):
                    vulns.append({
                        "name": "Cart Tampering Risk",
                        "severity": "High",
                        "location": url,
                        "parameter": "quantity/cart_total",
                        "description": "Hidden form fields for cart quantities or totals found. These can be manipulated before checkout.",
                        "impact": "Attackers can modify quantities, totals, or discounts to pay less than intended.",
                        "recommendation": "Validate and recalculate all cart values server-side. Never trust client-submitted quantities or totals.",
                        "evidence": f"Pattern matched: {pattern}",
                    })
                    break

            # Check for coupon/promo inputs
            coupon_paths = ["/cart", "/checkout", "/basket"]
            for path in coupon_paths:
                try:
                    cart_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
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
                ("/robots.txt", "Robots.txt"),
                ("/sitemap.xml", "Sitemap"),
                ("/.well-known/security.txt", "Security.txt"),
            ]

            for path, desc in sensitive_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if resp.status_code == 200 and len(resp.text) > 10:
                        # Special handling — robots.txt and sitemap are normal
                        if path in ["/robots.txt", "/sitemap.xml", "/.well-known/security.txt"]:
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
                            "evidence": f"HTTP 200 returned for {path} ({len(resp.text)} bytes)",
                        })
                except Exception:
                    continue

            # Check for API keys in page source
            resp = self.session.get(url, timeout=self.timeout)
            api_patterns = [
                (r'["\']sk_live_[a-zA-Z0-9]{20,}["\']', "Stripe Secret Key"),
                (r'["\']pk_live_[a-zA-Z0-9]{20,}["\']', "Stripe Publishable Key (live)"),
                (r'["\']AKIA[A-Z0-9]{16}["\']', "AWS Access Key"),
                (r'AIza[0-9A-Za-z_-]{35}', "Google API Key"),
                (r'["\']ghp_[a-zA-Z0-9]{36}["\']', "GitHub Token"),
            ]
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
                "stack trace:", "internal server error",
                "django debug", "laravel_debugbar", "xdebug",
                "phpmyadmin", "server error in", "asp.net error",
            ]
            body_lower = resp.text.lower()
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
            common_dirs = ["/images/", "/uploads/", "/static/", "/media/", "/assets/"]
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
            # Check common API paths
            api_paths = [
                "/api", "/api/v1", "/api/v2",
                "/api/products", "/api/users", "/api/orders",
                "/graphql", "/api/graphql",
            ]

            for path in api_paths:
                try:
                    resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if resp.status_code == 200:
                        # Check if API returns data without auth
                        content_type = resp.headers.get("Content-Type", "").lower()
                        if "json" in content_type and len(resp.text) > 50:
                            vulns.append({
                                "name": "Unauthenticated API Access",
                                "severity": "High",
                                "location": urljoin(url, path),
                                "parameter": path,
                                "description": f"API endpoint {path} returns data without requiring authentication.",
                                "impact": "Attackers can access product data, user information, or order details without login.",
                                "recommendation": "Require authentication tokens for all API endpoints. Use OAuth 2.0 or API keys.",
                                "evidence": f"JSON response ({len(resp.text)} bytes) at {path} without auth",
                            })

                        # Check for rate limiting
                        rate_headers = ["x-ratelimit-limit", "x-ratelimit-remaining"]
                        has_rate = any(h in [k.lower() for k in resp.headers.keys()] for h in rate_headers)
                        if not has_rate and "json" in content_type:
                            vulns.append({
                                "name": "API Missing Rate Limiting",
                                "severity": "Medium",
                                "location": urljoin(url, path),
                                "parameter": "rate_limit",
                                "description": f"API endpoint {path} has no rate-limiting headers.",
                                "impact": "Attackers can flood the API with requests, causing DoS or data scraping.",
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
            resp = self.session.get(url, timeout=self.timeout)
            body_lower = resp.text.lower()

            # Check for CAPTCHA on main site
            captcha_keywords = ["captcha", "recaptcha", "hcaptcha", "turnstile", "g-recaptcha"]
            has_captcha = any(kw in body_lower for kw in captcha_keywords)

            # Check registration page
            reg_paths = ["/register", "/signup", "/create-account", "/account/register"]
            for path in reg_paths:
                try:
                    reg_resp = self.session.get(urljoin(url, path), timeout=self.timeout)
                    if reg_resp.status_code == 200 and "<form" in reg_resp.text.lower():
                        reg_body = reg_resp.text.lower()
                        if not any(kw in reg_body for kw in captcha_keywords):
                            vulns.append({
                                "name": "No CAPTCHA on Registration",
                                "severity": "Medium",
                                "location": urljoin(url, path),
                                "parameter": "registration_form",
                                "description": "Registration form has no CAPTCHA protection.",
                                "impact": "Bots can create fake accounts in bulk for spam, fraud, or inventory hoarding.",
                                "recommendation": "Add CAPTCHA to registration forms to prevent automated account creation.",
                                "evidence": f"Registration form at {path} without CAPTCHA",
                            })
                        break
                except Exception:
                    continue

            # Check for anti-bot headers
            anti_bot_headers = ["x-frame-options", "x-content-type-options", "strict-transport-security"]
            missing_security = []
            for header in anti_bot_headers:
                if header not in [k.lower() for k in resp.headers.keys()]:
                    missing_security.append(header)

            if len(missing_security) >= 2:
                vulns.append({
                    "name": "Weak Anti-Bot Defenses",
                    "severity": "Low",
                    "location": url,
                    "parameter": "security_headers",
                    "description": f"Multiple security headers missing: {', '.join(missing_security)}",
                    "impact": "Lack of security headers makes the site more vulnerable to automated attacks and content injection.",
                    "recommendation": "Implement all recommended security headers: HSTS, X-Frame-Options, X-Content-Type-Options.",
                    "evidence": f"Missing headers: {', '.join(missing_security)}",
                })

        except Exception as e:
            logger.error(f"Bot protection check error: {e}")
        return vulns
