from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import uvicorn
from app.agent import JobSearchAgent
from app.models import JobSearchRequest, SkillsetRequest
from app.config import settings

app = FastAPI(title="Job Search Agent")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize agent
job_agent = JobSearchAgent()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/search-jobs")
async def search_jobs(request: JobSearchRequest):
    """API endpoint to search for jobs"""
    try:
        results = job_agent.search_jobs(
            industry=request.industry,
            keywords=request.keywords,
            location=request.location,
            time_period=request.time_period
        )
        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/get-skillset")
async def get_skillset(request: SkillsetRequest):
    """API endpoint to get professional skillset recommendations"""
    try:
        skillset = job_agent.get_professional_skillset(
            profession=request.profession,
            experience_level=request.experience_level
        )
        return {"status": "success", "data": skillset}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)