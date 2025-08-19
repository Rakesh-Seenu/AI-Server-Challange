import os
from fastapi import FastAPI
import csv
import json
from fastapi import FastAPI
from pydantic import BaseModel
from src.ai.openai_chat import get_ai_platform
from src.auth.ratelimit import apply_rate_limit

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["amount", "currency", "due_date", "description", "company", "contact"])
        writer.writeheader()

app = FastAPI(
    title="AI Server",
    description="A simple AI server with chat completions and data extraction capabilities.",
)

# 1. Chat Completions Endpoint

class ChatRequest(BaseModel):
    model_name: str
    prompt: str

class PrefillRequest(BaseModel):
    email_text: str
    model: str  

class PrefillResponse(BaseModel):
    success: bool
    message: str

class ChatResponse(BaseModel):
    response: str
    

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat(request: ChatRequest):
    apply_rate_limit("global_unauthenticated_user")
    response_text = get_ai_platform(request.model_name).chat(request.prompt)
    return ChatResponse(response=response_text)

# 2. prefill Endpoint
@app.post("/v1/prefill", response_model=PrefillResponse)
async def prefill(request: PrefillRequest):
    """
    Extracts structured data from email text using an AI model
    and saves it to a CSV file.
    """
    try:
        email_text = request.email_text
        model = request.model
        
        with open("input_email_text.log", "a", encoding="utf-8") as log_file:
            log_file.write(email_text + "\n---\n")
        ai_instance = get_ai_platform(model)
        
        response_text = ai_instance.chat(request.email_text)

        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: Model returned invalid JSON: {response_text}. Error: {e}")
            return {"success": False, "message": f"Model did not return valid JSON. AI response: {response_text}"}

        required_fields = ["amount", "currency", "due_date", "description", "company", "contact"]

        row = {field: extracted_data.get(field, "") for field in required_fields}
        
        try:
            row["amount"] = float(row["amount"]) if row["amount"] else 0.0
        except ValueError:
            print(f"Warning: Could not convert amount '{row['amount']}' to float. Defaulting to 0.0.")
            row["amount"] = 0.0 

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=required_fields)
            writer.writerow(row)

        return {"success": True, "message": "Data extracted and written successfully."}
    except Exception as e:

        print(f"Exception in prefill endpoint: {e}")
        return {"success": False, "message": f"An unexpected error occurred: {e}"}

    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8090)