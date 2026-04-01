"""
DAST Scan API Routes
Uses AsyncScanEngine for concurrent scanning + StressScanner for load testing.
Now includes JWT-based access control and scan history saving.
"""

import json
import logging
from flask import Blueprint, request, jsonify
from core.async_engine import AsyncScanEngine
from scanners.ecom_scanner import EcomScanner
from core.scorer import calculate_score, get_severity_counts, get_grade
from ai.analysis import generate_ai_analysis
from scanners.stress_scanner import StressScanner
from api.auth_routes import get_optional_user
from db import get_db

logger = logging.getLogger(__name__)

scan_bp = Blueprint("scan", __name__, url_prefix="/api")


def _save_scan_history(user_id, url, depth, response_data):
    """Save scan results to history for authenticated users."""
    try:
        db = get_db()
        db.execute(
            """INSERT INTO scan_history
               (user_id, url, score, grade, severity_counts, results,
                ai_analysis, crawl_info, timing, scan_log, depth)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                url,
                response_data.get("score", 0),
                response_data.get("grade", "F"),
                json.dumps(response_data.get("severity_counts", {})),
                json.dumps(response_data.get("results", [])),
                json.dumps(response_data.get("ai_analysis", {})),
                json.dumps(response_data.get("crawl_info", {})),
                json.dumps(response_data.get("timing", {})),
                json.dumps(response_data.get("scan_log", [])),
                depth,
            ),
        )
        db.commit()
        db.close()
        logger.info(f"Scan saved to history for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save scan history: {e}")


# -----------------------------------------------
# MAIN SCAN ROUTE
# -----------------------------------------------
@scan_bp.route("/scan", methods=["POST"])
def run_scan():
    """
    Execute a full DAST security scan.

    Access control:
        - No token: forced to 'quick' depth, no stress test, no history save
        - Valid token: any depth, stress test allowed, results saved to history
    """
    data = request.get_json()

    url = data.get("url")
    scans = data.get("scans", [])
    depth = data.get("depth", "standard")
    run_stress = data.get("stress_test", False)
    scan_mode = data.get("scan_mode", "general")  # "general" or "ecommerce"

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # ---- Access control ----
    user = get_optional_user()
    is_authenticated = user is not None

    if not is_authenticated:
        # Guests: quick scan only, no stress test
        depth = "quick"
        run_stress = False

    if depth not in ["quick", "standard", "deep"]:
        depth = "standard"

    try:
        # ----------------------------------------
        # Run scan engine based on mode
        # ----------------------------------------
        if scan_mode == "ecommerce":
            ecom = EcomScanner(timeout=8)
            ecom_results = ecom.scan(url)
            scan_data = {
                "results": ecom_results,
                "crawl_info": {"scan_mode": "ecommerce", "checks_run": 8},
                "scan_log": [{"phase": "ECOM", "message": f"Ecommerce scan complete: {len(ecom_results)} issues"}],
                "timing": {},
            }
        else:
            engine = AsyncScanEngine(depth=depth)
            scan_data = engine.run(url, scans=scans)

        results = scan_data.get("results", [])
        crawl_info = scan_data.get("crawl_info", {})
        scan_log = scan_data.get("scan_log", [])
        timing = scan_data.get("timing", {})

        # ----------------------------------------
        # Calculate score + AI analysis
        # ----------------------------------------
        score = calculate_score(results)
        grade = get_grade(score)
        severity_counts = get_severity_counts(results)
        ai_analysis = generate_ai_analysis(results, score)

        response = {
            "url": url,
            "score": score,
            "grade": grade,
            "severity_counts": severity_counts,
            "results": results,
            "ai_analysis": ai_analysis,
            "crawl_info": crawl_info,
            "scan_log": scan_log,
            "timing": timing,
            "authenticated": is_authenticated,
            "depth_used": depth,
        }

        # ----------------------------------------
        # Optional stress test (authenticated only)
        # ----------------------------------------
        if run_stress and is_authenticated:
            stress = StressScanner(
                max_concurrent=10,
                max_requests=50,
            )
            stress_results = stress.run(url)
            response["stress_test"] = stress_results

        # ----------------------------------------
        # Save to history (authenticated only)
        # ----------------------------------------
        if is_authenticated:
            _save_scan_history(user["user_id"], url, depth, response)

        return jsonify(response)

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return jsonify({
            "error": f"Scan failed: {str(e)}",
            "url": url,
            "score": 0,
            "grade": "F",
            "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "results": [],
            "ai_analysis": {
                "summary": f"Scan could not be completed: {str(e)}",
                "why_it_matters": "Unable to assess security posture.",
                "priority_actions": ["Verify the target URL is accessible and try again."],
            },
            "crawl_info": {},
            "scan_log": [],
            "timing": {},
        }), 500


# -----------------------------------------------
# STANDALONE STRESS TEST ROUTE
# -----------------------------------------------
@scan_bp.route("/stress-test", methods=["POST"])
def run_stress_test():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    concurrent = min(data.get("concurrent", 10), 20)
    total_requests = min(data.get("requests", 50), 100)

    try:
        stress = StressScanner(
            max_concurrent=concurrent,
            max_requests=total_requests,
        )
        results = stress.run(url)
        results["url"] = url
        return jsonify(results)
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        return jsonify({"error": str(e), "url": url}), 500


# -----------------------------------------------
# HEALTH CHECK
# -----------------------------------------------
@scan_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "WebGuard DAST Engine",
        "version": "2.2.0",
        "features": ["auth", "history", "access_control"],
        "scanners": ["sqli", "xss", "csrf", "auth", "ssl", "headers", "stress_test"],
    })


# -----------------------------------------------
# AVAILABLE SCANNERS
# -----------------------------------------------
@scan_bp.route("/scanners", methods=["GET"])
def list_scanners():
    return jsonify({
        "scanners": [
            {"key": "sqli", "name": "SQL Injection Scanner", "description": "Error-based, time-based blind, and auth bypass SQLi detection"},
            {"key": "xss", "name": "XSS Scanner", "description": "Reflected, DOM-based, and stored Cross-Site Scripting"},
            {"key": "csrf", "name": "CSRF Scanner", "description": "Missing CSRF tokens and insecure cookie SameSite settings"},
            {"key": "auth", "name": "Authentication Scanner", "description": "Cookie security flags, session rotation, JWT leakage"},
            {"key": "ssl", "name": "SSL/TLS Scanner", "description": "TLS version, cipher strength, certificates, HTTPS downgrade"},
            {"key": "headers", "name": "Security Headers Scanner", "description": "CSP, X-Frame-Options, HSTS, Referrer-Policy, Permissions-Policy"},
            {"key": "stress_test", "name": "Load Tester", "description": "Controlled concurrent load test measuring stability and response time"},
        ]
    })
