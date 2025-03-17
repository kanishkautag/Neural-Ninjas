from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
import uvicorn
from pydantic import BaseModel
import os
import shutil
import fitz  # PyMuPDF for PDF text extraction
import ollama  # AI model for resume analysis

# Import functions from the separate modules
from gemini_path import generate_learning_path
from courses import (
    recommend_courses, 
    get_course_levels, 
    get_course_subjects, 
    search_course_subject
)
from resume_analyzer import extract_text_from_pdf, analyze_resume
from config import settings

# Import the JobSearchAgent - updated to match your file structure
from agents import JobSearchAgent

# Create FastAPI app
app = FastAPI(
    title="Learning Path & Career Services API",
    description="API for recommending courses, generating learning paths, and job searching",
    version="1.1.0"
)

# Initialize the job search agent
job_search_agent = JobSearchAgent()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create a directory for static files if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define response models for courses
class Course(BaseModel):
    course_id: str
    course_title: str
    level: str
    subject: str
    price: float
    num_subscribers: int
    num_reviews: int
    url: Optional[str] = None

class CourseRecommendationResponse(BaseModel):
    recommendations: List[Course]
    count: int

class LevelListResponse(BaseModel):
    levels: List[str]

class SubjectListResponse(BaseModel):
    subjects: List[str]

class LearningPathResponse(BaseModel):
    learning_path: List[str]

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis: Optional[str] = None
    extracted_text: Optional[str] = None

# Chatbot models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    message: str
    conversation_history: List[ChatMessage]

# Job Search models
class JobSearchRequest(BaseModel):
    industry: str
    keywords: str
    location: str
    time_period: str

class SkillsetRequest(BaseModel):
    profession: str
    experience_level: str

class JobData(BaseModel):
    title: str
    link: str
    snippet: str
    source: str

class JobSearchResponse(BaseModel):
    jobs: List[JobData]
    market_summary: str
    query: Dict[str, Any]

class SkillsetResponse(BaseModel):
    profession: str
    experience_level: str
    skillset: Dict[str, List[str]]

# API Routes - these endpoints will be consumed by your frontend

# Course Endpoints
@app.get("/api/courses/levels", response_model=LevelListResponse)
async def get_levels():
    """Get all available course levels"""
    return {"levels": get_course_levels()}

@app.get("/api/courses/subjects", response_model=SubjectListResponse)
async def get_subjects():
    """Get all available course subjects"""
    return {"subjects": get_course_subjects()}

@app.get("/api/courses/recommend", response_model=CourseRecommendationResponse)
async def recommend(
    level: str = Query(..., description="Course level"),
    subject: str = Query(..., description="Course subject"),
    limit: int = Query(5, description="Number of recommendations to return")
):
    """Get course recommendations based on level and subject"""
    recommendations, count = recommend_courses(level, subject, limit)
    return {"recommendations": recommendations, "count": count}

@app.get("/api/courses/search_subject", response_model=List[str])
async def search_subject(query: str = Query(..., description="Subject search query")):
    """Search for course subjects matching the query"""
    return search_course_subject(query)

# Learning Path Endpoints
@app.get("/api/learning-path", response_model=LearningPathResponse)
async def get_learning_path(
    career: str = Query(..., description="Career path, e.g., Machine Learning Engineer"),
    num_points: int = Query(10, description="Number of learning points")
):
    """Generate a learning path for a specific career"""
    try:
        learning_path = generate_learning_path(career, num_points)
        return {"learning_path": learning_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")

# Resume Analyzer Endpoint
@app.post("/api/analyze-resume", response_model=AnalysisResponse)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """Endpoint to analyze a resume from an uploaded PDF file"""
    if not file.filename.endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Please upload a PDF file"}
        )
    
    try:
        file_content = await file.read()
        resume_text = extract_text_from_pdf(file_content)
        
        if not resume_text:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Could not extract text from the PDF"}
            )
        
        analysis_result = analyze_resume(resume_text)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True, 
                "message": "Resume analyzed successfully", 
                "analysis": analysis_result,
                "extracted_text": resume_text[:2000]  # Limit display for large resumes
            }
        )
    except Exception as e:
        # Log the error server-side for debugging
        print(f"Error analyzing resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error: {str(e)}"}
        )

# Chatbot Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Endpoint for the AI chatbot conversation"""
    try:
        # Format the conversation history for the AI model
        formatted_history = []
        for msg in request.conversation_history:
            formatted_history.append({"role": msg.role, "content": msg.content})
        
        # Define a system message to guide the AI behavior
        system_message = {
            "role": "system",
                "content": """"You are a Career AI Assistant for SkillMorph, designed to help users improve their career paths in AI and technology. Offer concise, actionable advice on resume building, job searches, technical skill development, and career planning. Provide clear, practical responses with real-world examples when necessary. Break down complex topics step by step, while staying within the context of user-provided information. Maintain a friendly and helpful tone, focusing solely on career growth and skill enhancement. Your answers should be precise and to the point"""
        }
        
        # Add the new user message
        new_message = {"role": "user", "content": request.message}
        
        # Combine conversation for the AI model
        messages = [system_message] + formatted_history + [new_message]
        
        # Get response from Ollama AI
        model = "llama3.2:1b"  # Or any other model you prefer
        response = ollama.chat(model=model, messages=messages)
        assistant_message = response['message']['content']
        
        # Update conversation history
        updated_history = request.conversation_history + [
            ChatMessage(role="user", content=request.message),
            ChatMessage(role="assistant", content=assistant_message)
        ]
        
        return ChatResponse(
            message=assistant_message,
            conversation_history=updated_history
        )
    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Sorry, I'm having trouble processing your request right now."}
        )

# Job Search Endpoints
@app.post("/api/job-search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """Search for jobs based on industry, keywords, location, and time period"""
    try:
        result = job_search_agent.search_jobs(
            industry=request.industry,
            keywords=request.keywords,
            location=request.location,
            time_period=request.time_period
        )
        
        # Convert results to match the response model
        jobs = [JobData(**job) for job in result.get("jobs", [])]
        
        return JobSearchResponse(
            jobs=jobs,
            market_summary=result.get("market_summary", ""),
            query=result.get("query", {})
        )
    except Exception as e:
        print(f"Error searching jobs: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching for jobs: {str(e)}"
        )

@app.post("/api/skillset", response_model=SkillsetResponse)
async def get_skillset(request: SkillsetRequest):
    try:
        result = job_search_agent.get_professional_skillset(
            profession=request.profession,
            experience_level=request.experience_level
        )
        
        return SkillsetResponse(
            profession=result.get("profession", ""),
            experience_level=result.get("experience_level", ""),
            skillset=result.get("skillset", {})
        )
    except Exception as e:
        print(f"Error getting skillset: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving skillset information: {str(e)}"
        )
# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy"}

if __name__=="__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)