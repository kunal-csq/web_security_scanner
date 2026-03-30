from scanners.crawler import extract_forms

forms = extract_forms("https://demo.owasp-juice.shop")

print(forms)