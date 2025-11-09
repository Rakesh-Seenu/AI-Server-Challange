import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import csv
import json
import traceback
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from src.ai.openai_chat import get_ai_platform
import logging
from src.ai.openai_prefill import get_ai_platform as get_prefill_platform
from src.auth.ratelimit import apply_rate_limit

# Define absolute paths for data and log files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.csv")
LOG_FILE = os.path.join(BASE_DIR, "input_email_text.log")
logger = logging.getLogger(__name__)

# Ensure the data file exists with headers
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["amount", "currency", "due_date", "description", "company", "contact"])
        writer.writeheader()

app = FastAPI(
    title="AI Server",
    description="A simple AI server with chat completions and data extraction capabilities.",
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get raw request body for debugging
    body = await request.body()
    body_str = body.decode('utf-8')
    print(f"Raw request body: {repr(body_str)}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "msg": str(err.get("msg")),
                    "loc": err.get("loc"),
                    "type": err.get("type"),
                    "ctx": {
                        "error": str(err),
                        "raw_body": repr(body_str)  # Include raw body in error response
                    }
                }
                for err in exc.errors()
            ]
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
# 1. Chat Completions Endpoint
from pydantic import ConfigDict

class ChatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str
    prompt: str

from typing import Optional
import re

class PrefillRequest(BaseModel):
    email_text: str
    model: str = "llama"
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email_text": """Dear Ms. Patel,

I hope this message finds you well. """,
                "model": "llama"
            }
        }
    )

    def clean_email_text(self) -> str:
        """Clean and normalize email text"""
        if not self.email_text:
            return ""
        # Handle different types of line endings
        email = self.email_text.replace('\r\n', '\n').replace('\r', '\n')
        # Normalize multiple newlines
        email = re.sub(r'\n{3,}', '\n\n', email)
        # Remove any potential control characters
        email = ''.join(char for char in email if ord(char) >= 32 or char in '\n\t')
        return email.strip()

class PrefillResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

    @classmethod
    def validate_text(cls, v: str) -> str:
        """Pre-validate text before model instantiation"""
        if not isinstance(v, str):
            raise ValueError("email_text must be a string")
        if not v.strip():
            raise ValueError("email_text cannot be empty")
        return v

    def clean_email_text(self) -> str:
        """Clean and normalize email text"""
        # First validate the text
        text = self.validate_text(self.email_text)
        
        # Convert to string and normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove null bytes and other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Normalize multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Final cleanup
        return text.strip()

class PrefillResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Apply rate limit for chat endpoint
    print("Applying rate limit for chat endpoint")
    apply_rate_limit("global_unauthenticated_user")
    response_text = get_ai_platform(request.model_name).chat(request.prompt)
    return ChatResponse(response=response_text)

# 2. prefill Endpoint
@app.post("/v1/prefill", response_model=PrefillResponse)
async def prefill(request_data: PrefillRequest):
    """
    Extracts structured data from email text using an AI model and saves it to a CSV file.

    Example request: curl -X POST "http://127.0.0.1:8090/v1/prefill" -H "Content-Type: application/json" -d '{"email_text": "Your email content here", "model": "llama"}'
    """
    try:

        if not request_data.email_text:
            return JSONResponse(
                status_code=422,
                content={"detail": "email_text is required"}
            )

        # Apply rate limit for prefill endpoint
        print("Applying rate limit for prefill endpoint")
        apply_rate_limit("global_unauthenticated_user")
        print("Rate limit applied successfully")
        
        # Clean and normalize the email text
        cleaned_email = request_data.clean_email_text()
        
        # Log the incoming email text
        try:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- New Request at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                log_file.write(cleaned_email + "\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
        
        # Get AI response
        ai_instance = get_prefill_platform(request_data.model)
        response_text = ai_instance.chat(cleaned_email)
        
        # Log the AI response
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"AI Response:\n{response_text}\n")
        except Exception as e:
            print(f"Warning: Could not write AI response to log: {e}")

        # Parse JSON response
        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            error_msg = f"Model did not return valid JSON. AI response: {response_text}"
            print(f"JSONDecodeError: {error_msg}. Error: {e}")
            return {"success": False, "message": error_msg}

        # Validate and process the data
        required_fields = ["amount", "currency", "due_date", "description", "company", "contact"]
        row = {field: extracted_data.get(field, "") for field in required_fields}
        
        # # Convert amount to float
        # try:
        #     row["amount"] = float(row["amount"]) if row["amount"] else int(row["amount"])
        # except ValueError as e:
        #     print(f"Warning: Could not convert amount '{row['amount']}' to float. Error: {e}")
        #     row["amount"] = 0.0

        # Save to CSV
        try:
            with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=required_fields)
                writer.writerow(row)
        except Exception as e:
            error_msg = f"Failed to write to CSV file: {e}"
            print(f"Error: {error_msg}")
            return {"success": False, "message": error_msg}

        return {"success": True, "message": "Data extracted and written successfully."}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
        print(f"Exception in prefill endpoint: {error_msg}")
        return {"success": False, "message": error_msg}

    
if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    # Add the project root to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    
    # Run using the module import string format
    uvicorn.run("main:app", host="127.0.0.1", port=8090, reload=True)