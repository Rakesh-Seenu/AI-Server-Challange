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
        with open("prompts/system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

# Load from environment first
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# If not found, fallback to api_keys.txt
if not GROQ_API_KEY:
    api_keys = load_api_keys()
    GROQ_API_KEY = GROQ_API_KEY or api_keys.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in env or api_keys.txt")


class GroqPlatform(AIPlatform):
    def __init__(self, api_key: str = None, system_prompt: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.1-8b-instant"
        self.system_prompt = system_prompt or self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts/system_prompt.txt if available"""
        try:
            with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a helpful assistant. Keep answers concise (3–5 sentences max)."
        
    def chat(self, prompt: str) -> str:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content.strip()

system_prompt = load_system_prompt()

def get_ai_platform(model_name: str, groq_api_key: str = None) -> AIPlatform:
    # Since we're only using one model, we'll return the GroqPlatform instance
    # regardless of the model name input
    return GroqPlatform(api_key=groq_api_key or GROQ_API_KEY)
