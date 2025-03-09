import fitz  # PyMuPDF for PDF text extraction
import ollama  # AI model for resume analysis
from fastapi import HTTPException
from gemini_path import gmodel

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
        model = "llama3.2:1b"  # Ollama model
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