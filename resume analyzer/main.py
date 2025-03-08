from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF for PDF text extraction
import ollama  # AI model for resume analysis
import uvicorn
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="Resume Analyzer API")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for static files if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis: Optional[str] = None
    extracted_text: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_html():
    """Return the HTML for the frontend"""
    # Fix: Use explicit UTF-8 encoding when reading the file
    with open("static/index.html", "r", encoding="utf-8") as file:
        return file.read()

def extract_text_from_pdf(file_content):
    """Extracts text from a PDF file content"""
    try:
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")

def analyze_resume(resume_text):
    """Uses Ollama AI to analyze the resume"""
    try:
        model = "mistral"  # Ollama model
        prompt = f"""
        You are an expert resume analyst. Evaluate the following resume content:
        
        {resume_text}

        Provide:
        1️⃣ Strengths in resume
        2️⃣ Weaknesses or areas of improvement
        3️⃣ Suggested improvements to make it ATS-friendly
        4️⃣ Score out of 10 based on industry standards
        """

        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

@app.post("/analyze-resume", response_model=AnalysisResponse)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """Endpoint to analyze a resume from an uploaded PDF file"""
    if not file.filename.endswith('.pdf'):
        return AnalysisResponse(success=False, message="Please upload a PDF file")
    
    try:
        file_content = await file.read()
        resume_text = extract_text_from_pdf(file_content)
        
        if not resume_text:
            return AnalysisResponse(success=False, message="Could not extract text from the PDF")
        
        analysis_result = analyze_resume(resume_text)
        
        return AnalysisResponse(
            success=True, 
            message="Resume analyzed successfully", 
            analysis=analysis_result,
            extracted_text=resume_text[:2000]  # Limit display for large resumes
        )
    except Exception as e:
        return AnalysisResponse(success=False, message=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)