from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uvicorn
from pydantic import BaseModel
import os
import shutil

# Import functions from the separate modules
from gemini_path import generate_learning_path
from courses import (
    recommend_courses, 
    get_course_levels, 
    get_course_subjects, 
    search_course_subject
)
from resume_analyzer import extract_text_from_pdf, analyze_resume

# Create FastAPI app
app = FastAPI(
    title="Learning Path & Course Recommendation API",
    description="API for recommending courses and generating learning paths",
    version="1.0.0"
)


# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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



@app.post("/analyze-resume", response_model=AnalysisResponse)
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

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy"}



if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)