import os
import pandas as pd
import joblib
import numpy as np
from typing import List, Dict, Tuple
from difflib import get_close_matches

MODEL_DIR = "model"

# Load models and encoders at startup
knn_model = joblib.load(os.path.join(MODEL_DIR, 'knn_model.joblib'))
level_encoder = joblib.load(os.path.join(MODEL_DIR, 'level_encoder.joblib'))
subject_encoder = joblib.load(os.path.join(MODEL_DIR, 'subject_encoder.joblib'))
df = pd.read_csv(os.path.join(MODEL_DIR, 'processed_courses.csv'))

level_mapping = dict(zip(level_encoder.classes_, level_encoder.transform(level_encoder.classes_)))
subject_mapping = dict(zip(subject_encoder.classes_, subject_encoder.transform(subject_encoder.classes_)))

def get_course_levels() -> List[str]:
    """Return a list of all course levels."""
    return sorted(level_mapping.keys())

def get_course_subjects() -> List[str]:
    """Return a list of all course subjects."""
    return sorted(subject_mapping.keys())

def recommend_courses(level: str, subject: str, limit: int = 5) -> Tuple[List[Dict[str, any]], int]:
    """Recommend courses based on the level and subject."""
    if level not in level_mapping or subject not in subject_mapping:
        return [], 0

    level_encoded = level_mapping[level]
    subject_encoded = subject_mapping[subject]
    query_vector = np.array([level_encoded, subject_encoded, 0.75, 0.75]).reshape(1, -1)

    distances, indices = knn_model.kneighbors(query_vector, n_neighbors=min(50, len(df)))

    exact_matches, level_matches, other_matches = [], [], []
    for idx in indices[0]:
        course = df.iloc[idx]
        if course['level'] == level and course['subject'] == subject:
            exact_matches.append(idx)
        elif course['level'] == level:
            level_matches.append(idx)
        else:
            other_matches.append(idx)

    all_matches = exact_matches + level_matches + other_matches
    final_indices = all_matches[:limit]

    if not final_indices:
        return [], 0

    selected_cols = ['course_id', 'course_title', 'level', 'subject', 'price', 'num_subscribers', 'num_reviews', 'url']
    recommendations = df.iloc[final_indices][selected_cols].to_dict(orient='records')

    for rec in recommendations:
        rec['course_id'] = str(rec['course_id'])

    return recommendations, len(recommendations)

def search_course_subject(query: str) -> List[str]:
    """Search for course subjects matching the query."""
    subjects = list(subject_mapping.keys())
    matches = get_close_matches(query, subjects, n=5, cutoff=0.2)

    if not matches:
        matches = [s for s in subjects if query.lower() in s.lower()][:5]
    
    return matches
