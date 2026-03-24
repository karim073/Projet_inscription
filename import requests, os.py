import requests, os

api_key = os.environ.get("MAILGUN_API_KEY")
domain = os.environ.get("MAILGUN_DOMAIN")
email_from = os.environ.get("EMAIL_FROM")

response = requests.post(
    f"https://api.mailgun.net/v3/{domain}/messages",
    auth=("api", api_key),
    data={
        "from": email_from,
        "to": "ton_email_test@example.com",
        "subject": "Test",
        "text": "Bonjour, ceci est un test Mailgun."
    }
)
print(response.status_code, response.text)