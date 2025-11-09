import requests
import json

# Test the prefill endpoint
response = requests.post("http://localhost:8090/v1/prefill", json={
    "email_text": """Dear Ms. Patel,

I hope this message finds you well. This is a gentle reminder regarding Invoice #INV-7841 issued on October 28, 2025 for digital advertising campaign management and analytics reporting.

The total amount due is $5,320 USD, payable no later than November 25, 2025.

Kindly remit payment to the account listed on your invoice to ensure uninterrupted access to your campaign dashboard.

If you've already processed the payment, please disregard this email. Otherwise, do not hesitate to contact us for any clarifications.

Company: Apex Marketing Group
Contact: finance@apexmktg.com
 | +1 (646) 221-9988

Thank you for your prompt attention.""",
    "model": "llama"
})

print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))
