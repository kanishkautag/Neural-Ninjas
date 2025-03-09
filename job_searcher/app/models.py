from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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