import httpx
import json
import logging
from typing import List, Dict, Any, Optional

from app.config import SERPER_API_KEY, SERPER_BASE_URL, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.models import SearchResult, JobSearchResponse, JobSearchRequest, SkillsetRequest, SkillsetResponse, Skill

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_web(query: str) -> List[Dict[str, Any]]:
    """
    Search the web using Serper API
    """
    try:
        if not SERPER_API_KEY:
            logger.error("Serper API key is missing")
            return []
            
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": 10
        }
        
        logger.info(f"Sending request to Serper API: {query}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SERPER_BASE_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Serper API request failed with status {response.status_code}: {response.text}")
                return []
            
            data = response.json()
            return data.get("organic", [])
    except Exception as e:
        logger.error(f"Error in search_web: {str(e)}")
        return []


async def process_results(results: List[Dict[str, Any]]) -> List[SearchResult]:
    """
    Process and clean search results
    """
    processed_results = []
    
    try:
        for result in results:
            processed_results.append(
                SearchResult(
                    title=result.get("title", ""),
                    link=result.get("link", ""),
                    snippet=result.get("snippet", ""),
                    date=result.get("date", None),
                    source=result.get("source", None)
                )
            )
        
        return processed_results
    except Exception as e:
        logger.error(f"Error processing results: {str(e)}")
        return []


async def generate_summary(search_results: List[SearchResult], industry: str) -> str:
    """
    Generate a summary of search results using Ollama
    """
    try:
        # If no results, return a generic message
        if not search_results:
            return f"No recent information found for {industry} industry. Please try with different keywords or check your API configuration."
            
        # Format the search results to send to the LLM
        formatted_results = "\n\n".join([
            f"Title: {result.title}\nSnippet: {result.snippet}\nDate: {result.date or 'Unknown'}\nSource: {result.source or 'Unknown'}"
            for result in search_results[:5]  # Limit to top 5 for summary
        ])
        
        prompt = f"""
You are a helpful job market analyst. Based on the following search results about job trends 
and news in the {industry} industry, provide a concise summary of the current job market situation,
notable trends, and key insights that would be valuable for job seekers.

Search Results:
{formatted_results}

Please provide a 3-4 paragraph summary highlighting the most important points.
"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        logger.info(f"Sending request to Ollama: {OLLAMA_BASE_URL}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API request failed with status {response.status_code}: {response.text}")
                return f"Error generating summary. Please check if Ollama is running at {OLLAMA_BASE_URL} with the model {OLLAMA_MODEL}."
            
            data = response.json()
            return data.get("response", "Unable to generate summary.")
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"Error generating summary: {str(e)}"


async def search_job_info(request: JobSearchRequest) -> JobSearchResponse:
    """
    Main agent function to search for job information and summarize results
    """
    try:
        # Construct search query
        query_parts = [f"{request.industry} jobs"]
        
        if request.keywords:
            query_parts.append(" ".join(request.keywords))
        
        if request.location:
            query_parts.append(request.location)
        
        if request.time_period:
            query_parts.append(request.time_period)
        
        query = " ".join(query_parts)
        logger.info(f"Constructed query: {query}")
        
        # Search the web
        search_results_raw = await search_web(query)
        
        # Process results
        search_results = await process_results(search_results_raw)
        
        # Generate summary
        summary = await generate_summary(search_results, request.industry)
        
        return JobSearchResponse(
            results=search_results,
            summary=summary,
            industry=request.industry,
            query_used=query
        )
    except Exception as e:
        logger.error(f"Error in search_job_info: {str(e)}")
        raise


async def get_profession_skillset(request: SkillsetRequest) -> SkillsetResponse:
    """
    Get required skillset for a specific profession using Ollama
    """
    try:
        prompt = f"""
You are a career advisor and industry expert. Based on your knowledge of the job market in 2024,
provide a comprehensive analysis of the skills required for the profession: {request.profession}
at the {request.experience_level} experience level.

Structure your response in JSON format with the following structure:
{{
  "technical_skills": [
    {{
      "name": "skill name",
      "description": "brief description of the skill",
      "importance": "essential/preferred/bonus"
    }}
  ],
  "soft_skills": [
    {{
      "name": "skill name",
      "description": "brief description of the skill",
      "importance": "essential/preferred/bonus"
    }}
  ],
  "certifications": ["certification1", "certification2"],
  "tools": ["tool1", "tool2"],
  "summary": "A brief paragraph summarizing the key skills and their importance for this profession"
}}

Focus on current, relevant skills that are in demand in today's job market.
Include 5-8 technical skills and 3-5 soft skills.
"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        logger.info(f"Sending skillset request to Ollama for profession: {request.profession}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API request failed with status {response.status_code}: {response.text}")
                return await generate_fallback_skillset(request, error_msg=f"Error connecting to Ollama: {response.status_code}")
            
            data = response.json()
            llm_response = data.get("response", "")
            
            # Extract JSON from LLM response
            try:
                # Try to find JSON block if response includes markdown or other text
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > 0:
                    json_str = llm_response[json_start:json_end]
                    parsed_data = json.loads(json_str)
                else:
                    # Fallback to parsing the entire response
                    parsed_data = json.loads(llm_response)
                
                # Create skill objects
                technical_skills = [
                    Skill(
                        name=skill.get("name", ""),
                        description=skill.get("description", ""),
                        importance=skill.get("importance", "preferred")
                    )
                    for skill in parsed_data.get("technical_skills", [])
                ]
                
                soft_skills = [
                    Skill(
                        name=skill.get("name", ""),
                        description=skill.get("description", ""),
                        importance=skill.get("importance", "preferred")
                    )
                    for skill in parsed_data.get("soft_skills", [])
                ]
                
                return SkillsetResponse(
                    profession=request.profession,
                    experience_level=request.experience_level,
                    technical_skills=technical_skills,
                    soft_skills=soft_skills,
                    certifications=parsed_data.get("certifications", []),
                    tools=parsed_data.get("tools", []),
                    summary=parsed_data.get("summary", "")
                )
                
            except Exception as e:
                logger.error(f"Error parsing LLM response as JSON: {str(e)}")
                return await generate_fallback_skillset(request, llm_response=llm_response)
    except Exception as e:
        logger.error(f"Error in get_profession_skillset: {str(e)}")
        return await generate_fallback_skillset(request, error_msg=str(e))


async def generate_fallback_skillset(request: SkillsetRequest, llm_response: Optional[str] = None, error_msg: Optional[str] = None) -> SkillsetResponse:
    """
    Fallback function to generate skillset if JSON parsing fails
    """
    error_detail = ""
    if error_msg:
        error_detail = f" Error: {error_msg}"
    elif llm_response:
        error_detail = " The model response couldn't be parsed correctly."
        
    # Default skills for fallback
    technical_skills = [
        Skill(name="Core Skill 1", description="Essential skill for this profession", importance="essential"),
        Skill(name="Core Skill 2", description="Important technical knowledge", importance="essential"),
        Skill(name="Specialized Skill", description="Specialized knowledge in this field", importance="preferred")
    ]
    
    soft_skills = [
        Skill(name="Communication", description="Ability to communicate effectively", importance="essential"),
        Skill(name="Problem Solving", description="Analytical thinking and problem solving", importance="essential")
    ]
    
    return SkillsetResponse(
        profession=request.profession,
        experience_level=request.experience_level,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        certifications=["Relevant certification"],
        tools=["Common tool in this profession"],
        summary=f"These are common skills required for a {request.experience_level} {request.profession}.{error_detail} Please check if Ollama is running with model {OLLAMA_MODEL} and try again."
    )