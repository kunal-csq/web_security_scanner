import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_forms(url):

    forms = []

    try:

        res = requests.get(url, timeout=10)

        soup = BeautifulSoup(res.text, "html.parser")

        for form in soup.find_all("form"):

            action = form.attrs.get("action")
            method = form.attrs.get("method", "get").lower()

            inputs = []

            for inp in form.find_all("input"):

                input_name = inp.attrs.get("name")
                input_type = inp.attrs.get("type", "text")

                inputs.append({
                    "name": input_name,
                    "type": input_type
                })

            forms.append({
                "action": urljoin(url, action),
                "method": method,
                "inputs": inputs
            })

    except Exception as e:
        print("Crawler error:", e)

    return forms