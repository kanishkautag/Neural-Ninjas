from pydantic import BaseModel
from typing import List, Optional


class JobSearchRequest(BaseModel):
    industry: str
    keywords: Optional[List[str]] = None
    location: Optional[str] = None
    time_period: Optional[str] = "past week"  # e.g., "past week", "past month"
    

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    date: Optional[str] = None
    source: Optional[str] = None


class JobSearchResponse(BaseModel):
    results: List[SearchResult]
    summary: str
    industry: str
    query_used: str


class SkillsetRequest(BaseModel):
    profession: str
    experience_level: Optional[str] = "mid-level"  # e.g., "entry-level", "mid-level", "senior"


class Skill(BaseModel):
    name: str
    description: str
    importance: str  # "essential", "preferred", "bonus"


class SkillsetResponse(BaseModel):
    profession: str
    experience_level: str
    technical_skills: List[Skill]
    soft_skills: List[Skill]
    certifications: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    summary: str