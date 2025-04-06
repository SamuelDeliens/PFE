import requests

url = "https://api.mantiks.io/company/jobs?linkedin_url=https%3A%2F%2Ffr.linkedin.com%2Fcompany%2Fgoogle&website=https%3A%2F%2Fabout.google&age_in_days=-2147483648&keyword=&keyword_excluded="

headers = {
    "accept": "application/json",
    "x-api-key": "Hello"
}

response = requests.get(url, headers=headers)

print(response.text)