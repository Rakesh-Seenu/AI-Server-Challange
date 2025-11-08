"""Simple public test for candidate to run"""

import json
import requests

SERVER_URL = "http://localhost:8090"


def test_chat_completions():
    """Test OpenAI proxy endpoint"""
    url = f"{SERVER_URL}/v1/chat/completions"
    payload = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": "Hello, respond with just 'Hi!'"}],
        "max_tokens": 10,
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    content = data["choices"][0]["message"]["content"].strip()
    print(f"✓ Chat completions: {content}")


def escape_json_string(s: str) -> str:
    """Escape a string exactly like Groq playground does"""
    # Replace backslashes first to avoid double escaping
    s = s.replace('\\', '\\\\')
    # Replace quotes
    s = s.replace('"', '\\"')
    # Replace newlines and other control characters
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return s

def test_prefill_simple():
    """Test prefill endpoint with simple email"""
    url = f"{SERVER_URL}/v1/prefill"

    # Test with the exact email content that worked in Groq playground
    email_text = '''Dear Ms. Patel,

I hope this message finds you well. This is a gentle reminder regarding Invoice #INV-7841 issued on October 28, 2025 for digital advertising campaign management and analytics reporting.

The total amount due is $5,320 USD, payable no later than November 25, 2025.

Kindly remit payment to the account listed on your invoice to ensure uninterrupted access to your campaign dashboard.

If you've already processed the payment, please disregard this email. Otherwise, do not hesitate to contact us for any clarifications.

Company: Apex Marketing Group
Contact: finance@apexmktg.com | +1 (646) 221-9988

Thank you for your prompt attention.'''
    
    # Create the payload as a dictionary first
    payload = {
        "email_text": email_text,
        "model": "llama"
    }
    
    # Convert to JSON with proper encoding
    json_data = json.dumps(payload, ensure_ascii=False)
    print("JSON payload:", repr(json_data))
    
    # Send as bytes to ensure proper encoding
    response = requests.post(
        url,
        data=json_data.encode('utf-8'),  # Convert to bytes with UTF-8 encoding
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }
    )
    
    # Send request with raw JSON data
    response = requests.post(
        url,
        data=json_data,  # Use data instead of json to send pre-formatted JSON
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    print("Response status:", response.status_code)
    print("Response headers:", dict(response.headers))
    print("Response content:", response.text)

    assert response.status_code == 200
    data = response.json()
    print(f"✓ Prefill: {json.dumps(data, separators=(',', ':'))}")
    assert data["success"] is True

    # Show CSV
    import os
    import csv

    if os.path.exists("data.csv"):
        with open("data.csv", "r") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                print(f"Row {i + 1}: {json.dumps(dict(row), separators=(',', ':'))}")


def cleanup_csv():
    """Clean up CSV file after tests"""
    import os

    if os.path.exists("data.csv"):
        os.remove("data.csv")
        print("Cleaned up data.csv file")


if __name__ == "__main__":
    try:
        test_chat_completions()
        test_prefill_simple()
        print("All tests passed!")
    finally:
        cleanup_csv()
