import requests

def scan(url, depth):
    payload = "<script>alert(1)</script>"

    try:
        response = requests.get(url + payload, timeout=5)

        if payload.lower() in response.text.lower():
            return {
                "name": "Cross-Site Scripting (XSS)",
                "severity": "Medium",
                "confidence": "High",
                "description": "User input is reflected without proper sanitization",
                "evidence": "Script payload reflected in response"
            }

    except Exception as e:
        return {
            "name": "Cross-Site Scripting (XSS)",
            "severity": "Low",
            "confidence": "Low",
            "description": f"Request failed: {str(e)}"
        }

    return {
        "name": "Cross-Site Scripting (XSS)",
        "severity": "Low",
        "confidence": "Medium",
        "description": "No reflected XSS patterns detected"
    }
