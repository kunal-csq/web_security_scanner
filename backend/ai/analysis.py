"""
DAST AI Analysis Module
Generates plain-text security analysis without markdown formatting.
Returns: Summary, Why It Matters, Fix Priority List.
"""

from core.scorer import get_severity_counts, get_grade


def generate_ai_analysis(results, score):
    """
    Generate structured AI security analysis.

    All output is plain text WITHOUT markdown symbols (no ###, **, etc.).

    Args:
        results: List of vulnerability dicts
        score: Numeric security score (0-100)

    Returns:
        dict with: summary, why_it_matters, priority_actions
    """
    counts = get_severity_counts(results)
    grade = get_grade(score)
    total = len(results)

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------
    summary = (
        f"Security scan completed with a score of {score}/100 (Grade: {grade}). "
        f"Total vulnerabilities detected: {total}. "
    )

    if counts["critical"] > 0:
        summary += (
            f"CRITICAL ALERT: {counts['critical']} critical vulnerabilities found "
            f"that require immediate remediation. "
        )

    if counts["high"] > 0:
        summary += (
            f"{counts['high']} high-severity issues detected that pose significant risk. "
        )

    if counts["medium"] > 0:
        summary += (
            f"{counts['medium']} medium-severity issues identified that should be "
            f"addressed in the next release cycle. "
        )

    if counts["low"] > 0:
        summary += (
            f"{counts['low']} low-severity findings noted for security hardening. "
        )

    if total == 0:
        summary = (
            f"Security scan completed with a score of {score}/100 (Grade: {grade}). "
            f"No vulnerabilities were detected. The application appears to follow "
            f"good security practices based on the tests performed."
        )

    # -----------------------------------------
    # WHY IT MATTERS
    # -----------------------------------------
    why_it_matters = "Unaddressed vulnerabilities expose the application to real-world attacks. "

    risk_areas = []

    vuln_names = [r.get("name", "").lower() for r in results]

    if any("sql injection" in n for n in vuln_names):
        risk_areas.append(
            "SQL Injection flaws allow attackers to read, modify, or delete "
            "database contents including user credentials and sensitive records"
        )

    if any("xss" in n or "cross-site scripting" in n for n in vuln_names):
        risk_areas.append(
            "Cross-Site Scripting enables session hijacking, credential theft, "
            "and phishing attacks targeting your users"
        )

    if any("csrf" in n for n in vuln_names):
        risk_areas.append(
            "CSRF vulnerabilities allow attackers to perform actions on behalf "
            "of authenticated users without their consent"
        )

    if any("ssl" in n or "tls" in n or "certificate" in n for n in vuln_names):
        risk_areas.append(
            "SSL/TLS weaknesses expose user data to interception through "
            "man-in-the-middle attacks"
        )

    if any("cookie" in n or "session" in n or "httponly" in n for n in vuln_names):
        risk_areas.append(
            "Session management flaws put user sessions at risk of hijacking "
            "and unauthorized access"
        )

    if any("header" in n or "csp" in n or "x-frame" in n for n in vuln_names):
        risk_areas.append(
            "Missing security headers leave the application vulnerable to "
            "clickjacking, MIME sniffing, and content injection attacks"
        )

    if risk_areas:
        why_it_matters += "Key risk areas identified: "
        for i, area in enumerate(risk_areas, 1):
            why_it_matters += f"({i}) {area}. "
    else:
        why_it_matters += (
            "Continue monitoring and testing the application regularly "
            "to maintain its security posture."
        )

    # -----------------------------------------
    # FIX PRIORITY LIST (sorted by severity)
    # -----------------------------------------
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    sorted_results = sorted(
        results,
        key=lambda r: severity_order.get(r.get("severity", "").lower(), 4)
    )

    priority_actions = []
    seen_actions = set()

    for r in sorted_results:
        action_key = r.get("name", "")
        if action_key in seen_actions:
            continue
        seen_actions.add(action_key)

        severity = r.get("severity", "Unknown")
        name = r.get("name", "Unknown Issue")
        location = r.get("location", "Unknown")
        recommendation = r.get("recommendation", "Review and fix this issue")

        action = (
            f"[{severity.upper()}] {name} at {location} - {recommendation}"
        )
        priority_actions.append(action)

    if not priority_actions:
        priority_actions.append(
            "No immediate actions required. Continue following "
            "security best practices and perform regular scans."
        )

    return {
        "summary": summary.strip(),
        "why_it_matters": why_it_matters.strip(),
        "priority_actions": priority_actions,
    }
