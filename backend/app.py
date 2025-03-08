# app.py
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import pandas as pd
import numpy as np
import joblib
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from difflib import get_close_matches

# Create FastAPI app
app = FastAPI(
    title="Recommendation API",
    description="API for recommending Udemy courses and jobs based on preferences",
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

# Path to model directory
MODEL_DIR = "model"

# Load models and data at startup
@app.on_event("startup")
async def load_models():
    global knn_model, level_encoder, subject_encoder, features, df
    global level_mapping, subject_mapping
    global job_tfidf, job_tfidf_matrix, job_similarity, job_indices, job_exp_level_encoder, jobs_df
    
    # Check if course model files exist
    if not os.path.exists(os.path.join(MODEL_DIR, 'knn_model.joblib')):
        raise RuntimeError("Course model files not found. Please run train_and_save_model.py first.")
    
    # Load course model and encoders
    knn_model = joblib.load(os.path.join(MODEL_DIR, 'knn_model.joblib'))
    level_encoder = joblib.load(os.path.join(MODEL_DIR, 'level_encoder.joblib'))
    subject_encoder = joblib.load(os.path.join(MODEL_DIR, 'subject_encoder.joblib'))
    features = joblib.load(os.path.join(MODEL_DIR, 'features.joblib'))
    
    # Load course dataframe
    df = pd.read_csv(os.path.join(MODEL_DIR, 'processed_courses.csv'))
    
    # Create course mappings
    level_mapping = dict(zip(level_encoder.classes_, level_encoder.transform(level_encoder.classes_)))
    subject_mapping = dict(zip(subject_encoder.classes_, subject_encoder.transform(subject_encoder.classes_)))
    
    # Check if job model files exist
    job_models_exist = os.path.exists(os.path.join(MODEL_DIR, 'job_tfidf_vectorizer.joblib'))
    
    if job_models_exist:
        # Load job models and data
        job_tfidf = joblib.load(os.path.join(MODEL_DIR, 'job_tfidf_vectorizer.joblib'))
        job_tfidf_matrix = joblib.load(os.path.join(MODEL_DIR, 'job_tfidf_matrix.joblib'))
        job_similarity = joblib.load(os.path.join(MODEL_DIR, 'job_similarity_matrix.joblib'))
        job_indices = joblib.load(os.path.join(MODEL_DIR, 'job_indices.joblib'))
        job_exp_level_encoder = joblib.load(os.path.join(MODEL_DIR, 'job_exp_level_encoder.joblib'))
        
        # Load job dataframe
        jobs_df = pd.read_csv(os.path.join(MODEL_DIR, 'processed_jobs.csv'))
        
        print("Course and job models loaded successfully!")
    else:
        print("Course models loaded successfully! Job models not found.")

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

# Define response models for jobs
class Job(BaseModel):
    job_id: str
    Job_Title: str
    Job_Experience_Required: str
    Key_Skills: str
    salary: Optional[float] = None
    company: Optional[str] = None
    location: Optional[str] = None
    num_applicants: Optional[int] = None
    num_views: Optional[int] = None
    description: Optional[str] = None
    url: Optional[str] = None

class JobRecommendationResponse(BaseModel):
    recommendations: List[Job]
    count: int

class JobTitlesResponse(BaseModel):
    job_titles: List[str]

class ExpLevelListResponse(BaseModel):
    experience_levels: List[str]

# Course Endpoints
@app.get("/courses/levels", response_model=LevelListResponse)
async def get_course_levels():
    """Get all available course levels"""
    return {"levels": sorted(level_mapping.keys())}

@app.get("/courses/subjects", response_model=SubjectListResponse)
async def get_course_subjects():
    """Get all available course subjects"""
    return {"subjects": sorted(subject_mapping.keys())}

@app.get("/courses/recommend", response_model=CourseRecommendationResponse)
async def recommend_courses(
    level: str = Query(..., description="Course level"),
    subject: str = Query(..., description="Course subject"),
    limit: int = Query(5, description="Number of recommendations to return")
):
    """
    Get course recommendations based on level and subject
    """
    # Check if level exists
    if level not in level_mapping:
        raise HTTPException(
            status_code=404, 
            detail=f"Level '{level}' not found. Available levels: {list(level_mapping.keys())}"
        )
    
    # Check if subject exists
    if subject not in subject_mapping:
        raise HTTPException(
            status_code=404, 
            detail=f"Subject '{subject}' not found"
        )
    
    # Get encoded values
    level_encoded = level_mapping[level]
    subject_encoded = subject_mapping[subject]
    
    # Create query vector
    query_vector = np.array([
        level_encoded, 
        subject_encoded,
        0.75,  # Use 75th percentile for popularity features
        0.75
    ]).reshape(1, -1)
    
    # Get recommendations
    distances, indices = knn_model.kneighbors(query_vector, n_neighbors=min(50, len(df)))
    
    # Get recommended courses
    recommended_indices = indices[0]
    
    # Filter for exact level and subject matches first
    exact_matches = []
    level_matches = []
    other_matches = []
    
    for idx in recommended_indices:
        course = df.iloc[idx]
        if course['level'] == level and course['subject'] == subject:
            exact_matches.append(idx)
        elif course['level'] == level:
            level_matches.append(idx)
        else:
            other_matches.append(idx)
    
    # Combine matches in priority order
    all_matches = exact_matches + level_matches + other_matches
    
    # Get final recommendations (limiting to top_n)
    final_indices = all_matches[:limit]
    
    if not final_indices:
        return {"recommendations": [], "count": 0}
    
    # Get selected courses
    selected_cols = ['course_id', 'course_title', 'level', 'subject', 'price', 'num_subscribers', 'num_reviews', 'url']
    available_cols = [col for col in selected_cols if col in df.columns]
    recommendations = df.iloc[final_indices][available_cols].to_dict(orient='records')
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@app.get("/courses/search_subject", response_model=List[str])
async def search_course_subject(query: str = Query(..., description="Subject search query")):
    """Search for course subjects matching the query"""
    from difflib import get_close_matches
    
    subjects = list(subject_mapping.keys())
    matches = get_close_matches(query, subjects, n=5, cutoff=0.2)
    
    # If no close matches, do a more lenient search
    if not matches:
        matches = [s for s in subjects if query.lower() in s.lower()][:5]
    
    return matches

# Job Endpoints
@app.get("/jobs/titles", response_model=JobTitlesResponse)
async def get_job_titles():
    """Get all available job titles"""
    try:
        return {"job_titles": sorted(job_indices.index.tolist())}
    except NameError:
        raise HTTPException(
            status_code=404,
            detail="Job models not loaded. Please run train_and_save_job_model.py first."
        )

@app.get("/jobs/experience_levels", response_model=ExpLevelListResponse)
async def get_job_experience_levels():
    """Get all available job experience levels"""
    try:
        return {"experience_levels": sorted(job_exp_level_encoder.classes_.tolist())}
    except NameError:
        raise HTTPException(
            status_code=404,
            detail="Job models not loaded. Please run train_and_save_job_model.py first."
        )

@app.get("/jobs/recommend_by_title", response_model=JobRecommendationResponse)
async def recommend_jobs_by_title(
    job_title: str = Query(..., description="Job title to find similar jobs for"),
    limit: int = Query(5, description="Number of recommendations to return")
):
    """
    Get job recommendations based on a job title using TF-IDF similarity of skills
    """
    try:
        # Check if job title exists
        if job_title not in job_indices.index:
            close_matches = get_close_matches(job_title, job_indices.index.tolist(), n=5, cutoff=0.6)
            if close_matches:
                suggestion_text = f"Job title '{job_title}' not found. Did you mean one of these: {', '.join(close_matches)}?"
            else:
                suggestion_text = f"Job title '{job_title}' not found. Available job titles: {', '.join(job_indices.index.tolist()[:5])}..."
            
            raise HTTPException(status_code=404, detail=suggestion_text)
        
        # Get recommendations
        index = job_indices[job_title]
        similarity_scores = list(enumerate(job_similarity[index]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        similarity_scores = similarity_scores[:limit]
        job_indices_list = [i[0] for i in similarity_scores]
        
        if not job_indices_list:
            return {"recommendations": [], "count": 0}
        
        # Get selected jobs
        selected_cols = ['job_id', 'Job Title', 'Job Experience Required', 'Key Skills', 
                        'salary', 'company', 'location', 'num_applicants', 'num_views', 'description', 'url']
        available_cols = [col for col in selected_cols if col in jobs_df.columns]
        
        # Rename columns for the response model
        rename_dict = {
            'Job Title': 'Job_Title',
            'Job Experience Required': 'Job_Experience_Required',
            'Key Skills': 'Key_Skills'
        }
        
        recommendations_df = jobs_df.iloc[job_indices_list][available_cols].copy()
        for old_col, new_col in rename_dict.items():
            if old_col in recommendations_df.columns:
                recommendations_df = recommendations_df.rename(columns={old_col: new_col})
        
        recommendations = recommendations_df.to_dict(orient='records')
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    except NameError:
        raise HTTPException(
            status_code=404,
            detail="Job models not loaded. Please run train_and_save_job_model.py first."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error recommending jobs: {str(e)}"
        )

@app.get("/jobs/search_title", response_model=List[str])
async def search_job_title(query: str = Query(..., description="Job title search query")):
    """Search for job titles matching the query"""
    try:
        from difflib import get_close_matches
        
        job_titles = job_indices.index.tolist()
        matches = get_close_matches(query, job_titles, n=5, cutoff=0.2)
        
        # If no close matches, do a more lenient search
        if not matches:
            matches = [t for t in job_titles if query.lower() in t.lower()][:5]
        
        return matches
    
    except NameError:
        raise HTTPException(
            status_code=404,
            detail="Job models not loaded. Please run train_and_save_job_model.py first."
        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)