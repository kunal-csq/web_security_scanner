import os
import requests

def generate_ai_analysis(results, score):

    api_key = os.getenv("OPENROUTER_API_KEY")

    prompt = f"""
You are a senior cloud security analyst.

Scan score: {score}

Vulnerabilities found:
{results}

Provide:
1. Summary
2. Why it matters
3. Priority actions list
"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()

    try:
        content = data['choices'][0]['message']['content']
    except:
        return {
            "summary": "AI analysis unavailable.",
            "why_it_matters": "Error generating AI response.",
            "priority_actions": ["Review vulnerabilities manually."]
        }

    return {
        "summary": content,
        "why_it_matters": content,
        "priority_actions": [
            "Fix high severity vulnerabilities first",
            "Implement secure headers",
            "Sanitize user inputs",
            "Enable CSRF protection"
        ]
    }
