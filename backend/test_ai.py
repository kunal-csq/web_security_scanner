from google import genai
import os

client = genai.Client(api_key="AIzaSyCVVpKGWb3hT-zqKzYJ4Qf8tgWBfp6R2YQ")

response = client.models.generate_content(
    model="gemini-1.5-flash-latest",
    contents="Hello"
)

print(response.text)
