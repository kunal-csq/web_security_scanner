"""
DAST Scan Orchestrator Engine
Crawls once, then dispatches all scanner modules against discovered endpoints.
Uses ThreadPoolExecutor for concurrent scanning.
"""

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

# Scanner registry – maps scan keys to scanner classes/functions
SCANNER_REGISTRY = {
    "sqli": "sqli",
    "xss": "xss",
    "csrf": "csrf",
    "auth": "auth",
    "ssl": "ssl",
    "headers": "headers",
}


class ScanEngine:
    """
    Main scan orchestrator.
    Crawls the target once, then runs all requested scanners
    against the discovered endpoints concurrently.
    """

    def __init__(self, max_workers=4):
        self.max_workers = max_workers

    def run(self, url, scans=None, depth="standard"):
        """
        Execute a full security scan.

        Args:
            url: Target URL to scan
            scans: List of scanner keys to run (default: all)
            depth: Scan depth – 'quick', 'standard', 'deep'

        Returns:
            dict with: endpoints, results, crawl_info
        """
        if scans is None or len(scans) == 0:
            scans = list(SCANNER_REGISTRY.keys())

        # ----------------------------------------
        # PHASE 1: Crawl the target
        # ----------------------------------------
        logger.info(f"Starting crawl of {url} (depth={depth})")

        crawl_depth = {"quick": 1, "standard": 2, "deep": 3}.get(depth, 2)
        max_pages = {"quick": 10, "standard": 30, "deep": 50}.get(depth, 30)

        try:
            crawl_data = crawl_site(url, max_depth=crawl_depth, max_pages=max_pages)
        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            crawl_data = {
                "endpoints": [{
                    "endpoint": url,
                    "method": "GET",
                    "parameters": [],
                    "source_page": url,
                    "has_csrf_token": False,
                }],
                "links": [],
                "cookies": [],
                "total_forms": 0,
                "total_links": 0,
                "pages_crawled": 0,
            }

        endpoints = crawl_data.get("endpoints", [])
        cookies = crawl_data.get("cookies", [])

        logger.info(
            f"Crawl complete: {len(endpoints)} endpoints, "
            f"{crawl_data.get('pages_crawled', 0)} pages crawled"
        )

        # ----------------------------------------
        # PHASE 2: Run scanners concurrently
        # ----------------------------------------
        all_results = []

        scanner_tasks = {}

        if "sqli" in scans:
            scanner_tasks["sqli"] = lambda: SQLiScanner().scan(endpoints, url)

        if "xss" in scans:
            scanner_tasks["xss"] = lambda: XSSScanner().scan(endpoints, url)

        if "csrf" in scans:
            scanner_tasks["csrf"] = lambda: CSRFScanner().scan(endpoints, url, cookies)

        if "auth" in scans:
            scanner_tasks["auth"] = lambda: AuthScanner().scan(endpoints, url, cookies)

        if "ssl" in scans:
            scanner_tasks["ssl"] = lambda: SSLScanner().scan(endpoints, url)

        if "headers" in scans:
            scanner_tasks["headers"] = lambda: check_headers(url)

        # Execute scanners using thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_scanner = {
                executor.submit(task): name
                for name, task in scanner_tasks.items()
            }

            for future in as_completed(future_to_scanner):
                scanner_name = future_to_scanner[future]
                try:
                    results = future.result(timeout=120)
                    if results:
                        all_results.extend(results)
                        logger.info(
                            f"Scanner '{scanner_name}' found "
                            f"{len(results)} issues"
                        )
                    else:
                        logger.info(f"Scanner '{scanner_name}' found no issues")
                except Exception as e:
                    logger.error(f"Scanner '{scanner_name}' failed: {e}")

        return {
            "endpoints": endpoints,
            "results": all_results,
            "crawl_info": {
                "pages_crawled": crawl_data.get("pages_crawled", 0),
                "total_forms": crawl_data.get("total_forms", 0),
                "total_links": crawl_data.get("total_links", 0),
                "endpoints_found": len(endpoints),
            },
        }
