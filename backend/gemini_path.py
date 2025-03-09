import os
import json
import google.generativeai as genai
from typing import List

# In gemini_path.py, consider changing to:
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC2XzjZZBh5CAFvJl8uZSe3MDUfqZBsYjA")
if API_KEY:
    genai.configure(api_key=API_KEY)
gmodel = genai.GenerativeModel('gemini-1.5-pro')

# Sample career paths for fallback/demo purposes
SAMPLE_PATHS = {
    "machine learning engineer": [
        "Linear Algebra", "Statistics Fundamentals", "Python Basics", 
        "Data Structures", "Pandas", "Data Visualization", 
        "Scikit-Learn", "Model Evaluation", "Neural Networks", "Deep Learning"
    ],
    "web developer": [
        "HTML Basics", "CSS Fundamentals", "JavaScript Core", 
        "DOM Manipulation", "Responsive Design", "Frontend Framework", 
        "Backend Basics", "Database Design", "API Development", "Deployment"
    ]
}

def generate_learning_path(career_path: str, num_points: int = 10) -> List[str]:
    """
    Generate a learning path using the Gemini API or fallback to sample data.
    """
    career_key = career_path.lower()
    if not API_KEY:
        return SAMPLE_PATHS.get(career_key, SAMPLE_PATHS["machine learning engineer"])[:num_points]
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = f"""
        Create a sequential learning path for someone pursuing a career in {career_path}.
        Generate exactly {num_points} concise learning points that should be mastered in order.
        Each point should be 2-3 words only.
        Format the response as a JSON list of strings only.
        """
        response = model.generate_content(prompt)
        response_text = response.text
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            learning_path = json.loads(json_str)
            return learning_path[:num_points]
    except Exception as e:
        print(f"Error generating learning path: {e}")
    
    return SAMPLE_PATHS["machine learning engineer"][:num_points]
