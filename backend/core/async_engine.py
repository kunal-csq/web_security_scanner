"""
DAST Async Scan Engine
Production-grade concurrent scanning with configurable workers per depth mode,
per-request timeouts, and structured progress logging.
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from scanners.selenium_crawler import crawl_site
from scanners.sqli_scanner import SQLiScanner
from scanners.xss_scanner import XSSScanner
from scanners.csrf_scanner import CSRFScanner
from scanners.auth_scanner import AuthScanner
from scanners.ssl_scanner import SSLScanner
from scanners.headers_scanner import check_headers

logger = logging.getLogger(__name__)

# -----------------------------------------------
# DEPTH MODE CONFIGURATION
# -----------------------------------------------
DEPTH_CONFIG = {
    "quick": {
        "max_pages": 2,
        "max_workers": 3,
        "crawl_depth": 1,
        "request_timeout": 5,
        "scanner_timeout": 30,
    },
    "standard": {
        "max_pages": 5,
        "max_workers": 5,
        "crawl_depth": 2,
        "request_timeout": 5,
        "scanner_timeout": 60,
    },
    "deep": {
        "max_pages": 15,
        "max_workers": 8,
        "crawl_depth": 3,
        "request_timeout": 5,
        "scanner_timeout": 120,
    },
}

# Scanner registry
SCANNER_REGISTRY = {
    "sqli": "SQL Injection",
    "xss": "Cross-Site Scripting",
    "csrf": "CSRF",
    "auth": "Authentication",
    "ssl": "SSL/TLS",
    "headers": "Security Headers",
}


class AsyncScanEngine:
    """
    Production-grade async scan engine.
    Crawls once, dispatches scanners concurrently via ThreadPoolExecutor,
    with configurable workers per depth mode and per-request timeouts.
    """

    def __init__(self, depth="standard"):
        config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])
        self.max_pages = config["max_pages"]
        self.max_workers = config["max_workers"]
        self.crawl_depth = config["crawl_depth"]
        self.request_timeout = config["request_timeout"]
        self.scanner_timeout = config["scanner_timeout"]
        self.depth = depth
        self.scan_log = []

    def _log(self, phase, message):
        """Add timestamped log entry."""
        entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "phase": phase,
            "message": message,
        }
        self.scan_log.append(entry)
        logger.info(f"[{entry['timestamp']}] [{phase}] {message}")

    def run(self, url, scans=None):
        """
        Execute full async security scan.

        Args:
            url: Target URL
            scans: List of scanner keys (default: all)

        Returns:
            dict: endpoints, results, crawl_info, scan_log, timing
        """
        if scans is None or len(scans) == 0:
            scans = list(SCANNER_REGISTRY.keys())

        start_time = time.time()

        # ========================================
        # PHASE 1: CRAWL
        # ========================================
        self._log("CRAWL", f"Starting crawl of {url} (depth={self.depth}, max_pages={self.max_pages})")

        try:
            crawl_data = crawl_site(
                url,
                max_depth=self.crawl_depth,
                max_pages=self.max_pages,
            )
            endpoints = crawl_data.get("endpoints", [])
            cookies = crawl_data.get("cookies", [])
            self._log("CRAWL", f"Complete: {len(endpoints)} endpoints, {crawl_data.get('pages_crawled', 0)} pages")
        except Exception as e:
            self._log("CRAWL", f"Failed: {e} — using fallback endpoint")
            endpoints = [{
                "endpoint": url,
                "method": "GET",
                "parameters": [],
                "source_page": url,
                "has_csrf_token": False,
            }]
            cookies = []
            crawl_data = {
                "endpoints": endpoints,
                "links": [],
                "cookies": [],
                "total_forms": 0,
                "total_links": 0,
                "pages_crawled": 0,
            }

        crawl_time = time.time() - start_time

        # ========================================
        # PHASE 2: DISPATCH SCANNERS CONCURRENTLY
        # ========================================
        self._log("SCAN", f"Dispatching {len(scans)} scanners with {self.max_workers} workers")

        scanner_tasks = {}

        if "sqli" in scans:
            scanner_tasks["sqli"] = lambda: SQLiScanner(timeout=self.request_timeout).scan(endpoints, url)
        if "xss" in scans:
            scanner_tasks["xss"] = lambda: XSSScanner(timeout=self.request_timeout).scan(endpoints, url)
        if "csrf" in scans:
            scanner_tasks["csrf"] = lambda: CSRFScanner().scan(endpoints, url, cookies)
        if "auth" in scans:
            scanner_tasks["auth"] = lambda: AuthScanner().scan(endpoints, url, cookies)
        if "ssl" in scans:
            scanner_tasks["ssl"] = lambda: SSLScanner().scan(endpoints, url)
        if "headers" in scans:
            scanner_tasks["headers"] = lambda: check_headers(url)

        all_results = []
        scanner_timings = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_scanner = {}
            scanner_start_times = {}

            for name, task in scanner_tasks.items():
                future = executor.submit(task)
                future_to_scanner[future] = name
                scanner_start_times[name] = time.time()
                self._log("SCAN", f"Started: {SCANNER_REGISTRY.get(name, name)}")

            for future in as_completed(future_to_scanner):
                scanner_name = future_to_scanner[future]
                elapsed = round(time.time() - scanner_start_times[scanner_name], 2)
                scanner_timings[scanner_name] = elapsed

                try:
                    results = future.result(timeout=self.scanner_timeout)
                    if results:
                        all_results.extend(results)
                        self._log("SCAN", f"Complete: {SCANNER_REGISTRY.get(scanner_name, scanner_name)} — {len(results)} issues ({elapsed}s)")
                    else:
                        self._log("SCAN", f"Complete: {SCANNER_REGISTRY.get(scanner_name, scanner_name)} — clean ({elapsed}s)")
                except Exception as e:
                    self._log("SCAN", f"Failed: {SCANNER_REGISTRY.get(scanner_name, scanner_name)} — {str(e)[:80]}")

        total_time = round(time.time() - start_time, 2)
        self._log("DONE", f"Scan complete in {total_time}s — {len(all_results)} total issues found")

        return {
            "endpoints": endpoints,
            "results": all_results,
            "crawl_info": {
                "pages_crawled": crawl_data.get("pages_crawled", 0),
                "total_forms": crawl_data.get("total_forms", 0),
                "total_links": crawl_data.get("total_links", 0),
                "endpoints_found": len(endpoints),
            },
            "scan_log": self.scan_log,
            "timing": {
                "crawl_time": round(crawl_time, 2),
                "total_time": total_time,
                "scanner_timings": scanner_timings,
            },
        }
