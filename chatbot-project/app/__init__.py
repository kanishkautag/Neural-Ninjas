from fastapi import APIRouter, HTTPException

from app.models import JobSearchRequest, JobSearchResponse
from app.agent import search_job_info

router = APIRouter()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """
    Search for job information and trends in a specific industry
    """
    try:
        response = await search_job_info(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}