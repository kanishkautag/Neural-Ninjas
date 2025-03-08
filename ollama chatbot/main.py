from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Career Guidance AI Assistant")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Ollama API settings - update model name if needed
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"  # Make sure this model is installed

async def get_ollama_response(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I couldn't generate a response.")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "Error connecting to the AI model. Check if Ollama is running."
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Connection error. Make sure Ollama is running and '{MODEL_NAME}' is installed."

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask", response_class=JSONResponse)
async def ask_question(request: Request, question: str = Form(...)):
    enhanced_prompt = f"You are a career guidance assistant. Answer in 40-50 words. Answer: {question}"
    response = await get_ollama_response(enhanced_prompt)
    return {"answer": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)