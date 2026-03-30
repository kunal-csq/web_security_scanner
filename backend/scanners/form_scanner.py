import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_all_forms(url):

    try:

        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        forms = soup.find_all("form")

        form_details = []

        for form in forms:

            action = form.attrs.get("action")
            method = form.attrs.get("method", "get").lower()

            inputs = []

            for input_tag in form.find_all("input"):
                input_name = input_tag.attrs.get("name")
                input_type = input_tag.attrs.get("type", "text")

                inputs.append({
                    "name": input_name,
                    "type": input_type
                })

            form_details.append({
                "action": urljoin(url, action),
                "method": method,
                "inputs": inputs
            })

        return form_details

    except:
        return []
