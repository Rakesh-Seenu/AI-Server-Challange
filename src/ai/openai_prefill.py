import os
from openai import OpenAI
from .base import AIPlatform
from dotenv import load_dotenv
load_dotenv()

def load_api_keys():
    keys = {}
    if os.path.exists("api_keys.txt"):
        with open("api_keys.txt", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    keys[key.strip()] = value.strip()
    return keys

def load_system_prompt():
    try:
        with open("prompts/prefill_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

# Load from environment first
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# If not found, fallback to api_keys.txt
if not OPENAI_API_KEY or not OPENROUTER_API_KEY:
    api_keys = load_api_keys()
    OPENAI_API_KEY = OPENAI_API_KEY or api_keys.get("OPENAI_API_KEY")
    OPENROUTER_API_KEY = OPENROUTER_API_KEY or api_keys.get("OPENROUTER_API_KEY")

if not OPENAI_API_KEY or not OPENROUTER_API_KEY:
    raise ValueError("OPENAI_API_KEY or OPENROUTER_API_KEY not set in env or api_keys.txt")


class OpenAIPlatform(AIPlatform):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", prefill_prompt: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.prefill_prompt = prefill_prompt or self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts/system_prompt.txt if available"""
        try:
            with open("prompts/prefill_prompt.md", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Extract the following fields from the email and return only valid JSON with no extra text: amount, currency, due_date, description, company, contact (with name, department, email, phone, website)"
        
    def chat(self, email_text: str) -> str:
        messages = []
        if self.prefill_prompt:
            messages.append({"role": "system", "content": self.prefill_prompt})
        messages.append({"role": "user", "content": email_text})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "InvoiceExtraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"},
                            "due_date": {"type": "string"},
                            "description": {"type": "string"},
                            "company": {"type": "string"},
                            "contact": {"type": "string"}
                        },
                        "required": [
                            "amount", "currency", "due_date", 
                            "description", "company", "contact"
                        ]
                    }
                }
            }
        )

        return response.choices[0].message.content.strip()


class OpenRouterPlatform(AIPlatform):
    def __init__(self, api_key: str = None, model: str = "deepseek/deepseek-r1-0528:free", prefill_prompt: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided for OpenRouterPlatform")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",  
        )
        self.model = model
        self.prefill_prompt = prefill_prompt or self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts/system_prompt.txt if available"""
        try:
            with open("prompts/prefill_prompt.md", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a helpful assistant. Keep answers concise (3–5 sentences max)."

    def chat(self, prompt: str) -> str:
        messages = []
        if self.prefill_prompt:
            messages.append({"role": "system", "content": self.prefill_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "InvoiceExtraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"},
                            "due_date": {"type": "string"},
                            "description": {"type": "string"},
                            "company": {"type": "string"},
                            "contact": {"type": "string"}
                        },
                        "required": [
                            "amount", "currency", "due_date", 
                            "description", "company", "contact"
                        ]
                    }
                }
            }
        )

        return response.choices[0].message.content.strip()


system_prompt = load_system_prompt()

def get_ai_platform(model: str, openai_api_key: str = None, openrouter_api_key: str = None) -> AIPlatform:
    model_map = {
        "gpt": "gpt-5-mini",
        "deepseek": "deepseek/deepseek-r1-0528:free"
    }

    mapped_model = model_map.get(model.lower(), model)

    if "gpt" in mapped_model:
        return OpenAIPlatform(api_key=openai_api_key or OPENAI_API_KEY, model=mapped_model)
    elif "deepseek" in mapped_model or "moonshotai" in mapped_model or "qwen" in mapped_model:
        return OpenRouterPlatform(api_key=openrouter_api_key or OPENROUTER_API_KEY, model=mapped_model)
    else:
        raise ValueError(f"Unsupported model: {model}")
