"""
Controlled Load Test / Stress Scanner
Sends throttled concurrent requests to measure application stability.

SAFETY GUARANTEES:
- Max 20 concurrent threads
- Max 100 total requests
- Auto-abort if avg response time > 3s
- Small delays between batches to prevent flooding
- No payload injection — only GET requests
"""

import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Safety limits
MAX_CONCURRENT = 20
MAX_REQUESTS = 100
ABORT_THRESHOLD_MS = 3000  # Abort if avg > 3s
BATCH_DELAY = 0.2  # 200ms between batches
REQUEST_TIMEOUT = 10  # Per-request timeout


class StressScanner:
    """
    Safe, throttled load tester.
    Measures response time, error rate, and stability.
    """

    def __init__(self, max_concurrent=10, max_requests=50):
        self.max_concurrent = min(max_concurrent, MAX_CONCURRENT)
        self.max_requests = min(max_requests, MAX_REQUESTS)

    def run(self, url):
        """
        Run controlled load test against target URL.

        Returns:
            dict with: avg_response_time, max_response_time, min_response_time,
                        error_rate, timeout_rate, stability_score, request_count,
                        status_codes, aborted, results_detail
        """
        logger.info(
            f"Starting load test: {url} "
            f"(concurrent={self.max_concurrent}, total={self.max_requests})"
        )

        response_times = []
        errors = 0
        timeouts = 0
        status_codes = {}
        aborted = False
        total_sent = 0

        def send_request(request_id):
            """Send a single GET request and measure timing."""
            try:
                start = time.time()
                resp = requests.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    headers={
                        "User-Agent": "WebGuard-LoadTest/2.0 (Safe Controlled Test)",
                    },
                    allow_redirects=True,
                )
                elapsed_ms = round((time.time() - start) * 1000, 2)

                return {
                    "id": request_id,
                    "status": resp.status_code,
                    "time_ms": elapsed_ms,
                    "error": None,
                    "timeout": False,
                }
            except requests.exceptions.Timeout:
                return {
                    "id": request_id,
                    "status": 0,
                    "time_ms": REQUEST_TIMEOUT * 1000,
                    "error": "timeout",
                    "timeout": True,
                }
            except requests.exceptions.RequestException as e:
                return {
                    "id": request_id,
                    "status": 0,
                    "time_ms": 0,
                    "error": str(e)[:100],
                    "timeout": False,
                }

        # Send requests in batches
        request_id = 0
        batch_size = self.max_concurrent

        while total_sent < self.max_requests and not aborted:
            batch_count = min(batch_size, self.max_requests - total_sent)

            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                futures = []
                for _ in range(batch_count):
                    request_id += 1
                    futures.append(executor.submit(send_request, request_id))

                for future in as_completed(futures):
                    result = future.result()
                    total_sent += 1

                    if result["error"]:
                        errors += 1
                        if result["timeout"]:
                            timeouts += 1
                    else:
                        response_times.append(result["time_ms"])
                        code = str(result["status"])
                        status_codes[code] = status_codes.get(code, 0) + 1

            # Check abort condition after each batch
            if len(response_times) >= 5:
                recent_avg = sum(response_times[-10:]) / len(response_times[-10:])
                if recent_avg > ABORT_THRESHOLD_MS:
                    logger.warning(
                        f"Load test aborted: avg response time {recent_avg:.0f}ms > {ABORT_THRESHOLD_MS}ms"
                    )
                    aborted = True

            # Throttle between batches
            time.sleep(BATCH_DELAY)

        # Calculate metrics
        if response_times:
            avg_time = round(sum(response_times) / len(response_times), 2)
            max_time = round(max(response_times), 2)
            min_time = round(min(response_times), 2)
            p95_sorted = sorted(response_times)
            p95_index = int(len(p95_sorted) * 0.95)
            p95_time = round(p95_sorted[min(p95_index, len(p95_sorted) - 1)], 2)
        else:
            avg_time = 0
            max_time = 0
            min_time = 0
            p95_time = 0

        error_rate = round((errors / total_sent * 100) if total_sent > 0 else 0, 2)
        timeout_rate = round((timeouts / total_sent * 100) if total_sent > 0 else 0, 2)

        # Stability score (0-100)
        stability = 100
        if avg_time > 2000:
            stability -= 30
        elif avg_time > 1000:
            stability -= 15
        elif avg_time > 500:
            stability -= 5

        if error_rate > 20:
            stability -= 40
        elif error_rate > 10:
            stability -= 25
        elif error_rate > 5:
            stability -= 15
        elif error_rate > 0:
            stability -= 5

        if timeout_rate > 10:
            stability -= 20
        elif timeout_rate > 5:
            stability -= 10

        if aborted:
            stability -= 15

        stability = max(stability, 0)

        logger.info(
            f"Load test complete: {total_sent} requests, "
            f"avg={avg_time}ms, errors={error_rate}%, stability={stability}"
        )

        return {
            "avg_response_time": f"{avg_time}ms",
            "max_response_time": f"{max_time}ms",
            "min_response_time": f"{min_time}ms",
            "p95_response_time": f"{p95_time}ms",
            "error_rate": f"{error_rate}%",
            "timeout_rate": f"{timeout_rate}%",
            "stability_score": stability,
            "request_count": total_sent,
            "successful_requests": total_sent - errors,
            "failed_requests": errors,
            "status_codes": status_codes,
            "aborted": aborted,
            "aborted_reason": "Response time exceeded 3s threshold" if aborted else None,
        }
