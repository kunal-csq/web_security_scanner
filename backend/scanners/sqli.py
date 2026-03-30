import requests

def scan(url, depth):
    test_payload = "'"
    try:
        response = requests.get(url + test_payload, timeout=5)

        if any(err in response.text.lower() for err in ["sql", "syntax", "mysql", "sqlite"]):
            return {
                "name": "SQL Injection",
                "severity": "High",
                "confidence": "High",
                "description": "Potential SQL error messages detected in response",
                "evidence": "Database error pattern found"
            }

    except Exception as e:
        return {
            "name": "SQL Injection",
            "severity": "Low",
            "confidence": "Low",
            "description": f"Request failed: {str(e)}"
        }

    return {
        "name": "SQL Injection",
        "severity": "Low",
        "confidence": "Medium",
        "description": "No SQL injection patterns detected"
    }
