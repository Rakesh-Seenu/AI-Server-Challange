import os
import json
from groq import Groq
from .base import AIPlatform
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
def load_api_keys():
    keys = {}
    if os.path.exists("api_keys.txt"):
        with open("api_keys.txt", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    keys[key.strip()] = value.strip()
    return keys

SYSTEM_PROMPT = """You are a specialized JSON data extraction API. You must follow these rules EXACTLY:

1. Output ONLY a single, valid JSON object
2. NO text before or after the JSON
3. Use ONLY double quotes for strings
4. ALL values must be strings (even numbers)
5. ESCAPE all special characters in strings
6. NO comments or explanations
7. NO line breaks within values
8. NO trailing commas
9. EXACT format: {"key": "value"}

Your task is to parse the provided email content and identify the following details:
- **amount**: The monetary value of the invoice/request as a string. (e.g., "1500.00")
- **currency**: The currency type as a string. (e.g., "USD", "EUR", "GBP")
- **due_date**: The date by which payment is due as a string. (e.g., "January 15, 2025", "2025-01-15")
- **description**: A brief description of the services or goods as a string. (e.g., "Software Development Services")
- **company**: The name of the company issuing the invoice or making the request as a string. (e.g., "Acme Corp")
- **contact**: The contact person or email for inquiries as a string. (e.g., "billing@acme.com")

If a field is not explicitly found in the input text, you MUST use an empty string ("") for its value. Ensure all values are strings, even for amounts."""

# Load from environment first
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# If not found, fallback to api_keys.txt
if not GROQ_API_KEY:
    api_keys = load_api_keys()
    GROQ_API_KEY = GROQ_API_KEY or api_keys.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in env or api_keys.txt")


class GroqPlatform(AIPlatform):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided")

        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"

    def chat(self, email_text: str) -> str:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": email_text
            }
        ]
        logging.info(f"Prompt: {email_text}")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        # Get the response content and ensure it's valid JSON
        response = completion.choices[0].message.content.strip()
        
        # Basic cleanup of potential formatting issues
        response = response.replace('\n', ' ').replace('\r', ' ')
        response = ' '.join(response.split())  # normalize whitespace
        
        try:
            # Validate JSON by parsing and re-stringifying
            parsed = json.loads(response)
            # Ensure all values are strings
            for key in parsed:
                parsed[key] = str(parsed[key]).strip()
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response from model: {response}")
            # Return a minimal valid JSON if parsing fails
            return json.dumps({
                "amount": "",
                "currency": "",
                "due_date": "",
                "description": "",
                "company": "",
                "contact": ""
            })


def get_ai_platform(model: str = None, api_key: str = None) -> AIPlatform:
    # We're only using Groq now, so model parameter is ignored
    return GroqPlatform(api_key=api_key or GROQ_API_KEY)
