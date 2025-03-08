# app.py
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Union
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
    description="API for recommending Udemy courses based on preferences",
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
    
    print("Course models loaded successfully!")

# Define response models for courses
class Course(BaseModel):
    course_id: Union[str, int]
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
    
    # Convert course_id to string for all recommendations
    for recommendation in recommendations:
        recommendation['course_id'] = str(recommendation['course_id'])
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@app.get("/courses/search_subject", response_model=List[str])
async def search_course_subject(query: str = Query(..., description="Subject search query")):
    """Search for course subjects matching the query"""
    subjects = list(subject_mapping.keys())
    matches = get_close_matches(query, subjects, n=5, cutoff=0.2)
    
    # If no close matches, do a more lenient search
    if not matches:
        matches = [s for s in subjects if query.lower() in s.lower()][:5]
    
    return matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
