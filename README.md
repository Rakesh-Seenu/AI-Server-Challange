# Simple AI Server
### Overview
This project implements a simple AI server with two core functionalities: chat completions and email data extraction. It's built using FastAPI and designed to be compatible with OpenAI's ChatCompletion API.

# Architecture diagram
<img width="745" height="426" alt="image" src="https://github.com/user-attachments/assets/cca09a42-5375-4f4c-8486-c03a69e7560e" />

# Requirements
Before running the application, ensure you have Python 3.8+ installed.

# Server Setup
The server listens on localhost:8090.
It implements two main endpoints: /v1/chat/completions and /v1/prefill.
The API is built with FastAPI.

1. Chat Completions Endpoint
Path: /v1/chat/completions
This endpoint acts as a proxy for chat completion models and is designed to be compatible with OpenAI's ChatCompletion API.
Supported Models:
- gpt-5-mini from OpenAI
- One free model from OpenRouter (e.g., deepseek/deepseek-r1-0528:free, moonshotai/kimi-k2:free, qwen/qwen3-235b-a22b:free)

2. Prefill Endpoint
Path: /v1/prefill
This endpoint is responsible for extracting specific payment information from email text and saving it to a data.csv file.
```
Request Format
POST /v1/prefill
Body: {
  "email_text": "...",
  "model": "..."
}

Response Format
Success: {"success": true, "message": "Data extracted and written successfully."}
Error: {"success": false, "message": "An unexpected error occurred: {error_details}"}
```

# Installation
To set up the project locally, follow these steps:
1. Clone the repository:
```git clone <your-repository-url>
cd <your-repository-name>
```
2. Create a virtual environment (recommended):
```python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```pip install -r requirements.txt```
4. Set up API Keys:
Create a .env file in the root directory of your project and add your API keys:
```
OPENAI_API_KEY="your_openai_api_key_here"
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```
Note: The actual implementation for how get_ai_platform uses these keys would determine the exact variable names, but python-dotenv is listed in requirements.txt, suggesting this approach.

# Usage
Running the Server
To start the FastAPI server, run the main.py file:
```
python main.py
```
The server will start at http://localhost:8090.

## Running Tests
To verify the functionality of the server, you can run the provided public tests. Make sure the server is running before executing the tests.
```
python public_test.py
```
This script will execute tests for both the chat completions and prefill endpoints and print the results to the console. It will also clean up the data.csv file after the tests complete.

# Project Structure
main.py: The main FastAPI application, containing the server endpoints.
public_test.py: A script to test the /v1/chat/completions and /v1/prefill endpoints.
requirements.txt: Lists all Python dependencies required for the project.
data.csv: (Generated) Stores the extracted data from emails.


Upload this project to a GitHub repository and share the link.

Zip the solution folder (as if you would publish it to Git) and send it back.
