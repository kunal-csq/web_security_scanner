"""
DAST SSL/TLS Security Scanner Module
Checks TLS version, cipher strength, HSTS, certificate validity,
and HTTPS downgrade vulnerabilities.
"""

import ssl
import socket
import requests
import logging
from urllib.parse import urlparse
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Weak cipher suites to flag
WEAK_CIPHERS = [
    "RC4", "DES", "3DES", "NULL", "EXPORT", "anon",
    "RC2", "IDEA", "SEED", "MD5",
]

# Deprecated TLS versions
DEPRECATED_TLS = ["TLSv1", "TLSv1.0", "TLSv1.1", "SSLv2", "SSLv3"]


class SSLScanner:
    """SSL/TLS security scanner."""

    def __init__(self, timeout=10):
        self.timeout = timeout

    def scan(self, endpoints, target_url):
        """
        Scan for SSL/TLS security issues.

        Args:
            endpoints: List of endpoint dicts (not used directly, required for interface)
            target_url: Target URL to scan

        Returns:
            List of vulnerability dicts in standard format
        """
        vulnerabilities = []

        parsed = urlparse(target_url)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        # Check TLS version and cipher suite
        vulns = self._check_tls_config(hostname, port)
        vulnerabilities.extend(vulns)

        # Check certificate validity
        vulns = self._check_certificate(hostname, port)
        vulnerabilities.extend(vulns)

        # Check HSTS
        vulns = self._check_hsts(target_url)
        vulnerabilities.extend(vulns)

        # Check HTTPS downgrade
        vulns = self._check_https_downgrade(target_url)
        vulnerabilities.extend(vulns)

        # Check for weak TLS versions
        vulns = self._check_weak_tls_versions(hostname, port)
        vulnerabilities.extend(vulns)

        return vulnerabilities

    def _check_tls_config(self, hostname, port):
        """Check current TLS version and cipher suite."""
        vulnerabilities = []

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    tls_version = ssock.version()
                    cipher = ssock.cipher()

                    cipher_name = cipher[0] if cipher else "Unknown"
                    cipher_bits = cipher[2] if cipher and len(cipher) > 2 else 0

                    # Check TLS version
                    if tls_version in DEPRECATED_TLS:
                        vulnerabilities.append({
                            "name": "Deprecated TLS Version",
                            "severity": "High",
                            "location": f"{hostname}:{port}",
                            "parameter": "TLS Protocol",
                            "description": (
                                f"The server uses {tls_version} which is deprecated "
                                f"and has known security vulnerabilities including "
                                f"POODLE, BEAST, and other attacks."
                            ),
                            "impact": (
                                "Deprecated TLS versions can be exploited to decrypt "
                                "sensitive data transmitted between client and server."
                            ),
                            "recommendation": (
                                "Disable TLS 1.0 and TLS 1.1. Configure the server "
                                "to use TLS 1.2 or TLS 1.3 exclusively."
                            ),
                            "evidence": f"TLS Version: {tls_version}",
                        })

                    # Check cipher strength
                    if any(weak in cipher_name.upper() for weak in WEAK_CIPHERS):
                        vulnerabilities.append({
                            "name": "Weak Cipher Suite",
                            "severity": "High",
                            "location": f"{hostname}:{port}",
                            "parameter": "Cipher Suite",
                            "description": (
                                f"The server negotiated a weak cipher suite: "
                                f"{cipher_name}. Weak ciphers can be broken by "
                                f"attackers to decrypt traffic."
                            ),
                            "impact": (
                                "Encrypted traffic can potentially be decrypted "
                                "by an attacker with sufficient resources."
                            ),
                            "recommendation": (
                                "Configure the server to use strong cipher suites "
                                "only. Prefer AES-GCM, ChaCha20-Poly1305 ciphers. "
                                "Disable RC4, DES, 3DES, NULL, and EXPORT ciphers."
                            ),
                            "evidence": (
                                f"Cipher: {cipher_name} | "
                                f"Bits: {cipher_bits}"
                            ),
                        })

                    # Check for short key length
                    if cipher_bits and cipher_bits < 128:
                        vulnerabilities.append({
                            "name": "Insufficient Cipher Key Length",
                            "severity": "High",
                            "location": f"{hostname}:{port}",
                            "parameter": "Cipher Key Length",
                            "description": (
                                f"The cipher key length is only {cipher_bits} bits. "
                                f"Modern security standards require at least 128 bits."
                            ),
                            "impact": (
                                "Short key lengths can be brute-forced by attackers."
                            ),
                            "recommendation": (
                                "Use cipher suites with key lengths of at least 128 bits. "
                                "256-bit keys are recommended for high-security deployments."
                            ),
                            "evidence": (
                                f"Cipher: {cipher_name} | Key length: {cipher_bits} bits"
                            ),
                        })

        except ssl.SSLError as e:
            vulnerabilities.append({
                "name": "SSL/TLS Handshake Failure",
                "severity": "Medium",
                "location": f"{hostname}:{port}",
                "parameter": "SSL Configuration",
                "description": (
                    f"SSL/TLS handshake failed: {str(e)}. "
                    f"The server may have misconfigured SSL settings."
                ),
                "impact": (
                    "Clients may fail to establish secure connections, or "
                    "the server may be vulnerable to downgrade attacks."
                ),
                "recommendation": (
                    "Review and fix SSL/TLS configuration. Ensure valid "
                    "certificates and supported protocol versions."
                ),
                "evidence": f"SSL Error: {str(e)}",
            })

        except Exception as e:
            logger.debug(f"Error checking TLS config: {e}")

        return vulnerabilities

    def _check_certificate(self, hostname, port):
        """Check SSL certificate validity and expiration."""
        vulnerabilities = []

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    if not cert:
                        vulnerabilities.append({
                            "name": "No SSL Certificate",
                            "severity": "Critical",
                            "location": f"{hostname}:{port}",
                            "parameter": "SSL Certificate",
                            "description": "No SSL certificate presented by the server.",
                            "impact": "All traffic is transmitted in plaintext.",
                            "recommendation": "Install a valid SSL/TLS certificate.",
                            "evidence": "No certificate in TLS handshake",
                        })
                        return vulnerabilities

                    # Check expiration
                    not_after = cert.get("notAfter", "")
                    if not_after:
                        expiry = datetime.strptime(
                            not_after, "%b %d %H:%M:%S %Y %Z"
                        )
                        now = datetime.utcnow()

                        if expiry < now:
                            vulnerabilities.append({
                                "name": "Expired SSL Certificate",
                                "severity": "Critical",
                                "location": f"{hostname}:{port}",
                                "parameter": "Certificate Expiry",
                                "description": (
                                    f"SSL certificate expired on {not_after}. "
                                    f"Expired certificates break trust and may "
                                    f"allow man-in-the-middle attacks."
                                ),
                                "impact": (
                                    "Users receive security warnings. Attackers can "
                                    "perform MITM attacks with spoofed certificates."
                                ),
                                "recommendation": (
                                    "Renew the SSL certificate immediately. Set up "
                                    "automated renewal using Let's Encrypt or similar."
                                ),
                                "evidence": f"Certificate expired: {not_after}",
                            })
                        elif (expiry - now).days < 30:
                            vulnerabilities.append({
                                "name": "SSL Certificate Expiring Soon",
                                "severity": "Medium",
                                "location": f"{hostname}:{port}",
                                "parameter": "Certificate Expiry",
                                "description": (
                                    f"SSL certificate expires in {(expiry - now).days} "
                                    f"days ({not_after})."
                                ),
                                "impact": (
                                    "Certificate will expire soon, potentially causing "
                                    "service disruption."
                                ),
                                "recommendation": (
                                    "Renew the SSL certificate before expiration. "
                                    "Set up automated renewal."
                                ),
                                "evidence": (
                                    f"Expires: {not_after} | "
                                    f"Days remaining: {(expiry - now).days}"
                                ),
                            })

                    # Check subject alternative names
                    san = cert.get("subjectAltName", ())
                    hostnames = [name for typ, name in san if typ == "DNS"]
                    if hostname not in hostnames and f"*.{'.'.join(hostname.split('.')[1:])}" not in hostnames:
                        vulnerabilities.append({
                            "name": "Certificate Hostname Mismatch",
                            "severity": "High",
                            "location": f"{hostname}:{port}",
                            "parameter": "Certificate SAN",
                            "description": (
                                f"Certificate does not include hostname '{hostname}' "
                                f"in Subject Alternative Names. Valid for: "
                                f"{', '.join(hostnames[:5])}"
                            ),
                            "impact": (
                                "Browsers will show security warnings. Connection "
                                "may not be trusted."
                            ),
                            "recommendation": (
                                "Obtain a certificate that includes the correct "
                                "hostname in the SAN field."
                            ),
                            "evidence": (
                                f"Hostname: {hostname} | "
                                f"Certificate SANs: {', '.join(hostnames[:5])}"
                            ),
                        })

        except ssl.SSLCertVerificationError as e:
            vulnerabilities.append({
                "name": "SSL Certificate Verification Failed",
                "severity": "Critical",
                "location": f"{hostname}:{port}",
                "parameter": "Certificate Validation",
                "description": (
                    f"SSL certificate verification failed: {str(e)}. "
                    f"The certificate may be self-signed, expired, or issued "
                    f"by an untrusted CA."
                ),
                "impact": (
                    "Users cannot verify server identity. "
                    "Man-in-the-middle attacks are possible."
                ),
                "recommendation": (
                    "Use a certificate from a trusted Certificate Authority. "
                    "Ensure the certificate chain is complete."
                ),
                "evidence": f"Verification error: {str(e)}",
            })

        except Exception as e:
            logger.debug(f"Error checking certificate: {e}")

        return vulnerabilities

    def _check_hsts(self, target_url):
        """Check for HTTP Strict Transport Security (HSTS) header."""
        vulnerabilities = []

        try:
            response = requests.get(
                target_url, timeout=self.timeout, verify=False
            )
            headers = response.headers

            if "Strict-Transport-Security" not in headers:
                vulnerabilities.append({
                    "name": "Missing HSTS Header",
                    "severity": "Medium",
                    "location": target_url,
                    "parameter": "Strict-Transport-Security",
                    "description": (
                        "The Strict-Transport-Security (HSTS) header is missing. "
                        "Without HSTS, users can be redirected to HTTP and their "
                        "traffic intercepted via MITM attacks."
                    ),
                    "impact": (
                        "Users accessing the site for the first time or after HSTS "
                        "expiry can be subjected to SSL stripping attacks."
                    ),
                    "recommendation": (
                        "Add the Strict-Transport-Security header with a long max-age: "
                        "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
                    ),
                    "evidence": "HSTS header not found in response",
                })
            else:
                hsts_value = headers["Strict-Transport-Security"]
                # Check max-age
                if "max-age=" in hsts_value.lower():
                    max_age_str = hsts_value.lower().split("max-age=")[1].split(";")[0].strip()
                    try:
                        max_age = int(max_age_str)
                        if max_age < 15768000:  # Less than 6 months
                            vulnerabilities.append({
                                "name": "Weak HSTS Configuration",
                                "severity": "Low",
                                "location": target_url,
                                "parameter": "HSTS max-age",
                                "description": (
                                    f"HSTS max-age is set to {max_age} seconds "
                                    f"({max_age // 86400} days). Recommended minimum "
                                    f"is 6 months (15768000 seconds)."
                                ),
                                "impact": (
                                    "Short HSTS duration reduces protection window."
                                ),
                                "recommendation": (
                                    "Increase HSTS max-age to at least 1 year (31536000)."
                                ),
                                "evidence": f"HSTS: {hsts_value}",
                            })
                    except ValueError:
                        pass

        except Exception as e:
            logger.debug(f"Error checking HSTS: {e}")

        return vulnerabilities

    def _check_https_downgrade(self, target_url):
        """Check if HTTP to HTTPS redirect is properly configured."""
        vulnerabilities = []

        parsed = urlparse(target_url)
        if parsed.scheme != "https":
            return vulnerabilities

        # Check HTTP version
        http_url = target_url.replace("https://", "http://")

        try:
            response = requests.get(
                http_url, allow_redirects=False, timeout=self.timeout, verify=False
            )

            if response.status_code not in [301, 302, 307, 308]:
                vulnerabilities.append({
                    "name": "Missing HTTPS Redirect",
                    "severity": "High",
                    "location": http_url,
                    "parameter": "HTTP Redirect",
                    "description": (
                        f"HTTP requests to {http_url} are not redirected to HTTPS "
                        f"(status code: {response.status_code}). Users accessing "
                        f"the site via HTTP will have their traffic sent in plaintext."
                    ),
                    "impact": (
                        "Sensitive data including credentials and session tokens "
                        "can be intercepted when users access the site over HTTP."
                    ),
                    "recommendation": (
                        "Configure the server to redirect all HTTP traffic to HTTPS "
                        "using a 301 (permanent) redirect."
                    ),
                    "evidence": (
                        f"HTTP request to {http_url} returned status "
                        f"{response.status_code} instead of 301/302 redirect"
                    ),
                })
            elif response.status_code in [302, 307]:
                # 302 is a temporary redirect — should be 301
                vulnerabilities.append({
                    "name": "Temporary HTTPS Redirect",
                    "severity": "Low",
                    "location": http_url,
                    "parameter": "HTTP Redirect Type",
                    "description": (
                        f"HTTP to HTTPS redirect uses status {response.status_code} "
                        f"(temporary) instead of 301 (permanent). Browsers may not "
                        f"cache the redirect."
                    ),
                    "impact": (
                        "Temporary redirects are not cached by browsers, reducing "
                        "the effectiveness of HTTPS enforcement."
                    ),
                    "recommendation": (
                        "Use 301 (Moved Permanently) for HTTP to HTTPS redirects."
                    ),
                    "evidence": (
                        f"Redirect status: {response.status_code} | "
                        f"Location: {response.headers.get('Location', 'N/A')}"
                    ),
                })

        except Exception as e:
            logger.debug(f"Error checking HTTPS downgrade: {e}")

        return vulnerabilities

    def _check_weak_tls_versions(self, hostname, port):
        """Attempt connections with weak TLS versions to check if they're accepted."""
        vulnerabilities = []

        weak_protocols = {
            "TLSv1.0": ssl.TLSVersion.TLSv1 if hasattr(ssl.TLSVersion, 'TLSv1') else None,
            "TLSv1.1": ssl.TLSVersion.TLSv1_1 if hasattr(ssl.TLSVersion, 'TLSv1_1') else None,
        }

        for protocol_name, protocol_version in weak_protocols.items():
            if protocol_version is None:
                continue

            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.minimum_version = protocol_version
                context.maximum_version = protocol_version

                with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        vulnerabilities.append({
                            "name": f"Weak TLS Version Supported ({protocol_name})",
                            "severity": "High",
                            "location": f"{hostname}:{port}",
                            "parameter": "TLS Protocol Version",
                            "description": (
                                f"Server accepts connections using {protocol_name}, "
                                f"which is deprecated and has known vulnerabilities."
                            ),
                            "impact": (
                                f"Attackers can force a downgrade to {protocol_name} "
                                f"and exploit known vulnerabilities like POODLE or BEAST."
                            ),
                            "recommendation": (
                                f"Disable {protocol_name} on the server. Only allow "
                                f"TLS 1.2 and TLS 1.3."
                            ),
                            "evidence": (
                                f"Successfully connected using {protocol_name}"
                            ),
                        })

            except (ssl.SSLError, socket.error, OSError):
                # Good — weak version is rejected
                pass
            except Exception as e:
                logger.debug(f"Error testing {protocol_name}: {e}")

        return vulnerabilities
