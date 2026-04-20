"""
DAST Security Score Calculator
Calculates a security score from 100 based on vulnerability severity.
"""


# Severity weight mapping
SEVERITY_WEIGHTS = {
    "critical": -30,
    "high": -20,
    "medium": -10,
    "low": -5,
    "info": 0,
}


def calculate_score(results):
    """
    Calculate security score starting from 100.

    Args:
        results: List of vulnerability dicts with 'severity' field

    Returns:
        int: Score from 0 to 100
    """
    score = 100

    for r in results:
        severity = r.get("severity", "").lower()
        score += SEVERITY_WEIGHTS.get(severity, 0)

    return max(score, 0)


def get_severity_counts(results):
    """
    Count vulnerabilities by severity level.

    Args:
        results: List of vulnerability dicts

    Returns:
        dict: {critical: n, high: n, medium: n, low: n}
    """
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for r in results:
        severity = r.get("severity", "").lower()
        if severity in counts:
            counts[severity] += 1

    return counts


def get_grade(score):
    """
    Convert numeric score to letter grade.

    Args:
        score: Numeric score 0-100

    Returns:
        str: Letter grade (A+, A, B, C, D, F)
    """
    if score >= 95:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 30:
        return "D"
    else:
        return "F"
